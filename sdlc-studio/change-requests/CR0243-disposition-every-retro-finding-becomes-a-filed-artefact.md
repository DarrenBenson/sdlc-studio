# CR-0243: Disposition: every retro finding becomes a filed artefact or a recorded decline

> **Status:** Proposed
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Provenance:** RFC0032 D1
> **Raised-by:** sdlc-studio; agent; v1
> **Priority:** P1
> **Type:** feature

## Summary

No retro finding has ever become a Bug or CR: `file_finding.py` is wired to review and never to retro. In sdlc-studio-lens, 9 retros carry a Lessons section and reference exactly 1 artefact id between them. Wire `file_finding` into retro, and add a BLOCKING gate leg: each finding must be filed (BG/CR) or declined with a reason. Declining is equally green, so honesty costs what noise costs and there is nothing to game. Untouched prose blocks the close.

## Impact

{{who this affects and what breaks}}

**Effort:** {{S|M|L}}

## Acceptance Criteria

- [ ] A retro finding can be filed as a Bug or CR via `file_finding.py`, as review already does. Verify: rg -q 'retro' .claude/skills/sdlc-studio/scripts/`file_finding.py`
- [ ] A new gate leg BLOCKS a sprint close when a retro finding is neither filed nor declined. Verify: rg -q 'disposition' .claude/skills/sdlc-studio/scripts/gate.py
- [ ] A finding declined WITH a recorded reason passes the gate - decline is a first-class disposition, not a workaround. Verify: python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k gate
- [ ] The gate leg is validated against the bug it defends (LL0010): a retro with an undispositioned finding must FAIL before the leg is trusted. Verify: python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -k disposition

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
