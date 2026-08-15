# BG0577: A fix that lands without closing its bug leaves a backlog item that reads real and is not, and nothing detects it - 12% of the open bug backlog was fiction

> **Status:** Fixed
> **Verification depth:** functional (the detector driven against a fixture reproducing the real BG0534/BG0563 pair this bug cites - reported at 67% overlap - with three controls confirming a shared file alone, the same words in a different module, and units declaring nothing are all left alone; NARROWED deliberately to one of the three checks, with the reason for each omission written on the bug; mutation: 4 declared mutants, all KILLED, restore byte-exact)
> **Created:** 2026-08-13
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Severity:** High
> **Points:** 5

## Summary

Working the open bug backlog on 2026-08-13 found that five of its forty-one units - roughly seventeen of one hundred and seventeen points, 12% - were not work at all. Two were already REPAIRED, with the repair landed and the bug never closed. Two carried premises that had EXPIRED, their counts having gone to zero without either bug being touched. One was a straight DUPLICATE of another open bug.

None of these is detectable today. `status.py points` counts open artefacts, `conformance` judges units that reached a terminal status, and neither asks whether an OPEN bug is still true. So the backlog reports a number that only ever grows more wrong, and every artefact computed from it inherits the error silently.

The cost is not the wasted points, which are recoverable. It is that the figure is load-bearing. The delivery plan approved on 2026-08-13 was sized at 117 points with a 9.3M-41M token forecast and a three-run shape derived from that total - all of it computed over a backlog now known to be 12% fiction. A capacity ceiling, a velocity rate and a run count were each chosen against a number nobody could check, and the only reason the error surfaced was that somebody read all forty-one bugs one at a time.

This is the same class the repository files hardest against - a claim nothing exercises - pointed at its own backlog rather than at its code.

## Acceptance Criteria

- [x] **AC1** Given two open bugs declaring the SAME files and describing the same subject, when `sprint breakdown` runs, then the pair is reported at plan time - where the cost of carrying both is about to be paid.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k one_file_set_and_one_subject_are_paired
  - **Verified:** yes (2026-08-15)
- [x] **AC2** Given two bugs sharing a file set but about different things, when the check runs, then they are NOT paired - a shared file is a cluster, already reported beside this, and a report nobody can read is one nobody reads.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k shared_file_alone_is_not_a_duplicate
  - **Verified:** yes (2026-08-15)
- [x] **AC3** Given two bugs with the same words about different modules, when the check runs, then they are not paired - the same defect in two places is two bugs.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k different_file_set_is_never_paired
  - **Verified:** yes (2026-08-15)
- [x] **AC4** Given units that declare no `Affects`, when the check runs, then they are skipped rather than paired on their shared emptiness.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k no_declared_affects_is_skipped
  - **Verified:** yes (2026-08-15)
- [x] **AC5** Given any pair it finds, when it reports, then nothing is closed or altered - a backlog that silently closed its own items would be this failure with the sign reversed.
  - **Verify:** manual read `probable_duplicates` - it returns rows and writes nothing

## Steps to Reproduce

Measured 2026-08-13 against the 41 open bugs:

1. ALREADY REPAIRED, bug still Open.
   - BG0547 asserts the depth-parity advisory ASSIGNS `gate_warn` while the AC-verify advisory accumulates. All six assignment sites in `transition.py` `_pre_write_gates` now use the accumulating form `gate_warn = f"{gate_warn}; ..." if gate_warn else ...`.
   - BG0537 asserts `check_root_docs` reads raw lines while `check_body_links` blanks code spans. All three link passes in `tools/check_links.py` (lines 244, 282, 353) run their input through `_without_code`.

2. PREMISE EXPIRED.
   - BG0421 asserts twenty-one Open Questions reached a terminal status unanswered. Sweeping `sdlc_md.unresolved_questions` over every markdown file under `sdlc-studio/` returns 0.
   - BG0350 asserts twenty-five Done stories carry no independent critic verdict. `conformance.py check --root .` reports `588/670 conformant, 0 not, 82 exempt`.

3. DUPLICATE.
   - BG0534 and BG0563 describe one defect - `_EDIT_VERBS` in `verify_ac.py` being an enumeration - from opposite ends, with byte-identical `Affects`. One change closed both.

Each was found by reading the bug and re-running its own evidence. No command reports any of these five states.

## Proposed Fix

Two checks, both cheap, neither existing:

FIRST, a repaired-but-open detector. For each open bug, run the criteria it already carries - a bug reaching `Fixed` must have a `Verify:` line or a ticked box, and many carry one while Open. A bug whose own evidence passes is a candidate for closure and should be REPORTED, never auto-closed: whether the fix is complete is a judgement, and the point is to put it in front of somebody.

SECOND, a premise re-check on any bug whose summary states a COUNT. The four-of-five instances above all did - twenty-one questions, twenty-five stories, twenty findings, four units. Where the count is derivable, re-derive it and report the drift; where it is not, age the bug and prompt a re-read after N days.

The duplicate case is already partly covered: `sprint.py breakdown` reports shared-file clusters, and a pair with byte-identical `Affects` and a high title-token overlap is a stronger signal than a cluster. Report it at plan time, where the cost of carrying both is about to be paid.

Do NOT auto-close anything. The failure this bug describes is a backlog trusted without checking; a backlog that silently closes its own items would be the same failure with the sign reversed.

## Impact

Every plan, forecast and capacity decision computed from the backlog is wrong by an unknown margin, and the margin only grows: a bug filed today is checked at filing and never again. The measured instance is 12%, found by hand on one backlog on one day, so it is a lower bound rather than a rate.

Filed High because it defeats the estimator rather than degrading it, and because the evidence is two artefacts - an approved plan and a released version - rather than an argument. It is also the cheapest class of waste to remove: a repaired-but-open bug costs a full grooming, test-plan, review and sign-off cycle to discover, and one command to detect.

## Delivered here, and what is NOT

**Delivered: the duplicate detector**, in `sprint breakdown`, beside the shared-file clusters it
strengthens. It is the cheapest of the three checks this bug asks for and the only one that needs
no judgement: an identical file set PLUS an overlapping subject is a stronger signal than a
cluster, and it is reported at plan time because that is where the cost of carrying both is about
to be paid. It reports and does nothing else.

**Not delivered: the repaired-but-open detector.** It rests on running an open bug's own criteria,
and the premise check for it falsified its own design - measured on 2026-08-13, **0 of 31 open
bugs carried an executable `Verify:` line**, so there is nothing to run. It needs criteria on open
bugs first, which is a grooming programme rather than a check.

**Not delivered: the premise re-check on stated counts.** Deriving a count from a bug's prose is
a parser over free text, and a wrong re-derivation would report drift that is not there - the
same false-positive class this run spent the day removing from other guards.

Both remain worth building and neither is started. The narrowing is stated rather than implied,
because a bug closed as though it were whole is the shape this bug is about.

This session is itself the evidence for all three: of the bugs triaged today, BG0490 was half
stale, BG0519 was entirely stale, and BG0493 was entirely live. Nothing but reading each one
could tell them apart.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in sprint.py `probable_duplicates`, raise the title-overlap threshold so a real pair is missed | Given two open bugs declaring the SAME files and describing the same subject, when `sprint breakdown` runs, then the pair is reported at plan time - where the cost of carrying both is about to be paid. |
| AC2 | in sprint.py `probable_duplicates`, compare only the Affects so every cluster is a duplicate | Given two bugs sharing a file set but about different things, when the check runs, then they are NOT paired - a shared file is a cluster, already reported beside this, and a report nobody can read is one nobody reads. |
| AC3 | in sprint.py `probable_duplicates`, drop the Affects equality and compare titles alone | Given two bugs with the same words about different modules, when the check runs, then they are not paired - the same defect in two places is two bugs. |
| AC4 | in sprint.py `probable_duplicates`, stop skipping units that declare no Affects | Given units that declare no `Affects`, when the check runs, then they are skipped rather than paired on their shared emptiness. |
| AC5 | unnameable: the claim is that the function WRITES nothing, and no edit makes a pure reader write | Given any pair it finds, when it reports, then nothing is closed or altered - a backlog that silently closed its own items would be this failure with the sign reversed. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-13 | sdlc-studio | Created via `new` (deterministic) |

## Measured after filing: the first proposed check cannot work as written

The proposed fix above opens with "a repaired-but-open detector: for each open bug, run the
criteria it already carries". Measured against the corpus on 2026-08-14, immediately after
filing: **0 of 31 open bugs carry an executable `Verify:` line.**

They carry criteria - most of them the tool-derived scaffold - but a verifier is authored at the
moment somebody transitions the unit, which is precisely the step a repaired-but-open bug never
reached. The check needs the artefact of the thing that did not happen.

So the detector has to work from something an OPEN bug does have. Three candidates, none free:

  1. The bug's `Affects` paths plus `git log -S` over the phrases in its Summary - did a commit
     touch this surface and mention this defect after the bug was filed? Noisy, and it is a
     search rather than a test, but it needs nothing the artefact lacks.
  2. The COUNT re-check, which is the half that already works. Four of the five fiction units
     stated a number - twenty-one questions, twenty-five stories, twenty findings, four units -
     and every one of those was re-derivable. That is the cheapest real signal available.
  3. Ask at grooming rather than continuously: when a bug is about to enter a batch, re-read it.
     That is where the cost of carrying a dead bug is about to be paid, and where a human is
     already reading it.

Recorded here rather than left in the proposal, because a fix specified against data that does
not exist is the same defect this bug is about, one level up - a claim nobody exercised.
