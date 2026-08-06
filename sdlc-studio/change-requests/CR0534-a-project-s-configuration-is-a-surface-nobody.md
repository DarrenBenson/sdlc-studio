# CR-0534: a project's configuration is a surface nobody is introduced to and nobody revisits: the operator cannot see what is in force, what the default would have been, or which setting their own history says is wrong

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/config.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/templates/core/config.yaml, .claude/skills/sdlc-studio/scripts/tests/test_config.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py
> **Evidence:** Three instances in one session, 2026-08-06, in the operator's own repository. (1) `review.policy: carry-forward` was adopted as D0129 on a previous run and the delivering agent did not know it was in force - believing a REJECT blocked, it ran an entire extra adversarial round before checking, while the setting sat documented at reference-config.md:181. (2) The gate budget lane reported OVER on most commits of RUN-01KZ9315 - 383s, 392s, 405s, 445s against a 380s ceiling already raised once from 120s - and nothing proposes re-deriving the ceiling or cutting what feeds it. (3) The estimator's calibration record says est/actual 0.44x out of sample, printed at every plan beside 'not enough history to recalibrate (need 5). Nothing is re-fitted automatically' - the tool knows its constant is wrong, says so every run, and there is no path from that to a changed setting.
> **Date:** 2026-08-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson; human; operator proposal at the RUN-01KZ9315 close
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

There are 64 documented configuration keys and no command that shows an operator what is in force. `reference-config.md` documents them well, but a reference is a thing you consult when you already know a setting exists - it cannot tell you that a default has been quietly governing your project for forty sprints, and it is not read by anyone who does not suspect there is something to read.

Three distinct gaps, and they want three different answers:

**1. Nobody can see the effective configuration.** There is no `config show`. The project file states the keys the operator has changed; every other key is a default living in code, invisible unless you go looking for it in a 652-line reference. An operator cannot answer 'what is this project actually doing' without reading the source. `reference-config.md`'s table is the documentation of the defaults - it is not, and cannot be, a report of the ones in force here.

**2. Nobody chose most of them.** A default is a decision made by whoever wrote the tool, on behalf of a project they had never seen. Some are genuinely universal. Others - the review policy, the two-role cutoff, the appetite, the gate budget - are project judgements wearing a default's clothes, and the project has never been asked. The config file records the DECIDED ones as numbered decisions (D0129, D0130), which is exactly right, and says nothing at all about the sixty that were never put to anyone.

**3. Nothing revisits them against the evidence.** The retro measures the sprint and never asks whether the settings that governed it were the right ones - although the retro is the one moment holding both the setting and its consequence. Every input needed is already on disk: the gate budget is measured on every commit against a declared ceiling, the review policy's cost is in the verdict ledger, the appetite is stamped on the run state and compared to what was delivered, the estimator's constants have a calibration record that already reports being out by 0.44x. The numbers exist and nothing joins them to the knob that produced them.

## Impact

Every consuming project, and this one. The operator states they are conscious there must be many settings they are unaware of, which is the reportable symptom: the person accountable for the project cannot enumerate what governs it.

## Acceptance Criteria

- [ ] A command prints every configuration key in force with its effective value, its source (project file, code default, or the decision id that set it) and its one-line meaning, so an operator can answer what governs this project without reading the source
- [ ] the keys that are project judgements rather than universal truths are named as such and can be decided explicitly, each recorded as a numbered decision the way D0129 and D0130 are
- [ ] the retro reads the run's own measurements against the settings that governed it and proposes changes with the evidence attached - gate budget against measured gate time, estimator constants against the calibration record, appetite against what was delivered
- [ ] a proposal is never applied automatically and lands in the retro's findings table where it must be ruled on like any other finding
- [ ] a setting with no measurement to judge it against is reported as unjudged rather than left out, since a silent omission reads as a setting nobody needs to think about

## Recommendation

C, decomposed so the first slice ships alone. `config show` is small, immediately useful, and is the thing every later slice reads - a proposal engine with no way to display what is in force would be proposing changes to values the operator still cannot see. The retro lane should start with the three signals that already have measurements and declared ceilings on disk (gate budget, estimator constants, appetite versus delivered), because a proposal derived from a number is arguable and a proposal derived from taste is noise. It must PROPOSE and never apply: a tool that silently retunes its own gates is a tool whose gates mean nothing, and the D0129/D0130 pattern - a numbered decision, dated, with its reason - is already the right shape for the operator's answer.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | Darren Benson | Raised |
