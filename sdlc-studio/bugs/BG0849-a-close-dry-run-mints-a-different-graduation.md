# BG0849: A close dry run mints a different graduation change request id each time, so a retro cannot rule it before the close

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_graduation_ruling.py, .claude/skills/sdlc-studio/help/sprint.md, changelog.d/BG0849.md
> **Depends on:** BG0826, BG0851
> **Created:** 2026-09-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-29T08:37:44Z

## Summary

`sprint.py close --dry-run` reports the lesson-graduation change request it would file (LC-002 graduating -> CR01M3P4PW), and the next dry run names another id (CR01M3P45Z), and the real close a third (CR01M3P45S). A retro's `## Known issues carried` table cannot rule an id nobody can predict, so the new CR is always handed over UNRULED. Seen on the sdlc-studio.com web run RUN-01M3HRHY.

## Steps to Reproduce

Reproduced at HEAD 46cb9acf on 2026-09-30 in a throwaway git tree built from the lean close fixture, with `schema_version: 3` (ULID ids), a lesson store holding LC-900 active with two repeats after its recording run, and a retro carrying `> **Run:**`, `> **Batch:**` and an empty `## Known issues carried` table:

1. `sprint.py close --dry-run --retro RETRO0001`: `LC-900 graduating -> CR01M3SGQQ`.
2. The same again: `LC-900 graduating -> CR01M3SGRE`.
3. `sprint.py close --retro RETRO0001` (chain stubbed green except `retro-extract` and `checklist`): `LC-900 graduating -> CR01M3SGBH`, and the checklist hands it over: `UNRULED CR01M3SGBH - an open finding nobody ruled on is not a carried issue, it is one nobody looked at`.

On a sequential-id project (no `schema_version: 3`) all three name CR0001, so the defect is the ULID minting; schema 3 is what `init` gives a new project. The id is minted by `file_finding` inside `lessons.close_pass` at the moment of filing, and the dry run files into a scratch copy, so no run can know the id before the close. The class code (LC-900) is the one stable name all three print.

## Proposed Fix

Let a retro rule a graduation CR by its lesson class, through the link the lesson store already keeps: when the close graduates a class, `lessons.close_pass` writes the CR's id onto the class's row (`state: graduating`, `cr: CR01M3...`), and the report's Lessons table already prints it as `graduating (CR01M3SG5P)`. A `## Known issues carried` row whose id is `LC-nnn` (`retro.carried_issues` accepts the code) rules the CR that the store names for that class; `_ck_known_issues` resolves the code through the store before it joins the rows to the run's open findings. No new field on the CR and no change to `file_finding.py` or `lessons.py`: a second copy of a link the store holds is a hand-kept pin [LC-008]. A graduation CR nobody ruled stays UNRULED, and its row names the class to rule it by. Deterministic ULIDs are not attempted: an id minted ahead of its filing time breaks the ordering the ids carry.

## Acceptance Criteria

- [ ] **AC1** Given a schema 3 run whose close graduates LC-900 and whose retro's `## Known issues carried` table rules `LC-900` as not-stop-ship, when `sprint.py close --dry-run` and then `sprint.py close` run, then neither reports the graduation CR UNRULED, the known-issues row the close records counts it ruled, and the lesson store's LC-900 row names the CR the close filed. Fails on: HEAD, where the close reports `UNRULED CR01M3...` because the retro's row id matches nothing; on a fix that keeps ids stable only within one process, which the dry run's scratch copy never shares; and on a join that reads the CR's title for the class, which a CR retitled in grooming defeats (the test retitles it)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_graduation_ruling.py::GraduationRulingTests::test_a_retro_rules_the_graduation_cr_by_its_class
- [ ] **AC2** Given the same run with no row for LC-900, when `sprint.py close` runs, then the graduation CR is still reported UNRULED, and the row names both the CR's id and LC-900. Fails on: a fix that drops graduation CRs from the known issues, which hides a CR nobody ruled; and on HEAD's row, which names the id alone
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_graduation_ruling.py::GraduationRulingTests::test_an_unruled_graduation_cr_names_its_class

## Impact

Every close that graduates a lesson hands over one known issue nobody could have ruled, which trains readers to ignore UNRULED.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-29 | sdlc-studio | Filed |
| 2026-09-30 | sprint planning | Groomed: premise re-run at HEAD - holds on a schema 3 (ULID) project (dry runs CR01M3SGQQ and CR01M3SGRE, close CR01M3SGBH, UNRULED), not on sequential ids (CR0001 each time); fix chosen as ruling by lesson class; two executable criteria (a class row rules the CR; an unruled one names its class); Affects: lessons.py, retro.py, sprint_report.py, help/sprint.md, a lean test and the fragment (sprint.py and test_sprint.py dropped); Points 2 to 3. |
| 2026-09-30 | sprint planning | Goal review round 2, finalised by hand: the ruling resolves the LC code through the link the lesson store already records (`cr` on the graduating row), not a new `Lesson class` field the filer would have to write [LC-008]; lessons.py dropped from Affects (no file_finding.py either); AC1 retitles the CR so a title-reading join fails; Depends on BG0826 (the scaffolded table) and BG0851 (its AC4 guards signed pages against a new counting rule). |
