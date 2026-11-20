# BG1663: BG1655 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py, changelog.d/BG1663.md
> **Created:** 2026-11-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-20T10:55:35Z

## Summary

BG1655 was rejected at round 2, the review cap, by agent-aacb9598745fe99e9 (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] The repair leaves the rule's definition false: reference-persona.md:472, the row best-practices/persona.md names as where a rule's definition lives, still gives `the Primary persona, Sam` and `Sam (Primary)` as claims that warn when no card names Sam, and still says "a word opening a clause after a colon is no name". At cfb2a4fd both Sam forms print nothing through `validate.py seats --format json` (each warned at ff97be63), and a two-word run after a colon warns, so the row describes neither D0554's two-word rule nor D0556's bracket form. `git log -S` puts the colon clause in ff97be63 and the Sam examples in a011a415, both true until this repair. The fix is one row, with reference-persona.md added to BG1655's Affects [LC-018]; [pre-existing] BG1662 Two capitalised words before a bracketed role still read as an unknown persona: `Ship the Admin Console (Primary) first.` and `Serve Power Users (Primary) first.` each warn `seat-persona-unknown` at cfb2a4fd and at ff97be63, the second naming `Serve Power Users` because a bullet's capitalised opening verb joins the run (validate.py:1607). The second form adds to BG1662's evidence.; RULINGS: Prior finding "An unknown full name after a colon no longer warns" CLOSED: `Primary persona: Zed Quill` and `Ask the Primary persona: Zed Quill would refuse this.` each warn naming Zed Quill at cfb2a4fd, and restoring the colon skip in `_reads_as_name` fails the suite. Prior finding "Residual misreads in the class the bug names" CLOSED for the pronoun, conjunction, `Not`, `Speed` and `Web UI` lines (each silent at cfb2a4fd, pinned by AC4), MOVED for `Ship the Admin Console (Primary)`, now BG1662 and reported above. Prior finding "`_reads_as_name` reads only a run's first word" CLOSED: reading `words[-1]` is killed by `The Admin Team`, a lone initial taken for an acronym by `Zed J Quill`, and a first-word-only acronym guard by `Web UI`. Re-executed: verify\_ac dry-run 4 of 4 pass, `test_validate_seats_cast.py`, `test_shipped_card_passes_standard.py`, `test_persona_standard.py` and `test_validate.py` 213 passed under pytest, the first two OK under unittest, and nine mutants of `_reads_as_name` all killed (colon skip restored, last word read, lone initial as acronym, first-word acronym guard, bracket form dropped, bracket not held to its close, bracket read for the trailing role, two-word run no name, every lone word read), with the clone's tree clean after. Claim inventory: the commit's and fragment's cases are TRUE by probe, and the fragment's opening "no longer warns over ordinary prose" is still OVER-CLAIMED by BG1662's form. Remarks, not findings: title-case placeholders after a colon (`Primary persona: Not Yet Chosen`, `Primary persona: To Be Decided`) warn at cfb2a4fd and were silent at ff97be63, which D0554's two-capitalised-words rule accepts. A lone unknown name outside brackets going silent is D0554's ruled trade-off.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1655 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1655 again in a later run.

## Acceptance Criteria

- [ ] **AC1** Given `reference-persona.md`'s `seat-persona-unknown` row, when its stated rule and each backticked example in it are run through `validate.py seats` against a fixture cast, then the row states the shipped rule (a name is read only where a run resolves to a cast member, is two or more capitalised words, or is a lone word in brackets after a role, per D0554 and D0556) and every example warns or stays silent as the row says
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py::ReferenceRowTests::test_the_seat_persona_unknown_row_examples_behave_as_stated
- [ ] **AC2** BG1655 AC1 still passes: Given a cast of Maya Okafor (Primary) and a seat card holding `Ask the Primary persona: Is it simpler?`, `the Primary persona: When they arrive` and `Serve the CLI (Primary) before the web UI`, when `validate.py seats` runs, then it prints no `seat-persona-unknown` finding; and a card holding `the Primary persona, Zed Quill` still warns `seat-persona-unknown` naming Zed Quill
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py::SeatClaimNameTests::test_a_word_after_the_role_that_is_no_name_is_not_read_as_one
- [ ] **AC3** BG1655 AC2 still passes: Given the cast holds only Maya Okafor, when a seat card says `the Primary persona is Maya Smith`, then `validate.py seats` warns `seat-persona-unknown` naming Maya Smith, while `the Primary persona is Maya` and `the Primary persona is Maya Okafor` resolve with no finding
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py::SeatClaimNameTests::test_a_first_name_with_the_wrong_surname_is_unknown
- [ ] **AC4** BG1655 AC3 still passes: Given a `personas/index.md` that omits Hana Ito while her card's Cast role is Primary, when a seat card says `the Secondary persona, Hana`, then `validate.py seats` warns `seat-persona-role` naming Primary and Secondary
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py::SeatClaimNameTests::test_a_card_the_registry_omits_is_role_checked_against_its_card
- [ ] **AC5** BG1655 AC4 still passes: Given a cast of Maya Okafor and Jonah Reyes and a seat card holding `As the Primary persona, I want a quick start.`, `Lead with the Primary persona, She decides.`, `the Primary persona, If pressed`, `the Primary persona, Then the rest` and `the Primary persona is Not yet chosen`, when `validate.py seats` runs, then it prints no `seat-persona-unknown` finding; and `Primary persona: Zed Quill` and `Ask the Primary persona: Zed Quill would refuse this.` each warn `seat-persona-unknown` naming Zed Quill, and `the primary persona (Darren)` still warns naming Darren (D0554, D0556)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate_seats_cast.py::SeatClaimNameTests::test_only_a_cast_name_or_a_full_name_run_is_read_as_a_name

AC1 must fail on: a row that keeps an example the rule no longer warns on (a lone unknown first name such as `the Primary persona, Sam`), or a test that checks the row's wording without running its examples. BG1662 (a two-word product surface before a bracketed role) is a separate Low and not this bug's to fix.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-20 | sdlc-studio | Filed |
