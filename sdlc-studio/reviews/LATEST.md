# Latest review anchor

<!-- close-status:begin -->
> **RUN-01KYNKDP closed stopped.** 47 unit(s) in the batch. **Sign-off is OWED and is the operator's** - the two-role gate holds Done.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **Retro:** RETRO0083 · **Goal verdict:** partial (per clause) · **Outcome:** delivered 47 of 48

## Where the pipeline is

RUN-01KYNKDP delivered 47 of its 48 units and 143 of 148 points: two efficiency epics, a dead
flag removed, and **36 bugs - the entire open bug backlog except two, both of which are named
rather than absorbed.** Open bugs went from 37 to 2.

**Sign-off owed.** The 12 stories stand at Review pending an adversarial pass by a context that
did not write them and the operator's sign-off as reviewer of record. The author records
neither; the two-role rule holds. The 36 bugs are Fixed, which is terminal for their type.

## What RUN-01KYNKDP changed

- **EP0189 (from CR0498)** - the close ceremony costs less than the work it certifies.
  `close --dry-run` reports every refusal of all seven steps in ONE read-only pass against a
  scratch copy, retro content included; `critic record|evidence|signoff` each take a whole batch;
  a missing argument is refused once, before any write; the retro scaffold passes its own
  validator; the close records the gate verdict it earned and reports its own cost.
- **EP0181** - `reconcile detect` reads the artefact corpus once per sweep rather than once per
  lookup, and the gate prints each lane's own seconds.
- **The whole RV0024 review residue (15 bugs)** plus the older backlog: measurement defects,
  corpus truth, and four specs describing a product other than this one.

## The measurements, not the impressions

| Instrument | Before | After |
| --- | --- | --- |
| Pre-commit gate | 427s | 319s |
| `reconcile detect` | 22.3s (777,732 file opens) | 1.3s |
| Close refusal discovery | 3 serial attempts, ~400s each | 1 read-only pass, 2m, all 15 named |
| `critic` spawns per close | 57 | 3 |
| Open bugs | 37 | 2 |

## Known divergences

**US0554's saving is SUSPENDED, by this sprint's own later repair.** BG0398 is correct: a
listing-only declaration is one module's statement about its own read, and honouring it
tree-wide silenced a second module's content read. Applying unanimity means this repo - which
has two readers of the `sdlc-studio` entry and one declarer - correctly withholds the narrowing.
The second reader's dependency is a fixture path the static scanner over-attributes to the real
tree. Filed as **BG0400** rather than papered over with a declaration that would not be true.

**91 seams, 72 of them unowned.** Same shape as the previous run: the batch is heavily
concentrated in `sprint.py`, `gate.py` and `critic.py` by design (the planner withheld parallel
delivery for exactly that reason). Reported rather than omitted.

**BG0350 was dropped, deliberately.** Closing it needs verdicts for an adversarial review that
did not happen. Recording them would manufacture the evidence the gate exists to demand.

## The finding that outlives the batch

Eight of the fifteen residue bugs were ONE shape: a guard that answered a narrower question than
it claimed, and reported the narrow answer as the broad one. `caller-check --unit` kept the last
value. `index_derived_issues` read four of five keys. The seam owner matched by substring. The
waiver report was built from stories only. Each returned a clean verdict over something it had
not looked at - and each had passing tests.

Three further findings did NOT reproduce (BG0368, BG0373, half of BG0371). Checking cost
minutes; repairing them would have meant changing correct code. In every case the finding's own
Proposed Fix named the thing that WAS missing - an assertion - and that is what shipped.

## Next steps

1. **Sign-off on the 12 stories is the operator's** - the adversarial pass has not been run by an
   independent context, so Done is not reachable from here.
2. **BG0400 first in the next batch.** Until it lands, every artefact-only commit pays the full
   suites - the saving US0554 delivered is real code sitting behind a measurement defect.
3. **BG0350 remains open** and will stay open until someone independent of the run consuming the
   result can do the pass.
4. **CR0496 and CR0497 are still unrefined** in the discovery backlog, along with 35 other items.
