#!/usr/bin/env bash
# Puts a new Artburg Blocks everywhere it is needed: the server, the Prism client and the web map.
#
#   tools/deploy.sh            build, wait until the server AND the game are closed, test, install
#   tools/deploy.sh --now      do not wait: exit with code 3 if the server or the game is running
#   tools/deploy.sh --no-build install the jar that is already in build/libs
#   tools/deploy.sh --no-test  skip booting the server on the test world (not recommended)
#
# The order matters: the jar goes to the server first and the server is booted on a throwaway world
# (tools/server_test.py, port 25599, the real world is not touched). Only if every block registers there does it go to
# the client and the web map; otherwise the server gets its previous jar back. Old jars are kept in mods/_disabled as
# <name>.before-<new version>. A server with the mod lets in only clients that have the same mod, so other players
# need the new jar too. Log: deploy.log next to this project's README.
set -u
cd "$(dirname "$0")/.."
ROOT=$(pwd)

SERVER_MODS="/e/Artburg Server/mods"
CLIENT_MODS="/c/Users/arthaix/AppData/Roaming/PrismLauncher/instances/1.12.2/minecraft/mods"
MAP_REPO="/e/Artburg Map/osm"
MAP_PACKS="assets/resourcepacks"
LOG="$ROOT/deploy.log"

WAIT=1; BUILD=1; TEST=1
for a in "$@"; do
    case "$a" in
        --now) WAIT=0 ;;
        --no-build) BUILD=0 ;;
        --no-test) TEST=0 ;;
        *) echo "unknown option $a (see the top of $0)"; exit 2 ;;
    esac
done

log() { echo "$(date '+%m-%d %H:%M:%S') $*" | tee -a "$LOG"; }
die() { log "STOPPED: $*"; case "$*" in BUSY*) exit 3 ;; esac; exit 1; }

# ---------------------------------------------------------------- version and build
VERSION=$(sed -n "s/^version = '\([^']*\)'.*/\1/p" build.gradle)
CODE_VERSION=$(sed -n 's/.*String VERSION = "\([^"]*\)".*/\1/p' src/main/java/ru/arthaix/artburgblocks/ArtburgBlocks.java)
[ -n "$VERSION" ] || die "no version in build.gradle"
[ "$VERSION" = "$CODE_VERSION" ] || die "build.gradle says $VERSION but ArtburgBlocks.VERSION is $CODE_VERSION"
NAME="artburgblocks-$VERSION.jar"
JAR="build/libs/$NAME"

log "Artburg Blocks $VERSION: start"
if [ "$BUILD" = 1 ]; then
    python tools/gen_textures.py || die "texture generator failed"
    python tools/gen_granite.py > /dev/null || die "granite generator failed"
    python tools/gen_asphalt.py > /dev/null || die "asphalt generator failed"
    python tools/gen_meta.py > /dev/null || die "meta block generator failed"
    ./gradlew build > build.log 2>&1 || die "gradle build failed, see build.log"
fi
[ -f "$JAR" ] || die "$JAR does not exist"
STAGED="$ROOT/build/$NAME.staged"            # a rebuild while we wait must not change what gets installed
cp -f "$JAR" "$STAGED"
log "jar $NAME $(sha256sum "$STAGED" | cut -c1-16)"
# the blocks the test boot must find registered: those inside this jar, not the source tree, which may be ahead of it
BLOCKS=$(unzip -Z1 "$STAGED" 'assets/artburgblocks/blockstates/*.json' | sed 's#.*/##; s/\.json$//' | tr '\n' ' ')
log "blocks in the jar: $(echo $BLOCKS | wc -w)"

# ---------------------------------------------------------------- server and game must be closed
server_count() {
    powershell.exe -NoProfile -Command "@(Get-CimInstance Win32_Process -Filter \"Name='java.exe'\" | Where-Object { \$_.CommandLine -like '*-jar forge-1.12.2*nogui*' }).Count" | tr -d '[:space:]'
}
client_count() {
    # Prism starts the game with javaw.exe; any javaw counts, a java.exe only when it comes from Prism
    powershell.exe -NoProfile -Command "@(Get-CimInstance Win32_Process -Filter \"Name='javaw.exe' OR Name='java.exe'\" | Where-Object { \$_.Name -eq 'javaw.exe' -or \$_.CommandLine -like '*PrismLauncher*' }).Count" | tr -d '[:space:]'
}
off=0
deadline=$(( $(date +%s) + 72 * 3600 ))
said=0
while :; do
    s=$(server_count); c=$(client_count)
    if [ "$s" = "0" ] && [ "$c" = "0" ]; then off=$((off + 1)); else off=0; fi
    [ "$off" -ge 2 ] && break                                    # closed on two checks in a row
    if [ "$WAIT" = 0 ] && [ "$off" = 0 ]; then log "BUSY: server running: $s, game running: $c"; exit 3; fi
    if [ "$off" = 0 ] && [ "$said" = 0 ]; then log "waiting for the server ($s) and the game ($c) to be closed"; said=1; fi
    [ "$(date +%s)" -lt "$deadline" ] || die "gave up waiting after 72 h"
    sleep $([ "$off" = 0 ] && echo 20 || echo 5)
done
log "server and game are closed"

# ---------------------------------------------------------------- swapping a jar in a mods folder
# swap DIR: older artburgblocks jars go to DIR/_disabled, the staged one comes in; prints what was put aside
swap() {
    local dir="$1" f base
    mkdir -p "$dir/_disabled" || return 1
    for f in "$dir"/artburgblocks-*.jar; do
        [ -e "$f" ] || continue
        base=$(basename "$f")
        if [ "$base" = "$NAME" ] && cmp -s "$f" "$STAGED"; then continue; fi
        mv -f "$f" "$dir/_disabled/$base.before-$VERSION" || return 1
        echo "$base"
    done
    cp -f "$STAGED" "$dir/$NAME"
}
# unswap DIR: back to what swap put aside
unswap() {
    local dir="$1" f
    rm -f "$dir/$NAME"
    for f in "$dir"/_disabled/artburgblocks-*.jar.before-"$VERSION"; do
        [ -e "$f" ] && mv -f "$f" "$dir/$(basename "$f" .before-"$VERSION")"
    done
}
# check DIR: exactly one artburgblocks jar and it is ours (two copies = duplicate mod crash)
check() {
    local n
    n=$(ls "$1" | grep -c '^artburgblocks-.*\.jar$')
    [ "$n" = "1" ] && cmp -s "$1/$NAME" "$STAGED"
}

# ---------------------------------------------------------------- 1. server, then the test boot
# a server that already has exactly this jar was tested with it before: nothing to put in, test or roll back
ALREADY=0; check "$SERVER_MODS" && ALREADY=1
if [ "$ALREADY" = 1 ]; then
    log "server: already has $NAME"
else
    aside=$(swap "$SERVER_MODS") || die "could not put the jar on the server"
    check "$SERVER_MODS" || { unswap "$SERVER_MODS"; die "server mods folder is not right after the swap"; }
    log "server: $NAME in${aside:+, put aside: $aside}"
fi
if [ "$TEST" = 1 ] && [ "$ALREADY" = 0 ]; then
    log "server: booting on the test world"
    out=$(python tools/server_test.py $BLOCKS 2>&1)
    if ! echo "$out" | grep -q "^passed"; then
        unswap "$SERVER_MODS"
        [ "$(server_count)" = "0" ] || log "WARNING: a test server is still running, look at tools/server_test.log"
        die "test boot failed, the server has its previous jar back: $(echo "$out" | tr '\n' ' ')"
    fi
    log "server: $(echo "$out" | tr '\n' ' ')"
fi

# ---------------------------------------------------------------- 2. client
# the game may have been started during the test boot: its jars are locked then, try again on the next run
[ "$(client_count)" = "0" ] || die "BUSY: the game was started meanwhile, the client and the web map wait for the next run"
aside=$(swap "$CLIENT_MODS") || die "could not put the jar into the client (the server already has it)"
check "$CLIENT_MODS" || die "client mods folder is not right after the swap, look at $CLIENT_MODS"
log "client: $NAME in${aside:+, put aside: $aside}"

# ---------------------------------------------------------------- 3. web map (its textures come from the jar)
# The map's renderers keep the jars open for hours, so an old one often cannot be deleted yet. It does no harm meanwhile
# (the map reads the jars in name order and the later one wins) and tools/autosync.sh removes it on a later pass.
(
    cd "$MAP_REPO" || exit 1
    cp -f "$STAGED" "$MAP_PACKS/$NAME" && git add "$MAP_PACKS/$NAME" || exit 1
    for f in "$MAP_PACKS"/artburgblocks-*.jar; do
        [ -e "$f" ] || continue
        [ "$(basename "$f")" = "$NAME" ] && continue
        git rm -q "$f" 2>/dev/null || echo "$(date '+%m-%d %H:%M:%S') web map: $(basename "$f") is in use by the map renderer, it goes on a later pass"
    done
    if ! git diff --cached --quiet -- "$MAP_PACKS"; then
        git commit -q -m "Карта: Artburg Blocks $VERSION" -- "$MAP_PACKS" || exit 1
        git push -q origin main 2>/dev/null || echo "push failed, the commit stays local"
    fi
) >> "$LOG" 2>&1 || die "web map: could not update $MAP_REPO/$MAP_PACKS"
cmp -s "$MAP_REPO/$MAP_PACKS/$NAME" "$STAGED" || die "web map: $NAME is not there"
log "web map: $NAME in, $(cd "$MAP_REPO" && git log --oneline -1 -- "$MAP_PACKS/$NAME")"

rm -f "$STAGED"
log "Artburg Blocks $VERSION: installed on the server, the client and the web map"
