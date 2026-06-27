# US0045: agentic-wave worktree doctrine doc enrichment (CR0126)

> **Status:** Ready
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Epic:** EP0010
> **Persona:** Dani (Engineering)
> **Depends on:** -

## User Story

**As** an agent running agentic waves on any project
**I want** the worktree doctrine documented in the skill
**So that** I do not rediscover the stale-HEAD and merge pitfalls the hard way

## Context

### Persona Reference

**Dani (Engineering)** - the engineering amigo, owner of the deterministic
tooling and the mechanical gates that keep a sprint honest. Dani cares that
hard-won execution lessons live in the skill, where every project inherits
them, rather than being relearned per project.
[Full persona details](../personas.md#dani-engineering)

### Background

This story implements CR0126, a documentation change to
`reference-agentic-lessons.md`. The rules were distilled from a consuming
repo's project lessons log (EP0037-0041), which repeatedly lost time to
worktree-based agentic waves. The file already covers Wave-1-sequential and the
two-parallel sweet spot, but four hard-won rules surfaced in that log are not
yet in the skill, so every new project rediscovers them:

- Commit per wave, not per epic: `Agent({ isolation: 'worktree' })` branches
  from a cached HEAD captured at an earlier agent-tool invocation, not current
  main, so a later wave's agents cannot see files an earlier wave produced.
- Single-agent-on-main is the default; parallel worktrees are the exception
  with explicit opt-in criteria.
- Cherry-pick worktree branches by scope narrowness, not story points or
  number.
- Wave 1 forward-declares every shared type, interface, and hub-file addition
  the later waves consume.

These are agentic-execution doctrine, not project facts, so they belong in the
skill. The change is documentation only. The mechanical pre-launch check and the
`repo_map.py`-derived scaffold file set raised in the CR stay advisory and are
out of scope here.

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type        | Constraint                                                                                        | AC Implication                                                                |
| ------ | ----------- | ------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| Epic   | Determinism | Doctrine belongs in the skill where every project inherits it, not relearned per project (LL0008) | The doc states the rules explicitly enough that an agent can follow them, AC1 |
| PRD    | Performance | Not applicable - skill-internal change                                                            | None                                                                          |
| PRD    | Security    | Not applicable - skill-internal change                                                            | None                                                                          |

---

## Acceptance Criteria

### AC1: the four worktree-wave rules are documented

- **Given** `reference-agentic-lessons.md`
- **When** the doc is read
- **Then** it documents commit-per-wave (HEAD includes all prior waves before any worktree branch) with the `git apply` recovery, single-agent-on-main as the default with the three parallel opt-in criteria, cherry-pick by scope narrowness, and the Wave-1 forward-scaffold rule
- **Verify:** `manual`
- **Verification target:** functional
- **Verified:** no

### AC2: anchor links resolve and the style guard passes

- **Given** the edited `reference-agentic-lessons.md`
- **When** the link checker and style guard run
- **Then** both pass with no broken anchors and no style violations
- **Verify:** `bash -lc "cd /home/darren/code/DarrenBenson/sdlc-studio && npm run lint:links && npm run lint:style"`
- **Verification target:** functional
- **Verified:** no

> **Verification target tiers:** `functional` (single round-trip – default) | `conversational` (multi-turn / multi-step session continuity) | `soak` (live traffic over a window) | `live` (operator-confirmed in production). End-to-end ACs default to `conversational`; production-affecting ACs default to `soak`; ACs shipping behind a flag awaiting promotion default to `live`. See `reference-test-best-practices.md#verification-depth-tiers`.

---

## Scope

### In Scope

- The doc enrichment of `reference-agentic-lessons.md`: the four rules
  (commit-per-wave with `git apply` recovery, single-agent-on-main default plus
  three parallel opt-in criteria, cherry-pick by scope narrowness, Wave-1
  forward-scaffold) plus the Agent Prompt Template reference to the
  forward-scaffold enumeration.

### Out of Scope

- Any script or mechanical pre-launch check (HEAD-includes-all-prior-waves) -
  the CR keeps this advisory.
- Deriving the forward-scaffold file set from `scripts/repo_map.py` - also
  advisory in the CR.

---

## Technical Notes

This touches one file, `.claude/skills/sdlc-studio/reference-agentic-lessons.md`.
Add the four rules to the Wave Structure section and reference the
forward-scaffold enumeration from the Agent Prompt Template guidance so it lands
in generated prompts. Where the CR names a mechanical check or a
`repo_map.py`-derived file set, document it as advisory and name the reason, per
the CR's own determinism criterion. Carry the CHANGELOG `[Unreleased]` entry in
the same commit (LL0004). No anchors elsewhere in the skill should break.

### API Contracts

Not applicable - documentation-only change, no external API.

### Data Requirements

None - no persisted state, the change is prose in one reference file.

---

## Edge Cases & Error Handling

| Scenario                                                                                 | Expected Behaviour                                                                                            |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| The Agent Prompt Template guidance is updated but omits the forward-scaffold enumeration | Treated as incomplete: AC1 fails, because the rule must land in generated prompts, not just the prose section |
| The commit-per-wave rule is documented without the `git apply` recovery pattern          | Treated as incomplete: AC1 fails, the recovery path is part of the rule                                       |

> **Minimum edge cases:** 2 for API stories, 2 for others

---

## Test Scenarios

- [ ] Read `reference-agentic-lessons.md` and confirm all four rules plus the `git apply` recovery and the three parallel opt-in criteria are present and unambiguous (AC1).
- [ ] Run `npm run lint:links && npm run lint:style` and confirm both pass with no broken anchors and no style violations (AC2).

> **Minimum test scenarios:** 2 for API stories, 2 for UI

---

## Dependencies

### Story Dependencies

None.

### External Dependencies

None.

---

## Estimation

**Story Points:** 2
**Complexity:** Low

---

## Rollback Envelope

> Required when `affects_production_runtime: true`; optional otherwise. See `reference-story.md#rollback-envelope`.

**Affects production runtime:** false

*Not applicable - story does not change runtime behaviour.*

---

## Open Questions

None.

---

## Revision History

| Date       | Author | Change                                               |
| ---------- | ------ | ---------------------------------------------------- |
| 2026-06-27 | Dani   | Authored to Ready (design rung, breakdown of CR0126) |
