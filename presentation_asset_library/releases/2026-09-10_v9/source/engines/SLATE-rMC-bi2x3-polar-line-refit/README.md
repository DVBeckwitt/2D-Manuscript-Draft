# SLATE-rMC

SLATE-rMC is a compact detector-native X-ray scattering core. It maps a configured incident beam,
CIF-derived reciprocal rods, mosaic probability, finite-stack structure strength, refraction, and
attenuation directly to a continuous detector-coordinate density and then integrates that density
over detector pixels.

The production path is continuous and deterministic. It does not construct an Ewald-sphere mesh,
sample an orientation cloud, create scattering-event rows, resample candidates, or deposit points
onto pixels. The Ewald sphere appears only through the elastic equation, solved analytically for
each rod and incident state.

## Quick start

Python 3.12 or 3.13 is required.

```powershell
uv sync --frozen --group dev --extra visualization
uv run python scripts/verify_seed.py
uv run pytest
```

The authoritative Bi2Se3 input is
[`configs/bi2se3_simulation.yaml`](configs/bi2se3_simulation.yaml). It controls the source, sample,
detector pose and both detector tilts, mosaic, finite 2H structure model, numerical backend, and
which external figures are rendered.

For fitting at selected continuous detector coordinates, contract v15 also accepts a general
layered CIF through `cif_conventional_cell_finite_repeat.v1` and the shared
`build_source_averaged_structure_detector(...)` boundary. Bi2Se3, Bi2Te3, ordered generic CIFs, and
the fixed five-parent PbI2 provider use the same sparse detector and rank-gated region fitter. The
optimized CPU/CUDA detector also evaluates exact complete-cell CIF repeats containing at most two
distinct element/charge factor groups; larger chemistries fail closed to the sparse path. A CIF alone
does not define observation regions, fit coordinates, background, mosaic, or stacking law. See
`docs/EXAMPLES.md` for the shared API and limitations.

Generic configured strength declaration:

```yaml
structure_factor:
  model_id: cif_conventional_cell_finite_repeat.v1
  repeats: 5
  normalization: FINITE_TOTAL
  unknown_u_iso_A2: 0.0
```

```powershell
uv run python scripts/run_configured_simulation.py configs/bi2se3_simulation.yaml
```

Generated figures and diagnostics must resolve outside the repository. Override the configured
destination with `--output-dir` when needed. Select `cpu` or `cuda` explicitly in the YAML; CUDA
fails clearly when no compatible device is available.

For a one-incident-state, native-pixel convergence diagnostic, use
`scripts/generate_bi2se3_continuous_detector.py`. Its omitted physical options inherit the same YAML
fixture, so there is only one default authority.

The real-OSC workflow core is modular and resumable. It fits positions first, optionally tests a
tightly bounded lattice change, combines that result with an explicitly provided mosaic state, and
then calibrates background and runs the A/B/C/joint structure fit. The same adapter and state
contracts serve the tracked Bi2Se3 and Bi2Te3 layered-quintuple recipes. Model evaluation stays
continuous; only measured OSC data and detector displays are pixel arrays. The measured pixels are
a piecewise-constant count field projected over the same continuous mixed-chart rectangles as the
model, with fractional-pixel covariance retained.

Current composition requires `rasim-fixed-mosaic-state-v2`, including the signed rod-local
orientation, coordinate, and probability-measure IDs. The tracked material-specific v1 mosaics and
single-film workflow cases are historical folded-law inputs and current code rejects them. See
`docs/EXAMPLES.md` for stage contracts and `tasks/28_bi2x3_polar_line_refit.md` for the current joint
Bi2X3 refit. Historical replay examples remain input-provenance references only.

## Interactive tools

All supported live viewers are collected in [`interactive/`](interactive/README.md):

```powershell
uv run --extra visualization python interactive/detector_viewer.py
uv run --extra visualization python interactive/ewald_sphere_viewer.py
```

The detector viewer provides continuous full-native Monte Carlo updates while parameters change.
The Ewald viewer synchronizes Bi2Se3 and Bi2Te3 Ewald spheres and detector planes at 5, 10, and 15
degrees. Their controls, backend choices, and scientific qualifications are documented beside the
entry points and in `docs/EXAMPLES.md`.

## Scientific contracts

- Internal angles are radians; distances are metres; wavelengths and crystal lengths are
  angstroms; wavevectors are inverse angstroms.
- Arrays are `[row, column]`; continuous detector coordinates are `(column_px, row_px)`.
- Every physical `(h,k)` rod is evaluated independently before an exact-family intensity sum.
- Source, phase, polarization, structure, mosaic, optical, Jacobian, and pixel-integration factors
  each have one owner and are applied once.
- Invalid rays carry explicit status and zero intensity.
- The pre-binned detector field is callable at arbitrary floating-point detector coordinates.
- Pixel values are deterministic box integrals, never display interpolation.

Read `AGENTS.md`, `docs/CONVENTIONS.md`, `docs/RESULT_MEASURE.md`, `docs/ARCHITECTURE.md`, and
`docs/CONTRACTS.md` before changing the numerical core. Compact proof commands and accepted
classifications are recorded in `docs/VALIDATION.md` and `docs/PHYSICS_LEDGER.md`.
