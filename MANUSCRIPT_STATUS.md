# Manuscript Status

Last updated: 2026-06-29

This is the canonical manuscript guidance and status document for the 2D diffraction / mosaicity manuscript. It subsumes the previous advisor notes, meeting-prep checklists, figure status, supplement status, changelogs, and manuscript task trackers. Use this file as the single source of truth for writing, rewriting, figure planning, caption drafting, structural editing, and manuscript triage.

Former detailed documents are intentionally not required for active work; git history remains the archive for exact old wording.

## Source Context

Primary meeting source: Dr. Paul Maselli / David manuscript discussion on 2026-04-30.

No next advisor meeting date is currently known. The earlier planned date, 2026-05-07, is past.

Current manuscript priority: Bi2Se3 and Bi2Te3 ordered-film figures and physics narrative.

Source context used during current revisions:

| Item | Role |
|---|---|
| `Voice 260430_141619_llm.txt` | Transcript/source notes from the 2026-04-30 Maselli meeting. |
| `2D-Manuscript-Draft.zip` | Manuscript repo archive used to identify current section and figure structure. |
| `Combined_variance_report_PbI2_Bi2Te3_Bi2Se3_updated.tex` | Technical/report material available for uncertainty and manuscript cross-checking. |

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
| `sections/introduction.tex` | IN PROGRESS | Should focus breadth around layered-film orientation and ordered-film validation. |
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
| Create Bi2Se3 detector/projection figure | IN PROGRESS | Main-text figure | Show measured data prominently with Q/Q_R/Q_z trajectories or integration regions. |
| Create Bi2Te3 detector/projection figure | IN PROGRESS | Main-text figure | Use the same logic and styling as Bi2Se3. |
| Add Bi2Se3 Q_z projection overlays | IN PROGRESS | Figure panels | Plot measured and calculated intensity versus Q_z. |
| Add Bi2Te3 Q_z projection overlays | IN PROGRESS | Figure panels | Plot measured and calculated intensity versus Q_z. |
| Define reflection-family labels | IN PROGRESS | Figure/caption convention | Initial m-indexed convention is present; final notation still needs advisor check. |
| Add early two-component mosaicity evidence | IN PROGRESS | Text + figure | Low-L m=0 evidence is inserted; a direct narrow-core versus Lorentzian-tail comparison may still be needed. |
| Write Q-space/projection caveat | DONE | Methods/results paragraph | Results state why projected Q_z is not an ideal perfect-crystal cut and why data/model comparison remains meaningful. |
| Add experimental incident-angle table | TODO | Methods or workflow table | List all collected angles, not just shown angles. |
| Replace remaining future-tense scaffold prose | TODO | Results prose | Convert "should show" language to result-forward statements once final figures are inserted. |

### P1 - Complete-Draft Support

| Task | Status | Deliverable | Notes |
|---|---|---|---|
| Write 2theta-phi/caked implementation supplement | TODO | Supplement section | Main text should not be driven by this. |
| Explain sub-pixelation/binning | TODO | Supplement section | Needed for pixel-sensitive detector transformations. |
| Explain Monte Carlo beam sampling | TODO | Supplement section | Include wavelength, beam position, and divergence. |
| Explain mosaic-event sampling | TODO | Supplement section | Describe optimized sampling and validation. |
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

- [ ] Bi2Se3 measured detector image with Q/Q_R/Q_z trajectory or integration-region annotation.
- [ ] Bi2Se3 measured/calculated Q_z projection overlays.
- [ ] Bi2Te3 measured detector image with Q/Q_R/Q_z trajectory or integration-region annotation.
- [ ] Bi2Te3 measured/calculated Q_z projection overlays.
- [x] Initial m or explicit (h,k,l) reflection-family label convention.
- [x] Paragraph explaining imperfect Q-space/projection interpretation.
- [x] Paragraph and figure concept for two-component mosaicity / Lorentzian-tail evidence.
- [ ] Table or list of all incident angles collected for Bi2Se3 and Bi2Te3.
- [ ] Supplement outline for 2theta-phi implementation, sub-pixelation, Monte Carlo sampling, and h-BN fitting.
- [ ] Direct mosaicity/Lorentzian-tail comparison panel if advisor wants stronger evidence.

## Advisor Questions

- Is the proposed reflection-family labeling convention clear enough?
- Which Bi2Se3/Bi2Te3 incident angles should be main-text figures versus supplement?
- Should Lorentzian-tail evidence be a standalone figure or part of the mosaicity figure?
- How many Q_z projection panels are enough for the main text?
- Is the inserted star-feature crop enough mosaic-tail evidence, or is a direct narrow-core versus Lorentzian-tail comparison required?

## Figure Guidance

Figures must show data. Do not obscure measured detector intensity with too many Bragg-position circles, colored paths, markers, or labels.

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
3. Low-L m=0 star-feature observation and bandwidth/mosaic-cap explanation.
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
| Documentation | DONE | This status file records the citation/framing decision, verification state, and release boundary. No separate advisor-note, changelog, or patch-handoff file was created. |
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

## Document Policy

Do not recreate separate advisor-note, meeting-prep, figure-status, supplement-status, input-inventory, TODO, or changelog documents unless explicitly requested. Add new manuscript guidance, active status, open questions, and durable decision summaries here instead.
