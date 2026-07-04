# CR-0132: reconcile status vocabulary must be project-configurable (drift-0 unreachable with bespoke statuses)

> **Status:** Proposed
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/reference-reconcile.md, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-outputs.md
> **Depends on:** -

## Summary

`reconcile.py` is the tool that keeps indexes honest, and its headline promise is "drift 0". In a
real consuming project that promise was **structurally unreachable**, which is worse than a missing
check - it trains the operator to ignore the one signal reconcile exists to give.

Observed in the field (agent-crew, this session): `reconcile.py detect` reported a persistent CR
`count-mismatch` that could not be cleared. Root cause: the project's CR index carries a `Built`
status row (a legitimate half-state: code merged, not yet Complete), but the script's row-status
parser does not recognise `Built`, so it computes a summary total that can never match the
human-maintained table. Every run reports drift; no `apply` clears it. By contrast, in the
sdlc-studio repo itself `reconcile apply` reaches 0 cleanly - because that repo uses only the
canonical status set the script models.

So the defect is precise: **the skill's status vocabulary is hard-coded and narrower than what real
projects grow into, with no config seam to extend it.** Projects legitimately add statuses
(`Built`, `Gated`, `Superseded`, `Deferred`); the reconcile census + summary recompute must count
whatever vocabulary the project actually uses, or "drift 0" is a lie for that project.

Proposed: teach reconcile the project's full status set, sourced from config rather than hard-coded.

1. Read the recognised statuses (per artefact type) from the project config (`.sdlc-studio.yaml` /
   `reference-config.md`), defaulting to the current canonical set when unspecified.
2. The census, `row_counts`, and summary recompute all range over that configured set, so a
   `Built`/`Gated`/etc. row is counted, not dropped, and `apply` can reach a true 0.
3. An **unknown** status (one in a file/row but not in the configured set) is reported as its own
   drift kind (`unknown-status`) - fail loud ([[LL0008]]), never silently miscounted.

## Acceptance Criteria

- [ ] reconcile reads the recognised per-type status vocabulary from project config, defaulting to
      the current canonical set when the key is absent (back-compatible: existing projects unchanged)
- [ ] census, `row_counts`, and the summary recompute all range over the configured set, so a
      project that uses `Built` (or any configured status) reaches a genuine `detect` drift 0 after
      `apply` - reproduce the agent-crew CR-summary case as a fixture and assert it clears
- [ ] a status present in a file/row but absent from the configured set is surfaced as an
      `unknown-status` drift, never silently treated as zero or folded into another bucket
- [ ] `reference-reconcile.md` + `reference-config.md` document the config key and the default set;
      `help/` updated where it lists reconcile drift kinds
- [ ] unit tests: configured-extra-status counted, unknown-status flagged, no-config default path
      unchanged
- [ ] `CHANGELOG.md` `[Unreleased]` entry ([[LL0004]])

## Out of Scope

- Prescribing a canonical status set for all projects (this CR makes the set configurable, it does
  not standardise it - status sprawl is a separate concern).
- Auto-transitioning artefacts to resolve drift (transitions stay the gated `transition` call).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | claude | Created via `new` (deterministic) |
