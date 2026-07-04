# CR-0132: reconcile findings must self-diagnose (name the out-of-vocab status + suggest the actionable fix)

> **Status:** Proposed
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/reference-reconcile.md, .claude/skills/sdlc-studio/help/status.md
> **Depends on:** -

## Summary

> **Root-cause correction (2026-07-04).** This CR was first filed claiming reconcile's status
> vocabulary is hard-coded and should be made project-configurable. That is **wrong** - `reconcile.py`
> already reads a per-type `status_vocab` from project config (`sdlc_md.status_vocab`), and
> `validate.py check` already flags an out-of-vocab status precisely. Deeper investigation found the
> real defect, below. The vocabulary mechanism is fine; the **diagnostics are not**.

The friction (agent-crew, this session): `reconcile.py detect` reported a persistent CR
`count-mismatch` I could not clear. Its `fix` hint said *"recompute the summary counts from the index
rows"* - so I ran `reconcile apply`, which changed nothing, and I wrongly concluded the drift was a
"structural quirk" to be ignored. **The signal trained me to distrust the signal.**

The actual cause: agent-crew's CRs use a `Built` (and `Done`) status that its `.config.yaml`
`status_vocab.cr` does not declare, so those rows canonicalise to `Unknown`, are dropped from
`row_counts`, and the summary total can never match. `validate.py check` says this in one line -
*"status 'Built ...' is not one of the allowed cr statuses"* - but nothing pointed me at `validate`,
and the `count-mismatch` finding named neither the offending status nor the config fix.

So the defect is **diagnostic quality**, and it generalises: a finding whose `fix` string is generic
and whose remedy lives in a *different* tool is a dead end. The fix an agent can act on must travel
**with** the finding.

Proposed - make reconcile's findings self-diagnosing (and set the pattern for other emitters):

1. When a `count-mismatch` is caused by one or more statuses canonicalising to `Unknown`, the finding
   names them and the artefacts carrying them, and its `fix` becomes actionable: *"status 'Built' on
   CR-0299, CR-0300 is not in `status_vocab.cr`; add it to `.config.yaml` or run `validate.py check`."*
2. `detect` cross-references the sibling tool that diagnoses the class of drift (here `validate`), so
   an agent is routed to the right next command instead of guessing.
3. The generic *"recompute the summary counts"* hint is kept only for a genuine arithmetic drift
   (all statuses in-vocab, counts simply stale) - the one case where `apply` actually resolves it.

## Acceptance Criteria

- [ ] a `count-mismatch` caused by out-of-vocab statuses names the offending status(es) and the
      artefacts carrying them in the finding, not a bare `id: null`
- [ ] its `fix` string is actionable and specific: add-to-`status_vocab` (with the config path) or
      run `validate.py check`, rather than the generic "recompute the summary counts"
- [ ] the generic recompute hint remains for a true arithmetic-only mismatch (all statuses in-vocab)
- [ ] `detect` output routes the operator/agent to the sibling diagnostic tool for the drift class
- [ ] reproduce the agent-crew case as a fixture: a CR index with a `Built` row absent from
      `status_vocab.cr` yields the specific finding + fix, and adding the status to config clears it
- [ ] `reference-reconcile.md` documents the self-diagnosing finding shape; `help/status.md` updated
- [ ] `CHANGELOG.md` `[Unreleased]` entry ([[LL0004]])

## Out of Scope

- Making the vocabulary configurable (already done - `status_vocab` in project config).
- The broader "every emitter suggests a fix on error" sweep across all 40+ scripts - this CR proves
  the pattern on the finding that actually dead-ended a session; generalising it is a follow-on.
- Auto-editing a project's `.config.yaml` (the sweep proposes; the operator adds the status).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | claude | Created via `new` (deterministic) |
| 2026-07-04 | claude | Root-cause corrected after deeper tooling investigation: the vocab is already configurable + validate already flags it; the real defect is undiagnosable findings. Retitled + rescoped. |
