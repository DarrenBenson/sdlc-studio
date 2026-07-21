# Reviews - LATEST (anchor)

> Derived from the close of **RUN-01KY1WCR** (RFC0048 option B: three tests were half the
> suite, 2026-07-21, RETRO-0063). Supersedes the RETRO-0062 picture.

## Where the pipeline is (2026-07-21)

**RUN-01KY1WCR is built and awaiting its review leg**: 4/4 stories, 12 points, EP0093 under
RFC0048. Stories past US0192 are held by the two-role gate, so they sit at Draft until an
adversarial pass is recorded and an independent reviewer of record signs off. Every unit was
mutation-checked during the build, not at the close - 9 mutants killed across the four.

## What shipped

A commit now costs **93.1s instead of 196.7s**, with no coverage given up.

| | Before | After |
| --- | --- | --- |
| Full unit suite | 153.1s | **78.6s** |
| `run_gate` (paid on every commit) | 35.6s | **6.95s** |
| Whole pre-commit gate | 196.7s | **93.1s** |

- **US0284** - `GateRealWrapperTests` ran the full ~35s gate over this repo **twice**: once to
  assert the result's shape, once to discover that `main` returns 0 or 1. It now runs once,
  lazily on first demand, and `main`'s exit-code mapping is pinned against a stub. One unstubbed
  end-to-end run is kept deliberately - it is the only thing proving the 15 real lanes wire up.
  `test_gate.py` 72.2s -> 36.2s; the stubbed test alone 35.451s -> 0.001s.
- **US0285** - the never-rolled evidence-log pin drove 5,050 records through `record()` one at a
  time. It now seeds the log past the cap in one write and appends a single record: identical
  failing condition, attributable to that one call. 10.4s -> 0.259s.
- **US0286** - `engagement_floor.detect` ran `git log --grep` **once per shipped unit** (842
  subprocesses), and `sdlc_md.project_override` re-parsed `.config.yaml` on **every call** (4,495
  times in one validate run). One git pass, and the parse memoised on file **content**. Lanes:
  engagement-floor 10.96s -> 0.57s, constitution 10.18s -> 1.45s, validate 8.24s -> 0.19s.
- **US0287** - RFC0048 **D6 closed**: a 120s per-commit budget, the operator's number, recorded
  with the 93.1s baseline it was chosen against. Advisory always; reports the **trend** against a
  dated baseline, and reads the **latest** run rather than the median.

## The premise was wrong three times, and measuring caught it each time

This is the run's real lesson, and it is uncomfortable: **every one of the three substantive
stories was planned on a premise the build falsified.**

1. **US0286** was planned as "three lanes re-walk the artefact corpus". Walking the corpus is
   0.105s of an 11.0s lane. The real causes were per-unit git subprocesses and per-call YAML
   re-parsing - two different bugs in two files, and `gate.py` was never touched.
2. **US0285** was planned to drive the pin with a small injected cap. `roll_jsonl`'s `max_lines`
   default binds at definition time, so that test would have passed whether or not the log
   rolled. A story about making a test cheaper nearly shipped a vacuous one.
3. **US0287** was planned to add a lane to the shipped `gate.py`. The timing history it reads is
   written by repo-only hook machinery, so the lane would have been permanently silent in every
   consuming project.

Each was caught by measuring or reading before writing, and each correction is recorded in the
story with its reason rather than quietly implemented as something else.

## Evidence

- `gate --format json` over this repo is **byte-identical** before and after US0286, across all
  15 lanes - stronger than the unit suite, which cannot see the real corpus.
- **9 mutants killed** during the build: exit-code mapping; a second end-to-end run (fails two
  pins, and takes 71.3s, so it shows in the clock too); a roll added to `telemetry._append`;
  path-only cache key (the staleness bug); dropped batch-commit rule; per-id git loop restored;
  budget blocking; budget reading the median; budget dropping its baseline.
- One behavioural narrowing recorded rather than buried: one-pass git attribution takes candidate
  ids from the word-bounded regex rather than git's `--grep` substring match, so a commit
  mentioning `US02845` no longer attributes to `US0284`. AC4 pins the two functions against each
  other rather than asserting they agree.

## Next steps

- **This run's review leg**: an adversarial pass over the sprint diff, then an independent
  reviewer-of-record sign-off, before the four stories can reach Done.
- **RFC0049 / RFC0050** - test strategy at planning, and an adversarial pass over the plan before
  the build. RFC0050's risk lens subsumes RFC0049 option B; do not build both.
- **BG0238** (High) - per-unit mutation evidence is never captured; the close lane reads the
  previous sprint's report. This run killed 9 mutants and, again, none is recorded anywhere but
  prose.
- **CR0381** (filed this run) - `artifact.py new` accepts a pipe-separated `--ac` and emits a
  malformed AC silently; it cost all four stories a hand-rewritten AC block at plan time.
- **BG0237**, **BG0236**, **CR0380** open. Standing: **RFC0046** needs D1 closed or an override;
  **CR0319** is the release cut. Release freeze holds.

## Lessons this run paid for

A plan's premises decay between writing and building, and on this run all three decayed the same
way - the plan named a plausible cause that measurement did not support. Profile before
optimising, and read the binding rules of the thing you intend to inject before designing a test
around injecting it.
