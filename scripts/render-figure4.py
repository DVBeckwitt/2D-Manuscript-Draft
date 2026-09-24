"""Compact measured detector strip with vector annotations; no data reconstruction."""
from pathlib import Path
import hashlib
import io
import json
import shutil
import zipfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'output/figure4_revision'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT/'figures/results_ordered/starshape.pptx'
with zipfile.ZipFile(SOURCE) as archive:
    source_bytes = archive.read('ppt/media/image2.png')
source = np.array(Image.open(io.BytesIO(source_bytes)).convert('RGB'))
# Native-pixel crop removes quiet edge rows and the extreme left boundary.
# Preserve the full radial interval containing reflectivity, 003 and 006.
box = (4, 8, 327, 90)
x0, y0, x1, y1 = box
crop = source[y0:y1, x0:x1].copy()
Image.fromarray(crop).save(OUT/'detector_crop.png')
assert np.array_equal(np.array(Image.open(OUT/'detector_crop.png')), source[y0:y1, x0:x1])
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                     'mathtext.fontset': 'dejavusans', 'pdf.fonttype': 42,
                     'svg.fonttype': 'none'})
fig = plt.figure(figsize=(7.2, 2.12), facecolor='white')
ax = fig.add_axes([.060, .20, .922, .776])
ax.imshow(crop, origin='upper', extent=(x0, x1, y1, y0), interpolation='none', aspect='equal')
ax.set(xlim=(x0, x1), ylim=(y1, y0))
ax.set_xticks([]); ax.set_yticks([])
for spine in ax.spines.values():
    spine.set_linewidth(.55)
    spine.set_edgecolor('#777777')

# Peak coordinates are visual annotations in the archived RGB detector strip,
# not fitted peak positions or angular calibration.
ax.text(22, 20, 'Reflectivity', color='white', fontsize=8.2, ha='left')
ax.annotate('', (14, 41), (26, 25),
            arrowprops={'arrowstyle': '-', 'color': 'white', 'lw': .65})
ax.text(116, 25, '003', color='white', fontsize=9, ha='center')
ax.text(237, 25, '006', color='white', fontsize=9, ha='center')
# Labeled extents replace ambiguous direction arrows. These are illustrative
# feature markers, not fitted widths or integration windows.
ax.plot([120, 120, 171, 171], [61, 65, 65, 61], color='white', lw=.8)
ax.text(145.5, 77, 'Radial streak', color='white', fontsize=9, ha='center')
ax.annotate('', (97, 33), (97, 61),
            arrowprops={'arrowstyle': '<->', 'color': 'white', 'lw': .85})
ax.text(87, 46, 'Transverse\nmosaic width', color='white', fontsize=8.5,
        ha='right', va='center', linespacing=1.12)
ax.set_xlabel(r'Radial $2\theta$', labelpad=5, fontsize=9)
ax.set_ylabel(r'Transverse $\phi_f$', labelpad=5, fontsize=9)

fig.canvas.draw()
renderer = fig.canvas.get_renderer()
for label in fig.findobj(matplotlib.text.Text):
    if label.get_text() and label.get_visible():
        bounds = label.get_window_extent(renderer)
        assert bounds.x0 >= 0 and bounds.y0 >= 0
        assert bounds.x1 <= fig.bbox.width and bounds.y1 <= fig.bbox.height
for ext in ['pdf', 'svg', 'png']:
    fig.savefig(OUT/f'Figure_4_compact.{ext}', dpi=360)
audit = {'source': str(SOURCE.relative_to(ROOT)), 'embedded_image': 'ppt/media/image2.png',
         'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
         'embedded_image_sha256': hashlib.sha256(source_bytes).hexdigest(),
         'source_dimensions': list(source.shape[:2][::-1]),
         'crop_box_xyxy': box, 'crop_dimensions': list(crop.shape[:2][::-1]),
         'crop_pixels_exact': True, 'color_mapping': 'Archived RGB unchanged; no new intensity scale',
         'annotations': 'Radial-streak bracket and transverse mosaic-width marker are illustrative extents, not measured widths or integration bounds. Model mechanism is stated in caption.',
         'canvas_inches': [7.2, 2.12], 'all_labels_inside_canvas': True,
         'height_reduction_at_equal_width_percent': 100*(1-2.12/(7.2*450/1325)),
         'scope': 'Presentation-only crop and vector labels; no counts, fitting or intensity reconstruction'}
(OUT/'verification.json').write_text(json.dumps(audit, indent=2)+'\n', encoding='utf-8')
shutil.copyfile(OUT/'Figure_4_compact.pdf', ROOT/'figures/results_ordered/00L_region_compact.pdf')
shutil.copyfile(OUT/'Figure_4_compact.pdf', ROOT/'output/pdf/Figure_4_compact.pdf')
print(json.dumps(audit, indent=2))
