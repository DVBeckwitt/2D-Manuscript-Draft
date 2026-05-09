# Blast check: chapter-by-chapter concision pass

Basis: `AGENTS.md`, the Maselli meeting transcript, and the current Maselli-revised LaTeX package. The goal is not to make the manuscript short at all costs. The goal is to cut material that delays the physics-first story: measured Bi2Se3/Bi2Te3 data, Q/QR/Qz trajectories, Qz overlays, and the two-component mosaicity evidence.

## Global rule for this pass

Keep text that helps a diffraction reader see one of four things:

1. What was measured.
2. What physical effect is modeled.
3. How the measured and calculated intensities are compared.
4. Why the Bi2Se3/Bi2Te3 overlays prove the model works.

Cut or move text that mainly explains software convenience, implementation bookkeeping, broad literature context, or parameter auditing before the fit evidence appears.

Recommended target reductions, after real figures are inserted:

- Introduction: reduce by about 25–35%.
- Diffraction Model: reduce by about 20–30% in the main text; move coordinate bookkeeping to SI.
- Mosaicity: keep mostly intact, but replace schematic-only explanation with evidence figure.
- Refinement Workflow: reduce prose by about 40% because the table already carries the step structure.
- Ordered Results: remove all future-tense scaffold language and make the section figure-driven.
- Discussion/Conclusion: reduce by about 35–45% by removing method repetition and meta-comments.
- PbI2: keep out of the active main text for now.

## 1. Introduction

### Current issue

The introduction spends too much space proving that layered films are broadly important before it gets to the manuscript’s central claim. The first paragraph lists many material families. That breadth is defensible, but it dilutes the Bi2Se3/Bi2Te3 ordered-film validation story that Dr. Maselli wants front and center.

### Change 1: compress the opening paragraph

Current function: establish broad motivation across PbI2, bismuth chalcogenides, TMDs, MXenes, graphene oxide, etc.

Recommended change: keep only one general sentence plus two examples directly tied to this manuscript.

Suggested replacement:

```latex
For layered thin films, the structural question is often not only which phase is present, but how the layer normals are oriented relative to the substrate. This orientation controls the response of many van der Waals and layered materials, including topological bismuth chalcogenides and layered halides. The films considered here are therefore a useful test case for a diffraction model that must recover both crystallographic intensity and orientational disorder from area-detector WAXS data.\cite{Jerng2013,Arendse2023,Fischer2023MOFGIWAXS}
```

This removes the long family catalog. Those additional citations can move to a broader background paragraph or SI if needed.

### Change 2: shorten the orientational-limits explanation after Fig. 1

The paragraph after Fig. 1 walks through single crystal, 3D powder, and 2D powder in detail. The figure already shows the first two limits. The text should spend fewer words on single-crystal and 3D-powder basics and more on why 2D powders are hard.

Suggested replacement:

```latex
Figure~\ref{fig:intro_2x3} contrasts the limiting cases relevant to this work. Single crystals give sparse Bragg spots, and fully random 3D powders give Debye--Scherrer rings. A 2D powder is intermediate: crystallites share an approximately aligned layer normal but are azimuthally disordered in the film plane. Off-specular reflections therefore form reciprocal-space rings about $Q_z$, while $(00L)$ reflections remain concentrated near the specular direction. Mosaicity broadens these intersections into detector arcs and cap-like specular intensity, making the full 2D line shape a direct constraint on orientation and resolution.\cite{Kaganer1999,SmilgiesBlasini2007,Hexemer2015}
```

### Change 3: cut the methods-survey paragraph by half

The paragraph beginning with “This hybrid detector-space information...” is correct but too encyclopedic. The ODF/preferred-orientation discussion and recent radial-profile discussion can be compressed unless the paper directly compares against those methods.

Suggested replacement:

```latex
Standard WAXS reductions often collapse the area detector to one-dimensional profiles. That is efficient for nearly isotropic powders, but it discards or deweights the arcs and specular caps that carry the strongest constraints on out-of-plane texture, mosaic tails, and Bragg-rod line shape in 2D powders. Rather than refine a general orientation distribution, we use the experimentally motivated symmetry of these films: randomized in-plane orientation and a low-dimensional out-of-plane mosaic distribution. The model therefore refines the full detector image while keeping the parameters tied to the physical geometry of the film.\cite{Kaganer1999,SmilgiesBlasini2007,Hexemer2015,Savikhin2020}
```

### Change 4: split the contribution paragraph

The final introduction paragraph currently contains prior work, Nookiin, all model ingredients, current scope, and PbI2 deferral in one paragraph. It should be three short paragraphs or one shorter contribution paragraph.

Suggested replacement:

```latex
Here we present a forward model for WAXS from 2D powders that carries the calculation from crystallographic structure and film geometry to the measured area-detector image. The model includes detector geometry, grazing-incidence propagation, finite beam phase space, mosaicity, and structure-factor intensity.

The main result is demonstrated on ordered Bi$_2$Se$_3$ and Bi$_2$Te$_3$ films. For these films, the same model reproduces detector positions, local line shapes, and projected intensity profiles along indexed $Q_r$/m trajectories plotted versus $Q_z$.

Applications to PbI$_2$ diffuse scattering and stacking disorder use the same framework, but are deferred until the ordered-film validation is shown clearly.
```

## 2. Diffraction Model

### Current issue

This section is mostly aligned with the philosophy, but it still tries to carry both the physical model and implementation-level bookkeeping. The main text should keep the physical construction and push detailed coordinate conventions, sampling choices, and some weighting details to SI.

### Change 1: shorten the section-opening paragraph

Current paragraph lists every refinement objective. That repeats the workflow section.

Suggested replacement:

```latex
The forward model predicts the detector image produced by an indexed set of reciprocal-lattice vectors. For each reflection, the calculation determines the allowed exit rays, maps them to detector pixels, weights them by the structure factor and experimental transmission terms, and redistributes their intensity according to the mosaic distribution. The same detector-space prediction is then compared with measured peak positions, local line shapes, integrated Bragg intensities, and final $Q_z$ projection profiles.
```

### Change 2: move low-level coordinate details to SI

Keep in main text:

- $\mathbf{Q}=\mathbf{k}_f-\mathbf{k}_i$.
- Ewald/Bragg-sphere intersection.
- detector mapping exists.
- finite beam footprint and incidence angle are modeled.
- refraction/absorption weights are included.

Move to SI or compress heavily:

- detector tilt convention $\beta,\gamma,\chi$ unless needed by a figure;
- offsets $z_B,z_S$ and arm vectors $\vec g,\vec g'$ unless used in active results;
- exact Snell-law implementation;
- detailed list of beam widths, divergences, finite window, and discarded rays.

Suggested concise geometry block:

```latex
For each trial incident ray, the model computes the sample intersection, applies the incidence geometry and optical corrections, finds the reciprocal-space intersections that satisfy elastic scattering, and propagates the resulting exit rays to the detector. Finite beam size, divergence, footprint truncation, detector tilt, refraction, and absorption enter as experimental resolution and intensity terms. Their role in the main text is not to define new physics, but to ensure that the calculated image carries the same geometric broadening and attenuation as the measurement.
```

### Change 3: compress the structure-factor prose after the equation

The structure-factor equation should stay. The paragraph after it can be shorter.

Suggested replacement after Eq. `structure_factor`:

```latex
Here $o_a$, $f_a(Q)$, $\mathbf r_a$, and $\mathbf U_a$ are the occupancy, atomic form factor, fractional position, and anisotropic displacement tensor for atom $a$. Symmetry constraints are retained during refinement, so only the independent crystallographic parameters are varied. The detector weight for each allowed ray is multiplied by $|F_{\mathbf G}|^2$ before mosaic and experimental broadening are applied.
```

This removes the continuous-$F(\mathbf Q)$ aside unless diffuse scattering is reintroduced.

## 3. Mosaicity

### Current issue

This is the most philosophically important section and should not be overcompressed. The concise fix is structural: replace schematic explanation with early evidence. Dr. Maselli wants the long Lorentzian tail to appear as a physical necessity, not as a parameter choice.

### Change 1: insert the evidence figure before or immediately after the two-component paragraph

The paragraph beginning “The key experimental point...” is good. It needs the actual evidence figure, not only a placeholder comment.

Required figure content:

- one Bi2Se3 or Bi2Te3 detector crop or Qz profile;
- measured intensity;
- narrow-core-only calculation;
- Gaussian-plus-Lorentzian calculation;
- label the incident angle and the off-condition reflection(s);
- caption says explicitly: these reflections are visible only with a long-tail component.

### Change 2: remove or merge the standalone mosaic schematic if the evidence figure is strong

The `2d_mosaic.png` schematic is simple and may be redundant once the four-panel mosaic figure and evidence figure are present. Use either:

- evidence figure + four-panel reciprocal/detector schematic, or
- a combined figure with evidence as panel (e).

Do not keep three separate mosaic figures unless each one does a distinct job.

### Change 3: move the surface-density derivation to SI if the main text gets crowded

The equation for $\rho(\vartheta)$ is physically meaningful, but it is not the main result. In the main text, it can be reduced to one sentence unless reviewers need the derivation.

Suggested concise version:

```latex
After random in-plane rotation, the one-dimensional tilt density becomes an axially symmetric surface density on the Bragg sphere, with the usual $1/\sin\vartheta$ Jacobian. This density supplies the ray weights used to distribute $I_0$ over mosaic-broadened exit directions; the explicit normalized form is given in the supporting information.
```

Keep the equation in the main text only if it is needed to make the physical model credible before the results.

## 4. Refinement workflow

### Current issue

This section duplicates itself. The first paragraph explains the staged workflow, the table explains the staged workflow, and the paragraphs after the table explain the staged workflow again. Dr. Maselli wants enough step-by-step explanation, but not three versions of the same explanation.

### Change 1: let the table carry the details

Keep the table. Compress the prose before and after it.

Suggested opening:

```latex
We use a staged refinement because geometry, mosaicity, and crystallographic intensity are strongly correlated in a fully global fit. Each stage uses the detector-space observable most sensitive to one parameter class before the next class is introduced. Table~\ref{tab:refinement_workflow} summarizes the ordered-film workflow used for Bi$_2$Se$_3$ and Bi$_2$Te$_3$.
```

### Change 2: shorten the post-table explanation to two paragraphs

Suggested replacement for lines after the table:

```latex
The instrumental and alignment stages fix where an ideal reflection should appear on the detector. Direct-beam and calibrant data define the beam phase space and detector mapping, while indexed sample reflections determine the incidence condition, sample offsets, and goniometer misalignment.

The remaining stages refine what the peaks look like and how intense they are. Local detector profiles constrain the shared Gaussian-plus-Lorentzian mosaic distribution. Bragg ROI integrals constrain the ordered structure-factor parameters, and the final validation projects both measured and calculated images along the same indexed $Q_r$/m trajectories for comparison versus $Q_z$.
```

Then keep one sentence:

```latex
Implementation details required for efficiency, including $2\theta$--$\phi$ remapping, caked fields, lookup tables, and Monte Carlo sampling, are described in the supporting information.
```

### Change 3: shorten row 5 of the table

Current row 5 parameter column is too long. Replace with:

```latex
Image scale factors and ordered structure-factor parameters
```

Put the full list of occupancies, coordinates, displacements, and ADPs in the Diffraction Model or SI.

## 5. Ordered Bi2Te3/Bi2Se3 Results

### Current issue

This section currently reads like revision instructions rather than a results chapter because real figures are still missing. Once the figures exist, all “should be shown” language must become direct result language.

### Change 1: remove future-tense scaffold prose after figures are inserted

Current language:

> “For each material, the final main-text comparison should be shown in two parts...”

Replace with result-forward language:

```latex
Figures~X and~Y show the ordered-film validation for Bi$_2$Se$_3$ and Bi$_2$Te$_3$. For each material, the detector image identifies the indexed $Q_r$/m trajectories used for projection, and the companion panels compare measured and calculated intensity along those trajectories as functions of $Q_z$.
```

### Change 2: keep the projection caveat, but move it closer to the first overlay figure or into the caption

The paragraph explaining that $Q_z$ is not an ideal resolution-free coordinate is important. It should appear immediately before the first Qz overlay or in the caption, not as abstract prose detached from data.

Concise version:

```latex
The horizontal coordinate is reported as $Q_z$ along the selected trajectory. Because mosaicity, divergence, wavelength spread, incidence-angle uncertainty, and detector sampling broaden the effective scattering condition, the profiles are not ideal reciprocal-space cuts. The comparison is still direct because the same projection and resolution effects are applied to the calculated image.
```

### Change 3: move or shrink the structure-parameter table

The current ordered-parameter table interrupts the main result. Dr. Maselli’s philosophy makes the fit overlays primary and the parameter audit secondary.

Preferred change:

- Move Table `ordered_sf_parameters` to SI as `Table S1`.
- In the main text, keep one sentence:

```latex
The fitted lattice, coordinate, occupancy, and displacement parameters remained within the structural-prior ranges summarized in Table~S1, so the line-shape agreement does not require unphysical changes to the ordered structures.
```

Acceptable alternative if the table stays in main text:

- reduce it to three columns: Material / fitted lattice and coordinates / note on occupancies and ADPs;
- remove long literature-comparison clauses from table cells.

### Change 4: make this chapter the shortest prose-to-figure ratio in the paper

After the figures are added, this section should mostly be figure references and direct interpretation. Target: 2–3 paragraphs plus figures, not a long methods discussion.

## 6. PbI2 / diffuse-scattering results

### Current issue

This section is correctly inactive in `main.tex`. It should remain out of the main manuscript until the Bi2Se3/Bi2Te3 story is complete.

### Change if reintroduced later

Do not reintroduce PbI2 as a full second results chapter in the first complete draft. Use one of these structures:

1. one short “extension” paragraph plus one figure, or
2. a separate later manuscript/section after the ordered-film validation is accepted by the advisor.

The concise rule: PbI2 should not compete with the ordered-film demonstration unless the manuscript has already proven the model with Bi2Se3/Bi2Te3 overlays.

## 7. Discussion and conclusion

### Current issue

The discussion currently restates the method, projection caveat, two-component mosaicity, parameter consistency, and figure strategy. It is accurate but slightly redundant with the Methods, Mosaicity, Workflow, and Results sections.

### Change 1: reduce to three paragraphs

Suggested structure:

1. Central result: Bi2Se3/Bi2Te3 line-shape reproduction.
2. Physical reason the result matters: projection is resolution-limited, but calculation includes the same limitations.
3. Broader implication: two-component mosaicity and future diffuse/stacking applications.

Suggested replacement:

```latex
The ordered Bi$_2$Te$_3$ and Bi$_2$Se$_3$ films provide the central validation of the model. A single forward calculation accounts for detector geometry, finite beam phase space, sample alignment, mosaicity, and ordered structure-factor intensity, then compares measured and calculated profiles along the same indexed $Q_r$/m trajectories. The key result is the direct $Q_z$ line-shape agreement, not merely visual similarity between two detector images.

These profiles are not ideal reciprocal-space cuts. Mosaicity, divergence, wavelength spread, incidence-angle uncertainty, and detector sampling all broaden the effective meaning of $Q_z$. The useful point is that the same broadening is present in the calculated image before projection, so the overlay tests the complete experimental model rather than an idealized structure factor alone.

The two-component mosaic distribution is required to reproduce both the main off-specular arc widths and weak off-condition specular intensity. Once the ordered-film validation is shown clearly, the same framework can be extended to PbI$_2$ and other cases where diffuse scattering or stacking disorder modifies the Bragg-rod intensity.
```

### Change 2: remove meta-writing instructions from final discussion

The sentence beginning “The ordered-film result is clearest when it is presented...” is useful as a drafting note but should not remain in a finished manuscript. Once figures are inserted, replace it with a sentence about what the figures show.

## Highest-priority cuts before the next advisor meeting

1. Compress the introduction’s material-family survey.
2. Replace the long post-Fig. 1 orientational-limits paragraph with a shorter 2D-powder-focused version.
3. Reduce the workflow prose because the table already explains the staged refinement.
4. Move the ordered structure-parameter table to SI or shrink it substantially.
5. Convert all “should show” results text into “we show” text once the real figures are inserted.
6. Keep PbI2 out of the active main-text flow.
7. Remove final-discussion meta-comments about how the paper should be organized.
8. Add the Lorentzian-tail evidence figure; do not compensate for its absence with more prose.

## One-line diagnosis

The draft should become more concise by cutting breadth, redundancy, and implementation bookkeeping, not by cutting the step-by-step physics explanation needed to understand the Bi$_2$Se$_3$/Bi$_2$Te$_3$ Qz overlay figures.
