#!/usr/bin/env bash
# One pass of the automatic sync, run every few minutes by the Windows task "Artburg Blocks autosync"
# (tools/autosync-install.ps1). Keeps the server, the Prism client and the web map on the jar that was built last:
#
#   build/libs/artburgblocks-<version>.jar  (what `./gradlew build` made, version from build.gradle)
#
# Quiet when everything already has it. Otherwise, when the server and the game are both closed, runs
# tools/deploy.sh --now --no-build (test boot on a throwaway world first, then client and map). While either is running
# it simply tries again on the next pass. A jar that failed its test is not retried until a new build replaces it.
# Log: deploy.log.
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)
LOG="$ROOT/deploy.log"
SERVER_MODS="/e/Artburg Server/mods"
CLIENT_MODS="/c/Users/arthaix/AppData/Roaming/PrismLauncher/instances/1.12.2/minecraft/mods"
MAP_PACKS="/e/Artburg Map/osm/assets/resourcepacks"
FAILED="$ROOT/build/autosync.failed"
LOCK="$ROOT/build/autosync.lock"

log() { echo "$(date '+%m-%d %H:%M:%S') [autosync] $*" >> "$LOG"; }
mkdir -p build && date '+%Y-%m-%d %H:%M:%S' > build/autosync.last   # proof that the task runs

VERSION=$(sed -n "s/^version = '\([^']*\)'.*/\1/p" build.gradle)
NAME="artburgblocks-$VERSION.jar"
JAR="build/libs/$NAME"
[ -f "$JAR" ] || exit 0
# a build still being written
[ $(( $(date +%s) - $(stat -c %Y "$JAR") )) -ge 60 ] || exit 0

synced() {  # DIR: exactly one artburgblocks jar there and it is this build
    [ "$(ls "$1" 2>/dev/null | grep -c '^artburgblocks-.*\.jar$')" = "1" ] && cmp -s "$1/$NAME" "$JAR"
}

# old jars the map's renderers held open when they were replaced: remove each as soon as it is free
(
    cd "$MAP_PACKS/../.." || exit 0
    gone=""
    for f in assets/resourcepacks/artburgblocks-*.jar; do
        [ -e "$f" ] && [ "$(basename "$f")" != "$NAME" ] || continue
        cmp -s "$f" "$ROOT/$JAR" && continue
        git rm -q "$f" 2>/dev/null && gone="$gone $(basename "$f")"
    done
    if [ -n "$gone" ]; then
        git commit -q -m "Карта: убран старый Artburg Blocks:$gone" -- assets/resourcepacks && log "web map: removed$gone"
        git push -q origin main 2>/dev/null || true
    fi
)

# the map may keep an old jar a while (see above), it only needs this one
synced "$SERVER_MODS" && synced "$CLIENT_MODS" && cmp -s "$MAP_PACKS/$NAME" "$JAR" && exit 0

SUM=$(sha256sum "$JAR" | cut -c1-16)
if [ -f "$FAILED" ] && [ "$(cat "$FAILED")" = "$SUM" ]; then exit 0; fi

# one pass at a time (a test boot takes a few minutes); a lock older than an hour is left over from a crash
if ! mkdir "$LOCK" 2>/dev/null; then
    [ $(( $(date +%s) - $(stat -c %Y "$LOCK") )) -gt 3600 ] || exit 0
    rm -rf "$LOCK"; mkdir "$LOCK" || exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

tools/deploy.sh --now --no-build > /dev/null 2>&1
rc=$?
case "$rc" in
    0) rm -f "$FAILED" ;;
    3) ;;                                                  # server or game running: next pass
    *) echo "$SUM" > "$FAILED"; log "$NAME ($SUM) failed, not retried until the next build: see the lines above" ;;
esac
exit 0
