# CR-0293: US0166 AC3's Verify checks one cosmetic string in one of the two required files, and is a mis-written DSL line that passes only by flag-reinterpretation accident

> **Status:** Complete
> **Decomposed-into:** EP0075
> **Priority:** Medium
> **Type:** process
> **Size:** S
> **Affects:** sdlc-studio/stories/US0166-ship-a-stop-hook-installer-and-redefine-sprint.md, .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

AC3's Then requires BOTH reference-retro.md and help/gate.md to state the Definition-of-Done close clause and the --require-close/Stop-hook enforcement; the Verify is `grep -q "never at .deployed" .claude/skills/sdlc-studio/help/gate.md` - one file, a slogan, neither required clause, so reference-retro.md's compliance is unguarded coincidence (LL0013). It is also the only Verify in the batch missing the `shell` prefix: it parses under `verify_ac`'s grep DSL verb with pattern='-q' and passes only because rg/grep re-parse the mis-slotted argv '-q' as a flag - the panel executed the parse and confirmed ['rg','-q','-q','never at .deployed', gate.md]. It would break the moment the grep verb validates its pattern. A committed-Done story whose Verify reconcile --verify re-runs. Verified 3x.

## Impact

AC3's Then requires BOTH reference-retro.md and help/gate.md to state the Definition-of-Done close clause and the --require-close/Stop-hook enforcement; the Verify is `grep -q "never at .deployed" .claude/skills/sdlc-studio/help/gate.md` - one file, a slogan, neither required clause, so reference-retro.md's compliance is unguarded coincidence (LL0013).

## Acceptance Criteria

- [ ] AC3's Verify rewritten as shell command(s) checking both files for the close clause and the --require-close/Stop-hook enforcement text
- [ ] The bare (non-shell) grep line corrected so no Verify passes via a dash-leading pattern accident
- [ ] Optional hardening: `verify_ac`'s grep verb refuses a pattern beginning with '-'

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Raised |
