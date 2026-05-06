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
   Use the language readers expect: **Q**, **QR**, **Qz**, **HK/HKL indices**, **Bragg rods**, **Bragg positions**, **reciprocal space**, **incident angle**, **mosaicity**, **resolution**, and **line-shape fitting**. Avoid leading the main text with software-native language such as “caked space,” internal branch labels, configuration scripts, lookup tables, or optimization terminology.

4. **Physics first; optimization later.**
   The main text should explain the physical model and the experimental comparison. Computational optimizations belong in the supplementary material unless they are absolutely necessary to understand the physics.

5. **Figures drive the paper.**
   The paper should be written around clear figures. It is better to begin with too many figures and remove or consolidate later than to write with too few and create a communication problem.

6. **Explain more than feels necessary.**
   Do not compress a complicated procedure into a single sentence. If a step involves detector space, reciprocal-space trajectories, integration bands, projection, fitting, or simulation, explain it step by step. What is obvious to the author is probably not obvious to the reader.

## Primary manuscript story

The manuscript should follow this logic:

1. Present the experimental diffraction data and the physical problem.
2. Explain the model ingredients in physical terms: sample geometry, detector geometry, incident angle, beam position, divergence, wavelength spread, mosaicity, and resolution effects.
3. Introduce the two-component mosaicity model, including the long Lorentzian tail, early enough that the reader understands why it is necessary.
4. Show how measured data and calculated intensity are projected onto interpretable Q-space trajectories.
5. Demonstrate, with direct overlays, that the model reproduces the measured line shapes for Bi2Se3 and Bi2Te3.
6. Move computational implementation details to the supplementary material.
7. Treat PbI2, stacking faults, and diffuse scattering as a later or separate part of the story unless specifically being drafted.

## Main result to emphasize

The paper is not mainly about a software package. It is about showing that the calculation captures the experimental imperfections well enough to reproduce the measured diffraction profiles quantitatively.

The key claim should be:

> By including the relevant experimental geometry, beam effects, mosaicity, and projection procedure, the model reproduces the measured line shapes in the Bi2Se3 and Bi2Te3 data.

Whenever possible, support this claim visually with data/calculation overlays rather than only prose.

## Figure strategy

### Required figure types

For **Bi2Se3** and **Bi2Te3**, prepare figure sets that include:

1. A measured 2D diffraction image.
2. Q / QR / Qz trajectories or integration regions marked on the image.
3. Extracted projections plotted versus **Qz**.
4. Measured intensity and calculated intensity overlaid on the same axes.
5. Labels that identify the relevant reflection family, HK/HKL index, QR value, branch, and/or incident angle.

A useful structure is:

- One figure for the 2D image and selected trajectories / integration bands.
- One multi-panel figure for the extracted Qz projections and fit overlays.
- Repeat the same logic for Bi2Se3 and Bi2Te3.

### Figure-writing rules

- Make the measured data visually prominent.
- Do not obscure the data with too many circles, markers, colored guides, or labels.
- Avoid figures that look like artistic graphics rather than measured diffraction data.
- Use guide lines, trajectories, or boxes only when they clarify the extraction procedure.
- Captions must explain what the reader is seeing and how the plotted comparison was generated.
- Figures should make the quality of the fit obvious without requiring the reader to understand the software.
- Insert more figures than the final paper will probably keep; remove, merge, or move figures to the supplement later.

## Projection and coordinate-space guidance

The main text should present projections in a way that is natural for diffraction readers.

Use **Qz** as the main horizontal or projected coordinate for line profiles when that is the physical interpretation. Use **QR** or HK/HKL reflection-family labels to identify which reciprocal-space trajectory is being sampled.

It is acceptable that the implementation uses 2theta–phi coordinates or a “caked” representation internally. However, do not make 2theta–phi optimization the organizing principle of the main manuscript.

The manuscript should say, in effect:

- The data are projected along trajectories corresponding to fixed QR / reflection-family conditions.
- The resulting profiles are reported versus Qz.
- Because of mosaicity, beam divergence, wavelength spread, finite incident-angle uncertainty, and detector/sample resolution, these projected coordinates are not a perfect ideal-Q measurement.
- The calculation is subjected to the same projection and resolution effects as the data.
- Therefore, the data/model comparison remains meaningful and is the central test of the method.

Do not overstate the exactness of the Q-space projection. Acknowledge that the effective Q interpretation is resolution-limited or compromised by mosaicity and experimental imperfections.

## Two-component mosaicity

The two-component mosaicity model must be introduced early and supported with evidence immediately.

The manuscript should explain that a narrow mosaic distribution alone cannot account for all observed reflections. In particular, at some incident angles, reflections appear that would not be expected unless the sample has a long-tail mosaic component.

The long Lorentzian tail is not a minor implementation detail. It is an important physical insight. It should be presented as necessary for reproducing the measured intensities and line shapes.

When drafting this section:

- State the observational problem first.
- Identify the reflections or incident-angle condition that make the problem visible.
- Explain why a narrow mosaic component is insufficient.
- Introduce the long-tail component as the physical resolution.
- Show or cite a figure that demonstrates the effect.
- Then connect the mosaicity model to the quality of the global fit.

## Indexing and labeling

Use labels that a diffraction reader can interpret.

Avoid relying only on internal labels such as `M1`, `M2`, “plus branch,” or “minus branch.” These may be used only if they are clearly defined and tied to physical indices.

Preferred labels include:

- HK or HKL indices.
- Reflection-family labels.
- Equivalent-ring or powder-manifold labels, with the convention defined in the caption or text.
- QR values as secondary numerical information.

If several symmetry-equivalent reflections contribute to the same powder ring or reciprocal-space manifold, define a compact convention. For example, one label may represent a family of equivalent HK reflections, but the text or caption must state that convention explicitly.

The reader should always be able to tell which crystal reflection, reflection family, or reciprocal-space radius is being discussed.

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
- Define all internal terminology before using it.
- Keep the reader oriented in detector space, reciprocal space, and projected Q-space.
- Make clear what is measured, what is calculated, and how they are compared.
- Do not let software terminology dominate the paper.
- Do not introduce unnecessary coordinate systems in the main text.
- Do not hide important results in the supplement before they have been used to make the paper’s main argument.

## Immediate drafting priorities

For the next manuscript revision, focus on:

1. Bi2Se3 and Bi2Te3 only.
2. Qz projection figures with measured/calculated overlays.
3. 2D diffraction images with clear trajectories or integration regions.
4. A readable HK/HKL or reflection-family labeling convention.
5. An early two-component mosaicity section with direct evidence.
6. A clear explanation of why the projections are useful even though they are not perfect ideal-Q measurements.
7. A table or paragraph listing all collected incident angles.
8. A supplementary-material outline for computational details.

Do not prioritize PbI2, stacking faults, diffuse scattering, or software release polish until the Bi2Se3 and Bi2Te3 manuscript story is clear.

## Revision checklist for agents

Before returning a manuscript edit or new section, check the following:

- Does this text put the paper before the software?
- Does it explain the physics before the optimization?
- Does it use Q, QR, Qz, HK/HKL, and reciprocal-space language where appropriate?
- Does it avoid unnecessary software-native terminology in the main text?
- Does it make the measured data and calculated fit comparison clear?
- Does it preserve the central claim that the model quantitatively reproduces the line shapes?
- Does it introduce two-component mosaicity early enough and with evidence?
- Does it label reflections in a way a diffraction reader can understand?
- Does it indicate which details belong in the supplement?
- Does it add enough figure-driven explanation for the reader to follow the analysis?

## Forbidden or discouraged patterns

Avoid these patterns unless there is a specific reason:

- Making software cleanup the next manuscript bottleneck.
- Leading the main text with 2theta–phi implementation details.
- Calling internal coordinates or labels self-explanatory.
- Showing plots that obscure the measured data.
- Using QR numbers without connecting them to HK/HKL or reflection families.
- Compressing multi-step analysis procedures into one sentence.
- Presenting optimization choices as if they were the physics.
- Delaying the mosaicity evidence until late in the paper.
- Omitting figures that are needed to understand the method.
- Moving the strongest Bi2Se3 / Bi2Te3 fit evidence out of the main paper.

## One-sentence governing rule

Write the manuscript so that a diffraction physicist can see the data, understand the reciprocal-space construction, and recognize from the plotted overlays that the model captures the experimental line shapes quantitatively.
