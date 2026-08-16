# US0625: the doctrine states the rule and the stop-ship judgement is recorded per finding at review time

> **Status:** Ready
> **Delivers:** CR0526
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0206
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** reviewer of record deciding whether a finding stops a release
**I want** the stop-ship judgement recorded per finding at review time, with the doctrine stating the rule
**So that** a release decision rests on a ruling somebody made against a named finding, rather than on a severity label read later

## Acceptance Criteria

### AC1: the doctrine states the rule rather than implying it

- **Given** reference-doctrine.md
- **When** the stop-ship rule is read
- **Then** it states that a stop-ship judgement is recorded PER FINDING at review time, and that severity alone is not that judgement
- **Mutant:** delete the sentence - the rule survives only as practice, which is the state LL0027 names
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::StopShipRulingTests::test_the_doctrine_states_the_per_finding_rule

### AC2: a recorded verdict carries a stop-ship ruling for each finding

- **Given** a critic verdict carrying findings
- **When** it is recorded
- **Then** each finding carries an explicit stop-ship ruling, and a verdict whose findings carry none is refused rather than defaulted
- **Mutant:** default the ruling to not-stop-ship - a finding nobody judged reads as one somebody cleared
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::StopShipRulingTests::test_a_finding_with_no_ruling_is_refused

### AC3: the ruling is per finding, not per verdict

- **Given** a verdict carrying one stop-ship and one not-stop-ship finding
- **When** it is read back
- **Then** both rulings survive independently, so one blocking finding does not relabel its neighbours
- **Mutant:** collapse the rulings to a single verdict-level flag - the two findings stop being separable
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::StopShipRulingTests::test_two_findings_keep_their_own_rulings

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
