# CR-0130: blocker sweep: detect now-unblocked units (cross-project via PVD), pre-plan + reconcile lane

> **Status:** Complete
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/audit.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/pvd.py
> **Depends on:** -

## Summary

The skill tracks what is blocked but never re-checks whether a blocker has *cleared*. `audit.py`
already flags `unmet-deps` (a `Depends on:` referent not yet delivered) - the forward direction. The
inverse is missing: a unit sits at Status `Blocked` (or carries a `Depends on:` / epic `Blocked By`
referent) and stays there long after the thing it waited on reached a terminal state. Nothing sweeps
the backlog to surface "these are now unblocked - they can move to Ready and enter the next sprint."
The operator finds out by hand, or never, and freshly-unblocked work silently misses planning.

This matters most on **multi-project setups (PVD)**. A blocker is frequently cross-repo: a unit in
one repo waits on a capability delivered in another. The blocked unit's home repo has no signal when
the upstream repo ships - the dependency referent lives across the `product-manifest.yaml`
boundary. A blocker sweep that resolves referents through the manifest's `repos[].path` (the same
source `pvd.py` already reads) closes that gap: a capability marked Done in repo A unblocks a Blocked
unit in repo B, detected mechanically rather than by the operator remembering the link.

Proposed: a **blocker sweep** that, across all artefacts (and across repos via the PVD manifest):

1. Collects every unit with a blocker signal - Status `Blocked`, a `Depends on:` field, or an epic
   `Blocked By` row.
2. Resolves each referent's current status: in-repo by the file census ([[LL0001]]), cross-repo by
   reading the sibling repo named in `product-manifest.yaml`.
3. Reports the units now **fully unblocked** (every blocker is terminal/delivered) as candidates to
   transition `Blocked -> Ready`, and the still-blocked ones with the specific outstanding referent.

Wiring: run it **before sprint planning** so newly-unblocked work is eligible for the batch (a
pre-`plan` step, surfaced like the reconcile-before-plan gate), and add it as an advisory **reconcile
lane** so routine drift detection reports stale-blocked units. Per the determinism directive and
[[LL0008]]: detection is mechanical and the report is deterministic; the `Blocked -> Ready`
transition stays the gated `transition` call (the sweep proposes, it does not silently move state,
and it never reports a unit unblocked while any referent is unresolved or unreadable).

## Acceptance Criteria

- [ ] a blocker-sweep verb collects every unit with a blocker signal (Status `Blocked`, a
      `Depends on:` referent, or an epic `Blocked By` row) and reports, per unit, the referents and
      their current status
- [ ] referents resolve in-repo by the file census; **cross-repo referents resolve through
      `product-manifest.yaml` `repos[].path`** (reusing `pvd.py`'s manifest read), so a blocker
      cleared in a sibling repo is detected
- [ ] units whose every blocker is terminal/delivered are reported as **now-unblocked** candidates
      for `Blocked -> Ready`; the sweep proposes, it does not auto-transition (the gated `transition`
      stays the actor)
- [ ] the sweep runs **before sprint planning** (a pre-`plan` step) so newly-unblocked units are
      eligible for the batch, and is available as an advisory **reconcile lane**
- [ ] **fail loud, never false-clear** ([[LL0008]]): a referent that is missing, unreadable, or in an
      unknown status is reported as still-blocked (or as an error), never silently treated as cleared;
      a cross-repo path that cannot be read is named, not skipped
- [ ] **deterministic** (standing directive): detection and the report are script-backed and stable
      across runs; only the transition decision is the operator's/loop's
- [ ] unit tests: in-repo unblock, cross-repo unblock via a fixture manifest, partial-block (one of
      two referents cleared stays blocked), unreadable cross-repo path reported not skipped
- [ ] docs: `reference-reconcile.md`, `reference-sprint.md` (pre-plan step), `reference-project.md`
      (PVD cross-repo blockers), and `help/` updated; CHANGELOG `[Unreleased]` ([[LL0004]])

## Out of Scope

- Auto-transitioning `Blocked -> Ready` (stays the gated `transition` call - the sweep only proposes)
- The forward `unmet-deps` check, which `audit.py` already provides (this CR is the inverse)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-27 | field | Created via `new` (deterministic) |
