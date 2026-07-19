# Reviews - LATEST (anchor)

> Derived from the sprint-close review of **RUN-01KXX52Z** (clear the debt, make the tooling honest
> about what it covers, 2026-07-19, RETRO-0055). Supersedes the RETRO-0052 picture.

## Where the pipeline is (2026-07-19)

**RUN-01KXX52Z is built, verified and reviewed**: 6/6 units Fixed, 11 points, closing review
**APPROVED at round 2** (one REJECT, one repair round). Goal judged **achieved**.

The batch was bugs rather than stories, so Fixed is terminal and no two-role sign-off stands
between a unit and its close - the goal was reachable by the run itself.

**The delivery backlog is empty but for BG0212**, filed by this run. Discovery stands at 62
(59 CRs, 3 RFCs), 20 of them still awaiting a refine or triage. `close_owed` reports **none**:
318 units accounted for by retros, 261 grandfathered.

## What shipped

A debt phase and a bug phase.

- **The close-owed debt went 9 to 0**, three causes cleared three ways. **RETRO-0053** reconstructs
  the persona-layer sprint of 2026-07-16, which shipped in one commit and was never closed.
  **RETRO-0054** reconstructs the CR0322 sprint of 2026-07-17, which ran a full two-role close -
  review, repair round, re-verification, operator sign-off - and produced no retro artefact.
  **BG0201** was added to RETRO-0051's `Batch` line, where its prose had discussed it twice.
  Both new retros are marked RECONSTRUCTED and contribute nothing to calibration.
- **BG0202** - the confinement roster sweep reads a write mode wherever the call form puts it.
  Five modules gained a previously invisible append surface, all covered by another route: the
  detector was blind, the roster was not wrong. The bug named one.
- **BG0206** - a test module importing a sibling helper runs under both forms. 154 tests now run
  under the form that produced one `ModuleNotFoundError`. The guard is the point, not the one-line
  fix.
- **BG0209** - the shipped suite passes from an installed copy: 7 errors before, 7 clean skips
  after, dev repo still running all 144. The dev-repo rule now has one definition.
- **BG0207** - the RFC accept gate names every open decision, not just those before a broken fence.
  Inert across all 48 real RFCs; it was a false completeness claim, not a bypass.
- **BG0203** - the audit profile parser's not-found paths are pinned. **The filed premise was
  false** and the real defect was better.
- **BG0211** - a dead breakdown id no longer owes a close no close can give, and the cause is
  reported rather than silently forgiven.

Suite **3,208 green**, tools 236 green, drift 0, every commit gated.

## The CODE leg - two rounds

| Round | Findings | Outcome |
| --- | --- | --- |
| 1 | 1 MAJOR + 3 MINOR | REJECT |
| 2 | 3 MINOR | APPROVE |

**The MAJOR was in the guard written to prevent that class of defect.** BG0206's new sweep was
blind to `test_telemetry`, a module in its own directory, on two independent layers: the census
matched `ast.Import` only, so `from gitutil import git` was invisible; and fixing the census alone
would not have closed it, because that import sits inside a method and does not run at import time.

**Every round-2 finding was created by the round-1 repair - the third consecutive run with that
shape.** Two landed inside the very lines written to fix a round-1 finding: the mode-shape gate's
`break` lost `open('rt', 'w')`, and **the line that closed the MAJOR was itself deletable with
3,205 tests green**. The latter is the defect the author had caught in their own BG0209 work one
commit earlier, recurring inside the fix for it.

**Two of the six bugs were false as filed, and both were worth more once investigated.** BG0203's
two named survivors are both already pinned; the real defect is that a mutation run scoped below
its target's coverage manufactures survivors - 10 against one test file, 4 against the module's
actual tests, same code and same mutants. The author reproduced that error before spotting it.
BG0211's "zero epics are in this state" was wrong: there are 33.

## Next steps

- **CR0358** (High) - the close review is an unbounded repair loop. **Third consecutive run of
  evidence**, and its repair-regression detector would have flagged two of this round's three
  findings. Still the highest-value unbuilt item. Both rounds here were briefed neutrally by hand;
  nothing enforces that.
- **CR0363** (High, new) - a mutation run scoped below its target's coverage over-reports absence,
  and nothing warns. This produced BG0203 and was then repeated while investigating it.
- **CR0361** (M) - an agent meets the gates as refusals rather than as a briefing.
- **CR0351** (widened, M) - prose reaches 13 scripts through a shell argument, so a backtick
  silently empties the field it documents.
- Filed this run: **BG0212** (14 mutation survivors in `audit.py` outside the profile parser, the
  full 190-mutant enumeration recorded), **CR0363**.
- **CR0362** was hit live twice while filling in RETRO-0055: a finding fixed during the sprint can
  only be recorded as "declined", which is the wrong word for it.
- **CR0355** is **HELD until v5 launch** (D0046). Standing: **CR0278** - tokens not-yet-captured
  for interactive builds; this run's two review rounds cost ~113k and ~141k subagent tokens, which
  the point-based forecast does not model at all. Residual audit CRs (CR0280-CR0306) remain
  unrefined. Release freeze held.

## Lessons this run paid for

L-0134 to L-0139. **A narrow test command over-reports absence** - a mutation run scoped below its
target's coverage manufactures survivors, which then get filed as bugs. **A sweep that checks many
things in one process can be satisfied by the first one** - shared `sys.path` and `sys.modules`
state makes later cases pass on the back of earlier ones. **A finding is a hypothesis, not a
fact**: two of six here were false in their specifics. **A new guard needs a test of its
MECHANISM**, not just of the case that prompted it, because a guard is code and rots like code,
and a green suite says nothing about a guard nothing exercises. **Round 2's findings are made by
round 1's repair**: treat a repair as new code needing its own adversarial pass, never as the
closing of a loop.
