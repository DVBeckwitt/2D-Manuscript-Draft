# Changelog: uncertainty discussion and mosaicity cleanup

## Purpose

This revision adds the thesis-derived uncertainty discussion without adding new figures, and it cleans the mosaicity section so the main text follows the manuscript philosophy in `AGENTS.md`: physics first, Q/Qr/Qz/m language in the main text, implementation details in the supporting information, and Bi2Se3/Bi2Te3 line-shape validation as the central story.

## Main-text changes

### `sections/modelling_methods.tex`

- Added a compact subsection, `Projection and transformed-coordinate uncertainty`.
- Framed the detector image as the primary measured object and the Qz/m-indexed profiles as detector-derived projections.
- Added the leading detector-pixel footprint terms for angular coordinate uncertainty:
  - radial angular uncertainty, `sigma_{2theta,pix}`;
  - azimuthal uncertainty, `sigma_{phi,pix}`.
- Stated the key physical consequence: the radial term remains bounded, while the azimuthal term becomes problematic mainly near the low-2theta specular limit.
- Clarified that this is a projection/interpretation limit, not a post hoc correction to the data.
- Added a claim boundary: the overlays support the detector-space model comparison, but they are not a complete posterior uncertainty analysis for every fitted parameter.

### `sections/mosaicity_texture.tex`

- Rewrote the mosaicity section into manuscript-style prose.
- Opened with the physical role of mosaicity rather than implementation details.
- Stated the observational problem before introducing the model: off-condition m=0 / 00L intensity cannot be explained by a narrow mosaic core alone.
- Kept the compact two-component mosaicity equation in the main text because it is part of the physical model.
- Explained the Gaussian core and Lorentzian tail in terms of what each contributes to measured detector features.
- Removed the main-text Bragg-sphere surface-density derivation from this section; that detail now belongs in the supporting information.
- Kept the existing mosaic figure but rewrote the caption to emphasize what the reader should learn.

### `sections/results_ordered.tex`

- Changed the profile language from primarily `L profiles` to `Qz profiles`, while preserving `L` as a reciprocal-lattice-unit label where useful.
- Reworded the 003/star-feature discussion to avoid redundant explanation and to keep the feature tied to the Lorentzian-tail evidence.
- Added a concise uncertainty interpretation after the ordered-film validation figure.
- Clarified that the plotted profiles are detector-derived, resolution-limited observables.
- Stated that data and calculation remain directly comparable because both pass through the same projection, binning, and resolution effects.

### `sections/discussion_conclusion.tex`

- Added a final paragraph that defines the uncertainty boundary of the paper.
- Clarified that the manuscript is not claiming full posterior covariance for all fitted structural parameters.
- Reframed the claim as a like-for-like detector-space validation of the model and workflow.

## Supporting-information changes

### `2D_Supplemental/SI_implementation_outline.tex`

- Added a `Projection and intensity uncertainty` subsection.
- Added the thesis-derived coordinate-uncertainty formulas.
- Added the threshold-angle expression for azimuthal uncertainty.
- Included the numerical example for `d = 75 mm` and `p = 300 micrometers`:
  - maximum radial uncertainty approximately `0.066 degrees`;
  - azimuthal uncertainty below `1 degree` above about `2theta = 3.8 degrees`;
  - below `0.5 degrees` above about `2theta = 7.5 degrees`;
  - below `0.25 degrees` above about `2theta = 14.9 degrees`.
- Added detector-space variance propagation for projected-bin intensity.
- Explicitly stated that propagated profile uncertainty supports interpretation but does not replace a full parameter-covariance analysis.

## Figure policy

- No new figures were added.
- No existing figures were removed.
- The uncertainty material is text/equations only, with the detailed derivation pushed to the supporting-information outline.
