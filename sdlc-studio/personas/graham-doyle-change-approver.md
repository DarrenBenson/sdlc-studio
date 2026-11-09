# Graham Doyle

> A specific person, not a type. Served: affected by the product without ever using it (D0437).

## Quick Reference

| Attribute | Value |
| --- | --- |
| **Cast role** | Served |
| **Role** | Chairs the change approval board in an audited organisation |
| **Context** | Approves each release from the evidence put in front of him; never runs the tool or opens a terminal |

## Who They Are

Graham chairs the change approval board in the organisation where
[Abena Osei](abena-osei-head-of-engineering.md) leads engineering. Every release her teams make
comes before his board, and he either approves it or sends it back. He reads what is put in
front of him and asks who answers for it; he does not open the repository, run a command or use
the agents her teams direct. He is not a design target for the tool's interface: he is served
by what a run leaves behind, not by anything he operates.

## End Goals

*What he is trying to accomplish, most important first. A Sprint Goal for him traces to these.*

1. Approve a change from one document showing what changed, which criteria passed, who reviewed it independently, what is known to be wrong, and who is accountable
2. Trust that the evidence came from the process, not written after the fact
3. See fewer surprises in production over time

## Behaviours & Context

- **Environment:** the change board's meeting and the documents sent to it; never a terminal
- **Frequency:** once for each release that comes before the board
- **Proficiency:** strong in risk and audit; reads evidence closely, and has no reason to learn the tool

## Frustrations

- A release paper written after the work, which says what the team believes rather than what
  the run recorded
- A change put down to "the agent", with no person who answers for it
- Evidence spread over many documents, so the approval turns on what the team chose to bring
- A known defect he learns about in production rather than at the board

## Boundaries

- **He is Served, not a Secondary:** he never uses the tool, so no command, screen or step is
  designed for him. A want of his is met in the record a run produces, never by adding a step
  for him to the run.
- **No approval on every change.** He approves a release at the board; a sign-off he must give
  inside each run is declined (RFC0063 Non-Goals).
- **His End goals become standing criteria when EP0285 lands (D0437).**

---

- This card exists so a Sprint Goal for the change approver has someone to trace to without making him a design target.
