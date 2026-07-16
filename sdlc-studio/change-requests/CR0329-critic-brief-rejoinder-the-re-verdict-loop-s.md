# CR-0329: critic brief --rejoinder: the re-verdict loop's scaffolding emitted deterministically from the prior verdict

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; seams-sprint retro RUN-01KXPA4N

## Summary

CR0316 made the FIRST review's scaffolding deterministic; the re-verdict loop is still prose. Add `critic brief --unit X --seat qa --rejoinder <prior-verdict-file>`: emits the re-review brief - the prior VERDICT/ISSUES/BLOCKING quoted verbatim, the diff scope refreshed, an explicit instruction to RE-EXECUTE the prior probes and mutants (the vacuous-killing-test lesson made structural), and the same return contract. The author still writes the repairs summary; the scaffolding and the re-run-your-mutants demand stop being optional.

## Impact

Five REJECT-repair cycles this sprint each needed a bespoke hand-written re-review message (quote the prior ISSUES, list the repairs, restate the contract, instruct re-running the mutants); the scaffolding is identical every time and drift in it is what lets a vacuous repair slip.

## Acceptance Criteria

- [ ] brief --rejoinder emits the prior verdict block verbatim plus the re-execute-your-probes instruction and the return contract; a malformed prior-verdict file is refused
- [ ] The rejoinder brief instructs the reviewer to re-run previously named mutants/probes before approving - the lesson from the two vacuous killing tests, in the ceremony not just the lore

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
