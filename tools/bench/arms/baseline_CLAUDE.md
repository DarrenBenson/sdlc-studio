# CLAUDE.md

Guidance for Claude Code working in this repository.

## Working style

- Read the relevant existing code before changing it. Understand the current behaviour and
  conventions before writing new code that has to fit alongside them.
- Prefer small, focused changes over broad rewrites. Don't refactor code you weren't asked
  to touch.
- Match the existing code style (naming, structure, error handling) rather than imposing a
  different one.

## Before you finish a task

- Write a test that exercises the behaviour you changed, if the codebase has a test suite.
  Prefer a test that would fail before your change and pass after it - that's the proof the
  fix (or feature) actually works, not just that it looks right.
- Run the full test suite before declaring the task done, not just the test you added. A
  change that passes its own test but breaks something else is not finished.
- Re-read the original request once more before finishing, and check every part of it is
  actually addressed - partial completion of a multi-part ask is a common failure mode.
- Think about edge cases the request implies even if it doesn't spell them out: empty
  input, boundary values, malformed input, and any case a careless reading would skip.
  Don't add handling for cases that were not asked for and cannot occur, though - extra
  unrequested scope is also a failure mode, not a virtue.

## Verification

- Never claim a task is complete without having actually run the tests and seen them pass.
  If you cannot run something, say so explicitly rather than asserting success.
- If a test fails, investigate the actual root cause before changing anything - don't guess
  at a fix and hope it happens to pass.

## Communication

- Be direct and concise. State what you changed and why, not a narrated log of every step.
- If the request is ambiguous in a way that changes what "done" means, ask, rather than
  guessing and hoping.
