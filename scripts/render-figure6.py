"""Compose Figure 6 from archived scientific PDF image layers, without refitting."""
from pathlib import Path
import hashlib
import json
import math
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = Path('C:/Users/Kenpo/.codex/visualizations/2026/07/28/019fa948-8100-79b2-abc6-84b4e4747086/bi2se3-publication-final')
OUT = ROOT / 'output/figure6_revision'
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'source').mkdir(exist_ok=True)
manifest = json.loads((ARCHIVE / 'bi2se3-10deg-publication-manifest.json').read_text())
sources = {}
for name, stem in [('sphere_full', '02-painted-ewald-surface'), ('planar', '03-untilted-planar-mapping'), ('tilted', '04-tilted-detector-mapping')]:
    path = ARCHIVE / f'bi2se3-10deg-{stem}.pdf'
    layer = PdfReader(path).pages[0].images[0]
    target = OUT / 'source' / f'{name}.png'
    target.write_bytes(layer.data)
    sources[name] = {'pdf': str(path), 'pdf_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'layer_sha256': hashlib.sha256(layer.data).hexdigest(), 'pixels': list(layer.image.size)}

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 12, 'pdf.fonttype': 42, 'svg.fonttype': 'none'})
fig = plt.figure(figsize=(11.7, 3.3), facecolor='white')
panels = [(0.035, '(a)  Ewald sphere'), (0.37, '(b)  Reference detector'), (0.705, '(c)  Tilted detector')]
for x, title in panels:
    fig.text(x, .955, title, fontsize=14, weight='bold', va='top')

# The archived orthographic projection used z limits of 2.05 K and box
# aspect (1, 1, 1.08). Undo its screen-vertical stretch analytically.
vertical_scale = math.sqrt(math.sin(math.radians(18))**2 + (1.08 / 1.025)**2 * math.cos(math.radians(18))**2)
sphere = plt.imread(OUT / 'source/sphere_full.png')
corrected_ratio = sphere.shape[0] / sphere.shape[1] / vertical_scale
# Zero support uses the existing under-range black, rather than a gray cap.
# This changes only the zero-support display color, never computed intensity.
zero_rgb = np.array([119, 122, 125]) / 255
zero_support = np.all(np.abs(sphere[..., :3] - zero_rgb) < .5/255, axis=-1)
assert int(zero_support.sum()) == 88117
original = sphere.copy()
sphere[zero_support, :3] = 0
assert np.array_equal(sphere[~zero_support], original[~zero_support])
# The source camera puts the incident-aligned axis upright. In this
# left-to-right projection diagram it must point toward the detectors.
# Rotate the scientific layer exactly, without resampling its pixel values.
sphere = np.rot90(sphere, k=-1)
assert np.array_equal(np.rot90(sphere, k=1)[~zero_support], original[~zero_support])
ax = fig.add_axes([.045, .05, .255, .80])
ax.imshow(sphere, extent=[0, corrected_ratio, 0, 1], interpolation='none')
ax.set_aspect('equal'); ax.axis('off')
ray = json.loads((OUT / 'ray_correspondence.json').read_text())
point = ray['sphere_xy_fraction']
ax.plot(point[0]*corrected_ratio, point[1], 'o', ms=8, mfc='none', mec='white', mew=1.5)
ax.annotate('A', (point[0]*corrected_ratio, point[1]), xytext=(-17, 9), textcoords='offset points', color='white', weight='bold', fontsize=12)

for name, x in [('planar', .375), ('tilted', .71)]:
    ax = fig.add_axes([x, .195, .265, .535])
    # The source is detector-native: display with equal pixel scales.
    # Only the unused lower panel region is outside this shared viewport.
    ax.imshow(plt.imread(OUT / 'source' / f'{name}.png'), extent=[-.5, 2999.5, 2999.5, -.5], interpolation='none')
    ax.set_xlim(-.5, 2999.5); ax.set_ylim(1649.5, -.5); ax.set_aspect('equal')
    ax.set_xticks([0, 1500, 3000]); ax.set_yticks([0, 750, 1500])
    ax.tick_params(labelsize=10, length=3)
    ax.set_xlabel('Detector column (px)', fontsize=11, labelpad=3)
    if name == 'planar': ax.set_ylabel('Row (px)', fontsize=11, labelpad=2)
    for spine in ax.spines.values(): spine.set_linewidth(.7)
    if name == 'planar':
        col, row = ray['detector_column_row_px']
        ax.plot(col, row, 'o', ms=8, mfc='none', mec='white', mew=1.5)
        ax.annotate('A', (col, row), xytext=(8, 5), textcoords='offset points', color='white', weight='bold', fontsize=12)

fig.text(.5075, .80, 'Reference pose', ha='center', fontsize=11)
fig.text(.8425, .80, '20° row-axis tilt', ha='center', fontsize=11)
for start, end in [(.305, .356), (.648, .696)]:
    ax.annotate('', xy=(end, .76), xytext=(start, .76), xycoords=fig.transFigure,
                arrowprops={'arrowstyle': '-|>', 'color': '#51545a', 'lw': 1.3})

for suffix in ['pdf', 'svg', 'png']:
    fig.savefig(OUT / f'figure6_mapping.{suffix}', dpi=320)
target = ROOT / 'figures/geometry/ewald_intensity_to_detector_mapping_v2.pdf'
target.write_bytes((OUT / 'figure6_mapping.pdf').read_bytes())
sources['geometry'] = {'orthographic_vertical_stretch_removed': vertical_scale, 'sphere_rotation_clockwise_deg': 90, 'nonzero_sphere_pixels_preserved': True, 'zero_support_pixels_displayed_black': int(zero_support.sum()), 'corrected_sphere_height_over_width': 1 / corrected_ratio, 'detector_viewport_px': [0, 3000, 0, 1650], 'detector_aspect': 'equal', 'condition': manifest['settings'], 'numeric_intensities_modified': False, 'ray_correspondence': ray}
(OUT / 'source_manifest.json').write_text(json.dumps(sources, indent=2))
print(json.dumps(sources['geometry'], indent=2))
