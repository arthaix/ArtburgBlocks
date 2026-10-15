"""Textures, models and blockstates of the lawn blocks.

Every texture is 32x32 like the Artburg resource pack. Tops are drawn in their final colours (no biome tint): the
ordinary mowed lawn averages the colour vanilla grass has on the server, the other kinds are told apart from it.
Sides are vanilla dirt from whatever pack the player uses plus an overlay of our own with the turf edge.

    python tools/gen_textures.py            # writes into src/main/resources
    python tools/gen_textures.py --preview out.png
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

N = 32
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'main', 'resources', 'assets', 'artburgblocks')
TEX = os.path.join(ROOT, 'textures', 'blocks')
VARIANTS = 4

# palettes dark -> light
MOWED = [(46, 66, 32), (62, 86, 40), (78, 104, 50), (92, 120, 58), (108, 136, 66), (128, 152, 78)]
SOD = [(50, 88, 30), (66, 110, 36), (82, 130, 42), (98, 148, 50), (116, 164, 58), (138, 180, 72)]
LIGHT = [(58, 80, 38), (74, 100, 46), (90, 118, 56), (104, 132, 64), (120, 148, 72), (140, 162, 86)]
DARK = [(40, 58, 28), (54, 76, 34), (68, 92, 44), (80, 106, 50), (94, 120, 58), (112, 136, 68)]
TALL = [(28, 46, 20), (42, 62, 26), (58, 80, 34), (76, 98, 42), (96, 116, 52), (122, 134, 68)]
DRY = [(98, 86, 46), (122, 106, 58), (144, 126, 68), (164, 146, 82), (182, 164, 98), (200, 184, 120)]
SOIL = [(76, 54, 36), (94, 68, 46), (112, 82, 56), (130, 96, 66)]
WET_SOIL = [(50, 36, 26), (62, 45, 32), (74, 54, 38), (88, 64, 45)]
SPROUT = [(92, 148, 54), (118, 172, 70), (146, 192, 88)]
CONCRETE = [(112, 112, 108), (128, 128, 124), (144, 144, 140), (158, 158, 154)]
ROOTS = [(44, 34, 24), (56, 43, 30), (66, 52, 36)]


def rng(name, i):
    return np.random.default_rng(sum(ord(c) * 31 ** k for k, c in enumerate(name)) % 2 ** 32 * 101 + i)


def field(r, blur=1.0, white=0.55, aniso=None):
    """Tileable noise in 0..1: white noise mixed with blurred noise (blurred along v when aniso is given)."""
    w = r.random((N, N))
    s = r.random((N, N))
    sig = aniso if aniso else (blur, blur)
    s = ndi.gaussian_filter(s, sig, mode='wrap')
    s = (s - s.min()) / max(s.max() - s.min(), 1e-9)
    f = white * w + (1 - white) * s
    return (f - f.min()) / max(f.max() - f.min(), 1e-9)


def paint(f, pal, lo=0.0, hi=1.0):
    """Quantise a 0..1 field onto the palette steps (pixel art, no smooth gradients)."""
    t = lo + (hi - lo) * f
    idx = np.clip((t * len(pal)).astype(int), 0, len(pal) - 1)
    return np.array(pal, float)[idx]


def blobs(r, sigma, cover):
    """Tileable mask of soft round patches covering about `cover` of the area."""
    s = ndi.gaussian_filter(r.random((N, N)), sigma, mode='wrap')
    return s > np.quantile(s, 1 - cover)


# ---------------------------------------------------------------- tops

def top_mowed(r):
    return paint(field(r, 1.0, 0.6), MOWED)


def top_sod(r):
    # rolls 0.5 m wide run along v. A seam is a thin darker line, the edge of the roll beside it a little lighter
    # (fresh turf bulges at the cut); the joints of the rolls are faint and staggered by half a block
    img = paint(field(r, 0.8, 0.7), SOD, 0.12, 1.0)
    seam = np.array(SOD[1], float) * 0.88
    for x in (0, 16):
        for y in range(N):
            if r.random() < 0.65:
                img[y, x] = seam * (0.92 + 0.16 * r.random())
            if r.random() < 0.5:
                img[y, x + 1] = np.minimum(img[y, x + 1] * 1.12, 255)
    for y, xs in ((0, range(1, 16)), (16, range(17, 32))):
        for x in xs:
            if r.random() < 0.35:
                img[y, x] = (img[y, x] * 2 + seam) / 3
    return img


def top_striped(r, light):
    pal = LIGHT if light else DARK
    return paint(field(r, aniso=(3.0, 0.5), white=0.5), pal)


def top_overgrown(r):
    img = paint(field(r, 1.6, 0.45), TALL)
    heads = r.random((N, N))
    img[heads < 0.035] = (176, 166, 112)
    img[(heads >= 0.035) & (heads < 0.05)] = (150, 140, 92)
    return img


def top_dry(r):
    img = paint(field(r, 1.2, 0.55), DRY)
    green = blobs(r, 2.0, 0.22) & (r.random((N, N)) < 0.55)
    img[green] = paint(r.random((N, N)), [(84, 96, 50), (100, 110, 58)])[green]
    gaps = r.random((N, N)) < 0.06
    img[gaps] = (92, 72, 46)
    return img


def top_worn(r):
    img = paint(field(r, 1.0, 0.6), MOWED)
    bare = blobs(r, 2.2, 0.20)
    soil = paint(field(r, 0.8, 0.7), SOIL)
    edge = ndi.binary_dilation(bare, iterations=1, border_value=0) & ~bare
    img[bare] = soil[bare]
    fringe = edge & (r.random((N, N)) < 0.5)
    img[fringe] = soil[fringe]
    tufts = bare & (r.random((N, N)) < 0.10)
    img[tufts] = np.array(MOWED[3], float)
    return img


def top_seeded(r):
    img = paint(field(r, 0.7, 0.7), WET_SOIL)
    sprout = r.random((N, N)) < 0.13
    img[sprout] = paint(r.random((N, N)), SPROUT)[sprout]
    # a sprout is a short blade: the pixel above it sometimes too
    up = np.roll(sprout, -1, 0) & (r.random((N, N)) < 0.4)
    img[up] = np.array(SPROUT[0], float)
    return img


def top_grid(r):
    # eco-grid pavers: square cells 12 px with concrete ribs 4 px, period 16 (0.5 m)
    img = paint(field(r, 0.8, 0.7), CONCRETE)
    grass = paint(field(r, 1.0, 0.6), MOWED)
    soil = paint(r.random((N, N)), SOIL)
    for cy in (0, 16):
        for cx in (0, 16):
            y0, x0 = cy + 2, cx + 2
            cell = (slice(y0, y0 + 12), slice(x0, x0 + 12))
            img[cell] = grass[cell]
            for i in range(12):
                for j in range(12):
                    border = min(i, j, 11 - i, 11 - j)
                    if border == 0 and r.random() < 0.35:
                        img[y0 + i, x0 + j] = soil[y0 + i, x0 + j]
                    if (i == 0 or j == 0):                      # the rib shades the cell from the north-west sun
                        img[y0 + i, x0 + j] *= 0.78
    return img


# ---------------------------------------------------------------- side overlays (RGBA, transparent below the turf)

def edge_profile(r, lo, hi, gaps=0.0):
    h = r.integers(lo, hi + 1, N).astype(float)
    h = ndi.uniform_filter1d(h, 2, mode='wrap')
    h = np.round(h).astype(int)
    if gaps:
        h[r.random(N) < gaps] = 0
    return h


def side(r, pal, lo, hi, gaps=0.0, under=None, under_h=0):
    out = np.zeros((N, N, 4))
    h = edge_profile(r, lo, hi, gaps)
    f = field(r, 0.8, 0.7)
    for x in range(N):
        for y in range(h[x]):
            k = 1.0 - 0.35 * y / max(h[x], 1)                    # darker toward the roots
            c = np.array(pal[min(int(f[y, x] * len(pal)), len(pal) - 1)], float) * k
            out[y, x] = (*c, 255)
        if under:
            for y in range(h[x], min(h[x] + under_h, N)):
                out[y, x] = (*np.array(under[r.integers(len(under))], float), 255)
    return out


def side_seeded(r):
    out = np.zeros((N, N, 4))
    for x in range(N):
        for y in range(3):
            out[y, x] = (*np.array(WET_SOIL[r.integers(len(WET_SOIL))], float), 255)
        if r.random() < 0.18:
            out[0, x] = (*np.array(SPROUT[r.integers(len(SPROUT))], float), 255)
    return out


def side_grid(r):
    out = np.zeros((N, N, 4))
    for x in range(N):
        rib = (x % 16) < 2 or (x % 16) >= 14
        for y in range(5):
            if rib:
                c = CONCRETE[r.integers(len(CONCRETE))]
            elif y < 2:
                c = MOWED[r.integers(1, len(MOWED))]
            else:
                c = WET_SOIL[r.integers(len(WET_SOIL))]
            out[y, x] = (*np.array(c, float), 255)
        for y in range(5, 7):                                    # sand bed under the pavers
            out[y, x] = (*np.array([(150, 132, 100), (138, 120, 90)][r.integers(2)], float), 255)
    return out


# ---------------------------------------------------------------- the blocks

# name -> (top painter, side overlay painter, kind) ; kind: 'any' rotates freely, 'axis' keeps its direction
BLOCKS = {
    'lawn_sod':       (top_sod, lambda r: side(r, SOD, 3, 5, under=ROOTS, under_h=3), 'axis'),
    'lawn_mowed':     (top_mowed, lambda r: side(r, MOWED, 3, 6), 'any'),
    'lawn_striped':   (None, lambda r: side(r, MOWED, 3, 6), 'striped'),
    'lawn_overgrown': (top_overgrown, lambda r: side(r, TALL, 5, 11), 'any'),
    'lawn_dry':       (top_dry, lambda r: side(r, DRY, 3, 7), 'any'),
    'lawn_worn':      (top_worn, lambda r: side(r, MOWED, 2, 5, gaps=0.25), 'any'),
    'lawn_seeded':    (top_seeded, side_seeded, 'any'),
    'lawn_grid':      (top_grid, side_grid, 'any'),
}


def save(arr, name):
    a = np.clip(np.round(arr), 0, 255).astype(np.uint8)
    mode = 'RGBA' if a.shape[2] == 4 else 'RGB'
    Image.fromarray(a, mode).save(os.path.join(TEX, name + '.png'))


def model(path, top, overlay):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump({'parent': 'artburgblocks:block/lawn',
                   'textures': {'top': 'artburgblocks:blocks/' + top, 'overlay': 'artburgblocks:blocks/' + overlay}},
                  f, indent=2)
        f.write('\n')


def write_json(path, obj):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def tops_of(name, kind, painter):
    """[(texture name, array)] of every top a block needs."""
    out = []
    if kind == 'striped':
        for light in (False, True):
            for i in range(VARIANTS):
                out.append(('%s_%s_top_%d' % (name, 'light' if light else 'dark', i), top_striped(rng(name + str(light), i), light)))
    else:
        for i in range(VARIANTS):
            out.append(('%s_top_%d' % (name, i), painter(rng(name, i))))
    return out


def generate():
    os.makedirs(TEX, exist_ok=True)
    for d in ('blockstates', 'models/block', 'models/item'):
        os.makedirs(os.path.join(ROOT, d), exist_ok=True)
    for name, (painter, sider, kind) in BLOCKS.items():
        overlay = name + '_side_overlay'
        save(sider(rng(name, 99)), overlay)
        tops = tops_of(name, kind, painter)
        for tex, arr in tops:
            save(arr, tex)
            model(os.path.join(ROOT, 'models', 'block', tex.replace('_top', '') + '.json'), tex, overlay)
        mdl = lambda tex: 'artburgblocks:' + tex.replace('_top', '')
        if kind == 'any':
            vs = {'normal': [{'model': mdl(t), **({'y': y} if y else {})} for t, _ in tops for y in (0, 90, 180, 270)]}
        elif kind == 'axis':
            vs = {'axis=z': [{'model': mdl(t), **({'y': y} if y else {})} for t, _ in tops for y in (0, 180)],
                  'axis=x': [{'model': mdl(t), 'y': y} for t, _ in tops for y in (90, 270)]}
        else:
            vs = {}
            for light in ('false', 'true'):
                ts = [t for t, _ in tops if ('_light_' in t) == (light == 'true')]
                vs['axis=z,light=' + light] = [{'model': mdl(t), **({'y': y} if y else {})} for t in ts for y in (0, 180)]
                vs['axis=x,light=' + light] = [{'model': mdl(t), 'y': y} for t in ts for y in (90, 270)]
        write_json(os.path.join(ROOT, 'blockstates', name + '.json'), {'variants': vs})
        write_json(os.path.join(ROOT, 'models', 'item', name + '.json'), {'parent': 'artburgblocks:block/' + tops[0][0].replace('_top', '')})


# ---------------------------------------------------------------- preview

def preview(path, dirt_png=None):
    """Each kind as a 4x4 patch of blocks seen from above (variants as the game would pick them) and one side."""
    S = 4                                 # screen pixels per texel
    dirt = None
    if dirt_png and os.path.exists(dirt_png):
        dirt = np.asarray(Image.open(dirt_png).convert('RGB').resize((N, N), Image.NEAREST), float)
    names = list(BLOCKS)
    cell = 4 * N * S
    pad = 24
    W = len(names) * (cell + pad) + pad
    H = cell + N * S + 3 * pad
    canvas = Image.new('RGB', (W, H), (236, 236, 232))
    for k, name in enumerate(names):
        painter, sider, kind = BLOCKS[name]
        tops = dict(tops_of(name, kind, painter))
        r = np.random.default_rng(k)
        patch = np.zeros((4 * N, 4 * N, 3))
        for bz in range(4):
            for bx in range(4):
                if kind == 'striped':
                    light = bx % 2 == 0
                    t = tops['%s_%s_top_%d' % (name, 'light' if light else 'dark', r.integers(VARIANTS))]
                    t = np.rot90(t, 2 * r.integers(2))
                elif kind == 'axis':
                    t = np.rot90(tops['%s_top_%d' % (name, r.integers(VARIANTS))], 2 * r.integers(2))
                else:
                    t = np.rot90(tops['%s_top_%d' % (name, r.integers(VARIANTS))], r.integers(4))
                patch[bz * N:(bz + 1) * N, bx * N:(bx + 1) * N] = t
        im = Image.fromarray(np.clip(patch, 0, 255).astype(np.uint8)).resize((cell, cell), Image.NEAREST)
        x0 = pad + k * (cell + pad)
        canvas.paste(im, (x0, pad))
        ov = Image.open(os.path.join(TEX, name + '_side_overlay.png'))
        ov = np.asarray(ov, float)
        base = dirt if dirt is not None else np.full((N, N, 3), (122, 88, 60), float)
        sd = base * (1 - ov[..., 3:] / 255) + ov[..., :3] * (ov[..., 3:] / 255)
        side_row = np.concatenate([sd] * 4, 1)
        im2 = Image.fromarray(np.clip(side_row, 0, 255).astype(np.uint8)).resize((cell, N * S), Image.NEAREST)
        canvas.paste(im2, (x0, 2 * pad + cell))
    canvas.save(path)


if __name__ == '__main__':
    generate()
    if '--preview' in sys.argv:
        preview(sys.argv[sys.argv.index('--preview') + 1],
                sys.argv[sys.argv.index('--dirt') + 1] if '--dirt' in sys.argv else None)
