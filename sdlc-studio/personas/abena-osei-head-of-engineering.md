# Abena Osei

> A specific person, not a type. The Primary is the one the product is designed *for*.

## Quick Reference

| Attribute | Value |
| --- | --- |
| **Cast role** | Primary |
| **Interface** | The shipped skill: what installs into a project's skill directory (`.claude/skills/sdlc-studio/`) and runs in her teams' repositories |
| **Role** | Head of engineering in an audited organisation |
| **Context** | Leads several three-person teams (product owner, engineer, QA) directing agents the organisation already licenses; every release passes a change approval board |

## Who They Are

Abena was an engineer for a long time and now leads engineering in an organisation whose releases
are audited. Each of her teams is three people, a product owner, an engineer and a QA, directing
the coding agents the organisation already pays for, and not every team uses the same one. Every
release goes before a change approval board, and she is the one who answers for it there. She has
watched a team lose a day writing up for the board what its run already knew, and a defect nobody
could account for because the change was put down to "the agent". She wants the agents to do the
work while a named person leads each part of it, and the record the work leaves to be the evidence.

## End Goals

*What they are trying to accomplish, most important first. The design is judged against these.*

1. Every release passes the change board on the evidence the run produced, with no separate write-up
2. Every specification and every change names an accountable person, not 'the agent'
3. Know what each team's delivery costs per point and hold it to a monthly budget, whichever harness a team uses
4. A defect that escapes to production is traced to where it got through, and the mistake is not repeated
5. People who never open a terminal can follow progress without someone translating for them
6. The process stays small enough to serve the work; every step earns its place

## Experience Goals

*How they want to feel while using it.*

- Prepared at the change board - the evidence is already there, and it is the run's own
- In the lead - the agents do the work, and a person she can name answers for each part of it
- Unburdened by ceremony - nothing her teams do exists only to be shown to someone

## Behaviours & Context

- **Environment:** her teams work in terminals with the agents the organisation licenses, not all
  the same harness; she reads the committed record and the sprint reports, and signs the runs
- **Frequency:** weekly across her teams, and at each release when the change board sits
- **Proficiency:** fluent on the CLI but seldom at it now; she reads evidence closely and has no
  time to assemble it herself
- **The board:** approves a release from what is put in front of it; its members never run the
  tool or open a terminal

## Frustrations

*What trips them up with the current tools or status quo.*

- A release held at the board until someone writes up what the run already recorded
- Work put down to "the agent", so nobody can say who decided what
- Agent spend she cannot compare across teams or harnesses until the month has closed
- A production defect fixed once and then repeated, because nothing recorded where it got through
- Status only an engineer can read, so she translates it for everyone who cannot

## Scenario

*A short narrative of this persona using the product to reach an End goal.*

One of Abena's teams has a set of accepted change requests ready. Its engineer runs
`/sdlc-studio sprint --crs Proposed --goal done`, the product owner approves the triage plan it
shows, and the loop drives each unit through its tests, an independent review and a green commit.
The close files the sprint report: what shipped, what it cost against the team's budget, and
whether the estimate held. Abena reads it and signs the run once, with `sprint.py sign`. At its
next sitting the release passes the change approval board on the signed report's evidence, with no
separate write-up.

## Boundaries

- **[Rowan Achterberg](rowan-achterberg-skill-maintainer.md) is Primary for this repository's own
  tooling**, which does not ship and which Abena's teams never see. His want is met there, never by
  adding a step to her teams' runs.
- **[Maya Okafor](maya-okafor-founder-engineer.md) is Secondary**, served fully but never at
  Abena's expense. What Abena's teams need beyond a solo builder's wants is held small by End goal 6
  and by RFC0063's Non-Goals: one signature per run, no approval on each change, no GUI.
- A unit is judged against the Primary of the interface its Affects touch. A unit touching both
  touches a shipped path, so it is Abena's; a story minted with no `--persona` names her too, as the
  Primary the persona index lists first.

| A unit touching | Is judged against |
| --- | --- |
| The shipped skill | Abena Osei |
| Repository tooling | Rowan Achterberg |
| Both interfaces | Abena Osei |

## Evidence

- End goal 1: D0436, EP0275 (the versioned evidence annex) and EP0276 (the report of record,
  reviewable from the committed tree).
- End goal 2: D0436 and RFC0063 WS2, the owner field naming the accountable person.
- End goal 3: D0436, CR0685 and CR0690 (each harness's models priced, so a team's run reads a
  dollar cost).
- End goal 4: D0436, RFC0061 and RFC0063 WS6, the escape loop.
- End goal 5: D0436 and D0441 (the committed record as a versioned contract the companion
  dashboard reads).
- End goal 6: D0443, the counterweight.
- The card itself: D0436 (the operator's pick of the Primary), D0443 (End goal 6) and RFC0063
  (human in the lead).

---

- **Secondary:** see `maya-okafor-founder-engineer.md` and `jonah-reyes-team-lead.md` - each is
  served, but never at Abena's expense.
- **Negative persona:** see `trevor-hale-enterprise-pm.md` - who we are deliberately not designing for.
