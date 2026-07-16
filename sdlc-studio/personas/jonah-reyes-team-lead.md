# Jonah Reyes

> A specific person, not a type. The Secondary is served fully, but never at the Primary's expense.

## Quick Reference

| Attribute | Value |
| --- | --- |
| **Cast role** | Secondary |
| **Role** | Team lead of a three-developer product team adopting sdlc-studio on an inherited codebase |
| **Context** | Brownfield repo, mixed human-plus-agent workflow, delivery cannot stop for a process migration |

## Who They Are

Jonah leads a small team that inherited a working but under-documented codebase. The team already
ships through PRs and CI; what it lacks is a trustworthy account of what the system *is* - the
README lies, the original authors are gone, and every new feature starts with archaeology. Jonah
wants the discipline sdlc-studio brings, but he answers for a delivery schedule: adoption has to
happen alongside shipping, not instead of it, and it has to work for three humans and their agents
holding the same rules.

## End Goals

*What they are trying to accomplish, most important first. The design is judged against these.*

1. Get a validated specification out of the existing code - a migration blueprint the team can trust, not documentation theatre
2. Adopt the lifecycle incrementally - try it read-only first, turn on gates one at a time, never bet the schedule on a big-bang migration
3. Hold humans and agents to the same discipline - one artefact workspace, one set of gates, whoever (or whatever) is doing the work
4. Upgrade safely as the skill evolves - conventions and schemas migrate mechanically, with judgement calls reported rather than guessed

## Experience Goals

*How they want to feel while using it.*

- Safe to trial - the first run reads the repo and files findings; it does not rewrite anything
- Confident the extracted spec reflects the code, because tests validated it, not because prose asserts it
- Unembarrassed in front of the team - the tool's gates catch drift before a teammate does

## Behaviours & Context

- **Environment:** a shared repo with PRs and CI; each developer pairs with an agent in a terminal
- **Frequency:** adoption work weekly around delivery; the lifecycle daily once gates are on
- **Proficiency:** solid engineer-manager, terminal-fluent; delegates deep spec work to the agent and reviews the artefacts

## Frustrations

*What trips them up with the current tools or status quo.*

- Inherited docs that lie: the spec says one thing, the code does another, and nothing flags the gap
- All-or-nothing process tools: useful only after a migration nobody has time to run
- Three people (and three agents) each inventing their own workflow in the same repo
- Upgrades that silently change conventions mid-flight and leave the artefact workspace inconsistent

## Scenario

*A short narrative of this persona using the product to reach an End goal.*

Jonah points `review generate` at the inherited repo: it bootstraps the workspace, reviews
architecture, quality, and security read-only, and files its findings as bugs and CRs he can
triage with the team. Convinced, he runs `prd generate` and validates the extracted blueprint by
running the tests against the existing implementation, then turns on the reconcile and gate checks
one at a time as the team's PR habits absorb them. Months later a new skill release lands;
`migrate` converts what is mechanical, reports the three calls that need his judgement, and the
workspace stays consistent while the team keeps shipping.

---

- **Primary:** see `maya-okafor-founder-engineer.md` - Jonah is served, but never at Maya's expense; a feature that helps Jonah by adding ceremony for Maya is declined.
- **Negative persona:** see `trevor-hale-enterprise-pm.md` - Jonah wants shared discipline held by the tool; Trevor wants central governance held by a bureaucracy. The line between them bounds this card.
