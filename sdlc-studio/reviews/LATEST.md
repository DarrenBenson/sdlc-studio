# Latest review anchor

> **Review record:** RV0023 (2026-07-28) - RUN-01KYKVZM: three rounds, three rejects, and the
> repair rate that did not fall
> **Retro:** RETRO0081 · **Goal verdict:** partial · **Outcome:** closed with known issues

## Where the pipeline is

The delivery backlog was repopulated by the 2026-07-27 audit and is being worked down by a series of
efficiency sprints. RUN-01KYKVZM is the third: 31 units, 102 points, 0 blocked, closed with a partial
goal verdict. The two sprints before it (RUN-01KYJZGZ, RUN-01KYAHY9) are closed and signed off.

**Sign-off owed.** The 23 stories of RUN-01KYKVZM stand at Review pending the operator's sign-off as
reviewer of record. The author does not record it; the two-role rule holds.

## What RUN-01KYKVZM changed

- **EP0178** - a lane refuses a unit whose acceptance criteria it cannot read, runs those criteria
  before returning, and returns the proof the test strategy assigned it. A unit adding a mechanism
  names the caller that consumes it, or states there is none and names the follow-up.
- **EP0179** - the retro curates a fixed-size carried lesson set with a displacement rule, the sprint
  reads it at plan and in every lane brief, and the close reports delivery against overhead.
- **EP0180** - waivers are read and reported, validate can be pointed at one artefact, and `init`
  derives the artefact tree from the shipped type list.
- A **trust boundary** was found open and closed: the lane path executed a shell verifier from
  externally ingested content that `verify_ac` refuses. Reproduced live, repaired with one shared
  predicate, mutation-pinned, and mirrored to the installed copy.

## Known divergences

Eleven defects are carried, every one a defect in a unit this batch delivered rather than a
pre-existing finding. Two are High - **BG0378** (the transition verb sets a terminal status without
consulting the criteria floor, so only the commit recording it is refused) and **BG0379**
(caller-check silently passes a unit whose mechanism surface its own verifier emptied). The rest -
BG0365, BG0366, BG0367, BG0368, BG0369, BG0371, BG0372, BG0373, BG0374 - are Medium or Low with
recorded workarounds. Nothing is P0.

## The finding that outlives the batch

Three independent review rounds each returned REJECT, and each repair produced new defects: 17, then
3, then 3. **The rate did not fall.** Every round's damage came from one author repairing their own
review findings at pace with no independent verdict between attempts. Thirteen of the seventeen
round-one majors were **seam defects between units** - four directly contradicting pairs in one
batch, every one of which passed its own acceptance criteria, because a lane reads one unit and
review is the first actor that reads two.

That is what **CR0468** (seam ownership at decomposition), **CR0469** (a stakeholder-panel goal
verdict deciding whether a defect can be left), **CR0470** (bookend the goal review at plan and
close) and **CR0471** (name a sprint by its goal) exist to address. They are the most valuable output
of the sprint.

## Next steps

1. Operator sign-off on RUN-01KYKVZM as reviewer of record.
2. Open the next sprint on BG0378 and BG0379 first, repaired by a context that did not write them.
3. Refine CR0468 and CR0469 - they address the failure this review measured, which the 31 units did
   not.
