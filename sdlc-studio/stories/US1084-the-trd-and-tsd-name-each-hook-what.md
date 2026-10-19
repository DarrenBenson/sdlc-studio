# US1084: The TRD and TSD name each hook, what it runs, where the full suite runs and what a tag push does not run, read from the hooks themselves

> **Status:** Done
> **Delivers:** CR0644
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, sdlc-studio/tsd.md, tools/tests/test_lean_gate_docs.py, changelog.d/US1084.md
> **Epic:** EP0290
> **Points:** 3
> **Persona:** Rowan Achterberg

## User Story

**As** the skill maintainer reading the TRD and TSD to learn what a commit, a push and a tag prove
**I want** both documents to name each hook, what it runs and where the full suite runs, read from the hooks themselves
**So that** a green commit is never mistaken for a green tree, and a tag is never believed to have run steps that are manual

## Acceptance Criteria

- **AC1:** Given the hooks in `.githooks/`, when the TRD and the TSD are read, then each names every hook, the TSD's pipeline stages give them in the order git runs them (pre-commit, commit-msg, pre-push), and each points at the hook's own `--list` where the hook has one rather than restating its lanes
  - **Verify:** pytest tools/tests/test_lean_gate_docs.py::GateDocsTests::test_every_hook_is_named_in_run_order
  - **Verified:** yes (2026-10-19)
- **AC2:** Given each `--boundary` value `.githooks/pre-push` and the host path it sends through pass to `gate.py`, when the documents are read, then both name it beside the push or the tag that runs it, the TSD's push stage names the prerequisite check and the red-main acknowledgement (D0181) that run before the gate, and the TSD says the full suite runs at the push boundary while a commit runs only the selected suites against an advisory budget
  - **Verify:** pytest tools/tests/test_lean_gate_docs.py::GateDocsTests::test_each_boundary_the_hook_runs_is_named
  - **Verified:** yes (2026-10-19)
- **AC3:** Given the release steps no hook or workflow runs (`gate.py --release`, `release_cut.py record-green`, `release_cut.py tag-check`), when the TSD is read, then each is named as a manual pre-tag step and neither document says a tag push runs it (D0375)
  - **Verify:** pytest tools/tests/test_lean_gate_docs.py::GateDocsTests::test_unrun_release_steps_are_named_manual
  - **Verified:** yes (2026-10-19)
- **AC4:** Given every `.local` path `gate.py` and `tools/gate_timing.py` write, when the TRD is read, then each is named, and neither document says the gate writes nothing or is read-only
  - **Verify:** pytest tools/tests/test_lean_gate_docs.py::GateDocsTests::test_the_gates_local_writes_are_named
  - **Verified:** yes (2026-10-19)
- **AC5:** Given the gate's cost budget as `gate.py` declares it, when the TRD's performance row and the TSD's performance NFR are read, then each states the budget as a measured figure with its source and neither calls the gate sub-second
  - **Verify:** pytest tools/tests/test_lean_gate_docs.py::GateDocsTests::test_the_gate_cost_row_states_the_declared_budget
  - **Verified:** yes (2026-10-19)

## Notes

- Serves: Rowan Achterberg, End goal 3 (D0380 repoint; the card is sdlc-studio/personas/rowan-achterberg-skill-maintainer.md).
- AC1 must fail on: a hook dropped from either document, or the TSD's stages listed out of git's order.
- AC2 must fail on: a boundary the hook runs left unnamed, or the TSD restoring 'runs the whole gate on every commit'.
- AC3 must fail on: the TSD's tag row claiming the tag push runs `--release`, or one of the three steps dropped; the set is derived as the release commands the runbook names minus those any hook or workflow calls, never typed into the test.
- AC4 must fail on: a `.local` path gate.py writes left unnamed, or 'the gate writes nothing' restored.
- AC5 must fail on: 'Sub-second' restored for the gate (trd.md:616), or a budget stated that `gate.py` does not declare.
- Every derived set asserts a known member before it is compared, or an empty derivation passes vacuously (LL0043): `commit-msg` among the hooks, `push` and `release` among the boundaries, `release_cut.py tag-check` among the manual steps, `gate-suite-verdict.json` and `gate-timings.json` among the `.local` writes.
- Derive every fact from the source file it describes (the hooks, gate.py, the workflows, the runbook), as test_lean_prd_refresh.py derives subcommands from `--help`: an enumeration typed into the test is a lower bound, not a boundary (LL0043).
- Covers RV0028 TRD-2, TRD-3, TRD-9, TSD-1, TSD-2, TSD-5, TSD-14, TSD-17, TSD-23. Persona to be repointed to the skill-maintainer card once US1079 lands (D0377, D0379).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-19 | Claude Opus 5.5 | Groomed: criteria, Verify lines and the mutants each must fail on (D0377) |
| 2026-10-19 | Claude Opus 5.5 | Regroomed after the goal review (round 4): the seats' findings folded in: AC5 for the cost row, each hook's --list, the push stage's prerequisite and red-main checks, the gate_timing writes, known-member floors |
| 2026-10-19 | Claude Opus 5.5 | Repointed at Rowan Achterberg, Primary for the repository-tooling interface, before review (D0379, D0380) |
