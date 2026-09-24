"""Journal figure: Bragg rings, continuous rods, rotated cylinders, Ewald selection.

Reuses the immutable cylinder_bridge_v3 teaching geometry. No fitted quantities.
"""
from pathlib import Path
import hashlib
import importlib.util
import json
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import to_rgba
from matplotlib.patches import Circle
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/cylinder_bridge_journal'
OUT.mkdir(parents=True, exist_ok=True)
SOURCE = ROOT / 'output/cylinder_bridge_v3/source/cylinder_bridge.py'
spec = importlib.util.spec_from_file_location('archived_bridge', SOURCE)
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)
INK, TEAL, PURPLE = '#151515', '#087D88', '#79529D'
GRAY, BLUE, AMBER = '#A7B0B6', '#75A5BC', '#C17A24'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
    'mathtext.fontset': 'dejavusans', 'pdf.fonttype': 42, 'svg.fonttype': 'none',
    'text.color': INK, 'axes.labelcolor': INK, 'axes.linewidth': .55,
    'savefig.facecolor': 'white'})
EYE = np.cross(g.RIGHT, g.UP)
T = np.linspace(0, 2*np.pi, 361)
arrays = {}


def line(ax, q, color=INK, lw=.65, alpha=1, ls='-', zorder=3):
    p = g.project(q)
    return ax.plot(p[:, 0], p[:, 1], color=color, lw=lw, alpha=alpha,
                   ls=ls, zorder=zorder)


def depth_line(ax, q, center, color, lw=.65, alpha=1, zorder=3):
    """Front/back is always relative to the surface's own center."""
    front = (q-np.asarray(center)) @ EYE >= 0
    for mask, style, strength in [(front, '-', 1), (~front, (0, (2, 2)), .65)]:
        qq = q.copy()
        qq[~mask] = np.nan
        line(ax, qq, color, lw, alpha*strength, style, zorder)


def arrow(ax, a, b, color=INK, lw=.7, head=5, zorder=8):
    ax.annotate('', xy=b, xytext=a, arrowprops=dict(arrowstyle='-|>',
        color=color, lw=lw, mutation_scale=head, shrinkA=0, shrinkB=0), zorder=zorder)


def qaxis(ax, top=4.0, label=True):
    origin = g.project([0, 0, 0]); end = g.project([0, 0, top])
    arrow(ax, origin, end, GRAY, .65)
    ax.scatter(*origin, s=7, color=INK, zorder=10)
    ax.text(*(origin+np.array([.12, -.19])), r'$O$', fontsize=8)
    if label:
        ax.text(*(end+np.array([.07, .09])), r'$Q_z$', fontsize=9)


def sphere(ax, center, radius, face, edge, alpha=.25):
    cp = g.project(center)
    ax.add_patch(Circle(cp, radius, facecolor=face, edgecolor='none', alpha=alpha,
                       zorder=-5))
    ax.add_patch(Circle(cp, radius, fill=False, edgecolor=edge, lw=.65, zorder=0))
    # A single equatorial section supplies depth without a mesh.
    eq = np.asarray(center)+np.c_[radius*np.cos(T), radius*np.sin(T), np.zeros_like(T)]
    depth_line(ax, eq, center, edge, .4, .7, 0)


def ring(L, U=np.eye(3)):
    return np.c_[g.R*np.cos(T), g.R*np.sin(T), np.full_like(T, L)] @ U.T


def weighted(ax, q, weights, color=TEAL, lw=1, valid=None, factor=1, zorder=5):
    p = g.project(q)
    seg = np.stack([p[:-1], p[1:]], axis=1)
    v = .5*(weights[:-1]+weights[1:])*factor
    mask = np.ones(len(v), bool) if valid is None else valid[:-1] & valid[1:]
    colors = np.tile(to_rgba(color), (len(v), 1))
    colors[:, 3] = np.clip(v, 0, 1)
    ax.add_collection(LineCollection(seg[mask], colors=colors[mask], linewidths=lw,
                                    capstyle='butt', zorder=zorder))


def cylinder(ax, U=np.eye(3), strength=1, color=TEAL, dense=True):
    levels = np.linspace(g.LMIN, g.LMAX, 301 if dense else 67)
    for L in levels:
        line(ax, ring(L, U), color, .65, strength*.57*float(g.contrast(g.rod_intensity(L))), zorder=2)
    # Silhouette generatrices are perpendicular to the view's radial component.
    eye_local = U.T @ EYE
    beta = np.arctan2(eye_local[1], eye_local[0])+np.pi/2
    for b in [beta, beta+np.pi]:
        q = np.array([[g.R*np.cos(b), g.R*np.sin(b), g.LMIN],
                      [g.R*np.cos(b), g.R*np.sin(b), g.LMAX]]) @ U.T
        line(ax, q, GRAY, .55, .8*strength+.22*(1-strength), zorder=3)
    for L in [g.LMIN, g.LMAX]:
        depth_line(ax, ring(L, U), U @ np.array([0, 0, L]), GRAY, .45, .8*strength+.22*(1-strength), 3)


def ewald(ax):
    sphere(ax, g.CENTER, g.K, '#A9CEE2', BLUE, .23)


def labels(ax, tag):
    ax.set_aspect('equal'); ax.axis('off')
    ax.text(.015, .965, '('+tag+')', transform=ax.transAxes,
            ha='left', va='top', weight='bold', fontsize=10, zorder=30)


fig = plt.figure(figsize=(5.5, 4.75))
axs = [fig.add_axes(rect) for rect in [(.025, .525, .455, .46),
       (.505, .525, .47, .46), (.015, .015, .475, .49), (.51, .015, .475, .49)]]

# (a) A highlighted constant-|Q| sphere intersects the first ring exactly.
ax = axs[0]
ax.set_xlim(-1.7, 2.0); ax.set_ylim(-1.85, 4.25)
sphere(ax, np.zeros(3), np.sqrt(2), '#E7E8EA', GRAY, .6)
for L in [1., 2., 3.]:
    rr = ring(L); arrays[f'bragg_ring_L{int(L)}'] = rr
    depth_line(ax, rr, [0, 0, L], PURPLE, 1.1, 1, 5)
    ax.text(1.12, g.UP[2]*L, rf'$L={int(L)}$', fontsize=8, va='center')
for b in [np.pi/4, 5*np.pi/4]:
    line(ax, np.array([[np.cos(b), np.sin(b), g.LMIN],
                      [np.cos(b), np.sin(b), g.LMAX]]), GRAY, .55, .7, (0, (2, 3)), 1)
q = np.array([1., 0., 1.]); arrays['selected_bragg_vector'] = q
arrow(ax, [0, 0], g.project(q), PURPLE, .8)
ax.scatter(*g.project(q), s=13, color=PURPLE, edgecolor='white', lw=.35, zorder=10)
ax.text(0, -1.58, r'$|\mathbf{Q}|=|\mathbf{G}_{hk1}|$', fontsize=8, ha='center', va='center')
qaxis(ax)
labels(ax, 'a')

# (b) The same finite N=8 intensity supplies both profile and cylinder.
ax = axs[1]
ax.set_xlim(-2.7, 1.85); ax.set_ylim(-.53, 4.25)
cylinder(ax)
L = np.linspace(g.LMIN, g.LMAX, 2401)
S = g.rod_intensity(L)
arrays.update(profile_L=L, profile_S=S)
x0, w = -2.40, .98
y = L*g.UP[2]
ax.plot(x0+w*S, y, color=INK, lw=.7)
ax.plot([x0, x0], [y[0], y[-1]], color=INK, lw=.5)
ax.plot([x0, x0+w], [y[0], y[0]], color=INK, lw=.5)
for ll in [1, 2, 3]:
    yy = ll*g.UP[2]
    ax.plot([x0-.045, x0], [yy, yy], color=INK, lw=.5)
    ax.text(x0-.10, yy, str(ll), fontsize=7, va='center', ha='right')
    ax.plot([x0+w+.08, -1.06], [yy, yy], color=GRAY, lw=.45, ls=(0, (2, 3)))
ax.text(x0-.1, y[-1]+.17, r'$L$', fontsize=9, ha='center')
ax.text(x0+w/2, -.31, r'$S_8(L)$', fontsize=9, ha='center')
for v in [0, 1]:
    ax.text(x0+w*v, y[0]-.11, str(v), fontsize=7, ha='center', va='top')
beta = np.pi/4
qrod = np.c_[np.full(len(L), np.cos(beta)), np.full(len(L), np.sin(beta)), L]
arrays['representative_rod'] = qrod
weighted(ax, qrod, g.contrast(S), lw=1.65, factor=.85)
qaxis(ax)
ax.text(1.14, 1.75, r'$r=1$', fontsize=8)
labels(ax, 'b')

# (c) Three representative rigid cylinders intersect a fixed Ewald sphere.
ax = axs[2]
for aa in [axs[2], axs[3]]:
    aa.set_xlim(-5.82, 1.55); aa.set_ylim(-1.68, 5.46)
ewald(ax)
representatives = [(0, 0), (9, 35), (9, 215)]
for j, (alpha, psi) in enumerate(representatives):
    U = g.rotation(np.deg2rad(alpha), np.deg2rad(psi))
    arrays[f'representative_rotation_{j}'] = U
    cylinder(ax, U, strength=.28 if j == 0 else .18, color=GRAY, dense=False)
    # Reference normals make the rigid tilt explicit.
    line(ax, np.array([[0, 0, 0], U @ np.array([0, 0, 3.8])]), GRAY, .6, .75)
    for k, (qq, valid) in enumerate(g.exact_locus(U)):
        arrays[f'representative_locus_{j}_{k}'] = qq
        arrays[f'representative_valid_{j}_{k}'] = valid
        weighted(ax, qq, .18+.82*g.contrast(g.rod_intensity(g.LGRID)),
                 lw=.95, valid=valid, factor=.9)
qaxis(ax)
labels(ax, 'c')

# (d) Exact selected loci for the archived, normalized orientation quadrature.
ax = axs[3]
ewald(ax)
with np.load(ROOT / 'output/cylinder_bridge_v3/data/model_arrays.npz') as frozen:
    states = np.column_stack([frozen['alpha_rad'], frozen['psi_rad'], frozen['orientation_mass']])
allq, allvalid = [], []
for alpha, psi, mass in states:
    loci = g.exact_locus(g.rotation(alpha, psi))
    qstate, vstate = [], []
    for qq, valid in loci:
        weighted(ax, qq, g.contrast(g.rod_intensity(g.LGRID))*mass,
                 valid=valid, factor=12, lw=.9)
        qstate.append(qq); vstate.append(valid)
    allq.append(qstate); allvalid.append(vstate)
arrays.update(orientation_states=states, selected_q=np.array(allq),
              selected_valid=np.array(allvalid), selected_L=g.LGRID,
              ki=g.KI, ewald_center=g.CENTER, camera_eye=EYE)
for qq, valid in g.exact_locus(np.eye(3)):
    qq = qq.copy(); qq[~valid] = np.nan
    line(ax, qq, GRAY, .55, .9, (0, (2, 2)), 6)
cp = g.project(g.CENTER); origin = g.project([0, 0, 0])
ax.scatter(*cp, s=8, color=BLUE, zorder=9)
arrow(ax, cp, origin, BLUE, .8)
ax.text(*((cp+origin)/2+np.array([-.45, -.2])), r'$\mathbf{k}_i$', fontsize=9)
qq, mask = g.exact_locus(np.eye(3), np.array([2.]))[0]
assert mask[0]
point = g.project(qq[0]); arrays['exit_marker_q'] = qq[0]
arrow(ax, cp, point, AMBER, 1.0, 5.5)
ax.scatter(*point, s=16, color=AMBER, edgecolor='white', lw=.45, zorder=10)
ax.text(*((cp+point)/2+np.array([0, .18])), r'$\mathbf{k}_f$', fontsize=9)
qaxis(ax)
labels(ax, 'd')

# Check literal text bounds at the final print size before exporting.
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
outside = []
for ax in axs:
    for txt in ax.texts:
        bb = txt.get_window_extent(renderer)
        if bb.width and (bb.x0 < 0 or bb.y0 < 0 or bb.x1 > fig.bbox.width or bb.y1 > fig.bbox.height):
            outside.append(txt.get_text())
assert not outside, outside
for ext in ['pdf', 'svg', 'png']:
    fig.savefig(OUT / f'Cylinder_Bridge_Journal.{ext}', dpi=360)
plt.close(fig)
np.savez_compressed(OUT / 'geometry_arrays.npz', **arrays)
(ROOT / 'output/pdf').mkdir(parents=True, exist_ok=True)
shutil.copyfile(OUT / 'Cylinder_Bridge_Journal.pdf', ROOT / 'output/pdf/Cylinder_Bridge_Journal.pdf')

CAPTION = r'''\caption{Continuous rod scattering and Ewald selection for a representative off-axis family. (a) Random in-plane azimuth distributes ideal Bragg points into the purple rings at intrinsic orders $L=1,2,3$. Each ring lies on a constant-$|\mathbf Q|$ sphere centered at the reciprocal origin $O$; the gray sphere is shown for $L=1$. Dashed vertical guides mark the common cylinder radius. (b) The black profile is the peak-normalized interference factor of eight identical unit layers, $S_8(L)=|\sum_{n=0}^{7}\exp(2\pi i nL)|^2/64$. Its finite widths and fringes supply the teal intensity modulation on the cylinder. The stronger vertical trace marks one contributing rod, and $r=1$ denotes a representative basal reflection family. (c) Three representative cylinder orientations rotate rigidly about $O$. Gray lines follow their normal axes. Teal curves mark their exact intersections with the fixed pale-blue Ewald sphere, with line contrast emphasizing the rod maxima. (d) The cylinder guides are removed and the selected loci are weighted by an illustrative distribution of normal orientations. Gray dashed curves mark the aligned-cylinder intersections. The blue $\mathbf k_i$ and orange $\mathbf k_f$ share the Ewald center as their tail; the orange point satisfies $\mathbf k_f=\mathbf k_i+\mathbf Q$. The sphere is centered at $-\mathbf k_i$ and has radius $|\mathbf k_i|=2\pi/\lambda$. The camera direction is common to all panels, and (c,d) share the same expanded field of view. In the schematic reciprocal units, the cylinder radius and normal reciprocal repeat are unity, $|\mathbf k_i|=3.4$, and incidence is $20^\circ$. Intrinsic $L$ rotates with the crystallite and differs from laboratory $Q_z$ after tilt. Shading illustrates structural and orientation weighting with enhanced contrast, not calibrated Ewald-surface density or detector counts. No material-specific reflection intensities are implied. Stacking disorder changes the rod intensity within the same geometric construction.}'''
(OUT / 'caption.tex').write_text(CAPTION+'\n', encoding='utf-8')
record = {'scope': 'standalone journal schematic; no manuscript insertion or fitted result',
    'source': str(SOURCE.relative_to(ROOT)),
    'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
    'renderer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'print_size_inches': [5.5, 4.75], 'font': 'DejaVu Sans, 7-10 pt',
    'schematic_parameters': {'N': 8, 'R': g.R, 'K': g.K, 'incidence_deg': g.INCIDENCE_DEG,
        'L_range': [g.LMIN, g.LMAX], 'representative_tilts_deg': representatives},
    'orientation_law': 'archived v3: 82% Gaussian 3 deg + 18% Gaussian 9 deg, normalized with sin(alpha) measure on 18 deg cone, 12x32 quadrature',
    'display': {'contrast': 'asinh(S/0.02)/asinh(50)', 'panel_d_opacity': '12 * orientation_mass * contrast(S)',
        'panel_c_opacity': '.9 * (.18 + .82*contrast(S)); three geometric example loci, not population weights',
        'missing_physics': 'coarea/detector Jacobians, atomic form factors, optics, source spread, substrate/detector acceptance'},
    'all_text_inside_canvas': not outside,
    'output_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('Cylinder_Bridge_Journal.*')}}
(OUT / 'provenance.json').write_text(json.dumps(record, indent=2)+'\n', encoding='utf-8')
print(OUT / 'Cylinder_Bridge_Journal.png')
