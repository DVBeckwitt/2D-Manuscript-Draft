# 2026-05-12 advisor-feedback restructure

This revision implements the requested figure-driven reorganization around the advisor meeting feedback and the current `AGENTS.md` manuscript guidance.

## Files changed

- `main.tex`
  - Added robust draft-figure placeholder helpers so missing planned figures render as explicit boxes instead of breaking layout.
  - Added `sections/correlated_effects.tex` immediately after `sections/mosaicity_texture.tex`.
  - Re-enabled `sections/results_diffuse_pbi2.tex`.
  - Moved `sections/refinement_workflow.tex` to the end of the manuscript, immediately before `sections/discussion_conclusion.tex`.

- `sections/mosaicity_texture.tex`
  - Added a raw detector-image placeholder before the moved low-`L` feature figure.
  - Moved the former ordered-results low-`L`/star-feature figure float into the mosaicity section while preserving the label `fig:hk0_low_l_star`; the planned asset path is now `figures/mosaic/00L_region_horizontal_marked.png`.
  - Expanded the mosaicity explanation to emphasize the observational motivation, the difference between in-plane disorder and out-of-plane mosaicity, the Gaussian core, and the Lorentzian-like long tail.
  - Clarified that the Lorentzian-like component is a phenomenological long-tail description, not a claim that the physical distribution must be exactly Lorentzian.

- `sections/correlated_effects.tex`
  - New subsection after mosaicity.
  - Added tutorial-style prose explaining the coupled roles of mosaicity, finite wavelength bandwidth, divergence, Ewald-sphere thickness, Bragg-sphere size, and the mosaic cap.
  - Added placeholders for the requested figure sequence: Bragg-sphere-size/bandwidth schematic, calculated detector series versus `Delta lambda` or geometry, and measured/calculated crops for the low-`Q`/`003`, `03`, and `06`/`006` features.

- `sections/results_ordered.tex`
  - Removed the low-`L`/star-feature figure from the ordered-results section because it now motivates mosaicity earlier.
  - Reframed the ordered Bi2Se3/Bi2Te3 results as the validation payoff after the mosaicity and correlated-effects explanations.
  - Kept the main ordered-film validation figure and strengthened the explanation of what each row constrains.

- `sections/results_diffuse_pbi2.tex`
  - Replaced the deferred placeholder text with a draft PbI2 section positioned as the stacking-disorder/diffuse-scattering extension of the ordered-film framework.
  - Added explanation of stacking faults using layer registry, layer-pair correlations, fixed-`Q_R` cylinders, and diffuse intensity along `Q_z`.
  - Added figure placeholders for the PbI2 raw detector image, reciprocal-space diffuse-cylinder schematic, stacking-fault model, and ordered-versus-stacking projected-profile comparison.

- `sections/refinement_workflow.tex`
  - Expanded the workflow prose so the table does not stand alone.
  - Positioned the workflow as an end-of-paper practical sequence after the reader has seen the model and results.
  - Added a PbI2 stacking-disorder stage to the workflow table.

- `sections/discussion_conclusion.tex`
  - Updated the conclusion to connect the ordered validation, the PbI2 extension, and the staged workflow.

- `sections/introduction.tex`
  - Updated the final framing paragraph so PbI2 is described as an assembled diffuse-scattering extension after the ordered-film validation rather than as a parked future topic.

- `MANUSCRIPT_STATUS.md` and `figures/FIGURE_STATUS.md`
  - Updated tracking notes to match the new section order and placeholder plan.

- `figures/results_pbi2/README_DEFERRED.md`
  - Updated it from a deferred-status note into a short list of planned PbI2 figure filenames.

## Build check

- Ran two `pdflatex` passes from a clean auxiliary-file state using `\PassOptionsToPackage{draft}{graphicx}\input{main.tex}` to check the LaTeX structure with missing planned graphics. The source compiled without LaTeX fatal errors.
- The container does not provide `bibtex`, so local citation resolution was not completed in this environment; the bibliography source file remains unchanged.
