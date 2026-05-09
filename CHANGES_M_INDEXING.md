# Changes: scalar m reflection-family notation

## Purpose

This revision replaces the previous in-plane family label with the scalar label `m`. The intent is to keep the paper readable for a diffraction audience while avoiding the ambiguity of using a two-index-looking label as if it were also a scalar powder-ring or rod-family label.

## Main-text changes

- Added a formal definition of the scalar in-plane family label in `sections/modelling_methods.tex`:
  - `m(H,K) = [H K] M_parallel [H K]^T proportional to Q_r^2`.
  - For the hexagonal bismuth chalcogenide setting, `m` is proportional to `H^2 + H K + K^2`.
  - All integer `(H,K)` rods with the same `m` are still generated and projected individually before summation.
- Added `\label{sec:structure_factor}` so the results section can point to the definition of `m`.
- Replaced visible profile/trajectory language with `m` language throughout the active manuscript.
- Replaced the specular-family label with `m=0`.
- Replaced the 003/star-feature label with `m=0, L=3`.
- Renamed the internal figure label from the old zero-family name to `fig:m0_l3_star`.

## Section-specific edits

### `sections/modelling_methods.tex`

- Changed the projection-uncertainty subsection to describe `Q_z` profiles through selected `m`-indexed trajectories.
- Replaced the previous scalar family definition with `m(H,K)`.
- Clarified that `m` is a family label, not an individual crystallographic reflection.

### `sections/mosaicity_texture.tex`

- Replaced in-plane ring/rod-family language with `m`-indexed language.
- Replaced all zero-family mosaic-tail discussion with `m=0`.
- Updated the mosaicity figure caption so off-condition specular peaks are described as `m=0` peaks.

### `sections/refinement_workflow.tex`

- Replaced mixed fixed-radius/family-notation phrasing with `fixed-m trajectories`.
- Rephrased the deferred stacking-disorder sentence as fitting `m`-indexed rods as a function of `L`.

### `sections/results_ordered.tex`

- Replaced the ordered-film validation language with `m` terminology:
  - in-plane `m` families,
  - fixed-`m` Bragg-rod trajectories,
  - selected `m` families,
  - `m=0` specular-family reflections,
  - `m=0, L=3` for the 003 feature.
- Added an explicit reminder in the results opening that `m` is defined in the structure-factor section and that `m=0` denotes the specular `00L` family.
- Updated figure placeholders/captions to request direct `m` labels.

### `sections/discussion_conclusion.tex`

- Replaced the summary language with fixed-`m` trajectories and `m=0` features.

## Supporting-information and figure-documentation edits

- Updated `2D_Supplemental/SI_implementation_outline.tex` to describe curved fixed-`m` trajectories.
- Updated `2D_Supplemental/SI_failure_modes.tex` so the selected-rod analytical intensity uses `I_m`; the selected-rod mask was renamed from `m_ij` to `w_ij` to avoid conflict with the new family label.
- Updated mosaic schematic labels to `G_{m,L}` and `G_{r,m}`.
- Updated `figures/FIGURE_STATUS.md`, `MANUSCRIPT_STATUS.md`, `TODO.md`, and the manuscript-facing documentation so future figure tasks ask for `m` labels.
- Updated `AGENTS.md` so future agents use `m` as the preferred compact in-plane family label, with explicit `(h,k,l)` labels only where needed.

## Validation

- Recompiled `main.tex` successfully with `pdflatex`.
- Rendered the revised PDF pages for layout verification.
- Checked active manuscript/source files to ensure manuscript-facing in-plane-family label language uses `m`. Bibliographic author names and excluded historical patch/backup artifacts were not treated as manuscript terminology.
