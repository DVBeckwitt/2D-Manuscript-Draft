# Manuscript Status

Last updated: 2026-05-10
Source meeting: Dr. Paul Maselli / David manuscript discussion, 2026-04-30  
Next advisor meeting: CHECK - 2026-05-07 date is now past; update when the next meeting is known
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

## Recent completed changes

| Date | Type | Status | Notes |
|---|---|---|---|
| 2026-05-10 | Feature | DONE | Moved the low-L m=0 star-feature crop and explanation before the ordered-film validation figure in `sections/results_ordered.tex`, so the observation now precedes the fit-quality payoff. |
| 2026-05-10 | Bug/error | DONE | Verified the figure-order check, rebuilt `main.pdf` with two `pdflatex -interaction=nonstopmode -halt-on-error main.tex` passes, and found no unresolved-reference warnings in `main.log`. |
| 2026-05-10 | CI/CD | CHECK | No GitHub Actions workflows are present in `.github/`; current quality gate is local LaTeX build plus log/reference scan. |
| 2026-05-10 | Deprecation/migration | DONE | Superseded the old validation-before-star ordering. No migration was needed because figure labels stayed stable: `fig:hk0_low_l_star` and `fig:ordered_chalcogenide_validation`. |
| 2026-05-10 | Shipping/rollback | DONE | Local release artifact is `main.pdf`; rollback is a normal git revert of the figure-order commit if the advisor wants the old sequence restored. |

## Current repo/manuscript state

| Item | Status | Notes |
|---|---|---|
| `main.tex` scaffold | DONE | Inputs the section files. |
| `sections/introduction.tex` | IN PROGRESS | Contains 2D-powder motivation and orientational-state framing. |
| `sections/modelling_methods.tex` | IN PROGRESS | Should keep the main narrative in Q/Qr/Qz/m language. |
| `sections/mosaicity_texture.tex` | IN PROGRESS | Needs earlier evidence for two-component mosaicity and Lorentzian tails. |
| `sections/refinement_workflow.tex` | IN PROGRESS | Should explain staged refinement without becoming an optimization narrative. |
| `sections/results_ordered.tex` | IN PROGRESS | Star-feature observation now appears before the ordered-film validation payoff; remaining work is advisor-facing figure readability and final polish. |
| `sections/results_diffuse_pbi2.tex` | PARKED | Existing material is useful, but PbI2 is not the current focus. |
| `sections/discussion_conclusion.tex` | IN PROGRESS | Revise after ordered-film results are clarified. |
| Intro schematic figures | IN PROGRESS | Existing assets are useful; check final clarity. |
| Ordered-film figures | IN PROGRESS | Current star-feature and validation assets are inserted; still need advisor review for readability and completeness. |
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
| Define reflection-family labels | IN PROGRESS | Figure/caption convention | Initial m-indexed convention is present; final notation still needs advisor check. |
| Add early two-component mosaicity evidence | IN PROGRESS | Text + figure | Low-L m=0 star feature now appears before validation; full narrow-core versus Lorentzian-tail evidence still needs a dedicated check/figure if required. |
| Write Q-space/projection caveat | DONE | Methods/results paragraph | Results section now states why the projected coordinate is not an ideal perfect-crystal reciprocal-space cut and why the data/model comparison remains meaningful. |
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
| Low-L m=0 star-feature ordering | Working | Ready for advisor review | Figure and discussion now precede the validation overlay; labels stayed stable and `main.pdf` builds. |

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
- [x] Initial m or explicit (h,k,l) reflection-family label convention.
- [x] Paragraph explaining imperfect Q-space/projection interpretation.
- [ ] Paragraph and figure concept for two-component mosaicity / Lorentzian-tail evidence.
- [ ] Table or list of all incident angles collected for Bi2Se3 and Bi2Te3.
- [ ] Supplement outline for 2theta-phi implementation, sub-pixelation, Monte Carlo sampling, and h-BN fitting.
