"""Boot the real Artburg server directory on a separate throwaway world and check that Artburg Blocks loads there.

Same java and flags as start.bat, city preload off, its own port and world (--port 25599 --universe _abtest_universe),
so the real world, server.properties and players are never touched. Passes when the server comes up, nothing
about artburgblocks in the console looks like an error, and the test world's level.dat has every block of the mod
registered. The test world is deleted afterwards. Console: tools/server_test.log.

    python tools/server_test.py lawn_sod lawn_mowed ...     # block ids that must be registered
Exit code 0 = passed.
"""
import gzip
import os
import re
import shutil
import subprocess
import sys
import threading
import time

S = r"E:\Artburg Server"
UNIVERSE = "_abtest_universe"
WORLD = "abtest"
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "server_test.log")
BOOT_LIMIT = 15 * 60


def main(blocks):
    start_bat = open(os.path.join(S, "start.bat"), encoding="utf-8", errors="replace").read()
    line = next(l for l in start_bat.splitlines() if "java.exe" in l)
    m = re.search(r'"([^"]*java\.exe)"(.*)-jar\s+(\S+)', line)
    java, flags, jar = m.group(1), m.group(2).split(), m.group(3)
    args = [java] + [f for f in flags if f] + ["-Dchunkkeep.preload=false", "-jar", jar, "nogui",
                                              "--port", "25599", "--universe", UNIVERSE, "--world", WORLD]
    shutil.rmtree(os.path.join(S, UNIVERSE), ignore_errors=True)
    log = open(LOG, "w", encoding="utf-8", errors="replace")
    p = subprocess.Popen(args, cwd=S, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, encoding="utf-8", errors="replace")
    killer = threading.Timer(BOOT_LIMIT, p.kill)                  # a hung boot must not leave a server behind
    killer.start()
    t0 = time.time()
    up, bad = False, []
    try:
        for out in p.stdout:
            log.write(out)
            log.flush()
            low = out.lower()
            # FML's "Attempting connection with missing mods [...]" lists every mod and is no error
            if "artburgblocks" in low and (re.search(r"/(warn|error|fatal)\]", low) or "exception" in low):
                bad.append(out.strip())
            if not up and "Done (" in out:
                up = True
                print("server up after %.0f s" % (time.time() - t0), flush=True)
                time.sleep(5)
                p.stdin.write("stop\n")
                p.stdin.flush()
        p.wait(timeout=300)
    except Exception as e:
        bad.append("runner: %s" % e)
        p.kill()
    finally:
        killer.cancel()
        log.close()

    missing = list(blocks)
    level = os.path.join(S, UNIVERSE, WORLD, "level.dat")
    try:
        raw = gzip.open(level).read()
        missing = [b for b in blocks if ("artburgblocks:" + b).encode() not in raw]
    except Exception as e:
        bad.append("level.dat: %s" % e)
    shutil.rmtree(os.path.join(S, UNIVERSE), ignore_errors=True)

    if not up:
        print("FAILED: the server did not come up (see %s)" % LOG)
        return 1
    if missing:
        print("FAILED: not registered on the server: %s" % ", ".join(missing))
        return 1
    if bad:
        print("FAILED: errors about artburgblocks:\n  " + "\n  ".join(bad[:8]))
        return 1
    print("passed: %d blocks registered, no errors" % len(blocks))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
