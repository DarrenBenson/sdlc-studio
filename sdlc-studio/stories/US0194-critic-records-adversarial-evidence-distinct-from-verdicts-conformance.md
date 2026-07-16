# US0194: critic records adversarial evidence distinct from verdicts; conformance critiqued requires evidence plus a non-author sign-off with recorded delegate chain and the embedded decision brief

> **Status:** Ready
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-workflow-personas.md
> **Epic:** EP0064
> **Points:** 5

## User Story

**As** Jonah Reyes (team lead)
**I want** the two-role review model (seat subagent finds, independent principal signs) enforced as machinery
**So that** no unit closes on an uninformed or self-controlled sign-off, and the delegation chain is on the record

## Acceptance Criteria

### AC1: evidence and verdict are distinct; the critiqued stage requires both

- **Given** a unit reviewed by a seat subagent and a sign-off recorded by a principal
- **When** critic.py records the adversarial pass and conformance evaluates the critiqued stage
- **Then** critic.py records the adversarial pass as evidence distinct from the verdict; conformance critiqued requires evidence + a sign-off whose principal differs from the author AND from the authoring session's subagents
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_critic.py -k Evidence

### AC2: a delegated sign-off carries its chain; a self-controlled delegate is refused

- **Given** a sign-off delegated by the operator to a named principal in a separate trust boundary
- **When** the delegated verdict is recorded
- **Then** Delegated sign-off carries the recorded chain (operator -> delegate, trust boundary named); an authoring-session subagent as delegate is refused loudly
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_critic.py -k Delegate

### AC3: the sign-off request embeds the decision brief

- **Given** a run ready for the reviewer-of-record ask
- **When** the sign-off request is composed
- **Then** The sign-off request embeds the CR0318 decision brief (deliveries, critic REJECTs + repairs, gate/cost evidence) with approve/hold/delegate paths
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_critic.py -k SignoffBrief

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-16 | Claude Fable 5 | Design rung: ACs made executable |
