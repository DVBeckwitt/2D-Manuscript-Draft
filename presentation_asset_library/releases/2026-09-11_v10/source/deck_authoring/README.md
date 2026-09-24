# V10 presentation addition source

The exact final deck is the archival authority. To reuse the slide in PowerPoint, copy slide 19 from the v10 presentation. All earlier slides, notes, media, charts and embedded workbooks were retained byte-for-byte inside the new package. Only the presentation order/count metadata and new slide dependency parts were added.

These files preserve the authoring chain:

1. `build_slide.mjs` uses the bundled `@oai/artifact-tool` presentation API to make a single 16:9 slide with the cylinder animation's opening frame and speaker notes.
2. `bridge_slide.pptx` preserves that poster-only intermediate, so its exact layout does not depend on a future renderer.
3. `embed_videos.py` is the archived helper that adds the exact local movie with click-to-play timing and final-frame hold. `bridge_with_video.pptx` preserves this one-slide intermediate.
4. `insert_bridge.py` inserts the complete slide dependency closure at slide 19 of the immutable v9 deck. It preserves all prior slide content and asserts that only the four order/count/content-type package members change.
5. `finalize_deck.mjs` runs the bundled integrity/layout/import checks and copies the validated package to the final v10 path. The final deck SHA-256 is recorded in the catalog and verification receipts.

The JavaScript and Python snapshots retain the original workspace paths as execution provenance. They are not advertised as a portable one-command presentation rebuild. Re-running requires adjusting those paths and supplying a compatible ArtifactTool/runtime and its validation utilities; `insert_bridge.py` also requires `lxml` and FFprobe. The self-contained cylinder animation generator, pinned requirements, direct arrays and fonts are separately preserved under `../../assets/cylinder_bridge_v3/`.

The independent package and image comparison scripts, gallery browser test and their receipts document what was checked. The existing 25 slide renders match the preceding deck exactly. The new movie matches the sealed v3 MP4. Browser playback was checked; native PowerPoint application playback was not exercised.
