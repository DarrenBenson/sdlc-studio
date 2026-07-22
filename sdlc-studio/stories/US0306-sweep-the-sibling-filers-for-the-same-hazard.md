# US0306: Sweep the sibling filers for the same hazard

> **Status:** Done
> **Delivers:** CR0384
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/artifact.py,.claude/skills/sdlc-studio/scripts/file_finding.py
> **Epic:** EP0102
> **Points:** 2

## User Story

**As a** maintainer applying L-0154 to the fix US0305 delivers
**I want** every sibling artefact writer that takes free prose on the command line to gain the same
non-shell input path and the same hazard report
**So that** the next agent, reaching for `artifact.py new` instead of `file_finding.py file`, does
not hit the defect we just fixed in the other writer

## Context

L-0154: a defect found in one writer must be swept across every sibling writer before the run
closes. `artifact.py new` takes the same free-prose fields as `file_finding.py file` - `--summary`,
`--steps`, `--fix`, `--impact`, `--ac` - through the same command-line path, so it carries the same
hazard for the same reason. It is also the writer the skill's own guidance pushes agents towards
for artefact creation, which makes it the more likely caller of the two.

`artifact.py batch --spec` already reads a JSON file, so the sweep is partly a matter of extending
an existing habit rather than inventing one. The hazard report US0305 adds should be one shared
helper called by both writers, because two copies of a pattern list drift, and a drifted list is
the silent half of this defect all over again.

## Acceptance Criteria

### AC1: artifact.py new accepts the same JSON input path with the same fidelity

- **Given** a JSON document whose Steps and Summary fields contain backticks, a `$(...)` form and
  the literal text of a destructive git command
- **When** a Bug is created through `artifact.py new` using the non-shell input path
- **Then** the artefact reads back character for character as supplied, and HEAD and the index are
  unchanged after the call, matching US0305's guarantee field for field
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_artifact.py -k ArtifactJsonInputTests
- **Verified:** yes (2026-07-22)

### AC2: Both writers share one hazard implementation, so the two cannot drift

- **Given** the hazard patterns US0305 defines for an unbalanced backtick, a `$(` and a trailing
  backslash
- **When** the same offending field is passed through the flag path of `file_finding.py file` and
  of `artifact.py new`
- **Then** both report it, with the same wording, from a single shared helper rather than from two
  copies of the pattern list
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_artifact.py -k SharedHazardHelperTests
- **Verified:** yes (2026-07-22)

### AC3: A sweep test fails on any future prose writer added without the path

- **Given** the set of scripts exposing a free-prose flag such as `--steps`, `--fix`, `--summary`
  or `--impact`
- **When** the sweep test enumerates them from the scripts directory
- **Then** each in-scope writer is asserted to offer the non-shell input path, and a writer added
  later without one fails the test rather than being discovered by the next silent truncation
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_artifact.py -k ProseWriterSweepTests
- **Verified:** yes (2026-07-22)

## Open Questions

- CR0384 names only `file_finding.py` and `artifact.py` in its Affects, but a grep for free-prose
  flags across the scripts directory also finds `critic.py`, `close_owed.py`, `telemetry.py` and
  `sprint.py`. Whether those four are in the sweep, or are out of scope because they are not
  artefact filers, is not stated. AC3's enumeration needs that boundary decided before build, and
  the story is pointed at two writers on the CR's reading.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-22 | sdlc-studio | Groomed: user story and acceptance criteria authored |
