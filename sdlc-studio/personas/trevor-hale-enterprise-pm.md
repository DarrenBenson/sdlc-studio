# Trevor Hale

> The anti-persona - stated so we know who we are deliberately *not* designing for.

## Quick Reference

| Attribute | Value |
| --- | --- |
| **Cast role** | Negative |
| **Role** | GUI-first delivery manager |
| **Context** | Runs delivery from a GUI work-tracker and wants non-technical staff operating the tool and a human approval on every change |

## Who They Are

Trevor runs delivery from a GUI work-tracker. He does not write code and does not use a terminal;
he lives in boards and dashboards. He wants the tool operated by staff who never open a terminal,
the work kept in step with the enterprise tracker his organisation already uses, and a person to
approve every change before an autonomous agent may make it.

## End Goals (stated to exclude)

*Trevor's goals are real, but serving them would pull the product away from its Primary. We say no on purpose.*

1. Drive delivery from a rich GUI with boards, swimlanes, and portfolio dashboards
2. Enforce multi-stage human approval and sign-off gates on every change
3. Have non-technical staff operate the tool
4. Sync the work to Jira, Azure Boards or another enterprise tracker

## Why We Are Not Designing For Him

sdlc-studio is files, an agent and a CLI, and the specifications live in the repository. Trevor
needs a GUI, a tool non-technical staff can operate, a tracker kept in sync and a human gate on
every change, the opposite of the value here. Chasing those wants would add boards, tracker sync
and approval ceremony at the cost of the shipped skill's Primary,
[Abena Osei](abena-osei-head-of-engineering.md), whose teams direct agents from the CLI and whose
releases pass the change board on the evidence the run produced. Audit evidence and the running of
several teams are served through her (D0436), not through a governance layer built for him. His
requirements are a **clear signal to decline**, not a backlog.

## Boundaries

- **He is the Negative persona on both interfaces:** the shipped skill, whose Primary is
  [Abena Osei](abena-osei-head-of-engineering.md), and this repository's own tooling, whose Primary
  is [Rowan Achterberg](rowan-achterberg-skill-maintainer.md).
- **A run carries one signature (D0213).** The operator signs it once, after the close, with
  `sprint.py sign`, which refuses a principal who is a unit's author or a reviewer recorded on it.
  A sign-off on each unit, a second signature, or an approver on every ruling is his want, and is
  declined.
- **His objections are weighed on their evidence.** One is adopted when evidence shows that what
  he objects to harms a Primary's End goal, and declined when adopting it would serve only him. It
  is never adopted or dismissed for being his.

## Behaviours & Context

- **Environment:** a browser, a GUI work-tracker, recurring approval meetings
- **Frequency:** continuous oversight; never hands-on in a repo
- **Proficiency:** strong in process and reporting; will not use a CLI or let an agent change anything a person has not approved

## Frustrations

*What he would (legitimately) dislike about sdlc-studio - and why that is fine.*

- No GUI, boards, or portfolio view in the skill - intentional; sdlc-studio is file-and-agent driven
- An autonomous loop that commits without a human approval on each change - intentional; the loop is the point
- No sync to his enterprise tracker - intentional; the specifications live in the repository

## Scenario

*How a request from Trevor should be handled.*

Trevor asks for a board of his teams' work, a portfolio dashboard, a sign-off gate on each change
and the stories mirrored in his organisation's tracker. The right response is to recognise this as
the Negative persona. His wants for boards and dashboards are pointed at the read-only companion
dashboard over the committed record (RFC0063 D6), which shows the specifications and the runs
without changing them. The skill declines a human approval on every change, non-technical staff
running the tool and sync to an enterprise tracker: each serves a user the product is not for, and
building it would degrade the experience for the Primary. Note the request and keep sdlc-studio
lean.

---

- This persona exists to **bound** the design. When a feature only serves Trevor, that is a reason to say no.
