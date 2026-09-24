"""Check the actual exported Figure 1 geometry independently of its formulas."""
import json
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parents[1] / 'output/figure1_journal'
a = np.load(OUT / 'geometry_arrays.npz')
C, K = a['ewald_center'], float(a['ewald_radius'])
G, D = a['selected_G'], a['view_direction']
S, P, E = a['shell_intersection'], a['ring_intersections'], a['ring_plane_ewald_section']
radius, z = np.linalg.norm(G[:2]), G[2]

def elastic_residual(angle):
    q = np.array([radius*np.cos(angle), radius*np.sin(angle), z])
    return np.dot(q-C, q-C)-K*K

# Bracket and bisect around the azimuthal orbit, without using the renderer's
# closed-form intersection coordinates.
roots = []
angles = np.linspace(0, 2*np.pi, 513)
for lo, hi in zip(angles[:-1], angles[1:]):
    if elastic_residual(lo)*elastic_residual(hi) >= 0:
        continue
    for _ in range(55):
        mid = (lo+hi)/2
        if elastic_residual(lo)*elastic_residual(mid) <= 0:
            hi = mid
        else:
            lo = mid
    angle = (lo+hi)/2
    roots.append([radius*np.cos(angle), radius*np.sin(angle), z])
roots = np.array(roots)
assert len(roots) == 2
coefficients = a['lattice_points'] @ np.linalg.inv(a['lattice_basis'])
errors = {
    'independent_ring_root_error': float(np.max(np.min(np.linalg.norm(P[:,None]-roots[None,:], axis=2), axis=1))),
    'shell_ewald_residual': float(np.max(np.abs(np.linalg.norm(S-C, axis=1)-K))),
    'shell_radius_residual': float(np.max(np.abs(np.linalg.norm(S, axis=1)-np.linalg.norm(G)))),
    'ring_section_ewald_residual': float(np.max(np.abs(np.linalg.norm(E-C, axis=1)-K))),
    'ring_plane_residual': float(np.max(np.abs(E[:,2]-z))),
    'lattice_basis_integer_residual': float(np.max(np.abs(coefficients-np.round(coefficients)))),
}
assert max(errors.values()) < 1e-12, errors

# Check the flags used to draw the curve, not a separately reconstructed mask.
assert np.array_equal(a['shell_front_ewald'], ((S-C)@D) >= 0)
old_wrong = int(np.count_nonzero((S@D >= 0) != a['shell_front_ewald']))
assert old_wrong > 0, 'This fixture must catch the former wrong-center visibility rule.'

# Inverse-project the rendered ring plane. Each displayed black dot must be on
# BOTH the teal ring and the blue Ewald-section curve, not just in the silhouette.
proj = a['projection']
for q in P:
    xy = np.linalg.solve(proj[:,:2], proj@q-proj[:,2]*z)
    assert abs(np.linalg.norm(xy)-radius) < 1e-12
    assert abs(np.linalg.norm(xy-C[:2])-K) < 1e-12

report = {
    'checks': errors,
    'ring_intersection_count': len(roots),
    'old_visibility_misclassified_samples': old_wrong,
    'sample_count': len(S),
    'projected_points_on_both_drawn_circles': True,
    'scope': 'Schematic geometry and projection only; no fit or experimental validation.',
}
(OUT/'independent_validation.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
