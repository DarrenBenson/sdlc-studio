# CR-0239: Commit-id convention for per-id file attribution in the engagement floor

> **Status:** Complete
> **Size:** M
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Dani Okafor; persona; 4.0.0

## Summary

The engagement floor's git cross-check (git log --grep=<id>) cannot attribute a file to one id when a commit names several judged ids, so it skips such batch commits to avoid over-firing. As a result, understatement (a unit declares one file in Affects but the change touched more) escapes the floor whenever the unit shares its commit with another judged id - the norm in real sprints. git log alone lacks the information to apportion files per id.

## Impact

The engagement-floor lane does not catch Affects understatement for a unit committed alongside another judged id. Pure omission and solo-id-commit understatement are already caught; this closes the shared-commit understatement gap. No runtime code path - a commit-message discipline plus a commit-msg hook and a reader that maps a commit to a single id.

**Effort:** M

> **Affects:** .claude/skills/sdlc-studio/scripts/engagement_floor.py, .githooks/commit-msg, tools/enable-hooks.sh

## Acceptance Criteria

- [x] A per-commit id association exists - a `Refs: <id>` trailer. Grammar: one or more `Refs:` lines, each listing judged ids separated by commas and/or spaces (`Refs: US0301`, `Refs: US0301, US0302`, or repeated lines); the dashed spelling matches too. It maps a commit to each id it names.
- [x] The engagement floor's git leg reads the trailer (`_refs_ids`) and attributes a commit's files to each id a `Refs:` trailer names, even in a shared commit - so an understated `Affects` is caught once the owning unit carries a trailer. Strictly additive: the batch test reads the SUBJECT LINE only, so a body `Refs:` never turns a solo-subject commit into a pseudo-batch that would strip the subject id's own cross-check. A trailer can only raise a count, never lower one, for any body content (including the conventional see-also use of `Refs:`); each named id gets the full file set. A genuine multi-id subject with no trailer naming the unit is still skipped (unchanged).
- [x] An opt-in commit-msg hook (`.githooks/commit-msg` + `engagement_floor.py check-commit-msg`) warns when a subject names more than one judged id without a `Refs:` trailer covering them. Warns by default, blocks only under `SDLC_ENGAGEMENT_STRICT=1`. Degrades honestly (no git / no script / unparseable message never blocks). Never forced on a consuming project.

## Implementation Notes

- **Refs grammar:** `_REFS_LINE_RE` matches a `Refs:` line (case-insensitive); ids within accumulate across commas, spaces, and repeated lines.
- **Attribution rule (raise-only, never lowers):** a commit's files attribute to `rid` when a `Refs:` trailer names `rid` OR the SUBJECT LINE names at most one judged id. The batch test reads the subject only, never the body - so a body `Refs:` line can only ADD attribution, never turn a solo-subject commit into a pseudo-batch that strips the subject id's own count. Proven raise-only across the full subject x body matrix (`test_refs_never_lowers_count_below_the_no_refs_baseline`).
- **Hook opt-in:** enabled here via `tools/enable-hooks.sh` (core.hooksPath -> .githooks, alongside the pre-commit gate); a consuming project opts in per project by pointing its own commit-msg hook at the shipped script.
- **Tests:** `RefsTrailerAttributionTests` + `CommitMsgCheckTests` in `test_engagement_floor.py` (shipped); `test_commit_msg_hook.py` in `tools/tests` (the shim, repo-only). Docs updated: reference-scripts-verify, reference-config, D0026.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | Dani Okafor | Raised |
| 2026-07-14 | Dani Okafor | Built: Refs trailer attribution + opt-in commit-msg hook; ACs met, tests + docs in the same unit. Review pending (author != reviewer). |
| 2026-07-14 | Dani Okafor | Critic reject repaired: the batch detector read the full message, so a body `Refs:` naming a foreign id turned a solo-subject commit into a pseudo-batch and voided the subject id's solo cross-check (understatement escaped a case the pre-Refs floor caught). Fixed: batch test now reads the SUBJECT LINE only, making the trailer strictly raise-only. Red test + raise-only matrix + mutation proof added; wording corrected here, in the script docstring and D0026. |
