<!-- close-status:begin -->
> **RUN-01M0ATVZ closed goal-reached.** 4 unit(s) in the batch. **Sign-off is RECORDED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **Run of record:** RUN-01M0CT8P - six instruments that reported verdicts their own evidence did
> not support. Six units, 21 points, delivered. The goal was reached. It took FIVE plan-review
> rounds and THREE delivery-review rounds, and that is the number worth reading, not the points.

## THE HEADLINE: THREE OF SIX WERE NOT DELIVERED WHEN I FIRST TICKED THEM

Both delivery seats REJECTED the first cut, and between them found that **eight of thirty-four
mutants recorded as killed did not die on the test their criterion named.** The `--from-plan`
greens were replaying verdicts that had been typed, not executions.

- **BG0593's production change was unexercised.** Its tests rebuilt the scratch construction in a
  private helper, so deleting the entire change left all four of its tests green AND all 916 tests
  in the file green. Found by a reviewer deleting the code and running the suite.
- **BG0594's rate verdict was never written.** `over` was still `measured > budget`; reverting the
  intended fix survived all 53 tests in its file.
- **BG0594 AC6 was not delivered while its mutant read KILLED** - the mutant had been applied to
  the CALL SITE while the function behind it still returned the wrong series.

## THE DEFECT RELOCATED IN EVERY SINGLE ROUND

An equivalent mutant moved from BG0596 AC6 to BG0593 AC4. A duplicate pair moved from BG0595
AC3/AC5 to AC1/AC3. The scratch degradation moved from the tick row to `_ck_doc_surface`, which
still read the copy while its sibling read the real tree. **A repair judged only against its own
finding is how.** Round 2 of the plan review and rounds 2 and 3 of the delivery review each exist
because of it.

## WHAT THE NEXT SESSION SHOULD READ FIRST

**LL0054** is the diagnosis, and it is short: a test and its mutant authored together share one
mental model, so they agree with each other and not with the code. **Apply the mutant first,
against the unmodified tree, and confirm the named test is red before writing a line of it.**
Working that way caught the rate-ceiling error in one run where the old order needed a review
round.

**CR0547 is the gate that would have caught the worst of this.** `verify_ac revert-check`: revert a
unit's production files and REQUIRE its own verifiers to go red. It is filed, not built. The
registry already holds LL0040, LL0020 and LL0017 describing that hole from three angles, enforced
by nothing.

**CR0548**: derive `Verification depth` from the ledger. Every one of those fields except BG0597's
made a false factual claim in this batch, and two of the hand-written corrections were themselves
wrong.

## WHAT THE GATES CAUGHT THAT I DID NOT

Eleven refusals, every one a real inconsistency: release notes claiming four open High findings
against a corpus holding six; a disclosure page stale the moment two bugs were filed; a derived
index that moved when a unit was re-pointed; ten internal bug ids in shipped `scripts/`; an
unconfined git call; two criteria sharing one verifier; and `mutation register` dropping five
registrations because the file had been edited after they were recorded.

The **verify-ratchet** deserves its own line: it refuses any new pair of criteria sharing one
selector, and forcing BG0594 AC6 to have its own test is what exposed that it had never been
delivered.

## AND ONE THE TOOLING DID NOT CATCH, BECAUSE I WROTE IT

The revert check I built to find unexercised fixes **destroyed uncommitted work on its first run** -
it stashed the tree and restored production files from HEAD, discarding every edit since the last
commit, including the fix it had just been used to validate. It snapshots bytes now.

## OPEN, AND WHY

| Id | State |
| --- | --- |
| BG0599 | Open. `testplan derive` reports one row fault per invocation while computing all four - 22 round trips to clear 33 rows |
| BG0600 | Open. The `unnameable` exemption is held to the four mutant rules, so an honest declaration is refused unless it names a file and a verb it is not about. It forced that wording three times in this batch |
| CR0547 | Filed. The revert-check gate |
| CR0548 | Filed. Derived `Verification depth` |
| BG0586, BG0588, BG0592 | Open High. Untouched by this run |

**A junk row stands on BG0593's plan-review ledger** - reviewer `x`, issues `probe` - from a bad
invocation of mine. `critic supersede` refuses a principal the authoring session controls, which is
the gate working; clearing it is the operator's.
