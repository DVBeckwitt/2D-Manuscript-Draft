#!/usr/bin/env python3
"""Rebuild a schematic animation in a new directory from an archived source snapshot.

Python 3.10+ (standard library), Node.js, sharp and FFmpeg with libx264 are needed.
The incidence-angular recipe also uses @napi-rs/canvas. No packages are downloaded.
Use --list for recipes, or --help for runtime overrides. Sources and original
exports are never edited. Rebuilt media are not promised to be byte-identical:
fonts, rasterizer and encoder versions can change pixels and encoded bytes.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

BASE = "build_codex/slate_talk/"
MEDIA = "output/presentations/animations/"
DEFAULT_RELEASE = "2026-09-10_v9"


def recipe(script, stem, seconds, size=(1600, 900), args=(), inputs=(), proof=True):
    return dict(script=BASE + script, stem=stem, duration_seconds=seconds,
                size=list(size), fps=30, args=list(args), inputs=list(inputs),
                proof_supported=proof)


DETECTOR_INPUTS = [BASE + "ewald_mosaic_clean_end/final.svg",
                   MEDIA + "ewald_intersections_then_mosaic_clean_end_still.png"]
LABELED_INPUT = BASE + "ewald_detector_labeled_animation/manifest.json"
Q_INPUTS = [MEDIA + "ewald_traces_to_detector_still.png",
            MEDIA + "ewald_traces_to_detector_labeled_still.png", LABELED_INPUT]
DISORDER_INPUTS = [MEDIA + "detector_to_qz_qr_labeled_still.png",
                   BASE + "detector_q_labeled_animation/final.svg",
                   BASE + "pbi2_disorder_animation/profile_grid.json",
                   BASE + "pbi2_disorder_animation/mosaic_kernel.json",
                   BASE + "pbi2_disorder_animation/mosaic_kernel.bin"]
MIXTURE_INPUTS = [MEDIA + "pbi2_general_stacking_disorder_still.png",
                  BASE + "pbi2_disorder_animation/final.svg",
                  *DISORDER_INPUTS[2:],
                  BASE + "pbi2_polytype_mixture_animation/profile_grid.json"]
MATRIX_INPUTS = [*DISORDER_INPUTS, BASE + "pbi2_disorder_animation/final.svg",
                 BASE + "pbi2_polytype_mixture_animation/profile_grid.json",
                 BASE + "pbi2_polytype_mixture_animation/final.svg"]

RECIPES = {
    "rotation": recipe("animate_rotation.mjs", "sample_rotation_reciprocal_rings_indexed",
                       8.4, (1080, 1080), proof=False),
    "mosaic": recipe("animate_mosaic.mjs", "sample_mosaic_caps_and_bands", 12,
                     (1080, 1080), inputs=[MEDIA + "sample_rotation_reciprocal_rings_indexed_still.png"]),
    "crystallites": recipe("animate_ensemble_tilt_detail.mjs", "many_crystallites_clear_tilt", 17),
    "ewald": recipe("animate_ewald_mosaic.mjs", "ewald_intersections_then_mosaic_clean_end", 16),
    "detector": recipe("animate_ewald_detector.mjs", "ewald_traces_to_detector_labeled", 18,
                       args=["--labeled"], inputs=DETECTOR_INPUTS),
    "angular-coordinates": recipe("animate_detector_angles.mjs", "detector_to_phi_2theta_labeled",
                                  14.2, args=["--labeled"], inputs=[Q_INPUTS[1], LABELED_INPUT]),
    "reciprocal-coordinates": recipe("animate_detector_q.mjs", "detector_to_qz_qr_labeled", 14,
                                     args=["--labeled"], inputs=Q_INPUTS),
    "mosaic-tails": recipe("animate_lorentzian_mosaic.mjs", "lorentzian_mosaic_phi_2theta", 18,
                          inputs=[BASE + "detector_angles_animation/final.svg"]),
    "mosaic-tails-larger-c": recipe("animate_lorentzian_mosaic.mjs", "lorentzian_mosaic_phi_2theta_larger_c",
                                   18, args=["--c-scale=1.25"],
                                   inputs=[BASE + "detector_angles_animation/final.svg"]),
    "incidence-angular": recipe("animate_incidence_angular.mjs", "bi2se3_incidence_phi_2theta", 24),
    "incidence-axial": recipe("animate_incidence_mosaic.mjs", "bi2se3_incidence_sweep_00l", 24),
    "pbi2-disorder": recipe("animate_pbi2_disorder.mjs", "pbi2_general_stacking_disorder", 14,
                            inputs=DISORDER_INPUTS),
    "pbi2-mixture": recipe("animate_pbi2_polytype_mixture.mjs", "pbi2_disorder_to_polytype_mixture", 14,
                           inputs=MIXTURE_INPUTS),
    "pbi2-matrices": recipe("animate_pbi2_matrices.mjs", "pbi2_stacking_disorder_and_polytypes_matrices",
                            24, args=["--mode=combined"], inputs=MATRIX_INPUTS),
}
RECIPES["incidence-axial"]["historical_match_note"] = (
    "The archived current lattice helper has changed since this older axial-response export. "
    "Its eight proof frames render successfully but differ from historical proof frames. "
    "Use the preserved historical MP4 for the approved appearance; this recipe is a new render "
    "from current archived source, not reconstruction of that older export."
)


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest() if hasattr(hashlib, "file_digest") else hashlib.sha256(stream.read()).hexdigest()


def within(path, root):
    return path.resolve().is_relative_to(root.resolve())


def executable(value, label):
    found = shutil.which(value)
    if found:
        return str(Path(found).resolve())
    path = Path(value).expanduser()
    if path.is_file():
        return str(path.resolve())
    raise ValueError(f"{label} not found: {value}. Set --{label.lower()} to its installed executable.")


def run(command, **kwargs):
    return subprocess.run(command, check=True, text=True, encoding="utf-8", errors="replace", **kwargs)


def source_closure(workspace, script, seeds):
    """Follow relative static imports and copy explicitly declared generated inputs."""
    queue, found = [script, *seeds], set()
    while queue:
        relative = queue.pop()
        path = (workspace / relative).resolve()
        if not within(path, workspace):
            raise ValueError(f"Source dependency escapes the archive: {relative}")
        relative = path.relative_to(workspace).as_posix()
        if relative in found:
            continue
        if not path.is_file():
            raise ValueError(f"Missing archived source dependency: {relative}")
        found.add(relative)
        if path.suffix in {".mjs", ".js"}:
            for specifier in re.findall(r"\bfrom\s+['\"]([^'\"]+)['\"]", path.read_text(encoding="utf-8-sig")):
                if specifier.startswith("."):
                    queue.append((path.parent / specifier).relative_to(workspace).as_posix())
    return sorted(found)


def resolve_packages(node, node_modules, packages):
    # createRequire resolves each entry within its own installed dependency tree.
    anchor = Path(node_modules).expanduser().resolve() / "_archive_resolver.cjs"
    code = "const fs=require('node:fs'),p=require('node:path'),r=require('node:module').createRequire(process.argv[1]);const out={};for(const n of process.argv.slice(2))out[n]={entry:r.resolve(n),version:JSON.parse(fs.readFileSync(p.join(p.dirname(process.argv[1]),n,'package.json'),'utf8')).version,libraries:r(n).versions??null};console.log(JSON.stringify(out));"
    return json.loads(run([node, "-e", code, str(anchor), *packages], capture_output=True).stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("recipe", nargs="?", choices=sorted(RECIPES))
    parser.add_argument("--list", action="store_true", help="List recipes as JSON; no rendering or runtime needed")
    parser.add_argument("--release", type=Path, help="Release directory; defaults to releases/2026-09-10_v9 beside this tool")
    parser.add_argument("--output", type=Path, help="A new, empty directory outside the preserved release")
    parser.add_argument("--node", default="node", help="Node executable (default: node on PATH)")
    parser.add_argument("--ffmpeg", default="ffmpeg", help="FFmpeg executable (default: ffmpeg on PATH)")
    parser.add_argument("--ffprobe", help="Optional ffprobe executable; otherwise locate beside FFmpeg or on PATH")
    parser.add_argument("--node-modules", type=Path, default=Path.cwd() / "node_modules", help="Installed node_modules containing sharp (and canvas for incidence-angular)")
    parser.add_argument("--proof-only", action="store_true", help="Run generator's proof frames only, if supported; no video")
    args = parser.parse_args()
    if args.list:
        print(json.dumps({"scope": "Current archived generators; historical exports and edited PPT clips remain authoritative. Full rotation render and proof frames for all other recipes were validated at archive creation; review visuals after rebuilding on a new runtime.", "recipes": RECIPES}, indent=2))
        return
    if args.recipe is None or args.output is None:
        parser.error("Specify a recipe and --output, or use --list.")
    selected = RECIPES[args.recipe]
    if args.proof_only and not selected["proof_supported"]:
        parser.error("This generator has no proof-only mode; rotation renders its complete 8.4 seconds.")
    release = (args.release or Path(__file__).resolve().parents[1] / "releases" / DEFAULT_RELEASE).resolve()
    workspace = release / "source/workspace"
    output = args.output.expanduser().resolve()
    if within(output, release) or within(release, output):
        raise ValueError("--output must be outside the preserved release and cannot contain that release.")
    if output.exists() and (not output.is_dir() or any(output.iterdir())):
        raise ValueError("--output must be a new or empty directory; existing renders are never overwritten.")
    dependencies = source_closure(workspace, selected["script"], selected["inputs"])
    external_dependencies = []
    if BASE + "bi2se3_animation_lattice.mjs" in dependencies:
        for relative in ["configs/bi2se3_simulation.yaml", "examples/bi2se3/structures/Bi2Se3_vesta.cif"]:
            archived = release / "source/engines/SLATE-rMC" / relative
            if not archived.is_file():
                raise ValueError(f"Missing archived lattice dependency: {archived.relative_to(release)}")
            external_dependencies.append((archived, Path("SLATE-rMC") / relative))
    node, ffmpeg = executable(args.node, "node"), executable(args.ffmpeg, "ffmpeg")
    packages = resolve_packages(node, args.node_modules, ["sharp", *(["@napi-rs/canvas"] if args.recipe == "incidence-angular" else [])])
    ffprobe = args.ffprobe or str(Path(ffmpeg).with_name("ffprobe" + Path(ffmpeg).suffix))
    ffprobe = executable(ffprobe if args.ffprobe or Path(ffprobe).is_file() else "ffprobe", "ffprobe") if not args.proof_only else None
    scratch = output / "scratch/workspace"
    scratch.mkdir(parents=True)
    report = dict(schema_version=1, recipe=args.recipe, recipe_definition=selected,
                  created_utc=datetime.now(timezone.utc).isoformat(), release=str(release),
                  runtime={"python": sys.version, "node": run([node, "--version"], capture_output=True).stdout.strip(),
                           "ffmpeg": run([ffmpeg, "-version"], capture_output=True).stdout.splitlines()[0], "packages": packages},
                  scope="Re-render from the current archived generator, not a byte-exact restoration of every historical variant or PPT edit. Uses archived predecessor frames and cached schematic grids where declared.",
                  inputs=[], scratch_substitutions=[], status="started")
    for source, relative in external_dependencies:
        # The original helper resolves ../../../SLATE-rMC from its module URL.
        # Preserve that sibling layout in scratch, including the YAML's CIF link.
        target = scratch.parent / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        report["inputs"].append({"path": source.relative_to(release).as_posix(),
                                 "staged_path": "scratch/" + relative.as_posix(), "sha256": digest(source)})
    for relative in dependencies:
        source, target = workspace / relative, scratch / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        record = {"path": relative, "sha256": digest(source)}
        report["inputs"].append(record)
        if target.suffix not in {".mjs", ".js"}:
            continue
        original = target.read_text(encoding="utf-8-sig")
        patched = original
        modifications = []
        for name, package in packages.items():
            pattern = r"(\bfrom\s+)(['\"])" + re.escape(name) + r"\2"
            patched, count = re.subn(pattern, lambda m: m.group(1) + json.dumps(Path(package["entry"]).as_uri()), patched)
            if count:
                modifications.append({"type": "installed_package_entry", "package": name, "occurrences": count})
        patched, count = re.subn(r"(['\"])C:/ffmpeg/bin/ffmpeg\.exe\1", lambda m: json.dumps(ffmpeg.replace("\\", "/")), patched)
        if count:
            modifications.append({"type": "ffmpeg_executable", "occurrences": count})
        if patched != original:
            target.write_text(patched, encoding="utf-8", newline="")
            report["scratch_substitutions"].append({"path": relative, "source_sha256": record["sha256"],
                                                      "scratch_sha256": digest(target), "changes": modifications})
    report_path = output / "rebuild_report.json"
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    command = [node, str(scratch / selected["script"]), *selected["args"], *(["--proof-only"] if args.proof_only else [])]
    print(f"Rebuilding {args.recipe}; exports and logs will be in {output}", flush=True)
    try:
        with (output / "render.log").open("w", encoding="utf-8") as log:
            run(command, cwd=scratch, stdout=log, stderr=subprocess.STDOUT)
        exports = output / "exports"
        exports.mkdir()
        report["exports"] = []
        for source in sorted((scratch / MEDIA).glob(selected["stem"] + "*")):
            if source.is_file():
                shutil.copy2(source, exports / source.name)
                report["exports"].append({"path": "exports/" + source.name, "sha256": digest(source)})
        report["proofs"] = []
        for source in sorted((scratch / BASE).rglob("*.png")):
            if source.name != "contact.png" and not source.name.startswith("frame_"):
                continue
            relative = source.relative_to(scratch / BASE)
            target = output / "proofs" / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            report["proofs"].append({"path": target.relative_to(output).as_posix(), "sha256": digest(source)})
        if not args.proof_only:
            video = exports / (selected["stem"] + ".mp4")
            probe = json.loads(run([ffprobe, "-v", "error", "-select_streams", "v:0", "-count_frames", "-show_entries", "stream=codec_name,width,height,avg_frame_rate,nb_read_frames,duration", "-of", "json", str(video)], capture_output=True).stdout)["streams"][0]
            expected_frames = round(selected["duration_seconds"] * selected["fps"])
            if [probe["width"], probe["height"]] != selected["size"] or int(probe["nb_read_frames"]) != expected_frames:
                raise ValueError(f"Unexpected rendered video dimensions or frame count: {probe}")
            report["video_validation"] = probe
        report["status"] = "complete"
    except Exception as exc:
        report["status"], report["error"] = "failed", str(exc)
        raise
    finally:
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Complete. Inspect {output / ('proofs' if args.proof_only else 'exports')} and {report_path}. Review rebuilt visuals before replacing an approved asset.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print(f"Rebuild failed: {error}", file=sys.stderr)
        if isinstance(error, subprocess.CalledProcessError) and error.stderr:
            print(error.stderr, file=sys.stderr)
        sys.exit(1)
