# CR-0678: Add `repo_map.py outline` and `where` from the existing symbol index, and have the lane and critic briefs name each target symbol with its line range, so agents stop spending a fifth of their calls locating code

> **Status:** Proposed
> **Parent:** RFC0062
> **Priority:** Medium
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/repo_map.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-agent-prompt-template.md, .claude/skills/sdlc-studio/reference-repo-map.md, .claude/skills/sdlc-studio/templates/personas/amigos/, .claude/skills/sdlc-studio/scripts/tests/test_repo_map.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RFC0062 Phase 3, tool-output lens: finding 1
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T12:23:30Z

## Summary

Subagent calls whose every tool use was a search cost 4.47M (builders 166 calls 2.75M, reviewers 115 calls 1.51M, repairs 17 calls 0.21M) and code-read calls 2.94M (224 calls), 20% of the run. 89% of builders' 232k exploration tokens were read before their first source edit, and the median read was carried 36 later calls. sprint.py is 13,314 lines and was read by 11 of 36 agents. `repo_map.py` already extracts symbols with line numbers (`repo_map.py`:4, :93) but offers only build, query and stats (:597-623); reference-agent-prompt-template.md:39-44 says to fill the brief's file list from `repo_map.py query`, yet `repo_map` ran once in the whole run. US1118's lane brief named five functions and its hand-written builder brief none. Already true of the tree.

## Impact

Builders and reviewers pay about 10k to 15k per search call, mostly before their first edit, in this repository and in any consuming project with large hub files.

## Acceptance Criteria

- [ ] `repo_map.py outline <file>` prints each symbol's name, kind and start-end line range and `repo_map.py where <symbol>` prints its file and range, both served from the existing index, and a stale index is rebuilt or refused rather than printing wrong lines.
- [ ] `sprint.py lane brief` lists, for each Affects file, the symbols the story and its criteria name (or the top symbols `query` ranks) with their line ranges.
- [ ] `critic.py brief` names the enclosing symbol and its line range for each diff hunk.
- [ ] Before and after: search-only calls per builder on the benchmark (US1128) fall from run six's 11.9 (166 over 14) to 8 or fewer.

## Recommendation

Serve outlines from the index and put symbol ranges in both briefs. Saving 0.77M per run: one third of the 298 search-only calls avoided at about 10k each (builder context 104k x 0.1) = 0.99M, x 0.775 for the subagent spend left once the first-time-right CRs land. The one-third rate is the lens's assumption and the before-and-after criterion must confirm it; the upper bound at the measured 15.0k a search call is 1.49M before scaling, and narrower reads would also cut part of the 1.92M carried by code-read output, which is not counted. Risks: no check is removed and agents can still grep; a stale index points at wrong lines, so the brief step checks its age and gives ranges, not start lines.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
