"""Textures, models and blockstates of the asphalt blocks.

32x32 like the rest of the mod. Asphalt is drawn as binder (dark, a little mottled) with stones of the aggregate in it;
the kinds differ in how much binder is left on top: fresh asphalt is nearly black with bitumen sheen, wear uncovers the
stones and fades the binder. The ordinary kind averages (53, 53, 53), the grey concrete the city's roads are made of
in the Artburg pack, so it sits next to them. Every texture tiles: noise, cracks and patches wrap around the edges.

    python tools/gen_asphalt.py
    python tools/gen_asphalt.py --preview out.png
"""
import json, os, sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

N = 32
VARIANTS = 4
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'main', 'resources', 'assets', 'artburgblocks')
TEX = os.path.join(ROOT, 'textures', 'blocks')


def rng(name, i):
    return np.random.default_rng(sum(ord(c) * 31 ** k for k, c in enumerate(name)) % 2 ** 32 * 101 + i)


def mottle(r, sigma, amp):
    s = ndi.gaussian_filter(r.normal(0, 1, (N, N)), sigma, mode='wrap')
    return s / max(s.std(), 1e-9) * amp


def surface(r, binder, stones, stone_lo, stone_hi, mottle_amp, mottle_sigma=2.5, tint=(1, 1, 1)):
    """Binder grey + mottling + stones of the aggregate (single texels, sometimes two), greyscale times tint."""
    g = binder + r.normal(0, 2.0, (N, N)) + mottle(r, mottle_sigma, mottle_amp)
    stone = r.random((N, N)) < stones
    twin = np.roll(stone, 1, 1) & (r.random((N, N)) < 0.25)          # a stone two texels long now and then
    stone |= twin
    g[stone] = r.uniform(stone_lo, stone_hi, stone.sum())
    return np.stack([g * t for t in tint], -1)


def level(img, target):
    """Shift so the average grey is exactly target."""
    return img + (target - img.mean())


def crack(r, img, value, width=1, length=(18, 36), wobble=0.45):
    """A wandering crack, wrapped around the edges so the texture still tiles."""
    y, x = r.uniform(0, N, 2)
    a = r.uniform(0, 2 * np.pi)
    for _ in range(int(r.integers(*length))):
        a += r.normal(0, wobble)
        y, x = y + np.sin(a), x + np.cos(a)
        for d in range(width):
            yy, xx = int(y + d * np.cos(a)) % N, int(x - d * np.sin(a)) % N
            img[yy, xx] = value if np.isscalar(value) else value[yy, xx]
        if r.random() < 0.03:                                         # a branch
            crack(r, img, value, 1, (5, 12), wobble)


def k_fresh(r):
    img = surface(r, 27, 0.05, 40, 52, 1.5, tint=(0.97, 0.98, 1.03))
    sheen = r.random((N, N)) < 0.025                                  # bitumen still glossy on top
    img[sheen] += np.array([20, 22, 26])
    return level(img, 30)


def k_new(r):
    return level(surface(r, 37, 0.10, 56, 74, 2.0), 41)


def k_normal(r):
    return level(surface(r, 47, 0.18, 66, 96, 3.5), 53)


def k_worn(r):
    return level(surface(r, 58, 0.30, 72, 98, 4.5, tint=(1.02, 1.0, 0.97)), 66)


def k_old(r):
    img = surface(r, 68, 0.32, 82, 106, 7.0, mottle_sigma=3.5, tint=(1.03, 1.0, 0.96))
    hair = img[..., 0].copy()
    g = img.mean(-1)
    for _ in range(int(r.integers(1, 3))):                            # hairline cracks, only a shade darker
        crack(r, hair, g - 18, 1, (10, 22), 0.6)
    img = img * (hair / np.maximum(img[..., 0], 1))[..., None]
    pits = r.random((N, N)) < 0.012
    img[pits] = 44
    return level(img, 76)


def k_patched(r, i=0):
    img = k_normal(r)
    if i >= 2:                                                        # half the blocks have no patch: no grid of them
        return img
    new = k_new(r)
    for _ in range(1):                                                # cut out and filled again with new asphalt
        h, w = int(r.integers(16, 27)), int(r.integers(14, 25))
        y0, x0 = int(r.integers(0, N)), int(r.integers(0, N))
        ys, xs = (np.arange(y0, y0 + h) % N), (np.arange(x0, x0 + w) % N)
        img[np.ix_(ys, xs)] = new[np.ix_(ys, xs)]
        for yy in (ys[0], ys[-1]):                                    # the sealed seam around the cut
            img[yy, xs] = 36
        for xx in (xs[0], xs[-1]):
            img[ys, xx] = 36
    return img


def k_sealed(r, i=0):
    img = level(surface(r, 64, 0.30, 78, 102, 5.0, tint=(1.02, 1.0, 0.97)), 70)
    seal = np.full((N, N), np.nan)
    for _ in range(0 if i == 3 else 1):                               # a crack filled with black sealant, wider
        crack(r, seal, 24.0, 2, (40, 60), 0.10)
    m = ~np.isnan(seal)
    img[m] = 24 + r.normal(0, 1.5, (m.sum(), 1))
    return img


KINDS = {
    'asphalt_fresh': k_fresh,
    'asphalt_new': k_new,
    'asphalt': k_normal,
    'asphalt_worn': k_worn,
    'asphalt_old': k_old,
    'asphalt_patched': k_patched,
    'asphalt_sealed': k_sealed,
}


def write_json(path, obj):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def textures(name):
    paint = KINDS[name]
    takes_i = paint.__code__.co_argcount == 2                          # kinds whose variants differ on purpose
    return [np.clip(np.round(paint(rng(name, i), i) if takes_i else paint(rng(name, i))), 0, 255).astype(np.uint8)
            for i in range(VARIANTS)]


def generate():
    for name in KINDS:
        variants = []
        for i, a in enumerate(textures(name)):
            tex = '%s_%d' % (name, i)
            Image.fromarray(a, 'RGB').save(os.path.join(TEX, tex + '.png'))
            write_json(os.path.join(ROOT, 'models', 'block', tex + '.json'),
                       {'parent': 'block/cube_all', 'textures': {'all': 'artburgblocks:blocks/' + tex}})
            variants += [{'model': 'artburgblocks:' + tex, **({'y': y} if y else {})} for y in (0, 90, 180, 270)]
        write_json(os.path.join(ROOT, 'blockstates', name + '.json'), {'variants': {'normal': variants}})
        write_json(os.path.join(ROOT, 'models', 'item', name + '.json'), {'parent': 'artburgblocks:block/%s_0' % name})
        print(name, 'mean %.1f' % np.mean([t.mean() for t in textures(name)]))


def preview(path):
    """Each kind as 4x4 blocks with the game's random variants and turns, after a flat (53,53,53) road plate."""
    S, pad = 4, 20
    cell = 4 * N * S
    names = ['road plate'] + list(KINDS)
    canvas = Image.new('RGB', (len(names) * (cell + pad) + pad, cell + 2 * pad), (236, 236, 232))
    for k, name in enumerate(names):
        if name == 'road plate':
            patch = np.full((4 * N, 4 * N, 3), 53, np.uint8)
        else:
            ts, r = textures(name), np.random.default_rng(k)
            patch = np.zeros((4 * N, 4 * N, 3), np.uint8)
            for bz in range(4):
                for bx in range(4):
                    patch[bz * N:(bz + 1) * N, bx * N:(bx + 1) * N] = np.rot90(ts[r.integers(VARIANTS)], r.integers(4))
        canvas.paste(Image.fromarray(patch).resize((cell, cell), Image.NEAREST), (pad + k * (cell + pad), pad))
    canvas.save(path)


# ---------------------------------------------------------------- road marking paint

PAINT = {'white': (238, 238, 232), 'yellow': (236, 186, 38), 'orange': (238, 128, 32),
         'blue': (38, 86, 184), 'red': (196, 42, 36)}
WEARS = ['fresh', 'normal', 'worn']
GRIME = np.array((92, 90, 86), float)


def marking(r, color, wear):
    """Paint on ordinary asphalt. Fresh: clean, with the sparkle of the glass beads in it. Normal: a little duller,
    a stone peeking through here and there. Worn: duller still, the paint gone in patches down to the asphalt."""
    c = np.array(PAINT[color], float)
    road = k_normal(r)
    grain = 1 + r.normal(0, 0.025, (N, N)) + mottle(r, 2.5, 0.015)
    if wear == 'fresh':
        img = c * grain[..., None]
        beads = r.random((N, N)) < 0.04
        img[beads] = np.minimum(img[beads] * 1.08 + 6, 255)
        return img
    if wear == 'normal':
        img = (c * 0.95 * 0.92 + GRIME * 0.08) * (grain + r.normal(0, 0.012, (N, N)))[..., None]
        peek = r.random((N, N)) < 0.012
    else:
        img = (c * 0.92 * 0.88 + GRIME * 0.12) * (grain + r.normal(0, 0.02, (N, N)))[..., None]
        s = ndi.gaussian_filter(r.random((N, N)), 1.6, mode='wrap')
        peek = (s > np.quantile(s, 0.90)) | (r.random((N, N)) < 0.03)
    img[peek] = road[peek]
    return img


def generate_markings():
    for color in PAINT:
        name = 'marking_' + color
        vs = {}
        for wear in WEARS:
            key = 'wear=' + wear
            vs[key] = []
            for i in range(VARIANTS):
                tex = '%s_%s_%d' % (name, wear, i)
                a = np.clip(np.round(marking(rng(name + wear, i), color, wear)), 0, 255).astype(np.uint8)
                Image.fromarray(a, 'RGB').save(os.path.join(TEX, tex + '.png'))
                write_json(os.path.join(ROOT, 'models', 'block', tex + '.json'),
                           {'parent': 'block/cube_all', 'textures': {'all': 'artburgblocks:blocks/' + tex}})
                vs[key] += [{'model': 'artburgblocks:' + tex, **({'y': y} if y else {})} for y in (0, 90, 180, 270)]
        write_json(os.path.join(ROOT, 'blockstates', name + '.json'), {'variants': vs})
        print(name, ', '.join('%s %.0f' % (w, marking(rng(name + w, 0), color, w).mean()) for w in WEARS))


def preview_markings(path):
    """Each colour: fresh, normal, worn as 2x2 blocks, on a strip of ordinary asphalt."""
    S, pad = 4, 16
    cell = 2 * N * S
    canvas = Image.new('RGB', (3 * (cell + pad) + pad, len(PAINT) * (cell + pad) + pad), (236, 236, 232))
    for row, color in enumerate(PAINT):
        for col, wear in enumerate(WEARS):
            r = np.random.default_rng(row * 3 + col)
            patch = np.zeros((2 * N, 2 * N, 3))
            for bz in range(2):
                for bx in range(2):
                    t = marking(rng('marking_' + color + wear, int(r.integers(VARIANTS))), color, wear)
                    patch[bz * N:(bz + 1) * N, bx * N:(bx + 1) * N] = np.rot90(t, r.integers(4))
            im = Image.fromarray(np.clip(patch, 0, 255).astype(np.uint8)).resize((cell, cell), Image.NEAREST)
            canvas.paste(im, (pad + col * (cell + pad), pad + row * (cell + pad)))
    canvas.save(path)


if __name__ == '__main__':
    generate()
    generate_markings()
    if '--preview' in sys.argv:
        out = sys.argv[sys.argv.index('--preview') + 1]
        preview(out)
        preview_markings(out.replace('.png', '_marking.png'))
