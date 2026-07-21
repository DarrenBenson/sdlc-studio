# RFC-0048: Make the test suite cost-effective without lowering the floor: tier it by measured value, and review tests adversarially

> **Status:** Draft
> **Decomposed-into:** EP0093
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

## Summary

This project is now deep brownfield: 3,243 shipped tests, 243 tool tests, 15 gate checks, 11
pre-commit lanes, ~136 seconds of unit suite on every code commit. The gate is the reason no
false claim has shipped, and it has caught real defects in every sprint. It is also the largest
single cost in a sprint after the review loop, and it grows every time the project succeeds,
because each fix adds tests and nothing ever removes any.

Two questions are unsettled, and the naive answer to each is actively dangerous.

**Where is the cost actually?** Measured, not assumed:

| File | Wall time | Tests | Share of suite |
| --- | --- | --- | --- |
| `test_gate.py` | 56.4s | 198 | **41%** |
| `test_sprint.py` | 17.4s | 201 | 13% |
| `test_telemetry.py` | 11.0s | 69 | 8% |
| everything else (~60 files) | ~51s | ~2,775 | 38% |

**Three files are 62% of the runtime and 14% of the tests.** This is not a 3,243-test problem;
it is a three-file problem, and the cost is concentrated in tests that shell out to real
subprocesses rather than in test count. Any plan that starts by "consolidating tests" in general
is optimising the 38% while leaving the 62% alone.

**Is a test worth its runtime?** The honest answer needs evidence, because human judgement about
which tests are redundant is demonstrably wrong in BOTH directions on this codebase:

- **Tests that look redundant are sometimes the only pin.** BG0210's `type_ != "epic"` guard was
  covered by nothing across 3,180 tests. `in_dev_repo`'s second clause survived the whole 197-test
  gate suite. The depth-parity branch survived all 3,238.
- **Tests that look like coverage are sometimes vacuous.** Four times in one session a test of
  mine passed for an incidental reason. The worst was written specifically to pin a defect and
  could not reach it: re-introducing the defect left 326 tests green.

So the selection criterion cannot be "does this look redundant". It has to be **measured kill
yield** - which mutants a test kills, and at what runtime cost. The mutation gate already produces
exactly that data and is currently used only per-diff.

## The second problem: tests are the one artefact we do not review adversarially

We adversarially review specs. We adversarially review code. **We do not review tests** - they are
reviewed only incidentally, when a code reviewer happens to mutate a guard and notice the test
does not fail.

The evidence from RUN-01KXX52Z and RUN-01KXXERR is stark. Across both runs the **code** fixes
survived review essentially intact. Every MAJOR finding in both closing reviews was about a
**test**:

| Run | MAJOR finding | Class |
| --- | --- | --- |
| RUN-01KXX52Z r1 | the sibling-import sweep was blind to a module in its own directory | guard did not guard |
| RUN-01KXXERR r1 | `requirements` re-parsed prose; its pinning test passed on a coincidence | test passed incidentally |
| RUN-01KXXERR r2 | the replacement test was tautological - could not reach the defect it named | test could not fail |

Plus MINORs of the same class: an anti-vacuity sweep that was itself vacuous; a docstring claiming
both halves of a check were load-bearing when one was unpinned; two ACs whose `Verify` pointed at
tests that asserted something else.

**The pattern is not that the code is wrong. It is that the evidence for the code is wrong**, and
nothing in the process is pointed at the evidence. A test is the artefact that decides whether
everything else is trusted, and it is the only one nothing adversarially attacks.

## Design Options

### For cost (D1, D2)

- **Option A - Tier the suite.** A fast lane on every commit (the ~51s of pure-logic tests) and
  the full suite on push/CI and at close. Cheapest to build, and US0268 already established the
  cheap-first principle in the hook. Risk: a commit can be green against a lane that did not run
  the 62%, so the tier boundary has to be drawn by what a change TOUCHES, not by what is fast.
- **Option B - Attack the three files directly.** `test_gate.py`'s 56s is subprocess-dominated:
  it runs the real gate end to end, repeatedly. Convert the repeated end-to-end runs into one
  run whose result is asserted many times, keeping one true end-to-end case. Highest value per
  hour of work, no coverage change, and it does not need a policy decision.
- **Option C - Parallelise.** The suite is serial. Nothing about it is inherently so.
- **Option D - Retire by measured kill yield.** Run a full mutation enumeration per module, find
  tests whose kill set is a strict subset of another's, and retire the subset. Genuinely reduces
  coverage debt rather than moving it - and is the only option that can safely DELETE anything.
  Most expensive to establish, and needs the mutation gate to be cheap enough to run broadly
  (see CR0363, which is about the same gate lying when scoped too narrowly).

### For test quality (D3, D4)

- **Option E - A `test` audit lens profile.** The audit surface already has pluggable lens
  profiles (`project`, `skill`, `repo`, `code`). Add one whose lenses are the failure modes this
  session produced: *can this test fail?* (mutate the guard it names), *does it reach the code it
  claims to?*, *does its docstring describe what it asserts?*, *is it green for an incidental
  reason?* Fits existing machinery, runs on demand, no new ceremony.
- **Option F - A per-unit adversarial test review at close**, alongside the code review. Strongest
  coverage, but adds a round to a loop CR0358 already exists to bound - and the review loop is
  the single biggest cost in a sprint. Buying test quality with review rounds may be the worst
  possible currency.
- **Option G - Mechanise the specific check instead.** Every finding above would have been caught
  by one rule: **a new or changed test must be shown to fail against a mutant of the code it
  claims to pin.** That is `mutation.py` pointed at the diff's tests rather than its source, and
  it is deterministic - no reviewer, no round, no judgement.

## Recommendation

**B + G first, then E. Defer D. Reject F.**

- **B** because it is 41% of the cost, needs no policy decision, and changes no coverage.
- **G** because it converts the recurring failure into a deterministic gate. Four times this
  session a human-or-model reader failed to notice a test could not fail; a mutant would have
  noticed every time, and did, on each occasion anyone bothered to run one.
- **E** as the qualitative backstop for what G cannot mechanise (a docstring that misdescribes
  what it asserts is not a mutation-detectable property).
- **Defer D** until the mutation gate is cheap and honest enough to trust at scale - CR0363 is
  the prerequisite, because a mutation run scoped below its target's coverage over-reports
  absence, and retiring tests on that signal would delete real coverage.
- **Reject F** because it pays for test quality in review rounds, which is the currency we are
  shortest of.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Cost: attack the three heavy files (B), tier the suite (A), parallelise (C), or some combination - and in what order | Resolved: Option B first, and re-measured before planning: the cost is far more concentrated than the RFC's file-level table showed. test_gate.py is now 72.2s (was 56.4s - it grew 28% in two days for 3 extra tests), but 71.1s of that is TWO tests that both run the real gate over this repo end to end (test_real_wrappers_run_and_shape 35.56s asserting shape; test_main_returns_exit_code 35.54s asserting only that the exit code is 0 or 1). test_telemetry.py is 10.4s of which one test is 10.12s (5,050 sequential records to prove the log is never rolled). test_sprint.py's 19.3s is diffuse - ~100ms per test across 238 tests - with no hotspot. So THREE tests are 81.2s of a 153.1s suite: 53%. Attack those three first (test-only, no coverage change, no policy decision), then the diffuse test_sprint fixture cost separately if it still earns it. Additionally in scope, beyond option B's literal test-side wording: run_gate itself is 35.6s, of which engagement-floor (11.0s), constitution (10.2s) and validate (8.2s) are 83%, each independently re-walking the same ~1,800-artefact corpus. That 35.6s is paid again by the pre-commit gate lane on EVERY commit, so sharing the corpus is worth more than the test change it enables - it is the refactoring-for-efficiency case, taken deliberately rather than absorbed. |
| D2 | Do we ever RETIRE a test, and if so is measured mutation kill-yield the only sanctioned criterion (D)? | Open |
| D3 | Is a changed test required to fail against a mutant of the code it pins (G) - advisory, or a blocking gate? | Resolved: Advisory, close-scoped (option G). A changed test is mutation-checked against the code it pins at the close, over the sprint diff only; it reports and never blocks. RUN-01KXZQF0's evidence: ~40 min wall-clock, ~zero model tokens, and it found 2 test gaps that the full 3,300-test suite, per-story AC verification and both adversarial review rounds missed. The cost case is against blocking or per-commit placement; BG0212's 6-of-15 equivalent mutants are why a survivor must not refuse a close. -> CR0377 |
| D4 | Does a `test` audit lens profile earn its place (E), or is G sufficient? | Open |
| D5 | Does archival apply here? Index archival exists for artefacts (`archive.py`, `indexes.archive_after`) and four indexes are over the threshold. Is there an equivalent for tests, or is that a category error? | Open |
| D6 | What is the acceptable per-commit gate budget? Without a target number, every future guard is individually justifiable and the ratchet never stops | Resolved: 120 seconds per code commit, declared against a measured baseline of 93.1s on 2026-07-21 (skill-tests 78.1s + gate 6.95s + guards 8.0s), recorded in sdlc-studio/.config.yaml as gate_budget with that baseline beside it. Pre-EP0093 the same commit cost 196.7s, so the budget sits below what a commit cost two days earlier. ~29% headroom: enough to absorb machine variance without the lane becoming noise that gets scrolled past, tight enough that a jump the size of test_gate.py's recent +28% trips it. ADVISORY ALWAYS, never blocking - a wall-clock check on a loaded or shared machine must not refuse a correct commit, the same call D3 made for mutation. The check reports the TREND against the dated baseline rather than a bare pass/fail, because reporting only 'under budget' is exactly how test_gate.py grew 56.4s to 72.2s in two days unnoticed: it was under every ceiling the whole time. It reads the LATEST recorded run, not the median, since a median over a ten-run window still read ~152s two commits after the suite had dropped to 79s. Implemented in tools/gate_timing.py and .githooks/pre-commit rather than the shipped gate.py: the hook machinery is repo-only, so a shipped lane would be permanently silent in every consuming project. -> US0287 |

## Evidence and prerequisites

- Timings measured 2026-07-19 on this repo, serial, bytecode purged.
- **CR0363 DELIVERED** (RUN-01KXZQF0, 2026-07-20): the run now reports its selected test
  files, warns when a referencing test file falls outside the selection, and honours
  `--ignore`/`--deselect` - the manufactured-survivor prerequisite for D2 and G is met.
- **First live cost/yield data for D3/D6** (RUN-01KXZQF0 close, RETRO0060): three close-time
  evidence runs cost ~40 min wall-clock (~40s suite per mutant, 24-mutant ceiling) and ~zero
  model tokens - the token cost of a sprint lives in the review rounds and the build, not
  here. Yield was concentrated and real: the run found 2 test gaps that the full 3,300-test
  suite, per-story AC verification AND two adversarial review rounds all missed (an
  `assertNotEqual(rc, 0)` satisfied by a `None` return; an unpinned empty-directory branch).
  Read for D3: the value case is strong at the CLOSE, diff-scoped and bounded; the cost case
  is against blocking or per-commit placement, which would move a wall-clock cost onto every
  commit for value that concentrates on the behaviour-dense diff. Read for D6: the per-commit
  budget already bites - this sprint paid the ~150s suite roughly seven times before any
  mutation ran.
- **CR0376** (no-mutatable-surface close should skip loudly, not error) and **CR0377** (derive
  the minimal covering test command from the selection scan, halving wall-time per mutant)
  are the cost levers this data points at.
- **CR0358** (the close review is an unbounded repair loop) is why F is rejected: the review loop
  is already the largest cost in a sprint and is itself unbounded.
- **BG0212** established that a mutation survivor is not automatically a coverage gap - 6 of its
  15 were equivalent mutants. Any retirement criterion built on survivor counts must exclude
  equivalents or it will delete tests that are pulling their weight.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-19 | sdlc-studio | Drafted: measured cost distribution, the test-review gap, options and recommendation |
| 2026-07-20 | rfc resolve (operator decision) | resolve: D3 - Advisory, close-scoped (option G). A changed test is mutation-checked against the code it pins at the close, over the sprint diff only; it reports and never blocks. RUN-01KXZQF0's evidence: ~40 min wall-clock, ~zero model tokens, and it found 2 test gaps that the full 3,300-test suite, per-story AC verification and both adversarial review rounds missed. The cost case is against blocking or per-commit placement; BG0212's 6-of-15 equivalent mutants are why a survivor must not refuse a close. |
| 2026-07-20 | rfc resolve (operator decision) | resolve: D6 - Sequenced, not yet numbered: set the per-commit gate budget AFTER option B lands. Attacking the three heavy files (test_gate.py 56s, test_sprint.py 17s, test_telemetry.py 11s = 62% of runtime, 14% of tests) changes no coverage and needs no policy decision, so the budget gets set against the improved baseline rather than ratifying today's bloated ~150s. The RFC's own risk stands until then - without a number every future guard is individually justifiable - so D6 stays live with option B as its trigger, it is not deferred indefinitely. |
| 2026-07-21 | rfc resolve (operator decision) | resolve: D1 - Option B first, and re-measured before planning: the cost is far more concentrated than the RFC's file-level table showed. test_gate.py is now 72.2s (was 56.4s - it grew 28% in two days for 3 extra tests), but 71.1s of that is TWO tests that both run the real gate over this repo end to end (test_real_wrappers_run_and_shape 35.56s asserting shape; test_main_returns_exit_code 35.54s asserting only that the exit code is 0 or 1). test_telemetry.py is 10.4s of which one test is 10.12s (5,050 sequential records to prove the log is never rolled). test_sprint.py's 19.3s is diffuse - ~100ms per test across 238 tests - with no hotspot. So THREE tests are 81.2s of a 153.1s suite: 53%. Attack those three first (test-only, no coverage change, no policy decision), then the diffuse test_sprint fixture cost separately if it still earns it. Additionally in scope, beyond option B's literal test-side wording: run_gate itself is 35.6s, of which engagement-floor (11.0s), constitution (10.2s) and validate (8.2s) are 83%, each independently re-walking the same ~1,800-artefact corpus. That 35.6s is paid again by the pre-commit gate lane on EVERY commit, so sharing the corpus is worth more than the test change it enables - it is the refactoring-for-efficiency case, taken deliberately rather than absorbed. |
| 2026-07-21 | rfc resolve (operator decision) | resolve: D6 - 120 seconds per code commit, declared against a measured baseline of 93.1s on 2026-07-21 (skill-tests 78.1s + gate 6.95s + guards 8.0s), recorded in sdlc-studio/.config.yaml as gate_budget with that baseline beside it. Pre-EP0093 the same commit cost 196.7s, so the budget sits below what a commit cost two days earlier. ~29% headroom: enough to absorb machine variance without the lane becoming noise that gets scrolled past, tight enough that a jump the size of test_gate.py's recent +28% trips it. ADVISORY ALWAYS, never blocking - a wall-clock check on a loaded or shared machine must not refuse a correct commit, the same call D3 made for mutation. The check reports the TREND against the dated baseline rather than a bare pass/fail, because reporting only 'under budget' is exactly how test_gate.py grew 56.4s to 72.2s in two days unnoticed: it was under every ceiling the whole time. It reads the LATEST recorded run, not the median, since a median over a ten-run window still read ~152s two commits after the suite had dropped to 79s. Implemented in tools/gate_timing.py and .githooks/pre-commit rather than the shipped gate.py: the hook machinery is repo-only, so a shipped lane would be permanently silent in every consuming project. |
