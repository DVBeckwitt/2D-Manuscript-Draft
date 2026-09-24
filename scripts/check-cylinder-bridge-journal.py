"""Independent numerical checks of the plotted arrays, without renderer imports."""
from pathlib import Path
import json
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/cylinder_bridge_journal'
a = np.load(OUT / 'geometry_arrays.npz')
checks = {}
tol = 1e-12

for ell in [1, 2, 3]:
    q = a[f'bragg_ring_L{ell}']
    checks[f'ring_{ell}_sphere_error'] = float(np.max(np.abs(np.linalg.norm(q, axis=1)-np.sqrt(1+ell**2))))
    checks[f'ring_{ell}_cylinder_error'] = float(np.max(np.abs(np.linalg.norm(q[:, :2], axis=1)-1)))
    assert checks[f'ring_{ell}_sphere_error'] < tol
    assert checks[f'ring_{ell}_cylinder_error'] < tol

# Independent closed-form geometric-series identity against the plotted direct sum.
L, S = a['profile_L'], a['profile_S']
d = L-np.rint(L)
expected = (np.sinc(8*d)/np.sinc(d))**2
checks['finite_stack_profile_error'] = float(np.max(np.abs(expected-S)))
assert checks['finite_stack_profile_error'] < tol
x = np.arange(8192)/8192
period = (np.sinc(8*(x-np.rint(x)))/np.sinc(x-np.rint(x)))**2
checks['period_mean_error'] = float(abs(period.mean()-1/8))
assert checks['period_mean_error'] < tol

ki = a['ki']; K = np.linalg.norm(ki)
q = a['selected_q']; valid = a['selected_valid']
checks['selected_points'] = int(valid.sum())
checks['max_ewald_error'] = float(np.max(np.abs(np.linalg.norm(q[valid]+ki, axis=1)-K)))
checks['ewald_origin_error'] = float(abs(np.linalg.norm(a['ewald_center'])-K))
checks['orientation_mass_error'] = float(abs(a['orientation_states'][:, 2].sum()-1))
assert checks['max_ewald_error'] < tol and checks['ewald_origin_error'] < tol
assert checks['orientation_mass_error'] < tol and np.all(a['orientation_states'][:, 2] > 0)

# Invert each rotation using independently constructed Rz Ry Rz^-1 matrices.
radial_error, intrinsic_error = 0., 0.
for i, (alpha, psi, mass) in enumerate(a['orientation_states']):
    ca, sa, cb, sb = np.cos(alpha), np.sin(alpha), np.cos(psi), np.sin(psi)
    rz = np.array([[cb, -sb, 0], [sb, cb, 0], [0, 0, 1]])
    ry = np.array([[ca, 0, sa], [0, 1, 0], [-sa, 0, ca]])
    u = rz @ ry @ rz.T
    for branch in [0, 1]:
        m = valid[i, branch]
        intrinsic = q[i, branch, m] @ u
        radial_error = max(radial_error, float(np.max(np.abs(np.linalg.norm(intrinsic[:, :2], axis=1)-1))))
        intrinsic_error = max(intrinsic_error, float(np.max(np.abs(intrinsic[:, 2]-a['selected_L'][m]))))
checks['max_intrinsic_L_error'] = intrinsic_error
checks['max_cylinder_radius_error'] = radial_error
assert intrinsic_error < tol and radial_error < tol

rep_error = 0.
for j in range(3):
    u = a[f'representative_rotation_{j}']
    assert np.max(np.abs(u.T@u-np.eye(3))) < tol and abs(np.linalg.det(u)-1) < tol
    for k in range(2):
        qq = a[f'representative_locus_{j}_{k}']
        mask = a[f'representative_valid_{j}_{k}']
        rep_error = max(rep_error, float(np.max(np.abs(np.linalg.norm(qq[mask]+ki, axis=1)-K))))
checks['representative_ewald_error'] = rep_error
assert rep_error < tol

# Preserve the archived science inputs, including every selected coordinate.
old = np.load(ROOT/'output/cylinder_bridge_v3/data/model_arrays.npz')
checks['archived_valid_mask_identical'] = bool(np.array_equal(valid, old['valid']))
checks['archived_valid_coordinates_identical'] = bool(np.array_equal(q[valid], old['q'][valid]))
checks['archived_orientation_masses_identical'] = bool(np.array_equal(a['orientation_states'][:, 2], old['orientation_mass']))
assert checks['archived_valid_mask_identical'] and checks['archived_valid_coordinates_identical']
assert checks['archived_orientation_masses_identical']
checks['exit_marker_ewald_error'] = float(abs(np.linalg.norm(a['exit_marker_q']+ki)-K))
assert checks['exit_marker_ewald_error'] < tol
previous = OUT / 'before_compaction'
if previous.exists():
    old_layout = np.load(previous / 'geometry_arrays.npz')
    checks['compaction_all_arrays_identical'] = bool(set(a.files) == set(old_layout.files)
        and all(np.array_equal(a[k], old_layout[k], equal_nan=True) for k in a.files))
    checks['compaction_caption_identical'] = (OUT/'caption.tex').read_bytes() == (previous/'caption.tex').read_bytes()
    assert checks['compaction_all_arrays_identical'] and checks['compaction_caption_identical']
    old_size = json.loads((previous/'provenance.json').read_text())['print_size_inches']
    new_size = json.loads((OUT/'provenance.json').read_text())['print_size_inches']
    checks['canvas_area_reduction_percent'] = 100*(1-np.prod(new_size)/np.prod(old_size))
checks['pass'] = True
(OUT/'verification.json').write_text(json.dumps(checks, indent=2)+'\n', encoding='utf-8')
print(json.dumps(checks, indent=2))
