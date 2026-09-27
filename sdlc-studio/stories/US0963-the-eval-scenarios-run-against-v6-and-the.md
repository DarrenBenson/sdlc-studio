# US0963: The eval scenarios run against v6, and the independence scenario grades v6's rule

> **Status:** In Progress
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** evals/scenarios/06-independence-gate.json, evals/README.md, evals/.results/v6-rc1.json, changelog.d/US0963.md
> **Epic:** EP0267
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer whose agent learns the process from the skill's instructions
**I want** the behavioural scenarios re-run on the v6 skill before it is cut
**So that** an instruction rewritten this release that now steers the model wrong is caught before I install it

## Acceptance Criteria

- **AC1:** Given evals/scenarios/06-independence-gate.json, then it grades v6's independence rule: a bug reaches Fixed on green criteria and an independent `critic.py record` APPROVE with no `Verification depth` asked for, and a verdict whose reviewer is the author does not count as critiqued; and `tools/eval_run.py setup` builds its fixture. Fails on: HEAD, whose blocking behaviours (lines 15, 20, 31) grade a close blocked for a missing `Verification depth`, which v6 removed, so a correct v6 skill fails the scenario and a stale one passes it
  - **Verify:** shell ! grep -q 'Verification depth' evals/scenarios/06-independence-gate.json && d=$(mktemp -d) && python3 tools/eval_run.py setup --scenario 06-independence-gate --dir "$d/fx"
- **AC2:** Given all eight scenarios, when each runs as a fresh worker session and a fresh grader session against the installed 6.0.0-rc.1 skill and every graded behaviour is recorded with `eval_run.py record --run v6-rc1`, then `eval_run.py report --run v6-rc1` exits 0 and names all eight scenarios. Fails on: running only the four scenarios with a machine fixture (05-08) and reporting the set green; a blocking failure waved through rather than fixed or filed High
  - **Verify:** shell r=$(python3 tools/eval_run.py report --run v6-rc1) && for s in 01 02 03 04 05 06 07 08; do printf '%s\n' "$r" | grep -q "$s-" || exit 1; done

## Notes

The rc.1 notes promised it: 'the eval scenarios are re-run against v6 behaviour'. Measured 2026-09-27: the only recorded run is 2026-07-10 (v4, EP0029); 4 of 8 scenarios carry a machine `fixture` (05-08), the other 4 degrade to prose setup by hand; scenario 06 grades the deleted depth gate. Each scenario costs two real model sessions, which is why this is 5 points. Cut line if capacity runs short: 3 points for 06 rewritten plus 05-08 run, and the 6.0.0 notes name 01-04 as not re-run (US0953 AC4 requires the disclosure). evals/README.md step 3 says to note results 'in the release-gate sign-off': it becomes the run file and the release notes. Takes evals/scenarios/06 from US0924's Affects. Engineering to confirm `report` enumerates every scenario rather than only those recorded; if it does not, AC2's verify is what checks the eight. Ratchet (LC-008): uses the existing eval spine, adds no lane. Absorbs QA's Q4 (fixtures that build, a lean-loop scenario) (D0278).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (US0963) |
