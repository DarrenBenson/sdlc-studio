# BG1655: seat-persona-unknown reads a capitalised word after a seat card's role phrase as a persona name, and US1052's standard makes the rule block

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, changelog.d/BG1655.md
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T06:51:14Z

## Summary

US1046's qa seat (verdict sdlc-studio/reviews/verdicts/US1046/1d25a043db72-9aa2818d.txt, RUN-01M7VNR0). `_CLAIM_NOT_NAMES` (validate.py:1582) lists only articles and determiners, so 'Ask the Primary persona: Is it simpler?' warns seat-persona-unknown naming Is, 'the Primary persona: When they arrive' names When, and 'Serve the CLI (Primary) before the web UI' names CLI. US1052's persona standard lists seat-persona-unknown as blocks, and US1055 gates a run on blocking rules, so ordinary prose on a valid seat card would refuse a run. The same verdict found two more gaps in `_resolve_claim`: the first-name fallback (validate.py:1620-1625) accepts a wrong surname (the Primary persona is Maya Smith passes when the cast holds only Maya Okafor), and a persona with a card but no registry entry is never role-checked (validate.py:1661-1663).

Groomed in run twenty: the fix changes what `validate.py seats` and the persona standard report, so it ships a changelog fragment.

## Steps to Reproduce

In a fixture whose cast is Maya Okafor, give a seat card the line 'Ask the Primary persona: Is it simpler?' and run validate.py seats: it warns seat-persona-unknown naming Is.

## Proposed Fix

Read a persona name only where a capitalised token is followed by a cast surname or stands alone as a cast first name; never read a word after a colon, a question word or an acronym as a name; and refuse a first-name match whose stated surname differs.

## Acceptance Criteria

- [ ] **AC1** Given a cast of Maya Okafor (Primary) and a seat card holding `Ask the Primary persona: Is it simpler?`, `the Primary persona: When they arrive` and `Serve the CLI (Primary) before the web UI`, when `validate.py seats` runs, then it prints no `seat-persona-unknown` finding; and a card holding `the Primary persona, Zed Quill` still warns `seat-persona-unknown` naming Zed Quill
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py::SeatClaimNameTests::test_a_word_after_the_role_that_is_no_name_is_not_read_as_one
- [ ] **AC2** Given the cast holds only Maya Okafor, when a seat card says `the Primary persona is Maya Smith`, then `validate.py seats` warns `seat-persona-unknown` naming Maya Smith, while `the Primary persona is Maya` and `the Primary persona is Maya Okafor` resolve with no finding
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py::SeatClaimNameTests::test_a_first_name_with_the_wrong_surname_is_unknown
- [ ] **AC3** Given a `personas/index.md` that omits Hana Ito while her card's Cast role is Primary, when a seat card says `the Secondary persona, Hana`, then `validate.py seats` warns `seat-persona-role` naming Primary and Secondary
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py::SeatClaimNameTests::test_a_card_the_registry_omits_is_role_checked_against_its_card

AC1 must fail on: a stop list of the three test words, so another question word or acronym after the role is still read as a name (the Zed Quill control keeps a real unknown name warning). AC2 must fail on: any first-name match passing whatever surname follows. AC3 must fail on: a name the registry omits skipping the role check.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
