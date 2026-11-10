# CR-0696: Each unit carries a risk and compliance class from a declared component map, flagged at plan, and a high class adds a second review seat

> **Status:** Proposed
> **Parent:** RFC0064
> **Related:** CR0692, D0439
> **Priority:** High
> **Type:** feature
> **Size:** M
> **Date:** 2026-11-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-10T13:39:09Z

## Summary

RFC0064 WS3. A declared component map proposes each unit's risk and compliance class at refine, and the plan flags a unit whose files touch a higher-class component than its tag; the operator confirms at plan approval (D0459, the same pattern as D0439's machinery tag). A high-class unit gets a second independent review seat, whose yield each retro reports so it is dropped if it catches nothing (D0460). The change evidence pack groups by the class (CR0692). A human approval on every change stays out.

## Impact

Serves O10, Abena Osei's End goal 1 and Graham Doyle's End goal 1. Adds review cost on high-class units only.

## Acceptance Criteria

- [ ] A project declares its component map (paths to a class, such as payments, personal data or standard) in one committed file, and refine sets each unit's class from it
- [ ] `sprint plan` flags a unit whose Affects touch a component of a higher class than its tag, and the plan shows each unit's class for approval; no per-unit sign-off is added
- [ ] A high-class unit gets a second independent review seat, briefed with `critic.py brief`, and the retro reports what each second seat found that the first did not
- [ ] A project with no map classes every unit standard and the plan says so in one line; nothing refuses

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Raised |
