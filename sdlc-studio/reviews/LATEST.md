<!-- close-status:begin -->
> **RUN-01M0CT8P closed goal-reached.** 6 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **Run of record:** RUN-01M0CT8P - six instruments that reported verdicts their own evidence did
> not support. Six units, 21 points, 36 criteria, delivered and signed off by the panel. The goal
> was reached. It took FIVE plan-review rounds and SIX delivery-review rounds, and that number is
> the thing to read, not the points.

## THE HEADLINE: THE MARGINAL YIELD OF A REVIEW ROUND IS NOT FLAT, AND THIS RUN MEASURED IT

Delivery round 1 caught a defect that would have shipped: **BG0593's entire production change
could be deleted with all 916 tests in its own file still green**, because the tests rebuilt the
mechanism in a private helper. That single finding justifies the whole apparatus.

**Rounds 2 to 5 caught only defects in the EVIDENCE apparatus** - test-plan rows stale against
rewritten criteria, a mutant registered against a file its plan row did not name, a criterion
whose kill came from a sibling test, seven criteria carrying two live ledger rows each after
retract-and-re-register. All real. None a defect in shipped behaviour, and most manufactured by
the registration ledger rather than found in the code.

The cost: **11,034,109 main-thread tokens for 21 points - 525,434 per point** against a 44,427
forecast, and against a corpus history whose worst previous row is 353,810. Subagent tokens are
not counted and the rounds ran as subagents, so that understates it. 2,839 minutes against a
960-minute appetite.

**D0146 is the operator's ruling on that measurement**: the delivery round cap drops from 6 to 2
and round 3 onward files rather than blocks. It lands AFTER this run - relaxing the gate refusing
your own work is L-0344, and it reads green afterwards either way.

## THE ROOT CAUSE OF THE UNIFORM CEREMONY, MEASURED

`route.estimate` takes 0.40 of its weight from a complexity read over **every function in every
declared file**, so a two-line change to `sprint.py` inherits `sprint.py`'s worst function. Over
all 603 bugs: **87% tier `full`**, `code` and `risk` both saturated for 48%, and half the corpus
inside a six-point score spread (p25 48, median 50, p75 54).

CR0510 scoped the REVIEWER to changed hunks and left the ESTIMATOR reading whole files. **CR0549**
is that unfinished half. **CR0550** records that the test-plan gate is date-scoped only, so a
project finding it heavy can only switch it off wholesale - and states the dependency: band-scoping
buys nothing until CR0549 lands.

The A/B D0131 set up has now reported: **31 test-plan review passes against 6 code reviews, a
ratio of 0.19.** EP0207's claim was that reviewing the test costs a fraction of reviewing the code.

## WHAT ROUND 6 ESTABLISHED

All five earlier rounds ruled **CLOSED** with execution behind each, and **NONE MOVED** - the first
round in this run where no repair had shifted its defect sideways. 33 of 33 nameable mutants
executed and killed by their own named verifier; per-unit revert-checks land on exactly the
criteria the depth fields predict.

Its one blocker is the transferable lesson: **`changelog.d/BG0593.md` still described the symlink
design AC3 forbids by name**, three commits after the redesign removed it. A fragment written at
the first commit describes the design that existed then, and nothing re-reads it. Caught only by
applying the fragment's own sentence as a mutant and watching the unit's test kill it.

## WHAT THE GATES CAUGHT THAT I DID NOT

The workspace census refused three stacked `Verify:` lines on one criterion; the style guard
refused ten internal bug ids in shipped `scripts/`; `run-suite --check` refused a stale verdict
three times, each time because I had edited the tree after recording it; `critic record` refused
every finding carrying no origin tag; `critic repair` refused a disposition that matched no
finding it raised; and `review-batch` ESCALATED four units for a non-converging repair without
being asked.

`_rejected_unanswered` - BG0598's own fix - gated this run's close, correctly, until every REJECT
carried a complete repair record.

## OPEN, AND WHY

| Id | State |
| --- | --- |
| BG0601 | Open. The dry-run class sweep truncates each probe to its first two elements - a demonstrated bypass, not a hypothesis |
| BG0602 | Open. The close checklist derives its roster from an `_ck_` name prefix, so a renamed check leaves it silently |
| BG0603 | Open. `lint_stacked_verifiers` runs at Draft and Ready but not at Open, the status a bug occupies for its whole delivery |
| CR0549 | Filed. `route.estimate` scores whole files - the reason ceremony cannot be proportional here |
| CR0550 | Filed. The test-plan gate is date-scoped only |
| BG0599, BG0600 | Open. Carried from RUN-01M05A5M, untouched |
| CR0547, CR0548 | Filed. The revert-check gate, and derived `Verification depth` |
| BG0586, BG0588, BG0592 | Open High. Untouched by this run |

**Four units were ESCALATED** for a non-converging repair (BG0595, BG0596, BG0597, BG0598 - two
REJECTs each). The escalations stand on the record; the run continued to handoff, which is the
designed behaviour.

**A junk row stands on BG0593's plan-review ledger** - reviewer `x`, issues `probe` - from a bad
invocation of mine. `critic supersede` refuses a principal the authoring session controls, which is
the gate working; clearing it is the operator's.

**The operator's own sign-off is not claimed.** The panel signature is the product seat under
`review.signoff: panel`, disjoint from the qa and engineering seats and from the authoring session.
