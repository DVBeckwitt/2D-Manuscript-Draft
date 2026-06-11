# Input Inventory

Last updated: 2026-06-11

## Uploaded or available context

| Item | Role |
|---|---|
| `Voice 260430_141619_llm.txt` | Transcript of meeting with Dr. Paul Maselli. Source for current priorities. |
| `2D-Manuscript-Draft.zip` | Manuscript repo archive. Used to identify current section structure and figure folders. |
| `Combined_variance_report_PbI2_Bi2Te3_Bi2Se3_updated.tex` | Existing technical/report material available for manuscript cross-checking. |

## Repo structure observed from archive

Current `main.tex` uses:

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

Observed figure folders include:

- `figures/intro/`
- `figures/mosaic/`
- `figures/results_ordered/`
- `figures/results_pbi2/`
- `figures/theory/`

Observed supplement folder:

- `2D_Supplemental/`

## Ordered-result figure status after revision

The earlier ordered-result PNGs were removed from the active package because they were placeholders or incomplete result summaries. The `figures/results_ordered/` folder now contains `README_needed_figures.md`, which specifies the real Bi2Se3 and Bi2Te3 detector-trajectory and Qz-overlay figures still needed.

## Cleanup status

The 2026-06-11 cleanup removed legacy laptop/server build products, dated `.bak-20260424-162800` snapshots, temporary page/SyncTeX artifacts, Windows shortcuts, and old patch handoff files. Active manuscript sections, current figure assets, bibliography source, `main.pdf`, and `2D_Supplemental/SI_failure_modes.pdf` remain the retained review package.

Build plumbing now uses standard BibTeX from `main.tex` via `\bibliography{bibliography/references}`. The former ignored `main.generated_bbl` handoff path has been removed.

## AGENTS.md status

A repo-level `AGENTS.md` is present in this package and should govern future manuscript edits.
