# CR-0689: The persona registry and the PRD name a head of engineering in an audited organisation as the shipped skill's Primary, the change approver as Served and Maya Okafor as Secondary

> **Status:** Proposed
> **Parent:** RFC0063
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Opus 5.5 (operator-raised: RFC0063 WS1 and the rulings D0436-D0438 of 2026-11-09); agent; v1
> **Affects:** sdlc-studio/personas/index.md, sdlc-studio/personas/maya-okafor-founder-engineer.md, sdlc-studio/personas/trevor-hale-enterprise-pm.md, sdlc-studio/prd.md, tools/tests/test_persona_coherence.py, tools/tests/test_lean_prd_refresh.py
> **Priority:** High
> **Type:** Enhancement
> **Size:** M

## Summary

RFC0063 WS1, first in run nine (D0435). The operator ruled the registry's new shape on 2026-11-09: a NEW Primary card for the shipped skill, named by the seats (D0436); the change approver as a Served persona (D0437); O10-O13 from the operator's draft, worded by the seats (D0438). On 2026-11-09 the operator added two requirements: the new Primary's card carries the frustration "process that costs more than it catches", and O5 cites it as well as Maya Okafor's End goal 5. Jonah Reyes's card is unchanged, so O6-O9 keep their citations. The two new cards are written under sdlc-studio/personas/ with the names the seats give them.

## Impact

Every later unit is judged against the persona this sets (RFC0063). Today work for a change approver traces only to Trevor Hale, a Negative persona, so `sprint.py plan` prints `goal serves: NONE` for it. `tools/tests/test_persona_coherence.py` reads only the Primary, Secondary and Negative roles, so a Served card needs the test to learn that role; `tools/tests/test_lean_prd_refresh.py` requires each cited End goal to be cited exactly once and pins O5 on Maya Okafor's End goal 5.

## Acceptance Criteria

- [ ] A new card under sdlc-studio/personas/, named by the seats, is the shipped skill's Primary: a head of engineering in an audited organisation who leads several three-person teams (product owner, engineer, QA) directing agents the organisation licenses, every release passing a change approval board. Its End goals are D0436's five, in order, each with an Evidence line citing an id that resolves, and its Frustrations include "process that costs more than it catches".
- [ ] A change-approver card carries the Served cast role and D0437's three End goals; the index lists it under a Served heading, and `tools/tests/test_persona_coherence.py` reads Served as a role.
- [ ] Maya Okafor's card and the index move her to Secondary; Jonah Reyes's card is unchanged; Trevor Hale's card is narrowed to a GUI-first operator, non-technical staff running the tool and a human approval on every change; the index's history records the operator's pick (D0436) and names Maya's End goals 3 and 5 as less well served.
- [ ] The PRD's Mission leads with "human in the lead, not just in the loop"; Target Users names the new Primary, Maya and Jonah as Secondary, the change approver as Served and Trevor as Negative; Outcomes gain O10-O13 from D0438's draft as the seats word them, citing each End goal of the two new cards exactly once; O6-O9 keep their citations of Jonah.
- [ ] O5 cites the new Primary's frustration "process that costs more than it catches" as well as Maya Okafor's End goal 5, written so `test_lean_prd_refresh.py` still reads O5 as citing Maya Okafor End goal 5 and the once-each citation rule holds.
- [ ] `tools/tests/test_persona_coherence.py` and `tools/tests/test_lean_prd_refresh.py` pass on the changed registry and PRD, and `sprint.py plan` on a Sprint Goal serving O10 names the new Primary or the change approver under goal serves, not NONE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
