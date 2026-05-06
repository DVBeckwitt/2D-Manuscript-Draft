# Input Inventory

Last updated: 2026-04-30

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
\input{sections/refinement_workflow}
\input{sections/results_ordered}
% PbI2 diffuse-scattering results are deferred from the active draft.
% \input{sections/results_diffuse_pbi2}
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

## AGENTS.md status

A repo-level `AGENTS.md` is present in this package and should govern future manuscript edits.

