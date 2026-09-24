"""Joint fitting of heterogeneous detector-region observations."""

from __future__ import annotations

import hashlib
import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.linalg import cholesky, solve_triangular
from scipy.optimize import least_squares, minimize, nnls

from rasim_next.core.contracts import canonical_revision_sha256
from rasim_next.measurement.continuous_regions import ContinuousRegionQuadrature
from rasim_next.pipeline.bragg_space import StructureStrengthParameterization
from rasim_next.pipeline.source_averaged_structure import (
    SourceAveragedDetectorStructureResponse,
)

FloatArray = NDArray[np.float64]
IntArray = NDArray[np.int64]
BoolArray = NDArray[np.bool_]
_SHARED_INTENSITY_KKT_TOLERANCE = 1.0e-6


class _FunctionEvaluationLimit(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class FixedMatchedRegionBackground:
    """Frozen background correction, uncertainty, and anchor interpolation operator.

    The correction may be signed after dark subtraction and adjacent-anchor
    conditioning; it is never clipped before subtraction from the observation.
    """

    count_mass: ArrayLike
    covariance_count2: ArrayLike
    revision: str
    anchor_projection: ArrayLike | None = None

    def __post_init__(self) -> None:
        mass = np.array(self.count_mass, dtype=np.float64, copy=True, order="C")
        covariance = np.array(
            self.covariance_count2,
            dtype=np.float64,
            copy=True,
            order="C",
        )
        projection = (
            np.zeros((mass.size, mass.size), dtype=np.float64)
            if self.anchor_projection is None
            else np.array(self.anchor_projection, dtype=np.float64, copy=True, order="C")
        )
        covariance_eigenvalue = (
            np.linalg.eigvalsh(covariance)
            if covariance.shape == (mass.size, mass.size)
            else np.asarray((-math.inf,))
        )
        if (
            mass.ndim != 1
            or not mass.size
            or covariance.shape != (mass.size, mass.size)
            or projection.shape != (mass.size, mass.size)
            or np.any(~np.isfinite(mass))
            or np.any(~np.isfinite(covariance))
            or np.any(~np.isfinite(projection))
            or not np.allclose(covariance, covariance.T, rtol=0.0, atol=1.0e-10)
            or np.min(covariance_eigenvalue)
            < -1.0e-10 * max(float(np.max(np.abs(covariance_eigenvalue))), 1.0)
            or not isinstance(self.revision, str)
            or not self.revision
        ):
            raise ValueError("fixed matched-region background is invalid")
        mass.setflags(write=False)
        covariance.setflags(write=False)
        projection.setflags(write=False)
        object.__setattr__(self, "count_mass", mass)
        object.__setattr__(self, "covariance_count2", covariance)
        object.__setattr__(self, "anchor_projection", projection)


@dataclass(frozen=True, slots=True)
class MatchedRegionObservations:
    """Raw count masses grouped into complete signal/background blocks."""

    dataset_ids: tuple[str, ...]
    dataset_index: ArrayLike
    block_index: ArrayLike
    signal_family: ArrayLike
    is_background: ArrayLike
    count_mass: ArrayLike
    support_px2: ArrayLike
    background_coordinate: ArrayLike
    required_signal_families: tuple[int, ...]
    count_covariance_count2: ArrayLike | None = None

    def __post_init__(self) -> None:
        dataset_ids = tuple(self.dataset_ids)
        required = tuple(int(value) for value in self.required_signal_families)
        if (
            not dataset_ids
            or any(not isinstance(value, str) or not value for value in dataset_ids)
            or len(set(dataset_ids)) != len(dataset_ids)
        ):
            raise ValueError("dataset_ids must contain unique nonempty strings")
        if (
            not required
            or len(set(required)) != len(required)
            or any(value < 0 for value in required)
        ):
            raise ValueError("required_signal_families must contain unique nonnegative values")
        dataset = np.array(self.dataset_index, dtype=np.int64, copy=True, order="C")
        block = np.array(self.block_index, dtype=np.int64, copy=True, order="C")
        family = np.array(self.signal_family, dtype=np.int64, copy=True, order="C")
        background = np.array(self.is_background, dtype=np.bool_, copy=True, order="C")
        count = np.array(self.count_mass, dtype=np.float64, copy=True, order="C")
        support = np.array(self.support_px2, dtype=np.float64, copy=True, order="C")
        coordinate = np.array(
            self.background_coordinate,
            dtype=np.float64,
            copy=True,
            order="C",
        )
        shape = count.shape
        covariance_was_supplied = self.count_covariance_count2 is not None
        count_covariance = (
            np.diag(np.maximum(count, 1.0))
            if self.count_covariance_count2 is None
            else np.array(
                self.count_covariance_count2,
                dtype=np.float64,
                copy=True,
                order="C",
            )
        )
        covariance_eigenvalue = (
            np.linalg.eigvalsh(count_covariance)
            if count_covariance.shape == (count.size, count.size)
            else np.asarray((-math.inf,))
        )
        if (
            count.ndim != 1
            or not count.size
            or dataset.shape != shape
            or block.shape != shape
            or family.shape != shape
            or background.shape != shape
            or support.shape != shape
            or coordinate.shape != shape
            or count_covariance.shape != (count.size, count.size)
        ):
            raise ValueError("matched-region observation arrays must be aligned nonempty vectors")
        if (
            np.any((dataset < 0) | (dataset >= len(dataset_ids)))
            or np.any(block < 0)
            or np.any(~np.isfinite(count))
            or np.any(~np.isfinite(support))
            or np.any(support <= 0.0)
            or np.any(~np.isfinite(coordinate))
            or np.any(~np.isfinite(count_covariance))
            or not np.allclose(count_covariance, count_covariance.T, rtol=0.0, atol=1.0e-10)
            or np.min(covariance_eigenvalue)
            < -1.0e-10 * max(float(np.max(np.abs(covariance_eigenvalue))), 1.0)
            or np.any(background & (family != -1))
            or np.any((~background) & ~np.isin(family, required))
            or (not covariance_was_supplied and np.any(count < 0.0))
        ):
            raise ValueError("matched-region observations contain invalid values")
        unique_blocks = np.unique(block)
        if not np.array_equal(unique_blocks, np.arange(unique_blocks.size)):
            raise ValueError("block_index must be contiguous from zero")
        for block_id in unique_blocks:
            selected = block == block_id
            if np.unique(dataset[selected]).size != 1:
                raise ValueError("one background block cannot cross datasets")
            if np.count_nonzero(background[selected]) != 2 or not np.any(~background[selected]):
                raise ValueError("every block requires signals and exactly two background anchors")
            design = np.column_stack((support[selected], support[selected] * coordinate[selected]))
            if np.linalg.matrix_rank(design) != 2:
                raise ValueError("every block requires a rank-two affine background design")
        represented_globally = set(family[~background].tolist())
        missing = set(required) - represented_globally
        if missing:
            raise ValueError(f"joint observations lack signal families {sorted(missing)}")
        for value in (
            dataset,
            block,
            family,
            background,
            count,
            support,
            coordinate,
            count_covariance,
        ):
            value.setflags(write=False)
        object.__setattr__(self, "dataset_ids", dataset_ids)
        object.__setattr__(self, "dataset_index", dataset)
        object.__setattr__(self, "block_index", block)
        object.__setattr__(self, "signal_family", family)
        object.__setattr__(self, "is_background", background)
        object.__setattr__(self, "count_mass", count)
        object.__setattr__(self, "support_px2", support)
        object.__setattr__(self, "background_coordinate", coordinate)
        object.__setattr__(self, "required_signal_families", required)
        object.__setattr__(self, "count_covariance_count2", count_covariance)


@dataclass(frozen=True, slots=True)
class IntegratedPeakAreaProjection:
    """Fixed sum from conditioned signal bins to trusted detector-peak areas."""

    peak_ids: tuple[str, ...]
    peak_dataset_index: ArrayLike
    peak_signal_family: ArrayLike
    source_signal_peak_index: ArrayLike
    revision: str

    def __post_init__(self) -> None:
        peak_ids = tuple(self.peak_ids)
        dataset = np.array(self.peak_dataset_index, dtype=np.int64, copy=True, order="C")
        family = np.array(self.peak_signal_family, dtype=np.int64, copy=True, order="C")
        source_peak = np.array(
            self.source_signal_peak_index,
            dtype=np.int64,
            copy=True,
            order="C",
        )
        peak_count = len(peak_ids)
        if (
            not peak_ids
            or len(set(peak_ids)) != peak_count
            or any(not isinstance(value, str) or not value for value in peak_ids)
            or dataset.shape != (peak_count,)
            or family.shape != (peak_count,)
            or source_peak.ndim != 1
            or not source_peak.size
            or np.any(dataset < 0)
            or np.any(family < 0)
            or np.any((source_peak < 0) | (source_peak >= peak_count))
            or not np.array_equal(np.unique(source_peak), np.arange(peak_count))
            or not isinstance(self.revision, str)
            or not self.revision
        ):
            raise ValueError("integrated peak-area projection is invalid")
        for value in (dataset, family, source_peak):
            value.setflags(write=False)
        object.__setattr__(self, "peak_ids", peak_ids)
        object.__setattr__(self, "peak_dataset_index", dataset)
        object.__setattr__(self, "peak_signal_family", family)
        object.__setattr__(self, "source_signal_peak_index", source_peak)

    def aggregation_matrix(self, observations: MatchedRegionObservations) -> FloatArray:
        """Return the validated Boolean sum matrix in canonical signal-row order."""

        if not isinstance(observations, MatchedRegionObservations):
            raise TypeError("observations must be MatchedRegionObservations")
        signal = ~np.asarray(observations.is_background)
        source_peak = np.asarray(self.source_signal_peak_index)
        if source_peak.size != int(np.count_nonzero(signal)):
            raise ValueError("peak-area mapping does not cover every signal row exactly once")
        source_dataset = np.asarray(observations.dataset_index)[signal]
        source_family = np.asarray(observations.signal_family)[signal]
        peak_count = len(self.peak_ids)
        if np.any(np.asarray(self.peak_dataset_index) >= len(observations.dataset_ids)):
            raise ValueError("peak-area dataset index lies outside the observations")
        for peak_index in range(peak_count):
            selected = source_peak == peak_index
            if np.any(source_dataset[selected] != self.peak_dataset_index[peak_index]) or np.any(
                source_family[selected] != self.peak_signal_family[peak_index]
            ):
                raise ValueError("one integrated peak cannot cross datasets or signal families")
        matrix = np.zeros((peak_count, source_peak.size), dtype=np.float64)
        matrix[source_peak, np.arange(source_peak.size)] = 1.0
        matrix.setflags(write=False)
        return matrix


@dataclass(frozen=True, slots=True)
class MatchedRegionFitResult:
    """One joint solution with dataset scales and affine block backgrounds."""

    parameter_names: tuple[str, ...]
    parameters: FloatArray
    dataset_scales: FloatArray
    fitted_model_mass: FloatArray
    fitted_objective_model_mass: FloatArray
    fitted_background_mass: FloatArray
    fitted_signal_row: BoolArray
    weighted_residual: FloatArray
    objective_ids: tuple[str, ...]
    objective_dataset_index: IntArray
    objective_signal_family: IntArray
    prior_weighted_residual: FloatArray
    objective_half_chi_squared: float
    data_objective_half_chi_squared: float
    prior_objective_half_chi_squared: float
    jacobian_singular_values: FloatArray
    sensitivity_rank: int
    sensitivity_numerical_rank: int
    sensitivity_condition: float
    sensitivity_relative_tolerance: float
    penalized_jacobian_singular_values: FloatArray
    penalized_sensitivity_rank: int
    penalized_sensitivity_numerical_rank: int
    penalized_sensitivity_condition: float
    parameter_correlation: FloatArray
    success: bool
    optimizer_message: str
    function_evaluations: int


@dataclass(frozen=True, slots=True)
class SharedIntensityComponentFitResult:
    """One absolute-intensity solution shared by every reflection group."""

    component_coefficients: FloatArray
    component_fractions: FloatArray
    common_scale: float
    signal_prediction_count: FloatArray
    background_prediction_count: FloatArray
    background_coefficients: FloatArray
    standardized_residual: FloatArray
    component_singular_values: FloatArray
    component_sensitivity_condition: float
    equal_group_robust_cost: float
    sideband_weighted_rms: float
    success: bool
    optimizer_message: str
    function_evaluations: int


@dataclass(frozen=True, slots=True)
class StructureRegionResponseBlock:
    """One dataset's sparse detector transfer and exact region quadrature."""

    dataset_id: str
    response: SourceAveragedDetectorStructureResponse
    quadrature: ContinuousRegionQuadrature
    block_revision: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.dataset_id, str) or not self.dataset_id:
            raise ValueError("dataset_id must be a nonempty string")
        if not isinstance(self.response, SourceAveragedDetectorStructureResponse):
            raise TypeError("response must be SourceAveragedDetectorStructureResponse")
        if not isinstance(self.quadrature, ContinuousRegionQuadrature):
            raise TypeError("quadrature must be ContinuousRegionQuadrature")
        if not np.array_equal(
            self.response.column_px, self.quadrature.column_px
        ) or not np.array_equal(
            self.response.row_px,
            self.quadrature.row_px,
        ):
            raise ValueError("response coordinates and region quadrature must align exactly")
        if np.any(self.response.per_rod_caustic):
            raise ValueError("structure-region response cannot contain detector caustics")
        object.__setattr__(
            self,
            "block_revision",
            canonical_revision_sha256(
                ("definition_id", "structure_region_response_block.v1"),
                ("dataset_id", self.dataset_id),
                ("response_revision", self.response.response_revision),
                ("quadrature_revision", self.quadrature.quadrature_revision),
            ),
        )


@dataclass(frozen=True, slots=True)
class ParameterizedStructureRegionModel:
    """Shared structure parameters applied to fixed detector-region transfers."""

    parameterization: StructureStrengthParameterization
    blocks: tuple[StructureRegionResponseBlock, ...]
    parameter_names: tuple[str, ...] = field(init=False)
    parameter_units: tuple[str, ...] = field(init=False)
    reference_parameters: FloatArray = field(init=False)
    dataset_ids: tuple[str, ...] = field(init=False)
    observation_count: int = field(init=False)
    model_revision: str = field(init=False)

    def __post_init__(self) -> None:
        parameterization = self.parameterization
        names = tuple(getattr(parameterization, "parameter_names", ()))
        units = tuple(getattr(parameterization, "parameter_units", ()))
        reference = np.asarray(
            getattr(parameterization, "reference_parameters", ()), dtype=np.float64
        )
        parameterization_revision = getattr(parameterization, "parameterization_revision", None)
        reference_strength = getattr(parameterization, "reference_strength", None)
        reference_structure_revision = getattr(reference_strength, "structure_model_revision", None)
        if (
            not names
            or len(set(names)) != len(names)
            or len(units) != len(names)
            or reference.shape != (len(names),)
            or np.any(~np.isfinite(reference))
            or not isinstance(parameterization_revision, str)
            or len(parameterization_revision) != 64
            or not callable(getattr(parameterization, "bind_strength", None))
            or not isinstance(reference_structure_revision, str)
            or len(reference_structure_revision) != 64
        ):
            raise ValueError("structure-strength parameterization contract is incomplete")
        blocks = tuple(self.blocks)
        if not blocks or any(
            not isinstance(block, StructureRegionResponseBlock) for block in blocks
        ):
            raise ValueError("blocks must contain structure-region response blocks")
        observation_counts = {block.quadrature.observation_count for block in blocks}
        if len(observation_counts) != 1:
            raise ValueError("all structure-region blocks must share one observation row space")
        if any(
            block.response.reference_structure_model_revision != reference_structure_revision
            for block in blocks
        ):
            raise ValueError("response was compiled from a different reference structure model")
        dataset_ids = tuple(dict.fromkeys(block.dataset_id for block in blocks))
        frozen_reference = np.array(reference, copy=True)
        frozen_reference.setflags(write=False)
        model_revision = canonical_revision_sha256(
            ("definition_id", "parameterized_structure_region_model.v1"),
            ("parameterization_revision", parameterization_revision),
            ("block_revisions", tuple(block.block_revision for block in blocks)),
        )
        object.__setattr__(self, "blocks", blocks)
        object.__setattr__(self, "parameter_names", names)
        object.__setattr__(self, "parameter_units", units)
        object.__setattr__(self, "reference_parameters", frozen_reference)
        object.__setattr__(self, "dataset_ids", dataset_ids)
        object.__setattr__(self, "observation_count", observation_counts.pop())
        object.__setattr__(self, "model_revision", model_revision)

    def predict_mass_A2(self, parameters: ArrayLike) -> FloatArray:
        """Integrate one candidate structure over every fixed observation region."""

        candidate = self.parameterization.bind_strength(parameters)
        result = np.zeros(self.observation_count, dtype=np.float64)
        for block in self.blocks:
            density = block.response.apply_strength(candidate).density_A2_per_px2
            result += block.quadrature.integrate_density(density)
        if np.any(~np.isfinite(result)) or np.any(result < 0.0):
            raise FloatingPointError("parameterized structure model returned invalid mass")
        result.setflags(write=False)
        return result


@dataclass(frozen=True, slots=True)
class ParameterizedMatchedRegionFitResult:
    """Identifiable matched-region result bound to model and structure revisions."""

    fit: MatchedRegionFitResult
    model_revision: str
    parameterization_revision: str
    fitted_structure_model_revision: str
    maximum_sensitivity_condition: float


class StructureRegionIdentifiabilityError(RuntimeError):
    """Raised when a shared structure fit is not data-identifiable."""

    def __init__(self, message: str, result: MatchedRegionFitResult) -> None:
        super().__init__(message)
        self.result = result


def condition_matched_region_background_from_anchors(
    observations: MatchedRegionObservations,
    baseline: FixedMatchedRegionBackground,
) -> FixedMatchedRegionBackground:
    """Condition a frozen baseline on the two measured anchors in every block.

    The anchor residual above the baseline is treated as an affine density in
    the block coordinate.  Its prediction is frozen before structure fitting;
    anchor counting noise and baseline covariance are propagated into the
    resulting signal-background covariance.
    """

    if not isinstance(observations, MatchedRegionObservations):
        raise TypeError("observations must be MatchedRegionObservations")
    if not isinstance(baseline, FixedMatchedRegionBackground):
        raise TypeError("baseline must be FixedMatchedRegionBackground")
    count = np.asarray(observations.count_mass)
    if baseline.count_mass.shape != count.shape:
        raise ValueError("baseline background and observations must align")

    row_count = count.size
    conditioned_mass = np.array(baseline.count_mass, copy=True)
    if np.any(np.asarray(baseline.anchor_projection) != 0.0):
        raise ValueError("background baseline is already conditioned on anchors")
    baseline_transform = np.eye(row_count, dtype=np.float64)
    anchor_projection = np.zeros((row_count, row_count), dtype=np.float64)
    support = np.asarray(observations.support_px2)
    coordinate = np.asarray(observations.background_coordinate)
    is_background = np.asarray(observations.is_background)
    for block_id in range(int(np.max(observations.block_index)) + 1):
        index = np.flatnonzero(observations.block_index == block_id)
        anchor_local = np.flatnonzero(is_background[index])
        anchor_index = index[anchor_local]
        anchor_coordinate = coordinate[anchor_index]
        signal_coordinate = coordinate[index[~is_background[index]]]
        if (
            anchor_coordinate[0] == anchor_coordinate[1]
            or np.any(signal_coordinate < np.min(anchor_coordinate))
            or np.any(signal_coordinate > np.max(anchor_coordinate))
        ):
            raise ValueError("adjacent background anchors must bracket every signal coordinate")
        design = np.column_stack((support[index], support[index] * coordinate[index]))
        anchor_design = design[anchor_local]
        interpolation = np.linalg.solve(anchor_design.T, design.T).T
        residual_anchor_mass = count[anchor_index] - baseline.count_mass[anchor_index]
        conditioned_mass[index] += interpolation @ residual_anchor_mass

        selector = np.zeros((2, index.size), dtype=np.float64)
        selector[np.arange(2), anchor_local] = 1.0
        block_projection = interpolation @ selector
        anchor_projection[np.ix_(index, index)] = block_projection
        baseline_transform[np.ix_(index, index)] -= block_projection
    count_covariance = np.asarray(observations.count_covariance_count2)
    covariance = (
        baseline_transform @ np.asarray(baseline.covariance_count2) @ baseline_transform.T
        + anchor_projection @ count_covariance @ anchor_projection.T
    )
    covariance = 0.5 * (covariance + covariance.T)
    digest = hashlib.sha256()
    digest.update(b"matched-region-adjacent-affine-background.v1\0")
    digest.update(baseline.revision.encode("utf-8"))
    digest.update(np.ascontiguousarray(conditioned_mass).tobytes())
    digest.update(np.ascontiguousarray(covariance).tobytes())
    digest.update(np.ascontiguousarray(anchor_projection).tobytes())
    return FixedMatchedRegionBackground(
        count_mass=conditioned_mass,
        covariance_count2=covariance,
        revision=f"sha256-{digest.hexdigest()}.adjacent-affine.v1",
        anchor_projection=anchor_projection,
    )


def condition_matched_region_model_from_anchors(
    background: FixedMatchedRegionBackground,
    model_mass: ArrayLike,
) -> FloatArray:
    """Apply the data-side anchor subtraction operator to a diffraction model."""

    if not isinstance(background, FixedMatchedRegionBackground):
        raise TypeError("background must be FixedMatchedRegionBackground")
    model = np.asarray(model_mass, dtype=np.float64)
    if (
        model.shape != background.count_mass.shape
        or np.any(~np.isfinite(model))
        or np.any(model < 0.0)
    ):
        raise ValueError("model_mass must be a finite aligned nonnegative vector")
    return model - np.asarray(background.anchor_projection) @ model


def fit_shared_intensity_components(
    component_signal_count: ArrayLike,
    observed_count: ArrayLike,
    sigma_count: ArrayLike,
    signal_group_index: ArrayLike,
    background_design: ArrayLike,
    *,
    sideband_group_index: ArrayLike | None = None,
    initial_component_coefficients: Sequence[ArrayLike] = (),
    robust_scale: float = 2.5,
    maximum_component_condition: float = 1.0e8,
    maximum_function_evaluations: int = 400,
) -> SharedIntensityComponentFitResult:
    """Fit phase amounts with one common scale and sideband-profiled background.

    ``component_signal_count`` has shape ``(component, observation)``. Every row must
    be a unit-pure-component response on the same absolute normalization; rescaling one
    row independently changes the coefficient gauge and is outside this contract.
    Nonnegative component coefficients are shared by every nonnegative signal-group
    index; under that normalization, their sum is the common physical scale and their
    normalized values are phase fractions.
    Rows with group index ``-1`` are sidebands. At every candidate, only those rows
    determine the additive background after subtracting the candidate signal tails.
    Sideband residuals remain in the robust objective, grouped either together or by
    ``sideband_group_index``; they are not silently discarded after profiling.

    The objective is a descriptive robust score with a sideband-only weighted-least-
    squares nuisance profile. It is not a covariance-correct likelihood: uncertainty
    induced by estimating the background from those sidebands is not propagated, so
    the score and standardized residuals must not be used as chi-squared statistics or
    to construct parameter confidence intervals. ``maximum_function_evaluations`` is a
    per-start bound; ``function_evaluations`` reports the aggregate over every start.
    """

    supplied_component = np.asarray(component_signal_count)
    supplied_observed = np.asarray(observed_count)
    supplied_sigma = np.asarray(sigma_count)
    supplied_group = np.asarray(signal_group_index)
    supplied_design = np.asarray(background_design)
    if any(
        np.iscomplexobj(value)
        for value in (supplied_component, supplied_observed, supplied_sigma, supplied_design)
    ):
        raise ValueError("shared-intensity numeric arrays must be real")
    component = np.asarray(supplied_component, dtype=np.float64)
    observed = np.asarray(supplied_observed, dtype=np.float64)
    sigma = np.asarray(supplied_sigma, dtype=np.float64)
    design = np.asarray(supplied_design, dtype=np.float64)
    if supplied_group.ndim != 1 or not np.issubdtype(
        supplied_group.dtype,
        np.signedinteger,
    ):
        raise ValueError("signal_group_index must be a one-dimensional signed-integer vector")
    group = np.asarray(supplied_group, dtype=np.int64)
    if (
        component.ndim != 2
        or not component.shape[0]
        or observed.shape != (component.shape[1],)
        or sigma.shape != observed.shape
        or group.shape != observed.shape
        or design.ndim != 2
        or design.shape[0] != observed.size
        or not design.shape[1]
    ):
        raise ValueError("shared-intensity arrays are not aligned")
    if (
        np.any(~np.isfinite(component))
        or np.any(component < 0.0)
        or np.any(~np.isfinite(observed))
        or np.any(~np.isfinite(sigma))
        or np.any(sigma <= 0.0)
        or np.any(~np.isfinite(design))
        or np.any(group < -1)
    ):
        raise ValueError("shared-intensity arrays contain invalid values")
    signal = group >= 0
    sideband = group == -1
    represented_groups = np.unique(group[signal])
    if (
        not np.any(signal)
        or not np.any(sideband)
        or not np.array_equal(represented_groups, np.arange(represented_groups.size))
    ):
        raise ValueError("signal groups must be contiguous from zero and sidebands must be present")
    if sideband_group_index is None:
        sideband_group = np.full(observed.shape, -1, dtype=np.int64)
        sideband_group[sideband] = 0
    else:
        supplied_sideband_group = np.asarray(sideband_group_index)
        if supplied_sideband_group.ndim != 1 or not np.issubdtype(
            supplied_sideband_group.dtype, np.signedinteger
        ):
            raise ValueError("sideband_group_index must be a one-dimensional signed-integer vector")
        sideband_group = np.asarray(supplied_sideband_group, dtype=np.int64)
        if (
            sideband_group.shape != observed.shape
            or np.any(sideband_group[signal] != -1)
            or np.any(sideband_group[sideband] < 0)
        ):
            raise ValueError("sideband groups must identify exactly the sideband rows")
    represented_sideband_groups = np.unique(sideband_group[sideband])
    if not np.array_equal(
        represented_sideband_groups,
        np.arange(represented_sideband_groups.size),
    ):
        raise ValueError("sideband groups must be contiguous from zero")
    weighted_sideband_design = design[sideband] / sigma[sideband, None]
    background_relative_tolerance = 1.0e-12
    background_singular_values = np.linalg.svd(
        weighted_sideband_design,
        compute_uv=False,
    )
    background_tolerance = background_relative_tolerance * background_singular_values[0]
    if np.count_nonzero(background_singular_values > background_tolerance) != design.shape[1]:
        raise ValueError("sideband background design must have full rank at the declared tolerance")

    sideband_pseudoinverse = np.linalg.pinv(
        weighted_sideband_design,
        rcond=background_relative_tolerance,
    )
    background_intercept = sideband_pseudoinverse @ (observed[sideband] / sigma[sideband])
    background_component_response = sideband_pseudoinverse @ (
        component[:, sideband].T / sigma[sideband, None]
    )
    effective_component = component.T - design @ background_component_response
    standardized_component = effective_component / sigma[:, None]
    standardized_offset = (design @ background_intercept - observed) / sigma
    objective_group = np.array(group, copy=True)
    objective_group[sideband] = represented_groups.size + sideband_group[sideband]
    objective_group_count = represented_groups.size + represented_sideband_groups.size
    group_size = np.bincount(objective_group, minlength=objective_group_count)
    group_weight = 1.0 / (objective_group_count * group_size[objective_group])
    weighted_component = np.sqrt(group_weight[:, None]) * standardized_component
    component_maximum = np.max(np.abs(weighted_component), axis=0)
    component_norm = np.zeros(component.shape[0], dtype=np.float64)
    nonzero_component = component_maximum > 0.0
    component_norm[nonzero_component] = component_maximum[nonzero_component] * np.sqrt(
        np.sum(
            np.square(
                weighted_component[:, nonzero_component]
                / component_maximum[None, nonzero_component]
            ),
            axis=0,
        )
    )
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        direct_component_norm = np.sqrt(
            np.sum(group_weight[:, None] * np.square(standardized_component), axis=0)
        )
    direct_component_norm_is_safe = np.isfinite(direct_component_norm) & (
        (direct_component_norm > 0.0) | ~nonzero_component
    )
    component_norm[direct_component_norm_is_safe] = direct_component_norm[
        direct_component_norm_is_safe
    ]
    if np.any(component_norm <= np.finfo(np.float64).tiny):
        raise ValueError("every component must affect the sideband-conditioned signal")

    normalized_weighted_component = (
        np.sqrt(group_weight[:, None]) * standardized_component / component_norm[None, :]
    )
    component_left_singular_vectors, component_singular_values, _ = np.linalg.svd(
        normalized_weighted_component,
        full_matrices=False,
    )
    component_tolerance = (
        64.0
        * np.finfo(np.float64).eps
        * max(normalized_weighted_component.shape)
        * component_singular_values[0]
    )
    component_rank = int(np.count_nonzero(component_singular_values > component_tolerance))
    component_condition = (
        float(component_singular_values[0] / component_singular_values[-1])
        if component_rank == component.shape[0]
        else math.inf
    )
    maximum_condition = float(maximum_component_condition)
    if not math.isfinite(maximum_condition) or maximum_condition < 1.0:
        raise ValueError("maximum_component_condition must be finite and at least one")
    if component_rank != component.shape[0]:
        raise ValueError("shared-intensity component responses are rank deficient")
    if component_condition > maximum_condition:
        raise ValueError(
            "shared-intensity component sensitivity exceeds the declared condition limit"
        )

    scale_value = float(robust_scale)
    if isinstance(maximum_function_evaluations, bool) or not isinstance(
        maximum_function_evaluations,
        (int, np.integer),
    ):
        raise ValueError("maximum_function_evaluations must be a positive integer per start")
    maximum = int(maximum_function_evaluations)
    if not math.isfinite(scale_value) or scale_value <= 0.0:
        raise ValueError("robust_scale must be finite and positive")
    if maximum <= 0:
        raise ValueError("maximum_function_evaluations must be a positive integer per start")
    weighted_offset = np.sqrt(group_weight) * standardized_offset
    informative_offset = component_left_singular_vectors.T @ weighted_offset
    if np.any(~np.isfinite(informative_offset)):
        raise ValueError("shared-intensity component-projected offset is nonfinite")
    informative_maximum = float(np.max(np.abs(informative_offset)))
    informative_norm = (
        informative_maximum * float(np.linalg.norm(informative_offset / informative_maximum))
        if informative_maximum > 0.0
        else 0.0
    )
    offset_maximum = float(np.max(np.abs(weighted_offset)))
    offset_norm = (
        offset_maximum * float(np.linalg.norm(weighted_offset / offset_maximum))
        if offset_maximum > 0.0
        else 0.0
    )
    with np.errstate(over="ignore", under="ignore", invalid="ignore"):
        direct_offset_norm = float(np.sqrt(group_weight @ np.square(standardized_offset)))
    if math.isfinite(direct_offset_norm) and (direct_offset_norm > 0.0 or offset_maximum == 0.0):
        offset_norm = direct_offset_norm
    informative_scale = max(informative_norm, 1.0)
    offset_is_component_uninformative = offset_norm / informative_scale > 1.0e8
    target_scale = informative_scale if offset_is_component_uninformative else max(offset_norm, 1.0)
    coefficient_scale = target_scale / component_norm
    scaled_component = standardized_component * coefficient_scale[None, :]

    def objective_and_gradient(scaled_coefficients: FloatArray) -> tuple[float, FloatArray]:
        residual = standardized_offset + scaled_component @ scaled_coefficients
        absolute_residual = np.abs(residual)
        small = absolute_residual <= scale_value
        conjugate_ratio = np.empty_like(residual)
        normalized_small = residual[small] / scale_value
        conjugate_ratio[small] = normalized_small / (np.hypot(1.0, normalized_small) + 1.0)
        normalized_large = scale_value / absolute_residual[~small]
        conjugate_ratio[~small] = np.sign(residual[~small]) / (
            np.hypot(1.0, normalized_large) + normalized_large
        )
        loss = 2.0 * (scale_value * (residual * conjugate_ratio))
        derivative = 2.0 * (scale_value * (residual / np.hypot(scale_value, residual)))
        with np.errstate(over="ignore", under="ignore", invalid="ignore"):
            normalized = residual / scale_value
        direct_scale_is_safe = (
            math.sqrt(np.finfo(np.float64).tiny)
            <= scale_value
            <= math.sqrt(np.finfo(np.float64).max / 2.0)
        )
        direct = (
            direct_scale_is_safe
            & np.isfinite(normalized)
            & (np.abs(normalized) >= 1.0e-4)
            & (np.abs(normalized) <= 1.0e150)
        )
        direct_root = np.sqrt(1.0 + np.square(normalized[direct]))
        loss[direct] = 2.0 * scale_value * scale_value * (direct_root - 1.0)
        derivative[direct] = 2.0 * residual[direct] / direct_root
        return (
            float(group_weight @ loss),
            scaled_component.T @ (group_weight * derivative),
        )

    linear_weight = np.sqrt(group_weight)
    linear_target = (
        -(component_left_singular_vectors @ informative_offset)
        if offset_is_component_uninformative
        else -weighted_offset
    )
    nnls_start, _ = nnls(
        linear_weight[:, None] * scaled_component,
        linear_target,
    )
    starts = [nnls_start]
    for supplied in initial_component_coefficients:
        if np.iscomplexobj(np.asarray(supplied)):
            raise ValueError("initial component coefficients must be real")
        values = np.asarray(supplied, dtype=np.float64)
        if (
            values.shape != (component.shape[0],)
            or np.any(~np.isfinite(values))
            or np.any(values < 0.0)
        ):
            raise ValueError("initial component coefficients must be finite and nonnegative")
        starts.append(values / coefficient_scale)
    attempts: list[tuple[bool, float, FloatArray, str, int]] = []
    for start in starts:
        evaluations = 0
        best_cost = math.inf
        best_scaled_coefficients = np.array(start, copy=True)
        best_gradient = np.full(component.shape[0], math.inf, dtype=np.float64)

        def counted_objective(candidate: FloatArray) -> tuple[float, FloatArray]:
            nonlocal evaluations, best_cost, best_scaled_coefficients, best_gradient
            if evaluations >= maximum:
                raise _FunctionEvaluationLimit
            cost, gradient = objective_and_gradient(candidate)
            evaluations += 1
            if cost < best_cost:
                best_cost = cost
                best_scaled_coefficients = np.array(candidate, copy=True)
                best_gradient = np.array(gradient, copy=True)
            return cost, gradient

        try:
            optimized = minimize(
                counted_objective,
                start,
                jac=True,
                method="L-BFGS-B",
                bounds=((0.0, None),) * component.shape[0],
                options={
                    "ftol": 1.0e-14,
                    "gtol": 1.0e-10,
                    "maxfun": maximum,
                    "maxiter": maximum,
                },
            )
            success = bool(optimized.success)
            message = str(optimized.message)
            if success:
                best_cost = float(optimized.fun)
                best_scaled_coefficients = np.asarray(optimized.x, dtype=np.float64)
                best_gradient = np.asarray(optimized.jac, dtype=np.float64)
        except _FunctionEvaluationLimit:
            success = False
            message = "per-start function-evaluation limit reached"
        projected_gradient = np.where(
            (best_scaled_coefficients > 0.0) | (best_gradient < 0.0),
            best_gradient,
            0.0,
        )
        projected_gradient_maximum = float(np.max(np.abs(projected_gradient)))
        if success and projected_gradient_maximum > _SHARED_INTENSITY_KKT_TOLERANCE:
            success = False
            message = (
                "independent nonnegative KKT gate failed: "
                f"{projected_gradient_maximum:.17g} > "
                f"{_SHARED_INTENSITY_KKT_TOLERANCE:.17g}"
            )
        attempts.append((success, best_cost, best_scaled_coefficients, message, evaluations))
    successful = tuple(attempt for attempt in attempts if attempt[0])
    selected = min(successful or attempts, key=lambda attempt: attempt[1])
    coefficients = coefficient_scale * selected[2]
    coefficient_maximum = float(np.max(coefficients))
    if not math.isfinite(selected[1]) or np.any(~np.isfinite(coefficients)):
        raise ValueError("shared-intensity fit produced a nonfinite solution")
    if coefficient_maximum <= 0.0:
        raise ValueError("shared-intensity fit has no positive common scale")
    normalized_coefficient_sum = float(np.sum(coefficients / coefficient_maximum))
    if coefficient_maximum > np.finfo(np.float64).max / normalized_coefficient_sum:
        raise ValueError("shared-intensity fit has no finite common scale")
    common_scale = coefficient_maximum * normalized_coefficient_sum
    if common_scale <= np.finfo(np.float64).tiny:
        raise ValueError("shared-intensity fit has no positive common scale")
    with np.errstate(over="ignore", invalid="ignore"):
        background_coefficients = (
            background_intercept - background_component_response @ coefficients
        )
        signal_prediction = component.T @ coefficients
        background_prediction = design @ background_coefficients
        residual = (signal_prediction + background_prediction - observed) / sigma
    fractions = coefficients / common_scale
    if any(
        np.any(~np.isfinite(value))
        for value in (
            fractions,
            signal_prediction,
            background_prediction,
            background_coefficients,
            residual,
        )
    ):
        raise ValueError("shared-intensity fit produced a nonfinite prediction")
    for value in (
        coefficients,
        fractions,
        signal_prediction,
        background_prediction,
        background_coefficients,
        residual,
        component_singular_values,
    ):
        value.setflags(write=False)
    sideband_residual = residual[sideband]
    sideband_residual_maximum = float(np.max(np.abs(sideband_residual)))
    sideband_weighted_rms = (
        sideband_residual_maximum
        * float(
            np.linalg.norm(sideband_residual / sideband_residual_maximum)
            / math.sqrt(sideband_residual.size)
        )
        if sideband_residual_maximum > 0.0
        else 0.0
    )
    if not math.isfinite(sideband_weighted_rms):
        raise ValueError("shared-intensity fit produced a nonfinite sideband RMS")
    return SharedIntensityComponentFitResult(
        component_coefficients=coefficients,
        component_fractions=fractions,
        common_scale=common_scale,
        signal_prediction_count=signal_prediction,
        background_prediction_count=background_prediction,
        background_coefficients=background_coefficients,
        standardized_residual=residual,
        component_singular_values=component_singular_values,
        component_sensitivity_condition=component_condition,
        equal_group_robust_cost=selected[1],
        sideband_weighted_rms=sideband_weighted_rms,
        success=selected[0],
        optimizer_message=selected[3],
        function_evaluations=sum(attempt[4] for attempt in attempts),
    )


def profile_matched_region_nuisance(
    model_mass: ArrayLike,
    observations: MatchedRegionObservations,
    fixed_background: FixedMatchedRegionBackground,
    *,
    peak_area_projection: IntegratedPeakAreaProjection | None = None,
) -> tuple[FloatArray, FloatArray, FloatArray]:
    """Profile dataset scales against one frozen conditioned background."""

    if not isinstance(observations, MatchedRegionObservations):
        raise TypeError("observations must be MatchedRegionObservations")
    model = np.asarray(model_mass, dtype=np.float64)
    count = np.asarray(observations.count_mass)
    if model.shape != count.shape or not np.all(np.isfinite(model)) or np.any(model < 0.0):
        raise ValueError("model_mass must be a finite nonnegative aligned vector")
    if not isinstance(fixed_background, FixedMatchedRegionBackground):
        raise TypeError("fixed_background must be FixedMatchedRegionBackground")
    if fixed_background.count_mass.shape != count.shape:
        raise ValueError("fixed background and observations must align")
    signal = ~np.asarray(observations.is_background)
    signal_index = np.flatnonzero(signal)
    count_covariance = np.asarray(observations.count_covariance_count2)
    anchor_projection = np.asarray(fixed_background.anchor_projection)
    covariance = (
        count_covariance
        + np.asarray(fixed_background.covariance_count2)
        - anchor_projection @ count_covariance
        - count_covariance @ anchor_projection.T
    )
    covariance = covariance[np.ix_(signal_index, signal_index)]
    covariance = 0.5 * (covariance + covariance.T)
    conditioned_model = condition_matched_region_model_from_anchors(fixed_background, model)
    corrected = count[signal] - fixed_background.count_mass[signal]
    model_signal = conditioned_model[signal]
    if peak_area_projection is None:
        objective_dataset = np.asarray(observations.dataset_index)[signal]
    else:
        if not isinstance(peak_area_projection, IntegratedPeakAreaProjection):
            raise TypeError("peak_area_projection must be IntegratedPeakAreaProjection")
        aggregation = peak_area_projection.aggregation_matrix(observations)
        corrected = aggregation @ corrected
        model_signal = aggregation @ model_signal
        covariance = aggregation @ covariance @ aggregation.T
        covariance = 0.5 * (covariance + covariance.T)
        objective_dataset = np.asarray(peak_area_projection.peak_dataset_index)
    root_covariance = cholesky(covariance, lower=True, check_finite=False)
    design = np.zeros((corrected.size, len(observations.dataset_ids)), dtype=np.float64)
    design[np.arange(corrected.size), objective_dataset] = model_signal
    whitened_count = solve_triangular(
        root_covariance,
        corrected,
        lower=True,
        check_finite=False,
    )
    whitened_design = solve_triangular(
        root_covariance,
        design,
        lower=True,
        check_finite=False,
    )
    if np.any(np.linalg.norm(whitened_design, axis=0) <= np.finfo(np.float64).tiny):
        raise ValueError("candidate model has no scale-identifying signal in one dataset")
    scales, _ = nnls(whitened_design, whitened_count)
    objective_residual = whitened_count - whitened_design @ scales
    if peak_area_projection is None:
        residual = np.zeros_like(count)
        residual[signal] = objective_residual
    else:
        residual = objective_residual
    return residual, scales, np.array(fixed_background.count_mass, copy=True)


def fit_matched_regions(
    observations: MatchedRegionObservations,
    predict_model_mass: Callable[[FloatArray], ArrayLike],
    *,
    fixed_background: FixedMatchedRegionBackground,
    parameter_names: Sequence[str],
    initial_parameters: Sequence[ArrayLike],
    lower_bounds: ArrayLike,
    upper_bounds: ArrayLike,
    parameter_scales: ArrayLike | None = None,
    prior_residual: Callable[[FloatArray], ArrayLike] | None = None,
    peak_area_projection: IntegratedPeakAreaProjection | None = None,
    sensitivity_relative_tolerance: float = 1.0e-5,
    maximum_function_evaluations: int = 200,
) -> MatchedRegionFitResult:
    """Fit one parameter vector to every family and dataset simultaneously."""

    if not isinstance(observations, MatchedRegionObservations):
        raise TypeError("observations must be MatchedRegionObservations")
    names = tuple(parameter_names)
    if not names or any(not isinstance(name, str) or not name for name in names):
        raise ValueError("parameter_names must contain nonempty strings")
    lower = np.asarray(lower_bounds, dtype=np.float64)
    upper = np.asarray(upper_bounds, dtype=np.float64)
    if (
        lower.shape != (len(names),)
        or upper.shape != lower.shape
        or np.any(~np.isfinite(lower))
        or np.any(~np.isfinite(upper))
        or np.any(lower >= upper)
    ):
        raise ValueError("parameter bounds must be aligned, finite, and increasing")
    starts = tuple(np.asarray(value, dtype=np.float64) for value in initial_parameters)
    if not starts or any(
        value.shape != lower.shape or np.any(value < lower) or np.any(value > upper)
        for value in starts
    ):
        raise ValueError("initial parameters must lie inside the declared bounds")
    maximum = int(maximum_function_evaluations)
    if maximum <= 0:
        raise ValueError("maximum_function_evaluations must be positive")
    relative_tolerance = float(sensitivity_relative_tolerance)
    if (
        not math.isfinite(relative_tolerance)
        or relative_tolerance <= 0.0
        or relative_tolerance >= 1.0
    ):
        raise ValueError("sensitivity_relative_tolerance must lie strictly between zero and one")
    if parameter_scales is None:
        parameter_coordinate_scales = np.ones(len(names), dtype=np.float64)
        optimizer_scales: FloatArray | str = "jac"
    else:
        parameter_coordinate_scales = np.asarray(parameter_scales, dtype=np.float64)
        if (
            parameter_coordinate_scales.shape != lower.shape
            or np.any(~np.isfinite(parameter_coordinate_scales))
            or np.any(parameter_coordinate_scales <= 0.0)
        ):
            raise ValueError("parameter_scales must be aligned, finite, and positive")
        optimizer_scales = parameter_coordinate_scales

    def evaluated_prior(parameters: FloatArray) -> FloatArray:
        if prior_residual is None:
            return np.empty(0, dtype=np.float64)
        values = np.asarray(prior_residual(parameters), dtype=np.float64)
        if values.ndim != 1 or np.any(~np.isfinite(values)):
            raise ValueError("prior_residual must return one finite vector")
        return values

    prior_size = evaluated_prior(starts[0]).size
    if any(evaluated_prior(start).size != prior_size for start in starts[1:]):
        raise ValueError("prior_residual shape must be parameter independent")

    def data_residual(parameters: FloatArray) -> FloatArray:
        model = np.asarray(predict_model_mass(parameters), dtype=np.float64)
        values, _, _ = profile_matched_region_nuisance(
            model,
            observations,
            fixed_background,
            peak_area_projection=peak_area_projection,
        )
        return values[~observations.is_background] if peak_area_projection is None else values

    def residual(parameters: FloatArray) -> FloatArray:
        return np.concatenate((data_residual(parameters), evaluated_prior(parameters)))

    fitted = tuple(
        least_squares(
            residual,
            start,
            bounds=(lower, upper),
            max_nfev=maximum,
            x_scale=optimizer_scales,
        )
        for start in starts
    )
    selected = min(fitted, key=lambda result: float(result.cost))
    model = np.asarray(predict_model_mass(selected.x), dtype=np.float64)
    weighted_residual, dataset_scales, background = profile_matched_region_nuisance(
        model,
        observations,
        fixed_background,
        peak_area_projection=peak_area_projection,
    )
    signal_row = ~np.asarray(observations.is_background)
    data_weighted_residual = (
        weighted_residual[signal_row] if peak_area_projection is None else weighted_residual
    )
    data_row_count = data_weighted_residual.size
    data_jacobian = (
        np.asarray(selected.jac[:data_row_count], dtype=np.float64)
        * parameter_coordinate_scales[None, :]
    )
    penalized_jacobian = (
        np.asarray(selected.jac, dtype=np.float64) * parameter_coordinate_scales[None, :]
    )

    def diagnostics(jacobian: FloatArray) -> tuple[FloatArray, int, int, float]:
        singular = np.linalg.svd(jacobian, compute_uv=False)
        if singular.size < len(names):
            singular = np.pad(singular, (0, len(names) - singular.size))
        if not singular.size or singular[0] == 0.0:
            return singular, 0, 0, math.inf
        numerical_tolerance = 64.0 * np.finfo(np.float64).eps * max(jacobian.shape) * singular[0]
        practical_tolerance = max(
            numerical_tolerance,
            relative_tolerance * singular[0],
        )
        numerical_rank = int(np.count_nonzero(singular > numerical_tolerance))
        practical_rank = int(np.count_nonzero(singular >= practical_tolerance))
        condition = (
            float(singular[0] / singular[-1])
            if numerical_rank == len(names) and singular[-1] > 0.0
            else math.inf
        )
        return singular, practical_rank, numerical_rank, condition

    singular_values, rank, numerical_rank, condition = diagnostics(data_jacobian)
    penalized_singular, penalized_rank, penalized_numerical_rank, penalized_condition = diagnostics(
        penalized_jacobian
    )
    if rank == len(names):
        covariance = np.linalg.inv(data_jacobian.T @ data_jacobian)
        standard_deviation = np.sqrt(np.diag(covariance))
        correlation = covariance / np.outer(standard_deviation, standard_deviation)
    else:
        correlation = np.full((len(names), len(names)), np.nan, dtype=np.float64)
    prior_weighted_residual = evaluated_prior(np.asarray(selected.x, dtype=np.float64))
    data_objective = 0.5 * float(data_weighted_residual @ data_weighted_residual)
    prior_objective = 0.5 * float(prior_weighted_residual @ prior_weighted_residual)
    frozen = (
        np.array(selected.x, copy=True),
        np.array(dataset_scales, copy=True),
        np.array(dataset_scales[np.asarray(observations.dataset_index)] * model, copy=True),
        np.array(
            dataset_scales[np.asarray(observations.dataset_index)]
            * condition_matched_region_model_from_anchors(fixed_background, model),
            copy=True,
        ),
        np.array(background, copy=True),
        np.array(
            signal_row
            if peak_area_projection is None
            else np.ones(len(peak_area_projection.peak_ids), dtype=np.bool_),
            copy=True,
        ),
        np.array(weighted_residual, copy=True),
        np.array(prior_weighted_residual, copy=True),
        np.array(singular_values, copy=True),
        np.array(penalized_singular, copy=True),
        np.array(correlation, copy=True),
        np.array(
            np.asarray(observations.dataset_index)[signal_row]
            if peak_area_projection is None
            else peak_area_projection.peak_dataset_index,
            copy=True,
        ),
        np.array(
            np.asarray(observations.signal_family)[signal_row]
            if peak_area_projection is None
            else peak_area_projection.peak_signal_family,
            copy=True,
        ),
    )
    for value in frozen:
        value.setflags(write=False)
    return MatchedRegionFitResult(
        parameter_names=names,
        parameters=frozen[0],
        dataset_scales=frozen[1],
        fitted_model_mass=frozen[2],
        fitted_objective_model_mass=frozen[3],
        fitted_background_mass=frozen[4],
        fitted_signal_row=frozen[5],
        weighted_residual=frozen[6],
        objective_ids=(
            tuple(f"signal-row:{index}" for index in np.flatnonzero(signal_row))
            if peak_area_projection is None
            else peak_area_projection.peak_ids
        ),
        objective_dataset_index=frozen[11],
        objective_signal_family=frozen[12],
        prior_weighted_residual=frozen[7],
        objective_half_chi_squared=data_objective + prior_objective,
        data_objective_half_chi_squared=data_objective,
        prior_objective_half_chi_squared=prior_objective,
        jacobian_singular_values=frozen[8],
        sensitivity_rank=rank,
        sensitivity_numerical_rank=numerical_rank,
        sensitivity_condition=condition,
        sensitivity_relative_tolerance=relative_tolerance,
        penalized_jacobian_singular_values=frozen[9],
        penalized_sensitivity_rank=penalized_rank,
        penalized_sensitivity_numerical_rank=penalized_numerical_rank,
        penalized_sensitivity_condition=penalized_condition,
        parameter_correlation=frozen[10],
        success=bool(selected.success),
        optimizer_message=str(selected.message),
        function_evaluations=int(sum(result.nfev for result in fitted)),
    )


def fit_parameterized_matched_regions(
    observations: MatchedRegionObservations,
    model: ParameterizedStructureRegionModel,
    *,
    fixed_background: FixedMatchedRegionBackground,
    initial_parameters: Sequence[ArrayLike],
    lower_bounds: ArrayLike,
    upper_bounds: ArrayLike,
    parameter_scales: ArrayLike | None = None,
    prior_residual: Callable[[FloatArray], ArrayLike] | None = None,
    peak_area_projection: IntegratedPeakAreaProjection | None = None,
    sensitivity_relative_tolerance: float = 1.0e-5,
    maximum_sensitivity_condition: float = 1.0e5,
    maximum_function_evaluations: int = 200,
) -> ParameterizedMatchedRegionFitResult:
    """Fit one shared structure model and reject non-identifiable data directions."""

    if not isinstance(observations, MatchedRegionObservations):
        raise TypeError("observations must be MatchedRegionObservations")
    if not isinstance(model, ParameterizedStructureRegionModel):
        raise TypeError("model must be ParameterizedStructureRegionModel")
    if parameter_scales is None:
        raise ValueError(
            "parameter_scales are required for coordinate-invariant structure identifiability"
        )
    maximum_condition = float(maximum_sensitivity_condition)
    if not math.isfinite(maximum_condition) or maximum_condition < 1.0:
        raise ValueError("maximum_sensitivity_condition must be finite and at least one")
    if observations.count_mass.size != model.observation_count:
        raise ValueError("observations and structure-region model row spaces differ")
    if set(observations.dataset_ids) != set(model.dataset_ids):
        raise ValueError("observations and structure-region model dataset IDs differ")
    dataset_index_by_id = {
        dataset_id: index for index, dataset_id in enumerate(observations.dataset_ids)
    }
    for block in model.blocks:
        covered = block.quadrature.observation_covered
        if np.any(
            np.asarray(observations.dataset_index)[covered] != dataset_index_by_id[block.dataset_id]
        ):
            raise ValueError("one structure-region block crosses dataset observation rows")

    result = fit_matched_regions(
        observations,
        model.predict_mass_A2,
        fixed_background=fixed_background,
        parameter_names=model.parameter_names,
        initial_parameters=initial_parameters,
        lower_bounds=lower_bounds,
        upper_bounds=upper_bounds,
        parameter_scales=parameter_scales,
        prior_residual=prior_residual,
        peak_area_projection=peak_area_projection,
        sensitivity_relative_tolerance=sensitivity_relative_tolerance,
        maximum_function_evaluations=maximum_function_evaluations,
    )
    parameter_count = len(model.parameter_names)
    if not result.success:
        raise StructureRegionIdentifiabilityError(
            f"structure optimizer failed: {result.optimizer_message}",
            result,
        )
    if (
        result.sensitivity_rank != parameter_count
        or result.sensitivity_numerical_rank != parameter_count
    ):
        raise StructureRegionIdentifiabilityError(
            "structure sensitivity is rank deficient "
            f"({result.sensitivity_rank}/{parameter_count})",
            result,
        )
    if (
        not math.isfinite(result.sensitivity_condition)
        or result.sensitivity_condition > maximum_condition
    ):
        raise StructureRegionIdentifiabilityError(
            "structure sensitivity condition exceeds the declared maximum",
            result,
        )
    fitted_strength = model.parameterization.bind_strength(result.parameters)
    fitted_revision = getattr(fitted_strength, "structure_model_revision", None)
    if not isinstance(fitted_revision, str) or len(fitted_revision) != 64:
        raise RuntimeError("fitted structure provider omitted its model revision")
    return ParameterizedMatchedRegionFitResult(
        fit=result,
        model_revision=model.model_revision,
        parameterization_revision=model.parameterization.parameterization_revision,
        fitted_structure_model_revision=fitted_revision,
        maximum_sensitivity_condition=maximum_condition,
    )


__all__ = [
    "FixedMatchedRegionBackground",
    "IntegratedPeakAreaProjection",
    "MatchedRegionFitResult",
    "MatchedRegionObservations",
    "ParameterizedMatchedRegionFitResult",
    "ParameterizedStructureRegionModel",
    "SharedIntensityComponentFitResult",
    "StructureRegionIdentifiabilityError",
    "StructureRegionResponseBlock",
    "condition_matched_region_background_from_anchors",
    "condition_matched_region_model_from_anchors",
    "fit_matched_regions",
    "fit_parameterized_matched_regions",
    "fit_shared_intensity_components",
    "profile_matched_region_nuisance",
]
