# Meeting Notes — Dr. Paul Maselli Manuscript Discussion

Date: 2026-04-30  
Participants: Dr. Paul Maselli and David  
Next planned meeting: 2026-05-07, 2:00 PM, subject to rescheduling  
Primary topic: manuscript strategy and next figures for the 2D-powder WAXS manuscript

## Executive summary

Dr. Maselli's central message was that the manuscript must come before further software polishing. The programming and modeling work have succeeded, especially for Bi2Te3 and Bi2Se3, but the manuscript does not yet show that success clearly enough.

The immediate focus should be Bi2Se3 and Bi2Te3. PbI2, stacking faults, diffuse scattering, and broader software-release concerns should wait until the ordered-film story is clear and figure-complete.

The main result should be that the model quantitatively reproduces measured detector-space and Qz-projected line shapes. This must be visible in the paper through figures and measured/calculated overlays.

## Main guidance

### 1. The paper is the priority

The software release is secondary. The release matters only after the paper demonstrates the value of the work. The scientific contribution depends on writing the paper and making the results understandable.

Action: do not spend major time polishing software usability, configuration scripts, or release packaging until the manuscript figures and ordered-film results are in place.

### 2. Show the successful Bi2Se3 and Bi2Te3 fits

The successful fits to Bi2Te3 and Bi2Se3 should be a major result of the paper.

The paper should include figures where the reader can see:

- the measured 2D detector data;
- the Q/Qr/Qz trajectory or integration region;
- the extracted projection plotted versus Qz;
- the measured profile and calculated profile overlaid;
- labels identifying the reflection family or relevant HK/HKL information.

### 3. Use physics language in the main text

The main manuscript should be written for a scattering/diffraction audience. Use Q, Qr, Qz, HK/HKL, Bragg rods, reciprocal-space trajectories, mosaicity, and line-shape fitting.

The 2theta-phi/caked-space method may be the better implementation, but the main text should not be organized around computational optimization. First explain the physics and the observable being compared.

### 4. Put optimization details in the supplement

Implementation details should mostly go in the supplement:

- 2theta-phi/caked-space implementation;
- sub-pixelation;
- lookup tables;
- Monte Carlo sampling;
- beam position, divergence, and wavelength sampling;
- mosaic-event sampling;
- h-BN fitting method if part of the workflow.

The main text can mention that an optimized implementation was used and then refer to the supplement.

### 5. Make the figures look like data

Some current figures risk looking too much like graphics or schematic overlays. Bragg-position circles, colored QR/Qz paths, and other annotations should not obscure the actual detector intensity.

A good figure lets the reader see the data first, then see how the model or trajectories relate to it.

### 6. Label reflections in a physically interpretable way

Internal labels such as M1/M2 are not enough unless clearly defined. HK/HKL labels or reflection-family labels will be clearer for readers.

For hexagonal symmetry and powder rings, captions can define a representative HK family or manifold rather than listing every equivalent reflection repeatedly.

### 7. Discuss imperfect Q-space interpretation honestly

The Q or Qz projection is not perfectly exact because mosaicity, incident-angle uncertainty, beam divergence, wavelength spread, and resolution effects compromise direct interpretation of Q.

This does not invalidate the comparison. The key point is that the same projection and resolution imperfections are applied to the calculation and the data.

Suggested wording:

> Although the projected coordinate is reported as Qz, finite mosaicity and instrumental resolution mean that each profile contains contributions from a distribution of local scattering conditions. The calculation is projected through the same transformation and resolution effects as the measured data, allowing direct comparison of measured and calculated line shapes.

### 8. Introduce two-component mosaicity early

The two-component mosaicity model, especially the long Lorentzian tail, should be introduced with evidence early in the manuscript.

Key evidence: some reflections are observed at incident angles where they would not be expected under a narrow mosaic distribution. Their observation implies a long-tail component.

Suggested wording:

> At a single incident angle, the detector records high-angle reflections that would not be accessible for a narrow mosaic distribution. Their presence indicates a long-tail mosaic component. Including this component is essential for reproducing the observed detector intensity and line shapes.

### 9. List all incident angles collected

The experimental section should list all incident angles collected for Bi2Se3 and Bi2Te3, even if only selected images are shown in the main text.

Needed table columns:

- material;
- incident angles collected;
- incident angles shown in main text;
- incident angles reserved for supplement or not shown;
- role in refinement or validation.

### 10. Use more figures during drafting

It is better to put too many figures into the draft and remove or consolidate later than to write with too few figures. Too few figures create a communication problem.

## Decisions

| Decision | Current action |
|---|---|
| Focus next on Bi2Se3 and Bi2Te3. | Make ordered-film figures and text the immediate priority. |
| Defer PbI2 and stacking faults. | Keep PbI2 material parked until the ordered-film story is stable. |
| Use Q/Qr/Qz/HK/HKL language in the main text. | Do not make 2theta-phi optimization the main narrative. |
| Put implementation details in the supplement. | Create supplement outline for caked-space, sub-pixelation, Monte Carlo, and h-BN fitting. |
| Use more figures in the draft. | Insert rough figure versions now and refine later. |
| Show data/model overlays directly. | Build Qz projection figures with measured and calculated curves. |
| Develop reflection-family labels. | Replace or supplement internal M labels with HK/HKL-family labels. |

## Action items

### Must do before next meeting

- [ ] Make Bi2Se3 detector/projection figure with measured data visible.
- [ ] Make Bi2Se3 Qz projection overlays with measured and calculated curves.
- [ ] Make Bi2Te3 detector/projection figure with measured data visible.
- [ ] Make Bi2Te3 Qz projection overlays with measured and calculated curves.
- [ ] Mark Q/Qr/Qz trajectories or integration regions without obscuring data.
- [ ] Draft the reflection-family labeling convention.
- [ ] Draft the two-component mosaicity / Lorentzian-tail explanation.
- [ ] Identify the figure that proves the need for Lorentzian tails.
- [ ] Draft the Q-space/projection caveat paragraph.
- [ ] Add or draft the incident-angle table.

### Good to start

- [ ] Create supplement outline for implementation details.
- [ ] Write supplement section stub for 2theta-phi/caked-space implementation.
- [ ] Write supplement section stub for sub-pixelation/binning.
- [ ] Write supplement section stub for Monte Carlo ray sampling.
- [ ] Write supplement section stub for mosaic-event sampling.
- [ ] Write supplement section stub for h-BN fitting method.

### Parked

- [ ] PbI2 diffuse-scattering finalization.
- [ ] Stacking-fault/disorder analysis narrative.
- [ ] Software release cleanup.
- [ ] Extra optimization feature explanations.
- [ ] General software feature walkthrough.

## Proposed next-draft figure plan

### Figure A — Bi2Se3 detector geometry and projection setup

Show a measured Bi2Se3 detector image with Q/Qr/Qz trajectories or selected integration regions. Data must be prominent.

### Figure B — Bi2Se3 Qz projection fits

Show measured/calculated profiles versus Qz for selected reflection families. Include plus/minus branches if relevant.

### Figure C — Bi2Te3 detector geometry and projection setup

Use the same structure as Bi2Se3.

### Figure D — Bi2Te3 Qz projection fits

Use the same structure as Bi2Se3.

### Figure E — Mosaicity evidence

Show evidence for two-component mosaicity and long Lorentzian tails. This may involve high-angle reflections observed at a small incident angle, or a comparison showing failure of a narrow mosaic distribution and success of the long-tail component.

## Draft paragraph: projection/resolution caveat

The extracted profiles are reported as functions of Qz for a selected in-plane reflection family. Because the finite mosaic distribution, incident-angle spread, wavelength spread, beam divergence, and detector resolution all contribute to the measured line shape, the projected coordinate should not be interpreted as an ideal reciprocal-space coordinate for a single perfect crystallite. Instead, it is a detector-derived projection associated with a specified Qr/Qz trajectory and integration region. The same projection is applied to the calculated detector intensity, including the same mosaic and instrumental broadening terms, so that the measured and calculated profiles can be compared directly.

## Draft paragraph: Lorentzian-tail motivation

The need for a two-component mosaic distribution is apparent from reflections observed at incident angles where they would not be reached by a narrow mosaic distribution alone. These features require a small population of crystallites with substantially larger out-of-plane misorientation. We represent this contribution with a long-tail Lorentzian component in addition to the narrow central mosaic distribution. Although the tail is weak in the local peak profiles, it is essential for reproducing the high-angle detector intensity and for obtaining a consistent description of the measured line shapes across the image.

## Draft paragraph: supplement pointer

For clarity, the main text describes the projection and refinement in reciprocal-space language. In the implementation, the detector image is transformed and sampled in a 2theta-phi representation because that coordinate system provides a convenient and efficient way to define the same trajectories, handle sub-pixelated detector intensity, and avoid repeated detector-space remapping during refinement. The optimized implementation, including sub-pixelation and Monte Carlo sampling of beam and mosaic states, is described in the Supplementary Material.
