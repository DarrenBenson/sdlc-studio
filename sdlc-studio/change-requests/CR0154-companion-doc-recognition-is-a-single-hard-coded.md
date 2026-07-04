# CR-0154: companion-doc recognition is a single hard-coded suffix; any other companion trips validate + duplicate-id

> **Status:** Proposed
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** scripts/lib/sdlc_md.py (`artifact_files`) - consumed by validate, next_id/duplicate-id, reconcile
> **Found by:** a consuming project adopting the skill

## Summary

`sdlc_md.artifact_files()` (line 448) excludes exactly two things from the artifact set:
`_index.md` and any stem ending **`-consultations`**. That single suffix is the whole
companion-doc allowlist. A real consuming project keeps richer per-epic companions under the
shared id - e.g. `EP0244-workerbot-ladder-consultations.md` **and**
`EP0244-workerbot-ladder-decisions.md` (a frozen-design record) beside the primary
`EP0244-workerbot-model-ladder-policy.md`. The `-consultations` file is correctly ignored; the
`-decisions` file is treated as a real artifact, so it trips **two** checks at once:

- **validate:** `[no-status] no > **Status:** metadata line` - a design-freeze record has no status,
  correctly, but validate does not know it is a companion.
- **duplicate-id:** `EP0244` is now claimed by two files (the `-decisions` companion + the real
  epic), a false collision.

reconcile survives it (its census has a "a file with a recognised status wins over a status-less
namesake" rule), which proves the convention is already understood in one place but not shared. The
project has 21 companion docs; only the one with the non-`-consultations` suffix errors - a brittle
allowlist, not a real defect in the project.

This is the same family as CR0153 (reconcile's exact `status` column match) and CR0144 (per-parser
table assumptions): a shared helper hard-codes one convention, and every consumer of the helper
inherits the false-positive when a project legitimately diverges.

## Proposed change

Fix at the shared helper (`artifact_files`) so all three checks benefit at once. Preferred, in order:

1. **Header-based detection (most general, no allowlist to maintain).** A file under an artifact
   type dir is a companion/note - not a tracked artifact - when it carries **no artifact metadata
   header** (no `> **Status:**` and no `# <TYPE><id>:` title block). Exclude those from the artifact
   set. This needs no per-suffix knowledge and covers `-decisions`, `-design`, `-notes`, etc.
2. **Or config-driven suffixes.** A `companion_suffixes: [consultations, decisions, ...]` list in
   `sdlc-studio/.config.yaml`, defaulting to `[consultations]` for back-compat, so a project
   declares its own companion conventions.
3. At minimum, broaden the hard-coded set - but (1)/(2) stop the next project's `-<newsuffix>` from
   re-opening this.

## Acceptance Criteria

- [ ] A status-less, header-less companion sharing an artifact id (e.g. `EP0244-...-decisions.md`)
      is excluded from the artifact set: no `no-status` validate error and no `duplicate-id` collision.
- [ ] A genuinely malformed real artifact (has a `# EPxxxx` title but truly lacks a Status line) is
      still flagged - the exclusion keys on "not an artifact", not "any status-less file".
- [ ] `-consultations` behaviour is unchanged; reconcile/validate/next_id all read the companion set
      from the one shared helper (no second copy of the rule).
- [ ] Regression test (mutation-checked) over a fixture dir with a primary epic + a `-decisions`
      companion asserts one artifact, zero duplicate-id, zero validate error.

## Notes / provenance

Found running `validate` and `gate` on a consuming project mid-sprint-planning: 1 validate error and
1 duplicate-id, both resolving to the same `-decisions` companion. The convention (primary +
consultations + decisions per epic) is legitimate and already half-supported (`-consultations`);
the gap is that the support is a one-suffix allowlist in a shared helper rather than a proper
"is this an artifact?" test.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | Claude (cross-project dogfooding) | Created via `new` (deterministic) |
| 2026-07-04 | Claude (cross-project dogfooding) | Filled in from consuming-project gate run: `artifact_files` excludes only `-consultations`, so a `-decisions` companion trips validate + duplicate-id; propose header-based (or config-driven) companion detection in the shared helper. Same family as CR0153/CR0144. |
