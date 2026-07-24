# US0364: the refusal names the fallback source and reference-rfc.md documents the false-positive trade

> **Status:** Review
> **Delivers:** CR0357
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0126
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_rfc_accept_fallback.py, .claude/skills/sdlc-studio/reference-rfc.md

## User Story

**As an** operator refused an accept over a decision I know is settled
**I want** the refusal to say it came from the fail-closed fallback
**So that** I do not edit valid markdown, or stop believing the gate

> **Note on `Affects`:** the story was minted naming `scripts/rfc.py`. The accept gate does
> not live there - `rfc.py` is the decision-readiness digest. The refusal and both scan paths
> are in `scripts/transition.py`, and the header now says so.

## Acceptance Criteria

### AC1: the refusal names the fail-closed fallback as its source

- **Given** an RFC whose every register decision is closed, ending inside an unterminated
  fence whose appendix holds an example decision row reading Open
- **When** a transition to Accepted is refused
- **Then** the message says the list came from the fail-closed fallback and why, and an
  ORDINARY refusal does not say so - a clause printed on every refusal carries no information
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rfc_accept_fallback.py -k "fallback_path or came_from_the_fallback or does_not_claim"
- **Verified:** yes (2026-07-24)

### AC2: the trade is documented where the gate is described

- **Given** the trade was stated only in a source docstring, which an operator meeting the
  refusal never reads
- **When** `reference-rfc.md`'s accept step is read
- **Then** it describes the enforced gate, the override escape, the fallback, and names the
  trade as a rare false positive bought for the impossibility of a false negative
- **Verify:** shell grep -q 'false positive' .claude/skills/sdlc-studio/reference-rfc.md && grep -q 'fail' .claude/skills/sdlc-studio/reference-rfc.md && grep -q 'Decision-Override' .claude/skills/sdlc-studio/reference-rfc.md
- **Verified:** yes (2026-07-24)

### AC3: the override escape is named in the refusal, on both paths

- **Given** the sanctioned escape is a recorded `Decision-Override`, not `--force`
- **When** either refusal is printed
- **Then** both name the override and both say `--force` does not bypass it, and a recorded
  override clears the fallback refusal too - an escape that does not work on the path it
  exists for is a dead end being documented
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_rfc_accept_fallback.py -k "override"
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
