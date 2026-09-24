"""Polish the original Figure 2 composition using its native source geometry.

Preserves the detector pose, sample slab and nine diffraction rays.
The projected raster and beam-center ray form a qualitative measurement schematic.
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
OUT = ROOT / "output/figure2_journal"
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / "figures/intro/detector_2d_powder_biggerB_4deg_2m.png"
helper_path = ROOT / "figures/intro/Fig1H_maker.py"
spec = importlib.util.spec_from_file_location("fig2_original", helper_path)
helper = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = helper
spec.loader.exec_module(helper)

plt.rcParams.update({"font.family":"DejaVu Sans", "pdf.fonttype":42,
                     "svg.fonttype":"none"})
fig = plt.figure(figsize=(8.2*870/1080, 8.2*910/1080), facecolor="white")
ax = fig.add_axes([0,0,1,1], xlim=(350,1220), ylim=(910,0), aspect="equal")
ax.axis("off")
INK, EDGE, BLUE, AMBER = "#263541", "#8B969E", "#368EC2", "#D3933E"

def poly(points, fill, z=2, lw=.6):
    ax.add_patch(Polygon(points, closed=True, fc=fill, ec=EDGE, lw=lw,
                         joinstyle="round", zorder=z))

def label(x,y,s,size=12,color=INK,**kw):
    return ax.text(x,y,s,fontsize=size,color=color,va="center",**kw)

def segment(a,b,color=INK,width=.8,z=10,**kw):
    ax.plot([a[0],b[0]],[a[1],b[1]],color=color,lw=width,zorder=z,
            solid_capstyle="round",**kw)

face = np.asarray(helper.DEFAULT_FACE_CORNERS,float)
tl,tr,br,bl = face
depth = np.array([12.,-8.])
poly([tl,tr,tr+depth,tl+depth],"#E7EBEE")
poly([tr,tr+depth,br+depth,br],"#D5DDE2")

# Render actual native counts, using one global display mapping for the crop.
counts = np.load(OUT / "detector_counts.npz")["counts"]
source_info = json.loads((OUT / "detector_source.json").read_text())
texture = Image.fromarray(matplotlib.colormaps["turbo"](
    matplotlib.colors.Normalize(0, 2000, clip=True)(counts), bytes=True))
texture.save(OUT / "detector_native_display.png")
# Reuse the detector pose; resample RGB only for perspective projection.
scale=2
base=Image.new("RGBA",(1448*scale,1086*scale),(255,255,255,0))
helper.paste_perspective_image_to_quad(base,texture,face*scale)
ax.imshow(np.asarray(base),extent=(0,1448,1086,0),zorder=3,interpolation="none")
ax.add_patch(Polygon(face,fill=False,ec=EDGE,lw=.65,zorder=4,joinstyle="round"))

# Preserve the sample face and position, with a thinner schematic edge.
shift=np.array([0.,-60.])
poly(np.array([(480,892),(748,925),(748,936),(480,903)])+shift,"#D0D8DE",5)
poly(np.array([(820,835),(748,925),(748,936),(820,846)])+shift,"#DCE2E6",5)
poly(np.array([(565,815),(820,835),(748,925),(480,892)])+shift,"#ECF0F2",6)
tail=np.array(helper.DEFAULT_TAIL,float)+shift
peaks=helper.default_peaks()+[
    helper.Peak(406-368.51,273.04,"B7"),
    helper.Peak(406-373.13,197.05,"B8"),
    helper.Peak(406-375.12,101.91,"B9")]
peaks=helper.snap_peaks_to_local_maxima(peaks,helper.detector_intensity_map(SOURCE,2),14)
H=helper.compute_homography(np.array([[0,0],[406,0],[406,406],[0,406]],float),face)
index_evidence=json.loads((ROOT / "output/figure2_classic/indexing_evidence.json").read_text())
native_by_id=dict(zip(index_evidence["original_ids"],index_evidence["selected_archived_seeds"]))
# Archived native landmark centers position the six off-axis labels exactly.
# Axial centers retain the original selected source-image points via registration.
native_xy=np.array([native_by_id[p.label][:2] if p.label in native_by_id else
                   np.array([p.x,p.y])*index_evidence["display_registration"]["native_per_image_pixel_xy"]+
                   index_evidence["display_registration"]["native_offset_xy"] for p in peaks])
source_xy=(native_xy-np.array([963,721]))/813*406
heads=helper.map_points(H,source_xy.tolist())
beam_info=json.loads((OUT / "beam_center.json").read_text())
beam_source_xy=(np.array(beam_info["native_column_row"])-[963,721])/813*406
beam_center=helper.map_points(H,[beam_source_xy.tolist()])[0]

# Crisp vector rays leave the measured image unobscured by beam glow.
selected_ray=5
for i,head in enumerate(heads):
    segment(tail,head,AMBER,1.0 if i == selected_ray else .55,8,
            alpha=1.0 if i == selected_ray else .70)
selected_delta=heads[selected_ray]-tail
ax.add_patch(FancyArrowPatch(tail+.62*selected_delta,tail+.78*selected_delta,
                            arrowstyle="-|>",mutation_scale=11,lw=1.0,
                            color=AMBER,zorder=10,shrinkA=0,shrinkB=0))
label(*(tail+.65*selected_delta+[24,-5]),r"$\mathbf{k}_f$",15,AMBER)

# A crisp blue incident arrow replaces the pixelated, heavily shadowed arrow.
incident_start=tail-1.15*(beam_center-tail)
ax.add_patch(FancyArrowPatch(incident_start,tail,arrowstyle="Simple,tail_width=3.2,head_width=11,head_length=15",
                            color=BLUE,lw=0,zorder=9,shrinkA=0,shrinkB=0))
label(*(incident_start+[-18,-20]),r"$\mathbf{k}_i$",17,BLUE)

# The undeflected beam is the straight continuation of the incident arrow.
# Reflection indices and their leaders are intentionally omitted.
segment(tail,beam_center,BLUE,1.25,11,linestyle=(0,(4,2)))
ax.plot(*beam_center,"o",ms=4,mfc="none",mec="white",mew=.8,zorder=12)
beam_anchor=beam_center+np.array([32,-8])
segment(beam_center+[5,-3],beam_anchor+[-5,3],"white",.6,12)
label(*beam_anchor,"Beam center",11.5,"white",ha="left",zorder=12)

label(474,17,"Area detector",12)
label(859,825,"Sample",12)
segment((787,816),(848,825),INK,.7)

fig.canvas.draw()
for t in ax.texts:
    bounds=t.get_window_extent()
    assert fig.bbox.contains(bounds.x0,bounds.y0) and fig.bbox.contains(bounds.x1,bounds.y1),t.get_text()
for ext in ("pdf","svg","png"):
    fig.savefig(OUT/f"Figure_2_journal.{ext}",dpi=300,facecolor="white")
plt.close(fig)
(OUT/"provenance.json").write_text(json.dumps({
    "source":str(SOURCE.relative_to(ROOT)),
    "source_sha256":hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    "original_generator":str(helper_path.relative_to(ROOT)),
    "original_generator_sha256":hashlib.sha256(helper_path.read_bytes()).hexdigest(),
    "detector_face":face.tolist(),"sample_hit":tail.tolist(),
    "diffraction_rays":[{"original_id":p.label,"source_xy":[p.x,p.y],"drawing_xy":h.tolist()} for p,h in zip(peaks,heads)],
    "beam_center":{**beam_info,"drawing_xy":beam_center.tolist(),"incident_start":incident_start.tolist()},
    "reflection_labels_displayed":False,
    "style":{"selected_scattered_ray_id":peaks[selected_ray].label,"incident_and_direct_beam_color":BLUE,"beam_glow":False},
    "indexing_evidence":"../figure2_classic/indexing_evidence.json",
    "native_detector_source":source_info,
    "native_label_coordinates_xy":native_xy.tolist(),
    "canvas_area_reduction_same_detector_scale":1-(870*910)/(1080*970),
    "scope":"Single-scene diffraction schematic with nine unindexed diffraction rays, one selected k_f arrow and one annotated undeflected beam-center ray. Apparatus and ray geometry are schematic.",
    "raster_processing":"Native measured counts exported at 814x814 with global turbo linear 0..2000 counts display, then bilinear perspective resampling. No smoothing, background subtraction or fitting."
},indent=2)+"\n")
print(OUT/"Figure_2_journal.png")
