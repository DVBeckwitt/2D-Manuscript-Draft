# AGENTS.md - Manuscript Guidance Entry Point

## Required context

Before any writing, rewriting, figure planning, caption drafting, structural editing, advisor-comment response, or manuscript-status work, read `MANUSCRIPT_STATUS.md` in full.

`MANUSCRIPT_STATUS.md` is the canonical source for Dr. Paul F. Miceli's manuscript guidance, current priorities, the audited 22-comment revision plan, figure and supplement status, open advisor questions, build notes, and revision checklist. Do not recreate separate advisor-note, response-plan, meeting-prep, figure-status, supplement-status, task-list, or changelog files unless explicitly requested. Put durable decisions and task status in `MANUSCRIPT_STATUS.md`.

## Advisor philosophy as operating rules

Apply these rules to every manuscript change:

These rules translate the advisor's philosophy. The implementation-specific verification and traceability requirements under “Handling advisor comments” are project audit standards, not quotations attributed to the advisor.

1. Build the argument in the order **observation -> physical inference -> model ingredient -> matched quantitative comparison -> conclusion**.
2. Keep the central proof ahead of extensions: ordered Bi2Se3/Bi2Te3 data and measured/calculated overlays first, refinement workflow next, and PbI2 only afterward. Paper first; software second.
3. Explain physics in the main text. Put coordinate bookkeeping, algorithms, optimization, lookup tables, caking/remapping details, and long derivations in the Supporting Information unless they are essential to the physical claim.
4. Let figures carry the claim. A caption must identify the material and condition, measured and calculated quantities, every line/symbol/band, the comparison procedure, what to notice, and the conclusion supported.
5. Define every symbol and specialized term before use, number important equations, use standard diffraction language, and distinguish a reflection-family label from its multiplicity.
6. Preserve causal order and use one principal operation or inference per sentence at conceptually difficult points.
7. Replace vague words with a condition, value, range, or direct comparison. When an argument hinges on a model component being necessary, use a controlled comparison and apply residual/uncertainty gates where the audit table requires them.
8. State accomplishments plainly but only at the strength justified by displayed overlays, uncertainty analysis, and the stated structural model.
9. Draft enough to make the logic teachable, then cut repetition and move implementation-heavy material to the Supporting Information.

## Handling advisor comments

- Preserve the advisor's intent, but do not rubber-stamp a proposed response. Use `AGREE`, `AGREE WITH MODIFICATION`, `DISAGREE`, or `CHECK`, with a reason and an acceptance criterion.
- Do not invent beam parameters, lattice constants, fitted values, detunings, uncertainties, model behavior, or code details. Verify them from the actual data/model or leave the item `CHECK`/blocked.
- Do not treat digitized, visually reconstructed, clipped, or placeholder curves as quantitative evidence. Use direct data/model array exports for fits, ablations, residuals, and validation claims; label reconstructed figures provisional.
- Mark a comment `DONE` only when the exact manuscript or SI location is recorded and the requested evidence has been verified. Related prose, a placeholder, or an intended figure is only `IN PROGRESS`.
- Keep all 22 packet comments traceable to the audit table in `MANUSCRIPT_STATUS.md`; no comment may be silently merged or dropped.

Keep manuscript work focused on the current priority in `MANUSCRIPT_STATUS.md`: a clear, figure-driven Bi2Se3/Bi2Te3 ordered-film story using diffraction-language labels and direct measured/calculated overlays. Software release polish, implementation detail, and PbI2 expansion remain secondary unless that file says otherwise.
