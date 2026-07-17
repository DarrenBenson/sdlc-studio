# US0257: build refine --into with multi-parent link support (children_of, asymmetry gate, back-links) and docs

> **Status:** Review
> **Verification depth:** functional
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Epic:** EP0083
> **Points:** 5
> **Delivered-by:** claude-opus-4-8

## User Story

**As an** operator refining a backlog of small requests
**I want** a request's stories to decompose into an existing shared epic
**So that** a batch of small requests shares one container instead of minting a singleton epic each

## Acceptance Criteria

### AC1: --into adds stories to an existing open epic; a terminal, non-epic or unknown target is refused with nothing minted

- **Given** an open epic and a refinable request
- **When** `refine apply --request CRxxxx --into EPxxxx` runs
- **Then** the request's stories are minted under that epic (Parent links, the request's Decomposed-into, and the rolled-up Derived Point Total all wired both ways), and a terminal, non-epic or unknown `--into` target is refused with nothing minted
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_two_backlogs.py -k refine_into
- **Verified:** yes (2026-07-17)

### AC2: the link core resolves multiple parents so a shared batch epic satisfies the two-backlog symmetry and derivation gates

- **Given** a batch epic delivering more than one request (one Parent line per request)
- **When** `children_of` and the link-asymmetry gate resolve it
- **Then** every parent resolves both ways and the epic reads as decomposed from each request, with no link-asymmetry or undecomposed drift
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_two_backlogs.py -k refine_into_adds_stories
- **Verified:** yes (2026-07-17)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
