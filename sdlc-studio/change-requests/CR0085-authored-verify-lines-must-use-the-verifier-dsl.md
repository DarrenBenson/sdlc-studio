# CR-0085: enforce the test-spec as the AC-to-test bridge at epic scope (runner-targeted Verify lines as a sub-fix)

> **Status:** Complete
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Improvement

## Summary

The story's AC and the test that proves it were chosen *"at different times by different
processes with nothing binding them"* - so they drifted into two parallel, non-intersecting
descriptions, and the verifier read 0/7. The **test-spec (TS) artifact is the missing
binding.** Its template already carries the two structures that would have caught this: an
**AC Coverage Matrix** (Story | AC | Test Cases | Status) and an **Environment** block
(live server / DB / Docker prerequisites). Authoring the matrix *is* the act of choosing
the test-case names up front - so the AC, the TC id, and the test title become one name by
construction, and convergence falls out of the artifact existing. The fix is to **enforce
the TS as the AC-to-test bridge at epic scope**, with runner-targeted Verify lines as the
executable half *inside* it. The two are complementary, not either/or: Verify-line syntax
makes one AC mechanically runnable; the matrix makes the *set* of 5-13 stories converge and
declares the environment. Neither alone prevents the defect.

## Problem

From the reflection (verbatim): *"The defect was that the AC's test name and my Jest
`it(...)` title were chosen at different times ... had I filled that [AC Coverage] matrix
before writing code, the Verify line, the TC id, and the Jest title would have been one
name by construction. ... I skipped straight from story -> code with no intermediate
binding, which is precisely how you get 'two parallel descriptions'."* And: *"Make TS
required at epic implement / autosprint scope, optional for single-story. And it only
works if something enforces it."*

Ground truth: `sdlc-studio/test-specs/` was empty - zero TS authored (true no-artifacts
mode). The authored Verify lines compounded it - free-form `npm test -- file -t "..."`
(non-existent files; the `-- ... -t` form mis-parses) and `curl ... returns 200` (prose;
`returns` is not a DSL verb, so it routed to `shell` and failed `200: not found`) instead
of the DSL's `jest <pattern>` / `http METHOD URL -- <jq>` / `manual <what>`. US0001 went
0/7 -> 7/7 only once its Verify lines pointed at real `jest -t "<title>"` tests. So both
halves were missing: no binding artifact, and non-runnable Verify lines.

## Proposed Changes

### Item 1: Enforce the test-spec as the AC-to-test bridge (epic scope)

**Priority:** High
**Effort:** 3

Require a test-spec at **epic-implement / autosprint scope** (optional for single-story
work, where a full TS is overkill). The TS's AC Coverage Matrix is authored **before
code**, fixing the test-case names that the AC's Verify line and the implementation's test
title both adopt - convergence by construction. A TS only protects if **enforced**: a gate
validates the coverage-matrix status against the verify report (every AC has a mapped,
passing test case), so the matrix cannot be decorative. The Environment block declares
prerequisites (live server / DB / Docker), turning silent red failures into explicit
manual/integration-tier ACs.

### Item 2: Authoring emits DSL-correct, runner-targeted Verify lines (the executable half)

**Priority:** High
**Effort:** 2

Batch creation (CR0078) and the authoring loop (RFC0019) emit Verify lines in the DSL,
resolved to the project's detected runner (`jest <pattern>` / `pytest <node>` / `go`), with
the test-title taken from the TS matrix so the AC and its test share one name. Service-
dependent ACs use `http METHOD URL -- <jq>`; non-executable ones use `manual <what>`.
Agent-instructions (CR0083) state the convention so hand-written tests match the titles.

### Item 3: Advisory lint + manual lane + CLI grammar

**Priority:** Medium
**Effort:** 1

`validate` / `verify_ac` advisory-flags Verify lines that fall through to `shell` but look
like a mis-written runner invocation (`npm test -- ... -t`, `curl ... returns N`). `status`
surfaces the `manual` count as its own lane (not a failure), so env-bound ACs read as
"deferred: needs integration env". Minor: let `verify_ac` accept `--id USNNNN` like
`transition.py`, not only `--story <path>` (the inconsistent grammar tripped the agent).

## Acceptance Criteria

- [x] the TS-as-bridge discipline (matrix authored before code; names the Verify line and
      test both adopt) is documented at epic/autosprint scope in `reference-verify.md`
- [x] a gate validates the coverage matrix against `verify-report.json`
      (`verify_ac ts-check --spec <ts> --verify-report <json>`): every AC mapped to a passing
      test case, no placeholders, no "passing in the matrix but failing in the report"
- [x] the DSL + runner convention is documented (`reference-verify.md`) and **enforced
      negatively** by `verify_ac lint` (flags `npm test -- ... -t`, `curl ... returns N`);
      auto-emission from the matrix is authoring guidance, not deterministic (test titles
      exist only post-authoring)
- [x] the Environment block declares prerequisites (template); env-bound ACs author as
      `http`/`manual`, enforced by the lint - **deferred:** a distinct `status` manual lane
      (status.py does not read the verify-report today)
- [x] `verify_ac lint` advisory-flags `shell`-routed mis-writes; `verify_ac run --id` works;
      agent-instructions document the convention (CR0083)
- [x] pairs with CR0084 (the hard gate is a clean signal only once names converge);
      CHANGELOG `[Unreleased]` entry same commit (LL0004)

> **Deferred to a follow-up (workflow-surface, not deterministic here):** a *hard* epic-scope
> TS requirement wired into `epic implement` / the conformance gate, and a `status` manual
> lane. Both touch the model-driven workflow; the enforceable code spine (ts-check, lint,
> `--id`) and the documented discipline land here.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
| 2026-06-24 | sdlc | Reframed (agent verdict): lead with the test-spec as the AC-to-test bridge (AC Coverage Matrix authored before code = convergent names by construction; Environment block declares prereqs), Verify-line DSL as the executable half. TS required at epic/autosprint scope, optional single-story, and must be enforced or it is decorative |
