<!--
Sprint retro for the backlog-closeout tranche. Related: reference-autosprint.md, CR0018.
-->
# RETRO-0004: Backlog closeout

> **Date:** 2026-06-20
> **Batch:** CR0005, CR0006, CR0009, CR0015 + withdraw RFC0006/0010/0011
> **Goal:** done
> **Delivered:** 4 CRs / 4   **Withdrawn:** 3 RFCs   **Blocked:** 0

## Delivered

- **CR0005 / US0019** - verify_ac dry-run writes a distinct `.dry-run.json`
  enumerating the pending `(ac, old, new)` flips, and every run appends to
  `.local/verify-history.jsonl` - the audit trail the single snapshot lacked.
- **CR0006 / US0020** - a graded `eval <cmd> --threshold <f>` verifier verb (shells
  to a configurable eval tool, parses a JSON score, passes >= threshold; soft dep,
  stubbed in tests).
- **CR0009** (bounded core) - reference-code.md loads both `javascript.md` +
  `typescript.md` for TS (and `sql.md` + `postgresql.md` for PostgreSQL); each pair
  guide gained a `{#quick-conventions}` slice anchor. File-merge deferred (RFC-shaped).
- **CR0015** - `test_confinement.py` snapshots a fixture workspace and asserts the
  read-only scripts mutate nothing and a writing script touches only its named
  target - backing the TSD claim with a real test, not a wording downgrade.
- **RFC0006/0010/0011 Withdrawn** - terminal triage: RFC0001 settled the autonomy
  default (RFC0006); RFC0011 was moot once 0006 went; RFC0010's meta-point was
  actioned by CR0016 + the tranche audit.

## Blocked / deferred

- None delivered-side. The 8 substantive RFCs stay open as the **design backlog** -
  they need decisions, and accepting them spawns new CRs (out of a closeout's scope).

## What went well

- **The actionable backlog reached zero** - 0 Proposed CRs, 0 Open bugs - cleanly,
  with the loop's own gates green (conformance 20/20, drift 0 all scopes).
- **The honest fix beat the cheap one twice:** CR0015 wrote a real confinement test
  instead of downgrading the TSD claim; CR0017 (last sprint) had already corrected
  CR0005's overstated evidence, which made CR0005 precise to implement.
- **Right-sized the RFCs:** distinguished "deliverable now" (CRs) from "needs a
  decision" (RFCs), and only withdrew the genuinely obsolete ones rather than
  force-closing a healthy design queue.

## What was hard / what stalled

- **Wrong epic + dangling link on US0019/US0020:** first filed under EP0004, whose
  file is `EP0004-testing.md` (not `-testing-pipeline.md`) and which lists verify_ac
  out-of-scope. Caught and moved to EP0005. A reconcile/integrity pass would have
  flagged the dangling link; spotting it pre-commit saved a red gate.
- **Critic REJECT on CR0006:** an unguarded `float(threshold)` crashed the whole run
  on a malformed value - exactly the "no crash" the AC promised. Guarded + boundary
  test added.

## Lessons

- Check the epic file *exists* and that the artifact is in its scope before linking -
  a plausible-looking `EPxxxx-...md` link can be dangling (integrity catches it, but
  cheaper to get right). <!-- promotable -->
- "Withdraw vs leave open" is a real triage axis for RFCs: obsolete (settled
  elsewhere) -> Withdraw; healthy design option -> leave open. Don't conflate
  "close the backlog" with "force every idea terminal".

## Metrics

- Critic rejects: 1 (CR0006; repaired) · Commits: 3 green · Tests: 270 -> 285 ·
  New scripts: critic.py (last sprint) · New tests: confinement, eval-verb,
  report-history.
