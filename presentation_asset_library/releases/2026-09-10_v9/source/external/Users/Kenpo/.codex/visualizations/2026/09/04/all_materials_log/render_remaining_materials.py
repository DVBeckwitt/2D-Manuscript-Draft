"""Render the four remaining PbI2 comparison pages from frozen fit states.

Every profile is an exact native-data projection paired with deterministic
continuous chart quadrature of the corresponding frozen detector function.
No continuous-incidence acquisition or detector-pixel-center model sampling is
used.  The two mixed-polytype specimens are plotted against qz rather than a
phase-specific L coordinate.
"""

# ruff: noqa: E402, I001

from __future__ import annotations

import gc
import hashlib
import importlib.util
import json
import math
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from collections.abc import Callable
from dataclasses import dataclass, replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any

PROJECT_ROOT = Path(r"C:\Users\Kenpo\Nextcloud\Git Projects\SLATE-rMC")
GENERIC_ENGINE = Path(
    r"C:\Users\Kenpo\Nextcloud\Git Projects\SLATE-rMC-generic-diffraction-project-pipeline"
)
PBI2_ENGINE = Path(
    r"C:\Users\Kenpo\Nextcloud\Git Projects\SLATE-rMC-pbi2-b4-parent-specific-6h"
)
REQUESTED_MODE = sys.argv[1] if len(sys.argv) > 1 else "gd_sid"
RERENDER_ONLY = REQUESTED_MODE.startswith("rerender_")
RUN_MODE = REQUESTED_MODE.removeprefix("rerender_")
ENGINE = PBI2_ENGINE if RUN_MODE in {"clean1", "b4"} else GENERIC_ENGINE
sys.path[:0] = [str(ENGINE / "src"), str(PROJECT_ROOT)]
sys.dont_write_bytecode = True

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LogNorm, to_rgba
from matplotlib.patches import Patch
from PIL import Image, ImageDraw, ImageFont

from painted_ewald.bragg import BraggSpaceConfig, MosaicBraggSpace
from painted_ewald.surface import ContinuousEwaldCoating
from rasim_next.core.validity import ValidityCode
from rasim_next.geometry import angles_to_detector_coordinate_area_measure
from rasim_next.measurement import (
    ContinuousDetectorChartAreaMeasure,
    LayeredReciprocalFrame,
    compile_continuous_rectangle_quadrature,
    compile_detector_profile_projector,
    compile_native_pixel_region_projection,
    project_detector_profiles,
)
from rasim_next.pipeline.configured_simulation import build_geometry_only_ewald_context
from rasim_next.pipeline.continuous_detector import (
    DetectorEwaldMeasure,
    _solve_exit_mode_arrays,
    evaluate_detector_coordinates_geometry,
)
from rasim_next.pipeline.reciprocal_detector_chart import (
    LayeredReciprocalDetectorAreaChart,
)
from rasim_next.selection import detector_valid_mask_from_counts

HERE = Path(__file__).resolve().parent
OUTPUT = Path(r"C:\Users\Kenpo\Downloads\2D_Manuscript\figures\all_materials_current_continuous")
LIBRARY = Path(r"C:\Users\Kenpo\Nextcloud\Obsidian\Research\Rigaku XRD\SLATE Fit Library")
VIS_0831 = Path(
    r"C:\Users\Kenpo\.codex\visualizations\2026\08\31"
    r"\01a0595c-cb0b-7f63-84de-6d89e1c62878"
)
GD_EXECUTOR = (
    LIBRARY
    / "runs"
    / "pbi2-gd1-sid1-2026-08-26-sf-full-reciprocal"
    / "artifacts"
    / "executors"
    / "fit_structure_full_qz.py"
)
CLEAN1_ANGLE = VIS_0831 / "pbi2_clean1_m0_angle" / "compare_m0_angle.py"
CLEAN1_WIDE = VIS_0831 / "pbi2_clean1_wide_angle" / "clean1_wide_angle.ra_diag.npz"
B4_ROOT = LIBRARY / "runs" / "pbi2-b4-joint-mosaic-sf-2026-09-02-detector-background"
B4_CORE = B4_ROOT / "artifacts" / "final" / "pbi2_b4_joint_core_authority.py"
B4_RESPONSE = B4_ROOT / "artifacts" / "final" / "pbi2_b4_joint_response_executor.py"
B4_MOSAIC = B4_ROOT / "artifacts" / "final" / "pbi2_b4_joint_mosaic_authority.py"
B4_FIT = (
    B4_ROOT / "artifacts" / "final" / "pbi2_b4_joint_shared_intensity_sobol1024_7dd201c47e33.json"
)
B4_M0 = (
    B4_ROOT
    / "artifacts"
    / "final"
    / "pbi2_b4_m0_joint_continuous_angle_sobol1024_6d472310d160.ra_diag.npz"
)
B4_BACKGROUND = B4_ROOT / "artifacts" / "detector" / "pbi2_b4_detector_background.ra_diag.npz"
CLEAN1_FIT = VIS_0831 / "pbi2_clean1_joint_refit" / "result.json"
CLEAN1_JOINT = VIS_0831 / "pbi2_clean1_joint_refit" / "clean1_joint.ra_diag.npz"
CLEAN1_WIDE_MANIFEST = VIS_0831 / "pbi2_clean1_wide_angle" / "manifest.json"

FAMILIES = (1, 3, 4)
BRANCHES = ("plus", "minus")
FAMILY_COLORS = {1: "#CC79A7", 3: "#E69F00", 4: "#009E73"}
QZ_EDGES_AINV = np.linspace(0.0, 4.5, 91, dtype=np.float64)
OFFSPECULAR_GAUSS_ORDER = 4
OFFSPECULAR_SUBDIVISIONS = (2, 1)
ANGLE_GAUSS_ORDER = 2


@dataclass(frozen=True)
class MaterialCase:
    key: str
    label_plain: str
    label_math: str
    archetype: str
    image_id: str
    image_label: str
    incidence_deg: float
    detector: Any
    inputs: Any
    raw_count_per_px: np.ndarray
    measured_count_per_px: np.ndarray
    detector_valid_mask: np.ndarray
    background_count_per_px: float | np.ndarray
    scale_count_per_A2: float
    source_count: int
    model_status: str
    background_note: str
    density_evaluator: Callable[[int, np.ndarray, np.ndarray], tuple[np.ndarray, dict[str, Any]]]
    m0_profile: dict[str, np.ndarray] | None = None


@dataclass(frozen=True)
class AngleDetectorAreaChart:
    instrument: Any
    angle_frame: Any
    revision: str

    def map_detector_area(
        self, first_coordinate: np.ndarray, second_coordinate: np.ndarray
    ) -> ContinuousDetectorChartAreaMeasure:
        mapped = angles_to_detector_coordinate_area_measure(
            first_coordinate,
            second_coordinate,
            instrument=self.instrument,
            angle_frame=self.angle_frame,
        )
        return ContinuousDetectorChartAreaMeasure(
            column_px=mapped.coordinates.column_px,
            row_px=mapped.coordinates.row_px,
            detector_area_jacobian_px2_per_chart2=(mapped.detector_area_jacobian_px2_per_rad2),
            valid=mapped.coordinates.valid,
        )


def load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def loaded_module(name: str, path: Path) -> Any:
    if name in sys.modules:
        return sys.modules[name]
    return load_module(name, path)


def clean1_family_chunk_worker(
    image_id: str,
    incidence_deg: float,
    chunk_index: int,
    column_px: np.ndarray,
    row_px: np.ndarray,
    selected: dict[str, Any],
    family_m: int,
) -> tuple[int, np.ndarray, dict[str, Any]]:
    """Evaluate one normalized Clean1 source chunk for one rod family."""

    angle = loaded_module("all_materials_clean1_angle", CLEAN1_ANGLE)
    runner = angle.clean1.runner
    original_builder = runner.build_source_averaged_structure_detector

    def restricted_builder(*args: Any, **kwargs: Any) -> Any:
        detector = original_builder(*args, **kwargs)
        return family_detector(detector, family_m)

    runner.build_source_averaged_structure_detector = restricted_builder
    try:
        chunk, density_mass, _, audit = angle.source_chunk_density(
            image_id,
            incidence_deg,
            chunk_index,
            column_px,
            row_px,
            selected,
            batch_size=128 if family_m == 4 else 4096,
        )
    finally:
        runner.build_source_averaged_structure_detector = original_builder
    return int(chunk), np.asarray(density_mass, dtype=np.float64), audit


def b4_family_chunk_worker(
    chunk_index: int,
    detector: Any,
    probability: float,
    column_px: np.ndarray,
    row_px: np.ndarray,
    crystal: Any,
    family_m: int,
    parameters: dict[str, Any],
) -> tuple[int, float, np.ndarray, dict[str, Any]]:
    """Evaluate one B4 source chunk with the frozen 2H/6H structure state."""

    core = loaded_module("pbi2_b4_single_peak_refit", B4_CORE)
    if "tmp_b4_mosaic_fit" not in sys.modules:
        core.load_module("tmp_b4_mosaic_fit", B4_MOSAIC)
    response = loaded_module("all_materials_b4_response", B4_RESPONSE)
    columns = np.asarray(column_px, dtype=np.float64).ravel()
    rows = np.asarray(row_px, dtype=np.float64).ravel()
    fractions = np.asarray(parameters["phase_fractions"], dtype=np.float64)
    density = np.zeros(columns.shape, dtype=np.float64)
    batch_size = 32768 if family_m == 0 else max(columns.size, 1)
    audits = []
    chunk_probability = float(probability)
    for start in range(0, columns.size, batch_size):
        stop = min(start + batch_size, columns.size)
        observation = SimpleNamespace(
            column_px=columns[start:stop],
            row_px=rows[start:stop],
        )
        result = response._sf_chunk(
            chunk_index,
            detector,
            probability,
            observation,
            crystal,
            response._mosaic(tuple(parameters["mosaic"])),
            np.asarray([parameters["z_iodine_fractional_layer"]], dtype=np.float64),
            np.asarray([parameters["epsilon_2h"]], dtype=np.float64),
            np.asarray([parameters["epsilon_6h"]], dtype=np.float64),
            float(parameters["u_radial_A2"]),
            float(parameters["u_normal_A2"]),
        )
        _, returned_probability, two, six_plus, six_minus, audit = result
        if float(returned_probability) != chunk_probability:
            raise ValueError("B4 source-chunk probability changed across coordinate batches")
        density[start:stop] = (
            fractions[0] * np.asarray(two[0, 0], dtype=np.float64)
            + fractions[1] * np.asarray(six_plus[0, 0], dtype=np.float64)
            + fractions[2] * np.asarray(six_minus[0, 0], dtype=np.float64)
        )
        audits.append(audit)
    combined_audit = {
        "family_m": int(family_m),
        "batch_count": len(audits),
        "term_count": int(sum(item["term_count"] for item in audits)),
        "response_revisions": [item["response_revision"] for item in audits],
        "wall_seconds": float(sum(item["wall_seconds"] for item in audits)),
    }
    return int(chunk_index), chunk_probability, density, combined_audit


def b4_canonical_roundtrip_support(
    detectors: tuple[Any, ...],
    column_px: np.ndarray,
    row_px: np.ndarray,
) -> np.ndarray:
    """Identify coordinates accepted by every frozen B4 source state's exit check."""

    columns = np.asarray(column_px, dtype=np.float64).ravel()
    rows = np.asarray(row_px, dtype=np.float64).ravel()
    supported = np.ones(columns.shape, dtype=bool)
    for detector in detectors:
        states = detector.incident.states
        for state_index in np.flatnonzero(states.valid):
            active = np.flatnonzero(supported)
            if active.size == 0:
                return supported
            geometry = evaluate_detector_coordinates_geometry(
                columns[active],
                rows[active],
                incident=detector.incident,
                instrument=detector.instrument,
                ki_sample_Ainv=states.k_film_phase_sample_Ainv[state_index],
                include_surface_jacobian=True,
                incident_state_index=int(state_index),
            )
            reachable_rows = np.flatnonzero(np.asarray(geometry.valid).reshape(-1))
            if reachable_rows.size == 0:
                continue
            wavelengths = np.full(
                reachable_rows.size,
                states.wavelength_A[state_index],
                dtype=np.float64,
            )
            modes = _solve_exit_mode_arrays(
                geometry.kf_film_sample_Ainv.reshape(-1, 3)[reachable_rows],
                wavelengths,
                detector.material,
            )
            mode_valid = modes.status == ValidityCode.VALID
            valid_rows = reachable_rows[mode_valid]
            if valid_rows.size == 0:
                continue
            delta = (
                modes.k_air_phase_sample_Ainv[mode_valid]
                - geometry.kf_air_sample_Ainv.reshape(-1, 3)[valid_rows]
            )
            tolerance = (
                512.0
                * np.finfo(np.float64).eps
                * max(2.0 * np.pi / float(states.wavelength_A[state_index]), 1.0)
            )
            failed = (~np.all(np.isfinite(delta), axis=1)) | np.any(
                np.abs(delta) > tolerance, axis=1
            )
            supported[active[valid_rows[failed]]] = False
    return supported


if RUN_MODE == "b4":
    # Source-chunk detector objects pickle this module name. Preload the captured
    # authority under that exact name in both the parent and spawned workers.
    loaded_module("tmp_b4_mosaic_fit", B4_MOSAIC)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def file_record(path: Path) -> dict[str, str]:
    return {"path": str(path), "sha256": sha256_file(path)}


def family_detector(detector: Any, family_m: int) -> Any:
    rods = tuple(rod for rod in detector.rods if int(rod.family_m) == family_m)
    if not rods:
        raise ValueError(f"detector has no m={family_m} rods")
    return detector.restrict_rods(rods)


def nominal_detector_measure(case: MaterialCase) -> DetectorEwaldMeasure:
    context = build_geometry_only_ewald_context(
        case.inputs, instrument=case.detector.instrument
    )
    config = BraggSpaceConfig(
        reciprocal_basis_Ainv=case.detector.reciprocal_basis_Ainv,
        crystal_to_sample=case.detector.crystal_to_sample,
        rods=case.detector.rods,
        mosaic=case.detector.mosaic,
        k_norm_Ainv=2.0 * np.pi / float(context.incident.states.wavelength_A[0]),
    )
    coating = ContinuousEwaldCoating(
        MosaicBraggSpace(config, case.detector.strength_model),
        ki_sample_Ainv=context.ki_sample_Ainv,
    )
    return DetectorEwaldMeasure(
        coating=coating,
        incident=context.incident,
        material=context.material,
        instrument=context.instrument,
        rod_catalog_revision=case.detector.rod_catalog_revision,
    )


def structure_density(
    detector: Any,
    column_px: np.ndarray,
    row_px: np.ndarray,
    *,
    batch_size: int = 512,
) -> tuple[np.ndarray, dict[str, Any]]:
    columns = np.asarray(column_px, dtype=np.float64).ravel()
    rows = np.asarray(row_px, dtype=np.float64).ravel()
    if columns.shape != rows.shape:
        raise ValueError("detector coordinate arrays disagree")
    density = np.zeros(columns.size, dtype=np.float64)
    term_count = 0
    minimum_valid = np.iinfo(np.int64).max
    maximum_valid = 0
    for start in range(0, columns.size, batch_size):
        stop = min(start + batch_size, columns.size)
        response = detector.compile_structure_response(columns[start:stop], rows[start:stop])
        if np.any(response.per_rod_caustic):
            raise FloatingPointError("continuous quadrature encountered an exact caustic")
        evaluated = response.apply_strength(detector.strength_model)
        current = np.asarray(evaluated.density_A2_per_px2, dtype=np.float64)
        valid_source = np.asarray(evaluated.valid_source_count, dtype=np.int64)
        if (
            current.shape != (stop - start,)
            or np.any(~np.isfinite(current))
            or np.any(current < 0.0)
        ):
            raise FloatingPointError("invalid continuous detector density")
        density[start:stop] = current
        term_count += int(response.term_L.size)
        minimum_valid = min(minimum_valid, int(np.min(valid_source)))
        maximum_valid = max(maximum_valid, int(np.max(valid_source)))
    if columns.size == 0:
        minimum_valid = 0
    return density, {
        "coordinate_count": int(columns.size),
        "compiled_term_count": term_count,
        "minimum_valid_source_count": minimum_valid,
        "maximum_valid_source_count": maximum_valid,
        "backend": "cpu_sparse_structure_response",
    }


def family_fold_radius_Ainv(case: MaterialCase, family_m: int) -> float:
    frame = LayeredReciprocalFrame(
        reciprocal_basis_Ainv=case.inputs.reciprocal.basis_Ainv,
        sample_from_crystal_rotation=case.inputs.instrument.sample_from_crystal.rotation,
        axial_basis_index=2,
    )
    radii = []
    for rod in case.detector.rods:
        if int(rod.family_m) != family_m:
            continue
        q_crystal = case.inputs.reciprocal.basis_Ainv @ np.asarray(
            (float(rod.h), float(rod.k), 0.0), dtype=np.float64
        )
        q_sample = case.inputs.instrument.sample_from_crystal.rotation @ q_crystal
        radius, _ = frame.coordinates(q_sample[None, :])
        radii.append(float(radius[0]))
    if not radii:
        raise ValueError(f"m={family_m} has no fold radius")
    center = float(np.mean(radii))
    if np.max(np.abs(np.asarray(radii) - center)) > 2e-12 * max(1.0, abs(center)):
        raise ValueError(f"m={family_m} rods do not share one fold")
    return center


def family_radial_intervals(case: MaterialCase) -> dict[int, tuple[float, float]]:
    centers = {family: family_fold_radius_Ainv(case, family) for family in FAMILIES}
    intervals = {}
    for family, center in centers.items():
        nearest = min(abs(center - other) for key, other in centers.items() if key != family)
        half_width = min(0.2125, 0.45 * nearest)
        intervals[family] = (center - half_width, center + half_width)
    for left in FAMILIES:
        for right in FAMILIES:
            if left >= right:
                continue
            if intervals[left][1] >= intervals[right][0]:
                raise ValueError("family radial intervals overlap")
    return intervals


def compile_branch_quadrature(
    case: MaterialCase,
    family_m: int,
    branch: str,
    radial_interval_Ainv: tuple[float, float],
) -> Any:
    chart = branch_detector_chart(case, branch)
    cstar_Ainv = float(np.linalg.norm(case.inputs.reciprocal.basis_Ainv[:, 2]))
    l_edges = QZ_EDGES_AINV / cstar_Ainv
    bin_count = l_edges.size - 1
    return compile_continuous_rectangle_quadrature(
        chart=chart,
        first_coordinate_bounds=np.tile(radial_interval_Ainv, (bin_count, 1)),
        second_coordinate_bounds=np.column_stack((l_edges[:-1], l_edges[1:])),
        observation_row=np.arange(bin_count, dtype=np.int64),
        observation_count=bin_count,
        gauss_order=OFFSPECULAR_GAUSS_ORDER,
        background_coordinate_axis=0,
        subdivision_count=OFFSPECULAR_SUBDIVISIONS,
        first_coordinate_squared_fold_center=np.full(
            bin_count, family_fold_radius_Ainv(case, family_m), dtype=np.float64
        ),
    )


def branch_detector_chart(case: MaterialCase, branch: str) -> Any:
    if branch not in BRANCHES:
        raise ValueError(branch)
    reciprocal_frame = LayeredReciprocalFrame(
        reciprocal_basis_Ainv=case.inputs.reciprocal.basis_Ainv,
        sample_from_crystal_rotation=case.inputs.instrument.sample_from_crystal.rotation,
        axial_basis_index=2,
    )
    nominal = nominal_detector_measure(case)
    beam_center_column_px = float(case.inputs.instrument.detector_reference_coordinate_px[0])
    detector_columns = int(case.measured_count_per_px.shape[1])
    detector_column_interval_px = (
        (-0.5, beam_center_column_px)
        if branch == "plus"
        else (beam_center_column_px, detector_columns - 0.5)
    )
    chart = LayeredReciprocalDetectorAreaChart(
        detector_measure=nominal,
        reciprocal_frame=reciprocal_frame,
        detector_column_interval_px=detector_column_interval_px,
        air_exit_guard_rad=0.0,
    )
    return chart


def projected_field_mean(
    projection: Any,
    field: float | np.ndarray,
    support: np.ndarray,
) -> np.ndarray:
    if np.isscalar(field):
        return np.full(support.shape, float(field), dtype=np.float64)
    values = np.asarray(field, dtype=np.float64)
    mass, _ = projection.integrate_field(values, np.zeros(values.shape, dtype=np.float64))
    return np.divide(mass, support, out=np.full(support.shape, np.nan), where=support > 0.0)


def make_offspecular_profiles(
    case: MaterialCase,
) -> tuple[dict[int, dict[str, dict[str, np.ndarray]]], dict[int, dict[str, Any]]]:
    intervals = family_radial_intervals(case)
    prepared: dict[int, dict[str, dict[str, Any]]] = {family: {} for family in FAMILIES}
    evidence: dict[int, dict[str, Any]] = {}
    for family in FAMILIES:
        for branch in BRANCHES:
            quadrature = compile_branch_quadrature(case, family, branch, intervals[family])
            projection = compile_native_pixel_region_projection(
                quadrature, case.measured_count_per_px.shape
            )
            support = np.asarray(projection.observation_measure_px2, dtype=np.float64)
            measured = projected_field_mean(projection, case.measured_count_per_px, support)
            background = projected_field_mean(projection, case.background_count_per_px, support)
            unique_pixel = np.asarray(projection.flat_pixel_index, dtype=np.int64)
            pixel_index = unique_pixel[np.asarray(projection.pixel_column_index, dtype=np.int64)]
            invalid_overlap = np.bincount(
                np.asarray(projection.observation_row, dtype=np.int64),
                weights=(~case.detector_valid_mask.ravel()[pixel_index]).astype(np.float64),
                minlength=support.size,
            )
            prepared[family][branch] = {
                "quadrature": quadrature,
                "projection": projection,
                "support": support,
                "measured": measured,
                "background": background,
                "data_support": invalid_overlap == 0.0,
            }

        columns = np.concatenate(
            [np.asarray(prepared[family][branch]["quadrature"].column_px) for branch in BRANCHES]
        )
        rows = np.concatenate(
            [np.asarray(prepared[family][branch]["quadrature"].row_px) for branch in BRANCHES]
        )
        density, family_evidence = case.density_evaluator(family, columns, rows)
        evidence[family] = {
            **family_evidence,
            "radial_interval_Ainv": list(intervals[family]),
            "fold_radius_Ainv": family_fold_radius_Ainv(case, family),
        }
        cursor = 0
        for branch in BRANCHES:
            item = prepared[family][branch]
            quadrature = item["quadrature"]
            count = int(np.asarray(quadrature.column_px).size)
            local_density = density[cursor : cursor + count]
            cursor += count
            owner = np.asarray(quadrature.observation_row, dtype=np.int64)
            weight = np.asarray(quadrature.detector_area_weight_px2, dtype=np.float64)
            diffraction_mass = np.bincount(
                owner,
                weights=weight * local_density,
                minlength=item["support"].size,
            )
            diffraction = np.divide(
                diffraction_mass,
                item["support"],
                out=np.full(item["support"].shape, np.nan),
                where=item["support"] > 0.0,
            )
            model = case.scale_count_per_A2 * diffraction + item["background"]
            valid = (
                np.asarray(quadrature.observation_covered, dtype=bool)
                & item["data_support"]
                & (item["support"] > 0.0)
                & np.isfinite(item["measured"])
                & np.isfinite(model)
            )
            item.update(
                {
                    "qz_Ainv": 0.5 * (QZ_EDGES_AINV[:-1] + QZ_EDGES_AINV[1:]),
                    "diffraction_A2_per_px2": diffraction,
                    "model_total_count_per_px": model,
                    "valid": valid,
                }
            )
        if cursor != density.size:
            raise RuntimeError("family density split failed")
    return prepared, evidence


def build_angle_frame(case: MaterialCase, build_osc_angle_frame: Callable[..., Any]) -> Any:
    incident = build_geometry_only_ewald_context(
        case.inputs, instrument=case.detector.instrument
    ).incident
    return build_osc_angle_frame(
        mean_direction_lab=case.inputs.config.source.mean_direction_lab,
        instrument=case.inputs.instrument,
        sample_intersection_lab_m=incident.states.sample_intersection_lab_m[0],
        revision=f"all-materials-log-angle.v1:{case.image_id}",
    )


def angle_region_detector_mask(
    case: MaterialCase,
    angle_frame: Any,
    theta_edges_deg: np.ndarray,
    phi_edges_deg: np.ndarray,
) -> tuple[np.ndarray, dict[str, Any]]:
    """Return the exact native-pixel footprint of a declared angular rectangle."""

    theta_edges = np.asarray(theta_edges_deg, dtype=np.float64)
    phi_edges = np.asarray(phi_edges_deg, dtype=np.float64)
    projector = compile_detector_profile_projector(
        instrument=case.inputs.instrument,
        angle_frame=angle_frame,
        two_theta_bounds_rad=np.deg2rad(
            np.column_stack((theta_edges[:-1], theta_edges[1:]))
        ),
        phi_bin_edges_rad=np.broadcast_to(
            np.deg2rad(phi_edges), (theta_edges.size - 1, phi_edges.size)
        ),
        detector_valid_mask=np.ones(case.measured_count_per_px.shape, dtype=bool),
    )
    mask = np.zeros(case.measured_count_per_px.shape, dtype=bool)
    mask.ravel()[np.asarray(projector.coverage_pixel_index, dtype=np.int64)] = True
    return mask, {
        "projector_revision": projector.cache_key,
        "exact_geometric_pixel_count": int(np.count_nonzero(mask)),
    }


def make_structure_m0_profile(
    case: MaterialCase,
    build_osc_angle_frame: Callable[..., Any],
) -> tuple[dict[str, np.ndarray], dict[str, Any], np.ndarray]:
    angle_frame = build_angle_frame(case, build_osc_angle_frame)
    theta_edges_deg = np.linspace(1.0, 30.0, 291)
    phi_edges_deg = np.linspace(-10.0, 10.0, 81)
    theta_bounds = np.deg2rad(np.column_stack((theta_edges_deg[:-1], theta_edges_deg[1:])))
    phi_edges_rad = np.deg2rad(phi_edges_deg)[None, :]
    valid_native = np.asarray(case.detector_valid_mask, dtype=bool)
    raw_native = np.where(valid_native, case.measured_count_per_px, 0.0)
    background_native = (
        np.full(raw_native.shape, float(case.background_count_per_px), dtype=np.float64)
        if np.isscalar(case.background_count_per_px)
        else np.asarray(case.background_count_per_px, dtype=np.float64)
    )
    background_native = np.where(valid_native, np.maximum(background_native, 0.0), 0.0)
    shape = (theta_bounds.shape[0], phi_edges_deg.size - 1)
    measured_signal_map = np.zeros(shape, dtype=np.float64)
    measured_norm_map = np.zeros(shape, dtype=np.float64)
    background_signal_map = np.zeros(shape, dtype=np.float64)
    background_norm_map = np.zeros(shape, dtype=np.float64)
    measured_valid = np.zeros(shape, dtype=bool)
    coverage_pixels = []
    projector_keys = []
    topology = np.ones(valid_native.shape, dtype=bool)
    for theta_index, bounds in enumerate(theta_bounds):
        try:
            projector = compile_detector_profile_projector(
                instrument=case.inputs.instrument,
                angle_frame=angle_frame,
                two_theta_bounds_rad=bounds[None, :],
                phi_bin_edges_rad=phi_edges_rad,
                detector_valid_mask=topology,
            )
        except ValueError as error:
            if str(error) == "a local angular profile has no valid detector-pixel support":
                continue
            raise
        coverage = np.asarray(projector.coverage_pixel_index, dtype=np.int64)
        invalid_overlap = np.bincount(
            np.asarray(projector.coverage_profile_bin_index, dtype=np.int64),
            weights=(~valid_native.ravel()[coverage]).astype(np.float64),
            minlength=shape[1],
        )
        exact = np.asarray(projector.profile_bin_valid_mask[0], dtype=bool) & (
            invalid_overlap == 0.0
        )
        measured = project_detector_profiles(projector, raw_native)
        background = project_detector_profiles(projector, background_native)
        measured_signal_map[theta_index] = measured.S[0]
        measured_norm_map[theta_index] = measured.N[0]
        background_signal_map[theta_index] = background.S[0]
        background_norm_map[theta_index] = background.N[0]
        measured_valid[theta_index] = exact & measured.valid[0] & background.valid[0]
        coverage_pixels.append(coverage)
        projector_keys.append(projector.cache_key)

    selected_bins = np.flatnonzero(measured_valid.ravel())
    if selected_bins.size == 0:
        raise ValueError("m=0 angle region has no exact measured support")
    chart = AngleDetectorAreaChart(
        instrument=case.inputs.instrument,
        angle_frame=angle_frame,
        revision=f"m0-angle-chart.v1:{case.image_id}",
    )
    phi_bin_count = shape[1]
    theta_index, phi_index = np.divmod(selected_bins, phi_bin_count)
    quadrature = compile_continuous_rectangle_quadrature(
        chart=chart,
        first_coordinate_bounds=np.deg2rad(
            np.column_stack((theta_edges_deg[theta_index], theta_edges_deg[theta_index + 1]))
        ),
        second_coordinate_bounds=np.deg2rad(
            np.column_stack((phi_edges_deg[phi_index], phi_edges_deg[phi_index + 1]))
        ),
        observation_row=np.arange(selected_bins.size, dtype=np.int64),
        observation_count=selected_bins.size,
        gauss_order=ANGLE_GAUSS_ORDER,
        background_coordinate_axis=0,
    )
    columns = np.asarray(quadrature.column_px, dtype=np.float64)
    rows = np.asarray(quadrature.row_px, dtype=np.float64)
    density, info = case.density_evaluator(0, columns, rows)
    owner = np.asarray(quadrature.observation_row, dtype=np.int64)
    weight = np.asarray(quadrature.detector_area_weight_px2, dtype=np.float64)
    normalization = np.bincount(owner, weights=weight, minlength=selected_bins.size)
    signal = np.bincount(owner, weights=weight * density, minlength=selected_bins.size)
    signal_map = np.zeros(shape, dtype=np.float64)
    normalization_map = np.zeros(shape, dtype=np.float64)
    model_valid = np.zeros(shape, dtype=bool)
    signal_map.ravel()[selected_bins] = signal
    normalization_map.ravel()[selected_bins] = normalization
    model_valid.ravel()[selected_bins] = (
        np.asarray(quadrature.observation_covered, dtype=bool)
        & (normalization > 0.0)
        & np.isfinite(signal)
    )

    valid = measured_valid & model_valid & (normalization_map > 0.0)
    measured_signal = np.where(valid, measured_signal_map, 0.0)
    measured_norm = np.where(valid, measured_norm_map, 0.0)
    background_signal = np.where(valid, background_signal_map, 0.0)
    background_norm = np.where(valid, background_norm_map, 0.0)
    model_signal = np.where(valid, signal_map, 0.0)
    model_norm = np.where(valid, normalization_map, 0.0)
    measured_denominator = measured_norm.sum(axis=1)
    background_denominator = background_norm.sum(axis=1)
    model_denominator = model_norm.sum(axis=1)
    valid_theta = (
        (measured_denominator > 0.0)
        & (background_denominator > 0.0)
        & (model_denominator > 0.0)
        & np.any(valid, axis=1)
    )
    measured_line = np.divide(
        measured_signal.sum(axis=1),
        measured_denominator,
        out=np.full(shape[0], np.nan),
        where=valid_theta,
    )
    background_line = np.divide(
        background_signal.sum(axis=1),
        background_denominator,
        out=np.full(shape[0], np.nan),
        where=valid_theta,
    )
    diffraction_line = np.divide(
        model_signal.sum(axis=1),
        model_denominator,
        out=np.full(shape[0], np.nan),
        where=valid_theta,
    )
    theta_centers_deg = 0.5 * (theta_edges_deg[:-1] + theta_edges_deg[1:])
    qz_Ainv = (
        4.0
        * np.pi
        / float(case.inputs.config.source.mean_wavelength_A)
        * np.sin(0.5 * np.deg2rad(theta_centers_deg))
    )
    profile = {
        "qz_Ainv": qz_Ainv,
        "measured_count_per_px": measured_line,
        "background_count_per_px": background_line,
        "diffraction_A2_per_px2": diffraction_line,
        "model_total_count_per_px": case.scale_count_per_A2 * diffraction_line + background_line,
        "valid": valid_theta
        & np.isfinite(measured_line)
        & np.isfinite(diffraction_line)
        & np.isfinite(background_line),
    }
    mask = np.zeros(case.measured_count_per_px.shape, dtype=bool)
    mask.ravel()[np.unique(np.concatenate(coverage_pixels))] = True
    return (
        profile,
        {
            "gauss_order": ANGLE_GAUSS_ORDER,
            "two_theta_range_deg": [1.0, 30.0],
            "phi_range_deg": [-10.0, 10.0],
            "coordinate_count": int(columns.size),
            "compiled_term_count": int(info.get("compiled_term_count", 0)),
            "projector_count": len(projector_keys),
            "backend": "cpu_sparse_structure_response",
            "density_evaluation": info,
        },
        mask,
    )


def load_gd_sid_cases() -> tuple[list[MaterialCase], Callable[..., Any], dict[str, Any]]:
    module = load_module("all_materials_gd_sid", GD_EXECUTOR)
    source_fit = json.loads(module.SOURCE_JSON.read_text(encoding="utf-8"))
    geometry = module.checked_json(
        Path(source_fit["inputs"]["geometry_json"]), source_fit["inputs"]["geometry_sha256"]
    )
    background = module.checked_json(
        Path(source_fit["inputs"]["background_json"]),
        source_fit["inputs"]["background_sha256"],
    )
    replay_path = (
        LIBRARY
        / "runs"
        / "pbi2-gd1-sid1-2026-08-26-sf-full-reciprocal"
        / "artifacts"
        / "fits"
        / "sf_full_qz"
        / "gd1_sid1_sf_full_qz_replay.json"
    )
    replay = json.loads(replay_path.read_text(encoding="utf-8"))
    geometry_parameters = module.FIT.OLD.geometry_parameter_vector(geometry)
    states = module.FIT.OLD.frozen_background_states(background)
    dark_path = Path(source_fit["inputs"]["dark_path"])
    dark = module.FIT.read_osc(dark_path).detector_native_counts.astype(np.float64)
    dark_scale = float(background["inputs"]["dark_scale"])
    cases = []
    specifications = {
        "gd1": {
            "label": "GD1",
            "archetype": "simple 2H PbI₂",
            "image_id": "GD1-5deg",
            "angle": 5.0,
            "mosaic_label": "2H; fitted Gaussian/Lorentzian mosaic",
        },
        "sid1": {
            "label": "SiD1",
            "archetype": "broad-mosaic 2H PbI₂",
            "image_id": "SiD1-4deg-2min",
            "angle": 4.0,
            "mosaic_label": "2H; broad fitted Gaussian mosaic",
        },
    }
    for specimen, spec in specifications.items():
        sample_replay = replay["samples"][specimen]["structure_replay"]
        mosaic = sample_replay["mosaic_frozen"]
        structure = np.asarray(sample_replay["fit"]["selected"]["parameters"], dtype=np.float64)
        detector, inputs = module.FIT.build_detector(
            specimen,
            spec["angle"],
            geometry_parameters,
            float(mosaic["gaussian_sigma_deg"]),
            float(mosaic["lorentzian_hwhm_deg"]),
            float(mosaic["lorentzian_probability"]),
            256,
            structure_parameters=structure,
        )
        osc_path = next(
            Path(path)
            for image_id, _, path in module.FIT.IMAGE_SPECS[specimen]
            if image_id == spec["image_id"]
        )
        raw = module.FIT.read_osc(osc_path).detector_native_counts.astype(np.float64)
        valid = detector_valid_mask_from_counts(raw)
        measured = raw
        row, column = np.indices(raw.shape, dtype=np.float64)
        center_column, center_row = inputs.instrument.detector_reference_coordinate_px
        radius = np.hypot(column - center_column, row - center_row)
        radial = states[specimen].count_density(spec["image_id"], radius)
        scale = float(
            sample_replay["confirmations"]["256"]["scale_by_image_A2_to_count"][spec["image_id"]]
        )

        def evaluator(
            family_m: int,
            column_px: np.ndarray,
            row_px: np.ndarray,
            detector: Any = detector,
        ) -> tuple[np.ndarray, dict[str, Any]]:
            return structure_density(
                family_detector(detector, family_m), column_px, row_px, batch_size=512
            )

        cases.append(
            MaterialCase(
                key=specimen,
                label_plain=spec["label"],
                label_math=spec["label"],
                archetype=spec["archetype"],
                image_id=spec["image_id"],
                image_label=str(osc_path),
                incidence_deg=spec["angle"],
                detector=detector,
                inputs=inputs,
                raw_count_per_px=raw,
                measured_count_per_px=measured,
                detector_valid_mask=np.asarray(valid, dtype=bool),
                background_count_per_px=np.asarray(radial + dark_scale * dark, dtype=np.float64),
                scale_count_per_A2=scale,
                source_count=256,
                model_status="MODEL_LIMITED_CONDITIONAL_SF_REPLAY",
                background_note=(
                    "frozen radial background plus the acquisition-matched timed dark"
                ),
                density_evaluator=evaluator,
            )
        )
        del row, column, radius
    provenance = {
        "executor": file_record(GD_EXECUTOR),
        "source_fit": file_record(module.SOURCE_JSON),
        "replay": file_record(replay_path),
        "dark": file_record(dark_path),
    }
    return cases, module.build_osc_angle_frame, provenance


def load_clean1_case() -> tuple[list[MaterialCase], None, dict[str, Any]]:
    angle = loaded_module("all_materials_clean1_angle", CLEAN1_ANGLE)
    fit = json.loads(CLEAN1_FIT.read_text(encoding="utf-8"))
    if fit["status"] != "MODEL_LIMITED_CONDITIONAL_SHARED_INTENSITY_REFIT":
        raise ValueError("unexpected Clean1 frozen-fit status")
    selected = fit["selected"]
    source_count = int(fit["metadata"]["source_count"])
    if source_count != 512:
        raise ValueError("Clean1 selected fit is not the frozen 512-source state")
    scale = float(fit["source_checks"]["clean1_4"]["scale"])
    if scale != float(selected["scale"]):
        raise ValueError("Clean1 primary-image scale is not the frozen selected scale")
    simulation_inputs = angle.clean1.source_inputs({"angle": 4.7})
    runner = angle.clean1.runner
    material = runner.material_optics(
        simulation_inputs.crystal, simulation_inputs.samples.wavelength_A
    )
    incident = runner.build_incident_states(
        simulation_inputs.samples, material, simulation_inputs.instrument
    )
    simulation_inputs = replace(
        simulation_inputs, material=material, incident=incident
    )
    detector = runner.build_source_averaged_structure_detector(
        simulation_inputs,
        strength_model=runner.UnitRodStrength(
            np.asarray(simulation_inputs.strength.reciprocal_basis_Ainv, dtype=np.float64)
        ),
    )
    inputs = replace(
        runner.build_configured_geometry_inputs(simulation_inputs.config),
        instrument=simulation_inputs.instrument,
    )
    candidate = angle.clean1.Candidate(**selected["parameters"])
    fitted_mosaic = angle.clean1.MosaicParameters(
        gaussian_sigma_rad=math.radians(candidate.sg),
        lorentzian_half_width_rad=math.radians(candidate.gl),
        lorentzian_probability=candidate.eta,
    )
    detector = replace(detector, mosaic=fitted_mosaic)
    image_id = "clean1_4"
    osc_path = next(
        Path(path)
        for key, path, _ in angle.clean1.primary.IMAGE_SPECS
        if key == image_id
    )
    if angle.clean1.primary.sha256_file(osc_path) != angle.clean1.primary.OSC_SHA256[image_id]:
        raise ValueError("Clean1 OSC identity changed")
    raw = angle.clean1.primary.read_osc(osc_path).detector_native_counts.astype(np.float64)
    valid = angle.clean1.primary.detector_valid_mask_from_counts(raw)
    with np.load(CLEAN1_JOINT, allow_pickle=False) as joint:
        m0_selected = np.asarray(joint[f"{image_id}_family"], dtype=np.int64) == 0
        local_background = np.asarray(
            joint[f"{image_id}_background"], dtype=np.float64
        )[m0_selected]
    if local_background.size == 0 or not np.allclose(
        local_background, local_background[0], rtol=0.0, atol=1e-10
    ):
        raise ValueError("Clean1 frozen m=0 background is not constant")
    background_count = float(local_background[0])

    with np.load(CLEAN1_WIDE, allow_pickle=False) as archive:
        theta_edges_deg = np.asarray(archive["theta_edges_deg"], dtype=np.float64).copy()
        phi_edges_deg = np.asarray(archive["phi_edges_deg"], dtype=np.float64).copy()
        measured_signal = np.asarray(archive["measured_signal"], dtype=np.float64).copy()
        measured_area = np.asarray(archive["measured_area"], dtype=np.float64).copy()
        model_signal = np.asarray(
            archive["source512_physical00_signal"], dtype=np.float64
        ).copy()
        model_area = np.asarray(archive["model_area"], dtype=np.float64).copy()
    if not np.array_equal(theta_edges_deg, np.linspace(1.0, 30.0, 291)) or not np.array_equal(
        phi_edges_deg, np.linspace(-10.0, 10.0, 81)
    ):
        raise ValueError("Clean1 wide-angle archive does not have the requested bounds")
    frame = angle.nominal_frame(inputs, image_id)
    archive_projector = compile_detector_profile_projector(
        instrument=inputs.instrument,
        angle_frame=frame,
        two_theta_bounds_rad=np.deg2rad(
            np.column_stack((theta_edges_deg[:-1], theta_edges_deg[1:]))
        ),
        phi_bin_edges_rad=np.broadcast_to(
            np.deg2rad(phi_edges_deg),
            (theta_edges_deg.size - 1, phi_edges_deg.size),
        ),
        detector_valid_mask=np.asarray(valid, dtype=bool),
    )
    replayed = project_detector_profiles(archive_projector, raw)
    if not np.array_equal(replayed.S, measured_signal) or not np.array_equal(
        replayed.N, measured_area
    ):
        raise ValueError("Clean1 wide-angle raw projection does not replay bit-exactly")
    bin_valid = (
        np.asarray(replayed.valid, dtype=bool)
        & np.isfinite(measured_signal)
        & np.isfinite(measured_area)
        & np.isfinite(model_signal)
        & np.isfinite(model_area)
        & (measured_area > 0.0)
        & (model_area > 0.0)
    )
    measured_denominator = np.where(bin_valid, measured_area, 0.0).sum(axis=1)
    model_denominator = np.where(bin_valid, model_area, 0.0).sum(axis=1)
    measured_line = np.divide(
        np.where(bin_valid, measured_signal, 0.0).sum(axis=1),
        measured_denominator,
        out=np.full(theta_edges_deg.size - 1, np.nan),
        where=measured_denominator > 0.0,
    )
    diffraction_line = np.divide(
        np.where(bin_valid, model_signal, 0.0).sum(axis=1),
        model_denominator,
        out=np.full(theta_edges_deg.size - 1, np.nan),
        where=model_denominator > 0.0,
    )
    theta_centers_deg = 0.5 * (theta_edges_deg[:-1] + theta_edges_deg[1:])
    qz_Ainv = (
        4.0
        * np.pi
        / float(inputs.config.source.mean_wavelength_A)
        * np.sin(0.5 * np.deg2rad(theta_centers_deg))
    )
    provisional = MaterialCase(
        key="clean1",
        label_plain="Clean1",
        label_math="Clean1",
        archetype="2H+4H+6H+equal-mix PbI₂",
        image_id=image_id,
        image_label=str(osc_path),
        incidence_deg=4.7,
        detector=detector,
        inputs=inputs,
        raw_count_per_px=raw,
        measured_count_per_px=raw,
        detector_valid_mask=np.asarray(valid, dtype=bool),
        background_count_per_px=background_count,
        scale_count_per_A2=scale,
        source_count=source_count,
        model_status=(
            "MODEL_LIMITED; PRIMARY 512-STATE CHECK PASSED; FULL-WINDOW NOT CERTIFIED"
        ),
        background_note=(
            "frozen local m=0 constant background extrapolated across the display window"
        ),
        density_evaluator=lambda *_: (_ for _ in ()).throw(RuntimeError("unbound")),
    )
    detector_mask, mask_info = angle_region_detector_mask(
        provisional, frame, theta_edges_deg, phi_edges_deg
    )
    m0_valid = (
        (measured_denominator > 0.0)
        & (model_denominator > 0.0)
        & np.isfinite(measured_line)
        & np.isfinite(diffraction_line)
    )
    m0_profile = {
        "qz_Ainv": qz_Ainv,
        "measured_count_per_px": measured_line,
        "background_count_per_px": np.full(measured_line.shape, background_count),
        "diffraction_A2_per_px2": diffraction_line,
        "model_total_count_per_px": (
            scale * diffraction_line + background_count
        ),
        "valid": m0_valid,
        "detector_mask": detector_mask,
        "evidence": {
            "gauss_order": 2,
            "two_theta_range_deg": [1.0, 30.0],
            "phi_range_deg": [-10.0, 10.0],
            "source_count": source_count,
            "physical_field": "source512_physical00_signal",
            "raw_projector_revision": archive_projector.cache_key,
            "raw_archive_replay_bit_exact": True,
            "full_window_convergence_certified": False,
            "background_added_by_renderer": True,
            **mask_info,
        },
    }
    master_source_count = int(simulation_inputs.samples.wavelength_A.size)
    chunk_width = 8 * int(np.unique(simulation_inputs.samples.wavelength_A).size)
    if source_count % chunk_width:
        raise ValueError("Clean1 source prefix does not align to complete source chunks")
    chunk_count = source_count // chunk_width

    def evaluator(
        family_m: int,
        column_px: np.ndarray,
        row_px: np.ndarray,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        if family_m not in FAMILIES:
            raise ValueError(f"unsupported Clean1 off-specular family m={family_m}")
        columns = np.asarray(column_px, dtype=np.float64).ravel()
        rows = np.asarray(row_px, dtype=np.float64).ravel()
        if columns.shape != rows.shape:
            raise ValueError("Clean1 detector coordinate arrays disagree")
        results: dict[int, tuple[np.ndarray, dict[str, Any]]] = {}
        worker_count = min(8, chunk_count)
        with ProcessPoolExecutor(max_workers=worker_count) as executor:
            futures = {
                executor.submit(
                    clean1_family_chunk_worker,
                    image_id,
                    4.7,
                    chunk,
                    columns,
                    rows,
                    selected,
                    family_m,
                ): chunk
                for chunk in range(chunk_count)
            }
            for future in as_completed(futures):
                chunk, density_mass, audit = future.result()
                results[chunk] = (density_mass, audit)
                print(
                    f"Clean1 m={family_m} source chunk {chunk + 1}/{chunk_count} complete",
                    flush=True,
                )
        audits = [results[index][1] for index in range(chunk_count)]
        expected_rod_count = sum(
            int(rod.family_m) == family_m for rod in detector.rods
        )
        if any(int(item["configured_rod_count"]) != expected_rod_count for item in audits):
            raise ValueError("Clean1 worker family restriction did not bind")
        if any(
            h * h + h * k + k * k != family_m
            for item in audits
            for h, k in item["physical_rods"]
        ):
            raise ValueError("Clean1 worker leaked a different rod family")
        mass = float(sum(item["mass"] for item in audits))
        expected_mass = source_count / master_source_count
        if not np.isclose(mass, expected_mass, rtol=0.0, atol=2e-15):
            raise ValueError("Clean1 source-prefix probability mass changed")
        density = np.sum(
            [results[index][0] for index in range(chunk_count)], axis=0
        ) / mass
        if density.shape != columns.shape or np.any(~np.isfinite(density)) or np.any(density < 0):
            raise FloatingPointError("invalid Clean1 continuous family density")
        return np.asarray(density, dtype=np.float64), {
            "backend": "cpu_process_pool_frozen_clean1_response",
            "family_restricted": True,
            "display_source_count": source_count,
            "master_source_count": master_source_count,
            "source_probability_mass_before_prefix_normalization": mass,
            "chunk_count": chunk_count,
            "worker_count": worker_count,
            "configured_rod_count": expected_rod_count,
            "fit_support": "model-only" if family_m == 3 else "included in frozen fit",
            "compiled_term_count": int(sum(item["term_count"] for item in audits)),
            "response_revisions": sorted(
                {revision for item in audits for revision in item["response_revisions"]}
            ),
        }

    case = replace(provisional, density_evaluator=evaluator, m0_profile=m0_profile)
    provenance = {
        "renderer": file_record(Path(__file__)),
        "angle_authority": file_record(CLEAN1_ANGLE),
        "fit": file_record(CLEAN1_FIT),
        "joint_diagnostic": file_record(CLEAN1_JOINT),
        "wide_angle_manifest": file_record(CLEAN1_WIDE_MANIFEST),
        "wide_angle_diagnostic": file_record(CLEAN1_WIDE),
        "raw_osc": file_record(osc_path),
    }
    return [case], None, provenance


def load_b4_case() -> tuple[list[MaterialCase], Callable[..., Any], dict[str, Any]]:
    core = loaded_module("pbi2_b4_single_peak_refit", B4_CORE)
    mosaic = loaded_module("tmp_b4_mosaic_fit", B4_MOSAIC)
    response = loaded_module("all_materials_b4_response", B4_RESPONSE)
    fit = json.loads(B4_FIT.read_text(encoding="utf-8"))
    if fit["classification"] != "NO_ORACLE_CONDITIONAL_DISCRETE_SCREEN":
        raise ValueError("unexpected B4 frozen-fit classification")
    selected = fit["selected"]
    parameters = {
        "mosaic": list(fit["mosaic"]),
        "z_iodine_fractional_layer": float(selected["z_iodine_fractional_layer"]),
        "epsilon_2h": float(selected["epsilon_2h"]),
        "epsilon_6h": float(selected["epsilon_6h"]),
        "u_radial_A2": float(fit["u_radial_A2"]),
        "u_normal_A2": float(fit["u_normal_A2"]),
        "phase_fractions": [
            float(selected["fraction_2h"]),
            float(selected["fraction_6h_plus"]),
            float(selected["fraction_6h_minus"]),
        ],
    }
    geometry_inputs = mosaic.build_configured_geometry_inputs(
        mosaic.simulation_config(int(fit["source_count"]))
    )
    mosaic.SOURCE_STATE_CHUNK_COUNT = 16
    chunked_detector, _, simulation_inputs = core.sobol_detector(mosaic, 256)
    geometry_inputs = replace(geometry_inputs, instrument=chunked_detector.instrument)
    if len(chunked_detector.detectors) != 16:
        raise ValueError("B4 256-state display replay did not form 16 source chunks")
    representative = replace(
        chunked_detector.detectors[0], mosaic=response._mosaic(tuple(parameters["mosaic"]))
    )
    osc_path = Path(mosaic.OSC)
    raw = mosaic.read_osc(osc_path).detector_native_counts.astype(np.float64)
    valid = mosaic.detector_valid_mask_from_counts(raw)
    with np.load(B4_BACKGROUND, allow_pickle=False) as background_archive:
        background = np.asarray(
            background_archive["background_native_counts"], dtype=np.float64
        )
    if background.shape != raw.shape or np.any(~np.isfinite(background)) or np.any(background <= 0):
        raise ValueError("B4 frozen native background is invalid")

    def evaluator(
        family_m: int,
        column_px: np.ndarray,
        row_px: np.ndarray,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        rods = tuple(rod for rod in representative.rods if int(rod.family_m) == family_m)
        if not rods:
            raise ValueError(f"B4 detector has no m={family_m} rods")
        detectors = tuple(child.restrict_rods(rods) for child in chunked_detector.detectors)
        columns = np.asarray(column_px, dtype=np.float64).ravel()
        rows = np.asarray(row_px, dtype=np.float64).ravel()
        if columns.shape != rows.shape:
            raise ValueError("B4 detector-coordinate arrays disagree")
        supported = (
            b4_canonical_roundtrip_support(detectors, columns, rows)
            if family_m == 0
            else np.ones(columns.shape, dtype=bool)
        )
        selected_columns = columns[supported]
        selected_rows = rows[supported]
        if selected_columns.size == 0:
            raise ValueError("B4 family has no canonically supported detector coordinates")
        results: dict[int, tuple[float, np.ndarray, dict[str, Any]]] = {}
        with ProcessPoolExecutor(max_workers=8) as executor:
            futures = {
                executor.submit(
                    b4_family_chunk_worker,
                    index,
                    child,
                    float(probability),
                    selected_columns,
                    selected_rows,
                    simulation_inputs.crystal,
                    family_m,
                    parameters,
                ): index
                for index, (child, probability) in enumerate(
                    zip(detectors, chunked_detector.chunk_probability, strict=True)
                )
            }
            for future in as_completed(futures):
                index, probability, density, audit = future.result()
                results[index] = (probability, density, audit)
                print(
                    f"B4 m={family_m} source chunk {index + 1}/{len(detectors)} complete",
                    flush=True,
                )
        probability_sum = float(sum(item[0] for item in results.values()))
        if not np.isclose(probability_sum, 1.0, rtol=0.0, atol=2e-15):
            raise ValueError("B4 source chunk probabilities do not sum to one")
        selected_density = sum(
            results[index][0] * results[index][1] for index in range(len(detectors))
        )
        density = np.full(columns.shape, np.nan, dtype=np.float64)
        density[supported] = selected_density
        audits = [results[index][2] for index in range(len(detectors))]
        return np.asarray(density, dtype=np.float64), {
            "backend": "cpu_process_pool_frozen_b4_response",
            "display_source_count": 256,
            "fit_source_count": int(fit["source_count"]),
            "chunk_count": len(detectors),
            "worker_count": 8,
            "source_probability_mass": probability_sum,
            "coordinate_count": int(columns.size),
            "canonical_roundtrip_rejected_coordinate_count": int(
                np.count_nonzero(~supported)
            ),
            "compiled_term_count": int(sum(item["term_count"] for item in audits)),
            "response_revisions": [
                revision
                for item in audits
                for revision in item["response_revisions"]
            ],
        }

    case = MaterialCase(
        key="b4",
        label_plain="B4",
        label_math="B4",
        archetype="2H+6H PbI₂",
        image_id="B4-4deg",
        image_label=str(osc_path),
        incidence_deg=4.0,
        detector=representative,
        inputs=geometry_inputs,
        raw_count_per_px=raw,
        measured_count_per_px=raw,
        detector_valid_mask=np.asarray(valid, dtype=bool),
        background_count_per_px=background,
        scale_count_per_A2=float(selected["common_scale"]),
        source_count=256,
        model_status=(
            "NO_ORACLE CONDITIONAL FIT; 1024-STATE FIT, 256-STATE DISPLAY PROJECTION"
        ),
        background_note="frozen fitted positive native-detector background field",
        density_evaluator=evaluator,
    )
    provenance = {
        "renderer": file_record(Path(__file__)),
        "core_authority": file_record(B4_CORE),
        "response_authority": file_record(B4_RESPONSE),
        "mosaic_authority": file_record(B4_MOSAIC),
        "fit": file_record(B4_FIT),
        "m0_anchor": file_record(B4_M0),
        "native_background": file_record(B4_BACKGROUND),
    }
    return [case], mosaic.build_osc_angle_frame, provenance


def filled_region_for_display(mask: np.ndarray) -> np.ndarray:
    if mask.ndim != 2:
        raise ValueError("display mask must be two-dimensional")
    filled = np.zeros_like(mask, dtype=bool)
    active_rows = np.flatnonzero(np.any(mask, axis=1))
    if active_rows.size == 0:
        return filled
    left = np.asarray(
        [np.flatnonzero(mask[row])[0] for row in active_rows], dtype=np.float64
    )
    right = np.asarray(
        [np.flatnonzero(mask[row])[-1] for row in active_rows], dtype=np.float64
    )
    rows = np.arange(active_rows[0], active_rows[-1] + 1, dtype=np.int64)
    left_by_row = np.rint(np.interp(rows, active_rows, left)).astype(np.int64)
    right_by_row = np.rint(np.interp(rows, active_rows, right)).astype(np.int64)
    for row, first_column, last_column in zip(
        rows, left_by_row, right_by_row, strict=True
    ):
        filled[row, first_column : last_column + 1] = True
    return filled


def zero_density_for_display_geometry(
    family_m: int, column_px: np.ndarray, row_px: np.ndarray
) -> tuple[np.ndarray, dict[str, Any]]:
    del family_m, row_px
    return np.zeros(np.asarray(column_px).shape, dtype=np.float64), {
        "purpose": "display geometry only"
    }


def reciprocal_region_display_masks(
    case: MaterialCase,
) -> dict[int, dict[str, np.ndarray]]:
    """Classify detector centers against the declared continuous reciprocal regions."""

    row_count, column_count = case.measured_count_per_px.shape
    display_rows = min(
        row_count,
        math.ceil(float(case.inputs.instrument.detector_reference_coordinate_px[1])),
    )
    beam_column = float(case.inputs.instrument.detector_reference_coordinate_px[0])
    measure = nominal_detector_measure(case)
    frame = LayeredReciprocalFrame(
        reciprocal_basis_Ainv=case.inputs.reciprocal.basis_Ainv,
        sample_from_crystal_rotation=case.inputs.instrument.sample_from_crystal.rotation,
        axial_basis_index=2,
    )
    cstar_Ainv = float(np.linalg.norm(case.inputs.reciprocal.basis_Ainv[:, 2]))
    intervals = family_radial_intervals(case)
    masks = {
        family: {
            branch: np.zeros((row_count, column_count), dtype=bool)
            for branch in BRANCHES
        }
        for family in FAMILIES
    }
    column_values = np.arange(column_count, dtype=np.float64)
    for row_start in range(0, display_rows, 128):
        row_values = np.arange(
            row_start, min(row_start + 128, display_rows), dtype=np.float64
        )
        column, row = np.meshgrid(column_values, row_values)
        geometry = measure.evaluate_detector_geometry(
            column.ravel(), row.ravel(), include_surface_jacobian=False
        )
        qr_Ainv, ell = frame.coordinates(np.asarray(geometry.q_sample_Ainv))
        qz_Ainv = cstar_Ainv * ell
        kf_air = np.asarray(geometry.kf_air_sample_Ainv)
        air_exit_rad = np.arctan2(
            kf_air[:, 2], np.hypot(kf_air[:, 0], kf_air[:, 1])
        )
        common = (
            np.asarray(geometry.valid, dtype=bool)
            & np.isfinite(qr_Ainv)
            & np.isfinite(qz_Ainv)
            & (qz_Ainv >= QZ_EDGES_AINV[0])
            & (qz_Ainv <= QZ_EDGES_AINV[-1])
            & (air_exit_rad >= 0.0)
        )
        flat_column = column.ravel()
        local_shape = (row_values.size, column_count)
        for family, (radial_low, radial_high) in intervals.items():
            inside = common & (qr_Ainv >= radial_low) & (qr_Ainv <= radial_high)
            masks[family]["plus"][row_start : row_start + row_values.size] = (
                inside & (flat_column <= beam_column)
            ).reshape(local_shape)
            masks[family]["minus"][row_start : row_start + row_values.size] = (
                inside & (flat_column > beam_column)
            ).reshape(local_shape)
    return masks


def load_saved_profiles(
    case: MaterialCase,
) -> tuple[dict[int, dict[str, dict[str, Any]]], dict[str, np.ndarray], Path]:
    """Restore frozen profiles while rebuilding only their geometric projectors."""

    profile_path = HERE / f"{case.key}_continuous_profiles.npz"
    if not profile_path.is_file():
        raise FileNotFoundError(profile_path)
    geometry_case = replace(case, density_evaluator=zero_density_for_display_geometry)
    profiles, _ = make_offspecular_profiles(geometry_case)
    with np.load(profile_path, allow_pickle=False) as archive:
        for family in FAMILIES:
            for branch in BRANCHES:
                prefix = f"m{family}_{branch}"
                item = profiles[family][branch]
                for source, target in (
                    ("qz_Ainv", "qz_Ainv"),
                    ("measured_count_per_px", "measured"),
                    ("background_count_per_px", "background"),
                    ("diffraction_A2_per_px2", "diffraction_A2_per_px2"),
                    ("model_total_count_per_px", "model_total_count_per_px"),
                    ("valid", "valid"),
                ):
                    item[target] = np.asarray(
                        archive[f"{prefix}_{source}"]
                    ).copy()
        m0 = {
            key: np.asarray(archive[f"m0_{key}"]).copy()
            for key in (
                "qz_Ainv",
                "measured_count_per_px",
                "background_count_per_px",
                "diffraction_A2_per_px2",
                "model_total_count_per_px",
                "valid",
            )
        }
    return profiles, m0, profile_path


def region_masks(
    case: MaterialCase,
    profiles: dict[int, dict[str, dict[str, Any]]],
    m0_exact_mask: np.ndarray,
) -> tuple[dict[int, dict[str, np.ndarray]], np.ndarray, dict[str, Any]]:
    masks = reciprocal_region_display_masks(case)
    evidence: dict[str, Any] = {}
    for family in FAMILIES:
        evidence[str(family)] = {}
        for branch in BRANCHES:
            projection = profiles[family][branch]["projection"]
            quadrature_nodes = np.zeros(case.measured_count_per_px.shape, dtype=bool)
            quadrature_nodes.ravel()[
                np.asarray(projection.flat_pixel_index, dtype=np.int64)
            ] = True
            display = masks[family][branch]
            active_rows = np.flatnonzero(np.any(display, axis=1))
            run_count = display[:, 0].astype(np.int64) + np.count_nonzero(
                display[:, 1:] & ~display[:, :-1], axis=1
            )
            node_count = int(np.count_nonzero(quadrature_nodes))
            evidence[str(family)][branch] = {
                "quadrature_node_pixel_count": node_count,
                "display_region_pixel_count": int(np.count_nonzero(display)),
                "quadrature_node_containment_fraction": (
                    float(np.count_nonzero(quadrature_nodes & display) / node_count)
                    if node_count
                    else 1.0
                ),
                "display_active_row_count": int(active_rows.size),
                "display_internal_empty_row_count": (
                    int(
                        np.count_nonzero(
                            ~np.any(display[active_rows[0] : active_rows[-1] + 1], axis=1)
                        )
                    )
                    if active_rows.size
                    else 0
                ),
                "maximum_contiguous_runs_per_row": int(np.max(run_count, initial=0)),
            }
        if np.any(masks[family]["plus"] & masks[family]["minus"]):
            raise ValueError(f"m={family} display branches overlap")
    return masks, filled_region_for_display(m0_exact_mask), evidence


def render_profile_grid(
    case: MaterialCase,
    profiles: dict[int, dict[str, dict[str, Any]]],
    m0: dict[str, np.ndarray],
    destination: Path,
) -> None:
    figure = plt.figure(figsize=(10.8, 9.0), layout="constrained")
    outer = figure.add_gridspec(2, 1, height_ratios=(3.0, 1.15), hspace=0.18)
    upper = outer[0].subgridspec(3, 2, hspace=0.0, wspace=0.0)
    axes = np.asarray(
        [[figure.add_subplot(upper[row, column]) for column in range(2)] for row in range(3)]
    )
    m0_axis = figure.add_subplot(outer[1])
    positive_values = []
    for family in FAMILIES:
        for branch in BRANCHES:
            profile = profiles[family][branch]
            valid = np.asarray(profile["valid"], dtype=bool)
            for key in ("measured", "model_total_count_per_px"):
                values = np.asarray(profile[key], dtype=np.float64)[valid]
                positive_values.extend(values[np.isfinite(values) & (values > 0.0)])
    positive = np.asarray(positive_values, dtype=np.float64)
    if positive.size == 0:
        raise ValueError("off-specular profiles contain no positive values")
    y_min = max(float(np.quantile(positive, 0.002)) * 0.7, np.finfo(float).tiny)
    y_max = float(np.quantile(positive, 0.998)) * 1.4
    for row, family in enumerate(FAMILIES):
        for column, branch in enumerate(("minus", "plus")):
            axis = axes[row, column]
            profile = profiles[family][branch]
            valid = np.asarray(profile["valid"], dtype=bool)
            qz = np.asarray(profile["qz_Ainv"], dtype=np.float64)
            measured = np.asarray(profile["measured"], dtype=np.float64)
            model = np.asarray(profile["model_total_count_per_px"], dtype=np.float64)
            axis.plot(
                qz,
                np.where(valid & (measured > 0.0), measured, np.nan),
                color="#222222",
                lw=1.0,
                label="Data",
            )
            axis.plot(
                qz,
                np.where(valid & (model > 0.0), model, np.nan),
                color="#D55E00",
                lw=1.25,
                ls="--",
                label="Simulation + background",
            )
            axis.set(xlim=(QZ_EDGES_AINV[0], QZ_EDGES_AINV[-1]), ylim=(y_min, y_max))
            axis.set_yscale("log")
            axis.grid(which="both", color="#AAB2B9", alpha=0.27, lw=0.5)
            axis.text(
                0.5,
                0.965,
                rf"$m={family}{'+' if branch == 'plus' else '-'}$",
                transform=axis.transAxes,
                ha="center",
                va="top",
                fontsize=9,
            )
            if row < 2:
                axis.tick_params(labelbottom=False)
            else:
                axis.set_xlabel(r"$q_z$ ($\AA^{-1}$)")
            if column == 1:
                axis.tick_params(labelleft=False)
            if row == 0 and column == 1:
                axis.legend(frameon=False, loc="upper right", fontsize=7.5)
    axes[1, 0].set_ylabel(r"Intensity (count / px$^2$)")

    valid = np.asarray(m0["valid"], dtype=bool)
    qz = np.asarray(m0["qz_Ainv"], dtype=np.float64)
    measured = np.asarray(m0["measured_count_per_px"], dtype=np.float64)
    model = np.asarray(m0["model_total_count_per_px"], dtype=np.float64)
    m0_axis.plot(
        qz,
        np.where(valid & (measured > 0.0), measured, np.nan),
        color="#222222",
        lw=1.0,
        label="Data",
    )
    m0_axis.plot(
        qz,
        np.where(valid & (model > 0.0), model, np.nan),
        color="#D55E00",
        lw=1.25,
        ls="--",
        label="Simulation + background",
    )
    m0_positive = np.r_[measured[valid & (measured > 0.0)], model[valid & (model > 0.0)]]
    if m0_positive.size == 0:
        raise ValueError("m=0 profile contains no positive values")
    m0_axis.set(
        xlim=(0.0, max(2.2, float(np.nanmax(qz[valid])))),
        ylim=(
            max(float(np.quantile(m0_positive, 0.002)) * 0.7, np.finfo(float).tiny),
            float(np.quantile(m0_positive, 0.998)) * 1.4,
        ),
        xlabel=r"$q_z$ ($\AA^{-1}$)",
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
        f"{case.label_math} | fixed {case.incidence_deg:g}° | continuous projected profiles | log scale\n"
        f"{case.archetype}; N={case.source_count}; one frozen scale reused throughout",
        fontsize=11.5,
    )
    figure.savefig(destination, dpi=220, facecolor="white")
    plt.close(figure)


def render_detector(
    case: MaterialCase,
    masks: dict[int, dict[str, np.ndarray]],
    m0_mask: np.ndarray,
    destination: Path,
) -> dict[str, Any]:
    signal = np.asarray(case.measured_count_per_px, dtype=np.float64)
    valid = np.asarray(case.detector_valid_mask, dtype=bool)
    display_rows = min(
        signal.shape[0],
        math.ceil(float(case.inputs.instrument.detector_reference_coordinate_px[1])),
    )
    shown = np.array(signal[:display_rows], copy=True)
    shown[~valid[:display_rows]] = np.nan
    positive = shown[np.isfinite(shown) & (shown > 0.0)]
    if positive.size == 0:
        raise ValueError("detector image contains no positive counts")
    low = max(float(np.quantile(positive, 0.005)), np.finfo(float).tiny)
    high = float(np.quantile(positive, 0.998))
    extent = (-0.5, signal.shape[1] - 0.5, display_rows - 0.5, -0.5)
    figure, axis = plt.subplots(figsize=(12.0, 6.6), layout="constrained")
    axis.imshow(
        shown,
        origin="upper",
        extent=extent,
        cmap="magma",
        norm=LogNorm(vmin=low, vmax=high, clip=True),
        interpolation="none",
        aspect="equal",
        rasterized=True,
    )
    overlays = [(m0_mask[:display_rows], "#56B4E9", 0.18)]
    for family, color in FAMILY_COLORS.items():
        overlays.extend(
            (
                (masks[family]["plus"][:display_rows], color, 0.22),
                (masks[family]["minus"][:display_rows], color, 0.22),
            )
        )
    overlay = np.zeros((display_rows, signal.shape[1], 4), dtype=np.float32)
    for mask, color, alpha in overlays:
        rgba = np.asarray(to_rgba(color, alpha), dtype=np.float32)
        empty = overlay[..., 3] == 0.0
        overlay[mask & empty] = rgba
        overlap = mask & ~empty
        overlay[overlap, :3] = 0.5 * (overlay[overlap, :3] + rgba[:3])
        overlay[overlap, 3] = np.maximum(overlay[overlap, 3], rgba[3])
    axis.imshow(
        overlay,
        origin="upper",
        extent=extent,
        interpolation="none",
        aspect="equal",
        rasterized=True,
    )
    axis.set(
        title=f"(a) Measured {case.image_id} detector with transparent integration regions",
        xlabel="detector column (px)",
        ylabel="detector row (px, top-origin)",
        xlim=(-0.5, signal.shape[1] - 0.5),
        ylim=(display_rows - 0.5, -0.5),
    )
    axis.legend(
        handles=(
            Patch(facecolor=to_rgba("#56B4E9", 0.30), edgecolor="none", label="m=0"),
            *(
                Patch(
                    facecolor=to_rgba(color, 0.35),
                    edgecolor="none",
                    label=f"m={family} +/-",
                )
                for family, color in FAMILY_COLORS.items()
            ),
        ),
        loc="upper right",
        ncol=2,
        frameon=True,
        facecolor="white",
        framealpha=0.88,
        fontsize=8,
    )
    axis.text(
        0.01,
        0.02,
        "Log detector color; transparent display-only fills; no contour strokes",
        transform=axis.transAxes,
        color="white",
        fontsize=8,
        bbox={"facecolor": "black", "alpha": 0.52, "edgecolor": "none", "pad": 2.5},
    )
    figure.savefig(destination, dpi=200, facecolor="white", bbox_inches="tight")
    plt.close(figure)
    return {
        "display_rows": display_rows,
        "log_vmin": low,
        "log_vmax": high,
        "region_rendering": (
            "inverse-chart detector-center classification rendered as transparent "
            "raster fills; no edges or contour strokes"
        ),
    }


def flattened_rgb(path: Path) -> Image.Image:
    source = Image.open(path).convert("RGBA")
    white = Image.new("RGBA", source.size, "white")
    return Image.alpha_composite(white, source).convert("RGB")


def resized_to_width(image: Image.Image, width: int) -> Image.Image:
    height = round(image.height * width / image.width)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def centered_text(
    draw: ImageDraw.ImageDraw, canvas_width: int, y: int, text: str, font: Any, fill: str
) -> None:
    bounds = draw.textbbox((0, 0), text, font=font)
    draw.text(((canvas_width - (bounds[2] - bounds[0])) / 2, y), text, font=font, fill=fill)


def compose_page(
    case: MaterialCase,
    detector_png: Path,
    profiles_png: Path,
) -> tuple[Path, Path]:
    stem = f"{case.key}_current_continuous_log"
    png = OUTPUT / f"{stem}.png"
    pdf = OUTPUT / f"{stem}.pdf"
    content_width = 2304
    detector = resized_to_width(flattened_rgb(detector_png), content_width)
    profiles = resized_to_width(flattened_rgb(profiles_png), content_width)
    header_height = 92
    footer_height = 82
    margin = 48
    gap = 24
    canvas_width = 2400
    height = header_height + detector.height + gap + profiles.height + footer_height
    canvas = Image.new("RGB", (canvas_width, height), "white")
    draw = ImageDraw.Draw(canvas)
    font_root = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
    title_font = ImageFont.truetype(str(font_root / "DejaVuSans-Bold.ttf"), 42)
    note_font = ImageFont.truetype(str(font_root / "DejaVuSans.ttf"), 19)
    centered_text(
        draw,
        canvas_width,
        18,
        f"{case.label_plain} | {case.archetype} | fixed detector and log-intensity profiles",
        title_font,
        "#1E242B",
    )
    y = header_height
    for image in (detector, profiles):
        canvas.paste(image, (margin, y))
        y += image.height + gap
    centered_text(
        draw,
        canvas_width,
        height - 59,
        f"PROVISIONAL: {case.model_status} | deterministic continuous region quadrature | "
        f"simulated background included",
        note_font,
        "#5A6169",
    )
    centered_text(
        draw,
        canvas_width,
        height - 34,
        case.background_note,
        note_font,
        "#5A6169",
    )
    canvas.save(png, format="PNG", dpi=(200, 200), optimize=True)
    canvas.save(
        pdf,
        format="PDF",
        resolution=200.0,
        quality=95,
        subsampling=0,
        title=f"{case.label_plain}: current continuous log profiles",
        author="SLATE-rMC",
    )
    return png, pdf


def render_case(
    case: MaterialCase,
    build_osc_angle_frame: Callable[..., Any] | None,
) -> dict[str, Any]:
    started = time.perf_counter()
    profiles, family_evidence = make_offspecular_profiles(case)
    if case.m0_profile is None:
        if build_osc_angle_frame is None:
            raise ValueError("case lacks an m=0 integration authority")
        m0, m0_evidence, m0_mask = make_structure_m0_profile(case, build_osc_angle_frame)
    else:
        m0 = case.m0_profile
        m0_evidence = dict(case.m0_profile.get("evidence", {}))
        m0_mask = np.asarray(case.m0_profile["detector_mask"], dtype=bool)
    masks, smooth_m0_mask, mask_evidence = region_masks(case, profiles, m0_mask)
    with tempfile.TemporaryDirectory(prefix=f"slate_{case.key}_") as temporary:
        detector_png = Path(temporary) / "detector.png"
        profiles_png = Path(temporary) / "profiles.png"
        detector_evidence = render_detector(case, masks, smooth_m0_mask, detector_png)
        render_profile_grid(case, profiles, m0, profiles_png)
        png, pdf = compose_page(case, detector_png, profiles_png)
    profile_arrays = {}
    for family in FAMILIES:
        for branch in BRANCHES:
            item = profiles[family][branch]
            prefix = f"m{family}_{branch}"
            for source, target in (
                ("qz_Ainv", "qz_Ainv"),
                ("measured", "measured_count_per_px"),
                ("background", "background_count_per_px"),
                ("diffraction_A2_per_px2", "diffraction_A2_per_px2"),
                ("model_total_count_per_px", "model_total_count_per_px"),
                ("valid", "valid"),
            ):
                profile_arrays[f"{prefix}_{target}"] = np.asarray(item[source])
    for key in (
        "qz_Ainv",
        "measured_count_per_px",
        "background_count_per_px",
        "diffraction_A2_per_px2",
        "model_total_count_per_px",
        "valid",
    ):
        profile_arrays[f"m0_{key}"] = np.asarray(m0[key])
    profile_path = HERE / f"{case.key}_continuous_profiles.npz"
    np.savez_compressed(profile_path, **profile_arrays)
    return {
        "case": case.key,
        "label": case.label_plain,
        "archetype": case.archetype,
        "image_id": case.image_id,
        "fixed_incidence_deg": case.incidence_deg,
        "raw_osc": file_record(Path(case.image_label)),
        "source_count": case.source_count,
        "scale_count_per_A2": case.scale_count_per_A2,
        "model_status": case.model_status,
        "background_policy": case.background_note,
        "offspecular_quadrature": {
            "coordinate": "qz_Ainv",
            "range_Ainv": [float(QZ_EDGES_AINV[0]), float(QZ_EDGES_AINV[-1])],
            "bin_count": int(QZ_EDGES_AINV.size - 1),
            "gauss_order": OFFSPECULAR_GAUSS_ORDER,
            "subdivisions": list(OFFSPECULAR_SUBDIVISIONS),
            "squared_fold_coordinate": True,
            "families": {str(key): value for key, value in family_evidence.items()},
        },
        "m0_quadrature": m0_evidence,
        "detector_display": detector_evidence,
        "mask_evidence": mask_evidence,
        "continuous_scans_used": False,
        "region_sampling": (
            "deterministic continuous detector-region quadrature; no Monte Carlo "
            "region sampling and no detector-pixel-center model sampling; frozen "
            "source averages retain their declared deterministic source sequences"
        ),
        "profile_archive": file_record(profile_path),
        "outputs": {"png": file_record(png), "pdf": file_record(pdf)},
        "wall_seconds": time.perf_counter() - started,
    }


def rerender_saved_case(
    case: MaterialCase,
    build_osc_angle_frame: Callable[..., Any] | None,
) -> dict[str, Any]:
    """Rerender saved continuous profiles without reevaluating diffraction physics."""

    started = time.perf_counter()
    profiles, m0, profile_path = load_saved_profiles(case)
    if case.m0_profile is not None:
        m0_mask = np.asarray(case.m0_profile["detector_mask"], dtype=bool)
    else:
        if build_osc_angle_frame is None:
            raise ValueError("case lacks an m=0 integration authority")
        angle_frame = build_angle_frame(case, build_osc_angle_frame)
        m0_mask, _ = angle_region_detector_mask(
            case,
            angle_frame,
            np.linspace(1.0, 30.0, 291),
            np.linspace(-10.0, 10.0, 81),
        )
    masks, smooth_m0_mask, mask_evidence = region_masks(case, profiles, m0_mask)
    with tempfile.TemporaryDirectory(prefix=f"slate_{case.key}_display_") as temporary:
        detector_png = Path(temporary) / "detector.png"
        profiles_png = Path(temporary) / "profiles.png"
        detector_evidence = render_detector(case, masks, smooth_m0_mask, detector_png)
        render_profile_grid(case, profiles, m0, profiles_png)
        png, pdf = compose_page(case, detector_png, profiles_png)
    return {
        "detector_display": detector_evidence,
        "mask_evidence": mask_evidence,
        "profile_archive": file_record(profile_path),
        "outputs": {"png": file_record(png), "pdf": file_record(pdf)},
        "display_rerender_seconds": time.perf_counter() - started,
    }


def combine_manifests() -> None:
    final_path = HERE / "all_materials_log_manifest.json"
    records: dict[str, dict[str, Any]] = {}
    provenance: dict[str, Any] = {}
    if final_path.exists():
        existing = json.loads(final_path.read_text(encoding="utf-8"))
        records.update({record["case"]: record for record in existing.get("records", [])})
        if set(existing.get("scope", [])) == {"gd1", "sid1"}:
            provenance["gd_sid"] = existing.get("provenance", {})
        elif isinstance(existing.get("provenance"), dict):
            provenance.update(existing["provenance"])
    for mode in ("clean1", "b4"):
        path = HERE / f"manifest_{mode}.json"
        payload = json.loads(path.read_text(encoding="utf-8"))
        records.update({record["case"]: record for record in payload["records"]})
        provenance[mode] = payload["provenance"]
    expected = ("gd1", "sid1", "clean1", "b4")
    missing = [key for key in expected if key not in records]
    if missing:
        raise ValueError(f"cannot combine manifests; missing {missing}")
    manifest = {
        "schema": "pbi2-all-materials-current-continuous-log.v2",
        "scope": list(expected),
        "plot_coordinate": "qz_Ainv; phase-neutral for mixed-polytype specimens",
        "shared_layout": "log detector, m=1-/+, m=3-/+, m=4-/+, full-width log m=0",
        "simulated_background_included": True,
        "continuous_scans_used": False,
        "provenance": provenance,
        "records": [records[key] for key in expected],
    }
    final_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(final_path, flush=True)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    if RUN_MODE == "combine":
        combine_manifests()
        return
    loaders = {
        "gd_sid": load_gd_sid_cases,
        "clean1": load_clean1_case,
        "b4": load_b4_case,
    }
    if RUN_MODE not in loaders:
        raise ValueError(f"unknown render mode {RUN_MODE!r}")
    cases, build_angle_frame_function, provenance = loaders[RUN_MODE]()
    manifest_path = HERE / f"manifest_{RUN_MODE}.json"
    if RERENDER_ONLY:
        combined_manifest = False
        if not manifest_path.is_file():
            if RUN_MODE != "gd_sid":
                raise FileNotFoundError(manifest_path)
            manifest_path = HERE / "all_materials_log_manifest.json"
            combined_manifest = True
            if not manifest_path.is_file():
                raise FileNotFoundError(manifest_path)
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        records_by_case = {record["case"]: record for record in manifest["records"]}
        for case in cases:
            print(f"{case.key}: display rerender starting", flush=True)
            records_by_case[case.key].update(
                rerender_saved_case(case, build_angle_frame_function)
            )
            print(f"{case.key}: display rerender complete", flush=True)
            gc.collect()
        if combined_manifest:
            manifest["provenance"]["gd_sid"] = provenance
            manifest["records"] = [
                records_by_case[record["case"]] for record in manifest["records"]
            ]
        else:
            manifest["provenance"] = provenance
            manifest["records"] = [records_by_case[case.key] for case in cases]
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(manifest_path, flush=True)
        return
    records = []
    for case in cases:
        print(f"{case.key}: starting", flush=True)
        records.append(render_case(case, build_angle_frame_function))
        print(f"{case.key}: complete", flush=True)
        gc.collect()
    manifest = {
        "schema": "pbi2-all-materials-current-continuous-log.v2",
        "scope": [case.key for case in cases],
        "plot_coordinate": "qz_Ainv; phase-neutral for mixed-polytype specimens",
        "shared_layout": "log detector, m=1-/+, m=3-/+, m=4-/+, full-width log m=0",
        "simulated_background_included": True,
        "continuous_scans_used": False,
        "provenance": provenance,
        "records": records,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(manifest_path, flush=True)


if __name__ == "__main__":
    main()
