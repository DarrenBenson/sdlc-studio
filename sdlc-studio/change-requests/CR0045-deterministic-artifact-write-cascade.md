# CR-0045: deterministic artifact create + cross-link cascade

> **Status:** Proposed
> **Priority:** High
> **Type:** Feature
> **Requester:** Darren Benson (from the v2.2 usage retrospective)
> **Date:** 2026-06-21
> **Affects:** scripts/file_finding.py (generalise) or scripts/artifact.py (new), scripts/transition.py, reference-outputs.md
> **Depends on:** CR0035 (file_finding), CR0042 (transition), CR0026 (reconcile apply)
> **GitHub Issue:** --

## Summary

Detection is deterministic (reconcile/conformance/verify), but artifact **creation and
the cross-link cascade are still hand-driven** - the biggest friction observed driving
the skill through v2.1/v2.2. Creating one story today is ~10 manual steps: allocate ID,
render the file, add the index row, recompute counts, add the row to the parent epic's
Story Breakdown, link the CR, etc. `file_finding` does this for Bug/CR/RFC findings and
`transition` does status changes, but there is no general "create any artifact + wire
every index and cross-link in one deterministic step." This CR closes that gap - the
last big piece of "maximise deterministic tool use."

## Problem

The completion cascade is documented in `reference-outputs.md` but executed by hand or
by the agent re-deriving it each time (~3-4k tokens of bookkeeping per unit, error-prone
- early hand-edits drove BG0018/CR0026). It is mechanical and should be a script.

## Proposed Changes

- **`new`** - generalise the `file_finding` filer to every numbered type (story, epic,
  plan, test-spec, in addition to bug/cr/rfc): allocate the ID, render from the type's
  template (required sections enforced), write the file, append the type-correct index
  row, recompute counts (reuse `reconcile.apply_type`).
- **Cross-link wiring** - on `new story`, add its row to the parent epic's Story
  Breakdown; on `new` of a CR-spawned unit, link back. Deterministic, idempotent.
- **`close`** - terminal-transition + cascade: reuse `transition` (status + index row +
  counts + epic-breakdown tick) and tick the CR/story AC checkboxes where applicable.
- Document the one-command cascade in `reference-outputs.md`, replacing the by-hand steps.

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts/file_finding.py / artifact.py | create across all types + cross-link wiring | New / Enhancement |
| scripts/transition.py | reused for the close cascade | Reused |
| reference-outputs.md | document the deterministic cascade | Modified |

### Breaking Changes

None. Additive; the manual cascade still works, this makes it one command.

## Acceptance Criteria

- [ ] `new --type <story|epic|plan|test-spec|bug|cr|rfc> --title ... <fields>` allocates the ID, writes a structured file, appends the index row, and recomputes counts; `reconcile detect` is then clean.
- [ ] Creating a story wires it into the parent epic's Story Breakdown (idempotent); creating a CR-spawned unit links back.
- [ ] `close --id <id>` terminal-transitions the artifact and cascades (index row, counts, epic-breakdown tick, AC ticks) with `index_synced` honest.
- [ ] Unit-tested across types incl. the cross-link wiring; the by-hand cascade in reference-outputs.md is replaced by the command. Independent critic APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Darren Benson | Raised - the artifact write-cascade is the biggest remaining hand-driven step; make create+wire deterministic |
