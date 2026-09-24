"""External six-sample replay; existing numerical packages remain read-only."""

from __future__ import annotations

import importlib.util
import json
import sys
import time
import hashlib
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import numpy as np

HERE = Path(__file__).resolve().parent
BACKGROUND = HERE.parent / "background_correction"
ROOT = Path(r"C:\Users\Kenpo\Nextcloud\Git Projects\SLATE-rMC")
MATERIAL = sys.argv[1]
sys.dont_write_bytecode = True


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def report(event, **fields):
    print(json.dumps({"event": event, "material": MATERIAL, **fields}), flush=True)


def load_bi_case(material):
    # Import the exact archived CIF compiler before renderer imports select paths.
    sys.path[:0] = [str(ROOT.parent / "SLATE-rMC-bi2x3-polar-line-refit/src"), str(ROOT)]
    import rasim_next
    import painted_ewald

    sys.argv[1] = "bi2"
    bg = load("specular_background_replay", BACKGROUND / "correct_backgrounds.py")
    bi = bg.load("specular_bi_profiles", bg.BI_PATH)
    runner = bi.load_runner()
    refit, fit_profiles, _, _ = runner._legacy_modules(load_resume=False)
    refit.build_detectors = runner.build_detectors
    archive, archive_sha = runner._load_archive_bound(refit, runner.ARTIFACT)
    film = archive["films"][material]
    stage = film[bi.STAGES[material]]
    record = dict(film["prepared"])
    record["input_provenance"] = runner._record_input_provenance(record)
    detectors, series = runner.build_detectors(
        record, int(stage["source_count"]), runner._mosaic_parameters_from_stage(stage)
    )
    inputs = series.inputs[0]
    decoded = runner._load_decoded_fields(
        record, "fixed_5deg", record["input_provenance"]["files"]["decoded/fixed_5deg.npz"]["sha256"]
    )
    detector, authority = runner._build_exact_compiled_angle_detector(inputs, detectors[0])
    detector = bi.family_detector(detector, 0)
    frame = fit_profiles.nominal_frame(inputs, "bi2x3-signed-polar-line-angle.v1:fixed_5deg")
    with np.load(decoded["path"]) as source:
        # The old radial calibration mask is not a detector/beamstop mask.
        decoded["detector_valid_mask"] = source["detector_valid_mask"].copy()
    with np.load(BACKGROUND / f"{material}_background_corrected.ra_diag.npz") as prior:
        decoded["radial_background_count_per_px"] = prior["background_native_count_per_px"].copy()
    scales, _, _ = bi.load_prior_display_scales()
    report("loaded", source_count=detector.source_state_count, archive_sha256=archive_sha)
    return bg, bi, runner, record, inputs, detector, frame, decoded, scales[material], authority


def provisional_stack(top_roughness_A=5.23725139, bottom_roughness_A=10.0):
    from rasim_next.reflectivity.specular import ParrattStitchStack

    return ParrattStitchStack(
        substrate_refractive_index=complex(0.9999929532364343, 9.672907455164902e-8),
        top_roughness_A=top_roughness_A,
        bottom_roughness_A=bottom_roughness_A,
    )


def load_pb_case(material):
    sys.argv[1] = "gd_sid" if material in ("gd1", "sid1") else material
    pb = load("specular_pb_replay", HERE.parent.parent / "04/all_materials_log/render_remaining_materials.py")
    bg = SimpleNamespace(pb=pb)
    cases, frame_builder, provenance = {
        "gd1": pb.load_gd_sid_cases, "sid1": pb.load_gd_sid_cases,
        "clean1": pb.load_clean1_case, "b4": pb.load_b4_case,
    }[material]()
    case = next(c for c in cases if c.key == material)
    bridge = load("pbi2_specular_bridge", HERE / "pbi2_m0_adapter.py")
    generic = load("existing_cif_packing_for_m0", ROOT.parent / "SLATE-rMC-bi2x3-polar-line-refit"
                   / "src/rasim_next/pipeline/_continuous_detector_kernel.py")
    detectors, probabilities = (case.detector,), (1.0,)
    source_mass = 1.0
    indices = (np.arange(case.detector.source_state_count),)
    strength, envelope = case.detector.strength_model, case.detector.intensity_envelope
    if material in ("clean1", "b4"):
        from rasim_next.ordered.motifs import extract_pbi2_motifs
        from rasim_next.pipeline.bragg_space import CifFiniteStackStrength
        from rasim_next.core.contracts import EventIntensityNormalization
        from rasim_next.pipeline.continuous_detector import SampleQIntensityEnvelope

        if material == "clean1":
            angle = sys.modules["all_materials_clean1_angle"]
            simulation = angle.clean1.source_inputs({"angle": 4.7})
            selected = json.loads(pb.CLEAN1_FIT.read_text(encoding="utf-8"))["selected"]["parameters"]
            z, ur, uz = selected["z"], selected["ur"], selected["uz"]
            state = case.detector.incident.states
            waves = np.unique(state.wavelength_A)
            per_wave = case.source_count // len(waves)
            indices = (np.concatenate([np.flatnonzero(state.wavelength_A == w)[:per_wave] for w in waves]),)
            source_mass = float(np.sum(state.source_weight[indices[0]]))
            assert len(indices[0]) == case.source_count
            frame = angle.nominal_frame(case.inputs, case.image_id)
        else:
            mosaic = sys.modules["tmp_b4_mosaic_fit"]
            core = sys.modules["pbi2_b4_single_peak_refit"]
            chunked, _, simulation = core.sobol_detector(mosaic, 256)
            detectors = tuple(replace(d, mosaic=case.detector.mosaic) for d in chunked.detectors)
            probabilities = tuple(chunked.chunk_probability)
            indices = tuple(np.arange(d.source_state_count) for d in detectors)
            fit = json.loads(pb.B4_FIT.read_text(encoding="utf-8"))
            z = fit["selected"]["z_iodine_fractional_layer"]
            ur, uz = fit["u_radial_A2"], fit["u_normal_A2"]
            frame = pb.build_angle_frame(case, frame_builder)
        crystal = simulation.crystal
        motifs = extract_pbi2_motifs(crystal)
        assert len(motifs) == 1
        sites = tuple(replace(crystal.sites[a.site_index], fractional=(
            a.fractional_offset[0], a.fractional_offset[1],
            0.0 if a.element == "Pb" else float(np.copysign(z, a.fractional_offset[2])),
        )) for a in motifs[0].atoms)
        crystal = replace(crystal, sites=sites,
                          provenance=crystal.provenance + "; signed Pb-centered m0 trilayer")
        strength = CifFiniteStackStrength(crystal, repeats=72,
            normalization=EventIntensityNormalization.FINITE_PER_LAYER, unknown_u_iso_A2=0.0)
        envelope = SampleQIntensityEnvelope(u_radial_A2=ur, u_normal_A2=uz)
    else:
        frame = pb.build_angle_frame(case, frame_builder)
    detector = bridge.PbSpecularDetector(
        detectors, probabilities, strength, envelope, provisional_stack(),
        generic.pack_cif_finite_stack_structures, indices, source_mass,
    )
    report("loaded", source_count=case.source_count, source_mass_divisor=source_mass)
    return bg, case, detector, frame, provenance


def prepare_angle_observations(instrument, frame, raw, dark, background, detector_valid):
    from rasim_next.measurement import compile_detector_profile_projector, project_detector_profiles

    theta_edges = np.linspace(1.0, 30.0, 291)
    phi_edges = np.linspace(-10.0, 10.0, 81)
    projector = compile_detector_profile_projector(
        instrument=instrument, angle_frame=frame,
        two_theta_bounds_rad=np.deg2rad(np.column_stack((theta_edges[:-1], theta_edges[1:]))),
        phi_bin_edges_rad=np.broadcast_to(np.deg2rad(phi_edges), (290, 81)),
        detector_valid_mask=np.ones(raw.shape, dtype=bool),
    )
    invalid_overlap = np.bincount(
        projector.coverage_profile_bin_index,
        weights=(~detector_valid.ravel()[projector.coverage_pixel_index]).astype(float),
        minlength=290 * 80,
    ).reshape(290, 80)
    observed = project_detector_profiles(projector, raw)
    dark_projected = project_detector_profiles(projector, np.full(raw.shape, dark))
    bg = project_detector_profiles(projector, background)
    valid = projector.profile_bin_valid_mask & observed.valid & bg.valid & (invalid_overlap == 0)
    area = np.where(valid, observed.N, 0).sum(axis=1)
    measured = np.divide(np.where(valid, observed.S - dark_projected.S, 0).sum(axis=1), area,
                         out=np.full(290, np.nan), where=area > 0)
    background_line = np.divide(np.where(valid, bg.S, 0).sum(axis=1), area,
                                out=np.full(290, np.nan), where=area > 0)
    report("observations_prepared", valid_bins=int(valid.sum()), first_theta_deg=float(
        ((theta_edges[:-1] + theta_edges[1:]) / 2)[area > 0][0]))
    return measured, background_line, area > 0, np.flatnonzero(valid.ravel()), projector.cache_key


def angle_quadrature(chart, bins, order):
    from rasim_next.measurement import compile_continuous_rectangle_quadrature

    ti, pi = np.divmod(bins, 80)
    te, pe = np.linspace(1, 30, 291), np.linspace(-10, 10, 81)
    return compile_continuous_rectangle_quadrature(
        chart=chart,
        first_coordinate_bounds=np.deg2rad(np.column_stack((te[ti], te[ti + 1]))),
        second_coordinate_bounds=np.deg2rad(np.column_stack((pe[pi], pe[pi + 1]))),
        observation_row=ti, observation_count=290, gauss_order=order, background_coordinate_axis=0,
    )


def integrate_quadrature(detector, quad):
    density = np.empty(len(quad.column_px))
    for start in range(0, len(density), 32000):
        stop = min(len(density), start + 32000)
        result = detector.evaluate_detector_density_all_roots(
            quad.column_px[start:stop], quad.row_px[start:stop], execution_backend="cpu"
        )
        if np.any(result.caustic) or not np.all(np.isfinite(result.density_A2_per_px2)):
            raise FloatingPointError("Continuous m0 requires caustic-aware quadrature refinement")
        density[start:stop] = result.density_A2_per_px2
    weight = quad.detector_area_weight_px2
    area = np.bincount(quad.observation_row, weights=weight, minlength=290)
    signal = np.bincount(quad.observation_row, weights=weight * density, minlength=290)
    return np.divide(signal, area, out=np.full(290, np.nan), where=area > 0)


def restore_case():
    from scipy.optimize import minimize_scalar

    if MATERIAL.startswith("bi2"):
        bg, bi, runner, record, inputs, plain, frame, decoded, scale, authority = load_bi_case(MATERIAL)
        chart = runner._AngleDetectorAreaChart(plain.instrument, frame, "restored-m0-angle.v1")
    else:
        bg, case, plain, frame, authority = load_pb_case(MATERIAL)
        inputs, scale = case.inputs, case.scale_count_per_A2
        with np.load(BACKGROUND / f"{MATERIAL}_background_corrected.ra_diag.npz") as prior:
            field = prior["background_native_count_per_px"].copy()
        decoded = dict(detector_native_counts=case.measured_count_per_px, dark_background_counts=0.,
                       radial_background_count_per_px=field, detector_valid_mask=case.detector_valid_mask)
        chart = bg.pb.AngleDetectorAreaChart(plain.instrument, frame, "restored-m0-angle.v1")
    measured, background, valid, bins, projector_revision = prepare_angle_observations(
        plain.instrument, frame, decoded["detector_native_counts"], decoded["dark_background_counts"],
        decoded["radial_background_count_per_px"], decoded["detector_valid_mask"],
    )
    low_quad = angle_quadrature(chart, bins[bins < 40 * 80], 4)
    low = valid & (np.arange(290) < 40) & (measured > 0)
    evaluations = []

    def objective(sigma):
        detector = plain.with_specular_stitch(provisional_stack(sigma))
        model = scale * integrate_quadrature(detector, low_quad) + background
        residual = np.log10(model[low] / measured[low])
        cost = float(np.mean(residual ** 2))
        evaluations.append((float(sigma), cost))
        report("optical_trial", top_roughness_A=float(sigma), mean_square_log10_error=cost)
        return cost

    initial_cost = objective(5.23725139)
    seeds = np.array([0., 2.5, 5.23725139, 7.5, 10., 15., 25., 50.])
    costs = [initial_cost if s == 5.23725139 else objective(s) for s in seeds]
    best = int(np.argmin(costs))
    bounds = (seeds[max(0, best - 1)], seeds[min(len(seeds) - 1, best + 1)])
    fit = minimize_scalar(objective, bounds=bounds, method="bounded",
                          options={"xatol": 0.05, "maxiter": 25})
    candidates = list(zip(seeds.tolist(), costs)) + [(float(fit.x), float(fit.fun))]
    selected_sigma, selected_cost = min(candidates, key=lambda item: item[1])
    fitted = plain.with_specular_stitch(provisional_stack(selected_sigma))
    arrays = {}
    for order in (4, 8):
        started = time.perf_counter()
        quad = angle_quadrature(chart, bins, order)
        arrays[f"m0_diffraction_q{order}"] = integrate_quadrature(fitted, quad)
        report("full_m0_integrated", order=order, seconds=time.perf_counter() - started)
    q4, q8 = arrays["m0_diffraction_q4"], arrays["m0_diffraction_q8"]
    convergence = float(np.linalg.norm(q8[valid] - q4[valid]) / np.linalg.norm(q8[valid]))
    low_convergence = float(np.linalg.norm(q8[low] - q4[low]) / np.linalg.norm(q8[low]))
    final_cost = float(np.mean(np.log10((scale * q8[low] + background[low]) / measured[low]) ** 2))
    initial_q8 = integrate_quadrature(plain.with_specular_stitch(provisional_stack()),
                                      angle_quadrature(chart, bins[bins < 40 * 80], 8))
    final_initial_cost = float(np.mean(np.log10((scale * initial_q8[low] + background[low]) / measured[low]) ** 2))
    arrays["m0_initial_stitched_low_q8"] = initial_q8
    with np.load(BACKGROUND / f"{MATERIAL}_background_corrected.ra_diag.npz") as prior:
        for key in prior.files:
            if key.startswith(("m1_", "m3_", "m4_")):
                arrays[key] = prior[key].copy()
        arrays["m0_previous_diffraction"] = prior["m0_diffraction_A2_per_px2"].copy()
        arrays["m0_previous_measured"] = prior["m0_measured_count_per_px"].copy()
    if MATERIAL.startswith("bi2"):
        arrays["m0_plain_same_support_low_q4"] = integrate_quadrature(plain, low_quad)
    arrays.update(m0_measured_count_per_px=measured, m0_background_count_per_px=background,
                  m0_model_total_count_per_px=scale * q8 + background, m0_valid=valid,
                  m0_theta_deg=np.linspace(1.05, 29.95, 290),
                  m0_L=(4 * np.pi / inputs.config.source.mean_wavelength_A
                        * np.sin(np.deg2rad(np.linspace(1.05, 29.95, 290) / 2))
                        / np.linalg.norm(inputs.reciprocal.basis_Ainv[:, 2])),
                  roughness_trials=np.asarray(evaluations))
    archive_path = HERE / f"{MATERIAL}_specular.ra_diag.npz"
    np.savez_compressed(archive_path, **arrays)
    manifest = {
        "schema": "conditional-low-angle-parratt-restoration.v1", "sample": MATERIAL,
        "status": "PROVISIONAL_OPTICAL_STACK; NOT AN AUTHORITATIVE STRUCTURE REFIT",
        "substrate_assumption": "Historical unverified SiO2 compatibility index held fixed",
        "film_thickness_A": float(plain.instrument.film_thickness_A),
        "top_roughness_A": selected_sigma, "bottom_roughness_A": 10.0,
        "roughness_boundary_limited": selected_sigma < 0.5 or selected_sigma > 49.5,
        "scale_count_per_A2": scale, "initial_cost": initial_cost, "selected_cost": selected_cost,
        "q8_initial_cost": final_initial_cost, "q8_selected_cost": final_cost,
        "optimizer_success": bool(fit.success), "optimizer_message": str(fit.message),
        "low_angle_quadrature_relative_l2_q4_q8": low_convergence,
        "numerical_gate_pass": convergence < .02 and low_convergence < .01 and final_cost <= final_initial_cost + 1e-5,
        "interface_assumption": "local_lamella_follows_mosaic.v1",
        "objective": "Mean squared log10 simulation+fixed-background/data, 1<2theta<5 degrees; one frozen image scale",
        "quadrature_relative_l2_q4_q8": convergence,
        "projector_revision": projector_revision, "compiler_authority": authority,
        "diagnostic": str(archive_path),
        "diagnostic_sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
        "replay": bg.pb.file_record(Path(__file__)),
        "background_manifest": bg.pb.file_record(BACKGROUND / f"{MATERIAL}_background_corrected.json"),
        "background_diagnostic": bg.pb.file_record(BACKGROUND / f"{MATERIAL}_background_corrected.ra_diag.npz"),
    }
    (HERE / f"{MATERIAL}_specular.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    report("conditional_fit_saved", top_roughness_A=selected_sigma, convergence=convergence)


if __name__ == "__main__":
    restore_case()
