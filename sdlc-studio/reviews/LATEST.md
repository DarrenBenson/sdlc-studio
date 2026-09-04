<!-- close-status:begin -->
> **RUN-01M1H09S closed goal-reached.** 4 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **Run of record:** RUN-01M1NS3C - six gates that hold in the command people run, not only on
> the page that describes them. Eight units, 36 criteria, 150 mutants registered killed and two
> ruled equivalent (the two operator rulings). Goal **achieved**, every clause measured on main
> at 14a9d4d6. Sign-off is the operator's; the branch-protection edit is owed.

## THE HEADLINE: A PUSH FROM THIS CLONE NOW PAYS THE GATE, AND READS MAIN FIRST

For a whole release cycle AGENTS.md said two lanes bind at the push and release boundaries and
nothing invoked either: there was no `.githooks/pre-push`, the release boundary had no caller, and
a push completed in seconds. The required `ci` status check could never be satisfied by a direct
push, so the bypass line printed on every push and read as noise, and main stayed red for two days
with nobody looking. Both are closed under two rulings the operator made at plan sign-off, before
code: D0180 pays the full boundary gate on every push (ten to fifteen minutes until measured), and
D0181 keeps direct pushes gated locally. `.githooks/pre-push` (BG0641, 0da43495) binds
`gate.py --boundary push` for a branch ref and `release` for a tag ref, announces its cost before
paying it, records it after, runs behind the commit hooks' repo-locating scrub, and puts the gate's
output on the stream git shows the pusher. Before the gate it reads the latest push-triggered Lint
run on main (BG0642, 14a9d4d6) and refuses on any conclusion but success until the run id is
acknowledged once per clone; an unreadable or empty answer is named, never read as green, and never
blocks an offline push. `tools/boundary_roster.py` refuses a boundary AGENTS.md names with no
invocation behind it, and `enable-hooks.sh` names every tracked hook.

## WHAT ELSE LANDED

- **BG0643 (ee11bd3b)** - `file_finding.py file --verify` accepts the not-yet-written test it exists for (a class its file does not collect, a new method no method in that class is close to) and still refuses the same-leaf and in-class typos it can name.
- **BG0603 (d31383b5)** - `verify_ac.py lint --ratchet --bugs` refuses a stacked verifier at every non-terminal status, stories and bugs alike.
- **BG0644 (ba715bd2)** - the green-run noise ratchet is a per-module budget file: a selection is held to the sum of its modules' entries, a full run to `_total`, an unrecorded module contributes zero, and `budget-check` refuses a raised entry before the suite runs. This is the leak that turned main red for two days: a subset almost always printed fewer lines than the whole suite whatever it added.
- **BG0640 (77e40b35)** - the revert-check lane that examined nothing says so and says why; a crash still leads.
- **BG0647 (a77af6de, 652e451b)** - added in flight: the status integration test gathered THIS repository, 72 to 113 seconds and twelve ledger warnings into the noise count while a run was open, so every docs-only commit on this clone refused. It gathers a fixture now.
- **BG0650 (835c48f9)** - added in flight: the depth-count census read the entry-point denominator, so BG0641, the first artefact with a manual criterion and a derived field, refused every commit through the tools suite.

## HOW THE REVIEWS WENT

36 seat verdicts, 12 REJECTs, every one earned by execution and every one repaired and re-reviewed
to approval by the rejecting seat: BG0643 and BG0641 took three rounds, BG0642, BG0644, BG0603 and
BG0647 two. What the seats found that the author's checks could not: a noise budget calibrated on
this clone's open run; a gate whose lane name never reached the pusher's stream (git shows a
pre-push hook's stderr only, and a fixture that merged the streams could not tell); an enable-hooks
fixture writing `core.hooksPath` into a decoy repository; a fixture reaching the real `gh` through
an inherited PATH; a red tag push unpinned; a noisy-fixture test asserting one of two warning
sites. Escalations recorded by `critic record` for the operator: BG0643, BG0603 (split panel),
BG0644, BG0647, BG0641 (split, then three REJECTs), BG0642 (split, then two REJECTs).

## WHAT IS OWED

- **The reviewer-of-record sign-off** on all eight units - the operator's, or a named delegate outside this session: `sprint.py close --retro RETRO0113 --apply-signoff --principal <who>`.
- **The branch-protection edit** (BG0642 AC5, D0181): remove the `ci` required status check from main. Read back at close it still carries the check, so AC5 stays unticked and the AGENTS.md paragraph says owed.
- **LL0053 bit four units in one day**: the mutation ledger drops a target's rows on any byte change, and BG0642's edit to the hook emptied BG0641's thirty rows silently until the close dry-run. A ratchet that re-checks every earlier unit's evidence when a later unit touches its target is not filed yet; file it before the next batch.
- **Read next:** BG0649 (test_critic red alone), BG0645, BG0646, BG0648 (Medium, disclosed), CR0511's three new Lows (a refused push's duration seeding the estimate, hand-written depth counts, the unbounded `gh` read).
