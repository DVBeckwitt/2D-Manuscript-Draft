# Manuscript Status

Last updated: 2026-07-18

This is the canonical manuscript guidance and status document for the 2D diffraction / mosaicity manuscript. It subsumes the previous advisor notes, meeting-prep checklists, figure status, supplement status, changelogs, and manuscript task trackers. Use this file as the single source of truth for writing, rewriting, figure planning, caption drafting, structural editing, and manuscript triage.

Former detailed documents are intentionally not required for active work; git history remains the archive for exact old wording.

## Source Context

Primary meeting source: Dr. Paul F. Miceli / David manuscript discussion on 2026-04-30.

No next advisor meeting date is currently known. The earlier planned date, 2026-05-07, is past.

Current manuscript priority: Bi2Se3 and Bi2Te3 ordered-film figures and physics narrative.

Source context used during current revisions:

| Item | Role |
|---|---|
| `Voice 260430_141619_llm.txt` | Transcript/source notes from the 2026-04-30 Miceli meeting. |
| `2D-Manuscript-Draft.zip` | Manuscript repo archive used to identify current section and figure structure. |
| `Combined_variance_report_PbI2_Bi2Te3_Bi2Se3_updated.tex` | Technical/report material available for uncertainty and manuscript cross-checking. |
| `Advisor_Writing_Philosophy.md` | General writing principles distilled from the advisor's repeated guidance. Integrated below and in `AGENTS.md`. |
| `Comment_by_Comment_Response_Plan.md` | Proposed response to the 22 annotations. Independently audited below rather than accepted automatically. |
| `Commented_Manuscript_Paul_Miceli.pdf` | Exact 29-page annotated manuscript used to verify comment wording, authorship, order, and highlighted targets. |

Current `main.tex` includes:

```tex
\input{sections/introduction}
\input{sections/modelling_methods}
\input{sections/mosaicity_texture}
\input{sections/correlated_effects}
\input{sections/results_ordered}
\input{sections/results_diffuse_pbi2}
\input{sections/refinement_workflow}
\input{sections/discussion_conclusion}
```

## Status Definitions

| Status | Meaning |
|---|---|
| TODO | Not started or not yet placed into the manuscript. |
| IN PROGRESS | Work exists, but it is incomplete, unclear, or not manuscript-ready. |
| DONE | Incorporated into the manuscript or supplement in a form ready for advisor review. |
| PARKED | Important, but intentionally deferred. |
| CHECK | Needs advisor verification or a decision. |
| BLOCKED | Cannot be completed until a specific missing input, source, or calculation is available. |

## Advisor Comment Audit And Revision Tasklist - 2026-07-18

The packet inventory was checked against the annotated PDF rather than inferred from the response-plan Markdown. The 29-page PDF contains exactly 22 substantive annotations by Paul Miceli: 18 sticky notes and 4 highlighted-text comments on pages 1, 3, 5, 6, 7, 8, 11, 14, and 17. No substantive annotation is missing from the response plan.

Audit verdicts:

- **AGREE**: the packet's proposed response is appropriate as written in substance.
- **AGREE WITH MODIFICATION**: the advisor's intent is sound, but the proposed implementation is too broad, too certain, duplicative, or must be conditioned on the actual model/data.
- **DISAGREE WITH PROPOSED IMPLEMENTATION**: the underlying advisor concern is valid, but the packet prescribes wording or work that should be replaced rather than merely adjusted.
- **CHECK**: the advisor's wording is ambiguous enough that it should not be treated as a settled literal instruction.

Overall, the packet is directionally strong. The independent audit agrees with 10 proposed responses, agrees with 10 after modification, and disagrees with 2 proposed implementations (C20 and C21) while accepting the underlying advisor concerns. Current manuscript closure is 1 fully addressed, 13 partially addressed, 7 unaddressed, and 1 blocked on missing/uncertain experimental geometry. The main weaknesses of the packet are that it occasionally prescribes an implementation before the calculation has been verified, treats one heading edit too confidently, does not audit the structure-factor and optical conventions before reorganizing them, and makes a three-way optical-constant ablation sound mandatory before its scientific payoff and boundary-condition implementation are established.

One packet instruction is stale relative to the repository: the ordered Bi2Se3/Bi2Te3 detector and profile panels no longer need to be “restored.” The assets exist and already show close measured/calculated overlays. They still need readability checks, residual/uncertainty support, and verification that the displayed curves and labels are generated from the final analysis.

### Independent critical findings beyond the packet

1. **The current low-\(L\) bandwidth-scaling argument is not yet safe to publish.** The SI derives \(\Delta\psi\propto1/L\) by holding the Ewald-sphere center fixed while varying its radius. Physical wavelength variation changes both center and radius; the Bragg-law limit instead gives \(\Delta\theta_B\simeq(\Delta\lambda/\lambda)\tan\theta_B\). Treat the present \(1/L\) explanation as `CHECK` until a moving-center derivation and direct simulation/ablation establish the observed feature.
2. **The annotation's 003/006 detuning premise may compare unlike angles.** The manuscript gives \(c=28.6561\) Å and nominal 003/006 positions near \(2\theta=6^\circ/12^\circ\), which imply \(\lambda\approx1.00\) Å and conventional \(\theta_{B,003}\approx3.00^\circ\), \(\theta_{B,006}\approx6.01^\circ\). At \(\theta_i=5^\circ\), the naive Bragg-angle offsets would make 006 closer, not “very far” from condition. Do not use either subtraction as the final result; compute the full vector/orientation mismatch with actual wavelength, alignment, and angle definitions before using 003/006 visibility as evidence for the long tail.
3. **The optical implementation needs a physics audit before a sensitivity plot.** Use tangential-wavevector conservation and \(k_z=\sqrt{(\tilde n k_0)^2-k_\parallel^2}\) with the decaying branch as the primary boundary condition. Verify whether attenuation is integrated over normal depth or ray path, and convert field transmission amplitudes to flux consistently. A visually plausible ablation cannot validate an inconsistent propagation model.
4. **The near-critical handoff is not yet validation evidence.** The plotted Parratt and kinematic limits do not show the full blended forward prediction, the blend is ad hoc unless justified, and mosaic averaging of the optical branch is unspecified. Its README also records that the arrays were digitized from the annotated PDF, raster artifacts were repaired, and a visible plateau substitutes for a clipped branch. This figure is provisional and non-evidentiary; replace it with direct measured and calculated array exports and show the complete prediction against data or state the limitation.
5. **“Validation” currently means in-sample fit unless a held-out test is added.** All three listed incident angles appear to be used in refinement. Either call the examples fit/test cases and describe the evidence honestly, or reserve one or more angles/material conditions for a predictive check.
6. **The structure-factor convention is dimensionally ambiguous.** The current text combines a reciprocal vector \(\mathbf G\), fractional coordinates, an explicit \(2\pi\) phase, and a Debye-Waller exponent without stating whether reciprocal basis vectors include \(2\pi\). Establish one consistent crystallographic convention before reordering the subsection.
7. **The next-draft PbI2 scope is disproportionate.** `results_diffuse_pbi2.tex` is 348 lines versus 49 lines for ordered validation and still reports a pending transition-matrix refit. For the next advisor draft, either omit PbI2 from the main text or reduce it to the measured motivation and one final data/model panel; move the transition-matrix derivation, parameter table, and parent-stack detail to SI.
8. **Notation drift will worsen the requested equation expansion unless it is consolidated first.** The sources mix \(Q_r/Q_R\), \(h,H\), \(\phi,\varphi\), and use \(\eta\) both for mosaic-cap angular half-width and Lorentzian mixture weight. Create one notation ledger, choose conventions, and consolidate `SI_implementation_outline.tex` into the built SI rather than creating a third geometry source.
9. **The ordered overlays are visually strong but not yet provenance-ready.** This repository has PNG/JSON assets but no generation source or raw plotted arrays for the ordered panels. Record normalization and scaling, verify whether relative intensities share a meaningful scale, retain direct source arrays/scripts, add residual/uncertainty support, reduce bands that obscure data, and fix the clipped-looking Bi2Te3 detector y-axis labels.
10. **“Grown by TEM” is ambiguous and likely misleading to readers.** Define the intended growth-method acronym or replace it with the full method; otherwise TEM reads as transmission electron microscopy.

| ID | Advisor request | Audit verdict | Current state | Priority | Independent recommendation and acceptance gate |
|---|---|---|---|---|---|
| C01 | Open with 2D van der Waals films | AGREE | DONE | P1 | Resolved in the opening paragraphs and first figure of `sections/introduction.tex`. The 115-word first paragraph now follows layered-film importance -> substrate/growth-dependent azimuthal registry -> operational 2D-powder definition -> simultaneous area-detector observables, with no model or software language. The material-family catalogue was removed, the orientational-limits comparison is now the first visual, citation fit was checked, and a clean build plus rendered review of `main.pdf` pages 1-3 verified the change. |
| C02 | Explain the Ewald sphere and diffraction selection | AGREE WITH MODIFICATION | IN PROGRESS | P1 | Teach the elastic/Ewald condition once in a primary location, revise the reciprocal-space figure or caption so the sphere and intersections are visible, and cross-reference it elsewhere instead of duplicating tutorials. Accept when the single-crystal, 3D-powder, and 2D-powder detector signatures follow visibly from the drawn intersections. |
| C03 | State accomplishments and outline the paper | AGREE | IN PROGRESS | P2, last prose pass | Keep the existing contribution/roadmap close as a draft, but finalize it only after the ordered-film evidence and uncertainty boundary are fixed. Accept when every claimed accomplishment points to displayed evidence and PbI2 remains an extension. |
| C04 | Define \(\mathbf k_i\), \(\mathbf k_f\), \(\mathbf Q\), and \(\mathbf G\); number equations | AGREE | IN PROGRESS | P1 | Define every vector in prose before first use; place elastic scattering, momentum transfer, Bragg matching, and exit-vector relations in numbered, labeled equations with text references. Build a notation ledger before expanding equations. Accept when no central symbol is inferentially defined and the main/SI notation scan is consistent. |
| C05 | Define sample intersection | AGREE WITH MODIFICATION | TODO | P1 | Define the ray-film-plane hit and finite-sample rejection in physical language, but verify the actual coordinate convention and code behavior before writing the formula. Put the full ray-plane equation in SI. Accept when prose, equation, figure, and implementation describe the same boundary test and no second footprint factor double-counts rejected rays. |
| C06 | Unpack incidence geometry and optical corrections | AGREE WITH MODIFICATION | TODO | P1 | Replace the overloaded sentence with the actual causal pipeline, one operation per sentence. Do not commit to the packet's proposed operation order until it is checked against the model. Accept when each operation has a physical object/input/output and detailed transforms are cross-referenced to SI. |
| C07 | Introduce Monte Carlo sampling with incident rays | AGREE | IN PROGRESS | P1 | State immediately that wavelength, beam position, and direction are sampled from measured beam distributions; describe mosaic-event sampling separately; state that Miller pairs are enumerated, not Monte Carlo sampled. Accept when the two probability spaces and the discrete reflection construction cannot be confused. |
| C08 | Explain footprint from sample intersection | AGREE WITH MODIFICATION | TODO | P1 | Define one ray intersection first and the footprint as the distribution/envelope of accepted intersections. Repair the existing sample-geometry figure rather than automatically adding another figure. Verify whether ray rejection already supplies the footprint so an additional multiplicative correction does not double-count it. Accept when beam size, incidence angle, sample bounds, hit point, and weighting are connected explicitly. |
| C09 | Replace vague labels/profile extraction language | AGREE WITH MODIFICATION | IN PROGRESS | P1 | Replace software nouns with symmetry-family grouping, a finite detector integration band, and the reported \(I(Q_z)\) or \(I(L)\) profile. Use \(Q_R\) consistently. Accept when the method sentence and ordered-film caption identify the same bands and observables. |
| C10 | Explain reciprocal-space construction algorithm | AGREE WITH MODIFICATION | IN PROGRESS | P1 | Retain the current deterministic \((H,K)\) enumeration but add verified bounds, systematic-absence handling, symmetry grouping, Ewald/Bragg intersection, detector acceptance, and stopping criteria in SI. Accept only after these details are checked against the actual implementation. |
| C11 | Put geometric-correction equations in SI | AGREE | TODO | P1 | Extend and unify the existing SI rather than duplicating its projection and optical derivations: add coordinate frames, sample/detector rotations, ray-plane and detector-plane intersections, finite-sample acceptance, and pixel mapping, then cross-reference the existing projection/refraction pieces as one chain. Accept when the SI builds and the main text cites the complete section. |
| C12 | Repair Figure 4 and caption | AGREE | TODO | P1 | Redraw rather than patch the caption. Establish whether \(\mathbf g\) is an axis or arm; remove or unambiguously draw \(\delta\); show \(X_s,W,H\) or move them to SI. Accept when every drawn symbol is defined and every caption symbol is visible. |
| C13 | Put structure factor before multiplicity | AGREE WITH MODIFICATION | TODO | P1 | Reorder to one reflection and then family grouping, but first fix the reciprocal-vector/fractional-coordinate/\(2\pi\)/Debye-Waller convention. Accept when the phase and displacement exponents are dimensionally consistent, then \(\mathbf G_{hkl}\), \(F_{\mathbf G}\), and \(|F_{\mathbf G}|^2\) precede multiplicity. |
| C14 | Replace \(\mathbf M_\parallel\) with the explicit 2D-powder rule | AGREE WITH MODIFICATION | IN PROGRESS | P1 | For the hexagonal test cases use \(m=H^2+HK+K^2\) and \(Q_R=4\pi\sqrt m/(\sqrt3a)\), but explicitly call \(m\) a radial/family index, not a multiplicity. Define multiplicity separately as the count of allowed equivalent \((H,K)\) members. Accept when \(Q_r/Q_R\), upper/lower-case Miller indices, and family/multiplicity notation are consistent in text, SI, figures, and captions. |
| C15 | Reframe the mosaicity introduction | AGREE | IN PROGRESS | P1 | The present paragraph already distinguishes in-plane powder rotation from out-of-plane mosaicity; revise it to complete the advisor's causal sequence and state why an area detector is sensitive before showing the observation. Accept when cause, detector consequence, observation, and model appear in that order. |
| C16 | Replace “a limited part” with a quantitative condition | AGREE | BLOCKED | P0 | The repository does not report the beam wavelength, and the annotation's near/far premise may compare incidence with displayed \(2\theta\). Once the experimental spectrum is supplied, calculate the full 003/006 vector-orientation mismatch from wavelength, refined \(c\), alignment, bandwidth, and the incidence convention; state whether any reported quantity is \(\theta_B\), \(2\theta\), exit angle, or required crystallite tilt. Accept when the manuscript gives a reproducible like-for-like condition and eliminates “limited.” |
| C17 | Remind the reader that \(\phi\) is azimuth | AGREE | IN PROGRESS | P2 | Write “azimuthal extent along detector-plane angle \(\phi\)” and confirm that \(\phi\) is defined earlier. Accept when \(\phi/\varphi\) usage is intentional and a notation search finds no unexplained first use. |
| C18 | Demonstrate Gaussian core plus Lorentzian tail quantitatively | AGREE WITH MODIFICATION | IN PROGRESS | P0 | First correct or independently validate the moving-center bandwidth treatment so the tail is not compensating for a geometric artifact. Then show both (a) the final fit with the tail removed while other parameters are fixed and (b) a fairly re-optimized Gaussian-only nested model, alongside the Gaussian-plus-Lorentzian fit, multi-angle data, residuals, and identical verified geometry/instrument settings. Report widths, tail fraction, parameter correlation/uncertainty, and a declared comparison metric if supported. Accept when the necessity claim survives compensation by bandwidth/divergence/background across more than one condition and the Lorentzian form remains phenomenological, not unique. |
| C19 | Separate \(L\approx0\) intensity from mosaicity | AGREE WITH MODIFICATION | IN PROGRESS | P0 | Retain only a short signpost in the mosaic observation/caption and keep the mechanism in a distinct near-critical reflectivity subsection. State explicitly whether mosaicity enters that optical branch; do not infer causation from detector overlap. The present limiting-curve figure omits the blended prediction and uses digitized/repaired/clipped-source traces, so it is provisional and cannot validate the assignment. Accept only after direct measured/model arrays show the full prediction or the limitation is stated, and the two mechanisms cannot be conflated. |
| C20 | Introduce and justify optical constants | DISAGREE WITH PROPOSED IMPLEMENTATION | IN PROGRESS | P0 | Accept the advisor's request to explain and bound optical importance, but do not make the packet's three-way publication deliverable mandatory. Move the duplicated long derivation to SI, first verify tangential-wavevector conservation, the complex normal boundary condition, decaying branch, attenuation coordinate, and flux normalization, then run full- versus fixed-\(n\) sensitivity by declared ROI and \(Q_z\) range. Use \(n=1\) only as a separate total-optics-off diagnostic where meaningful. Add a main-text figure only if the effect is scientifically consequential. |
| C21 | Reframe ordered films as “Test cases:” | DISAGREE WITH PROPOSED IMPLEMENTATION / CHECK | IN PROGRESS | P0 | Coordinate-level extraction verifies that the highlight covers “Results: ordered.” The most literal low-risk edit is therefore “Test cases: Bi2Se3 and Bi2Te3 films,” replacing the highlighted phrase. Do not add the packet's invented word “Validation” unless the advisor confirms it; all listed angles appear fitted, so do not imply held-out prediction without a genuine holdout. Make the opening state exactly which positions, line shapes, intensities, and non-obvious features are tested. |
| C22 | Move workflow directly after ordered validation | AGREE | TODO | P0 | Change the order to ordered validation -> refinement workflow -> PbI2 extension and delete the workflow's current placement meta-comment. Accept when `main.tex`, the workflow opening, section cross-references, and the introduction roadmap all agree. |

### Recommended execution order

1. **Lock the evidence (C16, C18-C20 plus the ordered-film overlays).** Verify wavelength/lattice inputs and detunings; produce the controlled mosaic ablation; validate the optical boundary-condition implementation and show the full near-critical prediction or an explicit limitation; determine the bounded role of optical constants; finish figure readability and residual checks. Claims remain provisional until this gate passes.
2. **Repair story order (C19, C21, C22).** Separate near-critical optics from mosaicity, make the ordered films explicit test cases, state whether each comparison is an in-sample fit or a held-out prediction, place the workflow immediately after them, and keep PbI2 downstream.
3. **Rewrite the geometry/construction tutorial (C02, C04-C12).** Define vectors and physical objects in the main text, repair Figures 2 and 4, and add the reproducible equation/algorithm chain to SI.
4. **Repair and simplify reflection notation (C13-C14).** First make the reciprocal-vector, phase, coordinate, and Debye-Waller conventions dimensionally consistent. Then explain one reflection and its structure factor before family grouping; replace the abstract metric with the explicit hexagonal relation and distinguish family index from multiplicity.
5. **Polish mosaicity language (C15-C17).** Complete the causal introduction, replace vague selection language with verified detunings, and repair the \(\phi\) reminder.
6. **Finish the introduction and teaching captions last (C03 and all affected figures).** The C01 layered-film-first opening is complete. Once evidence and section order are stable, finalize the accomplishments paragraph, roadmap, and captions that teach the complete comparison.

### Completion protocol

For each C01-C22 item, record the exact revised manuscript/SI location, the evidence or build used to verify it, and one of `TODO`, `IN PROGRESS`, `DONE`, `CHECK`, `BLOCKED`, or `PARKED`. A placeholder, future-tense caption, or related paragraph is not `DONE`. Any disagreement or deliberate non-adoption must be evidence-based and recorded here before the response letter is drafted.

## Core Thesis

The next draft should visibly demonstrate that the forward model quantitatively reproduces measured area-detector diffraction line shapes for Bi2Se3 and Bi2Te3.

Main claim:

> When instrumental geometry, sample orientation, beam distribution, wavelength bandwidth, detector effects, mosaicity, projection procedure, and structure factor are handled consistently, the model reproduces the measured Bi2Se3 and Bi2Te3 line shapes, relative intensities, and non-obvious detector features well enough to support refinement-quality interpretation.

Use "refinement-quality" carefully. Tie it to plotted data/model overlays, propagated/systematic error, and the structure-factor/CIF/SIF treatment.

## Advisor Philosophy

1. Paper first, software second. Do not make software cleanup or release polish the manuscript bottleneck.
2. Show the success clearly. The central result is that the model reproduces measured Bi2Se3 and Bi2Te3 diffraction line shapes.
3. Write for a diffraction/scattering audience. Use Q, Q_R, Q_z, m-indexed reflection families, explicit (h,k,l) labels where useful, Bragg rods, Bragg positions, reciprocal space, incident angle, mosaicity, resolution, and line-shape fitting.
4. Physics first, optimization later. Put software-native terms such as caked space, internal branches, lookup tables, and optimization details in the supplement unless needed to understand the physics.
5. Figures drive the paper. Draft with enough figures first, then consolidate.
6. Explain more than feels necessary at difficult points: detector space, reciprocal-space trajectories, integration bands, projection, fitting, and simulation.
7. Captions must teach. A caption should explain what is measured, what is calculated, how the comparison was generated, and what conclusion the reader should draw.
8. Show the observational problem before the model correction.
9. Do not undersell the achievement. If justified by overlays and error analysis, careful refinement-quality language is appropriate.
10. Write to teach, not merely to document. The manuscript should read like a clear research talk expanded into paper form.
11. Use the data as the hook: unexpected reflections, the m=0, L=3 star feature, and low-Q / low-L features should motivate mosaicity, bandwidth, and the full detector-space model.
12. Treat explanation itself as a contribution when the geometry is counterintuitive or underexplained.
13. Draft big, then cut. Move implementation-heavy details later, after the main argument is understandable.
14. Define symbols and specialized terms before use, number important equations, and refer to them explicitly.
15. Prefer simple, explicit notation. Keep a reflection-family index distinct from the number of symmetry-equivalent reflections in that family.
16. Preserve causal order and avoid overloaded sentences; at difficult points, give each physical or computational operation its own sentence.
17. Replace vague qualifiers with testable conditions, numerical values, or direct comparisons.
18. When a model component is claimed to be necessary, show an otherwise-identical ablation, residuals, fitted values, and uncertainties where feasible.
19. Keep the strongest completed result ahead of extensions, future capabilities, and implementation detail.

## Primary Story

The paper should follow this logic:

1. Present the experimental diffraction data and physical problem before machinery.
2. Use visible detector images or crops as section springboards.
3. Point out puzzling features first: unexpected reflections at a single incident angle, low-order features, long-tail mosaicity, and the m=0, L=3 star feature.
4. Explain model ingredients physically: sample geometry, detector geometry, incident angle, beam position, divergence, wavelength spread, mosaicity, bandwidth, structure factor, and resolution.
5. Introduce two-component mosaicity early, including the long Lorentzian-like tail.
6. Explain finite bandwidth / Bragg-sphere / mosaic-cap geometry as a tutorial point.
7. Explain the m=0, L=3 star feature before using final fits to validate it.
8. Show how data and calculation are projected onto interpretable Q-space trajectories.
9. Demonstrate direct measured/calculated overlays for Bi2Se3 and Bi2Te3.
10. Use overlays, propagated/systematic error, and structure-factor treatment to support refinement-quality framing.
11. Move computational implementation details to the supplement after the main argument is understandable.
12. Treat PbI2, stacking faults, and diffuse scattering as subordinate until the ordered-film story is clear.

## Current Repo And Manuscript State

| Item | Status | Notes |
|---|---|---|
| `main.tex` scaffold | DONE | Inputs model, mosaic/correlated effects, ordered results, PbI2 extension, workflow, and conclusion. |
| Build plumbing | DONE | Uses standard BibTeX via `\bibliography{bibliography/references}`. Generated aux, BBL, log, SyncTeX, and non-review PDFs are ignored. |
| `sections/introduction.tex` | IN PROGRESS | C01 layered-film-first opening and first-visual order are resolved; C02/C03 tutorial, contribution, and roadmap work remains. |
| `sections/modelling_methods.tex` | IN PROGRESS | Keep the main narrative in Q/Q_R/Q_z/m language; move coordinate bookkeeping to SI. |
| `sections/mosaicity_texture.tex` | IN PROGRESS | Begins from low-L / m=0 observational motivation; still benefits from stronger direct Lorentzian-tail evidence. |
| `sections/correlated_effects.tex` | IN PROGRESS | Contains bandwidth / Bragg-sphere / mosaic-cap tutorial material. |
| `sections/results_ordered.tex` | IN PROGRESS | Focuses on ordered Bi2Se3/Bi2Te3 validation payoff; result figures need final readability and labeling checks. |
| `sections/results_diffuse_pbi2.tex` | IN PROGRESS | Reintroduced as an extension; keep subordinate until ordered-film validation is clear. |
| `sections/refinement_workflow.tex` | IN PROGRESS | Positioned near the end; should supplement the workflow table instead of repeating it. |
| `sections/discussion_conclusion.tex` | IN PROGRESS | Should summarize central validation, uncertainty boundary, and future diffuse/stacking extension without method repetition. |
| Ordered-film figures | IN PROGRESS | Inserted assets need readability, annotation-density, axis, and label checks. |
| PbI2 figures | IN PROGRESS | Parent-stack schematic complete; reciprocal-space and measured/calculated disorder figures still need completion. |
| Software release polish | PARKED | Paper must demonstrate scientific value first. |

## Active Tasks

### P0 - Next Advisor Draft

| Task | Status | Deliverable | Notes |
|---|---|---|---|
| Finalize Bi2Se3 detector/projection figure | IN PROGRESS | Main-text figure | Asset exists; verify direct-source provenance/scaling, keep measured data prominent, reduce obscuring band weight, and complete label/readability checks. |
| Finalize Bi2Te3 detector/projection figure | IN PROGRESS | Main-text figure | Asset exists; match Bi2Se3 styling and fix the clipped-looking detector y-axis labels before reuse. |
| Add Bi2Se3 Q_z projection overlays | IN PROGRESS | Figure panels | Plot measured and calculated intensity versus Q_z. |
| Add Bi2Te3 Q_z projection overlays | IN PROGRESS | Figure panels | Plot measured and calculated intensity versus Q_z. |
| Define reflection-family labels | IN PROGRESS | Figure/caption convention | Initial m-indexed convention is present; final notation still needs advisor check. |
| Add early two-component mosaicity evidence | IN PROGRESS | Text + controlled comparison | Low-L m=0 evidence is inserted; advisor comment C18 now requires a matched Gaussian-core-only versus Gaussian-plus-Lorentzian comparison with residuals and fitted uncertainty. |
| Verify ordered-figure provenance and scaling | TODO | Reproducible figure record | Retain scripts/direct arrays; state normalization and whether scales are common across families/images; add residual/uncertainty support before claiming relative-intensity validation. |
| Verify moving-center bandwidth geometry | CHECK | Corrected derivation + direct simulation | Replace or validate the fixed-center 1/L argument before it supports low-L or mosaic-tail claims. |
| Verify 003/006 Bragg conditions and orientation mismatch | BLOCKED | Quantitative sentence + calculation record | Obtain the actual wavelength distribution, then use full vector geometry, refined lattice, alignment, bandwidth, and explicit angle definitions; do not subtract incidence from displayed 2theta. |
| Bound the role of optical constants | TODO | ROI sensitivity statement + SI physics check | Validate boundary conditions/attenuation/flux first; compare full versus fixed n by declared ROI. Use n=1 only as a separate total-optics diagnostic. |
| Replace provisional reflectivity traces | BLOCKED | Direct-array full prediction | Current plot is digitized/repaired and omits the blended curve. Obtain direct measured and model arrays, show the full prediction, and declare how mosaicity enters. |
| Reorder workflow before PbI2 | TODO | `main.tex` + workflow opening | Required sequence: ordered-film validation, refinement workflow, then PbI2 extension. Remove the placement meta-comment. |
| Confirm ordered-section “Test cases:” intent | CHECK | Heading decision | Provisional literal edit is “Test cases: Bi2Se3 and Bi2Te3 films”; do not add “Validation” without confirmation or a held-out test. |
| Decide next-draft PbI2 scope | TODO | Main-text/SI boundary | Prefer omission until refit, or reduce to measured motivation plus one final data/model panel and move transition-matrix detail to SI. |
| Define or correct “grown by TEM” | CHECK | Results wording | Spell out the intended growth method; avoid the transmission-electron-microscopy reading. |
| Write Q-space/projection caveat | DONE | Methods/results paragraph | Results state why projected Q_z is not an ideal perfect-crystal cut and why data/model comparison remains meaningful. |
| Add experimental incident-angle table | TODO | Methods or workflow table | List all collected angles, not just shown angles. |
| Replace remaining future-tense scaffold prose | TODO | Results prose | Convert "should show" language to result-forward statements once final figures are inserted. |

### P1 - Complete-Draft Support

| Task | Status | Deliverable | Notes |
|---|---|---|---|
| Consolidate 2theta-phi/caked implementation supplement | IN PROGRESS | Built supplement section | Material exists in an unassembled outline and the built SI; merge into one canonical source rather than duplicating it. |
| Explain sub-pixelation/binning | TODO | Supplement section | Needed for pixel-sensitive detector transformations. |
| Explain Monte Carlo beam sampling | IN PROGRESS | Supplement section | Outline exists but is unassembled; include wavelength, beam position, divergence, event counts, seeds, and convergence. |
| Explain mosaic-event sampling | IN PROGRESS | Supplement section | Outline exists but is unassembled; separate it from beam sampling and document convergence/validation. |
| Create a notation ledger | TODO | Main text + SI convention table | Resolve Q_r/Q_R, h/H, phi/varphi, and the duplicate eta meanings before expanding equations. |
| Complete geometric-correction SI chain | TODO | Supplement section | Add frames, rotations, ray-plane and detector-plane intersections, finite-sample acceptance, refraction/transmission, pixel mapping, and projection bands. |
| Repair sample-geometry Figure 4 | TODO | Main-text figure + caption | Resolve axis/arm naming, delta, X_s, W, and H with a one-to-one symbol contract. |
| Add h-BN fitting method | TODO | Supplement section | Unique workflow step mentioned in the paper. |
| Assemble full ordered-film peak-profile checks | TODO | Supplement figures | Good place for full measured/calculated profile panels. |
| Finalize structure-factor/CIF/SIF and occupancy discussion | TODO | Main text plus SI | State what was fit, including size of occupancy changes. |
| Add propagated/systematic error support | IN PROGRESS | Main text plus SI | Main text gives the interpretation boundary; SI carries derivation. |

### P2 - Parked

| Task | Status | Reason |
|---|---|---|
| PbI2 diffuse scattering / stacking-fault finalization | IN PROGRESS | Keep subordinate to ordered-film validation. |
| PbI2 selected-rod validation figures | TODO | Placeholder exists; generate real figure later. |
| Software release cleanup | PARKED | Paper first. |
| Full software feature documentation | PARKED | Useful later, not central to current draft. |

## Immediate Checklist

- [ ] Final QA/provenance for the existing Bi2Se3 measured detector image and integration-region annotation.
- [ ] Final QA/provenance, scaling declaration, and residual/uncertainty support for the existing Bi2Se3 overlay.
- [ ] Final QA/provenance and y-axis-label repair for the existing Bi2Te3 detector image.
- [ ] Final QA/provenance, scaling declaration, and residual/uncertainty support for the existing Bi2Te3 overlay.
- [x] Initial m or explicit (h,k,l) reflection-family label convention.
- [x] Paragraph explaining imperfect Q-space/projection interpretation.
- [x] Paragraph and figure concept for two-component mosaicity / Lorentzian-tail evidence.
- [ ] Table or list of all incident angles collected for Bi2Se3 and Bi2Te3.
- [ ] Consolidate the unassembled implementation outline into the built SI; add the missing geometry chain and a notation ledger.
- [ ] Correct/validate moving-center bandwidth geometry before using the current 1/L claim.
- [ ] Fair Gaussian-only refit, same-fit no-tail counterfactual, and Gaussian-plus-Lorentzian comparison across multiple angles with residuals/correlation/uncertainty.
- [ ] Verified 003/006 full orientation mismatch from actual wavelength, lattice, alignment, bandwidth, and like-for-like angle definitions.
- [ ] Physics-checked, bounded optical-constant sensitivity result; long duplicated derivation removed from main text.
- [ ] Direct-array measured/full-model near-critical plot replacing the digitized/repaired limiting traces.
- [ ] Workflow moved directly after ordered-film validation and before PbI2.
- [ ] Literal provisional “Test cases:” heading marked for advisor confirmation; no added “Validation” without evidence.
- [ ] Decide whether PbI2 is omitted or reduced to one result panel until the refit is complete.
- [ ] Define/correct the “grown by TEM” phrase.

## Advisor Questions

- Is the proposed reflection-family labeling convention clear enough?
- Which Bi2Se3/Bi2Te3 incident angles should be main-text figures versus supplement?
- Should Lorentzian-tail evidence be a standalone figure or part of the mosaicity figure?
- How many Q_z projection panels are enough for the main text?
- Did “Test cases:” on page 14 request that exact heading prefix, or only validation framing?
- After the targeted sensitivity check, should the optical-constant ablation appear in the main text or only in the supplement?

## Figure Guidance

Figures must show data. Do not obscure measured detector intensity with too many Bragg-position circles, colored paths, markers, or labels.

Quantitative figures must be generated from retained direct data/model arrays with documented scripts and normalization. Digitized, repaired, clipped, or placeholder curves are provisional and cannot support fits, residuals, ablations, or validation claims.

Each main-text figure caption should state:

1. what material is shown;
2. what is measured and what is calculated;
3. what solid lines, dashed lines, boxes, rods, projection bands, and symbols mean;
4. what coordinate convention is being used;
5. how projected profiles were generated;
6. what feature the reader should notice;
7. how the figure supports the manuscript claim.

### Active Figure Status

| Figure / asset | Status | Purpose |
|---|---|---|
| `figures/intro/` | IN PROGRESS | Orientational limits and 2D-powder motivation. |
| `figures/results_ordered/00L_region_horizontal_marked.png` | IN PROGRESS | Low-L m=0 star-feature crop used to motivate mosaicity. |
| `figures/results_ordered/figure7_bi2se3_qr_rod_qz_profiles_detector_selected_q_regions_5deg.png` | IN PROGRESS | Bi2Se3 detector trajectory/projection setup; needs readability check. |
| `figures/results_ordered/figure7_bi2te3_qr_rod_qz_profiles_detector_selected_q_regions_5deg.png` | IN PROGRESS | Bi2Te3 detector trajectory/projection setup; match Bi2Se3 styling. |
| `figures/results_ordered/figure7_bi2se3_qr_rod_qz_profiles.png` | IN PROGRESS | Bi2Se3 measured/calculated Q_z overlays; final axis/label check needed. |
| `figures/results_ordered/figure7_bi2te3_qr_rod_qz_profiles.png` | IN PROGRESS | Bi2Te3 measured/calculated Q_z overlays; final axis/label check needed. |
| `figures/correlated_effects/fig_reflectivity_data_parratt_kinematic.png` | CHECK | Provisional only: digitized/repaired traces, clipped-branch plateau, and no full blended prediction. Replace with direct exports before using as evidence. |
| `figures/mosaic/lorentzian_tail_evidence.png` or existing ordered-film crop | TODO | Direct evidence that narrow-core mosaicity alone is insufficient. |
| `figures/mosaic/bragg_sphere_bandwidth_size_series.png` | TODO | Bragg-sphere size / Ewald thickness / mosaic-cap tutorial. |
| `figures/mosaic/delta_lambda_detector_series.png` | TODO | Detector-image sequence varying wavelength bandwidth, incidence angle, or Bragg-sphere size. |
| `figures/mosaic/low_q_003_03_06_data_model_overlay.png` | TODO | Measured/calculated overlay or control comparison for low-Q/003, 03, and 06-type features. |
| `figures/results_pbi2/transition_matrix/pbi2_polytype_stacks.{tex,png}` | DONE | Figure 11 parent-stack schematic in rF_sigma notation. |
| `figures/results_pbi2/pbi2_raw_detector_diffuse_motivation.png` | TODO | PbI2 measured detector image with diffuse features. |
| `figures/results_pbi2/pbi2_diffuse_data_model_overlay.png` | TODO | Measured/ordered/faulted/residual projection figure. |

Recommended main-text sequence:

1. Orientational limits / 2D powder motivation.
2. Model geometry and mosaicity.
3. Low-L m=0 star-feature observation and a verified bandwidth/mosaic-cap explanation; otherwise label the mechanism as an open check.
4. Bi2Se3 ordered-film detector setup and Q_z overlays.
5. Bi2Te3 ordered-film detector setup and Q_z overlays.
6. Refinement workflow and uncertainty/structure-factor framing.
7. PbI2 extension only if it does not compete with the ordered-film validation.

## Projection And Coordinate Guidance

Use Q_z as the main horizontal/projected coordinate for line profiles when that is the physical interpretation. Use Q_R or scalar m to identify which reciprocal-space trajectory is sampled.

The manuscript should say:

- data are projected along trajectories corresponding to fixed Q_R or m-family conditions;
- profiles are reported versus Q_z;
- mosaicity, beam divergence, wavelength spread, finite incident-angle uncertainty, and detector/sample resolution make the projected coordinate resolution-limited rather than an ideal reciprocal-space cut;
- calculation and data pass through the same projection and resolution effects;
- therefore the measured/calculated comparison is meaningful and is the central method test.

Do not overstate Q-space exactness. If a plotted reciprocal-space trajectory omits sample rotation, chi, or alignment distortions, describe it as an approximate projection guide rather than a physical explanation of peak offsets.

Suggested concise caveat:

> The horizontal coordinate is reported as Q_z along the selected trajectory. Because mosaicity, divergence, wavelength spread, incidence-angle uncertainty, and detector sampling broaden the effective scattering condition, these profiles are not ideal reciprocal-space cuts. The comparison remains direct because the same projection and resolution effects are applied to the calculated image.

## Indexing And Labels

Use labels that a diffraction reader can interpret.

For hexagonal Bi2Se3 and Bi2Te3, use the compact scalar reflection-family label:

```tex
m = h^2 + h k + k^2 .
```

Define m before use. Use m=1, m=3, or explicit (h,k,l) labels when space allows. Avoid relying only on internal labels such as M1, M2, plus branch, or minus branch unless they are explicitly tied to physical reflection families.

If symmetry-equivalent reflections contribute to the same ring/manifold, state that convention in the caption or text. Q_R values may be secondary numerical information, not the primary label.

## Two-Component Mosaicity

The two-component mosaicity model must appear early and be supported by visible evidence.

Core argument:

- A narrow mosaic distribution alone cannot explain all observed reflections.
- Some reflections appear at incident angles where a narrow mosaic component would not produce them.
- A weak long-tail component captures a small population of substantially tilted crystallites.
- The long tail helps explain both off-condition reflections and the low-Q / m=0, L=3 associated features when bandwidth is included.
- The Lorentzian-like form is a useful phenomenological approximation, not proof that the physical distribution is uniquely Lorentzian.

The compact mosaicity equation or equivalent explanation likely belongs in the main text because the long-tail component is physical, not merely computational machinery.

## Bandwidth / Bragg-Sphere / Mosaic-Cap Tutorial

This is a conceptual contribution and should be explained step by step.

Required explanation:

1. Define Bragg sphere, Ewald sphere, bandwidth thickness, allowed intersection ring, incident vector, outgoing vector, and mosaic cap.
2. Explain that allowed geometric intersections are not populated uniformly; intensity appears where the ring samples mosaic-smeared Bragg intensity.
3. Show why small Bragg spheres can intersect a large fraction of the mosaic cap, making low-order reflections robust across incidence changes.
4. Show why larger Bragg spheres intersect thinner cap regions and become more geometrically selective.
5. Pair schematic examples with calculated detector images.
6. Then show measured data and simulation side by side.

The m=0, L=3 star-like or line-like feature should be explained explicitly. The working interpretation is that finite Ewald-sphere thickness from wavelength bandwidth intersects the small 003 Bragg sphere and, together with mosaic extension, redistributes intensity into the observed detector feature. State that disabling the 003 reflection removes both the direct 003 peak and associated feature only if this remains verified.

## Experimental Section Requirements

The manuscript must state what data were collected, not only what data are shown.

For each material, include:

- incident angles collected;
- incident angles shown in the main text;
- incident angles moved to the supplement;
- why the shown angles are representative or useful.

Do not let the reader infer that only displayed incident angles were measured.

## Workflow Guidance

The workflow table is useful, but it cannot stand alone. A good workflow section should:

- say that many parameters must be established before quantitative comparison is possible;
- distinguish instrumental parameters from sample-dependent parameters;
- explain the sequence used to determine those parameters;
- describe what each step contributes to the final comparison;
- avoid making the reader infer the method from a table alone.

Placement matters. The workflow should not interrupt the physical story; it belongs after the model/results context makes the staging valuable.

## Supplement Scope

Main text should contain:

- physical motivation;
- main experimental data;
- model ingredients in physical language;
- two-component mosaicity argument;
- Q / Q_R / Q_z projection concept;
- Bi2Se3 and Bi2Te3 data/calculation overlays;
- enough experimental detail to understand shown data;
- the mosaicity equation or equivalent explanation;
- m=0, L=3 star-feature explanation;
- propagated/systematic error at the interpretation level;
- structure-factor/CIF/SIF and occupancy-change discussion needed for refinement-quality framing.

Supplement should contain:

- 2theta-phi implementation details;
- caked coordinate transformation;
- sub-pixelation and binning;
- lookup-table or detector-remapping details;
- Monte Carlo sampling details;
- beam position, divergence, wavelength spread sampling;
- mosaic-event sampling;
- computational efficiency/optimization arguments;
- full profile arrays or large peak-by-peak fit collections;
- h-BN fitting procedure if part of the analysis pipeline;
- additional incident-angle data;
- full CIF/SIF contents if too long for main text;
- full propagated-error derivations.

### Proposed Supplement Outline

| Section | Status | Contents |
|---|---|---|
| S1 Coordinate systems and projection implementation | TODO | Detector space, 2theta-phi, Q/Q_R/Q_z definitions, trajectory projection, projection caveat. |
| S2 Sub-pixelation and binning | TODO | Partial-pixel issues, intensity distribution across transformed bins. |
| S3 Beam and instrument sampling | TODO | Beam position, divergence, wavelength spread, detector projection, resolution contribution. |
| S4 Monte Carlo optimization | TODO | Replacing dense grids, avoiding wavelength-shell artifacts, preserving the same physical model. |
| S5 Mosaic-event sampling | TODO | Sampling mosaic orientations and validating that optimization preserves physics. |
| S6 Two-component mosaicity checks | TODO | Narrow-core versus long-tail comparisons and supplemental profiles. |
| S7 Full ordered-film peak profiles | TODO | Expanded Bi2Se3/Bi2Te3 measured/calculated profile comparisons. |
| S8 h-BN fitting method | TODO | What was fit, what parameters were extracted, and why it belongs in the workflow. |
| S9 PbI2 diffuse scattering and stacking-disorder details | PARKED | Selected rods, ordered baseline, diffuse residuals, stacking-fault model, validation branch comparisons. |

## Concision Guidance

Cut or move text that mainly explains software convenience, implementation bookkeeping, broad literature context, or parameter auditing before the fit evidence appears.

Keep text that helps a diffraction reader see:

1. what was measured;
2. what physical effect is modeled;
3. how measured and calculated intensities are compared;
4. why the Bi2Se3/Bi2Te3 overlays prove the model works.

Highest-priority cuts before the next advisor draft:

1. Compress the introduction's material-family survey.
2. Shorten the post-Fig. 1 orientational-limits paragraph.
3. Reduce workflow prose because the table already carries the staged refinement.
4. Move or shrink the ordered structure-parameter table.
5. Convert future-tense results text into direct result language once figures are final.
6. Keep PbI2 from competing with ordered-film validation.
7. Remove final-discussion meta-comments about how the paper should be organized.
8. Add Lorentzian-tail evidence instead of compensating with more prose.

## Decision Log

| Date | Decision / change | Current interpretation |
|---|---|---|
| 2026-07-18 | Resolved advisor comment C01. | Replaced the WAXS-first opening with a 115-word layered-film-first paragraph, defined the 2D-powder state operationally, made substrate/growth dependence explicit, removed the material-family catalogue, and moved the orientational-limits comparison ahead of the PbI2 overview. The guarded build succeeded and rendered pages 1-3 passed visual review. |
| 2026-07-18 | Audited the 22-comment Miceli packet and integrated the writing philosophy into `AGENTS.md`. | All comments are traceable here. Ten packet responses are accepted, ten require modification, and two proposed implementations are rejected/replaced while retaining the advisor's underlying concern. Critical physics/provenance checks now precede prose polish; at the time of this initial audit, no manuscript comment was fully closed. |
| 2026-06-29 | Added Smilgies/Li indexGIXS citation and narrowed detector-space framing. | Smilgies and Li are now cited as prior art for calculating/overlaying grazing-incidence diffraction-spot positions directly in detector space. The manuscript contribution is framed as detector-space intensity/profile forward modeling after the geometric indexing step, not as novelty in detector-space indexing itself. |
| 2026-06-25 | Pruned generated figure diagnostics. | Removed 76 unreferenced generated PbI2 assets: misplaced ordered-folder outputs, parent-level generated exports, and low/medium/high `profiles/` diagnostics. Active manuscript and supplement figure paths remain the source contract for retained assets. |
| 2026-06-25 | Integrated annotated-PDF changes. | Low-L near-origin intensity is described as reflectivity; optical-to-kinematic handoff terminology is used; Figure 8 is a single overlay of measured Bi2Se3 near-critical m=0, Parratt, and kinematic traces. Digitized figure inputs should be replaced by direct array exports before final submission. |
| 2026-06-25 | Consolidated legacy manuscript tracking. | Advisor notes, meeting-prep notes, figure status, supplement status, changelogs, TODO tracking, old patch handoffs, and temporary review artifacts are subsumed here or removed. Git history remains the archive for exact old wording. |
| 2026-06-23 | Replaced superseded PbI2 scalar slip/flip model. | PbI2 now uses a six-state direction-resolved transition-matrix model. Numerical epsilon_j and population weights remain pending a refit and must not be converted from old scalar p values. |
| 2026-06-23 | Replaced PbI2 parent-stack Figure 11. | The projected 2H/4H/6H atomic-stack schematic is integrated with rF_sigma notation and a teaching caption. |
| 2026-06-23 | Updated PbI2 intensity equations. | Main text uses parent probability 1-epsilon_j and alternatives epsilon_j/4, includes finite-stack self-plus-pair intensity, and keeps the full derivation in SI. |
| 2026-06-15 | Fixed clean-build BibTeX failure. | Clean builds should regenerate bibliography from tracked sources; watcher processes must be stopped manually before guarded rebuilds. |
| 2026-06-15 | Added GitHub Actions LaTeX build check. | CI checks root `main.pdf`, `build/main.aux`, and non-empty `build/main.bbl` with bibliography markers. |
| 2026-06-11 | Removed legacy build products and patch handoffs. | Active manuscript sources, current figure assets, bibliography source, `main.pdf`, and `2D_Supplemental/SI_failure_modes.pdf` are retained review artifacts. |
| 2026-05-22 | Added bandwidth-scaling and uncertainty material. | Main text states approximate 1/L angular-bandwidth scaling for m=0, 00L cap overlap; SI carries derivation and projection/intensity uncertainty formulas. |
| 2026-05-12 | Advisor-feedback restructure. | Low-L star feature moved before validation payoff; correlated effects section added; PbI2 reintroduced only as an extension; workflow moved near the end. |
| 2026-05-10 | Moved low-L m=0 star feature before ordered-film validation. | Observation now precedes the fit-quality payoff. |
| 2026-04-30 | Advisor meeting. | Paper first, ordered Bi2Se3/Bi2Te3 figures first, direct Q_z overlays, supplement for implementation, PbI2 parked/subordinate. |
| 2026-04-30 | Added preliminary literature-bounded parameter citations. | Fitted structural values remain provisional and must be checked against final refinement output before submission. |
| 2026-04-26 | Cleaned language and fit layout. | Eq. (4) notation uses selected-rod polar angle eta; figure inclusions were adjusted for page fit. |
| 2026-04-21 | Added Nookiin related-work citation. | Nookiin is complementary atomistic/supercell context, not a workflow dependency or software used by the present model. |
| 2026-03-13 | Pedagogical diffraction-model rewrite. | The model builds from ideal scattering geometry to experimental complications and weights. |
| 2026-03-03/04 | Advisor-annotation passes. | Section structure, notation, figure plumbing, beam/sample components, and supporting information were updated; detailed line-by-line history remains in git. |

## Current Change Status

| Area | Status | Notes |
|---|---|---|
| Feature | DONE | Added `SmilgiesLi2026IndexGIXS` to `bibliography/references.bib` and cited indexGIXS in the introduction, model opening, workflow, and discussion as prior art for detector-space visualization/indexing. |
| Bug/error | DONE | Corrected the framing risk that bare "detector-space forward model" could imply novelty in detector-space spot-position calculation or indexing. The manuscript now uses detector-space intensity/profile language for the present contribution, and a source scan found no remaining bare `detector-space forward model` matches in `sections/`. |
| CI/CD | DONE | Existing LaTeX CI workflow and build script were left unchanged. Local guarded rebuild succeeded with `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\build-main.ps1`; `main.pdf` was regenerated, `build/main.bbl` contains the new citation, and the final log has no unresolved citation or reference warnings. |
| Deprecation/migration | DONE | Deprecated the broader manuscript phrasing in favor of the narrower detector-space intensity/profile-forward-model framing. The geometric indexing stage is now explicitly separated from later intensity, profile, mosaicity, resolution, optical, structure-factor, and disorder calculations. |
| Documentation | IN PROGRESS | This status file records the citation/framing decision, the independently audited 22-comment response plan, verification state, and release boundary. `AGENTS.md` now enforces the advisor philosophy and traceability rules. No separate advisor-note, response-plan, changelog, or patch-handoff file was created. |
| Shipping/rollback | DONE | No external release was published. The review artifact `main.pdf` was rebuilt locally; rollback is a normal `git revert` of the citation/framing commit. |

## Build And Reset Recovery

The main manuscript uses `latexmkrc` to write the public artifact to repository-root `main.pdf`. Generated LaTeX auxiliaries, logs, and bibliography outputs go into `build/`, which is ignored by git.

Use the guarded clean rebuild when citations or bibliography output look stale:

```powershell
.\scripts\build-main.ps1
```

If VimTeX or another editor watcher is already running, the script stops before touching build state and prints matching process IDs. Stop the watcher in the editor or process manager, then rerun the script. The script intentionally does not kill watcher processes because Windows process command lines do not reliably prove which repository owns a generic `main.tex` watcher.

Underlying commands:

```powershell
latexmk -c main.tex
latexmk -pdf -g -interaction=nonstopmode -file-line-error main.tex
```

After a successful build, root `main.pdf` is the review artifact and GitHub Pages PDF. `build/main.aux` should contain `\bibstyle{apsrev4-2}` and `\bibdata{bibliography/references}`. `build/main.bbl` should be non-empty and contain `\begin{thebibliography}`. There should not be a second tracked `main.pdf` under any subdirectory.

If VimTeX or another editor reports `I found no \bibdata command` after a reset, first stop the continuous build watcher, then run the clean rebuild above. That BibTeX message usually means BibTeX read an incomplete or stale `.aux`; it does not by itself prove that `main.tex` is missing bibliography commands.

## Revision Checklist

Before returning a manuscript edit or new section, check:

- Does the text put the paper before software?
- Does it explain physics before optimization?
- Does it use Q, Q_R, Q_z, m-indexed labels, and reciprocal-space language where appropriate?
- Does it avoid unnecessary software-native terminology in the main text?
- Does it make the measured data and calculated fit comparison clear?
- Does it preserve the central claim that the model quantitatively reproduces line shapes?
- Does it introduce two-component mosaicity early enough and with evidence?
- Does it label reflections in a way a diffraction reader can understand?
- Does the caption teach the reader what to notice?
- Does it show data before explaining the model correction?
- Does it explain bandwidth / Bragg-sphere / mosaic-cap geometry clearly enough to teach it?
- Does it avoid overclaiming that Gaussian/Lorentzian forms are uniquely true?
- Does it explain the m=0, L=3 star feature before using it as validation evidence?
- Are sample-orientation effects included in plotted trajectories, or is the limitation stated?
- Are Q_R, Q_z, L, m, and explicit (h,k,l) labels defined before use?
- Does main text discuss propagated/systematic error rather than hiding it entirely in SI?
- Does the manuscript state what structural model, CIF/SIF file, occupancy changes, or structure-factor fitting were used?
- Does the final comparison make the refinement-quality claim visible?
- Are the Ewald vectors, reflection-family labels, multiplicity, angles, and specialized operations defined before use, with important equations numbered?
- Have vague qualifiers been replaced by a testable condition, value, range, or controlled comparison?
- If a component is called necessary, does an otherwise-identical ablation with residuals or a documented reason for not running one support that claim?
- Does `main.tex` place ordered-film validation before the refinement workflow and PbI2 extension?
- Does every C01-C22 item have an exact change location, verification evidence, and honest status?

## Document Policy

Do not recreate separate advisor-note, meeting-prep, figure-status, supplement-status, input-inventory, TODO, or changelog documents unless explicitly requested. Add new manuscript guidance, active status, open questions, and durable decision summaries here instead.
