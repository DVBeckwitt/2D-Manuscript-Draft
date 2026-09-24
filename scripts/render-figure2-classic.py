"""Polish the original Figure 2 composition using its native source geometry.

Preserves the detector pose, sample slab, incident arrow and nine outgoing beams.
The projected raster is a qualitative display. Indices use retained PbI2 records.
"""
from pathlib import Path
import importlib.util
import sys
import json
import hashlib

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, FancyArrowPatch
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output/figure2_classic"
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / "figures/intro/detector_2d_powder_biggerB_4deg_2m.png"
helper_path = ROOT / "figures/intro/Fig1H_maker.py"
spec = importlib.util.spec_from_file_location("fig2_original", helper_path)
helper = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = helper
spec.loader.exec_module(helper)

plt.rcParams.update({"font.family":"DejaVu Sans", "pdf.fonttype":42,
                     "svg.fonttype":"none"})
fig = plt.figure(figsize=(8.2, 8.2*970/1080), facecolor="white")
ax = fig.add_axes([0,0,1,1], xlim=(160,1240), ylim=(990,20), aspect="equal")
ax.axis("off")
INK, EDGE, BLUE, AMBER = "#263541", "#768490", "#2467A5", "#C17A24"

def poly(points, fill, z=2, lw=.8):
    ax.add_patch(Polygon(points, closed=True, fc=fill, ec=EDGE, lw=lw,
                         joinstyle="round", zorder=z))

def label(x,y,s,size=12,color=INK,**kw):
    return ax.text(x,y,s,fontsize=size,color=color,va="center",**kw)

def segment(a,b,color=INK,width=.8,z=10,**kw):
    ax.plot([a[0],b[0]],[a[1],b[1]],color=color,lw=width,zorder=z,
            solid_capstyle="round",**kw)

face = np.asarray(helper.DEFAULT_FACE_CORNERS,float)
tl,tr,br,bl = face
depth = np.array([28.,-18.])
poly([tl,tr,tr+depth,tl+depth],"#DCE2E6")
poly([tr,tr+depth,br+depth,br],"#C0CAD1")

# Reuse the original project's homography, at increased display sampling.
# This resamples RGB for perspective only. It does not recover raw counts.
scale=2
base=Image.new("RGBA",(1448*scale,1086*scale),(255,255,255,0))
helper.paste_perspective_image_to_quad(base,Image.open(SOURCE),face*scale)
ax.imshow(np.asarray(base),extent=(0,1448,1086,0),zorder=3,interpolation="none")
ax.add_patch(Polygon(face,fill=False,ec=EDGE,lw=.95,zorder=4,joinstyle="round"))

# The slab and source/sample intersection retain their original positions.
poly([(480,892),(748,925),(748,948),(480,915)],"#B7C1C9",5)
poly([(820,835),(748,925),(748,948),(840,858)],"#C6CFD5",5)
poly([(565,815),(820,835),(748,925),(480,892)],"#E3E8EB",6)
tail=np.array(helper.DEFAULT_TAIL,float)
peaks=helper.default_peaks()+[
    helper.Peak(406-368.51,273.04,"B7"),
    helper.Peak(406-373.13,197.05,"B8"),
    helper.Peak(406-375.12,101.91,"B9")]
peaks=helper.snap_peaks_to_local_maxima(peaks,helper.detector_intensity_map(SOURCE,2),14)
H=helper.compute_homography(np.array([[0,0],[406,0],[406,406],[0,406]],float),face)
heads=helper.map_points(H,[(p.x,p.y) for p in peaks])

# Restrained translucent cones retain the old scene's visual language.
# Smoothly taper the ends to avoid the previous hard triangular caps.
rgba=np.zeros((1086*scale,1448*scale,4),dtype=np.float32)
rgba[:,:,:3]=matplotlib.colors.to_rgb(AMBER)
for p,head in zip(peaks,heads):
    sigma=helper.projected_perpendicular_sigma(H,(p.x,p.y),tail,5.,5.)
    ys,xs,a=helper.cone_alpha_mask(rgba.shape[:2],tuple(tail*scale),tuple(head*scale),
                                 .65*scale,sigma*scale,.22,3.,.4)
    yy,xx=np.mgrid[ys,xs]
    delta=(head-tail)*scale
    s=((xx-tail[0]*scale)*delta[0]+(yy-tail[1]*scale)*delta[1])/np.dot(delta,delta)
    a*=np.clip((1-s)/.035,0,1)
    old=rgba[ys,xs,3]
    rgba[ys,xs,3]=1-(1-old)*(1-a)
ax.imshow(rgba,extent=(0,1448,1086,0),interpolation="none",zorder=7)
for head in heads:
    segment(tail,head,AMBER,.55,8,alpha=.34)

# A crisp blue incident arrow replaces the pixelated, heavily shadowed arrow.
ax.add_patch(FancyArrowPatch((215,958),tail,arrowstyle="Simple,tail_width=4.3,head_width=15,head_length=20",
                            color=BLUE,lw=0,zorder=9,shrinkA=0,shrinkB=0))
label(278,900,r"$\mathbf{k}_i$",20,BLUE)
label(708,791,r"$\mathbf{k}_f$",20,AMBER)

# Keep the original point IDs internally; label representative PbI2 reflections.
# Source registration and CIF-setting evidence: output/figure2_classic/indexing_evidence.json.
indices = {
    "B1": ("001", "2H"), "B2": ("002", "2H"), "B3": ("003", "2H"),
    "B4": ("104", "6H"), "B5": ("102", "2H"), "B6": ("018", "6H"),
    "B7": ("104", "6H"), "B8": ("102", "2H"), "B9": ("018", "6H"),
}
for p,head in zip(peaks,heads):
    direction=-1 if p.label in ("B4","B5","B6") else 1
    anchor=head+np.array([direction*58,-24])
    segment(head,anchor,"#F1F4F5",.65)
    hkl, polytype = indices[p.label]
    label(*anchor,rf"$({hkl})_{{\mathrm{{{polytype}}}}}$",11.5,INK,ha="center",zorder=12,
          bbox={"boxstyle":"round,pad=0.21,rounding_size=0.14",
                "facecolor":"white","edgecolor":"none","alpha":.95})

label(424,292,"Area detector",13,ha="right")
segment((431,305),(458,330),INK,.8)
ax.plot(458,330,"o",ms=3.5,mec="white",mew=.6,color=INK,zorder=12)
label(883,877,"Sample",13)
segment((760,885),(868,877),INK,.8)
ax.plot(760,885,"o",ms=3.5,mec="white",mew=.6,color=INK,zorder=12)

fig.canvas.draw()
for t in ax.texts:
    bounds=t.get_window_extent()
    assert fig.bbox.contains(bounds.x0,bounds.y0) and fig.bbox.contains(bounds.x1,bounds.y1),t.get_text()
for ext in ("pdf","svg","png"):
    fig.savefig(OUT/f"Figure_2_classic.{ext}",dpi=300,facecolor="white")
plt.close(fig)
(OUT/"provenance.json").write_text(json.dumps({
    "source":str(SOURCE.relative_to(ROOT)),
    "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "original_generator":str(helper_path.relative_to(ROOT)),
    "original_generator_sha256":hashlib.sha256(helper_path.read_bytes()).hexdigest(),
    "detector_face":face.tolist(),"sample_hit":tail.tolist(),
    "labels":[{"original_id":p.label,"hkl":indices[p.label][0],"polytype":indices[p.label][1],"source_xy":[p.x,p.y],"drawing_xy":h.tolist()} for p,h in zip(peaks,heads)],
    "indexing_evidence":"indexing_evidence.json",
    "scope":"Original single-scene composition with representative PbI2 reflection indices. Axial 2H labels approximately coincide with 6H 003/006/009. Positional assignments do not establish phase fractions. Beam cones do not encode physical broadening.",
    "raster_processing":"Original RGB image mapped by the original bilinear homography. No recoloring, intensity reconstruction or fitting. Translucent cones are illustration overlays."
},indent=2)+"\n")
print(OUT/"Figure_2_classic.png")
