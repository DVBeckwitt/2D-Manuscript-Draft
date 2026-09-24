"""Render Bi2X3 quicklooks using deterministic continuous-region quadrature."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from rasim_next.measurement import (
    LayeredReciprocalFrame,
    compile_continuous_rectangle_quadrature,
    compile_native_pixel_region_projection,
)
from rasim_next.pipeline.configured_simulation import build_nominal_ewald_context
from rasim_next.pipeline.reciprocal_detector_chart import (
    LayeredReciprocalDetectorAreaChart,
)

OUTPUT = Path(__file__).resolve().parent
PRIOR_SCALE_MANIFEST = OUTPUT / "continuous_region_preview_manifest.json"
RUNNER = (
    Path(r"C:\Users\Kenpo\Nextcloud\Obsidian\Research\Rigaku XRD\SLATE Fit Library")
    / "runs"
    / "bi2x3-signed-polar-line-refit-2026-09-03"
    / "replay"
    / "run_refit.py"
)
LABELS = {"bi2se3": r"Bi$_2$Se$_3$", "bi2te3": r"Bi$_2$Te$_3$"}
STAGES = {"bi2se3": "mosaic_final", "bi2te3": "mosaic_pre_caustic"}
FAMILY_RADIAL_INTERVAL_AINV = {
    "bi2se3": {
        1: (1.53869, 1.96369),
        3: (2.82066, 3.24566),
        4: (3.28989, 3.71489),
    },
    "bi2te3": {
        1: (1.44167, 1.86667),
        3: (2.65261, 3.07761),
        4: (3.09584, 3.52084),
    },
}
OFFSPECULAR_FAMILIES = (1, 3, 4)
OFFSPECULAR_L_EDGES = np.arange(2.0, 17.0001, 0.2, dtype=np.float64)
OFFSPECULAR_GAUSS_ORDER = 6
OFFSPECULAR_SUBDIVISIONS = (6, 3)
OFFSPECULAR_BRANCHES = ("plus", "minus")
ANGLE_REFERENCE_ORDER = 4
ANGLE_FINAL_ORDER = 8


def load_runner():
    spec = importlib.util.spec_from_file_location("bi2x3_current_continuous_render", RUNNER)
    if spec is None or spec.loader is None:
        raise ImportError(RUNNER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_prior_display_scales() -> tuple[dict[str, float], str, str]:
    document = json.loads(PRIOR_SCALE_MANIFEST.read_text(encoding="utf-8"))
    if document.get("schema") != "bi2x3-requested-continuous-region-quicklook.v1":
        raise ValueError("unexpected prior display-scale manifest schema")
    scales = {
        str(record["material"]): float(record["scale_count_per_A2"])
        for record in document["records"]
    }
    if set(scales) != set(LABELS) or any(
        not np.isfinite(value) or value < 0.0 for value in scales.values()
    ):
        raise ValueError("prior display-scale manifest is incomplete or invalid")
    return (
        scales,
        sha256_file(PRIOR_SCALE_MANIFEST),
        str(document["source_artifact_sha256"]),
    )


def family_detector(detector, family_m: int):
    rods = tuple(rod for rod in detector.rods if int(rod.family_m) == family_m)
    if not rods:
        raise ValueError(f"detector has no m={family_m} rods")
    return detector.restrict_rods(rods)


def rod_fold_center(inputs, reciprocal_frame, radial_interval, family_m: int) -> float:
    lower, upper = radial_interval
    radii = []
    for rod in inputs.rods:
        if int(rod.family_m) != family_m:
            continue
        q_crystal = inputs.reciprocal.basis_Ainv @ np.asarray(
            (float(rod.h), float(rod.k), 0.0), dtype=np.float64
        )
        q_sample = inputs.instrument.sample_from_crystal.rotation @ q_crystal
        radius, _ = reciprocal_frame.coordinates(q_sample[None, :])
        if lower < float(radius[0]) < upper:
            radii.append(float(radius[0]))
    if not radii:
        raise ValueError(f"m={family_m} radial band contains no rod fold")
    center = float(np.mean(radii))
    if np.max(np.abs(np.asarray(radii) - center)) > 2.0e-12 * max(1.0, abs(center)):
        raise ValueError(f"m={family_m} radial band contains more than one fold radius")
    return center


def compile_offspecular_branch_quadrature(
    material: str,
    record: dict,
    inputs,
    detector_column_count: int,
    family_m: int,
    branch: str,
):
    if family_m not in OFFSPECULAR_FAMILIES:
        raise ValueError(f"unsupported off-specular family: m={family_m}")
    if branch not in OFFSPECULAR_BRANCHES:
        raise ValueError(f"unknown off-specular branch: {branch}")
    reciprocal_frame = LayeredReciprocalFrame(
        reciprocal_basis_Ainv=inputs.reciprocal.basis_Ainv,
        sample_from_crystal_rotation=inputs.instrument.sample_from_crystal.rotation,
        axial_basis_index=2,
    )
    nominal = build_nominal_ewald_context(inputs)
    beam_center_column_px = float(record["position"]["beam_center_column_row_px"][0])
    detector_column_interval_px = (
        (-0.5, beam_center_column_px)
        if branch == "plus"
        else (beam_center_column_px, float(detector_column_count) - 0.5)
    )
    chart = LayeredReciprocalDetectorAreaChart(
        detector_measure=nominal.geometry,
        reciprocal_frame=reciprocal_frame,
        detector_column_interval_px=detector_column_interval_px,
        air_exit_guard_rad=0.0,
    )
    radial_interval = FAMILY_RADIAL_INTERVAL_AINV[material][family_m]
    bin_count = OFFSPECULAR_L_EDGES.size - 1
    return compile_continuous_rectangle_quadrature(
        chart=chart,
        first_coordinate_bounds=np.tile(radial_interval, (bin_count, 1)),
        second_coordinate_bounds=np.column_stack(
            (OFFSPECULAR_L_EDGES[:-1], OFFSPECULAR_L_EDGES[1:])
        ),
        observation_row=np.arange(bin_count, dtype=np.int64),
        observation_count=bin_count,
        gauss_order=OFFSPECULAR_GAUSS_ORDER,
        background_coordinate_axis=0,
        subdivision_count=OFFSPECULAR_SUBDIVISIONS,
        first_coordinate_squared_fold_center=np.full(
            bin_count,
            rod_fold_center(inputs, reciprocal_frame, radial_interval, family_m),
            dtype=np.float64,
        ),
    )


def offspecular_branch_profile(
    runner,
    material: str,
    record: dict,
    inputs,
    detector,
    decoded: dict,
    family_m: int,
    branch: str,
    scale_count_per_A2: float,
) -> dict:
    quadrature = compile_offspecular_branch_quadrature(
        material,
        record,
        inputs,
        decoded["detector_native_counts"].shape[1],
        family_m,
        branch,
    )
    bin_count = OFFSPECULAR_L_EDGES.size - 1
    projection = compile_native_pixel_region_projection(
        quadrature, decoded["detector_native_counts"].shape
    )
    support = np.asarray(projection.observation_measure_px2, dtype=np.float64)
    raw_mass, _ = projection.integrate_counts(decoded["detector_native_counts"])
    radial_mass, _ = projection.integrate_field(
        decoded["radial_background_count_per_px"],
        np.zeros(decoded["radial_background_count_per_px"].shape, dtype=np.float64),
    )
    measured = np.divide(
        raw_mass,
        support,
        out=np.full(bin_count, np.nan),
        where=support > 0.0,
    ) - float(decoded["dark_background_counts"])
    background = np.divide(
        radial_mass,
        support,
        out=np.full(bin_count, np.nan),
        where=support > 0.0,
    )

    pixel = np.asarray(projection.flat_pixel_index, dtype=np.int64)[
        np.asarray(projection.pixel_column_index, dtype=np.int64)
    ]
    invalid_overlap = np.bincount(
        np.asarray(projection.observation_row, dtype=np.int64),
        weights=(~np.asarray(decoded["detector_valid_mask"], dtype=bool).ravel()[pixel]).astype(
            np.float64
        ),
        minlength=bin_count,
    )
    exact_data_support = invalid_overlap == 0.0

    evaluated = runner._evaluate_angle_density(
        family_detector(detector, family_m),
        np.asarray(quadrature.column_px, dtype=np.float64),
        np.asarray(quadrature.row_px, dtype=np.float64),
        execution_backend="cuda",
    )
    owner = np.asarray(quadrature.observation_row, dtype=np.int64)
    weight = np.asarray(quadrature.detector_area_weight_px2, dtype=np.float64)
    diffraction_mass = np.bincount(
        owner,
        weights=weight * np.asarray(evaluated["density_A2_per_px2"], dtype=np.float64),
        minlength=bin_count,
    )
    diffraction = np.divide(
        diffraction_mass,
        support,
        out=np.full(bin_count, np.nan),
        where=support > 0.0,
    )
    valid = (
        np.asarray(quadrature.observation_covered, dtype=bool)
        & exact_data_support
        & (support > 0.0)
        & np.isfinite(measured)
        & np.isfinite(background)
        & np.isfinite(diffraction)
    )
    scale = float(scale_count_per_A2)
    if not np.isfinite(scale) or scale < 0.0:
        raise ValueError("scale_count_per_A2 must be finite and nonnegative")
    model = scale * diffraction + background
    return {
        "family_m": family_m,
        "branch": branch,
        "L": 0.5 * (OFFSPECULAR_L_EDGES[:-1] + OFFSPECULAR_L_EDGES[1:]),
        "measured_count_per_px": measured,
        "background_count_per_px": background,
        "diffraction_A2_per_px2": diffraction,
        "model_total_count_per_px": model,
        "valid": valid,
        "scale_count_per_A2": scale,
        "quadrature_coordinate_count": int(quadrature.column_px.size),
        "quadrature_revision": quadrature.quadrature_revision,
        "execution": evaluated["execution"],
    }


def direct_angle_fields(direct: dict, shape: tuple[int, int]) -> tuple[np.ndarray, ...]:
    signal_map = np.full(shape, np.nan, dtype=np.float64)
    normalization_map = np.full(shape, np.nan, dtype=np.float64)
    valid_map = np.zeros(shape, dtype=bool)
    signal = np.asarray(direct["diffraction_signal_A2"], dtype=np.float64)
    normalization = np.asarray(direct["direct_normalization_px2"], dtype=np.float64)
    valid = np.asarray(direct["valid"], dtype=bool) & (normalization > 0.0)
    bins = np.asarray(direct["angle_bin_index"], dtype=np.int64)
    signal_map.ravel()[bins] = signal
    normalization_map.ravel()[bins] = normalization
    valid_map.ravel()[bins] = valid
    return signal_map, normalization_map, valid_map


def m0_line_profile(
    runner,
    detector,
    angle_frame,
    decoded: dict,
    inputs,
    scale: float,
) -> tuple[dict, dict]:
    measured, projector = runner._measured_angle_maps(detector, angle_frame, decoded)
    selected_bins = np.asarray(projector["exact_full_angle_bin_index"], dtype=np.int64)
    reference = runner._integrate_continuous_angle_bins(
        family_detector(detector, 0),
        angle_frame,
        decoded,
        ANGLE_REFERENCE_ORDER,
        execution_backend="cuda",
        angle_bin_index=selected_bins,
    )
    final = runner._integrate_continuous_angle_bins(
        family_detector(detector, 0),
        angle_frame,
        decoded,
        ANGLE_FINAL_ORDER,
        execution_backend="cuda",
        angle_bin_index=selected_bins,
    )
    shape = np.asarray(measured["valid"], dtype=bool).shape
    reference_signal, reference_normalization, reference_valid = direct_angle_fields(
        reference, shape
    )
    diffraction_signal, diffraction_normalization, diffraction_valid = direct_angle_fields(
        final, shape
    )
    valid = (
        np.asarray(measured["valid"], dtype=bool)
        & reference_valid
        & diffraction_valid
        & np.isfinite(reference_signal)
        & np.isfinite(diffraction_signal)
    )
    reference_density = reference_signal[valid] / reference_normalization[valid]
    diffraction_density = diffraction_signal[valid] / diffraction_normalization[valid]
    relative_l2 = float(
        np.linalg.norm(diffraction_density - reference_density)
        / max(np.linalg.norm(reference_density), np.finfo(np.float64).tiny)
    )
    measured_signal = np.asarray(measured["measured_signal_count"], dtype=np.float64)
    measured_normalization = np.asarray(measured["measured_normalization_px2"], dtype=np.float64)
    background_signal = np.asarray(
        measured["measured_radial_background_signal_count"], dtype=np.float64
    )
    background_normalization = np.asarray(
        measured["measured_radial_background_normalization_px2"], dtype=np.float64
    )

    def masked(values: np.ndarray) -> np.ndarray:
        return np.where(valid, values, 0.0)

    measured_denominator = np.sum(masked(measured_normalization), axis=1)
    diffraction_denominator = np.sum(masked(diffraction_normalization), axis=1)
    background_denominator = np.sum(masked(background_normalization), axis=1)
    valid_theta = (
        (measured_denominator > 0.0)
        & (diffraction_denominator > 0.0)
        & (background_denominator > 0.0)
        & np.any(valid, axis=1)
    )
    measured_line = np.divide(
        np.sum(masked(measured_signal), axis=1),
        measured_denominator,
        out=np.full(shape[0], np.nan),
        where=valid_theta,
    )
    diffraction_line = np.divide(
        np.sum(masked(diffraction_signal), axis=1),
        diffraction_denominator,
        out=np.full(shape[0], np.nan),
        where=valid_theta,
    )
    background_line = np.divide(
        np.sum(masked(background_signal), axis=1),
        background_denominator,
        out=np.full(shape[0], np.nan),
        where=valid_theta,
    )
    model_line = scale * diffraction_line + background_line
    theta_edges = np.asarray(projector["theta_edges_deg"], dtype=np.float64)
    theta_centers_deg = 0.5 * (theta_edges[:-1] + theta_edges[1:])
    qz_Ainv = (
        4.0
        * np.pi
        / float(inputs.config.source.mean_wavelength_A)
        * np.sin(0.5 * np.deg2rad(theta_centers_deg))
    )
    axial_basis_magnitude_Ainv = float(
        np.linalg.norm(np.asarray(inputs.reciprocal.basis_Ainv, dtype=np.float64)[:, 2])
    )
    return {
        "L": qz_Ainv / axial_basis_magnitude_Ainv,
        "measured_count_per_px": measured_line,
        "background_count_per_px": background_line,
        "diffraction_A2_per_px2": diffraction_line,
        "model_total_count_per_px": model_line,
        "valid": valid_theta & np.isfinite(measured_line) & np.isfinite(model_line),
        "scale_count_per_A2": scale,
    }, {
        "angle_reference_order": ANGLE_REFERENCE_ORDER,
        "angle_final_order": ANGLE_FINAL_ORDER,
        "angle_quadrature_relative_l2": relative_l2,
        "valid_angle_bin_count": int(np.count_nonzero(valid)),
        "valid_theta_bin_count": int(np.count_nonzero(valid_theta)),
        "phi_collapse": "sum signal mass over common-valid phi bins, then divide by summed measure",
        "reference_wall_seconds": float(reference["wall_seconds"]),
        "final_wall_seconds": float(final["wall_seconds"]),
        "execution": final["execution"],
    }


def render_profile_grid(
    material: str,
    profiles: dict[int, dict[str, dict]],
    m0_profile: dict,
    stage_name: str,
    source_count: int,
) -> Path:
    destination = OUTPUT / f"{material}_profile_grid_continuous_log.png"
    figure = plt.figure(figsize=(10.8, 9.0), layout="constrained")
    outer = figure.add_gridspec(2, 1, height_ratios=(3.0, 1.15), hspace=0.18)
    upper = outer[0].subgridspec(3, 2, hspace=0.0, wspace=0.0)
    axes = np.asarray(
        [[figure.add_subplot(upper[row, column]) for column in range(2)] for row in range(3)]
    )
    m0_axis = figure.add_subplot(outer[1])
    offspecular_values = []
    for family_m in OFFSPECULAR_FAMILIES:
        for branch in OFFSPECULAR_BRANCHES:
            profile = profiles[family_m][branch]
            valid = np.asarray(profile["valid"], dtype=bool)
            offspecular_values.extend(
                np.asarray(profile["measured_count_per_px"], dtype=np.float64)[valid]
            )
            offspecular_values.extend(
                np.asarray(profile["model_total_count_per_px"], dtype=np.float64)[valid]
            )
    value_array = np.asarray(offspecular_values, dtype=np.float64)
    positive = value_array[np.isfinite(value_array) & (value_array > 0.0)]
    if not positive.size:
        raise ValueError("off-specular log view has no positive intensity")
    log_span = max(float(np.log10(np.max(positive) / np.min(positive))), 1.0)
    y_min = float(np.min(positive) / 10.0 ** (0.04 * log_span))
    y_max = float(np.max(positive) * 10.0 ** (0.06 * log_span))
    for row, family_m in enumerate(OFFSPECULAR_FAMILIES):
        for column, branch in enumerate(("minus", "plus")):
            axis = axes[row, column]
            profile = profiles[family_m][branch]
            valid = np.asarray(profile["valid"], dtype=bool)
            L = np.asarray(profile["L"], dtype=np.float64)
            measured = np.where(
                valid & (np.asarray(profile["measured_count_per_px"]) > 0.0),
                np.asarray(profile["measured_count_per_px"], dtype=np.float64),
                np.nan,
            )
            model = np.where(
                valid & (np.asarray(profile["model_total_count_per_px"]) > 0.0),
                np.asarray(profile["model_total_count_per_px"], dtype=np.float64),
                np.nan,
            )
            axis.plot(L, measured, color="#222222", lw=1.0, label="Data")
            axis.plot(
                L,
                model,
                color="#D55E00",
                lw=1.25,
                ls="--",
                label="Simulation",
            )
            axis.set(xlim=(2.0, 17.0), ylim=(y_min, y_max))
            axis.set_yscale("log")
            axis.grid(which="both", color="#AAB2B9", alpha=0.27, lw=0.5)
            axis.text(
                0.5,
                0.965,
                rf"$m={family_m}{'+' if branch == 'plus' else '-'}$",
                transform=axis.transAxes,
                ha="center",
                va="top",
                fontsize=9,
            )
            if row < 2:
                axis.tick_params(labelbottom=False)
            else:
                axis.set_xlabel(r"$L$")
            if column == 1:
                axis.tick_params(labelleft=False)
            if row == 0 and column == 1:
                axis.legend(frameon=False, loc="upper right", fontsize=8)
    axes[1, 0].set_ylabel(r"Intensity (count / px$^2$)")
    m0_valid = np.asarray(m0_profile["valid"], dtype=bool)
    m0_L = np.asarray(m0_profile["L"], dtype=np.float64)
    m0_measured = np.asarray(m0_profile["measured_count_per_px"], dtype=np.float64)
    m0_model = np.asarray(m0_profile["model_total_count_per_px"], dtype=np.float64)
    m0_axis.plot(
        m0_L,
        np.where(m0_valid & (m0_measured > 0.0), m0_measured, np.nan),
        color="#222222",
        lw=1.0,
        label="Data",
    )
    m0_axis.plot(
        m0_L,
        np.where(m0_valid & (m0_model > 0.0), m0_model, np.nan),
        color="#D55E00",
        lw=1.25,
        ls="--",
        label="Simulation",
    )
    m0_axis.set(
        xlim=(0.0, 8.0),
        xlabel=r"$L$",
        ylabel=r"Intensity (count / px$^2$)",
    )
    m0_axis.set_yscale("log")
    m0_axis.grid(which="both", color="#AAB2B9", alpha=0.27, lw=0.5)
    m0_axis.text(
        0.5,
        0.965,
        r"$m=0$",
        transform=m0_axis.transAxes,
        ha="center",
        va="top",
        fontsize=9,
    )
    figure.suptitle(
        f"{LABELS[material]} | fixed 5° | continuous projected profiles | log scale\n"
        f"Archived v1 {stage_name}; N={source_count}; one m=1+ scale reused throughout; SF not run",
        fontsize=11.5,
    )
    figure.savefig(destination, dpi=220, facecolor="white")
    plt.close(figure)
    return destination


def main() -> None:
    runner = load_runner()
    (
        prior_display_scales,
        prior_scale_manifest_sha256,
        prior_scale_artifact_sha256,
    ) = load_prior_display_scales()
    refit, fit_profiles, _, _ = runner._legacy_modules(load_resume=False)
    refit.build_detectors = runner.build_detectors
    archive, artifact_sha256 = runner._load_archive_bound(refit, runner.ARTIFACT)
    if prior_scale_artifact_sha256 != artifact_sha256:
        raise ValueError("prior display scales were established from a different fit artifact")
    records = []
    for material in ("bi2se3", "bi2te3"):
        stage_name = STAGES[material]
        film = archive["films"][material]
        record = dict(film["prepared"])
        record["input_provenance"] = runner._record_input_provenance(record)
        stage = film[stage_name]
        source_count = int(stage["source_count"])
        detectors, series = runner.build_detectors(
            record,
            source_count,
            runner._mosaic_parameters_from_stage(stage),
        )
        image_id = "fixed_5deg"
        detector = detectors[0]
        inputs = series.inputs[0]
        angle_frame = fit_profiles.nominal_frame(
            inputs, f"bi2x3-signed-polar-line-angle.v1:{image_id}"
        )
        decoded = runner._load_decoded_fields(
            record,
            image_id,
            record["input_provenance"]["files"][f"decoded/{image_id}.npz"]["sha256"],
        )
        compiled_detector, authority = runner._build_exact_compiled_angle_detector(inputs, detector)
        scale = prior_display_scales[material]
        plus_profile = offspecular_branch_profile(
            runner,
            material,
            record,
            inputs,
            compiled_detector,
            decoded,
            1,
            "plus",
            scale,
        )
        profiles = {family_m: {} for family_m in OFFSPECULAR_FAMILIES}
        profiles[1]["plus"] = plus_profile
        profiles[1]["minus"] = offspecular_branch_profile(
            runner,
            material,
            record,
            inputs,
            compiled_detector,
            decoded,
            1,
            "minus",
            scale,
        )
        for family_m in (3, 4):
            for branch in OFFSPECULAR_BRANCHES:
                profiles[family_m][branch] = offspecular_branch_profile(
                    runner,
                    material,
                    record,
                    inputs,
                    compiled_detector,
                    decoded,
                    family_m,
                    branch,
                    scale,
                )
        m0_profile, angle_metrics = m0_line_profile(
            runner,
            compiled_detector,
            angle_frame,
            decoded,
            inputs,
            scale,
        )
        profile_grid_path = render_profile_grid(
            material, profiles, m0_profile, stage_name, source_count
        )
        family_evidence = {}
        for family_m, family_profiles in profiles.items():
            branch_evidence = {}
            for branch, profile in family_profiles.items():
                valid_profile = np.asarray(profile["valid"], dtype=bool)
                branch_evidence[branch] = {
                    "coordinate_count": profile["quadrature_coordinate_count"],
                    "quadrature_revision": profile["quadrature_revision"],
                    "valid_bin_count": int(np.count_nonzero(valid_profile)),
                    "L_supported_range": [
                        float(np.nanmin(np.asarray(profile["L"])[valid_profile])),
                        float(np.nanmax(np.asarray(profile["L"])[valid_profile])),
                    ],
                    "execution": profile["execution"],
                }
            family_evidence[str(family_m)] = {
                "radial_interval_Ainv": list(FAMILY_RADIAL_INTERVAL_AINV[material][family_m]),
                "branches": branch_evidence,
            }
        records.append(
            {
                "material": material,
                "image_id": image_id,
                "mosaic_stage": stage_name,
                "mosaic_parameters_deg": stage["fitted_mosaic_deg"],
                "source_count": source_count,
                "structure_model": "pure CIF baseline; no current SF stage",
                "display_scale_policy": "previously established nonnegative m=1+ scale loaded from the v1 continuous-region preview; reused unchanged for m=1+/-, m=3+/-, m=4+/-, and m=0",
                "display_scale_source": {
                    "path": str(PRIOR_SCALE_MANIFEST),
                    "sha256": prior_scale_manifest_sha256,
                },
                "view_normalization": "logarithmic; one common off-specular y scale across all six panels; independent logarithmic m=0 y scale; nonpositive conditioned values are explicitly omitted; no family normalization",
                "scale_count_per_A2": scale,
                "offspecular_region_integration": {
                    "method": "continuous reciprocal-chart Gauss-Legendre quadrature with squared fold coordinate",
                    "gauss_order": OFFSPECULAR_GAUSS_ORDER,
                    "subdivisions": list(OFFSPECULAR_SUBDIVISIONS),
                    "L_edges": [
                        float(OFFSPECULAR_L_EDGES[0]),
                        float(OFFSPECULAR_L_EDGES[-1]),
                        float(OFFSPECULAR_L_EDGES[1] - OFFSPECULAR_L_EDGES[0]),
                    ],
                    "families": family_evidence,
                },
                "m0_region_integration": {
                    "method": "direct continuous two-theta/phi Gauss-Legendre bin integration collapsed over common-valid phi by conserved signal mass",
                    "two_theta_range_deg": [1.0, 30.0],
                    "phi_range_deg": [-10.0, 10.0],
                    "qualification": "provisional display; q4-to-q8 difference reported but no stable-bin convergence gate applied",
                    **angle_metrics,
                },
                "background_included": True,
                "continuous_scans_used": False,
                "model_pixelized": False,
                "region_sampling_method": "deterministic quadrature; no Monte Carlo or detector-pixel-center model sampling",
                "status": "PROVISIONAL_CURRENT_CODE_FORWARD_PROJECTION_ARCHIVED_V1_MOSAIC; SF_NOT_RUN",
                "model_evaluation_authority": authority,
                "outputs": {
                    "profile_grid_png": {
                        "path": str(profile_grid_path),
                        "sha256": sha256_file(profile_grid_path),
                    },
                },
            }
        )
        print(f"{material} complete", flush=True)
    manifest = {
        "schema": "bi2x3-requested-continuous-region-log-view.v4",
        "source_artifact": str(runner.ARTIFACT),
        "source_artifact_sha256": artifact_sha256,
        "records": records,
    }
    manifest_path = OUTPUT / "continuous_region_log_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(manifest_path, flush=True)


if __name__ == "__main__":
    main()
