# US0854: decompose the four 8-point stories and resolve the US0793/US0794 duplicate, so the delivery backlog is honest before the build run plans from it

> **Status:** Ready
> **Created:** 2026-09-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/stories
> **Epic:** EP0257
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** planner choosing the next batch
**I want** the delivery backlog to carry no unit whose size the tooling distrusts and no pair it cannot tell apart
**So that** the build run that follows plans from estimates worth having, rather than meeting the same two warnings this planner met and passing them on unchanged

## Acceptance Criteria

### AC1: the four 8-point stories are decomposed, and none of the parts is at the ceiling

- **Given** US0677, US0684, US0817 and US0840, each sized 8 - the point at which this project's own tooling says estimation reliability falls off
- **When** each is decomposed into parts that deliver the same scope
- **Then** no resulting unit is above 5 points, each part carries its own `Affects` and points, and the originals are superseded or retired with the decomposition named, so nothing is silently dropped in the split
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/backlog_triage.py`, raise the oversized ceiling instead of decomposing - the warning disappears, every unit still costs what it cost, and the estimate that was unreliable is now unreliable and unflagged
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/backlog_triage.py check --format json | python3 -c "import json,sys; d=json.load(sys.stdin); assert not [f for f in d.get('findings',[]) if f.get('kind')=='oversized'], 'oversized findings remain'"

### AC2: US0793 and US0794 are ruled the same change or genuinely distinct, with the ruling recorded

- **Given** the pair, which share four files and 50% of their wording
- **When** each is read against the other and against HEAD
- **Then** either one supersedes the other with the survivor named, or both carry a dated note saying why they are distinct despite the overlap - what is not acceptable is leaving the pair unjudged, because the next planner meets the same warning with no more information than this one had
- **Mutant:** in `.claude/skills/sdlc-studio/scripts/backlog_triage.py`, widen the duplicate similarity threshold until the pair stops matching - the detector then reports nothing and the two units stay in the backlog, which is the count falling by not looking rather than by deciding
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/backlog_triage.py check --format json | python3 -c "import json,sys; d=json.load(sys.stdin); assert not [f for f in d.get('findings',[]) if f.get('kind')=='duplicate'], 'duplicate findings remain'"

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-20 | sdlc-studio | Created via `new` (deterministic) |
