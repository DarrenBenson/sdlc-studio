# US1066: Another seat approves or rejects each proposed learning against its evidence and its card

> **Status:** Ready
> **Delivers:** CR0633
> **Created:** 2026-10-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/persona_memory.py, .claude/skills/sdlc-studio/reference-persona-learning.md, .claude/skills/sdlc-studio/reference-retro.md, .claude/skills/sdlc-studio/help/persona.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_approve.py, .claude/skills/sdlc-studio/scripts/tests/test_doc_coverage.py, changelog.d/US1066.md, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0287
> **Points:** 5
> **Depends on:** US1058, US1062
> **Persona:** Abena Osei

## User Story

**As a** Maya Okafor, who wants a learning checked by someone other than the seat that wrote it
**I want** `persona_memory.py approve-brief` to brief a different seat with the learning, the seat's adverse items and the subject card's Non-Negotiables and Authority, and `persona_memory.py approve` to record its decision and which adverse items the learning addresses, refusing the learning's own seat
**So that** only a learning another seat has checked against the ledger and the card can go live, and a learning that dodges what went wrong is visible

## Acceptance Criteria

- **AC1:** Given a proposed qa learning M-0001, when `persona_memory.py approve --id M-0001 --reviewer "Lena Marsh (product)" --addresses round:US0001r2` runs, then it reads approved with Approved-by, the date and the item it addresses, while `--reviewer "Kit Devane (qa)"` exits 2 naming that a seat never approves its own learning, whoever holds it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_approve.py::ApproveLearningTests::test_another_seat_approves_and_the_same_seat_is_refused
- **AC2:** Given qa's record listing adverse items round:US0001r2 and bug:BG0002, when `approve` runs with `--addresses bug:BG0099`, with no `--addresses`, and with `--addresses none --reason "keeps a habit that held"`, then the first two exit 2 naming the listed items and the third is recorded with its reason.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_approve.py::ApproveLearningTests::test_an_approval_names_what_the_learning_addresses_or_says_why_not
- **AC3:** Given a proposed learning, when `persona_memory.py approve-brief --id M-0001 --seat product` runs, then it carries the learning verbatim, qa's adverse items with their keys, the qa card's Non-Negotiables and Authority sections, the question whether the learning contradicts or loosens them, the product card to adopt and the approve and reject commands, while `--seat qa` exits 2.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_approve.py::ApproveLearningTests::test_the_approval_brief_carries_the_evidence_and_the_subject_card
- **AC4:** Given a proposed qa learning, when `approve --id M-0001 --reviewer "Lena Marsh (product)" --reject --reason ...` runs, then it reads rejected with the reviewer and reason, and `critic.py brief --seat qa` does not carry it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_persona_memory_approve.py::ApproveLearningTests::test_a_rejected_learning_never_reaches_the_brief

## Notes

- Run thirteen grooming (D0479):
  - Persona: change Maya Okafor to Abena Osei (Primary). Serves End goal 2 (a different, accountable seat approves); End goal 4.
  - Dependency on US1065 is SOFT: approve needs a proposed entry, which US1058 `add` creates (state proposed) and a fixture can write; it needs the adverse-item keys from US1062 to validate --addresses. Real deps: US1058 and US1062. It still builds after US1065 in the same lane.
  - Four ACs and must-fail lines are sound; only pinning tests and the doc-coverage test are missing from Affects.
  - Line numbers in this story's notes are stale at HEAD (critic.py brief 2527->3755, `_lessons_block` 2358->3283, sprint.py `_CLOSE_CHAIN` 5668->5906, `cmd_sign` 9708->10474, retro.py extract 3535->4045, `lessons.phase_digest` 1864->1999, validate.py `check_personas` 1342->1278/1391); builder re-greps by name.
- Release: 6.3 (D0388; was 6.2) (D0355 breakdown G13, reviewed by the refine panel; see the request's revision history).
- AC1 must fail on: independence judged by reviewer name, so a second qa card holder approves qa's learning
- AC2 must fail on: an approval recorded with no account of which adverse item the learning engages, so a learning that addresses nothing reads as one that addresses everything
- AC3 must fail on: the approver briefed with the learning alone, so nothing compares a learning with the card it may drift from (ADR-012's drift risk)
- AC4 must fail on: a rejection recorded as a note while the entry stays eligible
- Serves: Maya Okafor #3.
- D3: another seat approves against the evidence; the operator's strike is the signature story. The panel's self-flattery guards (b) and (c) live here: the addressed items, and the card's Non-Negotiables and Authority with the question.
- A user persona's learning may be approved by any seat; its adverse items are its red End goals and missed or partial verdicts. A reviewer naming no `(role)` group, or a role no card declares, is refused; approving an entry that is not proposed is refused.
- Independence is by recorded seat; by context it needs US1014 and US1015 (later).
- Re-sized 3 to 5 for the addressed items and the card sections.

## Triage (2026-10-21)

Kept (D0387). To plan it:

- The D0374 stakeholder consult for EP0287 is owed before build
- Blocked on US1065 (Draft)
- The 'Release: 6.2' note is stale under D0382

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-12 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-09 | Claude Opus 5.5 (engineering seat) | Groomed from the D0355 breakdown G13 after the refine panel's review |
| 2026-10-21 | Claude Opus 5.5 | Triage, 2026-10-21 (D0387, D0388): kept and groomed - fields, criteria or notes corrected on the triage's evidence; see the Triage section where present |
| 2026-11-15 | Claude Opus 5.5 (run thirteen grooming, D0479) | Groomed for run thirteen: Persona Abena Osei, Affects with the existing tests that pin what it changes, Depends-on reduced to real dependencies, notes |
| 2026-11-15 | Claude Opus 5.5 (run thirteen planning, D0479) | Affects gains the registry files a new verb imply (the mechanics-verb list, the command surface): run twelve lost five lands to their absence |
