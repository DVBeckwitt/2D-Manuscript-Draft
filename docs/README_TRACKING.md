# Manuscript Tracking Files

These files were added to organize manuscript work after the 2026-04-30 advisor meeting.

## Files

- `AGENTS.md` — repo instructions for future agents or assistants.
- `MANUSCRIPT_STATUS.md` — main task tracker.
- `TODO.md` — short checklist entry point.
- `docs/meeting-notes/2026-04-30-maselli-meeting.md` — detailed meeting notes and action items.
- `docs/NEXT_MEETING_PREP.md` — checklist for the next advisor meeting.
- `docs/INPUT_INVENTORY.md` — record of source files and current repo structure.
- `figures/FIGURE_STATUS.md` — figure inventory and figure-specific tasks.
- `2D_Supplemental/SUPPLEMENT_STATUS.md` — supplement outline and supplement-specific tasks.
- `.github/ISSUE_TEMPLATE/manuscript_task.md` — GitHub issue template.
- `.github/PULL_REQUEST_TEMPLATE.md` — lightweight PR template.
- `.github/labels.md` — suggested labels for issues/projects.

Use `MANUSCRIPT_STATUS.md` as the single source of truth.

## Build and reset recovery

The main manuscript uses `latexmkrc` to write generated LaTeX files into
`build/`. That directory is intentionally ignored by git. A command such as
`git reset --hard` restores tracked source files, but it does not remove stale
ignored files in `build/` or stop an editor build watcher.

Use this guarded clean rebuild when citations or bibliography output look stale:

```powershell
.\scripts\build-main.ps1
```

If VimTeX or another editor watcher is already running, the script stops before
touching build state and prints the matching process IDs. Stop the watcher in
the editor or process manager, then rerun the script. The script intentionally
does not kill watcher processes because Windows process command lines do not
reliably prove which repository owns a generic `main.tex` watcher.

The underlying `latexmk` commands are:

```powershell
latexmk -C main.tex
latexmk -pdf -g -interaction=nonstopmode -file-line-error main.tex
```

After a successful build, `build/main.aux` should contain
`\bibstyle{apsrev4-2}` and `\bibdata{bibliography/references}`, and
`build/main.bbl` should be non-empty.

If VimTeX or another editor reports `I found no \bibdata command` after a
reset, first stop the continuous build watcher, then run the clean rebuild
above. On Windows, active watcher processes can be checked manually with:

```powershell
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -match 'latexmk|perl|pdflatex|bibtex|miktex' } |
  Select-Object ProcessId,Name,CommandLine
```

That BibTeX message usually means BibTeX read an incomplete or stale `.aux`
file. It does not by itself prove that `main.tex` is missing the bibliography
commands.

Status as of 2026-06-15: the reset/bibliography failure is fixed locally with a
guarded clean-build script, `latexmkrc` clean behavior, and a GitHub Actions
LaTeX build check. The local build produces `build/main.pdf`,
`build/main.aux`, and a non-empty `build/main.bbl` with the expected BibTeX
markers.
