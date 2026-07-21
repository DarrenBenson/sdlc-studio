# Reviews - LATEST (anchor)

> Derived from **RUN-01KY1WCR** (RFC0048 option B, 2026-07-21, RETRO-0063).
> Supersedes the RETRO-0062 picture.

## Where the pipeline is (2026-07-21)

**RUN-01KY1WCR is built, adversarially reviewed, REJECTED once, and repaired.** 4/4 stories,
12 points, EP0093 under RFC0048. The four stories sit at Draft until a reviewer of record signs
off - the two-role gate holds everything past US0192.

## What shipped

A commit costs **93.1s instead of 196.7s**, with no coverage given up (suite 3,409 -> 3,422
tests). `run_gate`, which every commit pays, went **35.6s -> 6.95s**.

- **US0284** - `test_gate.py` ran the full gate over this repo twice: once for its shape, once to
  learn that `main` returns 0 or 1. One lazy run now serves both; `main` is pinned against a
  stub. 72.2s -> 36.2s.
- **US0285** - the never-rolled evidence-log pin drove 5,050 records through `record()`. It now
  seeds the log past the cap in one write and appends one. 10.4s -> 0.259s.
- **US0286** - `engagement_floor.detect` ran `git log --grep` once per shipped unit (842
  subprocesses); `project_override` re-parsed `.config.yaml` on every call (4,495 times per
  validate run). One git pass; the parse memoised on content digest.
- **US0287** - RFC0048 **D6 closed**: a 120s per-commit budget against a measured 99s baseline,
  advisory, reporting trend against a dated baseline.

## The adversarial review found three MAJORs, and it was right about all of them

Two were **false claims written in prose to justify my own code** - the failure this repo keeps
hitting (L-0146), now three sprints running.

1. **A shipped library path was made to raise.** Narrowing `project_override`'s read to
   `except OSError` let `UnicodeDecodeError` escape: one legacy-encoded byte in a consuming
   project's config turned 7 blocking lanes red with a message that never named the file. My
   comment said "same answer as before". Now catches `(OSError, ValueError)` and warns.
2. **The budget lane reported drift that was not drift.** The hook recorded a `total` on every
   commit, including docs-only ones that skip the 85s suites, so the live gate read
   `-85% since`. The hook comment claiming "the expensive lanes ran either way" was false. Now
   recorded only when the suites ran; the series is purged of the non-comparable entry.
3. **The guard for US0284's own saving did not guard.** It matched the literal
   `gate.run_gate(str(REPO))`, but the test US0284 deleted was spelled `gate.main([...])`.
   Pasting it back verbatim into a neighbouring class doubled the runtime with both guards
   silent. Now a module-scope refusal every route passes through, tested in both directions.

Six MINORs also accepted: the baseline was a hand-sum the check could not reproduce (now the
hook's own 99s, with the ~19% same-machine variance stated as a known limit); US0286 AC4
over-claimed "did not narrow"; AC3's verifier could not compare before with after and is now
manual; the parse cache was unbounded (now digest-keyed, capped).

## Evidence

- `gate --format json` byte-identical before and after US0286 across all 15 lanes, reproduced
  independently by the reviewer.
- **9 mutants killed** in the build, **3 more** proving the repairs (non-UTF-8 config, docs-only
  recording, the deleted test replayed verbatim).
- The reviewer could not break: the byte-identical claim, any new test's ability to fail, `$SECONDS`
  arithmetic, or US0284's "no assertion lost".

## The premise was wrong three times

All three substantive stories were planned on a premise the build falsified: US0286's "lanes
re-walk the corpus" (it is 0.105s), US0285's injected cap (would have passed either way),
US0287's shipped lane (would have been permanently silent). Each was caught by measuring or
reading first. This is the evidence base for **RFC0050**'s plan-time adversarial pass.

## Next steps

- **Sign-off** by a reviewer of record, then the four stories reach Done.
- **RFC0050** / **RFC0049** - RFC0050's risk lens subsumes RFC0049 option B; do not build both.
- **BG0238** (High) - per-unit mutation evidence is still never captured; 12 mutants died this
  run and none is recorded outside prose.
- **CR0381**, **BG0237**, **BG0236**, **CR0380** open. **RFC0046** needs D1 or an override;
  **CR0319** is the release cut. Release freeze holds.

## Lessons

A plan's premises decay; profile before optimising. A guard must be tested for its mechanism,
not the case that prompted it. Narrowing an exception clause is a behaviour change, not a tidy-up.
