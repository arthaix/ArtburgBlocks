# Artburg Blocks

Blocks of the Artburg server (Minecraft 1.12.2, Forge). Needed on the server and on every client.

Lawns, all `artburgblocks:` — in the creative tab "Артбург":

| id | name |
|---|---|
| `lawn_sod` | Свежий рулонный газон — rolls run the way you look while placing |
| `lawn_mowed` | Стриженый газон |
| `lawn_striped` | Газон с полосами покоса — lanes two blocks wide run the way you look, light/dark by position |
| `lawn_overgrown` | Некошеная трава |
| `lawn_dry` | Выгоревшая трава |
| `lawn_worn` | Вытоптанный газон |
| `lawn_seeded` | Свежий посев газона |
| `lawn_grid` | Газонная решётка |

They never spread or turn to dirt; flowers, saplings and tall grass can be planted on them.

## Building

    python tools/gen_textures.py      # textures, models, blockstates (32x32, Artburg pack style)
    ./gradlew build                   # build/libs/artburgblocks-<version>.jar

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
