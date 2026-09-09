# Bragg rods to detector intensity - Overleaf project, round 16

Upload this ZIP directly to Overleaf and compile `main.tex` with pdfLaTeX.

## Revision

Figure 8(a) now uses a reconstructed relative-intensity coordinate with percentile clipping and a sub-linear contrast stretch. This exposes intensity differences across the detector-visible `00L` Ewald patch that were compressed by the previous RGB-based scale. The panel includes a relative display colorbar. This changes only the visualization; it does not introduce an additional physical normalization.

## Project structure

- `main.tex`: Overleaf entry point.
- `src/page13_round16.tex`: editable replacement page containing Figure 8.
- `figures/fig_specular_detector_visible_round16.pdf`: revised vector figure.
- `base/bragg_rods_comments_refined_round15.pdf`: unchanged pages imported by `pdfpages`.
- `assets/`: rendered detector and caked fields used to regenerate Figure 8.
- `scripts/generate_figure8.py`: optional local regeneration script. Overleaf does not run this Python script; the generated PDF is already included.

The prior document was produced through iterative page replacement, so the unchanged pages are retained as PDF pages while the revised Figure 8 page remains editable LaTeX.
