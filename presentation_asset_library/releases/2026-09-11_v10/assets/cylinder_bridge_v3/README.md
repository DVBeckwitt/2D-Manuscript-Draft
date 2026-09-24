# Cylinder bridge v3

This revision smooths the opening and accelerates the visible broadening toward the thinner end. Open `index.html` for the local preview. The unchanged static comparison and the revised animation are intended for the bridge after Bi2Se3/Bi2Te3 and before PbI2.

## What changed

The movie starts with a very thick finite stack, N=512, whose peaks appear delta-like at the displayed scale. The same curves broaden throughout the opening, removing the change from symbolic arrows to finite curves.

For smooth variation between integer thicknesses, the teaching model uses an incoherent population of two neighboring integer layer counts. If the mean is n=m+f, it combines fractions 1-f of m-layer stacks and f of (m+1)-layer stacks. Intensity is normalized by the mixed peak height. This is an explicit illustrative thickness-distribution assumption, not a literal fractional layer or a new material fit. At integer thicknesses it equals the exact finite-stack law, including the N=8 endpoint.

The animation holds the narrowest peaks for 1 second. From 1 to 6.8 seconds, inverse mean thickness follows a quadratic progression, so the visible widening speeds up without slowing at the end. It then holds N=8 until 8 seconds. This describes accelerating visible broadening rather than a constant or accelerating physical layer-removal rate. The cylinder, mosaic and Ewald stages retain their previous timing and geometry.

## Files

- `Cylinder_Bridge.mp4`: 26 seconds, 1600×900, 20 fps, H.264, no audio.
- `Cylinder_Bridge.pdf`, `.svg`, `.png`: byte-preserved static figure from v2; the ideal-delta reference remains useful in this side-by-side comparison.
- `storyboard/`: opening and later reference frames.
- `caption.txt`: figure caption and revised animation assumptions.
- `data/`, `source/`, `provenance/`: numerical inputs, portable generators and verification.

## Rebuild

Install the pinned requirements, with FFmpeg/libx264 available, and run:

```text
python source/cylinder_bridge.py
python source/animate_bridge.py --proofs --movie
python source/build_gallery.py
python source/verify_science.py
```

The movie generator renders the new opening and decodes the unchanged 8–26 second tail from the bundled, hash-verified `data/retained_v2_movie.mp4`. This keeps revision work fast and independent of the original project. Encoding introduces a further H.264 compression generation in the reused tail, with image differences checked in the included receipt. Use `--full-render` to regenerate every frame from the local geometry instead. No original-project files or network resources are required by either route. FFmpeg can be set through `FFMPEG_BIN` or discovered on PATH.

The v2 static figure is retained exactly; the current source also preserves its layout and model. The caption documents the updated animation. No new review PDF is included in this animation revision. Earlier review PDFs remain in their frozen releases.

`file_manifest.json` and `SHA256SUMS.txt` identify the delivered files. Preserve each version separately. `python source/seal_release.py` creates and verifies this version's ZIP when deliberately rebuilding the release. Scientific decisions remain in the project's canonical `MANUSCRIPT_STATUS.md`.
