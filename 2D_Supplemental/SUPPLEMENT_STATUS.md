# Supplement Status

Last updated: 2026-04-30  
Current supplement priority: support the main manuscript without interrupting the physics narrative.

## Supplement purpose

The supplement should contain implementation and validation details that are important for reproducibility but too technical for the main text.

The main text should explain the diffraction physics and show the measured/calculated agreement. The supplement should explain how the calculation was implemented efficiently and how additional checks support the model.

## Status definitions

| Status | Meaning |
|---|---|
| TODO | Section not written. |
| IN PROGRESS | Material exists or is partly drafted, but not supplement-ready. |
| DONE | Ready for advisor review. |
| PARKED | Deferred. |
| CHECK | Needs advisor decision. |

## Proposed supplement outline

### S1. Coordinate systems and projection implementation

Status: TODO

Include:

- detector space;
- 2theta-phi/caked-space representation;
- Q/Qr/Qz definitions;
- why the implementation uses 2theta-phi;
- how the same trajectory/projection is applied to data and calculation;
- why the projection is not an ideal perfect-Q measurement.

### S2. Sub-pixelation and binning

Status: TODO

Include:

- why curved Q/Qr/Qz trajectories create partial-pixel issues;
- why direct detector-space bin assignment can be jumpy/noisy;
- how sub-pixelation distributes intensity across transformed bins;
- confirmation that this is implementation, not new physics.

### S3. Beam and instrument sampling

Status: TODO

Use clear terminology. Prefer `sampled incident-ray state` over internal terms such as `beam phase`, unless the internal term is explicitly defined.

Include:

- beam position on sample;
- incident divergence;
- wavelength spread;
- detector projection;
- how finite experimental resolution contributes to line shape.

### S4. Monte Carlo optimization

Status: TODO

Include:

- why a dense tensor-product grid is slow;
- why discrete wavelength shells can cause sampling artifacts;
- how Monte Carlo sampling covers the same distributions more equitably;
- how the optimized method preserves the same physical model.

### S5. Mosaic-event sampling

Status: TODO

Include:

- sampling mosaic events from the mosaic-orientation distribution;
- reusing geometric intersections for multiple mosaic events;
- why this improves efficiency;
- validation that the optimization does not change the physics.

### S6. Two-component mosaicity and Lorentzian-tail checks

Status: TODO

Include:

- narrow central mosaic component;
- long-tail Lorentzian component;
- observed reflections that require the tail;
- optional comparison of model with/without tail;
- supplemental profile checks if too detailed for main text.

### S7. Full ordered-film peak-profile comparisons

Status: TODO

Include:

- expanded measured/calculated peak-profile comparisons for Bi2Se3 and Bi2Te3;
- plus/minus branches if relevant;
- reflection-family labels;
- all profiles that are too numerous for main text.

### S8. h-BN fitting method

Status: TODO

Include:

- what was fit;
- why h-BN was used or needed;
- what parameters were extracted;
- how the method connects to calibration/refinement workflow;
- whether it is calibration, validation, or separate analysis.

### S9. PbI2 diffuse scattering and stacking-disorder details

Status: PARKED

Potential contents later:

- selected rod masks;
- ordered baseline;
- diffuse residuals;
- stacking-fault analytical correction;
- fitted fault/slip probability;
- validation branch comparison.

## Supplement tasks

| Task | Status | Notes |
|---|---|---|
| Create supplement section structure | TODO | Decide how this integrates with existing `2D_Supplemental/SI_failure_modes.tex`. |
| Write S1 coordinate/projection section | TODO | Connect 2theta-phi back to Q/Qr/Qz. |
| Write S2 sub-pixelation section | TODO | Explain pixel-noise issue. |
| Write S3 beam/instrument sampling section | TODO | Use clear terminology. |
| Write S4 Monte Carlo optimization section | TODO | Keep physics and implementation separate. |
| Write S5 mosaic-event sampling section | TODO | Include validation that optimization preserves physics. |
| Write S6 Lorentzian-tail checks | TODO | Supports main-text mosaicity claim. |
| Write S7 full ordered-film profile comparisons | TODO | Good location for all peak profiles. |
| Write S8 h-BN fitting method | TODO | Needed if part of workflow. |
| Add PbI2 supplement details | PARKED | Later. |

## Draft language: implementation overview

The main text describes the analysis in terms of detector-space observables and reciprocal-space quantities Qr and Qz. In the implementation, detector intensity is transformed into a 2theta-phi representation before selected trajectories and integration bands are evaluated. This representation is convenient because Q, Qr, and Qz are derived from the same angular variables, and because sub-pixelated detector intensity can be binned consistently along curved trajectories. The transformation is used only to implement the projection efficiently; the physical comparison remains the measured and calculated intensity evaluated along the same specified trajectory.

## Draft language: Monte Carlo beam sampling

Finite beam size, incident divergence, and wavelength spread were included by sampling incident-ray states from the corresponding experimental distributions. Each sampled state specifies the beam position on the sample, the incident direction, and the wavelength. The scattered intensity is then accumulated over many sampled states. This Monte Carlo procedure replaces a dense tensor-product grid over the same variables and reduces oversampling artifacts associated with discrete wavelength shells while preserving the same physical resolution model.

## Draft language: mosaic-event sampling

For each sampled incident-ray state, the Ewald construction determines the reciprocal-space intersections that can contribute to the detector image. Mosaic disorder is represented by sampling events from the mosaic-orientation distribution associated with these intersections. Multiple mosaic events can be generated for a single sampled incident-ray state, allowing the same geometric intersection to be reused while sampling the mosaic distribution densely. This improves computational efficiency without changing the underlying mosaic model.

## Cautions

Do not imply that the optimized Monte Carlo method changes the physics. It is an implementation of the same physical model.

Do not introduce implementation terms without defining them.

Do not move the central Bi2Se3/Bi2Te3 fit evidence into the supplement. The main paper needs enough fit evidence to be convincing.
