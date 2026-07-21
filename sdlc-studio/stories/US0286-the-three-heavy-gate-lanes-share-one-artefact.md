# US0286: The three heavy gate lanes stop re-parsing config and re-shelling git

> **Status:** Done
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py,.claude/skills/sdlc-studio/scripts/engagement_floor.py,.claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py,.claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py
> **Depends on:** US0284
> **Epic:** EP0093
> **Points:** 5
> **Persona:** repo maintainer (dogfooding operator)

## User Story

**As a** repo maintainer running the gate on every commit
**I want** the gate to stop repeating work it has already done
**So that** the 35.6 seconds every commit pays becomes a few

## Context

**The plan's premise was wrong, and profiling falsified it before a line was written.** The
plan said the three heavy lanes each re-walk the same ~1,800-artefact corpus, and that sharing
one parse would collapse the cost. Walking the corpus is not the cost: `artifact_files` is
0.105s of an 11.0s lane. Two entirely different causes were:

- **engagement-floor (11.0s)** ran `git log --grep` once per shipped unit - **842 git
  subprocesses**, 10.5s of the lane spent waiting on a process that re-read the same history
  each time.
- **validate (8.2s) and constitution (10.2s)** were dominated by PyYAML: `project_override`
  re-read and re-parsed `.config.yaml` on **every call**, 4,495 times in a single validate run,
  making YAML scanning ~75% of both lanes.

So the fix is two changes in two other files, and `gate.py` is not touched at all. The
`Affects` and the title are corrected to what was actually built.

This remains the only story in the epic touching product code, and the highest-value one: the
pre-commit hook pays this on every single commit, and the close pays it again.

The hazard is unchanged in kind, only in location: a cached parse that outlives its file would
let the gate pass on a config it never read. Fail-open staleness is the same class as the
vacuity defects this project keeps finding. The cache is therefore keyed on the file's
**content**, not its mtime - staleness becomes impossible by construction rather than by
argument - and AC2 and AC5 attack that failure directly rather than the happy path.

## Acceptance Criteria

### AC1: an unchanged config is parsed once, not once per call

- **Given** a project config read repeatedly, as every lane does per artefact
- **When** `project_override` is called many times over an unchanged file
- **Then** the YAML is parsed once and the rest are served from the memo
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::ConfigParseCacheTests::test_repeated_reads_of_one_config_parse_it_once
- **Verified:** yes (2026-07-21)

### AC2: an edited config can never be served from the cache

- **Given** a config edited in place to the SAME byte length, immediately after being read - the
  case an mtime-and-size key can collide on inside the clock's granularity
- **When** it is read again
- **Then** the new value is returned, because the key is the file's content
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::ConfigParseCacheTests::test_an_edited_config_is_never_served_from_cache
- **Verified:** yes (2026-07-21)

### AC3: every lane reports what it reported before

- **Given** the same tree, before and after the change
- **When** all 15 lanes run
- **Then** each reports the same count, status, blocking flag and detail
- **Verify:** manual capture `gate --format json` at the pre-change commit and at HEAD over the
  same tree and diff them. Deliberately NOT the unit suite: a suite run only shows the lanes
  pass NOW, and cannot compare before with after, so pointing this AC at `pytest test_gate.py`
  made it a verifier that could not fail for the criterion it named (found by the adversarial
  review; the vacuity class of US0226-0228).
- **Verified:** manual - byte-identical, confirmed independently by the reviewer
- **Verified:** yes (2026-07-21)

### AC4: the one-pass git attribution agrees with the per-id function

- **Given** a history containing every shape the attribution rule turns on - solo subject, batch
  subject with and without a `Refs:` trailer, an id only in the body, a hyphenated spelling
- **When** the one-pass map and the per-id function are both asked about each id
- **Then** they agree on every well-formed id, and where they deliberately differ the
  difference is the documented word-boundary narrowing - the batch pass never attributes MORE
  than the per-id function, only less
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_engagement_floor.py::BatchGitAttributionAgreesTests
- **Verified:** yes (2026-07-21)

### AC5: the saving itself is pinned, and the hazards are mutation-checked

- **Given** the new tests
- **When** the change is reverted piecewise as mutants
- **Then** each is killed: keying the parse cache on path alone (the staleness bug), dropping the
  batch-commit rule from the one-pass attribution, and reverting the one-pass git query to a
  per-id loop
- **Verify:** manual apply each mutant and record the kill before the change is accepted
- **Verified:** manual

### AC6: the saving is measured, not assumed

- **Given** the 35.6s `run_gate` baseline and per-lane split measured on 2026-07-21
- **When** the change is delivered
- **Then** the measured time and new split are recorded against it
- **Verify:** manual record the measured time and per-lane split at delivery; a standing
  threshold is machine-dependent.
- **Verified:** manual

## Delivery evidence (2026-07-21)

`run_gate` **35.6s -> 6.95s**. Per lane: engagement-floor **10.96s -> 0.57s** (842 git
subprocesses -> 1), validate **8.24s -> 0.19s**, constitution **10.18s -> 1.45s** (both from the
config memo). Full suite **107.8s -> 78.1s** on top of wave 1, so **153.1s -> 78.1s** across the
sprint so far.

Equivalence: `gate --format json` over this repo is **byte-identical** before and after across
all 15 lanes - the strongest available evidence that no lane's answer moved, and stronger than
the unit suite alone, which cannot see the real corpus.

Mutants killed: 3. Keying the parse cache on path alone fails AC2's test; dropping the
batch-commit rule fails AC4's agreement test and an existing understatement test; reverting the
one-pass git query to a per-id loop fails the one-git-log pin.

The AC4 wording above was corrected after the adversarial review: it originally claimed the
rewrite "did not narrow or widen attribution", which contradicted the function's own docstring
saying it narrows. A differential fuzz over 37 ids and 27 commit shapes found 6 disagreements -
4 the documented narrowing, 2 a commit message carrying a literal record separator. All are in
the under-attributing direction, which is the safe one for a blocking gate.

One deliberate behavioural narrowing, recorded rather than buried: candidate ids in the one-pass
attribution come from the judged-id regex (word-bounded) rather than git's `--grep` substring
match, so a commit mentioning `US02845` no longer attributes its files to `US0284`. That is
stricter and correct, and AC4's test pins the two functions against each other on real commit
shapes so the claim is checked rather than asserted.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-21 | sprint (build) | Premise corrected: profiling showed the cost was per-unit git subprocesses and per-call YAML re-parsing, not corpus re-walking. Title, Affects and ACs rewritten to what was built. |
