# Manuscript Status

Last updated: 2026-08-06

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
| `output/pdf/main_advisor_comment_color_proof.pdf` | Author-reviewed color proof containing three page-2 annotations addressed in the 2026-07-19 proof-response pass. |
| `main_pfm.pdf` | Current 27-page advisor-annotated manuscript reviewed on 2026-08-06. It contains 12 substantive comments on the Methods and ordered-film figures plus one empty note. |
| `build.zip` and `2D_Supplemental.zip` | Executable-model and manuscript/SI archives used for the independent implementation-parity audit and the present revision. |

Current `main.tex` includes:

```tex
\input{sections/introduction}
\input{sections/modelling_methods}
\input{sections/mosaicity_texture}
\input{sections/correlated_effects}
\input{sections/results_ordered}
\input{sections/refinement_workflow}
\input{sections/results_diffuse_pbi2}
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

## Advisor Comment Audit And Immediate Revision - 2026-08-06

The current annotated manuscript contains 12 substantive comments. The immediate revision follows the advisor's established division of labor: the main text teaches the physical sequence and the observable consequence, while coordinate bookkeeping, ray-plane intersections, optical boundary equations, numerical quadrature, and full profile definitions are placed in the Supporting Information. Grazing-incidence optics is treated as a standard correction, not as a principal contribution.

| ID | Advisor comment | Status | Implemented response and remaining gate |
|---|---|---|---|
| A01 | Discuss receiving detector geometry as clearly as sample geometry. | DONE | Section 2.1 now explains sample acceptance and detector acceptance as two consecutive physical operations. SI Sec. S1 gives the sample-plane and tilted-detector-plane intersections, continuous pixel coordinates, front-face condition, active-area bounds, and calculation order. The ordered-film configuration is correctly described as an unbounded in-plane sample plane, so no unsupported sample-edge broadening is claimed. |
| A02 | Use the conventional crystallographic definition of displacement parameters. | DONE | The main text now writes the structure factor with the conventional crystallographic displacement factor `T_a(hkl)`. SI Sec. S2 defines the isotropic U/B relation and records the current implementation scope: isotropic CIF displacement input and one shared uniaxial film-frame pair when directional damping is released. General site-resolved anisotropic CIF tensors are not claimed. |
| A03 | Remove the set-builder equation for the m family. | DONE | The set equation and member-count symbol were removed. Prose now states that common m means common ideal Q_R, while every allowed physical (h,k,l) member is evaluated before summation and no second multiplicity factor is applied. |
| A04 | Explain the relative 003/006 intensity and the extended 003 streak. | BLOCKED | Figure 5 is now used strictly as an observation. The text identifies the extended 003 region and more localized 006 region, but does not assign their relative intensity or the streak mechanism from detector position alone. Completion requires direct measured/model arrays on one common physical scale together with the retained spectrum, structure factors, refined geometry, orientation distribution, background treatment, and detector mapping. |
| A05 | Make Figure 6 carry the two-component mosaic explanation. | DONE | Figure 6 now labels the narrow core and broad low-probability component and explains which detector features sample each angular range. The caption explicitly states that the schematic explains sensitivity but is not an ablation. The no-tail and reoptimized Gaussian-only tests remain the separate C18 evidence gate. |
| A06 | Explain wavelength sampling as part of the overall calculation strategy. | DONE | Section 2 begins with the complete physical sequence. Section 2.4 now introduces position, direction, and wavelength as coordinates of one weighted incident state. SI gives the equal-mass antithetic Latin-hypercube source construction and convergence requirements. The continuous mosaic density and analytic Ewald roots are distinguished from a stochastic crystallite cloud. |
| A07 | Decide whether grazing-incidence optics belongs in the main text. | DONE | The optical derivation was removed from the main text. One short paragraph states its standard corrective role and explicitly says it is not a principal result. Boundary equations, branch conventions, attenuation, flux normalization, and wavelength dependence remain in SI Sec. S4.3. No claim that the effect is small in a particular ROI is made without a sensitivity calculation. |
| A08 | Define or remove the optical-to-kinematic phrase and account for the reflectivity work. | BLOCKED | The phrase was removed. The main text now identifies the near-critical signal as a separate standard specular regime and excludes it from the mosaic argument. SI records the Parratt diagnostic and the earlier empirical crossover, but direct matched measured and complete calculated arrays are still absent. The reconstructed raster traces are not used as quantitative main-text evidence. |
| A09 | Rewrite the held-out-prediction language. | DONE | Machine-learning terminology was removed. The text now states plainly that the 5, 10, and 15 degree datasets entered the staged refinement and that the displayed 5 degree condition is a fitted comparison, not an independent incidence-angle prediction. |
| A10 | Specify where the ordered-film comparison is shown. | DONE | The introduction and Section 3 now identify the Bi2Se3 and Bi2Te3 comparison figures explicitly. |
| A11 | Define the extraction or projection operation. | DONE | Section 2.1 and Section 3 state that each calculated trajectory defines a finite integration region and coordinate. Measured signal and calculated detector density use the same calibrated map, limits, and area normalization, with signal and normalization accumulated before division. SI gives the finite detector and angular-bin definitions and uncertainty propagation. |
| A12 | Make Figure 7 readable and explain how the profiles were generated. | DONE | The former composite was split into one full page per material. Each page now has large descriptive headings, a large detector panel, a larger profile panel, and a teaching caption. The caption defines centerlines, integration regions, detector-side signs, measured/calculated curves, and the supported claim. This layout correction does not resolve the separate provenance and common-scale limitations of the retained historical plot assets. |

Immediate manuscript work is therefore complete for A01--A03, A05--A07, and A09--A12. A04 and A08 remain blocked because they require scientific evidence that cannot be created reliably from the retained raster figures. The broad-component necessity test under C18 and direct ordered-figure provenance remain independent evidence gates rather than prose tasks.

## Advisor Comment Audit And Revision Tasklist - 2026-07-18

The packet inventory was checked against the annotated PDF rather than inferred from the response-plan Markdown. The 29-page PDF contains exactly 22 substantive annotations by Paul Miceli: 18 sticky notes and 4 highlighted-text comments on pages 1, 3, 5, 6, 7, 8, 11, 14, and 17. No substantive annotation is missing from the response plan.

Audit verdicts:

- **AGREE**: the packet's proposed response is appropriate as written in substance.
- **AGREE WITH MODIFICATION**: the advisor's intent is sound, but the proposed implementation is too broad, too certain, duplicative, or must be conditioned on the actual model/data.
- **DISAGREE WITH PROPOSED IMPLEMENTATION**: the underlying advisor concern is valid, but the packet prescribes wording or work that should be replaced rather than merely adjusted.
- **CHECK**: the advisor's wording is ambiguous enough that it should not be treated as a settled literal instruction.

Overall, the 2026-07 packet was directionally strong. This paragraph records the historical closure state from that pass. The later 2026-08-06 audit obtained the executable model and configuration, closed the geometry and calculation-order parity items, corrected the source-versus-mosaic sampling description, and demoted optics in the main text. The remaining scientific evidence gates are the common-scale 003/006 calculation, controlled mosaic ablations, direct ordered-figure provenance, and direct near-critical reflectivity arrays.

One packet instruction is stale relative to the repository: the ordered Bi2Se3/Bi2Te3 detector and profile panels no longer need to be “restored.” The assets exist and already show close measured/calculated overlays. They still need readability checks, residual/uncertainty support, and verification that the displayed curves and labels are generated from the final analysis.

### Independent critical findings beyond the packet

1. **The former inverse-order bandwidth argument has been removed.** The main text and SI now reconstruct the Ewald sphere for every wavelength and incident-direction sample, so both center and radius move; the Bragg-law derivative is retained only as a limiting check. The low-\(L\) mechanism remains unassigned until the measured spectrum and a direct full-vector simulation are available.
2. **The annotation's 003/006 detuning premise may compare unlike angles.** The manuscript gives \(c=28.6561\) Å and nominal 003/006 positions near \(2\theta=6^\circ/12^\circ\), which imply \(\lambda\approx1.00\) Å and conventional \(\theta_{B,003}\approx3.00^\circ\), \(\theta_{B,006}\approx6.01^\circ\). At \(\theta_i=5^\circ\), the naive Bragg-angle offsets would make 006 closer, not “very far” from condition. Do not use either subtraction as the final result; compute the full vector/orientation mismatch with actual wavelength, alignment, and angle definitions before using 003/006 visibility as evidence for the long tail.
3. **The optical equations and executable boundary implementation are now cross-checked.** The main text and SI conserve tangential wavevector, use the decaying complex-\(k_z\) branch, integrate attenuation over normal depth, and distinguish field amplitudes from normal flux. Optics is now a standard SI correction rather than a manuscript contribution. A full-versus-fixed-\(n\) ROI comparison remains optional internal sensitivity evidence if a numerical size claim is later desired.
4. **The near-critical crossover is explicitly provisional.** The digitized limiting-curve overlay is absent from the main text, and the SI retains the earlier empirical crossover only to make its assumptions auditable. Direct measured and calculated arrays, the complete prediction, and a declared mosaic treatment are still required for quantitative evidence.
5. **The ordered comparisons are now described in plain experimental language.** All three incident angles are disclosed as refinement inputs. The section heading and prose avoid held-out, in-sample, and validation language and state that the displayed condition was included in the refinement.
6. **The structure-factor convention now follows crystallographic usage.** The main text uses fractional coordinates and a conventional displacement factor \(T_a(hkl)\). The SI gives the isotropic U/B conversion and the verified current implementation scope. General site-resolved anisotropic CIF tensors are not imported, and the manuscript no longer implies otherwise.
7. **The next-draft PbI2 scope is disproportionate.** `results_diffuse_pbi2.tex` is 348 lines versus 49 lines for the ordered test cases and still reports a pending transition-matrix refit. For the next advisor draft, either omit PbI2 from the main text or reduce it to the measured motivation and one final data/model panel; move the transition-matrix derivation, parameter table, and parent-stack detail to SI.
8. **Notation and supplement sources are consolidated.** Built sources now use \(Q_R\), lower-case Miller indices, \(p_{\mathrm{tail}}\) for the mosaic mixture, distinct phase/index symbols, and explicit family-versus-multiplicity language. The standalone implementation outline was merged into the built SI and deleted rather than retained as a competing source.
9. **The ordered overlays are more readable but not yet provenance-ready.** The two materials now have separate full-page figures with larger detector and profile panels and descriptive headings. The retained assets still lack complete direct plotting arrays and a current accepted generation record. Record normalization and scaling, verify whether relative intensities share a meaningful scale, retain direct source arrays/scripts, and add residual or uncertainty support before using them for stronger quantitative claims.
10. **The ambiguous “grown by TEM” phrase was removed.** No replacement growth method was invented; a specific method can be added later only from verified experimental provenance.

| ID | Advisor request | Audit verdict | Current state | Priority | Independent recommendation and acceptance gate |
|---|---|---|---|---|---|
| C01 | Open with 2D van der Waals films | AGREE | DONE | P1 | Resolved in the opening paragraphs and first figure of `sections/introduction.tex`. The 115-word first paragraph now follows layered-film importance -> substrate/growth-dependent azimuthal registry -> operational 2D-powder definition -> simultaneous area-detector observables, with no model or software language. The material-family catalogue was removed, the orientational-limits comparison is now the first visual, citation fit was checked, and a clean build plus rendered review of `main.pdf` pages 1-3 verified the change. |
| C02 | Explain the Ewald sphere and diffraction selection | AGREE WITH MODIFICATION | DONE | P1 | Resolved in Fig. 1 and its explanatory paragraph in `sections/introduction.tex`. The caption and prose connect isolated point, spherical-shell, and axial-ring intersections to sparse spots, Debye--Scherrer rings, and paired 2D-powder features. The 2026-07-19 author-proof pass restored the earlier eight-panel layout and curated reciprocal-space panels while retaining that physics explanation. The obsolete single-crystal detector schematic and the redraw script that generated the rejected replacements were removed. The clean isolated build and rendered page 2 passed. |
| C03 | State accomplishments and outline the paper | AGREE | DONE | P2 | The close of `sections/introduction.tex` now states only the displayed in-sample fit result and gives the final roadmap: ordered test cases, workflow, then PbI2 extension. It makes no relative-intensity, held-out-prediction, or unique-tail claim. The guarded build has no unresolved references or citations. |
| C04 | Define \(\mathbf k_i\), \(\mathbf k_f\), \(\mathbf Q\), and \(\mathbf G\); number equations | AGREE | DONE | P1 | Resolved at the opening of `sections/modelling_methods.tex`: \(\mathbf k_i\) is the incident wavevector, \(\mathbf k_f\) the scattered wavevector, \(\mathbf Q\) their difference, and \(\mathbf G\) the reciprocal-lattice vector for \((h,k,l)\). Elastic scattering, momentum transfer, Bragg matching, and the scattered-wavevector relation are numbered and referenced as Eqs. 1--4. C04 itself introduced no frame superscripts or rotation-matrix rewrite; separate geometry-interface work for C05--C08, C10, and C11 supplies the broader SI treatment. The final main build, reference scan, and rendered Methods page verify the change. |
| C05 | Define sample intersection | AGREE WITH MODIFICATION | DONE | P1 | Section 2.1 explains sample acceptance physically and SI Sec. S1 gives the forward ray-plane intersection and optional finite support. The implementation/configuration audit confirms that the displayed ordered-film calculations use an unbounded in-plane sample plane, so sample-edge clipping is not claimed as a fitted broadening mechanism. |
| C06 | Unpack incidence geometry and optical corrections | AGREE WITH MODIFICATION | DONE | P1 | The Methods separates sample intersection, local incidence, standard planar-interface correction, scattering restriction, external exit direction, detector mapping, and finite integration. SI records the verified operation order. The optical mathematics is kept subordinate in SI. |
| C07 | Introduce Monte Carlo sampling with incident rays | AGREE WITH MODIFICATION | DONE | P1 | The implementation audit corrected the earlier description. The incident source is represented by seeded equal-mass antithetic Latin-hypercube states in position, direction, and wavelength. The crystallite-orientation distribution is a continuous density and its Ewald intersections are solved analytically rather than drawn as a second Monte Carlo cloud. |
| C08 | Explain footprint from sample intersection | AGREE WITH MODIFICATION | DONE | P1 | The footprint is defined as the weighted distribution of accepted sample-plane intersections, not a second displacement. Methods, SI, Figure 4, and the audited implementation use this same meaning. Optional finite support is documented without claiming edge clipping for the ordered-film results. |
| C09 | Replace vague labels/profile extraction language | AGREE WITH MODIFICATION | DONE | P1 | `sections/modelling_methods.tex` and the caption in `sections/results_ordered.tex` now identify physical \((h,k,l)\)/\(m\) labels, trajectory centerlines, finite detector integration bands, and matched measured/calculated \(Q_z\) or \(L\) profiles using \(Q_R\) consistently. The final main build and static notation scan verify the change. |
| C10 | Explain reciprocal-space construction algorithm | AGREE WITH MODIFICATION | DONE | P1 | SI defines physical rod identities, systematic absences, detector-coverage bounds, weighted source states, continuous mosaic density, analytic moving-Ewald intersections, detector acceptance, and convergence. The description now matches the audited production calculation rather than an event-deposition algorithm. |
| C11 | Put geometric-correction equations in SI | AGREE | DONE | P1 | SI Sec. S1 now contains sample-plane acceptance, the detector rigid transform, tilted detector-plane intersection, continuous pixel coordinates, front-face and active-area tests, and the finite-region integration definition. These equations were checked against the available executable model and result-measure specification. |
| C12 | Repair Figure 4 and caption | AGREE | DONE | P1 | `figures/geometry/sample_geometry_rotation.tex`, `figures/geometry/sample_geometry_alignment.tex`, and the caption in `sections/modelling_methods.tex` now show and define \(\mathbf r_{\mathrm{hit}}\), remove the undrawn \(\delta\) and \(X_s\), keep \(W,H\) in the SI acceptance equation, and define \(\hat{\mathbf g}_0,\hat{\mathbf g}\) as nominal/misaligned axis directions rather than arms. The guarded build and rendered page 7 passed. |
| C13 | Put structure factor before multiplicity | AGREE WITH MODIFICATION | DONE | P1 | Section 2.2 defines the conventional crystallographic structure factor and displacement factor before radial-family grouping. SI records the actual isotropic CIF and shared uniaxial implementation scope. The former Cartesian-tensor-as-definition wording and the unnecessary set-builder equation were removed. |
| C14 | Replace \(\mathbf M_\parallel\) with the explicit 2D-powder rule | AGREE WITH MODIFICATION | DONE | P1 | `sections/modelling_methods.tex` and `2D_Supplemental/SI_failure_modes.tex` define \(m=h^2+hk+k^2\), \(Q_R=4\pi\sqrt m/(\sqrt3a)\), lower-case Miller indices, \(Q_R\)-selected profiles, and crystallographic multiplicity as a one-orbit symmetry count distinct from radial-family member count. Accepted members are summed explicitly without a second factor. Both PDFs build, and the static scan finds no active \(\mathbf M_\parallel\) or \(Q_r\). |
| C15 | Reframe the mosaicity introduction | AGREE | DONE | P1 | The opening of `sections/mosaicity_texture.tex` now follows orientation cause -> detector-space consequence -> measured 003/006 observation -> phenomenological model, while separating the near-critical feature and correlated instrument terms. The final main build and rendered mosaicity page verify the revised sequence. |
| C16 | Replace “a limited part” with a quantitative condition | AGREE | BLOCKED | P0 | The vague phrase is removed. The text now says an ideal aligned crystallite can satisfy at most one discrete \((00l)\) condition and warns that displayed \(2\theta\) cannot be subtracted from incidence. A quantitative 003/006 orientation mismatch still requires the measured spectrum, refined lattice/alignment, bandwidth, and full vector geometry. |
| C17 | Remind the reader that \(\phi\) is azimuth | AGREE | DONE | P2 | `sections/modelling_methods.tex` defines \(\phi\), and the observation and caption in `sections/mosaicity_texture.tex` repeat “detector-plane angle/azimuth \(\phi\).” Unrelated optical/phase symbols were removed or renamed; the final builds and static symbol scan verify the convention. |
| C18 | Demonstrate Gaussian core plus Lorentzian tail quantitatively | AGREE WITH MODIFICATION | BLOCKED | P0 | The moving-Ewald error and necessity overclaims are removed; the broad component is explicitly phenomenological and only adequate within the fitted set. Completion requires direct arrays for a same-fit no-tail counterfactual, a fairly re-optimized Gaussian-only model, multi-angle residuals, widths/tail fraction, correlations, uncertainty, and one declared comparison metric. |
| C19 | Separate \(L\approx0\) intensity from mosaicity | AGREE WITH MODIFICATION | DONE | P0 | `sections/mosaicity_texture.tex` excludes the near-origin feature from mosaic evidence and points to the separate Reflectivity subsection in `sections/correlated_effects.tex`. That subsection states the missing direct arrays, complete prediction, and mosaic treatment explicitly, and the provisional digitized overlay is omitted from the main text. The final main build and source scan verify the separation; a quantitative near-critical result remains a distinct blocked evidence task. |
| C20 | Introduce and justify optical constants | DISAGREE WITH PROPOSED IMPLEMENTATION | DONE | P2 | The main text now treats refraction and attenuation as standard corrections and explicitly says they are not a principal result. SI retains the boundary equations, branch convention, attenuation integral, amplitude-versus-flux distinction, and wavelength accumulation. No numerical-size claim is made, so a full-versus-fixed-n comparison remains optional internal QA rather than a main-text completion gate. |
| C21 | Reframe ordered films as “Test cases:” | DISAGREE WITH PROPOSED IMPLEMENTATION / CHECK | DONE | P0 | The heading in `sections/results_ordered.tex` is literally “Test cases: Bi2Se3 and Bi2Te3 films.” The opening discloses that all \(5^\circ\), \(10^\circ\), and \(15^\circ\) images were fitted and bounds the comparison to selected locations and apparent line shapes; “Validation” and held-out-prediction language were not added. The final main build and heading/language scan verify the change. |
| C22 | Move workflow directly after ordered validation | AGREE | DONE | P0 | `main.tex`, the roadmap in `sections/introduction.tex`, and the opening of `sections/refinement_workflow.tex` now agree on ordered test cases -> refinement workflow -> PbI2 extension. The placement meta-comment was removed; the final input-order scan and main build verify the sequence. |

### Author proof comments - 2026-07-19

The color proof contains exactly three author annotations, all on page 2. These use `U` identifiers so they remain distinct from the audited C01--C22 advisor packet.

| ID | Exact author comment | Disposition | State | Revision and acceptance evidence |
|---|---|---|---|---|
| U01 | “fig 1 b,e, and h need to be reverted to the old figures. Why did you change them?” | AGREE WITH MODIFICATION | DONE | Panel (b), `figures/intro/mono_single_crystal.png`, was already byte-identical to the pre-change asset and needed no edit. The prior curated `reciprocal_3d_powder.png` and `reciprocal_2d_powder.png` assets were restored from `d0a05a7`. With U02 restoring the eight-panel layout, they are again panels (d) and (g). Their Git blobs now match the requested historical versions, and rendered page 2 confirms the visual restoration. |
| U02 | “why did you change figure 1c?” | AGREE | DONE | The single-crystal detector schematic had been added during C02 to complete a 3-by-3 real/reciprocal/detector matrix, even though earlier history deliberately omitted that cell. The schematic was removed, the detector cell was returned to blank, and all later panel labels and references were shifted back to the eight-panel convention. The C02 Ewald-selection explanation remains in the caption and prose. The obsolete schematic asset was deleted. The redraw script was also deleted because its only historical version reproduces the rejected reciprocal-panel replacements rather than the curated assets. The clean isolated build and rendered page 2 passed. |
| U03 | “We should avoid semicolons and never use em-dashes.” | AGREE WITH MODIFICATION | DONE | Prose semicolons were removed from all main-text and SI narrative, captions, lists, and tables by splitting causal or contrasting clauses into sentences. No rendered em dash is present. Mathematical semicolons that separate a function variable from its parameters and source-only TeX/TikZ command terminators were retained because they are notation or syntax, not prose punctuation. Source scans, a 27-page clean isolated main build, an 18-page SI rebuild, and PDF-text inspection passed. |

### Recommended execution order

1. **Recover direct evidence arrays for the blocked work.** Preserve the measured spectrum, refined geometry, direct ordered/mosaic/near-critical arrays, normalization, and plotting scripts together with the accepted configuration that produced them.
2. **Complete the central quantitative evidence gates.** Use the retained spectrum and geometry for the full-vector 003/006 comparison. Run the same-fit no-tail and reoptimized Gaussian-only mosaic comparisons. Regenerate the near-critical result from direct measured and complete calculated arrays only if it remains part of the argument.
3. **Finish ordered-figure provenance.** Record the source arrays, plotting script, image-wise nuisance scales, and whether any displayed amplitudes share a physical scale. Add residual or uncertainty support before stronger quantitative language.
4. **Decide the PbI2 main-text scope.** Keep the transition-matrix extension subordinate until its numerical refit and direct comparison figure are ready.

### Completion protocol

For each current A01-A12 item and each active earlier evidence gate, record the exact revised manuscript/SI location, the evidence or build used to verify it, and one of `TODO`, `IN PROGRESS`, `DONE`, `CHECK`, `BLOCKED`, or `PARKED`. A placeholder, future-tense caption, or related paragraph is not `DONE`. Any disagreement or deliberate non-adoption must be evidence-based and recorded here before the response letter is drafted.

## Core Thesis

The next draft should visibly test whether the forward model quantitatively reproduces measured area-detector diffraction line shapes for Bi2Se3 and Bi2Te3. Quantitative and refinement-quality language is an acceptance target, not a conclusion to assume before the remaining provenance, scaling, residual, and uncertainty checks.

Main claim:

> With the same detector-space coordinate map and finite integration applied to measured and calculated quantities, the displayed Bi2Se3 and Bi2Te3 fitted conditions show close agreement in selected feature locations and apparent line shapes. Claims about common-scale relative intensities, independent prediction, or refinement-quality interpretation remain conditional on verified source arrays, normalization, residuals, and uncertainty.

Use "refinement-quality" carefully. Tie it to plotted data/model overlays, propagated/systematic error, and the structure-factor/CIF/SIF treatment.

## Advisor Philosophy

1. Paper first, software second. Do not make software cleanup or release polish the manuscript bottleneck.
2. Show the strongest supported result clearly. The current central result is close agreement at displayed fitted conditions in selected Bi2Se3 and Bi2Te3 feature locations and apparent line shapes. Strengthen this only after the quantitative evidence gates pass.
3. Write for a diffraction/scattering audience. Use Q, Q_R, Q_z, m-indexed reflection families, explicit (h,k,l) labels where useful, Bragg rods, Bragg positions, reciprocal space, incident angle, mosaicity, finite detector integration, and line-shape fitting.
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
3. Point out puzzling observations first: off-condition reflections, low-order features, and the m=0, L=3 star feature; present proposed mechanisms only afterward.
4. Explain model ingredients physically: sample geometry, detector geometry, incident angle, beam position, divergence, wavelength spread, mosaicity, bandwidth, structure factor, and resolution.
5. Introduce the two-component mosaicity parameterization early, while treating the broad Lorentzian-like component as phenomenological until controlled comparisons establish necessity.
6. Explain the wavelength-dependent Ewald construction as a tutorial point, with the center and radius rebuilt for every wavelength and incident direction.
7. Separate the m=0, L=3 observation from its proposed mechanism; do not use it as validation evidence until the full-vector calculation and direct arrays are available.
8. Show how data and calculation are projected onto interpretable Q-space trajectories.
9. Demonstrate direct measured/calculated overlays for Bi2Se3 and Bi2Te3.
10. Use verified overlays, propagated/systematic error, and structure-factor treatment before adopting refinement-quality framing.
11. Move computational implementation details to the supplement after the main argument is understandable.
12. Treat PbI2, stacking faults, and diffuse scattering as subordinate until the ordered-film story is clear.

## Current Repo And Manuscript State

| Item | Status | Notes |
|---|---|---|
| `main.tex` scaffold | DONE | Inputs model, mosaic/correlated effects, ordered test cases, refinement workflow, PbI2 extension, and conclusion in that order. |
| Build plumbing | DONE | Uses standard BibTeX via `\bibliography{bibliography/references}`. Generated aux, BBL, log, SyncTeX, and non-review PDFs are ignored. |
| `sections/introduction.tex` | DONE | C01--C03 and the current advisor language corrections are incorporated: layered-film opening, visible Ewald/detector tutorial, bounded fitted-condition accomplishment, narrowed contribution statement, and the final roadmap. |
| `sections/modelling_methods.tex` | DONE | The main text gives the physical sequence, balanced sample/detector geometry, conventional structure-factor notation, and prose family grouping. Detailed geometry and implementation equations are in SI and have been checked against the available executable model. |
| `sections/mosaicity_texture.tex` | IN PROGRESS | Causal prose, \(\phi\), and near-critical separation are resolved; quantitative broad-component necessity remains blocked on C18 arrays/ablations. |
| `sections/correlated_effects.tex` | DONE | Wavelength is integrated into the incident-state strategy. Optics is reduced to a standard correction and the near-critical response is bounded as a separate diagnostic. Direct reflectivity arrays remain an evidence task, not a prose or section-completion task. |
| `sections/results_ordered.tex` | IN PROGRESS | Uses plain fitted-comparison language, defines the finite profile operation, and splits the ordered figure into readable material-specific pages. Direct-source provenance, common-scale interpretation, residuals, and uncertainty remain evidence limitations. |
| `sections/results_diffuse_pbi2.tex` | IN PROGRESS | Reintroduced as an extension; keep subordinate until the ordered-film evidence story is complete. |
| `sections/refinement_workflow.tex` | DONE | Correctly follows the ordered test cases, distinguishes instrument and sample stages, and uses observables consistent with the audited detector measure. |
| `sections/discussion_conclusion.tex` | DONE | Summarizes the bounded fitted-condition result, makes standard optics subordinate, states the evidence limits, and keeps PbI2 as an extension without unique-tail or quantitative-validation overclaims. |
| Ordered-film figures | IN PROGRESS | The readability and caption changes are complete. Direct-array provenance, common scaling, residuals, and uncertainty remain open before stronger quantitative claims. |
| PbI2 figures | IN PROGRESS | Parent-stack schematic complete; reciprocal-space and measured/calculated disorder figures still need completion. |
| Software release polish | PARKED | Paper must demonstrate scientific value first. |

## Active Tasks

### P0 - Next Advisor Draft

| Task | Status | Deliverable | Notes |
|---|---|---|---|
| Finalize Bi2Se3 detector/projection figure | IN PROGRESS | Main-text figure | The full-page layout, descriptive headings, and caption are complete. Verify direct-source provenance, scaling, and uncertainty support before stronger claims. |
| Finalize Bi2Te3 detector/projection figure | IN PROGRESS | Main-text figure | The full-page layout now matches Bi2Se3 and the rendered y-axis is readable. Verify direct-source provenance, scaling, and uncertainty support before stronger claims. |
| Add Bi2Se3 Q_z projection overlays | IN PROGRESS | Figure panels | Existing overlays are enlarged and explained. Verify direct-source provenance, normalization, residuals, and uncertainty. |
| Add Bi2Te3 Q_z projection overlays | IN PROGRESS | Figure panels | Existing overlays are enlarged and explained. Verify direct-source provenance, normalization, residuals, and uncertainty. |
| Define reflection-family labels | DONE | Figure/caption convention | Main text and SI define lower-case \((h,k,l)\), \(m=h^2+hk+k^2\), \(Q_R\), \(Q_z\), and \(L\), with family member count separated from one-orbit multiplicity. |
| Add early two-component mosaicity evidence | BLOCKED | Text + controlled comparison | Observation, model, and limitation are now separated; direct arrays are still required for the matched no-tail and re-optimized Gaussian-only comparisons under C18. |
| Verify ordered-figure provenance and scaling | BLOCKED | Reproducible figure record | Supply scripts/direct arrays; state normalization and whether scales are common across families/images; add residual/uncertainty support before claiming relative-intensity validation. |
| Correct moving-center bandwidth geometry | DONE | Main/SI physics interface | Main text and SI rebuild the Ewald center and radius for every wavelength/direction sample and reject a universal inverse-order rule. |
| Test the low-L bandwidth mechanism directly | BLOCKED | Direct full-vector simulation | Requires the measured spectrum, executable model/configuration, refined geometry, and direct arrays; the manuscript leaves the mechanism unassigned. |
| Verify 003/006 Bragg conditions and orientation mismatch | BLOCKED | Quantitative sentence + calculation record | Obtain the actual wavelength distribution, then use full vector geometry, refined lattice, alignment, bandwidth, and explicit angle definitions; do not subtract incidence from displayed 2theta. |
| Bound the role of optical constants | PARKED | Optional internal sensitivity check | Optics is not a principal contribution and no numerical-size claim is made. A full-versus-fixed-n comparison can be run later as internal QA if the retained spectrum, optical table, and direct ROI arrays are assembled. |
| Replace provisional reflectivity traces | BLOCKED | Direct-array full prediction | Current plot is digitized/repaired and omits the blended curve. Obtain direct measured and model arrays, show the full prediction, and declare how mosaicity enters. |
| Reorder workflow before PbI2 | DONE | `main.tex` + workflow opening | Ordered test cases now lead directly to the refinement workflow, then to the PbI2 extension; the placement meta-comment is removed. |
| Confirm ordered-section “Test cases:” intent | DONE | Heading decision | The heading is literally “Test cases: Bi2Se3 and Bi2Te3 films”; no “Validation” or held-out claim was added. |
| Decide next-draft PbI2 scope | TODO | Main-text/SI boundary | Prefer omission until refit, or reduce to measured motivation plus one final data/model panel and move transition-matrix detail to SI. |
| Remove ambiguous “grown by TEM” | DONE | Results wording | The phrase is removed; no replacement growth method was invented without verified provenance. |
| Write Q-space/projection caveat | DONE | Methods/results paragraph | Results state why projected Q_z is not an ideal perfect-crystal cut and why data/model comparison remains meaningful. |
| Disclose experimental incident angles | DONE | Ordered-results prose | The ordered section states that images at \(5^\circ\), \(10^\circ\), and \(15^\circ\) were included in refinement and distinguishes the displayed \(5^\circ\) comparison. |
| Replace remaining future-tense scaffold prose | DONE | Results prose | Built main-text and SI prose describe the present figures and current evidence boundaries directly. Placeholder macros remain only as safe build fallbacks when an image file is absent. |

### P1 - Complete-Draft Support

| Task | Status | Deliverable | Notes |
|---|---|---|---|
| Consolidate 2theta-phi/caked implementation supplement | DONE | Built supplement section | Unique material was merged into `2D_Supplemental/SI_failure_modes.tex`; the competing standalone outline was deleted. |
| Explain sub-pixelation/binning | DONE | Supplement section | SI defines the continuous detector density, native-pixel or finite-angular-bin integration, signal/normalization accumulation, and uncertainty propagation. |
| Explain weighted source-state quadrature | DONE | Supplement section | SI defines the seeded equal-mass antithetic Latin-hypercube construction in two positions, two directions, and wavelength, together with convergence and provenance requirements. |
| Explain continuous mosaic evaluation | DONE | Supplement section | SI states that mosaicity remains a continuous angular density and that wavelength-specific Ewald roots are solved analytically. No stochastic crystallite-orientation cloud is deposited. |
| Consolidate notation | DONE | Main text + SI convention | Built sources use \(Q_R\), lower-case Miller indices, \(p_{\mathrm{tail}}\), distinct phase/index symbols, and explicit family-versus-multiplicity language. |
| Complete geometric-correction SI chain | DONE | Supplement section | Sample and detector intersections, rigid detector mapping, active-area conditions, finite detector integration, moving wavelength, and standard planar-interface corrections are present and checked against the available implementation. |
| Repair sample-geometry Figure 4 | DONE | Main-text figure + caption | Figure/caption define \(\mathbf r_{\mathrm{hit}}\) and axis directions, remove \(X_s\) and the undefined \(\delta\), and place \(W,H\) in the SI acceptance equation. |
| Add h-BN fitting method | TODO | Supplement section | Unique workflow step mentioned in the paper. |
| Assemble full ordered-film peak-profile checks | BLOCKED | Supplement figures | Direct measured/model arrays and plotting provenance are required for expanded panels, residuals, and uncertainty. |
| Finalize structure-factor/CIF/SIF and occupancy discussion | IN PROGRESS | Main text plus SI | The conventional structure-factor and verified isotropic/shared-uniaxial implementation scope are explicit. The final fitted structural file, occupancy provenance, and any future general anisotropic-tensor support remain to be documented before numerical refinement claims. |
| Add propagated/systematic error support | IN PROGRESS | Main text plus SI | Main text gives the interpretation boundary; SI carries derivation. |

### P2 - Parked

| Task | Status | Reason |
|---|---|---|
| PbI2 diffuse scattering / stacking-fault finalization | IN PROGRESS | Keep subordinate to the ordered-film evidence story. |
| PbI2 selected-rod comparison figures | TODO | Placeholder exists; generate a direct-source figure later. |
| Software release cleanup | PARKED | Paper first. |
| Full software feature documentation | PARKED | Useful later, not central to current draft. |

## Immediate Checklist

- [x] Complete the Bi2Se3 main-text layout and readability review. Direct-array provenance remains a separate open evidence task.
- [ ] Recover Bi2Se3 direct plotting arrays, scaling record, residuals, and uncertainty support.
- [x] Complete the Bi2Te3 main-text layout and rendered y-axis readability review. Direct-array provenance remains separate.
- [ ] Recover Bi2Te3 direct plotting arrays, scaling record, residuals, and uncertainty support.
- [x] Initial m or explicit (h,k,l) reflection-family label convention.
- [x] Paragraph explaining imperfect Q-space/projection interpretation.
- [x] Paragraph and figure concept for the two-component orientation distribution, with explicit separation between geometric sensitivity and ablation evidence.
- [x] State that the \(5^\circ\), \(10^\circ\), and \(15^\circ\) Bi2Se3/Bi2Te3 images were included in refinement and identify the displayed \(5^\circ\) comparison.
- [x] Merge the standalone implementation outline into the built SI and consolidate notation.
- [x] Verify the sample/detector intersections, detector mapping, calculation order, and source-versus-mosaic integration against the available implementation.
- [x] Correct the wavelength construction so each sample moves both the Ewald-sphere center and radius; remove the universal inverse-order claim.
- [ ] Test the proposed low-L bandwidth mechanism with the measured spectrum and direct full-vector simulation.
- [ ] Fair Gaussian-only refit, same-fit no-tail counterfactual, and Gaussian-plus-Lorentzian comparison across multiple angles with residuals/correlation/uncertainty.
- [ ] Verified 003/006 full orientation mismatch from actual wavelength, lattice, alignment, bandwidth, and like-for-like angle definitions.
- [x] Physics-check the optical boundary, depth attenuation, and amplitude/flux interface, move the derivation to SI, and state that optics is not a principal contribution.
- [ ] Optional internal QA: run a bounded full-versus-fixed-\(n\) ROI sensitivity only if the manuscript later makes a numerical-size claim for the optical correction.
- [ ] Direct-array measured/full-model near-critical plot replacing the digitized/repaired limiting traces.
- [x] Move the workflow directly after ordered-film test cases and before PbI2.
- [x] Use the literal “Test cases:” heading without adding “Validation” or held-out claims.
- [ ] Decide whether PbI2 is omitted or reduced to one result panel until the refit is complete.
- [x] Remove “grown by TEM” without inventing a replacement growth method.

## Advisor Questions

- Is the proposed reflection-family labeling convention clear enough?
- Which Bi2Se3/Bi2Te3 incident angles should be main-text figures versus supplement?
- Should Lorentzian-tail evidence be a standalone figure or part of the mosaicity figure?
- How many Q_z projection panels are enough for the main text?
- Did “Test cases:” on page 14 request that exact heading prefix, or only validation framing?
- If a later internal sensitivity calculation finds a material optical effect in a central ROI, should that result be added to SI? The present main-text decision is already to keep optics subordinate.

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
| `figures/intro/` | DONE | Fig. 1 uses the restored eight-panel layout and the requested curated reciprocal-space assets. Panel (b) was already unchanged. The added single-crystal detector schematic and the nonmatching redraw script were removed. The caption and prose still map single-crystal points to sparse spots, 3D shells to rings, and 2D-powder reciprocal rings to paired detector features. Rendered page 2 was checked. |
| `figures/results_ordered/00L_region_marked.png` | IN PROGRESS | Built low-L m=0 observation crop; it is explicitly excluded from broad-mosaic evidence pending direct near-critical arrays and mechanism testing. |
| `figures/results_ordered/figure7_bi2se3_qr_rod_qz_profiles_detector_selected_q_regions_5deg.png` | IN PROGRESS | Main-text readability and caption integration are complete. Direct-source generation provenance remains open. |
| `figures/results_ordered/figure7_bi2te3_qr_rod_qz_profiles_detector_selected_q_regions_5deg.png` | IN PROGRESS | Main-text styling and readability now match Bi2Se3. Direct-source generation provenance remains open. |
| `figures/results_ordered/figure7_bi2se3_qr_rod_qz_profiles.png` | IN PROGRESS | The enlarged overlay passes rendered axis/label review. Direct arrays, scaling provenance, residuals, and uncertainty remain open. |
| `figures/results_ordered/figure7_bi2te3_qr_rod_qz_profiles.png` | IN PROGRESS | The enlarged overlay passes rendered axis/label review. Direct arrays, scaling provenance, residuals, and uncertainty remain open. |
| `figures/correlated_effects/fig_reflectivity_data_parratt_kinematic.png` | CHECK | Provisional only: digitized/repaired traces, clipped-branch plateau, and no full blended prediction. Replace with direct exports before using as evidence. |
| `figures/mosaic/lorentzian_tail_evidence.png` or existing ordered-film crop | TODO | Direct evidence that narrow-core mosaicity alone is insufficient. |
| `figures/mosaic/moving_ewald_wavelength_series.png` | BLOCKED | Planned wavelength-by-wavelength moving-center/radius schematic or direct simulation; requires the verified spectrum/model inputs before it can support a mechanism claim. |
| `figures/mosaic/low_q_003_03_06_data_model_overlay.png` | BLOCKED | Planned measured/calculated overlay or control comparison; direct arrays and the verified full-vector calculation are missing. |
| `figures/results_pbi2/transition_matrix/pbi2_polytype_stacks.{tex,png}` | DONE | Figure 11 parent-stack schematic in rF_sigma notation. |
| `figures/results_pbi2/pbi2_raw_detector_diffuse_motivation.png` | TODO | PbI2 measured detector image with diffuse features. |
| `figures/results_pbi2/pbi2_diffuse_data_model_overlay.png` | TODO | Measured/ordered/faulted/residual projection figure. |

Recommended main-text sequence:

1. Orientational limits / 2D powder motivation.
2. Model geometry and mosaicity.
3. Low-L m=0 star-feature observation, explicitly separated from any mechanism claim until direct full-vector tests are available.
4. Bi2Se3 ordered-film detector setup and Q_z overlays.
5. Bi2Te3 ordered-film detector setup and Q_z overlays.
6. Refinement workflow and uncertainty/structure-factor framing.
7. PbI2 extension only if it does not compete with the ordered-film evidence story.

## Projection And Coordinate Guidance

Use Q_z as the main horizontal/projected coordinate for line profiles when that is the physical interpretation. Use Q_R or scalar m to identify which reciprocal-space trajectory is sampled.

The manuscript should say:

- data are projected along trajectories corresponding to fixed Q_R or m-family conditions;
- profiles are reported versus Q_z;
- mosaicity, beam divergence, wavelength spread, incidence-angle uncertainty, detector mapping, and finite integration make the projected observable a finite-region measurement rather than an ideal reciprocal-space line cut;
- calculation and data pass through the same coordinate transformation, finite integration limits, and normalization;
- therefore the measured/calculated comparison is meaningful and is the central method test.

Do not overstate Q-space exactness. If a plotted reciprocal-space trajectory omits sample rotation, chi, or alignment distortions, describe it as an approximate projection guide rather than a physical explanation of peak offsets.

Suggested concise caveat:

> The horizontal coordinate is reported as Q_z along the selected trajectory. Because mosaicity, divergence, wavelength spread, incidence-angle uncertainty, and detector sampling broaden the effective scattering condition, these profiles are not ideal reciprocal-space cuts. The comparison remains direct because the same coordinate transformation and finite integration operation are applied to the calculated and measured detector quantities.

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

- Off-condition reflections motivate testing a component broader than the narrow mosaic core.
- The current Gaussian-like-core plus Lorentzian-like-broad-component parameterization is an adequate phenomenological description within the fitted set, not proof of a unique physical distribution.
- Sensitivity to the broad component is coupled to wavelength bandwidth, divergence, alignment, and background.
- Near-critical low-\(L\) intensity additionally depends on optical response and is excluded from evidence for the broad component.
- Necessity may be claimed only after a same-fit no-tail counterfactual and a fairly re-optimized Gaussian-only comparison show worse residuals across multiple angles, with fitted values, correlations, and uncertainty.

The compact parameterization belongs in the main text because it states the tested physical hypothesis; the controlled evidence and implementation detail can be expanded in SI.

## Bandwidth / Bragg-Sphere / Mosaic-Cap Tutorial

This is a conceptual contribution and should be explained step by step without assigning the low-\(L\) mechanism prematurely.

Required explanation:

1. Define the incident wavevector, exit wavevector, reciprocal-lattice vector, Ewald sphere, and elastic intersection condition.
2. For every wavelength and incident-direction sample, rebuild both the Ewald-sphere center \(-\mathbf k_i\) and radius \(2\pi/\lambda\).
3. Explain that allowed intersections are not populated uniformly; intensity also depends on the mosaic distribution, beam divergence, structure factor, optics, and detector acceptance.
4. Use the Bragg-law derivative only as a limiting sanity check, not as a universal inverse-order or cap-overlap law.
5. Pair schematic examples with calculated detector images only after the spectrum and executable geometry are verified.
6. Then compare measured and calculated detector-space consequences using direct arrays.

The m=0, L=3 star-like or line-like feature should be shown as an observation. Its bandwidth/mosaic interpretation remains a CHECK until the measured spectrum and full vector calculation reproduce the feature and a controlled reflection/optics comparison isolates the mechanism.

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
- weighted source-state quadrature details;
- beam position, divergence, and wavelength-state construction;
- continuous mosaic-density evaluation and analytic Ewald restriction;
- computational efficiency/optimization arguments;
- full profile arrays or large peak-by-peak fit collections;
- h-BN fitting procedure if part of the analysis pipeline;
- additional incident-angle data;
- full CIF/SIF contents if too long for main text;
- full propagated-error derivations.

### Proposed Supplement Outline

The standalone implementation outline has been merged into `2D_Supplemental/SI_failure_modes.tex` and deleted. The built SI is the only active supplement source; the statuses below distinguish written interfaces from missing executable or numerical evidence.

| Section | Status | Contents |
|---|---|---|
| S1 Geometric acceptance and detector mapping | DONE | Sample-plane acceptance, optional finite support, detector rigid transform, tilted-plane intersection, continuous pixel coordinates, active-area tests, and calculation order are written and implementation-checked. |
| S2 Crystallographic displacement conventions | DONE | Conventional structure-factor notation, isotropic U/B conversion, current CIF input scope, and shared uniaxial film-frame damping are documented. |
| S3 Wavelength sampling and moving Ewald construction | DONE | Weighted position/direction/wavelength states, moving center and radius, convergence checks, and the analytic Ewald restriction are documented. |
| S4 Staged workflow, projection, uncertainty, optics, and near-critical diagnostic | DONE | The finite detector observable, uncertainty propagation, continuous mosaic density, standard interface correction, and provisional direct-array limitation are documented. |
| S5 Transition-matrix derivation | IN PROGRESS | The symbolic PbI2 construction and deterministic checks are complete. Experimental transition-matrix refit values and a direct selected-rod comparison remain open. |
| S6 Two-component mosaicity checks | BLOCKED | Direct arrays are required for same-fit no-tail and re-optimized Gaussian-only comparisons with residuals, parameters, correlations, and uncertainty. |
| S7 Full ordered-film peak profiles | BLOCKED | Expanded direct-source Bi2Se3/Bi2Te3 profiles, residuals, scaling, and uncertainty require the missing arrays/scripts. |
| S8 h-BN fitting method | TODO | What was fit, what parameters were extracted, and why it belongs in the workflow. |

## Concision Guidance

Cut or move text that mainly explains software convenience, implementation bookkeeping, broad literature context, or parameter auditing before the fit evidence appears.

Keep text that helps a diffraction reader see:

1. what was measured;
2. what physical effect is modeled;
3. how measured and calculated intensities are compared;
4. what the current Bi2Se3/Bi2Te3 overlays support and which quantitative claims still require provenance, residuals, and uncertainty.

Highest-priority cuts before the next advisor draft:

1. Compress the introduction's material-family survey.
2. Shorten the post-Fig. 1 orientational-limits paragraph.
3. Reduce workflow prose because the table already carries the staged refinement.
4. Move or shrink the ordered structure-parameter table.
5. Convert future-tense results text into direct result language once figures are final.
6. Keep PbI2 from competing with the ordered-film evidence story.
7. Remove final-discussion meta-comments about how the paper should be organized.
8. Add the controlled broad-component comparisons required by C18 instead of compensating with more prose.

## Decision Log

| Date | Decision / change | Current interpretation |
|---|---|---|
| 2026-08-06 | Implemented the immediately resolvable current advisor comments and completed an independent implementation-parity audit. | The main text now teaches the physical sequence, balances sample and detector geometry, uses conventional crystallographic notation, defines the matched finite profile observable, splits the ordered-film figure for readability, and treats optics as a standard SI correction. The 003/006 mechanism, controlled mosaic ablation, ordered-figure provenance, and direct reflectivity result remain evidence gates. |
| 2026-07-30 | Added a dependency-only Overleaf export with persistent graphics caching. | `scripts/export-overleaf.ps1` packages both document entry points, losslessly wraps all referenced raster assets as PDFs, pre-renders live TikZ figures with overflow-safe bounds, removes unused staged graphics packages, compile-checks the main manuscript and SI, and creates `build_overleaf/overleaf.zip`. Git metadata, scripts, existing review PDFs, unreferenced assets, and LaTeX auxiliaries are excluded. The generated package preserved the 27-page main layout in rendered comparison; a clean local check completed in 9.11 s for the main manuscript and 8.19 s for the SI. |
| 2026-07-19 | Addressed all three author annotations in `main_advisor_comment_color_proof.pdf`. | Restored the earlier eight-panel Fig. 1 design and curated 3D/2D reciprocal panels, removed the reintroduced panel (c), retained the C02 diffraction-selection explanation, and removed prose semicolons and em dashes throughout the main manuscript and SI. Mathematical semicolon separators and source-only TeX syntax remain. The desired reciprocal assets were introduced as curated binaries in `9bb1c9b` and losslessly re-encoded in `bfb7869`. No historical generator reproduces them, so the misleading redraw script was removed. Both PDFs build, and revised Fig. 1 passed rendered review. |
| 2026-07-19 | Restyled paragraph-level headings as unnumbered blocks in the main manuscript and SI. | The shared preamble treatment is available to the main-text physical-foundation material and the SI. The four existing SI optical-interface subheadings retain semantic `\paragraph` hierarchy but appear on their own lines with book-like vertical spacing; numbering remains limited through `\subsubsection`. |
| 2026-07-18 | Completed the manuscript-resolvable advisor-correction pass. | C01--C04, C09, C12--C15, C17, C19, C21, and C22 are DONE; C05--C08 and C10 remain IN PROGRESS for executable/configuration parity; C11, C16, C18, and C20 are BLOCKED on specified missing inputs. Main/SI notation, Ewald/optical interfaces, causal ordering, workflow placement, and evidence boundaries are reconciled and verified by final builds, static scans, and rendered-page review. |
| 2026-07-18 | Resolved advisor comment C04 at its literal scope. | Defined \(\mathbf k_i\), \(\mathbf k_f\), \(\mathbf Q\), and \(\mathbf G\) immediately before use and numbered/cross-referenced the four associated diffraction equations. C04 itself introduced no frame superscripts or rotation-matrix rewrite; separate geometry-interface work for C05--C08, C10, and C11 supplies the broader SI treatment. The final build and rendered Methods page passed. |
| 2026-07-18 | Rewrote the C03 accomplishment and roadmap close. | Replaced the single capability-heavy paragraph with a prior-art transition, an evidence-bounded accomplishment paragraph, and a roadmap matching the final manuscript order. The ordered Bi2Se3/Bi2Te3 result was bounded to selected detector-feature locations and apparent profile line shapes rather than quantitative or predictive validation. PbI2 appears only as a separate extension. C03 is DONE after the C22 order and evidence boundary were reconciled and the main PDF rebuilt. |
| 2026-07-18 | Resolved advisor comment C01. | Replaced the WAXS-first opening with a 115-word layered-film-first paragraph, defined the 2D-powder state operationally, made substrate/growth dependence explicit, removed the material-family catalogue, and moved the orientational-limits comparison ahead of the PbI2 overview. The guarded build succeeded and rendered pages 1-3 passed visual review. |
| 2026-07-18 | Audited the 22-comment Miceli packet and integrated the writing philosophy into `AGENTS.md`. | All comments are traceable here. Ten packet responses are accepted, ten require modification, and two proposed implementations are rejected/replaced while retaining the advisor's underlying concern. Critical physics/provenance checks now precede prose polish; at the time of this initial audit, no manuscript comment was fully closed. |
| 2026-06-29 | Added Smilgies/Li indexGIXS citation and narrowed detector-space framing. | Smilgies and Li are now cited as prior art for calculating/overlaying grazing-incidence diffraction-spot positions directly in detector space. The manuscript contribution is framed as detector-space intensity/profile forward modeling after the geometric indexing step, not as novelty in detector-space indexing itself. |
| 2026-06-25 | Pruned generated figure diagnostics. | Removed 76 unreferenced generated PbI2 assets: misplaced ordered-folder outputs, parent-level generated exports, and low/medium/high `profiles/` diagnostics. Active manuscript and supplement figure paths remain the source contract for retained assets. |
| 2026-06-25 | Integrated annotated-PDF changes. | Historical state, superseded 2026-07-18: the digitized near-critical overlay was removed from the main text because it lacked the complete prediction and direct arrays. The observation remains separated from mosaic evidence; any future quantitative near-critical result requires direct exports and a declared mosaic treatment. |
| 2026-06-25 | Consolidated legacy manuscript tracking. | Advisor notes, meeting-prep notes, figure status, supplement status, changelogs, TODO tracking, old patch handoffs, and temporary review artifacts are subsumed here or removed. Git history remains the archive for exact old wording. |
| 2026-06-23 | Replaced superseded PbI2 scalar slip/flip model. | PbI2 now uses a six-state direction-resolved transition-matrix model. Numerical epsilon_j and population weights remain pending a refit and must not be converted from old scalar p values. |
| 2026-06-23 | Replaced PbI2 parent-stack Figure 11. | The projected 2H/4H/6H atomic-stack schematic is integrated with rF_sigma notation and a teaching caption. |
| 2026-06-23 | Updated PbI2 intensity equations. | Main text uses parent probability 1-epsilon_j and alternatives epsilon_j/4, includes finite-stack self-plus-pair intensity, and keeps the full derivation in SI. |
| 2026-06-15 | Fixed clean-build BibTeX failure. | Clean builds should regenerate bibliography from tracked sources; watcher processes must be stopped manually before guarded rebuilds. |
| 2026-06-15 | Added GitHub Actions LaTeX build check. | CI checks root `main.pdf`, `build/main.aux`, and non-empty `build/main.bbl` with bibliography markers. |
| 2026-06-11 | Removed legacy build products and patch handoffs. | Active manuscript sources, current figure assets, bibliography source, `main.pdf`, and `2D_Supplemental/SI_failure_modes.pdf` are retained review artifacts. |
| 2026-05-22 | Added bandwidth-scaling and uncertainty material. | Superseded 2026-07-18: the fixed-center inverse-order argument was removed. Main text and SI now rebuild the Ewald center and radius for every wavelength/direction sample; the low-\(L\) mechanism remains unassigned pending direct simulation. Projection/intensity uncertainty formulas are retained. |
| 2026-05-12 | Advisor-feedback restructure. | Low-L observation remains before the ordered test cases; correlated effects remain separate; PbI2 remains an extension. Superseded placement: the workflow now follows the ordered test cases directly and precedes PbI2. |
| 2026-05-10 | Moved low-L m=0 star feature before ordered-film validation. | Observation now precedes the fit-quality payoff. |
| 2026-04-30 | Advisor meeting. | Paper first, ordered Bi2Se3/Bi2Te3 figures first, direct Q_z overlays, supplement for implementation, PbI2 parked/subordinate. |
| 2026-04-30 | Added preliminary literature-bounded parameter citations. | Fitted structural values remain provisional and must be checked against final refinement output before submission. |
| 2026-04-26 | Cleaned language and fit layout. | Historical state, superseded 2026-07-18: the selected-rod polar angle formerly used eta; active SI now uses \(\vartheta_Q\), and unrelated phase symbols use distinct notation. |
| 2026-04-21 | Added Nookiin related-work citation. | Nookiin is complementary atomistic/supercell context, not a workflow dependency or software used by the present model. |
| 2026-03-13 | Pedagogical diffraction-model rewrite. | The model builds from ideal scattering geometry to experimental complications and weights. |
| 2026-03-03/04 | Advisor-annotation passes. | Section structure, notation, figure plumbing, beam/sample components, and supporting information were updated; detailed line-by-line history remains in git. |

## Current Change Status

| Area | Status | Notes |
|---|---|---|
| Feature | DONE | Implemented the immediately resolvable 2026-08-06 advisor comments across the main text and SI. The model narrative now follows incident state to sample acceptance, Ewald restriction, exit propagation, tilted-detector mapping, and matched finite integration. |
| Bug/error | DONE | Corrected the source-state versus mosaic treatment, conventionalized displacement notation, removed the unnecessary family-set equation, eliminated optics and detector-response overclaims, and bounded the 003/006 and reflectivity interpretations. |
| Build/QA | DONE | Main and SI PDFs rebuild without undefined references, undefined citations, overfull boxes, or clipped content. Rendered pages were reviewed after the edit. |
| Figure revision | DONE | The ordered-film composite is split into material-specific pages with larger panels, descriptive headings, and captions that define the profile construction and claim boundary. Direct-array provenance remains a separate evidence task. |
| Documentation | DONE | This canonical file records A01--A12, the updated implementation-parity conclusions, and the remaining blocked evidence gates. No competing status document was created. |
| Shipping/rollback | DONE | No external release was published or pushed. The manuscript and SI review PDFs were rebuilt locally. |

## Build And Reset Recovery

The main manuscript uses `latexmkrc` to write the public artifact to repository-root `main.pdf`. Generated LaTeX auxiliaries, logs, and bibliography outputs go into `build/`, which is ignored by git.

For an Overleaf upload, generate the clean cached package from the repository root:

```powershell
.\scripts\export-overleaf.ps1
```

The script creates `build_overleaf/overleaf/` and `build_overleaf/overleaf.zip`. Upload the ZIP contents with `main.tex` at the Overleaf project root. The package contains only the dependency closure for `main.tex` and `2D_Supplemental/SI_failure_modes.tex`; referenced TikZ and raster graphics are losslessly cached as PDFs. Persistent source-hash caches under `build_overleaf/graphics-cache/` make later exports rebuild only changed graphics. The default command compile-checks both entry points before creating the ZIP. Use `-SkipCompileCheck` only when a faster package-only refresh is intentional.

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
- Does it state only the currently supported fitted-condition location/apparent-line-shape result and identify what is still required for quantitative or refinement-quality claims?
- Does it introduce the two-component mosaicity hypothesis early without calling the broad component necessary before the C18 controls exist?
- Does it label reflections in a way a diffraction reader can understand?
- Does the caption teach the reader what to notice?
- Does it show data before explaining the model correction?
- Does it explain that wavelength sampling moves both the Ewald-sphere center and radius, without using a universal inverse-order or cap-overlap rule?
- Does it avoid overclaiming that Gaussian/Lorentzian forms are uniquely true?
- Does it separate the m=0, L=3 observation from its proposed mechanism and withhold validation language until direct tests exist?
- Are sample-orientation effects included in plotted trajectories, or is the limitation stated?
- Are Q_R, Q_z, L, m, and explicit (h,k,l) labels defined before use?
- Does main text discuss propagated/systematic error rather than hiding it entirely in SI?
- Does the manuscript distinguish the verified isotropic/shared-uniaxial structure-factor implementation from the still-unreported final fitted file and occupancy provenance?
- Is refinement-quality language withheld until source provenance, scaling, residual, and uncertainty evidence supports it?
- Are the Ewald vectors, reflection-family labels, multiplicity, angles, and specialized operations defined before use, with important equations numbered?
- Have vague qualifiers been replaced by a testable condition, value, range, or controlled comparison?
- Does narrative and caption prose avoid semicolons and em dashes while retaining semicolons that serve a mathematical or TeX-syntax role?
- If a component is called necessary, does an otherwise-identical ablation with residuals or a documented reason for not running one support that claim?
- Does `main.tex` place ordered-film test cases before the refinement workflow and PbI2 extension?
- Does every current A01-A12 item and each still-active older evidence gate have an exact change location, verification evidence, and honest status?

## Document Policy

Do not recreate separate advisor-note, meeting-prep, figure-status, supplement-status, input-inventory, TODO, or changelog documents unless explicitly requested. Add new manuscript guidance, active status, open questions, and durable decision summaries here instead.
