# CR-0535: a refusing verb cannot state its contract until you trip it: 39 verbs refuse, 2 can be asked what they demand

> **Status:** In Progress
> **Decomposed-into:** EP0210
> **Priority:** High
> **Type:** Improvement
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/reference-scripts.md, .claude/skills/sdlc-studio/help/, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py
> **Evidence:** Counted on RUN-01KZCAJX, 2026-08-06. `grep -rlE 'refus(ed|es)|REFUSED' scripts/*.py` -> 39 files; `grep -rln 'def cmd_requirements|requirements('` -> 2. Contract-vocabulary spot check across `help/` and `reference-*.md`: edit verbs 0 files, DSL shell-prefix 0, census attribution 0, `[check:]` registration 1, `label|consequence` 1.
> **Date:** 2026-08-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; operator proposal at the RUN-01KZCAJX delivery
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The diagnosis is NOT that the tooling is undocumented. `reference-scripts.md` is a real catalogue and `help/` holds ~40 pages. The diagnosis is that the documentation describes CAPABILITY - what a command does - while the refusals encode CONTRACT - what it demands of its caller - and the two are not connected. A contract is discoverable only by violating it.

Measured: 39 scripts under `scripts/` refuse on some condition. TWO can be asked what they will demand before being run. `transition.py requirements` is the proven pattern and its docstring already states why it works: it RUNS the real gate ladder via the dry-run path and reports what refuses, 'so there is no second copy of a requirement to drift from the guard that enforces it'. That is the whole design, and it exists for one verb out of thirty-nine.

The cost is a round-trip per contract, paid by whoever did not already know. One session, RUN-01KZCAJX, hit roughly twenty: `--option` needing `label|consequence`; `--issues` splitting on semicolons with each part needing an origin tag; `--fields-file` rejecting `ac` for `acs` and refusing a multi-line `evidence`; `goal-review record` wanting `done_means`/`one_increment` rather than `done`/`increment`; `signoff` requiring `--principal` even with `--panel`; `decision resolve` requiring `--index`; `testplan derive` refusing five honest mutants for want of a verb on an unpublished 29-item list, and a sixth for naming a path outside `Affects`; `verify_ac` refusing `bash tools/lint-style.sh` because `bash` is not a DSL verb and needs an explicit `shell` prefix - which meant that criterion had been unrunnable since the day it was groomed; a `[check:]` tag in the shipped Definition-of-Done template resolving to no registered id; and the test census refusing a new guard whose attribution rule considers only sibling `tools/*.py` modules.

Of those five vocabularies, THREE appear in no `help/` or `reference-*.md` file at all: the mutant edit verbs, the DSL verb set's shell-prefix rule, and the census attribution rule.

This is the dual of LL0027. That lesson says a rule that matters belongs in the command people actually run. Its unstated other half is that a command which refuses should be able to say what it wants BEFORE it refuses - otherwise the gate teaches only by punishing, and it punishes hardest whoever has read the least.

## Impact

Every agent and operator, on every project. The cost is invisible in any measurement the repo takes, because a refusal followed by a corrected retry looks like a working gate rather than a tax - which is why it has accumulated to thirty-nine verbs unnoticed.

## Acceptance Criteria

- [ ] A verb that can refuse can be ASKED what it will demand, before being run, and the answer is derived by executing its own guard rather than restated beside it - the pattern transition.py requirements already proves
- [ ] The input vocabularies that gate a caller - mutant edit verbs, DoR/DoD check ids, the Verify DSL verbs and their shell-prefix rule, option grammars, status vocabularies - are printable from the constant that enforces them, so a caller can read the accepted set without reading the source
- [ ] A lint lane asserts that every verb capable of refusing is reachable by the contract reporter, and names the ones that are not - coverage of 2 in 39 accumulated silently and will again without a lane that counts it
- [ ] help/ and reference-scripts.md POINT at the contract reporter rather than restating any contract, so no hand-maintained copy exists to drift
- [ ] The measured cost is reported: the number of refusals a run hits, so the claim that this reduces round-trips is a number in a retro rather than an assertion

## Recommendation

C, decomposed so B ships first and the lane follows. Start with the verbs whose refusals cost most in the measured session - `critic record`, `file_finding file`, `sprint decision`, `verify_ac testplan derive` - rather than uniformly across 39. The lane in C is what makes this stay true; without it this CR is a one-off cleanup that decays to the same state, and the repo has the same shape of finding already recorded as LL0013 (an enumeration silently exempts what it forgot).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | Darren Benson | Raised |
