# Oriented-powder presentation and asset library

Open **[index.html](index.html)** to browse the figures, play the animations, and find the exact assets used on each slide. It works offline: no account, web service, server, or package installation is needed. After downloading the ZIP, extract the whole folder before opening the gallery.

The current archived presentation is **[Oriented_Powder_8min_Animated_v9.pptx](releases/2026-09-10_v9/presentation/Oriented_Powder_8min_Animated_v9.pptx)**. This is the most recent edited deck, preserved byte-for-byte. It has 25 visible slides, no hidden slides, seven embedded movies, eight editable chart/workbook pairs, and one native parameter table. The historical filename is retained; this expanded deck has not been retimed to eight minutes. Live PowerPoint playback has not been verified.

Deck SHA-256: `0feca65d8e57c764666012cc75cd880da660fd1fea12eedba0cec69193c2cec3`.

## Find and reuse an asset

- **In this deck** shows the current slide selections. The exact embedded movie takes precedence over a similarly named standalone export.
- **Animations / Figures** include the other archived versions. Each family explains what it demonstrates, where to use it, and the scientific limits of the illustration or fit.
- **Slide pages** preserves the layout and speaker notes for all 25 slides. PNG previews are static; movies and click reveals remain in the PPT.
- **Versions & sources** links to exports, direct data, generators and provenance. The [catalog](catalog.json) is also readable by future scripts and assistants.

Use the MP4 for presentation playback and its PNG still as a fallback. Retain the original PNG and any existing SVG for figures. Use the preserved data when changing a scientific plot; do not digitize its image. The [plain-text asset guide](ASSET_GUIDE.md) remains useful without the gallery.

## What is preserved

| Location | Contents |
|---|---|
| `releases/2026-09-10_v9/presentation/` | Exact final v9 PPT. |
| `releases/2026-09-10_v9/slides/` | All 25 verified slide renders and UTF-8 speaker notes. |
| `releases/2026-09-10_v9/assets/` | Public MP4/GIF/PNG/SVG exports, current scientific panels, and exact media extracted from the PPT. |
| `releases/2026-09-10_v9/data/` | Original chart XML and embedded XLSX files, CSV worksheet values, native table CSV, and a chart-to-slide index. |
| `releases/2026-09-10_v9/source/` | Generators, configurations, model source snapshots, compact direct plot arrays, CSV alternatives, dictionaries, and runtime records. |
| `releases/2026-09-10_v9/source/original_presentation/` | The exact user-edited Downloads v8 used to build v9. The same-named project v8 was a different file. |
| `releases/2026-09-10_v9/provenance/` | Source-path and checksum mapping, fit/figure provenance, and verification receipts. |
| `tools/` | Gallery/catalog builders, portable rebuild adapters, and standard-library integrity tools. |

CSV numerical exports retain 17 significant digits where converted from floating-point arrays. NPZ/NPY data preserve the original array shapes and binary values. The original XLSX files remain authoritative for native chart formulas and formatting; CSV files are a portable view of stored worksheet values.

## Scientific meaning and one inherited label discrepancy

“In this deck” means selected for this presentation. It does not certify a uniquely determined or globally best structural fit. The Bi₂Se₃ profile panels use the retained September 3 mosaic state with compatible September 5 optics. Bi₂Te₃ uses the later conditional spatial-integration comparison. The stages differ; the figure grammar is parallel. The axial panels retain the low-angle reflectivity. Existing residual mismatches and the absence of Se uncertainty estimates remain documented in the source records.

The saved deck's **slide 7 says “50% Lorentzian,” but its embedded r = 0, 1, 3 incidence movie uses 25%**. The matching media hash and source configuration verify this discrepancy. This archive preserves the deck exactly and records the issue for a future edited release.

Schematic mosaic, Ewald, incidence and PbI₂ animations illustrate mechanisms. Their teaching parameters are not fitted sample results. Termination-mixture comparisons are conditional model comparisons; they do not establish unique termination identification or a blanket limitation of all other techniques.

## Rebuild without the original computer

Viewing and reuse need only the extracted library. Replotting needs the runtimes listed in the source runtime records. The adapters resolve archived paths and write to a **new directory**, preserving the release.

From a terminal in this library folder:

```text
python tools/verify_library.py
python tools/rebuild_animation.py --list
python tools/rebuild_animation.py rotation --output ../rebuilt-rotation
python releases/2026-09-10_v9/source/rebuild/replot_profiles.py --material se --output ../rebuilt-se
python releases/2026-09-10_v9/source/rebuild/replot_profiles.py --material te --output ../rebuilt-te
```

The animation adapter needs Python 3.10+, Node.js, `sharp`, and FFmpeg with H.264 support. The incidence recipe also uses `@napi-rs/canvas`. Run `--help` for explicit executable and package-location overrides. It does not silently download dependencies. Use Matplotlib 3.10.3 for the original Se rendering and 3.11.1 for Te; source runtime files record the other installed versions. Rendering can vary across operating systems, fonts and encoder versions even when numerical inputs are identical.

Verified in this release: a complete 252-frame rotation rebuild matched the MP4, GIF and PNG bytes; the other 13 animation recipes generated proof frames successfully. Of 124 historical proof images, 116 matched exactly. The eight differences belong to the older axial-incidence animation, whose current lattice helper has changed. Its original movie is preserved; the runner labels the new rendering as an alternative. All four Se profile PNGs and the full Te source figure plus five Te crops reproduced pixel-for-pixel.

Replotting stored results is different from refitting or recomputing the full Monte Carlo simulation. The compact Te export retains the arrays required for these plots instead of copying the original 5.97 GB integration bank. Full simulation/refitting has not been verified as a portable one-command rebuild. Original generator snapshots retain historical paths for provenance; use the supplied adapters for the verified operations. The source manifest lists omitted large intermediates and any unresolved inputs explicitly.

## Keep it useful over time

1. Treat `releases/2026-09-10_v9/` as immutable. Copy an asset or PPT out before editing it.
2. Give the next release a new date/version directory. Save the new export, exact source/configuration and direct data together. Record its purpose, predecessor, scientific status and slide use in the catalog. Avoid overwriting a file called “final.”
3. Keep old releases and their checksums. Update the top-level catalog/gallery to select the new release; the old ZIP remains an exact snapshot of the earlier catalog and files.
4. Track small source files, recipes and catalog metadata in Git. The local `.gitignore` excludes large binary payloads; those remain in this folder and in the archival ZIP. No commit, remote push, or Git LFS setup was performed by creating this library.
5. Keep a copy of the checked ZIP and its `.sha256` file on a second storage device or independent backup service. This folder is under Nextcloud, but synchronization or an offsite backup has not been verified.

`SHA256SUMS.txt` detects changes to every listed file. `FILES.json` gives sizes and hashes. The ZIP's separate checksum anchors the whole snapshot, including these manifests. Verify again after copying or extracting the archive.

The manuscript's ongoing scientific decisions and status remain in the project-root `MANUSCRIPT_STATUS.md`. Its copy inside this release is historical context, not a competing status document.
