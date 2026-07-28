# RV-0023: RUN-01KYKVZM: three rounds, three rejects, and the repair rate that did not fall

> **Date:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Run:** RUN-01KYKVZM
> **Retro:** RETRO0081
> **Goal verdict:** partial

## Scope

The whole of RUN-01KYKVZM: 31 units, 102 points, 0 blocked - EP0178 (a defect is caught by the lane
that made it), EP0179 (the learning loop and what it costs), EP0180 (the friction the previous close
exposed), plus 8 bugs. Three independent review rounds, each in a fresh context that did not write
the code, each pinned to a named commit sha.

## Findings

### The review, in three rounds

| Round | Reviewer | Verdict | What it found |
| --- | --- | --- | --- |
| 1 | independent panel | REJECT | 17 majors: a lane trust boundary, a two-parser contract split over 475 units, a caller resolver approving nonsense, an inert verb, and 13 seam defects |
| 2 | independent re-review of the repair | REJECT | 2 of 4 repairs closed with mutations killed; 1 pinned by no test at all; 1 over-claimed on a number the author reported without measuring |
| 3 | independent re-review of that repair | REJECT | the author's "guards green" was false - `gate.py` was failing on the four bugs just closed; an over-broad predicate; a vacuous verifier created by the repair meant to remove vacuous verifiers |

**The headline is the rate, not any single finding.** Each repair produced new defects: 17, then 3,
then 3. The rate did not fall across rounds. Every round's damage came from one author repairing
their own review findings at pace, with no independent verdict between attempts. That is the
strongest evidence this sprint produced, and it is an argument about the loop rather than about any
of the 31 units.

### Goal verdict: partial

| Clause | Verdict |
| --- | --- |
| A defect is caught by the lane that made it | **partial** - the lane work landed and two units blocked themselves, but BG0379 leaves one of the five caller criteria unable to fail, and BG0378 leaves the terminal refusal at the gate rather than at the verb |
| The loop measures what it costs | **achieved** - the ratio reports its bound and names what it excludes; BG0366 and BG0372 are narrower and do not falsify it |
| A lesson carried forward is read by the work that would repeat it | **achieved** - the carried set reached the plan and every lane brief; BG0365 is storage fragility |

Held at partial deliberately. Clause 1's original blocker (BG0370) is genuinely closed and verified
live on a fresh project, but BG0379 arrived in its place, and upgrading the verdict on the author's
own word after a day in which three of the author's claims were falsified is the exact error the
rounds kept finding.

### Verified state at close

```text
gate.py --root .                 gate: PASS (every lane, incl. validate + engagement-floor)
validate.py check                checked=1618 errors=0
skill suite                      4,868 OK
tools suite                      440 OK (2 skipped)
lint-style / links / budgets / neutrality   all 0
reconcile.py detect              drift_items=0
forward-port.sh --check          in sync
```

Each figure is the output of the named command, run at the closing commit. The round-3 finding that
mattered most was that an earlier version of this list was asserted from a subset - the npm lint
lanes - while `gate.py`, which the pre-commit hook runs, was red on the four bugs the author had
just closed.

### Carried, with priorities

**High:** BG0378 (the transition verb sets a terminal status without consulting the criteria floor,
so only the commit recording it is refused), BG0379 (caller-check silently passes a unit whose
mechanism surface its own verifier emptied).

**Medium/Low:** BG0365, BG0366, BG0367, BG0368, BG0369, BG0371, BG0372, BG0373, BG0374 - each a
defect in a unit this batch delivered, each with a recorded workaround, none blocking a user.

Nothing is P0. Nothing corrupts data or blocks a user without a workaround.

### Raised by the operator during the close

- **CR0468** - decomposition creates seams between units and nothing owns them. 13 of the 17 round-1
  majors were seam defects, including four directly contradicting pairs in one batch, every one of
  which passed its own acceptance criteria. A lane reads one unit; review is the first actor that
  reads two.
- **CR0469** - a sprint-goal-achieved verdict judged by a stakeholder panel, deciding whether a
  defect can be left or must be addressed. Ten defects were graded by the author with no rubric and
  two were wrong in opposite directions when tested.
- **CR0470** - bookend the goal review: at plan, will this content deliver the goal; at close, did
  it, given what was not delivered and what was raised.
- **CR0471** - name a sprint by its goal, not only by its run id.

Taken together these are a better outcome than the batch. CR0468 and CR0469 in particular address
the failure this review actually measured, which the 31 units did not.

## Verdict

**Closed with known issues, at the operator's direction**, goal verdict `partial`. The four High
defects the operator directed be fixed before close (BG0370, BG0375, BG0376, BG0377) are fixed, each
pinned by a mutation that kills it. Eleven defects are carried with recorded priorities, two of them
High. The gate is green on every lane, both suites pass, and the installed copy is in sync.

Author: Claude Opus 5. **Reviewer of record: the operator.** Not self-approved; the two-role rule
holds, so the delivered units stand at Review until that sign-off is recorded.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Written at the close of RUN-01KYKVZM after three review rounds |
