# AGENTS.md — Manuscript Writing Guidance

## Scope

These instructions apply to all writing, rewriting, figure planning, caption drafting, and structural editing for the 2D diffraction / mosaicity manuscript. They encode Dr. Paul Maselli’s guidance from the advisor meeting about how the manuscript should be written and what philosophy should control future revisions.

The manuscript is the priority. The software, code release, and implementation polish are secondary unless they directly support the manuscript figures and scientific argument.

## Core philosophy

1. **Paper first. Software second.**
   The manuscript is the primary deliverable. Do not delay manuscript progress in order to perfect the software release, clean configuration scripts, or optimize usability. Software can be beautified later; the paper must demonstrate the scientific value now.

2. **Show the success clearly.**
   The central result is that the model quantitatively reproduces the measured diffraction line shapes for **Bi2Se3** and **Bi2Te3**. This success must be visible in the main paper. Do not hide it inside two-dimensional detector images where the reader cannot assess the fit.

3. **Write for a scattering / diffraction audience.**
   Use the language readers expect: **Q**, **QR**, **Qz**, **m-indexed reflection families**, explicit **(h,k,l)** labels when needed, **Bragg rods**, **Bragg positions**, **reciprocal space**, **incident angle**, **mosaicity**, **resolution**, and **line-shape fitting**. Avoid leading the main text with software-native language such as “caked space,” internal branch labels, configuration scripts, lookup tables, or optimization terminology.

4. **Physics first; optimization later.**
   The main text should explain the physical model and the experimental comparison. Computational optimizations belong in the supplementary material unless they are absolutely necessary to understand the physics.

5. **Figures drive the paper.**
   The paper should be written around clear figures. It is better to begin with too many figures and remove or consolidate later than to write with too few and create a communication problem.

6. **Explain more than feels necessary.**
   Do not compress a complicated procedure into a single sentence. If a step involves detector space, reciprocal-space trajectories, integration bands, projection, fitting, or simulation, explain it step by step. What is obvious to the author is probably not obvious to the reader.

7. **Captions must teach.**
   Captions are part of the scientific argument, not just labels. A caption should explain what the reader is seeing, how the comparison was generated, and what conclusion the reader should draw. Redundancy between the caption and main text is acceptable when it helps the reader catch the main point.

8. **Show the observational problem before the model correction.**
   When introducing a model ingredient such as long-tail mosaicity, wavelength bandwidth, projection width, structure-factor fitting, or propagated uncertainty, first show the experimental feature that makes the ingredient necessary.

9. **Do not undersell the achievement.**
   The manuscript should make clear that the model reproduces difficult measured features, not merely that a calculation was performed. If justified by the figures and error analysis, use careful refinement-quality language to describe what the method enables.

## Primary manuscript story

The manuscript should follow this logic:

1. Present the experimental diffraction data and the physical problem.
2. Show the specific measured features that require additional model ingredients, especially unexpected reflections, long-tail mosaicity, and the 003/star feature.
3. Explain the model ingredients in physical terms: sample geometry, detector geometry, incident angle, beam position, divergence, wavelength spread, mosaicity, bandwidth, structure factor, and resolution effects.
4. Introduce the two-component mosaicity model, including the long Lorentzian tail, early enough that the reader understands why it is necessary.
5. Explain the 003/star feature before using the final fit to validate it.
6. Show how measured data and calculated intensity are projected onto interpretable Q-space trajectories.
7. Demonstrate, with direct overlays, that the model reproduces the measured line shapes and non-obvious detector features for Bi2Se3 and Bi2Te3.
8. Use the overlays, propagated/systematic error discussion, and structure-factor treatment to support the refinement-quality interpretation.
9. Move computational implementation details to the supplementary material.
10. Treat PbI2, stacking faults, and diffuse scattering as a later or separate part of the story unless specifically being drafted.

## Main result to emphasize

The paper is not mainly about a software package. It is about showing that a physically constrained detector-space forward model can reproduce measured diffraction features that would otherwise be difficult to interpret.

The key claim should be:

> When the instrumental geometry, sample orientation, beam distribution, wavelength bandwidth, detector effects, mosaicity, projection procedure, and structure factor are handled consistently, the model reproduces the measured Bi2Se3 and Bi2Te3 line shapes, relative intensities, and non-obvious detector features well enough to support refinement-quality interpretation.

Use “refinement-quality” carefully. The claim must be tied to the plotted data/model overlays, the propagated/systematic error discussion, and the structure-factor/CIF/SIF treatment.

Whenever possible, support this claim visually with data/calculation overlays rather than only prose.

## Figure strategy

### Required figure types

For **Bi2Se3** and **Bi2Te3**, prepare figure sets that include:

1. A measured 2D diffraction image.
2. Q / QR / Qz trajectories or integration regions marked on the image.
3. Extracted projections plotted versus **Qz**.
4. Measured intensity and calculated intensity overlaid on the same axes.
5. Labels that identify the relevant reflection family, scalar m label, QR value, branch, and/or incident angle.

A useful structure is:

- One figure for the 2D image and selected trajectories / integration bands.
- One multi-panel figure for the extracted Qz projections and fit overlays.
- Repeat the same logic for Bi2Se3 and Bi2Te3.

### Figure-writing rules

- Make the measured data visually prominent.
- Do not obscure the data with too many circles, markers, colored guides, or labels.
- Avoid figures that look like artistic graphics rather than measured diffraction data.
- Use guide lines, trajectories, or boxes only when they clarify the extraction procedure.
- Captions must explain what the reader is seeing, how the plotted comparison was generated, and what conclusion the reader should draw.
- Caption/text redundancy is allowed when it helps the reader catch the main point.
- Figures should make the quality of the fit obvious without requiring the reader to understand the software.
- Insert more figures than the final paper will probably keep; remove, merge, or move figures to the supplement later.

## Caption strategy

Captions should teach the paper. They should not merely identify panels.

Each main-text figure caption should state:

- what material is shown;
- what is measured and what is calculated;
- what solid lines, dashed lines, boxes, rods, projection bands, and symbols mean;
- what coordinate convention is being used;
- how projected profiles were generated;
- what feature the reader should notice;
- how the figure supports the manuscript claim.

Do not avoid redundancy between captions and main text. Readers often inspect figures before reading the full section. Important interpretive points should appear in the caption even if they also appear in the text.

Weak caption pattern:

> Detector image and Qz projections for Bi2Se3.

Preferred caption pattern:

> Measured Bi2Se3 detector image with the fixed-in-plane reciprocal-space trajectory used for projection. Dashed bounds show the detector-space integration region. The lower panels compare measured and calculated intensity after applying the same projection to both data and model, showing that the fitted geometry and mosaic distribution reproduce the observed line shape.

## Projection and coordinate-space guidance

The main text should present projections in a way that is natural for diffraction readers.

Use **Qz** as the main horizontal or projected coordinate for line profiles when that is the physical interpretation. Use **QR** or the scalar **m** reflection-family label to identify which reciprocal-space trajectory is being sampled.

It is acceptable that the implementation uses 2theta–phi coordinates or a “caked” representation internally. However, do not make 2theta–phi optimization the organizing principle of the main manuscript.

The manuscript should say, in effect:

- The data are projected along trajectories corresponding to fixed QR / reflection-family conditions.
- The resulting profiles are reported versus Qz.
- Because of mosaicity, beam divergence, wavelength spread, finite incident-angle uncertainty, and detector/sample resolution, these projected coordinates are not a perfect ideal-Q measurement.
- The calculation is subjected to the same projection and resolution effects as the data.
- Therefore, the data/model comparison remains meaningful and is the central test of the method.

Do not overstate the exactness of the Q-space projection. Acknowledge that the effective Q interpretation is resolution-limited or compromised by mosaicity and experimental imperfections.

If a plotted reciprocal-space trajectory is claimed to show where a diffraction feature should occur, it must include the relevant detector geometry and sample-orientation parameters. If the current plotted trajectory does not include sample rotation, chi, or other alignment distortions, do not explain peak offsets as physical effects. Either fix the trajectory calculation or explicitly describe the overlay as an approximate projection guide.

## Two-component mosaicity

The two-component mosaicity model must be introduced early and supported with evidence immediately.

The manuscript should explain that a narrow mosaic distribution alone cannot account for all observed reflections. In particular, at some incident angles, reflections appear that would not be expected unless the sample has a long-tail mosaic component.

The long Lorentzian tail is not a minor implementation detail. It is an important physical insight. It should be presented as necessary for reproducing the measured intensities and line shapes.

The mosaicity equation or a compact version of it likely belongs in the main text. The Lorentzian-tail component is not just implementation machinery; it is part of the physical explanation for why reflections appear under incident-angle conditions where a narrow mosaic distribution would fail.

When drafting this section:

- State the observational problem first.
- Identify the reflections or incident-angle condition that make the problem visible.
- Explain why a narrow mosaic component is insufficient.
- Introduce the long-tail component as the physical resolution.
- Show or cite a figure that demonstrates the effect.
- Then connect the mosaicity model to the quality of the global fit.

## 003 / star-feature explanation

The manuscript must explicitly explain the star-like or line-like feature associated with the m = 0, L = 3 region.

Do not treat this feature as an unexplained artifact or as ordinary reflectivity. The current interpretation is that the finite Ewald-sphere thickness from wavelength bandwidth intersects the small 003 Bragg sphere in a way that, combined with mosaic extension, redistributes intensity into the observed detector feature.

Required presentation:

1. Show the detector-space feature clearly.
2. Include the nearby 003 peak in the figure or crop.
3. State that disabling the 003 reflection in the calculation removes both the direct 003 peak and the associated feature, if this remains true after verification.
4. Add a schematic showing the Ewald sphere with bandwidth thickness, the 003 Bragg sphere, and the relevant overlap region.
5. Explain why the feature could otherwise be mistaken for total reflectivity or an unrelated detector artifact.
6. In the final data/model comparison, point out that the full model reproduces this feature.

This explanation should appear before the final fit-quality figure, so the final comparison becomes the payoff.

## Indexing and labeling

Use labels that a diffraction reader can interpret.

Avoid relying only on internal labels such as `M1`, `M2`, “plus branch,” or “minus branch.” These may be used only if they are clearly defined and tied to physical indices.

Preferred labels include:

- The scalar in-plane family label m, with explicit (h,k,l) labels where needed.
- Reflection-family labels.
- Equivalent-ring or powder-manifold labels, with the convention defined in the caption or text.
- QR values as secondary numerical information.

If several symmetry-equivalent reflections contribute to the same powder ring or reciprocal-space manifold, define a compact convention. For example, one m label may represent a family of equivalent in-plane reflections, but the text or caption must state that convention explicitly.

The reader should always be able to tell which crystal reflection, reflection family, or reciprocal-space radius is being discussed.

For hexagonal Bi2Se3 and Bi2Te3, use the compact scalar reflection-family label:

\[
m = h^2 + h k + k^2 .
\]

Use this only after defining it. Avoid pair-style scalar labels; use \(m=1\), \(m=3\), or explicit \((h,k,l)\) labels when space allows.

Every symbol must be defined before use, including \(Q_R\), \(Q_z\), \(L\), \(m\), explicit \((h,k,l)\) labels, branch labels, projection width, and reciprocal lattice units.

## Main text versus supplementary material

### Main text should contain

- The physical motivation.
- The main experimental data.
- The model ingredients in physical language.
- The two-component mosaicity argument.
- The Q / QR / Qz projection concept.
- Data/calculation overlays demonstrating the fit quality.
- The Bi2Se3 and Bi2Te3 results.
- Enough experimental details to understand what data were collected and what data are shown.
- The mosaicity equation or enough of it to explain how the two-component distribution is calculated.
- The 003/star-feature explanation and its Ewald-sphere bandwidth schematic.
- The propagated/systematic error introduced when detector pixels are converted to projected coordinates and fitted values.
- The structure-factor/CIF/SIF discussion needed to justify the refinement-quality claim.
- A statement about whether occupancies or structural parameters were fitted, including the size of any occupancy changes.

### Supplementary material should contain

- 2theta–phi implementation details.
- “Caked” coordinate transformation details.
- Sub-pixelation and binning procedures.
- Lookup-table or detector remapping details.
- Monte Carlo sampling details.
- Sampling of beam position, divergence, and wavelength spread.
- Mosaic-event sampling details.
- Computational efficiency and optimization arguments.
- Full profile arrays or large collections of peak-by-peak fits.
- h-BN fitting procedure, if it is part of the analysis pipeline.
- Additional incident-angle data not shown in the main text.
- Full CIF/SIF contents if they are too long for the main text.
- Full propagated-error derivations after the main paper explains the result and why it matters.
- Additional validation plots supporting the 003/star-feature interpretation.

The main paper may mention that computational optimizations were used for efficiency, but the detailed algorithm should be deferred to the supplement.

## Experimental-section requirements

The manuscript must state what data were collected, not only what data are shown.

For each material, include:

- Incident angles collected.
- Incident angles shown in the main text.
- Any incident angles moved to the supplementary material.
- The reason selected angles are representative or useful.

Do not let the reader infer that only the displayed incident angles were measured if more were collected.

## Writing style

Use clear, direct scientific prose. The paper should bring the reader along through the analysis rather than assuming they already understand the workflow.

When drafting or revising:

- Prefer physical explanations over implementation explanations.
- Expand compressed method statements into complete explanatory paragraphs.
- Use captions as part of the explanation, not merely as labels.
- Repeat central interpretive points in captions and main text when redundancy improves comprehension.
- Define all internal terminology before using it.
- Keep the reader oriented in detector space, reciprocal space, and projected Q-space.
- Make clear what is measured, what is calculated, and how they are compared.
- Do not let software terminology dominate the paper.
- Do not introduce unnecessary coordinate systems in the main text.
- Do not hide important results in the supplement before they have been used to make the paper’s main argument.

## Immediate drafting priorities

For the next manuscript revision, focus on:

1. Bi2Se3 and Bi2Te3 only.
2. Readable 2D diffraction images with clear trajectories, integration regions, and material labels.
3. Qz projection figures with measured/calculated overlays.
4. Teaching captions that define the plotted guides, projection bounds, axes, and conclusions.
5. A readable m-indexed reflection-family labeling convention, using a defined scalar \(m = h^2 + h k + k^2\) for hexagonal films.
6. An early two-component mosaicity section with direct evidence.
7. A 003/star-feature explanation with a detector crop and Ewald-sphere bandwidth schematic.
8. A clear explanation of why the projections are useful even though they are not perfect ideal-Q measurements.
9. A structure-factor/CIF/SIF and occupancy-change discussion.
10. A propagated/systematic error discussion in the main text.
11. Careful refinement-quality framing tied to the overlays and uncertainty discussion.
12. A table or paragraph listing all collected incident angles.
13. A supplementary-material outline for computational details.

Do not prioritize PbI2, stacking faults, diffuse scattering, or software release polish until the Bi2Se3 and Bi2Te3 manuscript story is clear.

## Meeting-prep triage rule

When preparing a short-turnaround draft for Paul, prioritize visible, low-risk improvements first unless correctness is at stake.

Default order:

1. Make figures readable.
2. Rewrite captions so they teach the reader what to notice.
3. Define labels, axes, and symbols.
4. Add short main-text explanations for structure factor, propagated error, and refinement-quality framing.
5. Add or revise the mosaicity-evidence figure.
6. Add the 003/star-feature crop and schematic.
7. Fix high-risk geometry or simulation issues last, unless the current figure would otherwise be misleading.

Do not confuse ease order with scientific importance. The 003/star feature and Q-space trajectory correctness are scientifically important, but they may require more technical work than caption and figure readability fixes.

## Revision checklist for agents

Before returning a manuscript edit or new section, check the following:

- Does this text put the paper before the software?
- Does it explain the physics before the optimization?
- Does it use Q, QR, Qz, m-indexed reflection-family labels, and reciprocal-space language where appropriate?
- Does it avoid unnecessary software-native terminology in the main text?
- Does it make the measured data and calculated fit comparison clear?
- Does it preserve the central claim that the model quantitatively reproduces the line shapes?
- Does it introduce two-component mosaicity early enough and with evidence?
- Does it label reflections in a way a diffraction reader can understand?
- Does it indicate which details belong in the supplement?
- Does it add enough figure-driven explanation for the reader to follow the analysis?
- Does the caption tell the reader what to notice, not just what is plotted?
- Does the text show the data before explaining the model correction?
- Does the mosaicity section include direct evidence for the Lorentzian tail?
- Does the paper explain the 003/star feature before using it as model-validation evidence?
- Are sample-orientation effects included in plotted Q-space trajectories, or is the limitation stated?
- Are \(Q_R\), \(Q_z\), \(L\), \(m\), and any explicit \((h,k,l)\) labels defined before use?
- Does the main text discuss propagated/systematic error rather than hiding it in the supplement?
- Does the manuscript state what structural model, CIF/SIF file, occupancy changes, or structure-factor fitting were used?
- Does the final comparison make the refinement-quality claim visible?

## Forbidden or discouraged patterns

Avoid these patterns unless there is a specific reason:

- Making software cleanup the next manuscript bottleneck.
- Leading the main text with 2theta–phi implementation details.
- Calling internal coordinates or labels self-explanatory.
- Showing plots that obscure the measured data.
- Using QR numbers without connecting them to m or a defined reflection family.
- Compressing multi-step analysis procedures into one sentence.
- Presenting optimization choices as if they were the physics.
- Delaying the mosaicity evidence until late in the paper.
- Omitting figures that are needed to understand the method.
- Moving the strongest Bi2Se3 / Bi2Te3 fit evidence out of the main paper.
- Treating caption/main-text redundancy as a problem when the repeated point is central.
- Presenting Q-space trajectory overlays as exact when sample-orientation effects are missing.
- Explaining peak offsets as physical effects before ruling out incomplete geometry or projection artifacts.
- Treating the 003/star feature as an unexplained artifact after the model can reproduce it.
- Moving propagated/systematic error, mosaicity logic, or structure-factor/refinement evidence entirely to the supplement.
- Using refinement-quality language without tying it to overlays, error propagation, and structure-factor treatment.

## One-sentence governing rule

Write the manuscript so that a diffraction physicist can see the data, understand why each model ingredient is necessary, and recognize from the plotted overlays, uncertainty discussion, and structure-factor treatment that the model captures the experimental line shapes and non-obvious detector features quantitatively.
