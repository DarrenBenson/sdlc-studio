# CR-0383: Root anchoring is a per-script convention, not a shared one: 62 scripts declare --root and one discovers it

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py,.claude/skills/sdlc-studio/reference-scripts.md,.claude/skills/sdlc-studio/best-practices/script.md
> **Date:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Class-level finding behind BG0228 and BG0240, measured during BG0228's sibling sweep. 62 scripts declare a --root flag, and `discover_root` is used by exactly ONE of them (`verify_ac.py`, and now `repo_map.py` through it). Every other writer treats a default --root . as the cwd, so any of them run from a subdirectory writes a stray sdlc-studio/ tree and exits 0. BG0228 and BG0240 are three instances of one missing convention, found one at a time; the remaining ~59 have not been checked. Known-good counter-examples exist: reconcile.py's report write is properly `repo_root`-anchored, and plan.py's --plans-dir is a deliberate non-root surface. So the fix is a shared resolver plus a rule, not a sweep of 62 hand-fixes.

## Impact

Any agent or operator running a skill script from a subdirectory rather than the project root - which is the normal case for an agent working inside scripts/, and the exact condition under which BG0228, BG0240's lessons.py half and BG0240's `loop_guard.py` half were all reproduced. The failure is silent and fail-open: a stray sdlc-studio/ tree is created beside the cwd, the script prints a relative path that hides where the file went, and it exits 0. A consuming project can therefore accumulate phantom workspaces that reconcile never sees, while the real workspace goes unwritten and the operator is told the write succeeded.

## Census (measured 2026-07-21, during RUN-01KY321Q)

The original filing said "62 scripts declare `--root` and one discovers it". The sibling sweep
BG0240 required has now produced the real shape, and it is worse in one specific place.

**20 further scripts** resolve the CLI `--root` as `Path(args.root)` with no discovery. Only four
use the family resolver (`verify_ac`, `repo_map`, and now `lessons`, `loop_guard`). **Ten of the
twenty drive WRITES**, worst first:

| script | what it writes when run from a subdirectory |
| --- | --- |
| `next_id.py:162,203,248` | **id allocation against an empty tree, so minted ids COLLIDE with existing ones** |
| `sprint.py:3220` | `sprint-plan.json`, the file the run reads back |
| `artifact.py:1236` | artefact files and index rows |
| `mutation.py:936` | the mutation report and ledger |
| `file_finding.py:690` | filed bugs, CRs and RFCs |
| `digest.py:139`, `command_audit.py:256`, `sprint_report.py:199`, `persona_gen.py:117`, `project_upgrade.py:719`, `migrate_v3.py:424`, `complexity.py:372` | reports and generated artefacts |

Readers with the same shape, where the symptom is a false CLEAN rather than a misplaced write:
`status.py`, `validate.py`, `reconcile.py`, `close_owed.py`, `backlog_triage.py`, `review_prep.py`,
`route.py`, `flow.py`.

`next_id.py` is the one to weigh first and is the reason this CR should not keep waiting. An id
allocated against a workspace the tool cannot see is not a misplaced file, it is a **collision with
an id that already exists**, and the repo's whole traceability model rests on ids being unique.
Everything else on this list produces a stray file somebody eventually notices.

## Acceptance Criteria

- [ ] `resolve_root` and `under_root` (or their agreed successors) are documented in reference-scripts.md as the single sanctioned way a script resolves --root and anchors a relative output path
- [ ] A census of the 62 --root-declaring scripts is recorded, classifying each as anchored, unanchored, or a deliberate non-root surface with its reason
- [ ] Every script classified unanchored is either fixed or has a filed follow-up naming it - silence is not a classification
- [ ] best-practices/script.md states the rule for new scripts, so the next one inherits it rather than repeating the omission
- [ ] A test pins the resolver's two halves from a cwd that is NOT the root: a named root is honoured verbatim, and a default root is discovered upward rather than taken as the cwd

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Raised |
