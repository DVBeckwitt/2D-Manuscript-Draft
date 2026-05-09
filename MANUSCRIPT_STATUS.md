# Manuscript Status

Last updated: 2026-04-30  
Source meeting: Dr. Paul Maselli / David manuscript discussion, 2026-04-30  
Next planned advisor meeting: 2026-05-07 at 2:00 PM, subject to rescheduling  
Current priority: Bi2Se3 and Bi2Te3 ordered-film figures and physics narrative

## Status definitions

| Status | Meaning |
|---|---|
| TODO | Not started or not yet placed into the manuscript. |
| IN PROGRESS | Work exists, but it is incomplete, not written up, or not manuscript-ready. |
| DONE | Incorporated into the manuscript or supplement in a form ready for advisor review. |
| PARKED | Important, but intentionally deferred. |
| CHECK | Needs advisor verification or a decision. |

## Current objective

The next draft should visibly demonstrate that the forward model quantitatively reproduces the measured area-detector diffraction line shapes for Bi2Te3 and Bi2Se3.

The manuscript needs measured detector images, Q/Qr/Qz trajectories or integration regions, extracted Qz projections, and measured/calculated overlays. The physics narrative should be in conventional diffraction language. Computational details should mostly move to the supplement.

## Current repo/manuscript state

| Item | Status | Notes |
|---|---|---|
| `main.tex` scaffold | DONE | Inputs the section files. |
| `sections/introduction.tex` | IN PROGRESS | Contains 2D-powder motivation and orientational-state framing. |
| `sections/modelling_methods.tex` | IN PROGRESS | Should keep the main narrative in Q/Qr/Qz/m language. |
| `sections/mosaicity_texture.tex` | IN PROGRESS | Needs earlier evidence for two-component mosaicity and Lorentzian tails. |
| `sections/refinement_workflow.tex` | IN PROGRESS | Should explain staged refinement without becoming an optimization narrative. |
| `sections/results_ordered.tex` | IN PROGRESS | Immediate target. Needs clear Bi2Se3/Bi2Te3 data/model result figures. |
| `sections/results_diffuse_pbi2.tex` | PARKED | Existing material is useful, but PbI2 is not the current focus. |
| `sections/discussion_conclusion.tex` | IN PROGRESS | Revise after ordered-film results are clarified. |
| Intro schematic figures | IN PROGRESS | Existing assets are useful; check final clarity. |
| Ordered-film figures | IN PROGRESS | Existing figure files are present, but advisor wants clearer projection evidence. |
| PbI2 figures | PARKED | Defer until ordered Bi2Se3/Bi2Te3 narrative is stable. |
| Software release polish | PARKED | Advisor said paper comes first. |

## Advisor-directed thesis of the next draft

> A physically constrained 2D-powder forward model, including detector geometry, beam/resolution effects, sample alignment, and two-component mosaicity, quantitatively reproduces the measured Bi2Te3 and Bi2Se3 area-detector line shapes and Qz-projected profiles.

## P0 tasks — next meeting

| Task | Status | Deliverable | Notes |
|---|---|---|---|
| Create Bi2Se3 detector/projection figure | TODO | Main-text figure | Show measured data prominently with Q/Qr/Qz trajectories or integration regions. |
| Create Bi2Te3 detector/projection figure | TODO | Main-text figure | Use the same logic as Bi2Se3. |
| Add Bi2Se3 Qz projection overlays | IN PROGRESS | Figure panels | Plot measured and calculated intensity vs Qz. |
| Add Bi2Te3 Qz projection overlays | IN PROGRESS | Figure panels | Plot measured and calculated intensity vs Qz. |
| Define reflection-family labels | TODO | Figure/caption convention | Prefer m or explicit (h,k,l) reflection-family labels over internal M labels. |
| Add early two-component mosaicity evidence | TODO | Text + figure | Show why a Lorentzian tail is necessary. |
| Write Q-space/projection caveat | TODO | Methods/results paragraph | Explain imperfect Q interpretation and why the model comparison remains valid. |
| Add experimental incident-angle table | TODO | Methods table | List all collected angles, not just shown angles. |

## P1 tasks — complete-draft support

| Task | Status | Deliverable | Notes |
|---|---|---|---|
| Write 2theta-phi/caked implementation supplement | TODO | Supplement section | Main text should not be driven by this. |
| Explain sub-pixelation/binning | TODO | Supplement section | Needed for pixel-sensitive detector/caked transformations. |
| Explain Monte Carlo beam sampling | TODO | Supplement section | Include wavelength, beam position, and divergence. |
| Explain mosaic-event sampling | TODO | Supplement section | Describe optimized sampling and validation. |
| Add h-BN fitting method | TODO | Supplement section | Unique workflow step mentioned in the paper. |
| Assemble all peak-profile checks | TODO | Supplement figure(s) | Good place for full measured/calculated profile panels. |

## P2 tasks — parked

| Task | Status | Reason |
|---|---|---|
| PbI2 diffuse scattering / stacking-fault section | PARKED | Advisor said to focus first on Bi2Se3 and Bi2Te3. |
| PbI2 selected-rod validation figures | PARKED | Keep available for later. |
| Software release cleanup | PARKED | Paper must demonstrate value before release polish matters. |
| Full software feature documentation | PARKED | Useful later, not central to the next draft. |

## Completed technically, but not manuscript-ready

| Item | Technical status | Manuscript status | Next step |
|---|---|---|---|
| Bi2Se3 model fits | Working | Not sufficiently shown | Insert data/model Qz projection figures. |
| Bi2Te3 model fits | Working | Not sufficiently shown | Insert data/model Qz projection figures. |
| Qz projection extraction | Working | Needs clearer presentation | Show trajectories/regions and plot extracted profiles vs Qz. |
| 2theta-phi/caked-space workflow | Working | Needs careful framing | Explain physics in Q/Qr/Qz language; implementation in supplement. |
| Monte Carlo optimization | Working | Supplement material | Write supplement explanation after main figures are in place. |
| Two-component mosaicity | Working | Needs early evidence | Add figure/text showing why Lorentzian tail is necessary. |
| h-BN fitting method | Working or near working | Needs supplement writeup | Explain because it is part of the workflow. |

## Figure-driven revision order

1. Insert rough Bi2Se3 and Bi2Te3 figures first.
2. Write captions that explain the data, calculation, trajectory, and conclusion.
3. Write the results text around the figures.
4. Add the two-component mosaicity evidence early.
5. Add the experimental incident-angle table.
6. Move implementation details into the supplement.
7. Revisit PbI2 after the ordered-film story is readable.

## Immediate checklist

- [ ] Bi2Se3 measured detector image with Q/Qr/Qz trajectory or integration-region annotation.
- [ ] Bi2Se3 measured/calculated Qz projection overlays.
- [ ] Bi2Te3 measured detector image with Q/Qr/Qz trajectory or integration-region annotation.
- [ ] Bi2Te3 measured/calculated Qz projection overlays.
- [ ] Proposed m or explicit (h,k,l) reflection-family label convention.
- [ ] Paragraph explaining imperfect Q-space/projection interpretation.
- [ ] Paragraph and figure concept for two-component mosaicity / Lorentzian-tail evidence.
- [ ] Table or list of all incident angles collected for Bi2Se3 and Bi2Te3.
- [ ] Supplement outline for 2theta-phi implementation, sub-pixelation, Monte Carlo sampling, and h-BN fitting.
