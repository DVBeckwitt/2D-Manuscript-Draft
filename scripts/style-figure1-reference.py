"""Apply journal presentation to the author's restored Figure 1 geometry.

The archived drawing definitions supply every point, curve and arrow. Styling
cannot change any non-text shape coordinates; fingerprints enforce that boundary.
"""
from pathlib import Path
import hashlib
import json
import shutil
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from reportlab.graphics import renderPDF, renderSVG
from reportlab.graphics.shapes import String, Circle, Polygon, PolyLine

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'output/figure1_reference_journal'
OUT.mkdir(parents=True, exist_ok=True)
PDF = ROOT/'figures/intro/orientational_limits_reference_journal.pdf'
REFERENCE = ROOT/'output/figure1_redesign_v3/make_figure.py'
source = REFERENCE.read_text(encoding='utf-8')
definitions = source[:source.index('for letter,d in drawings.items():')]
reference = {'__file__': str(REFERENCE)}
exec(compile(definitions, str(REFERENCE), 'exec'), reference)
drawings = reference['drawings']

for name, filename in [('Sans', 'DejaVuSans.ttf'), ('Sans-Bold', 'DejaVuSans-Bold.ttf'),
                       ('Sans-Oblique', 'DejaVuSans-Oblique.ttf')]:
    pdfmetrics.registerFont(TTFont(name, str(ROOT/'output/figure1_journal/fonts'/filename)))

INK, TEAL, AMBER, BLUE = '#151515', '#087D88', '#C17A24', '#2467A5'
PALETTE = {'#183442': INK, '#15877e': TEAL, '#da942c': AMBER, '#428ec1': BLUE,
           '#62aa9e': TEAL, '#8b65a7': '#79529D', '#668897': INK}
W, H = 620, 476
PRINT_SCALE = 468/W  # Current manuscript: 6.5-inch text width.

def hexcolor(c):
    return '#'+''.join(f'{round(v*255):02x}' for v in (c.red, c.green, c.blue))

def geometry(drawing):
    result = []
    for shape in drawing.contents:
        if isinstance(shape, String):
            continue
        values = shape.getProperties()
        result.append({'type': type(shape).__name__, **{key: values[key] for key in
                       ['points', 'cx', 'cy', 'r', 'x', 'y', 'width', 'height', 'transform']
                       if key in values}})
    return json.dumps(result, sort_keys=True)

baseline = {letter: geometry(d) for letter, d in drawings.items()}
bounds = {letter: d.getBounds() for letter, d in drawings.items()}
placements = {}
emphasis = {}
for letter, d in drawings.items():
    x0, y0, x1, y1 = bounds[letter]
    box = [x0-3, y0-3, x1+3, y1+3]
    s = min(214/(box[2]-box[0]), 126/(box[3]-box[1]))
    placements[letter] = {'bounds': box, 'scale': s}
    emphasis[letter] = {'selected_points': 0, 'intersection_segments': 0, 'faded_guides': 0}
    labels = []
    for shape in d.contents:
        if isinstance(shape, String):
            labels.append(shape)
            shape.fontName = 'Sans'
            shape.fontSize = (8.8 if shape.text in ['z', 'i'] else 12)/s
            shape.fillColor = HexColor(PALETTE.get(hexcolor(shape.fillColor), INK))
            if shape.text in ['a', 'b', 'c', 'Q']:
                shape.fontName = 'Sans-Oblique'
            elif shape.text == 'k':
                shape.fontName = 'Sans-Bold'
            continue
        selected_point = (isinstance(shape, Circle) and 2.5 < shape.r < 10
                          and hexcolor(shape.fillColor) == '#183442')
        intersection_segment = (letter == 'd' and isinstance(shape, PolyLine)
                                and len(shape.points) == 4
                                and hexcolor(shape.strokeColor) in ['#15877e', '#da942c'])
        # Facet shading is cosmetic; all specimen vertices and arrow endpoints
        # remain the author's original values.
        if isinstance(shape, Polygon) and hexcolor(shape.strokeColor) == '#236457':
            tone = .46 + .38*shape.fillColor.green
            shape.fillColor = HexColor('#'+''.join(f'{round(v*255):02x}' for v in
                                                  [tone*.94, tone, tone*1.02]))
            shape.strokeColor = HexColor('#53636A')
        for attr in ['strokeColor', 'fillColor']:
            value = getattr(shape, attr, None)
            if value is not None and hexcolor(value) in PALETTE:
                setattr(shape, attr, HexColor(PALETTE[hexcolor(value)]))
        # Keep fine construction lines reproducible at the current print size.
        if hasattr(shape, 'strokeWidth') and (not isinstance(shape, Circle) or shape.r > 10):
            shape.strokeWidth = max(shape.strokeWidth, .5/(s*PRINT_SCALE))
        if selected_point:
            shape.fillColor = HexColor('#000000')
            shape.strokeWidth = .85
            emphasis[letter]['selected_points'] += 1
        if intersection_segment:
            shape.strokeWidth *= 1.3
            emphasis[letter]['intersection_segments'] += 1
        if getattr(shape, 'strokeDashArray', None):
            shape.strokeOpacity *= .60
            emphasis[letter]['faded_guides'] += 1
    # Re-space only typographic subscripts after changing font metrics.
    if letter == 'd':
        beam_label = next(x for x in labels if x.text == 'k')
        beam_label.x -= 23
        beam_label.y += 7
    for base, sub in [('Q', 'z'), ('k', 'i')]:
        main = next((x for x in labels if x.text == base), None)
        small = next((x for x in labels if x.text == sub), None)
        if main is not None and small is not None:
            small.x = main.x + pdfmetrics.stringWidth(base, main.fontName, main.fontSize)
            small.y = main.y-main.fontSize*.23
    for label in labels:
        if label.text == 'O':
            label.y -= 4
    assert geometry(d) == baseline[letter], f'Geometry changed in panel {letter}'
    renderSVG.drawToFile(d, str(OUT/f'panel_{letter}.svg'))

c = canvas.Canvas(str(PDF), pagesize=(W, H), pageCompression=1)
c.setTitle('Diffraction across three orientational limits')

def text(x, top, value, size=12, bold=False):
    c.setFillColor(HexColor(INK))
    c.setFont('Sans-Bold' if bold else 'Sans', size)
    c.drawString(x, H-top-size*.82, value)

def flow_arrow(x0, x1, top):
    """A reading-order annotation in the gutter, outside the scientific panels."""
    y = H-top
    c.setStrokeColor(HexColor('#53636A'))
    c.setLineWidth(.9)
    c.line(x0, y, x1, y)
    c.line(x1-3.8, y+2.5, x1, y)
    c.line(x1-3.8, y-2.5, x1, y)

for x, title in [(12, 'Real space'), (232, 'Reciprocal space'), (438, 'Detector space')]:
    text(x, 5, title, 12)

detectors = {}
for row, (top, title, letters) in enumerate(zip([28, 176, 324],
        ['Single crystal', '3D powder', '2D powder'],
        [('a', 'b', None), ('c', 'd', 'e'), ('f', 'g', 'h')])):
    text(12, top, title, 12, True)
    text(232, top, ['Discrete points', 'Spherical shells', 'Azimuthal rings'][row], 11)
    flow_arrow(236, 264, top+82)
    flow_arrow(420, 449, top+82)
    for col, letter in enumerate(letters):
        x, y = [12, 232, 438][col], top+18
        if letter is None:
            text(x+23, top+75, 'Sparse spots', 11)
            continue
        text(x, y, f'({letter})', 12, True)
        if letter in drawings:
            x0, y0, x1, y1 = placements[letter]['bounds']
            s = placements[letter]['scale']
            px = x+(214-s*(x1-x0))/2
            py = H-y-126+(126-s*(y1-y0))/2
            c.saveState()
            c.translate(px-s*x0, py-s*y0)
            c.scale(s, s)
            renderPDF.draw(drawings[letter], c, 0, 0)
            c.restoreState()
        else:
            filename = 'detector_3d_powder_hbn.png' if letter == 'e' else 'detector_2d_powder_biggerB_4deg_2m.png'
            src = ROOT/'figures/intro'/filename
            original = Image.open(src).convert('RGBA')
            crop = (21, 21, 411, 419) if letter == 'e' else (0, 0, original.width, original.height)
            im = original.crop(crop)
            assert np.array_equal(np.asarray(im), np.asarray(original)[crop[1]:crop[3], crop[0]:crop[2]])
            s = min(125/im.width, 125/im.height)
            width, height = im.width*s, im.height*s
            image_x = x+23+(125-width)/2
            image_y = H-y-126+(125-height)/2
            c.drawImage(ImageReader(im), image_x, image_y, width, height, mask='auto')
            c.saveState()
            c.setFillColor(HexColor('#FFFFFF'))
            c.setFont('Sans', 11)
            c.drawRightString(image_x+width-6, image_y+8,
                              'h-BN' if letter == 'e' else 'PbI\u2082')
            c.restoreState()
            detectors[letter] = {'source_sha256': hashlib.sha256(src.read_bytes()).hexdigest(),
                                 'crop': crop, 'retained_pixels_unchanged': True}
c.showPage()
c.save()
report = {
    'reference': str(REFERENCE.relative_to(ROOT)),
    'reference_source_sha256': hashlib.sha256(REFERENCE.read_bytes()).hexdigest(),
    'geometry_unchanged': True,
    'communication': {'direct_labels': ['Discrete points', 'Spherical shells', 'Azimuthal rings'],
                      'inter_column_arrows': 6, 'emphasis': emphasis,
                      'detector_material_labels': {'e': 'h-BN', 'h': 'PbI2'},
                      'material_label_style': {'position': 'inside_bottom_right',
                                               'color': '#FFFFFF', 'right_inset_pt': 6,
                                               'baseline_inset_pt': 8},
                      'column_heading_weight': 'regular'},
    'geometry_sha256': {k: hashlib.sha256(v.encode()).hexdigest() for k, v in baseline.items()},
    'detectors': detectors,
    'layout': {'width': W, 'height': H, 'previous_width': 620, 'previous_height': 534,
               'placements': placements, 'mathematical_label_pt_at_6_5in': 12*PRINT_SCALE},
    'scope': 'Presentation only. Original cameras, points, curves, radii and arrow endpoints retained.',
}
(OUT/'verification.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
shutil.copy2(PDF, ROOT/'output/pdf/Figure_1_reference_journal.pdf')
print(json.dumps({'pdf': str(PDF), 'geometry_unchanged': True, 'size': [W, H]}, indent=2))
