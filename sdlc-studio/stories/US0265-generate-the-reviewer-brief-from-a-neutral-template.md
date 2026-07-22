# US0265: Generate the reviewer brief from a neutral template carrying the diff and risk surface but no prior verdicts, round number or expected conclusion

> **Status:** Done
> **Delivers:** CR0358
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py
> **Epic:** EP0085
> **Points:** 3

## User Story

**As an** operator relying on a review verdict being independent
**I want** the brief the author generates to carry the diff and risk surface but none of the framing that predicts a conclusion
**So that** a REJECT means the reviewer found something, not that the prompt told it what to find

## Acceptance Criteria

### AC1: The neutral brief carries the diff and risk surface

- **Given** a unit under review
- **When** the brief is generated
- **Then** it contains the diff scope, the risk surface and the return contract - everything the reviewer needs to do the work
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_neutral_brief_carries_diff_and_risk_surface
- **Verified:** yes (2026-07-20)

### AC2: The brief carries no prior verdict prose, round number, or expected conclusion

- **Given** a re-review after a prior REJECT
- **When** the brief is generated
- **Then** it contains no verdict word from the prior round, no round number, and no assertion about what the reviewer is expected to find
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_brief_omits_verdict_round_and_expected_conclusion
- **Verified:** yes (2026-07-20)

### AC3: The probes to re-execute still travel, stripped of their framing

- **Given** a prior verdict that named specific probes and mutants
- **When** the re-review brief is generated
- **Then** those probes are carried as a neutral list of checks to execute, without the verdict prose, severity labels or conclusions that surrounded them - the re-execution demand survives, the priming does not
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_probe_list_travels_without_its_framing
- **Verified:** yes (2026-07-20)

### AC4: A prior verdict whose probes cannot be extracted is refused, not silently dropped

- **Given** a prior verdict block whose named probes cannot be parsed
- **When** the re-review brief is generated
- **Then** it is refused loudly, naming the cause - a re-review that silently drops the re-execution demand would approve against a brief weaker than the one it replaced
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_unparseable_probe_list_is_refused
- **Verified:** yes (2026-07-20)

### AC5: The neutrality check is mechanical, not a reviewer's impression

- **Given** any generated brief
- **When** the neutrality assertion runs
- **Then** it mechanically checks the rendered text for the banned classes and fails on a violation, so a future edit that reintroduces priming is caught by the suite
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py -k test_neutral_text_reports_no_violations
- **Verified:** yes (2026-07-22)

## Notes

**This story narrows CR0358's AC5 deliberately.** `rejoinder_brief` quotes the prior
verdict verbatim for a stated reason: the re-reviewer must RE-EXECUTE the probes and
mutants the prior verdict named, and RUN-01KXZQF0's round-2 APPROVE was trustworthy
precisely because the same reviewer re-ran its own reproductions verbatim. Removing the
prior verdict wholesale, as CR0358's AC5 reads literally, would delete that mechanism.

AC3 and AC4 split what CR0358 conflated: the **probe list** is factual and must travel;
the **verdict prose, severity framing, round number and expected conclusion** are the
priming and must not. If the split proves unworkable in build, that is a design escalation
back to CR0358, not a quiet reversion to verbatim quoting.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-20 | sdlc-studio | Groomed: ACs authored; CR0358's AC5 narrowed to preserve the probe re-execution demand |
