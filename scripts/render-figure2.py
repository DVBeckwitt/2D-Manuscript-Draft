"""Rebuild Figure 2 as vector geometry plus the unmodified archived detector image.

The schematic is deliberately not a detector calibration or scattering calculation.
A/B/C identify image locations, not crystallographic indices. No raster intensity
is reconstructed, recolored, fitted, smoothed, or independently normalized.
"""
from pathlib import Path
import hashlib
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch, Circle
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "figure2_revision"
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / "figures/intro/detector_2d_powder_biggerB_4deg_2m.png"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                     "svg.fonttype": "none", "pdf.fonttype": 42})
INK, MUTED = "#22313D", "#61707C"
BLUE, AMBER, TEAL = "#176BB0", "#C97716", "#187D83"
fig = plt.figure(figsize=(12, 5.65), facecolor="white")
ax = fig.add_axes([0, 0, 1, 1], xlim=(0, 12), ylim=(0, 5.65))
ax.set_aspect("equal")
ax.axis("off")

def text(x, y, label, size=11, color=INK, **kw):
    return ax.text(x, y, label, fontsize=size*1.22, color=color, **kw)

def line(points, color=MUTED, width=1, **kw):
    p = np.array(points)
    ax.plot(p[:, 0], p[:, 1], color=color, lw=width, **kw)

def arrow(start, end, color=INK, width=1.5, size=12, **kw):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>",
                               mutation_scale=size, lw=width, color=color,
                               shrinkA=0, shrinkB=0, **kw))

def badge(x, y, label, color=INK):
    ax.add_patch(Circle((x, y), .105, fc="white", ec=color, lw=1.2, zorder=12))
    text(x, y-.004, label, size=9, color=color, weight="bold",
         ha="center", va="center", zorder=13)

text(.18, 5.36, "(a)  Beam, film and detector", 14, weight="bold")
text(6.52, 5.36, r"(b)  Measured PbI$_2$ pattern", 14, weight="bold")
line([(6.22,.40),(6.22,5.13)], color="#DCE3E7", width=.8)

# An affine projection of one schematic detector plane. All ray endpoints
# share that plane. Its coordinates and the sample sketch carry no calibration.
bl = np.array([3.52, 2.03])
u = np.array([2.26, -.38])
v = np.array([0, 2.91])
face = np.array([bl, bl+u, bl+u+v, bl+v])
ax.add_patch(Polygon(face + [.09,.08], fc="#DCE3E7", ec="#80919D", lw=.8, zorder=1))
ax.add_patch(Polygon(face, fc="#F0F4F6", ec="#627784", lw=1.2, zorder=2))
for f in (.25,.5,.75):
    line([bl+f*u,bl+f*u+v], "#D8E1E6", .65, zorder=3)
    line([bl+f*v,bl+f*v+u], "#D8E1E6", .65, zorder=3)
text(4.6, 4.98, "Area detector", 11, ha="center")

# Film and substrate, with an incident ray ending on the upper face.
surface = np.array([[1.24,.88],[2.98,.61],[3.53,1.15],[1.80,1.43]])
ax.add_patch(Polygon(np.vstack([surface[:3],surface[2]+[0,-.14],
                               surface[1]+[0,-.14],surface[0]+[0,-.14]]),
                    fc="#C8D2D8", ec="#7E8F9B", lw=.9, zorder=4))
ax.add_patch(Polygon(surface, fc="#BFE1DC", ec=TEAL, lw=1.2, zorder=5))
sample = np.array([2.36,1.04])
arrow((.28,1.54), sample, BLUE, 3, 17, zorder=7)
text(.35,1.86,"Incident beam",12,color=BLUE)
text(1.00,1.41,r"$\mathbf{k}_i$",14,color=BLUE)
arrow(sample+[0,.04], sample+[0,1.04], TEAL, 1.4, 11, zorder=7)
text(2.20,2.22,"Film normal",10,color=TEAL,ha="center")
text(2.34,.35,"Thin film on substrate",11,ha="center")

# Feature picks are qualitative locations in the existing 407 x 407 display.
# Rays and identifiers are annotations only, with no width/intensity meaning.
picks = {"A": (40, 305), "B": (204, 310), "C": (367, 305)}
for label, (px, py) in picks.items():
    end = bl + (px/406)*u + (1-py/406)*v
    arrow(sample, end, AMBER, 1.55, 11, zorder=8)
    ax.plot(*end,"o",ms=3.7,color=AMBER,zorder=9)
    badge(*(end+[.00,.21]),label)
text(3.18,1.34,r"$\mathbf{k}_f$",14,color=AMBER)
text(.37,3.64,"Scattered rays",12,color=AMBER)
text(.37,3.35,"Each direction maps to\na detector position.",10.5,
     color=MUTED,linespacing=1.45,va="top")

# Display the source unchanged and at its native aspect ratio. The SVG/PDF
# embeds the source image rather than vectorizing or estimating its intensities.
im = np.asarray(Image.open(SOURCE).convert("RGB"))
x0,y0,w = 6.73,.70,4.15
ax.imshow(im, extent=(x0,x0+w,y0,y0+w), interpolation="nearest", zorder=1)
ax.add_patch(Polygon([[x0,y0],[x0+w,y0],[x0+w,y0+w],[x0,y0+w]],
                    fill=False,ec="#B8C5CF",lw=.7,zorder=3))
def loc(px,py):
    return np.array([x0+(px+.5)*w/407,y0+(406.5-py)*w/407])
for label, (px,py) in picks.items():
    p = loc(px,py)
    offset = np.array([.30,.23]) if label != "C" else np.array([-.30,.23])
    anchor = p+offset
    line([p,anchor],"white",.9,zorder=9)
    badge(*anchor,label)

# Two external feature descriptions keep the original intensity visible.
text(8.84,.30,"A, C: off-specular peaks    B: axial peak",10.5,ha="center")
text(11.12,3.90,"Intensity\nbetween\npeaks",10,va="top",linespacing=1.25)
target = loc(370,253)
line([target,(10.99,target[1]),(11.04,3.17)],"#6F7E89",.9,zorder=9)
text(11.12,1.38,"Axial\nstreak",10,va="top",linespacing=1.25)
target2 = loc(204,344)
line([target2,(10.99,target2[1]),(11.04,.98)],"#6F7E89",.9,zorder=9)

fig.canvas.draw()
clipped = [t.get_text() for t in ax.texts
           if not fig.bbox.contains(t.get_window_extent().x0,t.get_window_extent().y0)
           or not fig.bbox.contains(t.get_window_extent().x1,t.get_window_extent().y1)]
if clipped:
    raise ValueError(f"Text extends outside figure: {clipped}")

fig.savefig(OUT/"Figure_2_revised.svg", facecolor="white")
fig.savefig(OUT/"Figure_2_revised.pdf", facecolor="white")
fig.savefig(OUT/"Figure_2_revised.png", dpi=220, facecolor="white")
plt.close(fig)
(OUT/"provenance.json").write_text(json.dumps({
    "source_image": str(SOURCE.relative_to(ROOT)),
    "source_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "source_size_pixels": [im.shape[1],im.shape[0]],
    "display_processing": "Native RGB image, nearest-neighbor display, no intensity change",
    "schematic": "Uncalibrated affine detector-plane drawing and guide rays",
    "feature_picks_display_pixels": picks,
    "feature_identifiers": "A/B/C are guide markers, not Miller indices",
    "scope": "Qualitative measured-image overview, not a new model calculation or fit"
},indent=2)+"\n")
print(OUT / "Figure_2_revised.png")
