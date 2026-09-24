"""Integrated journal mosaic schematic; deterministic vector geometry, no fit.

The spherical broad-component formula follows the archived F03 teaching helper.
The Gaussian is untapered here. Both are per-solid-angle teaching distributions,
not the manuscript's fitted angular-line density. No intensity data are edited.
"""
from pathlib import Path
import hashlib
import json
import shutil

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.colors import to_rgb
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Circle
from scipy.integrate import quad

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/figure5_journal'
OUT.mkdir(parents=True, exist_ok=True)
INK, PURPLE, AMBER = '#151515', '#79529D', '#C17A24'
TEAL, GREY = '#087D88', '#A7B0B6'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                     'mathtext.fontset': 'dejavusans', 'pdf.fonttype': 42,
                     'svg.fonttype': 'none', 'text.color': INK})
DEG = np.pi / 180
K, Q = 2., 1.6
INC = 3 * DEG
KI = K * np.array([-np.cos(INC), 0, -np.sin(INC)])
C = -KI
SIGMA, GAMMA, FRACTION = 5 * DEG, 12 * DEG, .28
GNORM = 2 * np.pi * quad(lambda a: np.exp(-.5*(a/SIGMA)**2)*np.sin(a), 0, np.pi,
                         epsabs=1e-13, epsrel=1e-13)[0]
D0 = 2 * np.sinh(GAMMA/2)**2
LNORM = 2*np.pi*np.log1p(2/D0)
YAW, ELEV = -148*DEG, 18*DEG
RIGHT = np.array([np.cos(YAW), np.sin(YAW), 0])
UP = np.array([-np.sin(YAW)*np.sin(ELEV), np.cos(YAW)*np.sin(ELEV), np.cos(ELEV)])
EYE = np.cross(RIGHT, UP)
CAMERA = np.array([RIGHT, UP])
PHI = (np.arange(768)+.5)*2*np.pi/768
audit = {'scope': 'Generic schematic; no material-specific reflection, fitted width, or detector intensity',
         'distribution': 'Normalized per solid angle; uniform independent in-plane spin; distinct from fitted angular-line law',
         'parameters': {'K': K, 'Q': Q, 'incidence_deg': 3, 'gaussian_sigma_deg': 5,
                        'lorentzian_gamma_deg': 12, 'broad_probability': FRACTION,
                        'off_axis_polar_angle_deg': 50, 'view_yaw_deg': -148, 'view_elevation_deg': 18},
         'checks': {}, 'panels': {}}
arrays = {}

def project(q):
    return np.asarray(q) @ CAMERA.T

def spherical(theta, phi, radius=Q):
    theta, phi = np.broadcast_arrays(theta, phi)
    return radius*np.stack([np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)], axis=-1)

def components(theta, theta0):
    theta = np.atleast_1d(theta)
    cosine = np.cos(theta[:, None])*np.cos(theta0) + np.sin(theta[:, None])*np.sin(theta0)*np.cos(PHI)
    sep = np.arccos(np.clip(cosine, -1, 1))
    g = (1-FRACTION)*np.exp(-.5*(sep/SIGMA)**2).mean(axis=1)/GNORM
    minus = D0 + 2*np.sin((theta-theta0)/2)**2
    plus = D0 + 2*np.sin((theta+theta0)/2)**2
    l = FRACTION/(LNORM*np.sqrt(minus*plus))
    return g, l

def line3(ax, xyz, **kw):
    p = project(xyz)
    return ax.plot(p[:, 0], p[:, 1], **kw)

def ewald_sphere(ax):
    """Complete spheres share the physical reciprocal-space scale."""
    center = project(C)
    ax.add_patch(Circle((0, 0), Q, facecolor='#E7E8EA', edgecolor='#B7BBC0',
                        lw=.7, zorder=0))
    ax.add_patch(Circle(center, K, facecolor='#A9CEE2', edgecolor='#75A5BC',
                        lw=.7, alpha=.48, zorder=1))

def intersection(n=1601):
    # Shell |q|=Q and Ewald |q+ki|=K intersect in an exact circle.
    normal = C/K
    center = normal*Q**2/(2*K)
    a = np.cross(normal, [0, 1, 0]); a /= np.linalg.norm(a)
    b = np.cross(normal, a)
    rho = np.sqrt(Q**2-(Q**2/(2*K))**2)
    t = np.linspace(-np.pi, np.pi, n)
    q = center + rho*(np.cos(t)[:, None]*a + np.sin(t)[:, None]*b)
    tangent = -np.sin(t)[:, None]*a + np.cos(t)[:, None]*b
    en = (q-C)/K
    across = np.cross(tangent, en)
    delta = np.array([-3.3, 3.3])*DEG
    edges = C+K*(en[:, None, :]*np.cos(delta)[None, :, None] + across[:, None, :]*np.sin(delta)[None, :, None])
    return q, edges

TRACE, EDGES = intersection()
THETA = np.arccos(np.clip(TRACE[:, 2]/Q, -1, 1))
audit['checks']['ewald_residual'] = float(np.max(np.abs(np.linalg.norm(TRACE-C, axis=1)-K)))
audit['checks']['shell_residual'] = float(np.max(np.abs(np.linalg.norm(TRACE, axis=1)-Q)))
audit['checks']['patch_ewald_residual'] = float(np.max(np.abs(np.linalg.norm(EDGES-C, axis=2)-K)))
assert max(audit['checks'].values()) < 1e-12
arrays['intersection_q'] = TRACE
arrays['ewald_patch_edges'] = EDGES

def panel(ax, theta0, letter, title):
    is_axial = theta0 == 0
    extent = (0, 34*DEG) if is_axial else (22*DEG, 78*DEG)
    # Full, undistorted Ewald spheres share the same origin, camera and scale.
    ax.set(xlim=(-3.90, 1.90), ylim=(-1.82, 2.68), aspect='equal')
    ax.axis('off')

    ewald_sphere(ax)
    keep = (THETA >= extent[0]) & (THETA <= extent[1])
    # Every displayed selected ray is above the reference sample plane.
    assert np.min(TRACE[keep, 2]+KI[2]) > 0

    # Smooth overlapping component densities on the same constant-|q| shell.
    # Fixed qualitative transfer within each panel, not a count scale.
    ts = np.linspace(*extent, 72)
    ps = np.linspace(-np.pi, np.pi, 145)
    tc = (ts[:-1]+ts[1:])/2
    g, l = components(tc, theta0)
    all_t = np.linspace(0, np.pi, 3001)
    ga, la = components(all_t, theta0)
    reference = float(np.max(ga+la))
    # Normalize each component for legibility, not relative probability or counts.
    broad_opacity = .58*np.sqrt(l/np.max(la))
    narrow_opacity = .80*np.sqrt(g/np.max(ga))
    cells, colors, depths = [], [], []
    for i in range(len(ts)-1):
        for j in range(len(ps)-1):
            xyz = spherical(ts[[i, i+1, i+1, i]], ps[[j, j, j+1, j+1]])
            center = xyz.mean(axis=0)
            # Precompose with the underlying gray/blue sphere context so
            # adjacent translucent vector cells do not leave overlap seams.
            # Render only the visible hemisphere: rear features remain dashed references.
            front = center@EYE >= 0
            if not front:
                continue
            base = np.array(to_rgb('#E7E8EA'))
            if np.linalg.norm(project(center)-project(C)) <= K:
                base = .48*np.array(to_rgb('#A9CEE2')) + .52*base
            col = broad_opacity[i]*np.array(to_rgb(AMBER)) + (1-broad_opacity[i])*base
            col = narrow_opacity[i]*np.array(to_rgb(PURPLE)) + (1-narrow_opacity[i])*col
            cells.append(project(xyz)); colors.append(col); depths.append(center@EYE)
    order = np.argsort(depths)
    ax.add_collection(PolyCollection([cells[i] for i in order], facecolors=np.array(colors)[order],
                                    edgecolors='face', linewidths=.05, antialiased=False, zorder=3))
    # Keep only the zero-tilt reference ring or point.
    if not is_axial:
        xyz = spherical(theta0, np.linspace(-np.pi, np.pi, 361))
        front = xyz@EYE >= 0
        for mask, style in [(front, '-'), (~front, (0, (3, 3)))]:
            p = xyz.copy(); p[~mask] = np.nan
            line3(ax, p, color=PURPLE, lw=1.0, ls=style, zorder=5)

    # Show the entire exact circle for context, with rear portions dashed.
    front = TRACE@EYE >= 0
    for mask, style in [(front, '-'), (~front, (0, (3, 3)))]:
        full = TRACE.copy(); full[~mask] = np.nan
        line3(ax, full, color=TEAL, lw=.85, alpha=.6, ls=style, zorder=6)
    # Emphasis identifies the displayed mosaic region, not a support cutoff.
    for mask, style in [(front, '-'), (~front, (0, (3, 3)))]:
        p = TRACE.copy(); p[~(keep & mask)] = np.nan
        line3(ax, p, color='white', lw=3.1, ls=style, zorder=7)
        line3(ax, p, color=TEAL, lw=2.0, ls=style, zorder=8)
    if is_axial:
        ax.plot(*project([0, 0, Q]), 'o', ms=3.8, color=PURPLE, mec='white', mew=.6, zorder=9)
    arrays[f'{letter}_theta'] = all_t
    arrays[f'{letter}_weighted_gaussian'] = ga
    arrays[f'{letter}_weighted_broad'] = la
    audit['panels'][letter] = {'polar_angle_deg': float(theta0/DEG),
                               'display_polar_range_deg': list(np.array(extent)/DEG),
                               'reference_density_sr-1': reference,
                               'layout_vertical_translation': 0,
                               'minimum_selected_exit_kz': float(np.min(TRACE[keep, 2]+KI[2]))}

def inset(ax, theta0):
    """View along Q_z: azimuthal averaging precedes mosaic tilt."""
    ax.set(xlim=(0, 10), ylim=(-.5, 2.3), aspect='equal')
    ax.axis('off')
    x1, x2, cy, radius = 1.65, 8.35, .95, .69
    ax.annotate('', (6.75, cy), (3.25, cy),
                arrowprops={'arrowstyle': '->', 'lw': .85, 'color': '#565D65'})
    ax.text(5., 1.25, 'Random in-plane\nazimuth', ha='center', va='bottom', fontsize=8., linespacing=1.1)
    if theta0:
        for center in [x1, x2]:
            ax.plot(center, cy, '+', ms=4, mew=.7, color='#A4A9AE')
        ax.add_patch(Circle((x1, cy), radius, fill=False, ec='#C5C9CD', lw=.6, ls=(0, (2, 3))))
        phi = np.arange(6)*np.pi/3 + np.pi/6
        ax.plot(x1+radius*np.cos(phi), cy+radius*np.sin(phi), 'o', ms=3.3, color=INK)
        ax.add_patch(Circle((x2, cy), radius, fill=False, ec=PURPLE, lw=1.8))
        ax.text(x1, -.13, 'Same $r$, same $Q_z$', ha='center', va='top', fontsize=7.8)
        ax.text(x2, -.13, 'Azimuthal ring', ha='center', va='top', fontsize=7.8)
        # Verify illustrative source points share Q_R and Q_z on the same shell.
        points = spherical(theta0, phi)
        assert np.ptp(np.linalg.norm(points[:, :2], axis=1)) < 1e-12
        assert np.ptp(points[:, 2]) < 1e-12
        arrays['azimuth_source_points'] = points
    else:
        ax.plot(x1, cy, 'o', ms=4, color=INK)
        ax.plot(x2, cy, 'o', ms=4, color=PURPLE)
        ax.text(x1, -.13, 'Axial point ($r=0$)', ha='center', va='top', fontsize=7.8)
        ax.text(x2, -.13, 'Unchanged', ha='center', va='top', fontsize=7.8)
    audit['checks']['azimuth_common_radius_and_height'] = True

fig = plt.figure(figsize=(7.2, 4.05), facecolor='white')
for left, theta0, letter, title in [(0.010, 50*DEG, 'a', 'Off-axis band'),
                                   (.515, 0., 'b', 'Axial cap')]:
    fig.text(left+.008, .968, f'({letter})', weight='bold', fontsize=10.5, va='top')
    fig.text(left+.066, .968, title, fontsize=10.5, va='top')
    cross = fig.add_axes([left+.015, .705, .445, .210])
    inset(cross, theta0)
    ax = fig.add_axes([left, .130, .475, .565])
    panel(ax, theta0, letter, title)
    ax.text(-2.6, 2.54, 'Ewald sphere', color='#487D97', fontsize=8.2, ha='center')
    ax.text(.28, -1.79, r'Constant-$|Q|$ sphere', color='#666B72', fontsize=8.2, ha='center')
fig.legend(handles=[Patch(facecolor=PURPLE, edgecolor='none', label='Narrow component'),
                    Patch(facecolor=AMBER, edgecolor='none', label='Broad component'),
                    Line2D([0], [0], color=TEAL, lw=2., label='Ewald intersection')],
           loc='lower center', bbox_to_anchor=(.50, .018), ncol=3,
           frameon=False, handlelength=1.25, columnspacing=1.3, fontsize=8.0)

# Independent quadrature of spherical component and band normalization.
norms = {}
for label, theta0 in [('cap', 0.), ('band', 50*DEG)]:
    for j, name in enumerate(['gaussian', 'broad']):
        mass = 2*np.pi*quad(lambda t: components([t], theta0)[j][0]*np.sin(t), 0, np.pi,
                            epsabs=2e-11, epsrel=2e-11)[0]
        expected = (1-FRACTION, FRACTION)[j]
        assert abs(mass-expected) < 1e-9, (label, name, mass)
        norms[f'{label}_{name}'] = mass
audit['checks']['component_integrals'] = norms
# Check the analytic broad-band convolution against an independent azimuth sum.
psi_check = (np.arange(8192)+.5)*2*np.pi/8192
ring_errors = []
for theta in np.array([0, 17, 38, 50, 67, 110, 180])*DEG:
    theta0 = 50*DEG
    separation = 2*np.sin((theta-theta0)/2)**2 + 2*np.sin(theta)*np.sin(theta0)*np.sin(psi_check/2)**2
    direct = FRACTION*np.mean(1/(LNORM*(D0+separation)))
    analytic = components([theta], theta0)[1][0]
    ring_errors.append(abs(direct-analytic)/analytic)
assert max(ring_errors) < 1e-12
audit['checks']['broad_ring_independent_relative_error'] = float(max(ring_errors))
audit['checks']['camera_orthonormal_residual'] = float(np.max(np.abs(CAMERA@CAMERA.T-np.eye(2))))
fig.canvas.draw()
renderer = fig.canvas.get_renderer()
outside = []
for artist in fig.findobj(matplotlib.text.Text):
    if artist.get_text() and artist.get_visible():
        bb = artist.get_window_extent(renderer)
        if bb.x0 < 0 or bb.y0 < 0 or bb.x1 > fig.bbox.width or bb.y1 > fig.bbox.height:
            outside.append(artist.get_text())
assert not outside, outside
audit['checks']['all_labels_inside_canvas'] = True
audit['render'] = {'width_inches': 7.2, 'height_inches': 4.05,
                   'ewald_sphere': 'Two complete spheres at true schematic radii; common camera and equal reciprocal scale; full intersection circle plus highlighted mosaic range',
                   'density_transfer': 'Broad alpha=.58*sqrt(broad/component_max); narrow alpha=.80*sqrt(narrow/component_max), separately normalized in each panel',
                   'colors': {'narrow': PURPLE, 'broad': AMBER, 'intersection': TEAL},
                   'surface_color': 'Broad amber then narrow purple, separately normalized for visibility and precomposed on the gray/blue front shell; both overlap',
                   'upper_insets': 'View along Q_z: representative common-r, common-Q_z points average to one ring; an axial point is unchanged. Dot count is illustrative, not multiplicity.',
                   'limits': 'Local mosaic shell crops are drawing limits, not distribution cutoffs. The complete Ewald sphere is visible. Brightness does not compare reflection intensities.'}
previous = OUT/'before_simplification/geometry_and_density.npz'
if previous.exists():
    with np.load(previous) as old:
        for name, values in arrays.items():
            if name.startswith(('a_', 'b_')):
                assert np.array_equal(values, old[name]), name
    audit['checks']['retained_density_arrays_identical'] = True
previous_geometry = OUT/'before_azimuth/geometry_and_density.npz'
if previous_geometry.exists():
    with np.load(previous_geometry) as old:
        for name in old.files:
            assert np.array_equal(arrays[name], old[name]), name
    audit['checks']['pre_azimuth_geometry_and_densities_identical'] = True
helper = ROOT/'output/manuscript_figure_drafts_v1/source/geometry_reference/lorentzian_mosaic_geometry.mjs'
audit['formula_reference'] = {'path': str(helper.relative_to(ROOT)), 'sha256': hashlib.sha256(helper.read_bytes()).hexdigest()}
for ext in ['pdf', 'svg', 'png']:
    fig.savefig(OUT/f'Figure_5_journal.{ext}', dpi=360)
np.savez_compressed(OUT/'geometry_and_density.npz', **arrays)
audit['renderer_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
(OUT/'verification.json').write_text(json.dumps(audit, indent=2)+'\n', encoding='utf-8')
shutil.copyfile(OUT/'Figure_5_journal.pdf', ROOT/'figures/mosaic/mosaic_integrated_journal.pdf')
(ROOT/'output/pdf').mkdir(exist_ok=True)
shutil.copyfile(OUT/'Figure_5_journal.pdf', ROOT/'output/pdf/Figure_5_journal.pdf')
print(json.dumps(audit['checks'], indent=2))
