# Figure Status

Last updated: 2026-05-12
Current figure priority: Bi2Se3 and Bi2Te3 ordered-film figures, plus the newly added mosaic-motivation and correlated-effects placeholders requested after the advisor discussion.

## Status definitions

| Status | Meaning |
|---|---|
| TODO | Figure does not exist or is not yet planned clearly. |
| IN PROGRESS | Figure exists in some form, but is incomplete, unclear, or not manuscript-ready. |
| DONE | Figure is inserted into the manuscript and ready for advisor review. |
| PARKED | Figure is useful but deferred. |
| CHECK | Needs advisor decision or notation review. |

## Advisor figure guidance

Figures need to show data. Do not let annotations, Bragg-position circles, colored paths, or internal labels obscure the measured detector intensity.

The ordered-film result should be figure-driven. The reader should be able to see that the model fits the measured data without needing to understand the software implementation.

Use Q, Qr, Qz, the scalar in-plane family label m, and explicit (h,k,l) labels where useful.

## Existing figure assets in the repo archive

### Intro figures

| Path or folder | Status | Notes |
|---|---|---|
| `figures/intro/` | IN PROGRESS | Real-space, reciprocal-space, and detector-space assets for orientational limits. |

### Mosaic figures

| Path or folder | Status | Notes |
|---|---|---|
| `figures/mosaic/raw_detector_mosaic_motivation.png` | TODO | New placeholder for the full raw detector image that motivates mosaicity before the low-L crop. |
| `figures/results_ordered/00L_region_horizontal_marked.png` | IN PROGRESS | Moved into the mosaicity section as the low-L m=0 star-feature crop; asset path is retained from the ordered-results figure folder for now. |
| `figures/mosaic/bragg_sphere_bandwidth_size_series.png` | TODO | Placeholder for Bragg-sphere size / Ewald thickness / mosaic cap tutorial sequence. |
| `figures/mosaic/delta_lambda_detector_series.png` | TODO | Placeholder for detector-image sequence varying wavelength bandwidth, incidence angle, or Bragg-sphere size. |
| `figures/mosaic/low_q_003_03_06_data_model_overlay.png` | TODO | Placeholder for measured/calculated overlay or control comparison for low-Q/003, 03, and 06-type features. |
| `figures/mosaic/2d_mosaic.png` | IN PROGRESS | Candidate for mosaicity explanation. |
| `figures/mosaic/inplane_detector_band.png` | IN PROGRESS | May support integration-region explanation. |
| `figures/mosaic/mosaic_schematic.png` | IN PROGRESS | Candidate schematic. |
| `figures/mosaic/specular_detector_cap.png` | IN PROGRESS | Candidate for specular-cap/mosaic discussion. |
| `figures/mosaic/pbi2_waxs.png` | PARKED | Legacy PbI2-related asset; new PbI2 placeholders are under `figures/results_pbi2/`. |

### Ordered-film result figures

The active manuscript now uses the current ordered-film assets in `figures/results_ordered/`. The low-L m=0 star-feature crop has been moved earlier into the mosaicity section so the reader sees the observational problem before the data/model payoff.

| Active file | Status | Notes |
|---|---|---|
| `figures/results_ordered/00L_region_horizontal_marked.png` | IN PROGRESS | Moved into the mosaicity section as the low-L m=0 star-feature crop; ready for advisor review once the real asset is present. |
| `figures/results_ordered/figure7_bi2se3_qr_rod_qz_profiles_detector_selected_q_regions_5deg.png` | IN PROGRESS | Inserted in the ordered validation figure; still needs advisor review for readability and annotation density. |
| `figures/results_ordered/figure7_bi2te3_qr_rod_qz_profiles_detector_selected_q_regions_5deg.png` | IN PROGRESS | Inserted in the ordered validation figure; should match Bi2Se3 styling and label convention. |
| `figures/results_ordered/figure7_bi2se3_qr_rod_qz_profiles.png` | IN PROGRESS | Inserted as measured/calculated profile overlays; final axis and label convention still need advisor check. |
| `figures/results_ordered/figure7_bi2te3_qr_rod_qz_profiles.png` | IN PROGRESS | Inserted as measured/calculated profile overlays; final axis and label convention still need advisor check. |

### PbI2 figures

PbI2 has been reintroduced as a draft extension with placeholders. The real detector, stacking-model, reciprocal-space, and selected-trajectory figures still need to be generated.

| Path or folder | Status | Notes |
|---|---|---|
| `figures/results_pbi2/pbi2_raw_detector_diffuse_motivation.png` | TODO | Placeholder for measured PbI2 detector image with diffuse features. |
| `figures/results_pbi2/pbi2_stacking_fault_model.png` | TODO | Placeholder for real-space stacking-fault schematic. |
| `figures/results_pbi2/pbi2_diffuse_cylinder_schematic.png` | TODO | Placeholder for reciprocal-space diffuse rods/cylinders schematic. |
| `figures/results_pbi2/pbi2_diffuse_data_model_overlay.png` | TODO | Placeholder for measured/ordered/faulted/residual projection figure. |

## P0 figure deliverables

| Proposed figure | Status | Suggested file name | Purpose |
|---|---|---|---|
| Raw detector mosaic motivation | TODO | `figures/mosaic/raw_detector_mosaic_motivation.png` | Show the full measured detector image before the low-L crop. |
| Low-L m=0 star-feature crop | IN PROGRESS | `figures/results_ordered/00L_region_horizontal_marked.png` | Show the near-origin specular feature in the mosaicity section before the correlated-effects tutorial and validation overlay. |
| Bi2Se3 detector image with Q/Qr/Qz trajectories | IN PROGRESS | `figures/results_ordered/figure7_bi2se3_qr_rod_qz_profiles_detector_selected_q_regions_5deg.png` | Show measured data and where projections come from; needs advisor readability check. |
| Bi2Se3 Qz projection overlays | IN PROGRESS | `figures/results_ordered/figure7_bi2se3_qr_rod_qz_profiles.png` | Show measured/calculated fits vs Qz/L; needs final axis-label check. |
| Bi2Te3 detector image with Q/Qr/Qz trajectories | IN PROGRESS | `figures/results_ordered/figure7_bi2te3_qr_rod_qz_profiles_detector_selected_q_regions_5deg.png` | Show measured data and where projections come from; same convention as Bi2Se3. |
| Bi2Te3 Qz projection overlays | IN PROGRESS | `figures/results_ordered/figure7_bi2te3_qr_rod_qz_profiles.png` | Show measured/calculated fits vs Qz/L; needs final axis-label check. |
| Two-component mosaicity evidence | IN PROGRESS | `figures/mosaic/lorentzian_tail_evidence.png` or existing ordered-film crop | Low-L m=0 evidence is inserted; a direct narrow-core versus Lorentzian-tail comparison may still be needed. |
| Reflection-label guide | IN PROGRESS | caption or `figures/results_ordered/reflection_family_labels.png` | Initial scalar m convention appears in text/captions; final convention needs advisor check. |

## Recommended main-text figure sequence

### Figure 1 — Orientational limits / 2D powder motivation

Status: IN PROGRESS  
Likely based on existing `figures/intro/` assets.

Purpose: introduce single crystal, 3D powder, and 2D oriented powder.

### Figure 2 — Model geometry and mosaicity

Status: IN PROGRESS  
Likely based on `figures/mosaic/` and `figures/theory/` assets.

Required update: add or cross-reference evidence for two-component mosaicity early.

### Figure 3 — Bi2Se3 ordered-film result

Status: TODO  
Immediate priority.

Suggested panels:

- measured detector/caked image with Q/Qr/Qz trajectory annotations;
- integration regions or selected reflection families;
- measured/calculated Qz projection overlays;
- optional residuals if they help.

### Figure 4 — Bi2Te3 ordered-film result

Status: TODO  
Immediate priority.

Use the same visual logic as Bi2Se3.

### Figure 5 — Low-L m=0 star-feature observation

Status: IN PROGRESS
Current file placeholder: `figures/results_ordered/00L_region_horizontal_marked.png`.

Purpose: show the unexpected near-origin specular-family detector feature in the mosaicity section before the final ordered-film validation figure.

### Figure 6 — Ordered-film validation overlay

Status: IN PROGRESS
Current files: `figures/results_ordered/figure7_*`.

Purpose: show Bi2Se3 and Bi2Te3 detector trajectories and measured/calculated profile overlays after the star-feature observation has been introduced.

### Future figure — Two-component mosaicity / Lorentzian-tail evidence

Status: IN PROGRESS
Still useful if it can be made cleanly.

Purpose: show that a narrow mosaic distribution alone cannot explain observed high-angle reflections at a given incident angle.

### Future figure — PbI2 selected-rod / stacking-disorder result

Status: TODO  
Placeholders are now inserted in the PbI2 section; generate real figures after the ordered-film story remains readable.

## Figure design rules

### Detector images

- Make measured intensity visible first.
- Use annotations sparingly.
- If Bragg-position markers obscure data, move them to a companion panel or reduce their opacity/size.
- Avoid making the image look like an abstract graphic unless it is explicitly a schematic.
- Use consistent trajectory and branch styling.

### Projection plots

- Plot measured data and calculated intensity on the same axes.
- Use Qz on the horizontal axis.
- Include reflection-family labels.
- Define plus/minus branches once.
- Avoid unexplained internal labels.

### Captions

Each caption should state:

1. what is measured data;
2. what is calculated/simulated;
3. what projection or integration region was used;
4. which reflection family is being shown;
5. what conclusion the panel supports.

## Reflection-labeling convention to develop

Current issue: QR values or M1/M2-style labels are not broadly meaningful.

Possible convention:

- Use a representative m family label for each in-plane ring/manifold.
- State that symmetry-equivalent in-plane reflections are grouped under the representative m label.
- Include L where needed for specific Bragg rods or profile panels.
- Define plus/minus detector branches separately from m and L labels.

Example caption language:

> Reflection families are labeled by the scalar in-plane family m; symmetry-equivalent reflections with the same in-plane scattering magnitude are grouped under the same m label. The plus and minus branches refer only to the two detector-side intersections of the same in-plane family.

## Immediate checklist

- [ ] Decide which Bi2Se3 incident angle(s) to show.
- [ ] Decide which Bi2Te3 incident angle(s) to show.
- [ ] Generate detector/caked image panels with data prominent.
- [ ] Add Q/Qr/Qz trajectories or integration bands.
- [ ] Generate Qz projection profiles with data/model overlays.
- [ ] Add m or explicit (h,k,l) reflection-family labels.
- [ ] Create one mosaic-tail evidence figure or panel, if the inserted m=0 crop is not enough.
- [x] Insert draft ordered-film figures into `sections/results_ordered.tex`.
- [x] Move the low-L m=0 star-feature figure before the ordered validation figure.
- [ ] Update captions before polishing text.
