<!-- close-status:begin -->
> **RUN-01M1H09S closed goal-reached.** 4 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **Run of record:** RUN-01M1H09S - the criteria a unit is judged on can be EXECUTED, and the
> instruments that judge them report one number each. Four units, 20 criteria, 22 mutants all
> killed. Goal **achieved**, all seven clauses measured. Release bar MET.

## THE HEADLINE: THE FILER COULD WRITE A CRITERION BUT NOT ITS VERIFIER

`file_finding.py file` - the command this project's doctrine names for filing every finding -
exposed `--ac` and nothing to pair with it. There was **no route to an executable acceptance
criterion for a bug**. `artifact.py new` appears to offer the model and does not: `--verify` is
story-only there and is silently dropped.

So the criteria the filer wrote carried no `Verify:` line; `verify_ac` reported nothing could be
executed; and the Done gate was inert *precisely because* zero verifiers were declared. A unit
reached a terminal status on a hand-stamped `Verification depth` with no criterion ever run.
`unit_is_ungroomed` asked whether a criterion was WRITTEN and never whether it could be CHECKED,
so `sprint plan` called such units plannable.

**It was found by the planning ceremony, not by a user.** A seven-unit batch was proposed for
this slot; a plan review found all twenty-five of its criteria unexecutable and refused the batch.

`sprint plan` now reports **9 ungroomed** over the same corpus that read **0** that morning. That
is the accepted cost, visible rather than forecast: 12 of 19 open bugs need a real verifier before
they can be planned.

## WHAT TO READ BEFORE THE NEXT RUN

**Three of the seven originally proposed units did not reproduce.** BG0634's stated cause never
existed; BG0631's two filed shapes both passed on HEAD; BG0632's link half had been fixed by
BG0619. Re-running every premise against HEAD before coding is what caught it. BG0631 was
re-groomed onto the collision case that *does* reproduce rather than closed.

**A regex run to fix three code spans rewrote 57 files.** MD038 flagged three spans in one
artefact; the pattern was written over every code span in `bugs/` and `changelog.d/`, modifying 39
bug artefacts and 18 changelog fragments from earlier runs. Caught immediately and fully restored,
because all 45 were committed - git saved it, not judgement. Then the restore was *also* too wide
and reverted this batch's own index rows, blocking the next commit on 17 rows of drift. **The same
error twice in ten minutes: a broad action where a narrow one was called for.** When the target is
enumerable, enumerate it.

**`npm run lint` passed while the commit hook refused.** The strict markdown rules over `bugs/`
run in the hook, not in `lint`. A locally green lint says nothing about the gate.

## WHAT THE NEXT RUN PICKS UP

**First question: the 12 of 19 open bugs that now need a real verifier before they can be
planned.** `sprint plan` refuses them - that is BG0636 working and the cost the operator accepted
on 2026-09-02. Grooming them is unestimated work sitting between this run and the next delivery
batch, and **BG0643 is why it will hurt**: the `--verify` flag this run shipped is refused for a
selector naming a test that does not exist yet, which is every bug filed before its fix. Three
findings filed after BG0636 landed had to be filed without the flag and hand-edited afterwards.
Fix BG0643 before grooming twelve units by hand.

**Then the newly filed set**, all ruled not-stop-ship:

- **BG0643** - `--verify` unusable for the case it exists for. Blocks the grooming above.
- **BG0637** - `_clean` escapes underscores inside code spans: 655 corrupted identifiers across
  the three review ledgers, 442 already double-escaped.
- **BG0638** - five sprint-checklist rows state conclusions they never established, and
  `_ck_known_issues` fails open where its sibling reports the same blindness as UNANSWERED.
- **BG0644** - the test-noise ratchet compares a SELECTED subset against a whole-suite
  baseline, so a commit that adds leaks passes the gate that is supposed to fail it. This
  run demonstrated it: 37 new leaks passed every commit and turned CI red on main.
- **BG0640** - the revert-check lane reports a clean pass when it examined nothing.
- **BG0641** - there is no `pre-push` hook, so `release-rehearsal` and `revert-check` bind at a
  boundary with nothing behind it, though AGENTS.md says they bind at push and release.
- **BG0642** - the required status check never reports at push time, so every push to main
  bypasses branch protection. Main was red for two days on 2026-09-01 and nobody read it.
- Carried: CR0511, CR0562, BG0627, BG0630, BG0633.

**CI was RED on main and the fix is in this commit.** The two warnings BG0636 and BG0631 shipped
fire from inside library calls that most fixtures make in passing, leaking 37 diagnostic lines
into a green suite. `tools/skill-tests.sh` fails a passing run that printed anything, so the full
run in CI refused at 142 against a baseline of 119 - while every commit that added the leaks
passed, because the hook checks an absolute count over a selected subset. The 24 sites now capture
through `tests/quiet.py`, the full suite measures 106, and the ratchet is lowered to match.

**Conformance is 732/814 with ZERO non-conformant**, reached on truth rather than a waiver: the
seven US0569-US0576 stories and US0674 each carry a recorded resolution, closing what was
verified at HEAD and carrying the residue to BG0640 and CR0552.

## OPEN

**BG0637** - `_clean` escapes underscores inside code spans, corrupting 655 identifiers across the
three review ledgers, 442 already double-escaped. **BG0638** - five sprint-checklist rows state
conclusions they never established, and `_ck_known_issues` fails open where its sibling reports the
same blindness as UNANSWERED. Both were found by reviews whose rejections had stood unanswered
since 2026-07-31.

**US0674 is the one unit that moved the wrong way** and is reported rather than repaired: its
legacy repair rows answer their rejection in substance but not mechanically, and attributing them
anyway is the guessing BG0631 AC4 exists to refuse.

Also open: CR0511, CR0562, BG0627, BG0630, BG0633.
