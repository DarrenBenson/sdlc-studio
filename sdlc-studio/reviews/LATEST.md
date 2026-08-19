<!-- close-status:begin -->
> **RUN-01M0ATVZ closed goal-reached.** 4 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **Run of record:** RUN-01M0ATVZ - a BUILD rung under SC0006. Four groomed bugs from the open
> backlog, delivered file-disjoint: BG0584, BG0585, BG0589, BG0590. All four are Fixed with
> adversarial evidence recorded. **Reviewer-of-record sign-off is OWED and is the operator's** -
> `critic signoff` refuses a principal the authoring session controls, which is the gate working.

## THE HEADLINE: THE CODE WAS RIGHT, THE EVIDENCE WAS NOT

Six review rounds across five units. **Every rejection but the first was a defect in a repair, not
in the original work** - and in three of four units the reviewer found the production code correct
and the tests unable to fail.

The clearest case: a seat enumerated every criterion-line spelling in the real corpus, confirmed
the BG0585 detector judged all of them correctly, then rejected the unit because three of its six
criteria were verified by tests that proved nothing.

- A control asserted lower-case `the` against a case-sensitive matcher, so it read False whether
  or not the fix over-reached, and the criterion's own declared mutant **survived all 6603 tests**.
- A census test resolved the repository root to `.claude/`, so its glob matched nothing and every
  assertion was skipped. **It measured nothing while reporting green.** Third instance of that
  shape this session.
- A wiring criterion named `sprint.py plan` and drove `breakdown` - read-only, exits 0 - so no
  refusal was ever asserted.

## WHAT THE NEXT SESSION SHOULD READ FIRST

**BG0592 is open, rejected FOUR times, and escalated twice.** Its diagnosis was right from round
one; every subsequent rejection was of the repair. Round 2 found a project-declared status bought a
silent exemption; round 3 found the repair of THAT reintroduced the false green the unit indicts
(`3/3 green` printed beside `2 failing`); round 4 found the fixture could not see a numerator
counting manual criteria as green, because every story in it had `manual=0`.

**Its `Verification depth` field has now been wrong five times running** - criterion counts, mutant
counts, and a claim of CLI coverage that did not exist. Read that field with suspicion, and prefer
`mutation.py run --story <id> --from-plan`, which reports from the ledger rather than from prose.

**Two numbers moved under measurement and both corrections were themselves wrong**: the retro
bullet style ("every retro carries asterisks" - measured 102 dash, 3 asterisk of 105) and the
grooming census (13 -> 17, briefly 18 while a newly filed bug sat ungroomed). A false premise
restated reads as verification, which is why it is worse than the original.

## THE GATE BUDGET IS BIMODAL, AND THE FIGURE YOU SEE IS SELECTION WIDTH

`total.selected` is two populations, not one series: ~1,400 tests selected costs ~212s, ~5,100
costs ~540s, at a stable 0.105-0.171 s/test throughout. The declared 380s ceiling sits BETWEEN the
modes, so it is wrong about both, and the lane reports the LATEST row rather than the series.

An earlier reading of this took the three most recent 212s rows as the current cost and proposed
re-baselining DOWNWARD. Two gate runs minutes later measured 535s and 554s. **The guard that
refused that change was right; the premise was mine.** Filed as BG0594. The full suite - not the
per-commit gate - is what genuinely grew, ~630s to ~921s, and nothing watches it.

## OPEN, AND WHY

| Id | State |
| --- | --- |
| BG0592 | Open. 4 REJECTs, escalated. Diagnosis sound, repair not converging |
| BG0593 | Open. `close --dry-run` previews against a scratch tree with no `.git`, so every git-reading row degrades to unjudged. Confirmed here: `tick-verification` reads `diff unreadable` under `--dry-run` and `24 ticked criteria supported` outside it |
| BG0594 | Open. The budget lane watches the per-commit gate only, against a bimodal population |
| BG0595 | Open. The commit-msg hook test is not hermetic, so the full suite goes red whenever work is in flight. Verified by stash: same code, clean passes, dirty fails |
| BG0596 | Open. `_testplan_rows` keys by criterion, so a second mutant on the same AC is silently dropped and `--from-plan` reports every one killed over rows it never joined |
| CR0511 | Open. `artifact._wire_story_to_epic` locates its insertion point with a hardcoded dash |

## WHAT THIS RUN CHANGED THAT EVERY LATER RUN INHERITS

- **The `derived-only` grooming limb works for the first time since 2026-08-06.** It had been
  reachable by nothing for twelve days, so the scaffold that reads like content passed every gate.
  Two currently-open bugs, BG0578 and BG0581, are newly unplannable as a result. That is the gate
  working, and it is a real cost to price.
- **A `design` rung can close without waiving a row it cannot answer.** D0145 retracts D0144.
- **`sprint close` no longer makes the tree uncommittable after reporting success.**
- **39 mutants are executed and REGISTERED through the shipped tool** rather than asserted in
  prose. Two reviewers found the prose record false where they re-ran it.

## PRACTICE WORTH CARRYING

**A detector's silence is evidence only once it has been shown able to speak.** The markdownlint
helper caught a missing binary and not a missing package, so it handed `npm ERR! 404` to an
`assertNotIn` and four criteria's lint half was inert in any clone without `npm ci` - while both
its docstring and the depth field said "skipped, never faked". It now lints a known-bad file first.

**Scope a rung fix to the rung it is about, never to "not `done`".** Done twice now: BG0582's
siblings were rejected for it, the ruling was written into `sprint.py` twice, and BG0584 made the
same mistake again with those comments in the file.

**Register mutants after the last edit.** An earlier pass was silently dropped when the files
changed under it, exactly as BG0550 records.
