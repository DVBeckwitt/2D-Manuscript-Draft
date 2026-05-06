# Changelog: Maselli philosophy + concision revision

This changelog is cumulative. It includes the earlier Maselli-revision changes and the follow-up concision pass requested after the chapter-by-chapter blast check.

## Guiding basis

The revision follows `AGENTS.md` and the advisor meeting feedback: paper first, software second; show the Bi2Se3/Bi2Te3 success clearly; write in Q/QR/Qz/HK language for a diffraction audience; move implementation and optimization details to the supplement; and use figures to demonstrate measured/calculated agreement.

## Global manuscript changes

- Kept the manuscript focused on ordered Bi2Se3 and Bi2Te3 as the active main-text validation case.
- Kept PbI2 diffuse scattering inactive in `main.tex`; the PbI2 source file is now a deferred-section stub with no active missing-figure references.
- Removed the placeholder-figure commands from `main.tex`; missing figures no longer render as visible placeholder boxes.
- Removed active placeholder result images from `figures/results_ordered/` and `figures/results_pbi2/`; README files now specify the real figures still needed.
- Added explicit source-level insertion points for the required Bi2Se3 and Bi2Te3 detector/trajectory and Qz-overlay figures.
- Added supporting-information bookkeeping for computational details and moved the ordered-parameter table out of the main text.
- Updated figure-status and input-inventory documents so they no longer describe deleted placeholder result PNGs as active assets.

## Introduction

- Compressed the broad material-family survey into a shorter motivation tied directly to layered-film orientation, bismuth chalcogenides, and layered halides.
- Kept the orientational-limit figure but shortened the post-figure explanation.
- Shifted emphasis away from general background and toward why 2D-powder WAXS patterns require full detector modeling.
- Compressed the discussion of standard 1D reductions, ODF/preferred-orientation approaches, and radial-profile methods.
- Split the contribution statement into short paragraphs: model scope, ordered Bi2Se3/Bi2Te3 validation, and deferred PbI2/stacking-disorder extension.

## Diffraction Model

- Shortened the section opening so it states the forward-model task directly: generate exit rays, map them to detector pixels, weight them physically, and compare the detector prediction with measured observables.
- Reduced low-level coordinate and implementation bookkeeping in the main text.
- Preserved the physical Ewald/Bragg-sphere construction.
- Condensed detector/sample geometry prose while keeping the geometry figures and captions.
- Shortened the structure-factor section after Eq. (1).
- Kept the important 2D-powder point that symmetry-equivalent reflections cannot be collapsed to a single powder multiplicity factor because geometry and orientation matter.

## Mosaicity

- Kept mosaicity early in the manuscript because it is a central physical point, not an implementation detail.
- Removed the standalone simple mosaic schematic from the active main text to avoid redundant figure clutter.
- Kept the four-panel mosaic figure that connects reciprocal-space broadening to detector-space arcs and specular caps.
- Strengthened the early two-component mosaicity paragraph: narrow core alone is insufficient; off-condition reflections require a long-tailed tilted-crystallite population.
- Kept a source-level insertion point for the required Lorentzian-tail evidence figure.
- Moved the explicit wrapped-distribution and surface-density forms to the supporting-information track, leaving the main text to state the physical role of the Gaussian core and Lorentzian tail.

## Refinement workflow

- Reduced repeated staged-refinement prose.
- Let the workflow table carry the step-by-step structure.
- Shortened the pre-table explanation to the reason for staging: geometry, mosaicity, and structure-factor intensity are correlated.
- Shortened the post-table explanation to two paragraphs: geometry/alignment, then profile/intensity/Qz validation.
- Shortened the table row for ordered-film validation; detailed lists of occupancies, coordinates, and ADPs no longer interrupt the table.
- Kept implementation details such as 2theta-phi remapping, caked fields, lookup tables, and Monte Carlo sampling in the supporting-information lane.

## Ordered Bi2Te3/Bi2Se3 results

- Removed active future-tense scaffold language where possible and replaced it with result-forward organization language.
- Kept non-rendering LaTeX comments marking the four required real figure insertion points:
  - Bi2Se3 detector image with Q/QR/Qz trajectories or integration bands.
  - Bi2Se3 measured/calculated Qz projection overlays.
  - Bi2Te3 detector image with Q/QR/Qz trajectories or integration bands.
  - Bi2Te3 measured/calculated Qz projection overlays.
- Moved the projection caveat closer to the figure-insertion location.
- Kept the caveat that Qz profiles are resolution-broadened, not ideal reciprocal-space cuts.
- Kept the requirement that HK/HKL reflection-family labels must be used or clearly tied to any internal labels.
- Moved the ordered-film structure-parameter table to `2D_Supplemental/SI_ordered_structure_parameters.tex` and replaced it in the main text with a short supporting-information reference.
- Kept the main-text emphasis on the measured/calculated line-shape overlays.

## Discussion and conclusion

- Reduced the discussion from five paragraphs to three.
- Removed meta-writing instructions about how the paper should be organized.
- Kept only the central result, the resolution/projection caveat, and the broader implication of the two-component mosaicity model.
- Preserved the point that PbI2 and stacking disorder are later extensions after the ordered-film validation is clear.

## Supporting-information additions

- Added `2D_Supplemental/SI_ordered_structure_parameters.tex` containing the ordered Bi2Te3/Bi2Se3 structure-parameter table moved out of the main text.
- Added `2D_Supplemental/SI_implementation_outline.tex` to hold the mosaic surface-density expression, coordinate-remapping notes, and Monte Carlo sampling notes moved out of the main text.
- Added `docs/BLAST_CHECK_CONCISION.md` to keep the chapter-by-chapter concision rationale with the manuscript package.

## Remaining figure tasks

The real data figures still need to be generated and inserted. I did not fabricate the missing Bi2Se3/Bi2Te3 Qz overlay figures. The main remaining tasks are:

1. Add the Bi2Se3 detector trajectory figure.
2. Add the Bi2Se3 measured/calculated Qz overlays.
3. Add the Bi2Te3 detector trajectory figure.
4. Add the Bi2Te3 measured/calculated Qz overlays.
5. Add the Lorentzian-tail evidence figure for the two-component mosaicity argument.
6. Assemble the supporting information so that Table S1 and the computational-implementation details are formally included.
7. Rebuild the PbI2 extension later from real selected-rod figures rather than the removed placeholder images.
