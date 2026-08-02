# BG0478: artifact.py new mints a CR the commit gate then refuses, so the recommended path is the blocked one

> **Status:** Fixed
> **Verification depth:** functional (both severity cases pinned through validate_file; the new-command report verified through the CLI on a real mint, and the probe artefacts removed)
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Provenance:** agent
> **Raised-by:** Claude Opus 5; human; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/templates/core/change-request.md, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Severity:** High
> **Points:** 3

## Summary

`artifact.py new --type cr --fields-file ...` is the path AGENTS.md names and the path the tool's own help calls RECOMMENDED. It writes an Acceptance Criteria section containing the literal placeholder, and validate.py then raises `[placeholder] unresolved placeholder in acceptance criteria`, which is an ERROR, not a warning. So the gate blocks the very next commit.

The author has to hand-edit an artefact the tool just wrote before the tool's output is acceptable to the repo. That is the hand-authoring CR0515 exists to make visible, induced by the deterministic path rather than avoided by it. It is also invisible until commit time: `new` exits 0 and reports `created CR-0518`, so nothing at the point of creation says the artefact is not yet valid.

Measured this run: filing CR0518 through the recommended path produced exactly one validation error in the whole workspace, and it was the artefact just created.

## Steps to Reproduce

1. python3 .claude/skills/sdlc-studio/scripts/artifact.py new --type cr --fields-file <any doc with title/summary/impact> -> exits 0, `created CR-xxxx`.
2. git add the new file; git commit -> gate FAIL, `[placeholder] unresolved placeholder in acceptance criteria`.
3. validate.py check -> 1 error, on the artefact `new` just wrote.

## Proposed Fix

Either `new` refuses to leave a placeholder that validate treats as an error (prompt for criteria, seed them from the summary, or emit an empty section validate reads as ungroomed-but-valid), or validate demotes an as-minted placeholder to the WARNING it already uses for other ungroomed states, so the two tools agree on whether a freshly created artefact is legal. They currently do not, and the disagreement is paid by whoever used the recommended path. Whichever way it resolves, `new` should say at creation time that the artefact still needs criteria, rather than reporting unqualified success.

## Acceptance Criteria

### AC1: a freshly-minted request's scaffold placeholder is a warning, not an error

- **Given** a CR at its opening status carrying the criteria placeholder
- **When** it is validated
- **Then** no error is raised, because a request that has just been minted is not-yet-written for exactly the reason a Draft story is - and the recommended path must not produce an artefact that blocks the next commit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::FreshArtefactPlaceholderTests::test_a_fresh_request_placeholder_is_a_warning
- **Verified:** yes (2026-08-02)

### AC2: a request past its opening status still errors

- **Given** a CR being acted on that still carries the placeholder
- **When** it is validated
- **Then** it errors, because an unfilled criterion on work in flight is real debt and a rule that never errors is not a rule
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::FreshArtefactPlaceholderTests::test_a_request_past_its_opening_status_still_errors
- **Verified:** yes (2026-08-02)

### AC3: `new` says the artefact is not finished

- **Given** `artifact.py new` minting an artefact whose criteria are still the scaffold
- **When** it reports
- **Then** it states the criteria are unwritten, rather than reporting unqualified success and sending the author away from a document that still needs writing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::FreshArtefactPlaceholderTests::test_the_warning_is_printed_by_the_shipped_command
- **Verified:** yes (2026-08-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | Claude Opus 5 | Created via `new` (deterministic) |
