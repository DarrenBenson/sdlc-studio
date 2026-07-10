# CR-0220: stakeholder panel generation: the other side of the table (persona generate --stakeholders)

> **Status:** In Progress
> **Depends on:** CR0218
> **Priority:** High
> **Type:** Feature
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

RFC0028. Generate the stakeholder panel consult already reads from personas/stakeholders/: economic buyer, compliance, ops/support, served groups - selected via one multi-select question, each card on a new stakeholder-template with goals, veto lines, evidence-they-read, Cooper Customer/Served designation, and the B2B arbitration rule (buyer goals never override the Primary user's interface). Depends on the converged-home CR.

## Acceptance Criteria

- [ ] stakeholder-template.md ships (role, goals, vetoes, evidence read, Customer/Served designation, B2B arbitration line); --stakeholders generates into personas/stakeholders/ flat layout
- [ ] `check_personas` learns the stakeholder schema (no permanent layout/section warnings on generated panels); consult stakeholders reads the generated panel and its output header names any provisional card
- [ ] Stakeholder cards keep the provisional-unverified stamp until persona review clears them (Cooper's provisional rule applies to research-ungrounded cards)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
