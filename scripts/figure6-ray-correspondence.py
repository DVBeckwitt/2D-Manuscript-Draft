"""Export one actual source-model ray for the Figure 6 projection guide."""
from pathlib import Path
import sys, json
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / 'presentation_asset_library/releases/2026-09-10_v9/source/engines/SLATE-rMC'
sys.path.insert(0, str(ENGINE / 'scripts/figures'))
import render_bi2se3_publication_mapping as m
from rasim_next.pipeline.configured_simulation import load_simulation_config, build_configured_simulation_inputs, build_nominal_ewald_context
settings = m.FigureSettings(incidence_deg=10, mosaic_alpha_count=32)
config = m.apply_figure_settings(load_simulation_config(ENGINE / 'configs/bi2se3_simulation.yaml', repository_root=ENGINE), settings)
inputs = build_configured_simulation_inputs(config)
nominal = build_nominal_ewald_context(inputs)
tilted = m.tilt_detector_about_reference(inputs.instrument, column_tilt_deg=0, row_tilt_deg=20)
rays = m._sample_schematic_rays(nominal, tilted_instrument=tilted, alpha_nodes_rad=m.select_scale_resolved_mosaic_alpha_nodes(inputs, count=32))
projection = m.project_detector_rays(np.broadcast_to(rays.origin_lab_m, rays.direction_lab.shape), rays.direction_lab, inputs.instrument)
rot = inputs.instrument.lab_from_sample.rotation
u = (rays.intrinsic_direction_lab @ rot) @ m._incident_aligned_basis(nominal.ki_sample_Ainv)
e, a = np.radians([18, -52])
view = np.array([np.cos(e)*np.cos(a), np.cos(e)*np.sin(a), np.sin(e)])
horizontal = u @ np.array([-np.sin(a), np.cos(a), 0])
vertical_scale = np.sqrt(np.sin(e)**2 + (1.08 / 1.025)**2*np.cos(e)**2)
vertical = u @ np.array([-np.sin(e)*np.cos(a), -np.sin(e)*np.sin(a), (1.08/1.025)*np.cos(e)]) / vertical_scale
good = (u @ view > .25) & (projection.column_px > 350) & (projection.column_px < 2650) & (projection.row_px > 150) & (projection.row_px < 1250)
indices = np.flatnonzero(good)
if not len(indices): raise RuntimeError('No visible common ray meets annotation bounds')
i = indices[np.argmax(rays.intrinsic_density_A2_rad2_inv[indices])]
origin = rays.origin_lab_m
direction = rays.direction_lab[i]
point = rays.ideal_point_lab_m[i]
t = np.dot(point-origin,direction)
error = np.linalg.norm(point-origin-t*direction)
assert error < 1e-10
result = {'sphere_xy_fraction': [float((1+vertical[i])/2), float((1-horizontal[i])/2)], 'detector_column_row_px': [float(projection.column_px[i]), float(projection.row_px[i])], 'internal_direction_lab': rays.intrinsic_direction_lab[i].tolist(), 'air_direction_lab': direction.tolist(), 'sample_origin_lab_m': origin.tolist(), 'detector_point_lab_m': point.tolist(), 'ray_collinearity_error_m': float(error), 'purpose': 'geometric correspondence; no intensity fitting or reconstruction'}
out=ROOT/'output/figure6_revision/ray_correspondence.json'
out.write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
