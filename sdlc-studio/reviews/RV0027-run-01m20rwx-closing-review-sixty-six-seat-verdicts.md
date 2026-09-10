# RV-0027: RUN-01M20RWX closing review: sixty-six seat verdicts, forty-four rejections, and one shape found nine times

> **Date:** 2026-09-10
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Scope

RUN-01M20RWX: 22 units, 72 points, base ref `98685d9f`. Every Medium open at that ref, plus
the four stories of CR0569 and CR0570.

Six independent seats reviewed the two commit groups - engineering, product and QA on each -
and three further seats reviewed test plans the terminal gate demanded. Sixty-six verdicts in
all, of which 44 were REJECT. Every seat ran `critic.py brief`, and every verdict carries its
brief fingerprint, because `critic record` refuses one that does not.

## Findings

**One shape, nine times: a criterion whose words go further than its fixture.**

- US0819 AC5 named three grep failures by name - a malformed pattern, a missing path, a glob
  matching nothing - and tested none of them. All three exit 2, which the probe read as `red`,
  the healthy class, on 126 verifiers in this corpus.
- US0819 AC8's test patched the reader it was about out of existence, so it asserted only that
  the helper's answer was honoured. The reader itself read commit SUBJECTS only, and a repo-wide
  census showed every one of the probe's 25 findings was a unit the same commit had delivered.
- US0821's two new CLI verbs were executed by no test: with the two-line dispatch deleted, all
  seven verifiers stayed green while `testplan rule` fell through to `testplan derive`, wrote a
  test plan into the artefact, recorded no ruling, and exited 0.
- US0821 AC7 required its values to round-trip and asserted that the WORD "pipe" survived a
  writer that replaced the character with a slash.
- US0822 AC8 said it judged a printed remedy by RUNNING it and read the source instead. Four
  remedies told a reader to run a command the tool now refuses, one of them printed by the very
  command that does the refusing.
- US0822 AC6's verifier named a class that does not exist - the only criterion of the nine that
  goes through the shipped lane.
- US0820 AC4's control was built on `not-probed`, a class the shipped code never emitted.
- BG0612 AC1 re-typed the predicate it was meant to exercise, so the whole edit-verb refusal
  could be deleted with the criterion green.
- BG0660 AC4's declared mutant stopped the function being a generator, so the test died on a
  TypeError before either assertion was reached.

**The deepest finding was structural, and a reviewer found it.** US0822 shipped anchored ledger
rows so an edit elsewhere in a shared file stops staling a unit's evidence. `plan_execution` -
the join `--from-plan`, the Fixed/Done gate and the depth deriver all read - still keyed on the
whole file's content hash, so the drift lane exonerated a row while the terminal gate demanded a
re-measure. The cost the unit exists to remove was still being paid at the one reader where it
hurts. Repaired, and measured on landing: 26 rows across three units moved from `not-run` to
counted, on files nobody had touched at their sites.

**Two blocking findings were refuted by execution rather than accepted.** BG0657's dead-stamps
count does not reproduce here - the shipped lane exits 0 with identities matching, and two other
seats read the same. BG0630's `--force` regression is over-claimed: the gate's entry call site
has never carried a force guard either, so making one firing waivable would let the same fact be
waived or refused by which route a caller took. Both are recorded as OVER-CLAIMED with the
commands that refute them.

**Three of the author's own mutant verdicts were retracted for the mirror-image reason** - each
applied to the wrong site, so it measured nothing whichever way it read.

## Verdict

**APPROVE, with every rejection answered on the record.** All 22 units reach a terminal
status: 18 bugs Fixed with their own verifiers passing, 4 stories Done through the close.

- 174 mutants registered for the batch, all killed, none surviving.
- 471 uncovered added lines ruled by id, almost all of them one artefact: four units changed
  `verify_ac.py` against one base ref, so the diff charges each with all 208 added statements.
- 113 criteria ticked against their own `Verified: yes` stamps - the close's tick-verification
  row had nothing to check before that, which is not the same as everything being supported.
- 38 open findings carried, each with a ruling and the reason it rests on.
- The goal is judged ACHIEVED: `known_issues --check` reports 3 disclosed findings and `--bar`
  reports none at a barred severity.

What is owed: the push, and the v5.1 tag. Both the operator's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-10 | sdlc-studio | Created via `new` (deterministic) |
