# Maselli-directed manuscript revision plan

**Status note (2026-05-12):** This older ordered-film triage plan has been partially superseded by the 2026-05-12 advisor-feedback restructure. The current draft reintroduces PbI$_2$ as a subordinate extension after the ordered-film results, moves the workflow to the end before the conclusion, and adds a correlated-effects section after mosaicity. See `CHANGES_20260512_ADVISOR_RESTRUCTURE.md` for the current changes.


This plan translates Dr. Maselli's manuscript philosophy into precise edits for the current draft. It is meant to be used as the next editing checklist, not as general advice.

## Edits already made in this package

1. `main.tex`
   - Removed the visible missing-figure fallback macros (`\maybeinclude` and `\maybeincludecompact`).
   - Rewrote `\panelgraphic` so missing figures fail compilation instead of generating visible placeholder boxes.
   - Commented out `\input{sections/results_diffuse_pbi2}` so the current main draft focuses on Bi2Se3 and Bi2Te3.
   - Left a source comment explaining that PbI2 should be re-enabled only after the ordered-film Qz projection figures are complete.

2. `sections/introduction.tex`
   - Rewrote the final contribution paragraph so the paper's stated validation target is Bi2Se3 and Bi2Te3, not PbI2.
   - Reframed the central result as quantitative line-shape agreement along selected Qr/m trajectories plotted versus Qz.
   - Deferred diffuse-scattering and stacking-disorder applications to later work in this draft.

3. `sections/mosaicity_texture.tex`
   - Removed the current PbI2 detector-pattern evidence figure from the active mosaicity argument.
   - Added a direct two-component mosaicity argument: Gaussian core for the main arc widths, Lorentzian tail for weak off-condition specular intensity.
   - Added source comments marking exactly where the ordered-film Lorentzian-tail evidence figure should be inserted.

4. `sections/refinement_workflow.tex`
   - Reduced the main workflow table to the ordered-film analysis stages.
   - Removed the main-text stacking-disorder refinement stage from the active workflow.
   - Added language that 2theta-phi, caked-coordinate bookkeeping, sub-pixelation, lookup tables, and Monte Carlo sampling belong in the supplement.

5. `sections/results_ordered.tex`
   - Removed the current ordered-film summary figure from the active manuscript.
   - Added explicit source-level insertion points for four required main-text figures:
     - Bi2Se3 measured detector image with Q/Qr/Qz trajectories or integration bands.
     - Bi2Se3 measured/calculated Qz projection overlays.
     - Bi2Te3 measured detector image with Q/Qr/Qz trajectories or integration bands.
     - Bi2Te3 measured/calculated Qz projection overlays.
   - Added text explaining that the projection should be reported versus Qz and labeled by m or explicit (h,k,l) or reflection family, with Qr values used as secondary information.
   - Added the required caveat that the projected Qz coordinate is resolution-limited by mosaicity, beam divergence, wavelength spread, incident-angle uncertainty, and detector sampling, while emphasizing that the same effects are applied to the calculation.

6. `sections/discussion_conclusion.tex`
   - Removed the PbI2-centered conclusion.
   - Rewrote the conclusion around the ordered-film validation, Qz projection overlays, two-component mosaicity, and the need to keep implementation details in the supplement.

7. `sections/results_diffuse_pbi2.tex`
   - Left the PbI2 section in the repository for later use but removed dependence on the deleted missing-figure macro.
   - This section is not currently included by `main.tex`.

## Precise changes still required before the next advisor meeting

### 1. Replace the removed ordered-film summary with real data figures

The old `ordered_detector_summary.png` combined detector images, residuals, generic ROI profiles, and post-fit intensity checks. It did not follow Dr. Maselli's requested logic because it did not clearly show the projection paths and it did not give enough Qz line-shape overlays.

Create two figure sets, one for Bi2Se3 and one for Bi2Te3.

For each material, make a detector image figure with these panels or visual elements:

- measured detector or transformed detector image;
- selected fixed-Qr or m-family trajectories drawn lightly;
- optional integration bands if they clarify the extraction;
- minimal Bragg-position markers, because large circles obscure the data;
- clear incident angle label;
- a caption explaining that each trajectory corresponds to a selected reflection family and that intensity is later projected along that path.

For each material, make a Qz overlay figure:

- x-axis: Qz;
- y-axis: intensity, normalized consistently within the figure;
- measured data and calculation on the same axes;
- one panel per selected reflection family or trajectory;
- labels using m or explicit (h,k,l) or reflection-family notation;
- plus/minus branch labels only if the caption defines them physically;
- no internal-only labels such as M1/M2 unless mapped explicitly to m-family labels.

### 2. Add an early Lorentzian-tail evidence figure

The mosaicity section currently contains the argument but not the evidence. Insert a real ordered-film evidence figure where the source comments mark it.

The strongest version of the figure would show:

- a fixed incident-angle measurement where specular or near-specular reflections are visible even though a narrow mosaic distribution would suppress them;
- a narrow-core-only calculation;
- the full Gaussian-plus-Lorentzian calculation;
- the specific reflection(s) whose presence requires the long tail;
- a caption that explicitly states that the Lorentzian tail is required for the observed off-condition intensity.

### 3. Define the reflection-label convention before the result figures

Add one paragraph before the ordered-film figures or in the first ordered-film caption.

Use language like:

> For hexagonal films, each plotted in-plane family label denotes the set of symmetry-equivalent in-plane reflections with the same in-plane reciprocal-space radius. The quoted Qr value is the corresponding radial magnitude and is used only as secondary numerical information. Branch labels distinguish the two detector-side intersections of the same reciprocal-space family at a given incident angle.

Then apply this convention consistently in every figure label and caption.

### 4. Add the experimental incident-angle table

The current draft does not list all incident angles collected. Add a table in the methods or refinement-workflow section.

Required columns:

- material;
- all incident angles collected;
- incident angles used for the main-text figures;
- incident angles moved to supplement;
- role of each angle, for example alignment, mosaic tail, Qz overlays, or validation.

Dr. Maselli specifically wanted all collected angles listed so readers do not think only the displayed subset was collected.

### 5. Move implementation details to the supplement

Keep the main paper in Q, Qr, Qz, m, Bragg rod, incident angle, mosaicity, and line-shape language.

Move the following into the supplementary material:

- 2theta-phi implementation details;
- caked coordinate transformation;
- sub-pixelation and binning;
- lookup-table remapping;
- Monte Carlo beam-position, divergence, and wavelength sampling;
- mosaic-event sampling;
- computational efficiency arguments;
- full peak-by-peak profile arrays;
- h-BN fitting method.

In the main text, one sentence is enough:

> Computationally, the projections were evaluated in an equivalent 2theta-phi representation for efficiency; implementation details and validation of the coordinate transformation are given in the Supporting Information.

### 6. Keep PbI2 out of the main result until the ordered-film figures work

The PbI2 section is preserved in the repository but excluded from `main.tex`. Reintroduce it only after the Bi2Se3/Bi2Te3 figure sequence is successful.

When PbI2 returns, it should be a separate extension of the method, not mixed into the first proof that the ordered-film line shapes are reproduced.

## Manuscript philosophy to preserve during future edits

- Do not lead with software implementation.
- Do not hide the success in dense detector-summary graphics.
- Show the data and calculated line shapes directly.
- Use diffraction language first: Q, Qr, Qz, m, Bragg rods, incident angle, mosaicity, resolution.
- Use more figures during drafting than will survive in the final paper.
- Make measured data visually prominent.
- Use the supplement for optimization details.
