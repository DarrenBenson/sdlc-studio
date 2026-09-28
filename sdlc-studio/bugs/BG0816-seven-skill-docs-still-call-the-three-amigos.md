# BG0816: Seven skill docs still call the Three Amigos by retired names, and AGENTS.md names a seat directory that does not exist

> **Status:** In Progress
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/reference-bug.md, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-consult.md, .claude/skills/sdlc-studio/reference-chat.md, .claude/skills/sdlc-studio/help/persona.md, .claude/skills/sdlc-studio/help/consult.md, AGENTS.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_amigo_names.py, changelog.d/BG0816.md
> **Evidence:** BG0814 build hand-back 2026-09-28; grep -rln 'Sarah Chen|Marcus Johnson|Priya Sharma' over the skill's .md files lists seven docs plus reference-workflow-personas.md (fixed by BG0814); ls .claude/skills/sdlc-studio/personas fails
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T11:14:50Z

## Summary

BG0814's builder found, and grep confirms at d8973d6f, the retired amigo names Sarah Chen, Marcus Johnson and Priya Sharma in reference-bug.md, reference-persona.md, reference-review.md, reference-consult.md, reference-chat.md, help/persona.md and help/consult.md. The resolver (`persona_resolve.py` resolve --seat <s> --render review) seats Lena Marsh (product), Dani Okafor (engineering) and Sam Eriksson (qa) from templates/personas/amigos/. An agent reading those docs looks for amigos the skill never loads, the same persona-versus-seat confusion eval 02 caught. AGENTS.md's 'Where things live' table names .claude/skills/sdlc-studio/personas/seats/, which does not exist. Some mentions may be deliberate sample USER personas rather than amigos; those stay.

## Steps to Reproduce

grep the skill docs for the three names; resolve each seat with `persona_resolve.py` and compare; ls the path AGENTS.md names.

## Proposed Fix

Where a doc means the Three Amigos, use the role labels the resolver prints (Product amigo, Engineering amigo, QA amigo) or the seat names it loads, and name the resolver once where useful; leave a name only where it is a sample user persona and say so. Correct AGENTS.md's seat path to templates/personas/amigos/.

## Acceptance Criteria

- [ ] **AC1** Given the skill's docs, then no passage that means the Three Amigos names Sarah Chen, Marcus Johnson or Priya Sharma, and each remaining mention of those names is marked as a sample user persona. Fails on: the rc.1 docs, where Bug Fix, review, consult and chat steps name amigos the resolver never loads
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_amigo_names.py::AmigoNameTests::test_no_amigo_passage_names_a_retired_seat
- [ ] **AC2** Given AGENTS.md's 'Where things live' table, then the row for the amigo seats names a directory that exists and that `persona_resolve.py` loads. Fails on: personas/seats/, which does not exist
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_amigo_names.py::AmigoNameTests::test_agents_md_names_the_real_seat_directory

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
