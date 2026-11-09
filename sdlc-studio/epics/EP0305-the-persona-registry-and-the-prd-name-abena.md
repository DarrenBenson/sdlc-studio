# EP0305: The persona registry and the PRD name Abena Osei as the shipped skill's Primary and Graham Doyle as Served

> **Status:** Draft
> **Derived Point Total:** 11
> **Parent:** CR0689
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0689. Delivers the work CR0689 requested.

## Story Breakdown

- [x] [US1146: Abena Osei becomes the shipped skill's Primary and Maya Okafor moves to Secondary](../stories/US1146-abena-osei-becomes-the-shipped-skill-s-primary.md)
- [ ] [US1147: Graham Doyle joins the registry as Served and Trevor Hale narrows to what the skill declines](../stories/US1147-graham-doyle-joins-the-registry-as-served-and.md)
- [ ] [US1148: The PRD leads with human in the lead and its outcomes cite Abena Osei and Graham Doyle](../stories/US1148-the-prd-leads-with-human-in-the-lead.md)

## Acceptance Criteria (Epic Level)

- [ ] A new card under sdlc-studio/personas/, named by the seats, is the shipped skill's Primary: a head of engineering in an audited organisation who leads several three-person teams (product owner, engineer, QA) directing agents the organisation licenses, every release passing a change approval board. Its End goals are D0436's five, in order, then End goal 6, "The process stays small enough to serve the work; every step earns its place." (D0443), each with an Evidence line citing an id that resolves.
- [ ] A change-approver card carries the Served cast role and D0437's three End goals; the index lists it under a Served heading, and `tools/tests/test_persona_coherence.py` reads Served as a role.
- [ ] Maya Okafor's card and the index move her to Secondary; Jonah Reyes's card is unchanged; Trevor Hale's card is narrowed to a GUI-first operator, non-technical staff running the tool and a human approval on every change; the index's history records the operator's pick (D0436) and names Maya's End goals 3 and 5 as less well served.
- [ ] The PRD's Mission leads with "human in the lead, not just in the loop"; Target Users names the new Primary, Maya and Jonah as Secondary, the change approver as Served and Trevor as Negative; Outcomes gain O10-O13 from D0438's draft as the seats word them, citing each End goal of the two new cards exactly once; O6-O9 keep their citations of Jonah.
- [ ] O5 cites Maya Okafor's End goal 5 and the new Primary's End goal 6, `;`-separated. The O5 pin in `tools/tests/test_lean_prd_refresh.py` (`O5_CITES`, today Maya Okafor End goal 5 alone) becomes that pair, so O5 citing exactly those two End goals passes, O5 citing either one alone fails, and every End goal of each cited card is still cited exactly once.
- [ ] `tools/tests/test_persona_coherence.py` and `tools/tests/test_lean_prd_refresh.py` pass on the changed registry and PRD, and `sprint.py plan` on a Sprint Goal serving O10 names the new Primary or the change approver under goal serves, not NONE.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
