# Changelog for advisor annotations

This file records manuscript edits made in response to advisor annotations, with brief rationale. It is intended to make structural decisions easy to audit while the draft is still evolving.

## 2026-04-25 — Complete Sections 4--5 figure/result pass

### What changed

- Replaced the placeholder four-panel figure blocks in Section 4 and Section 5 with full-width summary figures that align directly with the surrounding result narrative (`figures/results_ordered/ordered_detector_summary.png`, `figures/results_pbi2/pbi2_disorder_summary.png`).
- Rewrote the ordered-film prose so it describes the completed detector-space comparisons, local profile checks, and post-fit $Q_z$ intensity checks instead of referring to future/placeholder content (`sections/results_ordered.tex`).
- Rewrote the PbI$_2$ prose so the selected-rod refinement is described as completed, including the ordered-baseline residual, stacking-disorder fit, and before/after residual comparison (`sections/results_diffuse_pbi2.tex`).
- Removed placeholder caption language and fixed the displayed rod-profile equation punctuation so no standalone period appears after the equation.

### Status

- **Feature:** implemented for the main manuscript draft.
- **Scope:** no numerical fitted parameters were added in this pass; the text remains qualitative and tied to the figure-level comparisons.


## 2026-04-21 — Add adjacent Nookiin related-work citation

### What changed

- Added a narrow Introduction citation to Nookiin as complementary atomistic/supercell context for commensurate multilayer 2D heterostructures and reciprocal-space diffraction visualization (`sections/introduction.tex`).
- Added the citable Computer Physics Communications article as `AguilarSpindola2026Nookiin` (`bibliography/references.bib`).

### Status

- **Feature:** implemented.
- **Boundary:** Nookiin is not described as a workflow dependency, detector-space WAXS refinement method, or software used by the present model.
- **Validation:** `pdflatex -> bibtex -> pdflatex -> pdflatex` completed and the bibliography key resolves in `main.bbl`; no duplicate BibTeX key was found.
- **Known environment issue:** `latexmk` is unavailable because MiKTeX cannot find the required Perl script engine.

## 2026-03-13 — Pedagogical rewrite of diffraction-model narrative

### Advisor requests addressed

- **Explain the diffraction model in the order a reader would naturally build it up:** first the simplest single-ray scattering picture, then the experimental complications.
- **Make the structure-factor subsection read as the many-\(\mathbf G\) extension of that same geometry,** including the link between \(Q\), \(\mathbf G\), and the corresponding \(\mathbf{k}_f\) set.

### What changed (and why)

- Rewrote the opening of `\subsection{Diffraction Geometry}` so it now starts from the ideal elastic-scattering construction for one incident ray and one reflection, explicitly introducing \(\mathbf Q=\mathbf{k}_f-\mathbf{k}_i\), the Ewald sphere, the Bragg sphere, and the simplest relation \(\mathbf{k}_f=\mathbf{k}_i+\mathbf G\) before discussing real-world corrections (`sections/modelling_methods.tex`).
- Rewrote the opening paragraph of the `Diffraction Model` section so it now previews the same reader-facing sequence used below: determine allowed \(\mathbf{k}_f\) values in the simplest geometry, extend that construction to the experimental beam/sample/detector geometry, then apply structure-factor and mosaicity weights (`sections/modelling_methods.tex`).
- Moved the detector propagation immediately after that ideal construction so the reader sees how an allowed \(\mathbf{k}_f\) becomes a detector position before encountering beam divergence, footprint truncation, offsets, refraction, and absorption (`sections/modelling_methods.tex`).
- Further reorganized the diffraction-geometry prose into an explicit three-step progression: (1) find the simplest \(\mathbf{k}_f\), (2) generalize to more complicated rays while still focusing only on allowed \(\mathbf{k}_f\) values, and (3) discuss how each resulting \(\mathbf{k}_f\) is weighted (`sections/modelling_methods.tex`).
- Clarified the structure-factor subsection so \(F_{\mathbf G}\) is described operationally as a multiplicative factor applied to each allowed \(\mathbf{k}_f\) by evaluating the structure-factor function at the reciprocal-space intersection. The text now explicitly notes that this can be understood either on discrete integer-indexed reciprocal-lattice points or as a continuous function \(F(\mathbf Q)\) sampled at the intersected coordinate (`sections/modelling_methods.tex`).
- Rewrote the opening of the mosaicity subsection so it now starts from the ideal \(\mathbf{k}_f\) set and explains mosaicity as a redistribution of the ideal per-reflection intensity over nearby exit vectors, before introducing the wrapped misorientation density \(\omega(\Delta\theta)\), Bragg-circle/Bragg-sphere weighting, and detector-space consequences (`sections/mosaicity_texture.tex`).
- Reframed the `\subsection{Structure Factor}` opening so it now describes the full calculation as iterating over many symmetry-allowed \(\mathbf G\) vectors, evaluating the relevant \(Q\), assigning \(|F_{\mathbf G}|^2\), and generating the associated family of \(\mathbf{k}_f\) rays in the full forward model (`sections/modelling_methods.tex`).

## 2026-03-03 — Restructure the model narrative (paper flow)

### Advisor requests addressed

- **Rename Section 2 to “Diffraction Model” and add a high-level overview of the model strategy.**
- **Move the former Section 2.1 later** (standard definitions should not lead the narrative).
- **Fold the former “Section 3” into the model** (as a subsection, e.g., 2.3) and avoid framing this part as “texture” when the model is specifically about mosaicity.
- **Clarify the separation between model description and refinement/workflow** (the model comes first, and the fitting workflow follows).

### What changed (and where)

- Renamed `\section{Modelling Methods}` → `\section{Diffraction Model}` and added an opening overview paragraph to summarize the overall forward-model strategy (`sections/modelling_methods.tex`).
- Reordered the model subsections so **Diffraction Geometry** is introduced before the **Structure Factor** definitions, addressing the request that the (standard) crystallography not appear first (`sections/modelling_methods.tex`).
- Converted the former top-level `\section{Mosaicity and texture}` into a **subsection within the Diffraction Model** (`\subsection{Mosaicity}`), so it now reads naturally as part of Section 2 rather than a separate section (`sections/mosaicity_texture.tex`).
- Updated one table group label from “Texture and stacking” to “Mosaicity and stacking” to keep terminology aligned with the model emphasis (`sections/refinement_workflow.tex`).
- Added a brief lead sentence at the start of the refinement section explicitly pointing back to the model section, so the workflow is clearly positioned as “what we do after the model is defined” (`sections/refinement_workflow.tex`).

### Small supporting fixes made during the restructure

- Added `\label{eq:structure_factor}` to the structure-factor equation so the existing workflow text reference to `Eq.~\eqref{eq:structure_factor}` resolves cleanly (`sections/modelling_methods.tex`).
- Removed an orphaned stray `3` that was present as standalone text in the mosaicity section (`sections/mosaicity_texture.tex`).

### Why this order of edits

These changes were implemented as a single “paper flow” pass to reduce downstream rework: once section boundaries and subsection order are stable, later edits to notation, equation numbering, and figure layout/quality can be made without repeatedly re-threading the narrative across the draft.

### Not yet addressed in this pass

This pass intentionally does **not** attempt to solve other annotated items (e.g., figure redesign and publication-quality styling, notation choices such as $\chi$ and $\theta_i$, or full equation-numbering cleanup). Those changes interact strongly with one another and are better handled after the section structure is fixed.

## 2026-03-03 — Numbering and cross-reference plumbing

### Advisor requests addressed

- **Fix equation numbering and references** so that equation numbers are unique and cross-references resolve cleanly.
- **Fix figure “plumbing”** so that every top-level figure has a caption and is explicitly referenced in the text.

### What changed (and why)

- Removed the manual `\tag{1}` on the structure-factor equation so equation numbering is handled consistently by LaTeX and does not produce duplicate equation numbers or duplicate hyperlink anchors (`sections/modelling_methods.tex`).
- Added explicit in-text references to figures that previously appeared without being cited in the narrative, which avoids “orphaned” floats and makes the manuscript easier to follow during review:
  - Sample-geometry figure is now referenced as a complete figure rather than only by a subpanel label (`sections/modelling_methods.tex`).
  - The schematic+detector mosaic-broadening figure is now introduced in the text (`sections/mosaicity_texture.tex`).
  - The reciprocal-cylinder schematic is now referenced in the PbI$_2$ results introduction (`sections/results_diffuse_pbi2.tex`).

### Verification

- Confirmed the manuscript compiles with `pdflatex main.tex` (two passes to resolve cross-references). `latexmk` is not currently usable in this environment because MiKTeX cannot find Perl.

## 2026-03-03 — Notation and symbol standardization

### Advisor requests addressed

- **Standardize symbols and variable definitions globally** (especially for angles and offsets) so that notation is unambiguous across text, captions, and figures.
- **Write the Debye--Waller factor in a general tensor form** rather than committing early to a reduced approximation.
- **Avoid introducing unnecessary reference angles (e.g., $\theta_0$)** when the quantity can be defined directly relative to the substrate/film normal.

### What changed (and why)

- Adopted consistent offset notation for the sample/beam heights: `z_B` (beam-center vertical offset) and `z_S` (sample-center vertical offset). Updated text and the sample-geometry figures so captions and schematics agree (`sections/modelling_methods.tex`, `sections/refinement_workflow.tex`, `figures/geometry/sample_geometry_rotation.tex`, `figures/geometry/sample_geometry_no_rotation.tex`).
- Renamed the residual sample-normal tilt from `\chi` to `\delta` to avoid collision with the conventional use of $\chi$ for an in-plane/azimuthal angle. Updated both manuscript text and the sample-alignment schematic (`sections/modelling_methods.tex`, `sections/refinement_workflow.tex`, `figures/geometry/sample_geometry_alignment.tex`).
- Renamed the detector-plane azimuthal angle from `\phi` to `\chi` (the standard GIWAXS convention), and updated the system-geometry schematic accordingly (`sections/modelling_methods.tex`, `figures/geometry/system_geometry.tex`).
- Renamed the goniometer-arm vector label from `\vec{G}` to `\vec{g}` to avoid confusion with the reciprocal-lattice vector $\mathbf{G}$ used throughout the diffraction model (`sections/modelling_methods.tex`, `figures/geometry/sample_geometry_alignment.tex`).
- Updated the Debye--Waller factor in the structure-factor expression to the tensor form $\mathbf{G}\cdot\mathbf{U}_a\cdot\mathbf{G}$ and revised the surrounding explanation accordingly (`sections/modelling_methods.tex`).
- Standardized mosaic-kernel parameters to avoid reusing $\gamma$ (already used for detector tilt): the Lorentzian width is now denoted by $\Gamma$, including in the workflow table (`sections/mosaicity_texture.tex`, `sections/refinement_workflow.tex`).
- Removed $\theta_0$ from the mosaicity subsection and switched the Bragg-sphere polar-angle symbol to $\vartheta$ for clarity alongside $\theta_i$ and $2\theta$. Updated the mosaic schematics to match (`sections/mosaicity_texture.tex`, `figures/mosaic/mosaic_bragg_inplane.tex`, `figures/mosaic/mosaic_bragg_specular.tex`).

### Definitions added

- Defined $I_0$ (per-reflection intensity scale prior to mosaic redistribution) and clarified the meaning of $R$ and $\rho(\vartheta)$ in the Bragg-sphere normalization (`sections/mosaicity_texture.tex`).

## 2026-03-03 — Scope and terminology tightening

### Advisor requests addressed

- **Reduce unnecessary detail** in the main-text normalization discussion (keep the essential normalization statement without a step-by-step derivation).
- **Avoid “near-specular” language** in favor of clearer terms such as **specular** and **Bragg rods**.
- **Replace colloquial “misset”** with **misalignment**.
- **Introduce the wrapped mosaic distribution earlier** so the periodicity assumption is clear at first use.

### What changed (and why)

- Shortened the wrapped-distribution discussion and clarified periodicity at the first introduction of \(\omega(\Delta\theta)\) (`sections/mosaicity_texture.tex`).
- Tightened the Bragg-sphere normalization discussion by removing the explicit area-element/intensity-conservation derivation while retaining the normalized surface-density expression and a brief Jacobian note (`sections/mosaicity_texture.tex`).
- Replaced “near-specular” phrasing with “specular” and explicitly introduced Bragg-rod language where appropriate (intro narrative + refinement workflow + workflow table) (`sections/introduction.tex`, `sections/refinement_workflow.tex`).
- Replaced remaining uses of “texture/textures” in the introduction with more specific orientation language (e.g., “preferred orientation”, “orientation distributions”) to keep terminology aligned with the mosaicity-focused model (`sections/introduction.tex`).
- Replaced “goniometer misset” with “goniometer misalignment” and removed similarly colloquial wording (`sections/refinement_workflow.tex`).

## 2026-03-03 — Add missing beam/sample and propagation components

### Advisor requests addressed

- **Add missing model components** that materially affect the observed line shapes and intensities: incident-beam angular divergence, finite beam size, finite sample size/footprint truncation, and refraction/absorption corrections.
- **Decide what belongs in the main text versus deferred detail** so the model narrative stays readable while still being fully specified.

### What changed (and why)

- Expanded the Diffraction Geometry narrative to explicitly state that the forward model averages over a finite beam phase space (finite spot size and angular divergence), rather than treating the incident beam as a single ray (`sections/modelling_methods.tex`).
- Clarified how finite sample size and grazing-incidence footprint truncation are handled (by intersecting sampled rays with the sample plane and discarding rays outside the $W\times H$ window), so the origin of partial-illumination bias is clear in the model description (`sections/modelling_methods.tex`).
- Added a compact absorption-weight expression for a uniformly scattering film of thickness $t$, and stated how refraction is incorporated (effective internal angles + Fresnel transmission factors) (`sections/modelling_methods.tex`).
- Updated the mosaicity subsection to clarify the wrapped distribution and the Bragg-sphere Jacobian (`sections/mosaicity_texture.tex`).

## 2026-03-03 — Figure publication pass (layout + clarity)

### Advisor requests addressed

- **Rebuild Fig. 1 layout** into paired side-by-side panels with only (a)–(f) subpanel labels, and move all explanation into the caption.
- **Improve publication quality and clarity** of the geometry schematics, including explicitly showing detector orientation relative to the goniometer arm.
- **Sanity-check the illustrated incidence angle** (remove the misleading $\theta_i=35^\circ$ annotation from the schematic).

### What changed (and why)

- Rebuilt Fig.~1 into three paired rows: (a,b), (c,d), (e,f), with empty subcaptions so only the panel letters appear. The reciprocal-space/detector interpretation is now carried entirely by the main caption, and a single-crystal detector panel was added using `intro/mono_single_crystal.png` (`sections/introduction.tex`).
- Updated the intro narrative that describes Fig.~1 so it no longer assumes a “top row” layout, and added an explicit reference to the single-crystal detector panel (`sections/introduction.tex`).
- Removed the explicit $\theta_i=35^\circ$ annotation from the sample-rotation schematic and changed the illustrative rotated configuration to $5^\circ$ so the diagram no longer suggests a non-grazing geometry (`figures/geometry/sample_geometry_rotation.tex`).
- Simplified the sample-alignment schematic by removing an unrelated torque arrow, and added a small detector patch at the end of $\vec{g}'$ showing detector-plane axes and the detector normal $\hat{n}_{\mathrm{det}}$, making the detector orientation relative to the goniometer arm explicit (`figures/geometry/sample_geometry_alignment.tex`, `sections/modelling_methods.tex`).
- Improved the system-geometry schematic by adding detector-frame axes and removing an obsolete reference line so the detector orientation parameters are clearer at a glance (`figures/geometry/system_geometry.tex`).

## 2026-03-04 — Clarify $\chi$ usage (detector rotation vs detector-plane azimuth)

### Advisor requests addressed

- **Avoid confusing reuse of $\chi$** by assigning it a single meaning consistent across text and figures (related to the Page~6 note that $\chi$ is best reserved for an in-plane rotation).

### What changed (and why)

- Reserved $\chi$ for the detector in-plane rotation (a fixed detector-geometry degree of freedom) and denoted the detector-plane azimuth of a diffracted ray by $\phi$, removing an ambiguity where $\chi$ previously referred to both a refined geometry parameter and a per-ray coordinate (`sections/modelling_methods.tex`, `figures/geometry/system_geometry.tex`).

## 2026-03-04 — Revert Fig.~3(b) generator (.tex) to pre-edit state

### Advisor requests impacted

- This reopens the Fig.~3(b) clarity improvements that were previously made to explicitly show detector orientation relative to the goniometer arm (requested on Page~6).

### What changed (and why)

- Restored `figures/geometry/sample_geometry_alignment.tex` to its pre-edit version (from the baseline `main` branch) at the author’s request, undoing the detector-orientation patch and reverting labels within that schematic. This provides a clean starting point for an alternative redraw without preserving intermediate layout experiments in the tracked figure source.

## 2026-03-04 — Add supplemental document (workflow + failure modes)

### What changed (and why)

- Added a standalone supporting-information document for refinement workflow notes and stacking/polytype “failure-mode” derivations (`2D_Supplemental/SI_failure_modes.tex`) with supporting graphics (`2D_Supplemental/2H.png`, `2D_Supplemental/6H_R-3.png`).
- Added in-manuscript callouts to the supporting information where it is used (workflow expansion + stacking-fault derivations) (`sections/refinement_workflow.tex`, `sections/results_diffuse_pbi2.tex`, `sections/introduction.tex`).

### Verification

- Confirmed the supplemental document compiles with `pdflatex SI_failure_modes.tex` (two passes) from within `2D_Supplemental/`.
