# Persona Index

Goal-directed design personas for sdlc-studio itself (the Cooper model, RFC0017). The registry covers
two interfaces, one Primary each (D0379): the shipped skill, and this repository's own tooling, which
does not ship. A unit touching a shipped path is judged against the shipped skill's Primary. The
review seats that critique artefacts are a separate concern (RFC0016).

## Primary (the design target)

- [Maya Okafor](maya-okafor-founder-engineer.md) - solo founder-engineer; wants a disciplined,
  trustworthy lifecycle driven by an agent, not vibe-coding. Well-formed.
- [Rowan Achterberg](rowan-achterberg-skill-maintainer.md) - maintainer of this repository; Primary for
  the repository-tooling interface (hooks, push gate, CI, release cut and forward-port), which does not
  ship. Listed second, so a story minted with no persona still names the shipped skill's Primary.

## Secondary (served, never at the Primary's expense)

- [Jonah Reyes](jonah-reyes-team-lead.md) - small-team lead adopting sdlc-studio on an inherited
  brownfield repo; owns the `audit --profile repo` on-ramp, brownfield runbook, and `migrate` adoption path.
  Well-formed.

## Negative (deliberately not designed for)

- [Trevor Hale](trevor-hale-enterprise-pm.md) - enterprise delivery manager wanting a GUI,
  central governance, and a human gate on every change. A signal to decline, not a backlog.
  Well-formed.

## Superseded

The flat [`../personas.md`](../personas.md) is a **legacy appendix**, kept for history
only. It holds a June 2026 brownfield extraction of four user *categories* (operator,
consuming developer, executing agent, maintainer) with no declared Primary. It is not
the design target and is not maintained; this registry is.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 | Recorded the flat `personas.md` as a superseded legacy appendix (US0451); the PRD's Target Users now names this registry (US0450) |
| 2026-06-21 | Darren Benson | Seeded sdlc-studio's own Primary + Negative personas (dogfood of the Cooper template, RFC0017/CR0058) |
| 2026-07-16 | Claude Fable 5 (persona review, operator-directed) | Maya gains the cost-honesty frustration + sprint-report scenario (RFC0038/EP0048); Secondary Jonah Reyes added (brownfield adoption path); Trevor confirmed unchanged |
| 2026-10-19 | Claude Opus 5.5 (US1079) | Rowan Achterberg added as Primary for the repository-tooling interface beside Maya for the shipped skill, each card declaring its interface (D0379, after the D0374 stakeholder consult) |
