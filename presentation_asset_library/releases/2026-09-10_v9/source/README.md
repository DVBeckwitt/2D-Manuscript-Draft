# Source archive for the preserved v9 deck

This snapshot preserves source files and selected scientific inputs independently of Downloads, temporary builds and chat history. `../provenance/source_snapshot.json` maps each copied original path to its archived relative path and SHA-256. Originals are unchanged; the release PowerPoint is the delivery master.

## Recreate the Se and Te profile figures

Use separate Python environments because the two original figures used different Matplotlib versions. Python 3.12.2 was used for verification. Open a terminal in this source folder. The examples create environments and results outside the immutable release; substitute another external working directory if needed.

Windows PowerShell:

```powershell
$archiveSource = (Get-Location).Path
python -m venv C:/work/oriented-powder-se-env
& C:/work/oriented-powder-se-env/Scripts/python.exe -m pip install -r "$archiveSource/rebuild/requirements-se.txt"
& C:/work/oriented-powder-se-env/Scripts/python.exe "$archiveSource/rebuild/replot_profiles.py" --material se --output C:/work/oriented-powder-se-replot

python -m venv C:/work/oriented-powder-te-env
& C:/work/oriented-powder-te-env/Scripts/python.exe -m pip install -r "$archiveSource/rebuild/requirements-te.txt"
& C:/work/oriented-powder-te-env/Scripts/python.exe "$archiveSource/rebuild/replot_profiles.py" --material te --output C:/work/oriented-powder-te-replot
```

macOS/Linux:

```bash
archive_source="$PWD"
python3 -m venv /tmp/oriented-powder-se-env
/tmp/oriented-powder-se-env/bin/python -m pip install -r "$archive_source/rebuild/requirements-se.txt"
/tmp/oriented-powder-se-env/bin/python "$archive_source/rebuild/replot_profiles.py" --material se --output /tmp/oriented-powder-se-replot

python3 -m venv /tmp/oriented-powder-te-env
/tmp/oriented-powder-te-env/bin/python -m pip install -r "$archive_source/rebuild/requirements-te.txt"
/tmp/oriented-powder-te-env/bin/python "$archive_source/rebuild/replot_profiles.py" --material te --output /tmp/oriented-powder-te-replot
```

The package versions are recorded, while byte-identical verification was performed on Windows; other platforms may render fonts differently. The helper only changes data-loading locations; original generators are preserved. It verifies the rebuilt plots against archived PNG pixels and writes a report. With the recorded runtime, all four Se images and the full Te figure plus five Te crops reproduce pixel-for-pixel. Different renderer/font versions may change typography without changing numeric data. See `rebuild/verified_*_replot.json`.

`direct_data/` contains round-trip-precision CSV, JSON dictionaries and compact Te NPZ arrays. Se exact arrays remain at `workspace/build_codex/slate_talk/animated_deck_v9/figures/se_retained/bi2se3_retained_profiles_direct.npz`. The CSVs retain negative values, valid masks and unavailable values; Se has no invented uncertainty bars. Every CSV numeric field was verified against direct arrays.

## What the snapshot preserves

- `workspace/build_codex/slate_talk/`: original animation, diagram, chart and presentation generators; geometry helpers; profile grids; manifests; final detector arrays and Monte Carlo/axial intermediates.
- `original_presentation/User_edited_v8_source.pptx`: exact uploaded source of final v9, SHA-256 `03f7c853bc92153c675364db5a4f9aa055c5c488a8b17a9d6cf98614ae4e8136`. This is a historical editing input, not the delivery PPT.
- `external/`: exact bounded dependencies, structure CIFs, selected fit records, optical archives and original figure images.
- `engines/`: checked-out scientific Python source and package/license metadata. These are source snapshots, not an installed or validated standalone simulation environment.
- `fonts/`: original profile fonts with license files.
- `context/`: project guidance at archive time. The root project MANUSCRIPT_STATUS.md remains canonical for ongoing decisions.

The source snapshot includes generators from multiple historical versions so sources of retained alternatives are not lost. Final selection is defined by the release catalog and exact deck media, not by filenames in this source folder.

## Animation replay

From the library root, `python tools/rebuild_animation.py --list` lists archived recipes. The runner copies source to a fresh scratch directory and does not change this release. See its help for Node, FFmpeg and installed package paths. Current incidence-axial recipe is labeled an alternative where later helper changes prevent exact historical frame reproduction.

## Reproducibility boundaries

Viewing the release and replaying the supplied profile plots do not need the original machine. Complete refitting or simulation from raw detector measurements has not been independently rebuilt from this release. Original scripts retain historical absolute paths; relocation is only verified for dedicated adapters.

The 5.97 GB mutable Te integration bank is not copied wholesale. The exact arrays needed by the displayed figure, its full-source SHA-256, its embedded original figure generator, and extracted coordinates are preserved in a compact package; successful pixel-identical replay validates the extraction. Larger historical termination/optical intermediate banks and Python-object packets are listed as omitted in the manifest. The direct displayed termination CSVs and detector comparison arrays are preserved.

The Se and Te panels describe different retained analysis stages, not two newly accepted optimum refinements. Se retains the visible 006 mismatch and unavailable uncertainty estimates. Te retains conditional beam-position integration, remaining residuals, and count-plus-background uncertainty scales. Final Te detector rendering meets presentation-resolution color stability but retains five stricter local count checks. Schematic animation parameters and illustrative polytype fractions must not be reported as fitted measurements.

`archive_creation_*.py` documents how this archive was assembled and how compact arrays were extracted. Those creation scripts depend on original locations and are not the portable replay command. No runtime binaries, virtual environments or full integration-bank dependency closure are bundled.
