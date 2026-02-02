# Manuscript

This repository contains the LaTeX source and figure assets for the manuscript.

## Layout

- `manuscript/main.tex`: LaTeX entrypoint.
- `manuscript/sections/`: Section source files included by `main.tex`.
- `bibliography/references.bib`: BibTeX database.
- `figures/`: Figure assets organized by topic.

## Build

From the repository root:

```bash
cd manuscript
pdflatex main.tex
bibtex main
pdflatex main.tex
pdflatex main.tex
```

Adjust the bibliography tool if you use a different workflow.
