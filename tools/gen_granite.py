"""Copies of SBM's white granite (sbm:belygranit) in other brightnesses: textures, models, blockstates.

The texture is taken from the SBM jar on the server, so the copies are the same slabs, only lighter or darker.
Darker = every texel times the factor. Lighter = towards white (255 - (255 - c) * k, k chosen so the average is the
factor times the original's), so the light grains do not burn out into flat white.

    python tools/gen_granite.py
"""
import io, json, os, zipfile
import numpy as np
from PIL import Image

SBM_JAR = r"E:\Artburg Server\mods\SBM+ARTBURG2.9.3.jar"
SOURCE = "assets/sbm/textures/blocks/bely_granit_1.png"
LEVELS = [60, 70, 80, 90, 110, 120]           # percent of the original's brightness; 100 is sbm:belygranit itself

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src', 'main', 'resources', 'assets', 'artburgblocks')


def write_json(path, obj):
    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, indent=2)
        f.write('\n')


def shade(rgb, factor):
    if factor <= 1:
        return rgb * factor
    m = rgb.mean()
    k = (255 - factor * m) / (255 - m)
    return 255 - (255 - rgb) * k


def main():
    src = np.asarray(Image.open(io.BytesIO(zipfile.ZipFile(SBM_JAR).read(SOURCE))).convert('RGB'), float)
    for level in LEVELS:
        name = 'belygranit_%d' % level
        out = np.clip(np.round(shade(src, level / 100.0)), 0, 255).astype(np.uint8)
        Image.fromarray(out, 'RGB').save(os.path.join(ROOT, 'textures', 'blocks', name + '.png'), optimize=True)
        write_json(os.path.join(ROOT, 'models', 'block', name + '.json'),
                   {'parent': 'block/cube_all', 'textures': {'all': 'artburgblocks:blocks/' + name}})
        write_json(os.path.join(ROOT, 'models', 'item', name + '.json'), {'parent': 'artburgblocks:block/' + name})
        write_json(os.path.join(ROOT, 'blockstates', name + '.json'), {'variants': {'normal': {'model': 'artburgblocks:' + name}}})
        print(name, 'mean %.1f (original %.1f)' % (out.mean(), src.mean()))


if __name__ == '__main__':
    main()
