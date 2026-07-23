# Reviews - LATEST (anchor)

> **RUN-01KY7W1F (Sprint 1 of the three-sprint run) delivered all 19 units to Review.** The
> independent 3-reviewer adversarial panel found 7 defects (1 MAJOR), all fixed before sign-off;
> goal-verdict = ACHIEVED. RETRO0069 recorded. **Sign-off is owed and is the operator's** - the
> two-role gate (`review.two_role_after: 192`) holds Done. Not closed at the close command until
> sign-off lands.

## Where the pipeline is (2026-07-23)

Sprint 1 of a planned three-sprint run (~60 pts each) is BUILT and REVIEWED: 8 sprint-engine
epics, 19 stories, every story at Review, every epic In Progress pending sign-off. Goal ACHIEVED.

Sprint Goal: *stop eight sprint-engine tools being hand-driven - refine mints a plannable unit,
the seat brief and goal review become reproducible and amendable, the forecast prices the rung,
the delivery mode is a recorded choice, an artefact title has a deterministic correction, prose
reaches every creation script without a shell, and the plan sees built-and-committed work - each
independently verified, so sprints 2 and 3 run on instruments they can trust.*

## What shipped

- **EP0130** - `sprint plan` flags built-not-closed and excludes it from the build forecast.
- **EP0151** - the forecast prices the rung: a design run reads UNMEASURED, not the build rate.
- **EP0150** - atomic three-surface artefact retitle (ULID-safe after review).
- **EP0155** - refine mints a plannable, ungroomed-marked unit (Affects required or inherited).
- **EP0154** - `sprint plan` offers sequential/parallel delivery; test files count as coupling.
- **EP0146** - shell-safe `--fields-file` for critic/close_owed/sprint prose + hazard reporting.
- **EP0152** - goal review distinguishes an amendment (carry-forward) from a material change.
- **EP0153** - a deterministic seat brief, recorded with the verdicts; fields-file seats.

## How it was delivered

The batch is sprint.py-coupled, so the core was built serially; two file-disjoint clusters
(EP0155 refine, EP0150 retitle) ran as parallel worktree agents - exactly the sequential/parallel
split EP0154 itself now detects. Each epic committed as a green unit through the full gate.

## The closing review

Three fresh-context adversarial reviewers over disjoint slices of the ~2137-line engine diff.
7 defects found: 1 MAJOR (the design-rung forecast RELABELLED the marginal UNMEASURED but still
priced it at the build rate - a selection-bias hole, the test asserted the label not the value),
2 MEDIUM (retitle H1 missed ULID ids; refine's ungroomed marker failed MD022), 1 MEDIUM (an
amendment naming a requesting seat that never reviewed the prior goal), 3 LOW. All 7 fixed with
value-asserting tests. Sprint-review coverage recorded APPROVE (reviewer != author).

## Evidence

729 affected-suite tests green after the fixes; full gate green on every commit; drift 0. The
engine dogfooded itself: the mint-time Affects gate, the engagement-floor Refs guard, and the
noise ratchet (which caught 69 leaks two `--no-verify` merges had smuggled onto main) all fired.

## Next steps

- **Sign-off is owed and is the operator's.** `sprint close --retro RETRO0069 --apply-signoff
  --principal "..."`. RFC0051 records why an agent cannot honestly supply it.
- **Sprints 2 and 3** (~60 pts each) remain in the three-sprint run.
- Follow-ups on the backlog: BG0271 (gate unrunnable in a worktree), BG0272-0274 (review findings).

## Lessons

Assert the value, not the label - a test that checks a tool named its state does not prove it
reached it (the MAJOR). A `--no-verify` in one clone becomes another's red gate. A library
function that prints leaks into every test that calls it - return the notes, print at the CLI.
