# CR-0542: nothing rehearses the two paths every user takes first, so a defect on them is found by a user: drive greenfield-to-first-plan and v4-to-green-gate through the shipped CLI on every gate run

> **Status:** Complete
> **Decomposed-into:** EP0214
> **Priority:** High
> **Type:** Feature
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, tools/rehearse-release.sh, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, AGENTS.md
> **Evidence:** Readiness sweep, 2026-08-09, on 167e7e38. Two fixtures built by hand in about twenty minutes - a greenfield project from `init.py run`, and a v4-era project at schema_version 2 with legacy units - surfaced three consumer-facing defects that a 6354-test suite, twenty gate lanes and a 253-point backlog had all missed: BG0558 (`sprint plan` refuses a greenfield project's first batch because no declared Affects path exists yet), BG0559 (`gate.py` doc-surface raises ModuleNotFoundError in every consuming project), BG0560 (`gate.py` FAILs on three lanes immediately after a clean `migrate --apply`). None was reachable from inside this repository, because this repository is neither greenfield nor upgrading.
> **Date:** 2026-08-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Every check in this repository runs against this repository. The two situations a user is actually in - a project that has just been created, and a project being upgraded from v4 - are the two the suite cannot occupy, and both were found to be broken the first time anybody walked them.

The ask is a rehearsal that walks them for real, through the shipped CLI, as a gate lane. Two fixtures, both built from nothing on each run so neither can accumulate state:

GREENFIELD: `init.py run` into an empty git repository, write one ordinary sized story whose Affects names files that do not exist yet, `sprint.py plan --write`, and assert a run was opened. That is the whole first-hour path, and it is currently refused.

UPGRADE: build a v4-era workspace (`schema_version` 2, a Done story with no Affects or Points, a CR carrying a legacy Effort), `migrate.py --apply`, then `gate.py`, and assert the gate is GREEN. Today it FAILs on conformance, reconcile and index-derived.

Three design constraints, each paid for by a defect this repository has already filed.

It must drive the COMMAND, never the library. `brief_fingerprint(brief(...))` passed in-process for a whole sprint while `critic.py brief` printed nothing, and `docgen`'s `--root` threaded to the file it WROTE but not the content it READ. A rehearsal built from imports would reproduce that class exactly, on the one lane whose entire purpose is to catch it.

It must FAIL on the tree as it stands, before any of BG0558, BG0559 or BG0560 is repaired. A rehearsal that is green on a tree known to be broken is a rehearsal that proves nothing, and this repository has filed that shape twice - BG0457's set comparison that cannot fail, and RUN-01KZ9315's self-referential assertion where both sides of the comparison moved together.

It must run somewhere its cost is affordable. The gate is already over its budget on most commits, and the rehearsal spawns two fixture projects. Bind it to `--boundary push,release` rather than to every commit, on the same reasoning that keeps `lint:corpus` outside the per-commit gate: a guard whose cost is paid on every commit gets switched off.

## Impact

Every adopter, on their first hour. The two paths in question are the only two ways anybody arrives: a new project, or an existing one being upgraded. Both are structurally invisible to a test suite that runs inside the skill's own repository, and the evidence is that all three defects found by walking them were live in a tree that passed every gate. Without this lane the next three are found the same way, except by a user rather than by a sweep.

## Acceptance Criteria

- [ ] A gate lane builds a greenfield fixture from nothing via `init run`, drives it through `sprint plan --write` and asserts a run was opened, reading the process exit code directly rather than through a pipe
- [ ] The same lane builds a v4-era fixture, runs `migrate --apply` and then `gate.py`, and asserts the gate is GREEN - the upgrade's outcome, not the migrate's report
- [ ] Both fixtures are constructed fresh per run in a temporary directory outside the repository, and a test proves the lane fails if a fixture write lands inside the working tree (BG0536's shape)
- [ ] The lane is proven to FAIL on a tree carrying BG0558, BG0559 or BG0560 unrepaired, by reverting each repair in turn and asserting the lane reddens - the positive control, without which the lane's green means nothing
- [ ] The lane is bound to the push and release boundaries rather than to every commit, and its measured cost is recorded against the gate budget

## Recommendation

Option 1. Option 2 puts the fixtures inside the process that already resolves this repository's own modules and paths, which is the confound the lane exists to remove - and `test_cli_grammar.py` is the standing evidence that an in-suite test can check a flag's grammar exhaustively and its effect not at all. Option 3 is what the project has today: AGENTS.md already tells an author to exercise every claim through the shipped entry point, and all three defects shipped anyway, which is LL0027 - a rule stated with no gate behind it is a known-weak rule.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Raised |
