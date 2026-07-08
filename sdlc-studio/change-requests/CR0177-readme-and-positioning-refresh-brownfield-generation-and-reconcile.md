# CR-0177: README and positioning refresh: brownfield generation and reconcile as proof of the anti-vibe-coding philosophy

> **Status:** Complete
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0017](../epics/EP0017-positioning-and-evidence.md)
> **Priority:** Medium
> **Type:** Improvement
> **Raised-by:** Lena Marsh (Product amigo)
> **Depends on:** none blocking (team-shape section gated on CR0167-CR0169 shipping)

## Summary

Reframe the README headline around the two genuinely differentiated capabilities: brownfield
generation (point it at existing code, get a validated, test-verified blueprint) and
reconcile (self-policing drift detection between artefacts and reality) - presented as proof
of the anti-vibe-coding philosophy, not as the philosophy itself.

## Motivation

The current README (and the v3.5.0 "antidote to vibe coding" masthead) leads with breadth:
the command catalogue up top reads as parity with lookalike SDLC frameworks, of which there
are many. The two capabilities no lookalike has - generate mode's test-validated migration
blueprint, and reconcile's census-based self-policing - are below the fold. Positioning
should invert that: the philosophy is the umbrella, the two differentiators are its proof,
and breadth is a supporting fact rather than the lead. The tool is also moving to a
team-based story (small human teams, larger agentic teams, trunk-based flow), but that claim
must wait for the supporting schema CRs to ship - marketing ahead of capability is the exact
vibe-coding energy the masthead disavows.

## Scope

**In scope**

- README restructure per the hard constraints in the acceptance criteria below.
- Masthead/tagline continuity: builds on the existing anti-vibe-coding tagline, does not
  replace it.
- `review generate` (CR0175) presented as the try-it-first on-ramp once that command exists;
  copy drafted now, published with the command.
- Team-shape story (small human teams, larger agentic teams, trunk-based flow) drafted now,
  published only after CR0167/CR0168/CR0169 ship.

**Out of scope**

- Renaming the tool, changing install flows, or touching SKILL.md routing.
- Publishing performance or comparison claims ahead of RFC0025/CR0178 numbers.
- Website/blog assets beyond the README (separate effort if wanted).

## Acceptance Criteria

Hard constraints on the reframe:

- [ ] a. The anti-vibe-coding message stays central and becomes the umbrella: files over
      chat, evidence over intent, verification over confidence. Brownfield and reconcile are
      presented as proof of that philosophy, not as the philosophy itself.
- [ ] b. The tool does not read as brownfield-only. Greenfield (`prd create` and the
      interview flow) remains a first-class, equally visible front door. The framing is one
      discipline, two entry points: start clean or take over existing code, with the same
      evidence-first workflow either way.
- [ ] c. The command catalogue moves below the fold; breadth reads as parity with lookalike
      frameworks, while the two differentiators plus the philosophy read as a category of
      one.
- [ ] The team-shape story appears only once CR0167, CR0168, and CR0169 have shipped, not
      before (release-gated copy, checked at publish time).
- [ ] The on-ramp paragraph (try `review generate` on your existing repo first) lands with
      or after CR0175, never before.
- [ ] Style gates pass (lint-style, neutrality); no capability claim in the new copy lacks a
      shipped feature behind it.

## Dependencies

| Artefact | Relationship |
| --- | --- |
| CR0167, CR0168, CR0169 | Gate the team-shape section only; the core reframe proceeds now |
| CR0175 | Gates the on-ramp mention |
| CR0176 | Lite profile answers the ceremony objection in the same copy |
| RFC0025 / CR0178 | Future numbers strengthen the claims; absence of numbers means absence of quantified claims |

## Effort

**S.** Copy and structure work against explicit constraints; the release-gating discipline
is the only novel mechanism.

## Risk

Positioning drift: each future feature PR nudges its pet command back above the fold until
the catalogue leads again. Mitigation: the three constraints above are written as acceptance
criteria so a future README change can be reviewed against them; consider a doc-freshness
advisory noting the fold line.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Lena Marsh (Product amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Lena Marsh (Product amigo) | Full scope drafted; three hard constraints encoded as ACs |
