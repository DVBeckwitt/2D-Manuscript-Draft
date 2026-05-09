# Figure Status

Last updated: 2026-04-30  
Current figure priority: Bi2Se3 and Bi2Te3 ordered-film figures showing measured data, Q/Qr/Qz trajectories or integration regions, and measured/calculated Qz projection overlays.

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
| `figures/mosaic/2d_mosaic.png` | IN PROGRESS | Candidate for mosaicity explanation. |
| `figures/mosaic/inplane_detector_band.png` | IN PROGRESS | May support integration-region explanation. |
| `figures/mosaic/mosaic_schematic.png` | IN PROGRESS | Candidate schematic. |
| `figures/mosaic/specular_detector_cap.png` | IN PROGRESS | Candidate for specular-cap/mosaic discussion. |
| `figures/mosaic/pbi2_waxs.png` | PARKED | PbI2-related; defer for now. |

### Ordered-film result figures

The earlier placeholder/result PNGs in `figures/results_ordered/` were removed from the active package because they were not the final advisor-requested figures. The folder now contains `README_needed_figures.md` and should be repopulated with real data figures only.

| Proposed file | Status | Needed action |
|---|---|---|
| `figures/results_ordered/bise_qz_trajectories.png` | PLACEHOLDER INSERTED | Measured Bi2Se3 detector image with projected fixed-$Q_r$ rod centerlines, direct m labels near fitted peaks, linear intensity, no stars, no legend. |
| `figures/results_ordered/bise_qz_projection_overlays.png` | PLACEHOLDER INSERTED | Bi2Se3 measured/calculated intensity overlays versus $Q_z$ for selected m/fixed-$Q_r$ trajectories. |
| `figures/results_ordered/bite_qz_trajectories.png` | PLACEHOLDER INSERTED | Measured Bi2Te3 detector image with the same rod/m-label convention as Bi2Se3; linear intensity, no stars, no legend. |
| `figures/results_ordered/bite_qz_projection_overlays.png` | PLACEHOLDER INSERTED | Bi2Te3 measured/calculated intensity overlays versus $Q_z$ for selected m/fixed-$Q_r$ trajectories. |

### PbI2 figures

The earlier PbI2 result PNGs were removed from `figures/results_pbi2/` and replaced with `README_DEFERRED.md`. PbI2 remains parked until the ordered Bi2Se3/Bi2Te3 figures are complete.

| Path or folder | Status | Notes |
|---|---|---|
| `figures/results_pbi2/` | PARKED | Reintroduce only with real selected-rod data/calculation/residual figures. |

## P0 figure deliverables

| Proposed figure | Status | Suggested file name | Purpose |
|---|---|---|---|
| Bi2Se3 detector image with Q/Qr/Qz trajectories | PLACEHOLDER INSERTED | `figures/results_ordered/bise_qz_trajectories.png` | Show measured data and where projections come from; linear intensity, direct m labels, no stars. |
| Bi2Se3 Qz projection overlays | PLACEHOLDER INSERTED | `figures/results_ordered/bise_qz_projection_overlays.png` | Show measured/calculated fits vs $Q_z$. |
| Bi2Te3 detector image with Q/Qr/Qz trajectories | PLACEHOLDER INSERTED | `figures/results_ordered/bite_qz_trajectories.png` | Show measured data and where projections come from; same convention as Bi2Se3. |
| Bi2Te3 Qz projection overlays | PLACEHOLDER INSERTED | `figures/results_ordered/bite_qz_projection_overlays.png` | Show measured/calculated fits vs $Q_z$. |
| Two-component mosaicity evidence | TODO | `figures/mosaic/lorentzian_tail_evidence.png` | Show why long-tail mosaicity is required. |
| Reflection-label guide | TODO | caption or `figures/results_ordered/reflection_family_labels.png` | Explain the scalar m family convention. |

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

### Figure 5 — Two-component mosaicity / Lorentzian-tail evidence

Status: TODO  
Immediate priority if it can be made cleanly.

Purpose: show that a narrow mosaic distribution alone cannot explain observed high-angle reflections at a given incident angle.

### Figure 6 — PbI2 selected-rod / stacking-disorder result

Status: PARKED  
Do not prioritize until ordered-film story is stable.

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
- [ ] Create one mosaic-tail evidence figure or panel.
- [ ] Insert draft figures into `sections/results_ordered.tex` or related section.
- [ ] Update captions before polishing text.
