"""Reproduce the six fixed-scan figures with held-out detector background fits.

External artifact replay only. Existing geometry, diffraction, scales and source
states remain authoritative. Background-only controls exclude all shown rods;
shadow-contaminated whole profile bins are flagged, never partly reintegrated.
"""

# Runtime authority must be selected before importing its numerical modules.
# ruff: noqa: E402, I001

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from dataclasses import dataclass, field as dataclass_field, replace
from pathlib import Path

sys.dont_write_bytecode = True
MODE = sys.argv[1]
ROOT = Path(r"C:\Users\Kenpo\Nextcloud\Git Projects\SLATE-rMC")
PB_PATH = Path(
    r"C:\Users\Kenpo\.codex\visualizations\2026\09\04\all_materials_log\render_remaining_materials.py"
)
BI_PATH = Path(
    r"C:\Users\Kenpo\.codex\visualizations\2026\09\04\bi2x3_requested_regions\render_current_continuous_regions.py"
)
HERE = Path(__file__).resolve().parent
OUTPUT = Path(r"C:\Users\Kenpo\Downloads\2D_Manuscript\figures\background_corrected_continuous")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


if MODE == "bi2":
    sys.path[:0] = [str(ROOT.parent / "SLATE-rMC-bi2x3-polar-line-refit/src"), str(ROOT)]
    importlib.import_module("painted_ewald")
    importlib.import_module("rasim_next")
pb = load("background_pb_replay", PB_PATH)
import numpy as np
from scipy.ndimage import maximum_filter, median_filter
from scipy.optimize import least_squares
from rasim_next.fitting.radial_background import (
    RadialBackgroundProfiles,
    RadialBackgroundState,
    fit_shared_radial_background,
)

ADAPTER_ROOT = ROOT.parent / "SLATE-rMC-bi2x3-polar-line-refit" if MODE == "bi2" else ROOT
adapter = load(
    "background_existing_cells", ADAPTER_ROOT / "scripts/fit_layered_quintuple_regions.py"
)


def report(event, **values):
    print(json.dumps({"event": event, **values}), flush=True)


def coarse_mean(field, step=8):
    rows, cols = field.shape
    return (
        field[: rows // step * step, : cols // step * step]
        .reshape(rows // step, step, cols // step, step)
        .mean(axis=(1, 3))
    )


def native_from_coarse(field, shape, order=1):
    # Coordinates coincide with block centers; edge extension is explicit.
    from scipy.ndimage import map_coordinates

    row, col = np.indices(shape, dtype=float)
    return map_coordinates(field, ((row - 3.5) / 8, (col - 3.5) / 8), order=order, mode="nearest")


def background_controls(case, masks, m0_mask, dark):
    counts = case.measured_count_per_px - dark
    protected = m0_mask.copy()
    for family in masks.values():
        for mask in family.values():
            protected |= mask
    small = coarse_mean(counts)
    smooth = median_filter(small, size=5)
    row, col = np.indices(small.shape, dtype=float)
    center_col, center_row = case.inputs.instrument.detector_reference_coordinate_px
    radius = np.hypot(8 * col + 3.5 - center_col, 8 * row + 3.5 - center_row)
    radial_index = np.minimum((radius / 32).astype(int), 99)
    upper = (8 * row + 3.5) < center_row
    unprotected = coarse_mean(protected.astype(float)) == 0.0
    envelope = np.zeros(100)
    for index in range(100):
        local = smooth[(radial_index == index) & upper & unprotected]
        envelope[index] = np.quantile(local, 0.75) if local.size else np.nan
    known = np.isfinite(envelope)
    envelope = np.interp(np.arange(100), np.flatnonzero(known), envelope[known])
    expected = envelope[radial_index]
    # Only severe signal deficits with an illuminated radial control are shadows.
    shadow_small = (smooth < 0.30 * expected) & (expected > 12.0)
    shadow_small = maximum_filter(shadow_small, size=3)
    shadow = native_from_coarse(shadow_small.astype(float), counts.shape, order=0) > 0.5
    sharp = small - median_filter(small, size=5 if case.key.startswith("bi2") else 21)
    sharp = sharp > np.maximum(4.0, 5.0 * np.sqrt(np.maximum(smooth, 1.0) / 64))
    sharp = maximum_filter(sharp, size=9)
    sharp_native = native_from_coarse(sharp.astype(float), counts.shape, order=0) > 0.5
    native_row = np.arange(counts.shape[0])[:, None]
    excluded = (~case.detector_valid_mask) | shadow | sharp_native | (native_row >= center_row)
    return counts, protected, excluded, shadow


def fit_field(case, counts, protected, excluded, dark, guard_px):
    # Coarse dilation avoids an expensive full-resolution morphology sweep.
    small_guard = coarse_mean(protected.astype(float)) > 0
    small_guard = maximum_filter(small_guard, size=2 * int(np.ceil(guard_px / 8)) + 1)
    guard = native_from_coarse(small_guard.astype(float), counts.shape, order=0) > 0.5
    exclusion = excluded | guard
    center = tuple(case.inputs.instrument.detector_reference_coordinate_px)
    stride = 2 if case.key.startswith("bi2") else 4
    radius, sector, density, support = adapter._robust_radial_cells(
        counts=counts,
        beam_center_column_row_px=center,
        excluded_flat_pixel_index=np.flatnonzero(exclusion),
        sample_stride=stride,
        radial_bin_width_px=16.0,
        azimuth_sector_count=64,
        minimum_radius_px=60.0,
        maximum_radius_px=2300.0,
        border_px=12,
    )
    train = sector % 4 != 0
    profiles = RadialBackgroundProfiles(
        dataset_ids=(case.key,),
        dataset_index=np.zeros(radius.size, dtype=int),
        radius_px=radius,
        azimuth_sector_index=sector,
        density_count_per_px=density,
        support_px2=support,
        is_training=train,
    )
    fitted = fit_shared_radial_background(profiles)
    if not fitted.success:
        raise RuntimeError(f"{case.key}: radial background optimizer failed")
    base = fitted.state.count_density(case.key, radius)
    angle = (sector + 0.5) * 2 * np.pi / 64
    xy = np.column_stack((radius * np.cos(angle), radius * np.sin(angle))) / 1500.0
    scale = np.sqrt(np.maximum(density, 1.0))
    correction = least_squares(
        lambda beta: np.r_[((base * np.exp(xy @ beta) - density) / scale)[train], beta / 0.5],
        np.zeros(2),
        bounds=(-1.0, 1.0),
        loss="soft_l1",
        f_scale=1.0,
    )
    extended = base * np.exp(xy @ correction.x)
    heldout = ~train
    mae_base = float(np.mean(np.abs(base[heldout] - density[heldout])))
    mae_extended = float(np.mean(np.abs(extended[heldout] - density[heldout])))
    beta = correction.x if mae_extended < 0.98 * mae_base else np.zeros(2)
    selected = base * np.exp(xy @ beta)
    row, col = np.indices(counts.shape, dtype=float)
    rr = np.hypot(col - center[0], row - center[1])
    field = (
        fitted.state.count_density(case.key, rr)
        * np.exp((beta[0] * (col - center[0]) + beta[1] * (row - center[1])) / 1500.0)
        + dark
    )
    old = np.broadcast_to(case.background_count_per_px, counts.shape) - dark
    # Compare old and new on the identical robust held-out observation cells.
    old_r, old_s, old_y, _ = adapter._robust_radial_cells(
        counts=old,
        beam_center_column_row_px=center,
        excluded_flat_pixel_index=np.flatnonzero(exclusion),
        sample_stride=stride,
        radial_bin_width_px=16.0,
        azimuth_sector_count=64,
        minimum_radius_px=60.0,
        maximum_radius_px=2300.0,
        border_px=12,
    )
    new_keys = list(
        zip(sector.tolist(), np.floor((radius - 60) / 16).astype(int).tolist(), strict=True)
    )
    old_lookup = dict(
        zip(
            zip(old_s.tolist(), np.floor((old_r - 60) / 16).astype(int).tolist(), strict=True),
            old_y,
            strict=True,
        )
    )
    old_prediction = np.asarray([old_lookup.get(key, np.nan) for key in new_keys])
    matched = heldout & np.isfinite(old_prediction)
    metrics = {
        "guard_px": guard_px,
        "control_cell_count": int(radius.size),
        "heldout_cell_count": int(matched.sum()),
        "state_parameters": fitted.state.parameter_vector.tolist(),
        "spatial_beta_xy": beta.tolist(),
        "radial_only_heldout_mae": mae_base,
        "spatial_candidate_heldout_mae": mae_extended,
        "old_heldout_mae": float(np.mean(np.abs(old_prediction[matched] - density[matched]))),
        "new_heldout_mae": float(np.mean(np.abs(selected[matched] - density[matched]))),
        "old_heldout_bias": float(np.mean(old_prediction[matched] - density[matched])),
        "new_heldout_bias": float(np.mean(selected[matched] - density[matched])),
        "minimum_control_radius_px": float(radius.min()),
        "center_column_row_px": list(center),
        "optimizer_success": fitted.success,
    }
    metrics["adopted_new_field"] = metrics["new_heldout_mae"] < 0.90 * metrics["old_heldout_mae"]
    if not metrics["adopted_new_field"]:
        field = np.array(np.broadcast_to(case.background_count_per_px, counts.shape), copy=True)
        selected = old_prediction.copy()
    elif case.key in {"sid1", "clean1"}:
        # No off-rod controls constrain the central radius. Retain the earlier
        # local background there; only blend where new detector controls exist.
        start = float(radius.min())
        blend = np.clip((rr - start) / 64.0, 0.0, 1.0)
        blend = blend * blend * (3.0 - 2.0 * blend)
        prior = np.broadcast_to(case.background_count_per_px, counts.shape)
        field = prior * (1.0 - blend) + field * blend
        metrics["central_prior_policy"] = {
            "retain_prior_below_radius_px": start,
            "smooth_blend_width_px": 64.0,
        }
    if case.key == "b4":
        source_path = pb.B4_BACKGROUND.with_name("pbi2_b4_detector_background.manifest.json")
        source = json.loads(source_path.read_text(encoding="utf-8"))
        state = RadialBackgroundState.from_parameter_vector(
            (case.key,),
            np.asarray(source["background_parameters"]),
            parameter_covariance=np.zeros((6, 6)),
        )
        beam_col, beam_row = source["beam_center_column_row_px"]
        radial_field = state.count_density(case.key, np.hypot(col - beam_col, row - beam_row))
        blend = np.clip((float(radius.min()) - rr) / 64.0, 0.0, 1.0)
        blend = blend * blend * (3.0 - 2.0 * blend)
        prior = np.broadcast_to(case.background_count_per_px, counts.shape)
        field = prior * (1.0 - blend) + radial_field * blend
        metrics["targeted_correction"] = (
            "Central continuity correction: remove artificial horizon step using original radial state below unsupported control radius; outer field unchanged; central extrapolation not independently validated"
        )
        metrics["central_continuity_radius_px"] = float(radius.min())
        metrics["radial_state_source"] = pb.file_record(source_path)
    final_r, final_s, final_y, _ = adapter._robust_radial_cells(
        counts=field - dark,
        beam_center_column_row_px=center,
        excluded_flat_pixel_index=np.flatnonzero(exclusion),
        sample_stride=stride,
        radial_bin_width_px=16.0,
        azimuth_sector_count=64,
        minimum_radius_px=60.0,
        maximum_radius_px=2300.0,
        border_px=12,
    )
    final_lookup = dict(
        zip(
            zip(final_s.tolist(), np.floor((final_r - 60) / 16).astype(int).tolist(), strict=True),
            final_y,
            strict=True,
        )
    )
    selected = np.asarray([final_lookup.get(key, np.nan) for key in new_keys])
    matched &= np.isfinite(selected)
    metrics["final_heldout_mae"] = float(np.mean(np.abs(selected[matched] - density[matched])))
    metrics["final_heldout_bias"] = float(np.mean(selected[matched] - density[matched]))
    metrics["control_sampling_stride"] = stride
    report("background_fitted", case=case.key, **metrics)
    return (
        field,
        metrics,
        {
            "radius": radius,
            "sector": sector,
            "density": density,
            "support": support,
            "training": train,
            "old": old_prediction,
            "new": selected,
        },
    )


def fit_background(case, masks, m0_mask, dark):
    counts, protected, excluded, shadow = background_controls(case, masks, m0_mask, dark)
    field, metrics, cells = fit_field(case, counts, protected, excluded, dark, 32)
    wide, sensitivity, _ = fit_field(case, counts, protected, excluded, dark, 48)
    relative = np.abs(wide - field) / np.maximum(field, 1.0)
    selected = protected & ~shadow & case.detector_valid_mask
    metrics["guard_sensitivity_median_relative"] = float(np.median(relative[selected]))
    metrics["guard_sensitivity_p95_relative"] = float(np.quantile(relative[selected], 0.95))
    metrics["wide_guard"] = sensitivity
    metrics["empirical_shadow_pixels"] = int(shadow.sum())
    return field, wide, shadow, metrics, cells


def pb_m0_background(case, frame_builder, new_field):
    geometry_case = replace(
        case,
        background_count_per_px=new_field,
        density_evaluator=pb.zero_density_for_display_geometry,
    )
    if case.key == "clean1":
        angle = pb.loaded_module("all_materials_clean1_angle", pb.CLEAN1_ANGLE)
        frame = angle.nominal_frame(case.inputs, case.image_id)
        with np.load(pb.CLEAN1_WIDE, allow_pickle=False) as archive:
            common = (archive["measured_area"] > 0) & (archive["model_area"] > 0)
        theta = np.linspace(1, 30, 291)
        phi = np.linspace(-10, 10, 81)
        projector = pb.compile_detector_profile_projector(
            instrument=case.inputs.instrument,
            angle_frame=frame,
            two_theta_bounds_rad=np.deg2rad(np.column_stack((theta[:-1], theta[1:]))),
            phi_bin_edges_rad=np.broadcast_to(np.deg2rad(phi), (290, 81)),
            detector_valid_mask=case.detector_valid_mask,
        )
        projected = pb.project_detector_profiles(projector, new_field)
        common &= projected.valid
        norm = np.where(common, projected.N, 0).sum(axis=1)
        background = np.where(common, projected.S, 0).sum(axis=1) / norm
        return background, case.m0_profile["detector_mask"], {"operator": projector.cache_key}
    if case.key == "b4":
        # The saved B4 m0 used canonical roundtrip support. Rebuild its source
        # chunks from the same authority, evaluating geometry only.
        core = sys.modules["pbi2_b4_single_peak_refit"]
        mosaic = sys.modules["tmp_b4_mosaic_fit"]
        chunked, _, _ = core.sobol_detector(mosaic, 256)
        rods = tuple(rod for rod in case.detector.rods if int(rod.family_m) == 0)
        detectors = tuple(child.restrict_rods(rods) for child in chunked.detectors)

        def supported_zero(family, columns, rows):
            supported = pb.b4_canonical_roundtrip_support(detectors, columns, rows)
            return np.where(supported, 0.0, np.nan), {"geometry_only": True}

        geometry_case = replace(geometry_case, density_evaluator=supported_zero)
    profile, evidence, mask = pb.make_structure_m0_profile(geometry_case, frame_builder)
    return (
        profile["background_count_per_px"],
        mask,
        {**evidence, "measured_replay": profile["measured_count_per_px"]},
    )


def save_result(
    case, profiles, m0, field, wide, shadow, metrics, cells, provenance, masks, m0_mask
):
    arrays = {
        "background_native_count_per_px": field,
        "wide_guard_background_native_count_per_px": wide,
        "empirical_shadow_mask": shadow,
    }
    arrays.update({f"control_{key}": value for key, value in cells.items()})
    comparisons = {}
    for name, item in [
        (f"m{m}_{branch}", profiles[m][branch]) for m in (1, 3, 4) for branch in ("minus", "plus")
    ] + [("m0", m0)]:
        measured = item.get("measured_count_per_px", item.get("measured"))
        background = item.get("background_count_per_px", item.get("background"))
        for key, val in {
            "coordinate": item.get("L", item.get("qz_Ainv")),
            "measured_count_per_px": measured,
            "background_count_per_px": background,
            "diffraction_A2_per_px2": item["diffraction_A2_per_px2"],
            "model_total_count_per_px": item["model_total_count_per_px"],
            "old_background_count_per_px": item["old_background"],
            "old_model_total_count_per_px": item["old_model"],
            "original_valid": item["original_valid"],
            "valid": item["valid"],
            "possible_shadow_bin": item.get(
                "possible_shadow_bin", np.zeros(item["valid"].shape, dtype=bool)
            ),
        }.items():
            arrays[f"{name}_{key}"] = val
        assert np.allclose(
            case.scale_count_per_A2 * item["diffraction_A2_per_px2"] + background,
            item["model_total_count_per_px"],
            equal_nan=True,
            rtol=1e-13,
        )
        valid = (
            item["valid"]
            & (measured > 0)
            & (item["old_model"] > 0)
            & (item["model_total_count_per_px"] > 0)
        )
        comparisons[name] = {
            "old_mean_absolute_log10_error": float(
                np.mean(np.abs(np.log10(item["old_model"][valid] / measured[valid])))
            ),
            "new_mean_absolute_log10_error": float(
                np.mean(np.abs(np.log10(item["model_total_count_per_px"][valid] / measured[valid])))
            ),
            "retained_bins": int(valid.sum()),
            "possible_shadow_bins_retained": int(
                np.count_nonzero(item["original_valid"] & item.get("possible_shadow_bin", False))
            ),
        }
    archive = HERE / f"{case.key}_background_corrected.ra_diag.npz"
    np.savez_compressed(archive, **arrays)
    report("profiles_saved", case=case.key, comparisons=comparisons)
    with tempfile.TemporaryDirectory(prefix=f"slate_background_{case.key}_") as temp:
        temp = Path(temp)
        detector_png = temp / "detector.png"
        profile_png = temp / "profiles.png"
        pb.render_detector(case, masks, pb.filled_region_for_display(m0_mask), detector_png)
        if case.key.startswith("bi2"):
            bi = sys.modules["background_bi_replay"]
            bi.OUTPUT = temp
            profile_png = bi.render_profile_grid(
                case.key, profiles, m0, bi.STAGES[case.key], case.source_count
            )
        else:
            pb.render_profile_grid(case, profiles, m0, profile_png)
        png, pdf = pb.compose_page(case, detector_png, profile_png)
    manifest = {
        "schema": "detector-background-corrected-continuous-figures.v1",
        "case": case.key,
        "background_status": "PROVISIONAL_EMPIRICAL_OFFROD_VALIDATION_SELECTED_BACKGROUND; NOT A NEW STRUCTURE FIT",
        "model_status": case.model_status,
        "scale_count_per_A2": case.scale_count_per_A2,
        "diffraction_and_scale_frozen": True,
        "background_fit": metrics,
        "shadow_policy": "possible shadow bins identified from >1% empirical shadow area; all original supported bins remain visible in both curves; obstruction is not modeled",
        "validation_scope": "Withheld off-rod sectors select the model; errors are selection-set results, not untouched final-test estimates. Central priors/extrapolations remain provisional.",
        "profile_comparisons": comparisons,
        "sources": provenance,
        "replay": pb.file_record(Path(__file__)),
        "diagnostic": pb.file_record(archive),
        "outputs": {"png": pb.file_record(png), "pdf": pb.file_record(pdf)},
    }
    (HERE / f"{case.key}_background_corrected.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    report("figure_complete", case=case.key, pdf=str(pdf))


def run_pb():
    loader = {"gd_sid": pb.load_gd_sid_cases, "clean1": pb.load_clean1_case, "b4": pb.load_b4_case}[
        MODE
    ]
    cases, frame_builder, provenance = loader()
    for case in cases:
        report("case_loaded", case=case.key)
        profiles, m0, old_path = pb.load_saved_profiles(case)
        masks = pb.reciprocal_region_display_masks(case)
        if case.m0_profile is not None:
            m0_mask = case.m0_profile["detector_mask"]
        else:
            frame = pb.build_angle_frame(case, frame_builder)
            m0_mask, _ = pb.angle_region_detector_mask(
                case, frame, np.linspace(1, 30, 291), np.linspace(-10, 10, 81)
            )
        dark = 0.0
        if MODE == "gd_sid":
            executor = sys.modules["all_materials_gd_sid"]
            source = json.loads(executor.SOURCE_JSON.read_text(encoding="utf-8"))
            background = json.loads(
                Path(source["inputs"]["background_json"]).read_text(encoding="utf-8")
            )
            dark = executor.FIT.read_osc(
                Path(source["inputs"]["dark_path"])
            ).detector_native_counts.astype(float) * float(background["inputs"]["dark_scale"])
        field, wide, shadow, metrics, cells = fit_background(case, masks, m0_mask, dark)
        for family in profiles.values():
            for item in family.values():
                item["old_background"] = item["background"].copy()
                item["old_model"] = item["model_total_count_per_px"].copy()
                item["original_valid"] = item["valid"].copy()
                item["background"] = pb.projected_field_mean(
                    item["projection"], field, item["support"]
                )
                fraction = pb.projected_field_mean(
                    item["projection"], shadow.astype(float), item["support"]
                )
                item["possible_shadow_bin"] = fraction > 0.01
                item["model_total_count_per_px"] = (
                    case.scale_count_per_A2 * item["diffraction_A2_per_px2"] + item["background"]
                )
        m0["old_background"] = m0["background_count_per_px"].copy()
        m0["old_model"] = m0["model_total_count_per_px"].copy()
        m0["original_valid"] = m0["valid"].copy()
        new_m0, _, m0_evidence = pb_m0_background(case, frame_builder, field)
        if "measured_replay" in m0_evidence:
            replay = m0_evidence.pop("measured_replay")
            if not np.allclose(
                replay, m0["measured_count_per_px"], rtol=1e-12, atol=1e-9, equal_nan=True
            ):
                raise ValueError(f"{case.key}: m0 background projection changed support")
        m0["background_count_per_px"] = new_m0
        m0["model_total_count_per_px"] = (
            case.scale_count_per_A2 * m0["diffraction_A2_per_px2"] + new_m0
        )
        corrected = replace(
            case,
            background_count_per_px=field,
            background_note=(
                "Central background continuity correction is provisional; original outer background and diffraction preserved"
                if case.key == "b4"
                else "Off-rod background; frozen diffraction/scale; all data retained, including possible shadow-affected low-q bins"
            ),
        )
        save_result(
            corrected,
            profiles,
            m0,
            field,
            wide,
            shadow,
            metrics,
            cells,
            {
                **provenance,
                "prior_profiles": pb.file_record(old_path),
                "m0_projection": m0_evidence,
            },
            masks,
            m0_mask,
        )


def bi_display_masks(case, bi):
    shape = case.measured_count_per_px.shape
    measure = bi.build_nominal_ewald_context(case.inputs).geometry
    frame = pb.LayeredReciprocalFrame(
        reciprocal_basis_Ainv=case.inputs.reciprocal.basis_Ainv,
        sample_from_crystal_rotation=case.inputs.instrument.sample_from_crystal.rotation,
        axial_basis_index=2,
    )
    masks = {m: {b: np.zeros(shape, dtype=bool) for b in ("plus", "minus")} for m in (1, 3, 4)}
    center = case.inputs.instrument.detector_reference_coordinate_px
    for first in range(0, int(np.ceil(center[1])), 128):
        rows = np.arange(first, min(first + 128, int(np.ceil(center[1]))))
        col, row = np.meshgrid(np.arange(shape[1], dtype=float), rows.astype(float))
        geometry = measure.evaluate_detector_geometry(
            col.ravel(), row.ravel(), include_surface_jacobian=False
        )
        qr, ell = frame.coordinates(np.asarray(geometry.q_sample_Ainv))
        common = (
            np.asarray(geometry.valid)
            & (ell >= 2)
            & (ell <= 17)
            & (np.asarray(geometry.kf_air_sample_Ainv)[:, 2] >= 0)
        )
        for m, bounds in bi.FAMILY_RADIAL_INTERVAL_AINV[case.key].items():
            inside = common & (qr >= bounds[0]) & (qr <= bounds[1])
            for branch in ("plus", "minus"):
                side = col.ravel() <= center[0] if branch == "plus" else col.ravel() > center[0]
                masks[m][branch][first : first + rows.size] = (inside & side).reshape(
                    rows.size, shape[1]
                )
    return masks


@dataclass
class CachedAngleReplay:
    """Reuse the identical q4/q8 diffraction integrals for two background fields."""

    runner: object
    integrals: dict = dataclass_field(default_factory=dict)
    measured: dict | None = None
    projector_bundle: dict | None = None

    def _measured_angle_maps(self, detector, frame, decoded):
        if self.measured is None:
            self.measured, self.projector_bundle = self.runner._measured_angle_maps(
                detector, frame, decoded
            )
            return self.measured, self.projector_bundle
        result = dict(self.measured)
        shape = self.projector_bundle["shape"]
        signal = np.zeros(shape)
        norm = np.zeros(shape)
        field = np.where(
            decoded["detector_valid_mask"],
            np.maximum(decoded["radial_background_count_per_px"], 0),
            0,
        )
        for index, projector in self.projector_bundle["items"]:
            projected = pb.project_detector_profiles(projector, field)
            signal[index] = projected.S[0]
            norm[index] = projected.N[0]
        result["measured_radial_background_signal_count"] = signal
        result["measured_radial_background_normalization_px2"] = norm
        assert np.array_equal(norm, self.measured["measured_radial_background_normalization_px2"])
        return result, self.projector_bundle

    def _integrate_continuous_angle_bins(self, detector, frame, decoded, order, **kwargs):
        if order not in self.integrals:
            self.integrals[order] = self.runner._integrate_continuous_angle_bins(
                detector, frame, decoded, order, **kwargs
            )
        return self.integrals[order]


def run_bi():
    bi = load("background_bi_replay", BI_PATH)
    runner = bi.load_runner()
    refit, fit_profiles, _, _ = runner._legacy_modules(load_resume=False)
    refit.build_detectors = runner.build_detectors
    archive, archive_sha = runner._load_archive_bound(refit, runner.ARTIFACT)
    scales, scale_sha, _ = bi.load_prior_display_scales()
    for material in ("bi2se3", "bi2te3"):
        film = archive["films"][material]
        stage = film[bi.STAGES[material]]
        record = dict(film["prepared"])
        record["input_provenance"] = runner._record_input_provenance(record)
        detectors, series = runner.build_detectors(
            record, int(stage["source_count"]), runner._mosaic_parameters_from_stage(stage)
        )
        inputs = series.inputs[0]
        decoded = runner._load_decoded_fields(
            record,
            "fixed_5deg",
            record["input_provenance"]["files"]["decoded/fixed_5deg.npz"]["sha256"],
        )
        compiled, authority = runner._build_exact_compiled_angle_detector(inputs, detectors[0])
        angle_frame = fit_profiles.nominal_frame(
            inputs, "bi2x3-signed-polar-line-angle.v1:fixed_5deg"
        )
        raw = np.asarray(decoded["detector_native_counts"], dtype=float)
        measured = raw - float(decoded["dark_background_counts"])
        case = pb.MaterialCase(
            key=material,
            label_plain={"bi2se3": "Bi₂Se₃", "bi2te3": "Bi₂Te₃"}[material],
            label_math=bi.LABELS[material],
            archetype="pure ordered film",
            image_id=f"{material} fixed 5deg",
            image_label=decoded["path"],
            incidence_deg=5,
            detector=detectors[0],
            inputs=inputs,
            raw_count_per_px=raw,
            measured_count_per_px=measured,
            detector_valid_mask=np.asarray(decoded["detector_valid_mask"], dtype=bool),
            background_count_per_px=np.asarray(decoded["radial_background_count_per_px"]),
            scale_count_per_A2=scales[material],
            source_count=int(stage["source_count"]),
            model_status="ARCHIVED V1 MOSAIC; PURE CIF; SF NOT RUN",
            background_note="Off-rod detector background; fixed dark/scale; central extrapolation provisional; all supported data retained",
            density_evaluator=pb.zero_density_for_display_geometry,
        )
        report("case_loaded", case=material)
        masks = bi_display_masks(case, bi)
        m0_mask, _ = pb.angle_region_detector_mask(
            case, angle_frame, np.linspace(1, 30, 291), np.linspace(-10, 10, 81)
        )
        field, wide, shadow, metrics, cells = fit_background(case, masks, m0_mask, 0.0)
        corrected_decoded = dict(decoded)
        corrected_decoded["radial_background_count_per_px"] = field
        profiles = {m: {} for m in (1, 3, 4)}
        for m in (1, 3, 4):
            for branch in ("minus", "plus"):
                item = bi.offspecular_branch_profile(
                    runner,
                    material,
                    record,
                    inputs,
                    compiled,
                    corrected_decoded,
                    m,
                    branch,
                    case.scale_count_per_A2,
                )
                quad = bi.compile_offspecular_branch_quadrature(
                    material, record, inputs, raw.shape[1], m, branch
                )
                projection = pb.compile_native_pixel_region_projection(quad, raw.shape)
                support = np.asarray(projection.observation_measure_px2)
                item["old_background"] = pb.projected_field_mean(
                    projection, case.background_count_per_px, support
                )
                item["old_model"] = (
                    case.scale_count_per_A2 * item["diffraction_A2_per_px2"]
                    + item["old_background"]
                )
                item["original_valid"] = item["valid"].copy()
                item["possible_shadow_bin"] = (
                    pb.projected_field_mean(projection, shadow.astype(float), support) > 0.01
                )
                profiles[m][branch] = item
                report("continuous_profile_complete", case=material, family=m, branch=branch)
        cached_runner = CachedAngleReplay(runner)
        m0, m0_evidence = bi.m0_line_profile(
            cached_runner, compiled, angle_frame, corrected_decoded, inputs, case.scale_count_per_A2
        )
        old_m0, _ = bi.m0_line_profile(
            cached_runner, compiled, angle_frame, decoded, inputs, case.scale_count_per_A2
        )
        assert np.array_equal(
            m0["diffraction_A2_per_px2"], old_m0["diffraction_A2_per_px2"], equal_nan=True
        )
        assert np.array_equal(
            m0["measured_count_per_px"], old_m0["measured_count_per_px"], equal_nan=True
        )
        m0["old_background"] = old_m0["background_count_per_px"]
        m0["old_model"] = old_m0["model_total_count_per_px"]
        m0["original_valid"] = m0["valid"].copy()
        corrected = replace(case, background_count_per_px=field)
        save_result(
            corrected,
            profiles,
            m0,
            field,
            wide,
            shadow,
            metrics,
            cells,
            {
                "fit_archive": {"path": str(runner.ARTIFACT), "sha256": archive_sha},
                "scale_manifest_sha256": scale_sha,
                "decoded": {"path": decoded["path"], "sha256": decoded["sha256"]},
                "continuous_diffraction_authority": authority,
                "m0_projection": m0_evidence,
            },
            masks,
            m0_mask,
        )


if __name__ == "__main__":
    OUTPUT.mkdir(parents=True, exist_ok=True)
    pb.OUTPUT = OUTPUT
    if MODE == "bi2":
        run_bi()
    else:
        run_pb()
