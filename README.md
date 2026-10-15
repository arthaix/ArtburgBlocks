# Artburg Blocks

Blocks of the Artburg server (Minecraft 1.12.2, Forge). Needed on the server and on every client.

Lawns, all `artburgblocks:` — in the creative tab "Артбург":

| id | name |
|---|---|
| `lawn_sod` | Свежий рулонный газон — rolls run the way you look while placing |
| `lawn_mowed` | Стриженый газон |
| `lawn_striped` | Газон с полосами покоса — lanes run the way you look, light/dark by position |
| `lawn_overgrown` | Некошеная трава |
| `lawn_dry` | Выгоревшая трава |
| `lawn_worn` | Вытоптанный газон |
| `lawn_seeded` | Свежий посев газона |
| `lawn_grid` | Газонная решётка |

They never spread or turn to dirt; flowers, saplings and tall grass can be planted on them.

## Building

    python tools/gen_textures.py      # textures, models, blockstates (32x32, Artburg pack style)
    ./gradlew build                   # build/libs/artburgblocks-<version>.jar
