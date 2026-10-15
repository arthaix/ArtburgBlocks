# Artburg Blocks

Building blocks of the Artburg server: Minecraft 1.12.2, Forge 14.23.5. Needed on the server and on every client.
Everything is in the creative tab «Артбург». Most blocks keep up to 16 looks (shades, colours, states) in their
metadata, so every look also works as Chisels & Bits bits and LittleTiles tiles.

## Blocks

**Lawns** — fresh rolled sod (the rolls run the way you look while placing it), mowed, striped (mowing lanes two
blocks wide, light and dark by position), overgrown, dry, worn, newly seeded, grass pavers. They never spread or
turn to dirt; flowers, saplings and tall grass can be planted on them.

**White granite** — `sbm:belygranit` at 60, 70, 80, 90, 110 and 120 % of its brightness.

**Asphalt** — freshly laid, new, ordinary (the grey of the existing roads), worn, old, patched, with sealed cracks;
coloured asphalt for bus and bike lanes.

**Road marking** — white, yellow, orange, blue and red paint, each fresh, normal or worn.

**Facade clinker** — long facade clinker, 333 × 62.5 mm (a course is one bit high): running bond with light or dark
joints, quarter bond and stack bond, each in 48 single-tone shades — matte classics, glazed (dark emerald, bottle
green, petrol, cobalt, bordeaux, cherry, mustard, copper and bronze metallic …) and sixteen more.

**Street** — curbs (granite, concrete, painted), concrete pavers (bricks along X or Z, herringbone, 500 and 250 mm
slabs), tactile paving, granite setts, manholes, storm grates and drain channels.

**Walls** — panel-house panels (concrete, pebble-dash, small tiles, sealed seams), brickwork, profiled sheet in RAL
colours, glass facades, architectural concrete; platform edges with the yellow line and warning tiles; see-through
steel grating.

## Rules

[RULES.md](RULES.md) is what every block has to follow: one colour per block, no gradients inside a brick, real
sizes and current shades.

## Building

    python tools/gen_textures.py      # lawns
    python tools/gen_granite.py       # white granite (reads the SBM jar on the server)
    python tools/gen_asphalt.py       # asphalt and road marking
    python tools/gen_meta.py          # everything with 16 looks, and meta_blocks.json the mod registers them from
    ./gradlew build                   # build/libs/artburgblocks-<version>.jar

Textures, models, blockstates and names come only from these generators; the PNG files are not edited by hand.

## Getting it onto the server, the client and the web map

Automatic: the Windows task "Artburg Blocks autosync" (`tools/autosync-install.ps1` registers it) runs
`tools/autosync.sh` hidden every 3 minutes. Whenever the jar in `build/libs` differs from what the server, the Prism
client or the web map has, and the server and the game are both closed, it runs `tools/deploy.sh --now --no-build`.
So a release is: bump the version in `build.gradle` and `ArtburgBlocks.java`, `./gradlew build`, have the game and
the server closed. Log: `deploy.log`; `build/autosync.last` is the time of the last pass.

By hand: `tools/deploy.sh` (builds, waits for the server and the game to close, then installs). Either way the jar goes
to the server first and the server is booted on a throwaway world (`tools/server_test.py`, port 25599, the real world
is not touched); only if every block registers there does it go on to the client and the web map, a failed test puts
the previous jar back and that build is not retried. Old jars are kept in `mods/_disabled`.

## Licence

All rights reserved, see [LICENSE](LICENSE).
