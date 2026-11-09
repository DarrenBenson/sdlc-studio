# Persona Index

**Last updated:** 2026-11-09

Goal-directed design personas for sdlc-studio itself (the Cooper model, RFC0017). The registry covers
two interfaces, one Primary each (D0379): the shipped skill, and this repository's own tooling, which
does not ship. A unit touching a shipped path is judged against the shipped skill's Primary. The
review seats that critique artefacts are a separate concern (RFC0016), linked under Review seats.

## Primary (the design targets, one per interface)

- [Abena Osei](abena-osei-head-of-engineering.md) - head of engineering in an audited
  organisation; leads several three-person teams directing the agents the organisation licenses,
  and answers for every release at a change approval board. Primary for the shipped skill (D0436).
  Well-formed.
- [Rowan Achterberg](rowan-achterberg-skill-maintainer.md) - maintainer of this repository; Primary for
  the repository-tooling interface (this repository's `tools/`, `.githooks/` and `.github/`, and the
  forward-port to the installed copy), which does not ship. A story minted with no persona names
  him when its Affects, test modules and changelog fragments set aside, lie wholly under those three
  paths (US1080). Listed second, he is never the fallback: every other unnamed mint names Abena.

## Secondary (served, never at either Primary's expense)

- [Maya Okafor](maya-okafor-founder-engineer.md) - solo founder-engineer; wants a disciplined,
  trustworthy lifecycle driven by an agent, not vibe-coding, and is the way in for a builder who
  starts alone. Well-formed.
- [Jonah Reyes](jonah-reyes-team-lead.md) - small-team lead adopting sdlc-studio on an inherited
  brownfield repo; owns the `audit --profile repo` on-ramp, brownfield runbook, and `migrate` adoption path.
  Well-formed.

## Negative (deliberately not designed for)

- [Trevor Hale](trevor-hale-enterprise-pm.md) - enterprise delivery manager wanting a GUI,
  central governance, and a human gate on every change. A signal to decline, not a backlog.
  Well-formed.

## Review seats

Not personas: the registry reader registers no bullet under this heading. Each link is the card
`persona_resolve.py resolve --seat <seat> --path-only` prints, this repository's override of the
shipped seat.

- [Engineering](seats/engineering.md)
- [Product](seats/product.md)
- [QA](seats/qa.md)

## Superseded

The flat [`../personas.md`](../personas.md) is a **legacy appendix**, kept for history
only. It holds a June 2026 brownfield extraction of four user *categories* (operator,
consuming developer, executing agent, maintainer) with no declared Primary. It is not
the design target and is not maintained; this registry is.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Darren Benson | Seeded sdlc-studio's own Primary + Negative personas (dogfood of the Cooper template, RFC0017/CR0058) |
| 2026-07-16 | Claude Fable 5 (persona review, operator-directed) | Maya gains the cost-honesty frustration + sprint-report scenario (RFC0038/EP0048); Secondary Jonah Reyes added (brownfield adoption path); Trevor confirmed unchanged |
| 2026-07-27 | Claude Fable 5 | Recorded the flat `personas.md` as a superseded legacy appendix (US0451); the PRD's Target Users now names this registry (US0450) |
| 2026-07-29 | Claude Opus 5 (BG0307) | Jonah Reyes's line names the `audit --profile repo` on-ramp where it named the retired `review generate` |
| 2026-10-19 | Claude Opus 5.5 (US1079) | Rowan Achterberg added as Primary for the repository-tooling interface beside Maya for the shipped skill, each card declaring its interface (D0379, after the D0374 stakeholder consult) |
| 2026-11-01 | Claude Opus 5.5 (US1083) | History put in date order and the missing 2026-07-29 row added; Last updated added; the review seats linked; Rowan's line says when an unnamed mint names him (US1080); the Primary and Secondary headings read for two Primaries |
| 2026-11-09 | Claude Opus 5.5 (US1146) | Abena Osei added as the shipped skill's Primary on the operator's pick (D0436), listed first so an unnamed mint names her; Maya Okafor moves to Secondary and is now less well served on her End goal 3, driving a whole batch to done autonomously (D0443 narrowed D0436's list to that one); Rowan's card and line, and Trevor's Boundaries, name Abena as the shipped skill's Primary |
