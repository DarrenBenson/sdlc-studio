# Reviews - LATEST (anchor)

> Derived from the sprint-close review of **RUN-01KXWWM3** (bound the loop, make the close honest,
> 2026-07-19, RETRO-0052). Supersedes the RETRO-0051 picture.

## Where the pipeline is (2026-07-19)

**RUN-01KXWWM3 is built, verified and reviewed**: 4/4 units Fixed, 9 points, closing review
**APPROVED at round 2** (one REJECT, one repair round). The previous run, RUN-01KXVYGR, closed
goal-reached with 32 units signed off.

The batch was bugs rather than stories, so no two-role sign-off stands between a unit and terminal -
the goal was reachable by the run itself, unlike RUN-01KXVYGR's.

## What shipped

- **BG0205** - `refine` no longer seeds one story with its siblings' acceptance criteria. A
  multi-story breakdown seeds none and carries the request's criteria to the epic; a single-story
  breakdown is unchanged. The batch's unblocker.
- **BG0204** - a generated H1 has ONE definition, `sdlc_md.heading_title`. Dogfooded at this close:
  RETRO-0052's H1 comes from a Sprint Goal ending in a full stop and carries none.
- **BG0208** - a close completing with an `achieved` verdict records `goal-reached`. The cause was
  not a forgetful success path: `_close_handoff` short-circuits when a handoff exists, and the skip
  covered the outcome as well as the artefact.
- **BG0210** - close-owed can reach zero. A derived epic inherits its children's coverage; 35 epics
  forgiven, 48 to 13 on one tree, every survivor genuinely uncovered.

Suite **3,186 green**, tools **236 green**, drift 0, validate 0 errors, every commit gated.

## The CODE leg - two rounds

| Round | Findings | Outcome |
| --- | --- | --- |
| 1 | 1 MAJOR + 6 MINOR | REJECT |
| 2 | 5 MINOR | APPROVE |

**Not one finding was a misbehaviour of shipped code.** Every one was a claim wider than its
evidence, in commit messages, docstrings and mutation coverage. The MAJOR: the `type_ != "epic"`
guard - the single check stopping the close-owed relaxation becoming a blanket exemption - was
pinned by nothing, while the commit claimed all four branches were mutation-killed by their own
tests.

**The recurring shape, twice this sprint: a test that passes for an incidental reason.**
`_ac_heading`'s strip looked covered because every test used a long criterion, where truncation
removes the punctuation anyway; `close_owed`'s type guard looked covered because every test used
childless non-epics. Both survived deletion against the full suite. Mutating the guard is the only
way to find this - reading the test cannot.

Bounding the batch worked: 4 units and 9 points against the previous run's 32 and 89, and two review
rounds against five.

## Next steps

- **CR0358** (High) - the close review is an unbounded repair loop: no convergence check, no round
  ceiling, no cost surface, and the author writes the reviewer's prompt. Still the highest-value
  unbuilt item. Both rounds here were briefed neutrally by hand; nothing enforces that.
- **CR0351** (widened, M) - prose reaches 13 scripts through a shell argument, so a backtick silently
  empties the field it documents. File/stdin form is the fix; the detector catches 3 of 4 real
  corruptions and is defence in depth only.
- **CR0361** (M) - an agent meets the gates as refusals rather than as a briefing; five anticipatable
  refusals in one 3-point bug, each behind a full gate run.
- Filed this run: **BG0209** (seven shipped tests read this repo's own story files, so the payload
  fails its own suite when installed), **BG0211** (an epic whose breakdown declares a dead id is owed
  a close no close can give - latent, over-reporting direction), **CR0362** (a finding fixed during
  the sprint has no honest disposition; this retro records eleven repairs as "declined").
- **CR0355** is **HELD until v5 launch** (D0046) - the Claude for Open Source acknowledgement; the
  logo needs prior written permission and must never delay the release.
- Standing: **CR0278** - tokens not-yet-captured for interactive builds; the two review rounds cost
  ~115k and ~117k subagent tokens, which the point-based forecast does not model at all. Residual
  audit CRs (CR0280-CR0306) remain unrefined. Release freeze held.

## Lessons this run paid for

L-0127 to L-0129. **A test that passes for an incidental reason is not coverage** - mutate the guard,
because reading the test cannot find this. **When two paths answer the same question, extract before
the second answer drifts** - the H1 rule had three private copies, child-resolution had two. **A
fix's own argument constrains its implementation** - BG0208's case is that the archive is the
permanent record, so re-stamping `ended_at` while correcting `outcome` corrupted what it protected.
