# BG1528: The PRD Context section still calls the installed copy the back-port source and cites CLAUDE.md for it

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** sdlc-studio/prd.md, tools/tests/test_lean_prd_refresh.py, changelog.d/BG1528.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, prd lens, survived 3 of 3 refute votes; observed at sdlc-studio/prd.md Section 2 Problem Statement, Context (lines 210-212)
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:22:50Z

## Summary

Section 2 of `sdlc-studio/prd.md` (Problem Statement, Context, lines 210 to 212) says the installed copy under the home directory is the back-port source for production fixes and points the reader at `CLAUDE.md`. The doctrine is the reverse: a fix lands in this repository and is mirrored out to the installed copy with `tools/forward-port.sh`. Neither `CLAUDE.md`, `AGENTS.md` nor `CONTRIBUTING.md` contains the word back-port, so the citation points at nothing. CR0432 corrected the same inverted statement in the TRD and the personas page and is Complete, but the PRD was outside its scope. A reader rebuilding from the PRD would edit the installed copy first, which the forward-port check then reports as drift.

## Steps to Reproduce

1. Open `sdlc-studio/prd.md` and read the Context paragraph of section 2 (lines 210 to 212).
2. Observe the sentence saying the installed copy is the back-port source for production fixes, with a pointer to `CLAUDE.md`.
3. Search `CLAUDE.md`, `AGENTS.md` and `CONTRIBUTING.md` for the word back-port, ignoring case: there is no match.
4. Read the Forward-porting section of `AGENTS.md`: it says never to run the installer here and to mirror with `tools/forward-port.sh`.
5. Expected: the PRD states the same direction of flow as AGENTS.md. Actual: it states the opposite and cites a page that does not say it.

## Proposed Fix

Rewrite the Context sentence in `sdlc-studio/prd.md` to say this repository is the source, that fixes land here and are mirrored to the installed copy by `tools/forward-port.sh`, and cite the Forward-porting section of `AGENTS.md` in place of `CLAUDE.md`. Add an assertion to `tools/tests/test_lean_prd_refresh.py` that the PRD does not contain the phrase back-port source and does name `forward-port.sh`, so the inverted statement cannot return.

## Acceptance Criteria

- [ ] **AC1** Given the Context paragraph of section 2 of `sdlc-studio/prd.md`, when it is read, then it says this repository is the source, that fixes land here and are mirrored to the installed copy by `tools/forward-port.sh`, and cites the Forward-porting section of `AGENTS.md`. Fails on: the phrase back-port source, or a PRD that does not name `forward-port.sh`.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::PrdRefreshTests::test_the_context_names_forward_port_as_the_direction_of_flow

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
