# US0310: reference-sprint.md states the concurrent-write hazard where it states the single-writer rule

> **Status:** Draft
> **Delivers:** CR0388
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md,.claude/skills/sdlc-studio/reference-review.md
> **Epic:** EP0105
> **Points:** 2

## User Story

**As an** agent about to commit while an independent reviewer is working in the same tree
**I want** the concurrent-write hazard written down beside the single-writer rule I already read
**So that** the rule covers review time as well as build time, instead of leaving the more
dangerous of the two windows undocumented

## Context

CR0388's remaining criterion, unallocated by the first decomposition of that request and added
once the grooming pass found it.

The single-writer rule is already written down, and only for a `mutation.py` run during a build.
The hazard at REVIEW time is not covered anywhere, and review is precisely when an author is
making ceremony commits (retro, review anchor, findings) that touch nothing the reviewer is
working on and therefore feel safe.

State the corrected mechanism, not the one CR0388 originally filed. The staged file did not
carry a hand-applied mutant: a helper directory of symlinks turned a shell redirect into a write
through the symlink into the live tree. Documentation that describes only the mutant case would
leave a reader confident about the wrong hazard, which is worse than silence. See also
[[LL0039]].

US0307 and US0308 build the guard. This story is the written rule the guard enforces, and it
carries no code.

## Acceptance Criteria

### AC1: The single-writer rule covers review time, not only a build-time mutation run

- **Given** reference-sprint.md, which today states the single-writer rule for a `mutation.py`
  run during a build
- **When** the rule is read
- **Then** it also states that an independent review is a concurrent-writer window, and names
  the ceremony commits an author typically makes during one
- **Verify:** grep "review is a concurrent-writer window" .claude/skills/sdlc-studio/reference-sprint.md
- **Verified:** yes (2026-07-22)

### AC2: The documented mechanism is the corrected one

- **Given** CR0388's correction, that the observed incident was a redirect writing through a
  symlink rather than a hand-applied mutant going stale
- **When** the hazard is described in either reference file
- **Then** the description names the redirect-through-a-symlink mechanism, and does not claim
  a staged mutant was the cause
- **Verify:** grep "symlink" .claude/skills/sdlc-studio/reference-review.md
- **Verified:** yes (2026-07-22)

### AC3: The rule states why a green suite is not evidence the tree is clean

- **Given** that the observed incident was caught only because the staged file broke the suite,
  and that a surviving mutant by definition leaves the suite green
- **When** the rule is read
- **Then** it states that a passing gate does not establish that no concurrent write is staged
- **Verify:** grep "green" .claude/skills/sdlc-studio/reference-review.md
- **Verified:** yes (2026-07-22)

### AC4: Both reference files point at the guard rather than restating it

- **Given** US0307 and US0308 implement the declared-window guard
- **When** either reference file describes the rule
- **Then** it names the window commands as the enforcement path, so the prose and the mechanism
  cannot drift into describing different rules
- **Verify:** grep "window" .claude/skills/sdlc-studio/reference-sprint.md
- **Verified:** yes (2026-07-22)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
