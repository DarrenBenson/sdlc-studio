# Backlog sweep 2026-09-24

> **Ruling:** D0265 (product seat, subject `backlog:lean-sweep-2026-09-24`), applying D0264
> **Story:** US0907
> **Run:** RUN-01M39MC0
> **Date:** 2026-09-24

The planning review of 2026-09-24 classified the 327 open backlog items against the back-to-basics direction. This record is the product seat's ruling on that list: one row per item, with its verdict, the planning verdict it came from, what the sweep did and the reason.

- **SUPERSEDED, RETIRE, MERGE:** closed through `transition.py` to the type's abandonment status (a story Superseded or Won't Implement, a bug Superseded or Won't Fix, a CR Superseded or Rejected; an epic's close derived from its children), with a `Closed with findings in:` field and a revision row citing D0265 and the reason. A MERGE row names its survivor, and the survivor names its sources in a `Merged from:` field.
- **HELD:** planning called these superseded by deletion batch 2 (EP0263), which has not shipped. Under D0264 a finding is superseded only by work that has shipped, so each stays open with a `Closes with:` field naming the EP0263 story whose delivery closes it.
- **DELIVERED:** the work shipped, so the item closes to its delivered status: BG0709 and BG0716 Fixed, CR0441 Complete, EP0171 Done.
- **KEEP-LEAN, KEEP-VALUE, UNSURE:** not touched. Five planning SUPERSEDED rows were re-ruled UNSURE on review: BG0705, BG0706, BG0714, EP0236 and CR0545.

## Counts

Counted by what the sweep did. Stories, bugs, CRs and epics are the items it acted on.

| Verdict | Items | Acted on | Stories | Bugs | CRs | Epics |
| --- | --- | --- | --- | --- | --- | --- |
| SUPERSEDED | 65 | 65 | 38 | 4 | 17 | 6 |
| RETIRE | 109 | 107 | 72 | 9 | 16 | 10 |
| MERGE | 23 | 21 | 17 | 1 | 2 | 1 |
| DELIVERED | 4 | 4 | 0 | 2 | 1 | 1 |
| HELD | 47 | 47 | 20 | 12 | 9 | 6 |
| KEEP-LEAN | 45 | - | - | - | - | - |
| KEEP-VALUE | 17 | - | - | - | - | - |
| UNSURE | 17 | - | - | - | - | - |
| **Total** | **327** | **244** | **147** | **28** | **45** | **24** |

193 items were closed as ruled out, 4 closed as delivered, and 47 held open. 4 (US0812, US0814, BG0727, BG0732) were already disposed of earlier in RUN-01M39MC0. Of the 327 listed items, 121 are still open. Across the whole workspace the open backlog is now 153: 58 stories, 47 bugs, 25 CRs, 21 epics and 2 RFCs, counting work filed after the planning review and the Sprint 3 epics.

## Dispositions

Planning is the verdict the planning review gave. Action is `swept` (closed by this ruling), `delivered`, `already terminal` (disposed of earlier in the run), `untouched`, or `OPEN - closes with <story> (D0264)`. Status is the item's status when this record was written. Into names the unit a MERGE item merged into.

| ID | Type | Verdict | Planning | Action | Status | Into | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
| EP0171 | epic | DELIVERED | SUPERSEDED | delivered | Done | - | its close derives Done: US0470 to US0473 were delivered, and the three open stories are superseded by US0870, US0875 and US0876; planning ruled it SUPERSEDED |
| US0469 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0870 AC3 gives a batch add its own forecast row; US0875 AC3 reports drops and adds against plan |
| US0474 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | RV record from sprint-review APPROVE: US0876 close no longer gates on review-current; sprint-review ledger deleted in batch 2 |
| US0475 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | review-current lane clearing: US0876 (lane failures become known issues); batch 2 deletes the sprint-review ledger |
| EP0194 | epic | KEEP-LEAN | KEEP-LEAN | untouched | Draft | - | residual of CR0512: only US0581 open |
| US0581 | story | KEEP-LEAN | KEEP-LEAN | untouched | Ready | - | pre-existing finding matching an open Bug/CR annotated and never blocks: mechanises the 'only regression blocks' review rule the lean single review keeps; relaxes, adds no gate |
| EP0196 | epic | RETIRE | RETIRE | swept | Superseded | - | hand-rolled-work detection: a new per-script provenance ledger plus a close report section, no evidence it catches product defects |
| US0586 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] per-run provenance ledger for every script action: new ledger |
| US0587 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] close report section for artefacts changed without tool provenance: new report section |
| US0588 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] outstanding/blocking classification of hand-rolled actions: new ritual |
| US0589 | story | RETIRE | RETIRE | swept | Won't Implement | - | test of a detector being retired |
| US0590 | story | RETIRE | RETIRE | swept | Won't Implement | - | doctrine prose restating the tooling rule the shipped starter already states (templates/agent-instructions.md:108) and SKILL.md:290 points at |
| EP0210 | epic | RETIRE | RETIRE | swept | Superseded | - | contract reporter over 39 refusing verbs: the lean answer is fewer refusals (deletion batches), not tooling to describe them |
| US0646 | story | RETIRE | RETIRE | swept | Won't Implement | - | contract reporter infrastructure over refusals the deletion batches remove |
| US0647 | story | RETIRE | RETIRE | swept | Won't Implement | - | vocab printing for gating vocabularies (mutation, verify_ac) largely deleted in batch 2 |
| US0648 | story | RETIRE | RETIRE | swept | Won't Implement | - | reporter for four verbs whose refusals batch 2 deletes (critic, verify_ac) |
| US0649 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] new lint lane counting contract-reporter coverage |
| US0650 | story | RETIRE | RETIRE | swept | Won't Implement | - | doc repointing for a retired reporter |
| US0651 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] refusal counter + retro figure: new report metric |
| EP0218 | epic | HELD | SUPERSEDED | OPEN - closes with US0909, US0911 (D0264) | Draft | - | planning: SUPERSEDED - plan review / test-plan gate relocation: both gates deleted in batch 2 (D0255 permanent stand-down); superseded only once US0909, US0911 ships (D0264) |
| US0682 | story | HELD | SUPERSEDED | OPEN - closes with US0911 (D0264) | Blocked | - | planning: SUPERSEDED - mutation_evidence vs test-plan scope: both deleted in batch 2; superseded only once US0911 ships (D0264) |
| US0683 | story | HELD | SUPERSEDED | OPEN - closes with US0911 (D0264) | Blocked | - | planning: SUPERSEDED - report of test-plan gate application: gate deleted in batch 2; superseded only once US0911 ships (D0264) |
| US0685 | story | HELD | SUPERSEDED | OPEN - closes with US0911 (D0264) | Blocked | - | planning: SUPERSEDED - test-plan entry gate: deleted in batch 2; superseded only once US0911 ships (D0264) |
| US0686 | story | HELD | SUPERSEDED | OPEN - closes with US0911 (D0264) | Blocked | - | planning: SUPERSEDED - test-plan entry refusal wording: deleted in batch 2; superseded only once US0911 ships (D0264) |
| US0687 | story | HELD | SUPERSEDED | OPEN - closes with US0909 (D0264) | Blocked | - | planning: SUPERSEDED - plan-review approval at terminal: plan review deleted in batch 2; superseded only once US0909 ships (D0264) |
| US0688 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | merge plan+delivery review into one brief: US0872 single review; plan review deleted in batch 2 |
| US0689 | story | HELD | SUPERSEDED | OPEN - closes with US0909 (D0264) | Blocked | - | planning: SUPERSEDED - dated cutoff for the move: moot once the gate is deleted (batch 2); superseded only once US0909 ships (D0264) |
| US0690 | story | HELD | SUPERSEDED | OPEN - closes with US0909 (D0264) | Blocked | - | planning: SUPERSEDED - close report of plan-review exemptions: gate deleted in batch 2; superseded only once US0909 ships (D0264) |
| EP0219 | epic | RETIRE | RETIRE | swept | Superseded | - | exemption restore-condition bookkeeping for adopt_after thresholds: a new ledger on grandfathering the deletions make moot |
| US0691 | story | RETIRE | RETIRE | swept | Won't Implement | - | forward-port --check exclusion listing: repo-only tool, close now forward-ports (US0889) |
| US0692 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] machine-readable restore condition on thresholds: new ledger |
| US0693 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] fired-restore-condition report: new report |
| US0694 | story | RETIRE | RETIRE | swept | Won't Implement | - | exemption state distinction: part of the retired ledger |
| EP0220 | epic | RETIRE | RETIRE | swept | Superseded | - | grandfathering records for gates batch 2-3 delete; v6 migrate carries config forward instead |
| US0695 | story | RETIRE | RETIRE | swept | Won't Implement | - | enumerate grandfathering per gate: gates being deleted |
| US0696 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] durable exemption artefact per grant: new ledger |
| US0697 | story | RETIRE | RETIRE | swept | Won't Implement | - | stub RETRO for pre-adoption cohort: new ritual |
| US0698 | story | RETIRE | RETIRE | swept | Won't Implement | - | stub-retro exclusion from accuracy: follows US0697 |
| US0699 | story | RETIRE | RETIRE | swept | Won't Implement | - | status shows standing exemptions: follows the retired ledger |
| EP0221 | epic | SUPERSEDED | SUPERSEDED | swept | Superseded | - | shippable-increment release gate: goal verdict recorded once at close (D0254) and stop-ship printed at sign (D0257) |
| US0700 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] mechanical shippable clause in Release DoD: new release gate |
| US0701 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | goal half derived from recorded goal verdict: D0254 records it once at close, report shows it (US0875) |
| US0702 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | judges run's goal clauses: no clauses under D0253 |
| US0703 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] tag-check refusal naming failing half: new tag refusal |
| US0704 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | partial verdict releasable only by operator decision: D0257 signer decides |
| US0705 | story | RETIRE | RETIRE | swept | Won't Implement | - | lower-bound reporting for unfiled findings: new report nuance |
| US0706 | story | RETIRE | RETIRE | swept | Won't Implement | - | inheritance of a retired clause |
| EP0222 | epic | HELD | SUPERSEDED | OPEN - closes with US0923 (D0264) | Draft | - | planning: SUPERSEDED - review provenance: brief provenance deleted in batch 2 (D0255); superseded only once US0923 ships (D0264) |
| US0707 | story | HELD | SUPERSEDED | OPEN - closes with US0923 (D0264) | Draft | - | planning: SUPERSEDED - [+constraint] row records how obtained / not via brief: brief provenance deleted in batch 2; superseded only once US0923 ships (D0264) |
| US0708 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] review KINDs each with mandated practices: adds brief ceremony |
| US0709 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] missing-practice refusal per kind: new refusal |
| US0710 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | record reviewer count per round: US0872 records every round with its reviewer |
| US0711 | story | RETIRE | RETIRE | swept | Won't Implement | - | agent-instruction prose making the seat path the only route |
| EP0223 | epic | SUPERSEDED | SUPERSEDED | swept | Superseded | - | five review classes as obligations/detectors: US0887/US0888 failure-class store graduates recurring classes into checks on evidence |
| US0712 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | doctrine naming five classes: failure classes live in lessons.jsonl (US0887) |
| US0713 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | [+constraint] divergent-reader detector: graduation path (US0888) decides which classes earn a check |
| US0714 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | [+constraint] self-agreeing test REFUSED: graduation path (US0888) decides |
| US0715 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] new gate lane must carry inventory guards: meta-gate on gates, the ratchet itself |
| US0716 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] design-rung shape census before implementation: new pre-implementation ritual |
| EP0224 | epic | SUPERSEDED | SUPERSEDED | swept | Superseded | - | close gates on two questions: US0876 one-pass close |
| US0717 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0876: close finishes in one pass, gaps become known issues |
| US0718 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | D0257: stop-ship listed first and printed at sign, signer decides |
| US0720 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0872 AC2: a fixed unit clears at round 2 |
| US0721 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | close cost: US0871 per-unit measurement and US0876 make the close cheap enough not to meter |
| EP0225 | epic | KEEP-LEAN | KEEP-LEAN | untouched | Draft | - | stale-base review worktrees: keep US0722 only |
| US0722 | story | KEEP-LEAN | KEEP-LEAN | untouched | Draft | - | [+constraint] brief refuses when tree lacks the unit: cheap, observed 7 of 7 delegated reviewers, saves a wasted review round on the one review the lean loop keeps |
| US0723 | story | RETIRE | SUPERSEDED | swept | Won't Implement | - | the review base recorded today is the unit's verdict row count, not a commit (critic._mark_review_base), so the planning reason was wrong; US0722 (kept) stops a review on a tree without the unit before it runs, which is the defect this epic exists for, so a commit stamped on each verdict afterwards adds a field no persona reads |
| US0724 | story | RETIRE | RETIRE | swept | Won't Implement | - | doctrine restatement of the base contract |
| EP0226 | epic | SUPERSEDED | SUPERSEDED | swept | Superseded | - | unreviewed span during run: US0872 reviews each unit as it is delivered |
| US0725 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | [+constraint] span report at transition: US0872 per-unit review |
| US0726 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | configurable span threshold: follows US0725 |
| US0727 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | sprint status open span: follows US0725 |
| US0728 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | advisory-until-yield for span report: follows US0725 |
| US0729 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | silence control for span report: follows US0725 |
| EP0227 | epic | HELD | SUPERSEDED | OPEN - closes with US0918, US0920, US0936 (D0264) | Draft | - | planning: SUPERSEDED - broken vs under-evidenced verdicts / evidence debt: evidence ledger and mutation register deleted in batch 2; superseded only once US0918, US0920, US0921 ships (D0264) |
| US0730 | story | HELD | SUPERSEDED | OPEN - closes with US0918 (D0264) | Draft | - | planning: SUPERSEDED - evidence-cannot-fail verdict class: evidence ledger deleted in batch 2; superseded only once US0918 ships (D0264) |
| US0731 | story | HELD | SUPERSEDED | OPEN - closes with US0936 (D0264) | Draft | - | planning: SUPERSEDED - [+constraint] evidence debt per criterion naming surviving mutant: mutation register deleted in batch 2; superseded only once US0921 ships (D0264) |
| US0732 | story | HELD | SUPERSEDED | OPEN - closes with US0918 (D0264) | Draft | - | planning: SUPERSEDED - batch summary split counts: follows US0730; superseded only once US0918 ships (D0264) |
| US0733 | story | HELD | SUPERSEDED | OPEN - closes with US0920 (D0264) | Draft | - | planning: SUPERSEDED - [+constraint] terminal refused while evidence debt open: batch 2 deletes the evidence surface; superseded only once US0920 ships (D0264) |
| US0734 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | seat brief verdict calibration: single reviewer US0872 plus batch 2 brief deletions |
| EP0228 | epic | SUPERSEDED | SUPERSEDED | swept | Superseded | - | installed-copy drift before close: US0889 close forward-ports the skill |
| US0735 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0889 forward-ports at close |
| US0736 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0889 forward-ports at close |
| US0737 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0889 forward-ports at close |
| US0738 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0889 replaced the blocking installed-copy gate with a mirror |
| US0739 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | decision on shape: US0889 chose mirror |
| EP0229 | epic | MERGE | MERGE | swept | Superseded | CR0594 | prior-art as an author step: CR0594 (briefs carry the history of the files they touch) |
| US0740 | story | MERGE | MERGE | swept | Superseded | CR0594 | CR0594 |
| US0741 | story | MERGE | MERGE | swept | Superseded | CR0594 | CR0594 |
| US0742 | story | MERGE | MERGE | swept | Superseded | CR0594 | CR0594 |
| US0743 | story | MERGE | MERGE | swept | Superseded | CR0594 | CR0594 |
| US0744 | story | MERGE | MERGE | swept | Superseded | CR0594 | CR0594 |
| EP0230 | epic | KEEP-VALUE | KEEP-VALUE | untouched | Draft | - | parallelisable fraction for --agentic planning; trim to US0745 |
| US0745 | story | KEEP-VALUE | KEEP-VALUE | untouched | Draft | - | sprint breakdown reports independent components over Affects: tells a consuming project whether --agentic pays; report-only, no gate |
| US0746 | story | MERGE | MERGE | swept | Superseded | US0745 | US0745 |
| US0747 | story | MERGE | MERGE | swept | Superseded | US0745 | US0745 |
| US0748 | story | RETIRE | RETIRE | swept | Won't Implement | - | runbook row |
| US0749 | story | RETIRE | RETIRE | swept | Won't Implement | - | invariant-only story: the `--agentic` rule stays unchanged, so there is nothing to build; US0745 is an ungroomed Draft that carries no such test, so its grooming states the invariant if it is ever wanted |
| EP0231 | epic | UNSURE | UNSURE | untouched | Draft | - | charter scope query over decomposed units: decided by whether charters/queue survive batch 3-4 |
| US0750 | story | UNSURE | UNSURE | untouched | Draft | - | charter query selecting a request's decomposed units: keep only if charters survive batch 3-4 |
| US0751 | story | MERGE | MERGE | swept | Superseded | US0750 | US0750 |
| US0752 | story | RETIRE | RETIRE | swept | Won't Implement | - | repo-specific SC0001 prose/query pin |
| US0753 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] new materialise-time report |
| EP0232 | epic | RETIRE | RETIRE | swept | Superseded | - | revert each hunk to prove coverage: coverage becomes opt-in in batch 2; a new batch-boundary evidence lane |
| US0754 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] per-hunk revert check: new evidence lane |
| US0755 | story | RETIRE | RETIRE | swept | Won't Implement | - | regression corpus for the retired check |
| US0756 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] answer ledger for uncovered hunks: new ledger |
| US0757 | story | RETIRE | RETIRE | swept | Won't Implement | - | placement decision for the retired check |
| US0758 | story | RETIRE | RETIRE | swept | Won't Implement | - | verdict nuance for the retired check |
| EP0233 | epic | KEEP-VALUE | KEEP-VALUE | untouched | Draft | - | configuration visibility; trim to US0759, after batch 4 shrinks the keys |
| US0759 | story | KEEP-VALUE | KEEP-VALUE | untouched | Draft | - | one command prints every key in force with value, source and meaning: consuming projects cannot see 64 keys today; do after batch 4 cuts keys |
| US0760 | story | RETIRE | RETIRE | swept | Won't Implement | - | numbered decisions for judgement keys: ritual |
| US0761 | story | RETIRE | RETIRE | swept | Won't Implement | - | retro proposes config changes: the 3-line retro and calibration re-fit cover the one measured setting |
| US0762 | story | RETIRE | RETIRE | swept | Won't Implement | - | follows US0761 |
| US0763 | story | RETIRE | RETIRE | swept | Won't Implement | - | UNJUDGED report rows: new report section |
| EP0234 | epic | RETIRE | RETIRE | swept | Superseded | - | specs learn about gates via failing spec lanes: gate inventories in TRD/TSD are ceremony; CR0594 covers the loop reading the specs |
| US0764 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] spec lane fails until TRD names a new refusal |
| US0765 | story | RETIRE | RETIRE | swept | Won't Implement | - | derived TSD gate rows |
| US0766 | story | RETIRE | RETIRE | swept | Won't Implement | - | mutation proof of four spec guards |
| US0767 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] regenerate-and-diff spec lane |
| US0768 | story | RETIRE | RETIRE | swept | Won't Implement | - | count of unnamed refusing verbs |
| EP0235 | epic | RETIRE | RETIRE | swept | Superseded | - | lane-check corpus ratchet: D0260 moved lane-check to a hand-run review aid |
| US0769 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] baseline that REFUSES an increase: a ratchet |
| US0770 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] baseline that rises only by recorded decision: a ratchet |
| US0771 | story | RETIRE | RETIRE | swept | Won't Implement | - | per-unit lane-check line at delivery: D0260 has the reviewer run it |
| EP0236 | epic | UNSURE | SUPERSEDED | untouched | Draft | - | planning ruled it SUPERSEDED by BG0575 (release.yml asset publishing), but its remaining child US0774 is UNSURE, so the epic stays open until US0774 is decided |
| US0772 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | nothing invokes tools/release_assets.py check, so no boundary refuses a Release missing assets; the cover is release.yml, which publishes the assets on every tag (BG0575, commit 2588384b) |
| US0773 | story | RETIRE | RETIRE | swept | Won't Implement | - | move the check into shipped release_cut: no consumer evidence |
| US0774 | story | UNSURE | UNSURE | untouched | Draft | - | consuming projects inherit a release step: decide on whether any consuming project asks for it after v6 |
| EP0237 | epic | KEEP-LEAN | KEEP-LEAN | untouched | Draft | - | out-of-batch deliveries are invisible to 'delivered to plan'; trim to US0777 |
| US0775 | story | MERGE | MERGE | swept | Superseded | US0777 | US0777 |
| US0776 | story | MERGE | MERGE | swept | Superseded | US0777 | US0777 (its paired control) |
| US0777 | story | KEEP-LEAN | KEEP-LEAN | untouched | Draft | - | close lists units delivered outside the batch as a non-blocking row: makes the one-page report's delivered-to-plan honest; report-only |
| EP0238 | epic | KEEP-LEAN | KEEP-LEAN | untouched | Draft | - | appetite on working time; most superseded by US0871, keep US0783 |
| US0778 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0871 measures per-unit elapsed time as delivered |
| US0779 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0871 per-unit active time excludes idle between units |
| US0780 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0875 estimates row shows forecast/actual minutes |
| US0781 | story | RETIRE | RETIRE | swept | Won't Implement | - | unclassifiable interval counted as spent: nuance with no evidence |
| US0782 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0875 estimates row replaces retro accuracy line |
| US0783 | story | KEEP-LEAN | KEEP-LEAN | untouched | Draft | - | appetite breaker still reads wall clock (loop_guard.elapsed_minutes): a run left open overnight trips it; read US0871 working time instead |
| EP0239 | epic | UNSURE | UNSURE | untouched | Draft | - | revert-check in an isolated copy: decided by whether revert-check survives batch 2; if kept, US0784 is a real hazard |
| US0784 | story | UNSURE | UNSURE | untouched | Draft | - | revert-check rewrites live tracked files while running: fix only if revert-check survives batch 2, else delete the lane |
| US0785 | story | MERGE | MERGE | swept | Superseded | US0784 | US0784 |
| US0786 | story | MERGE | MERGE | swept | Superseded | US0784 | US0784 |
| US0787 | story | MERGE | MERGE | swept | Superseded | US0784 | US0784 |
| US0788 | story | RETIRE | RETIRE | swept | Won't Implement | - | re-authoring old US0672 criteria: D0259 calls rewriting closed criteria ceremony |
| EP0240 | epic | RETIRE | RETIRE | swept | Superseded | - | exemption reason judged on meaning: tightens refusals on revert-check exemptions |
| US0789 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] new refusal on reason tokens |
| US0790 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] new refusal on restated reasons |
| US0791 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] new refusal on repeated reasons |
| US0792 | story | RETIRE | RETIRE | swept | Won't Implement | - | adoption report for the retired refusal |
| EP0241 | epic | HELD | SUPERSEDED | OPEN - closes with US0936 (D0264) | Draft | - | planning: SUPERSEDED - killed-elsewhere mutation rows: mutation register/ledger deleted in batch 2; superseded only once US0921 ships (D0264) |
| US0793 | story | HELD | SUPERSEDED | OPEN - closes with US0936 (D0264) | Draft | - | planning: SUPERSEDED - mutation ledger deleted in batch 2 (triage also flags US0793/US0794 duplicate); superseded only once US0921 ships (D0264) |
| US0794 | story | HELD | SUPERSEDED | OPEN - closes with US0936 (D0264) | Draft | - | planning: SUPERSEDED - mutation ledger deleted in batch 2; superseded only once US0921 ships (D0264) |
| US0795 | story | HELD | SUPERSEDED | OPEN - closes with US0936 (D0264) | Draft | - | planning: SUPERSEDED - mutation ledger deleted in batch 2; superseded only once US0921 ships (D0264) |
| US0796 | story | HELD | SUPERSEDED | OPEN - closes with US0936 (D0264) | Draft | - | planning: SUPERSEDED - [+constraint] baseline-then-block: mutation ledger deleted in batch 2; superseded only once US0921 ships (D0264) |
| EP0242 | epic | HELD | SUPERSEDED | OPEN - closes with US0936 (D0264) | Draft | - | planning: SUPERSEDED - independent judgement for bugs: US0872 one reviewer per unit; two-role sign-off deleted in batch 2; superseded only once US0921 ships (D0264) |
| US0799 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | doctrine of which types are judged: US0872 reviews every unit |
| US0800 | story | HELD | SUPERSEDED | OPEN - closes with US0936 (D0264) | Draft | - | planning: SUPERSEDED - mutant killed by unnamed test: mutation ledger deleted in batch 2; superseded only once US0921 ships (D0264) |
| EP0243 | epic | HELD | SUPERSEDED | OPEN - closes with US0910 (D0264) | Draft | - | planning: SUPERSEDED - derived-depth re-derivation: verification depth tiers deleted in batch 2; superseded only once US0910 ships (D0264) |
| US0801 | story | HELD | SUPERSEDED | OPEN - closes with US0910 (D0264) | Draft | - | planning: SUPERSEDED - depth tiers deleted in batch 2; superseded only once US0910 ships (D0264) |
| US0802 | story | HELD | SUPERSEDED | OPEN - closes with US0910 (D0264) | Draft | - | planning: SUPERSEDED - depth tiers deleted in batch 2; superseded only once US0910 ships (D0264) |
| US0803 | story | HELD | SUPERSEDED | OPEN - closes with US0910 (D0264) | Draft | - | planning: SUPERSEDED - ledger eviction visibility: mutation ledger deleted in batch 2; superseded only once US0910 ships (D0264) |
| EP0244 | epic | KEEP-VALUE | KEEP-VALUE | untouched | Draft | - | one flag name per concept across verbs; do after batch 2-3 so it covers only surviving verbs |
| US0804 | story | KEEP-VALUE | KEEP-VALUE | untouched | Draft | - | --unit accepted by every verb: agents in consuming projects guess flags today |
| US0805 | story | KEEP-VALUE | KEEP-VALUE | untouched | Draft | - | --fields-file keys spelled as the verb's own flags |
| US0806 | story | MERGE | MERGE | swept | Superseded | US0804 | US0804 |
| US0807 | story | MERGE | MERGE | swept | Superseded | US0804 | US0804 |
| EP0245 | epic | KEEP-LEAN | KEEP-LEAN | untouched | Draft | - | filing a finding leaves the tree red until known-issues.md is regenerated |
| US0808 | story | KEEP-LEAN | KEEP-LEAN | untouched | Draft | - | file_finding regenerates docs/known-issues.md: removes a red-tree trap on the core filing path |
| US0809 | story | MERGE | MERGE | swept | Superseded | US0808 | US0808 (paired control) |
| US0810 | story | MERGE | MERGE | swept | Superseded | US0808 | US0808 |
| EP0246 | epic | KEEP-VALUE | KEEP-VALUE | untouched | Done | - | declared Python 3.10 floor is broken: confirmed sprint_report.py:425 fails to parse under 3.10 (uv run --python 3.10) |
| US0811 | story | KEEP-LEAN | KEEP-LEAN | untouched | Superseded | - | [+constraint] floor check; run it as a CI step at 3.10, not a new pre-commit lane |
| US0812 | story | MERGE | MERGE | already terminal | Superseded | US0811 | US0811 |
| US0813 | story | KEEP-VALUE | KEEP-VALUE | untouched | Superseded | - | repair sprint_report.py: the report and close cannot run on Python 3.10/3.11 today, which the skill declares supported |
| US0814 | story | RETIRE | RETIRE | already terminal | Superseded | - | [+constraint] binding into pre-commit: put the check in CI instead (90s commit budget) |
| EP0248 | epic | RETIRE | RETIRE | swept | Superseded | - | self-run gate for gate/hook changes: US0881's full suite at push runs hooks as the hook does |
| US0855 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] self-run field writer: new ledger field |
| US0856 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] transition refuses Fixed/Done without self-run: new gate |
| US0857 | story | RETIRE | RETIRE | swept | Won't Implement | - | pre-push self-run mode for the retired gate |
| EP0253 | epic | SUPERSEDED | SUPERSEDED | swept | Superseded | - | module-alone narrowing at push: US0881 moved module-alone to the release boundary |
| US0824 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0881 |
| US0825 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0881 |
| US0826 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0881 (scheduled sweep not needed at push) |
| US0827 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0881 |
| US0843 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | US0881 |
| EP0254 | epic | RETIRE | RETIRE | swept | Superseded | - | sharding the weekly corpus lane: lean CI runs the suite once; decide the corpus lane's survival in the deletion batches rather than optimise it |
| US0828 | story | RETIRE | RETIRE | swept | Won't Implement | - | shard corpus pass |
| US0829 | story | RETIRE | RETIRE | swept | Won't Implement | - | shard union collector with baseline judging |
| US0830 | story | RETIRE | RETIRE | swept | Won't Implement | - | shard death reporting |
| US0831 | story | RETIRE | RETIRE | swept | Won't Implement | - | shard timing |
| EP0256 | epic | KEEP-VALUE | KEEP-VALUE | untouched | Draft | - | stakeholder feedback: keep one advisory consult at refine (US0838); retire the trigger, gates and yield bookkeeping |
| US0838 | story | KEEP-VALUE | KEEP-VALUE | untouched | Draft | - | refine runs a stakeholder persona consult over an epic: the one consult on record found the batch's biggest design gap; keep advisory, lightweight record |
| US0839 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] risk trigger naming units that owe a consult: new obligation |
| US0841 | story | RETIRE | RETIRE | swept | Won't Implement | - | unanswered stakeholder Reject reported at close for operator ruling: operator reached only at approval and sign |
| US0842 | story | RETIRE | RETIRE | swept | Won't Implement | - | consult yield metrics: new ledger |
| US0847 | story | RETIRE | RETIRE | swept | Won't Implement | - | persona card provenance fields: ceremony |
| US0858 | story | RETIRE | RETIRE | swept | Won't Implement | - | [+constraint] closed-set validation of consult artefacts: new refusal |
| US0859 | story | RETIRE | RETIRE | swept | Won't Implement | - | consult coverage stamping: ceremony |
| EP0259 | epic | KEEP-LEAN | KEEP-LEAN | untouched | Draft | - | ODD for the andon cord (D0233 kept); US0866 only |
| US0866 | story | KEEP-LEAN | KEEP-LEAN | untouched | Draft | - | plan records its operating domain so the andon cord's ODD-exit condition (D0233) has something to test; approval defines it |
| US0867 | story | SUPERSEDED | SUPERSEDED | swept | Superseded | - | [+constraint] refusal of a goal clause reaching outside the domain: no clauses under D0253 |
| BG0679 | bug | HELD | SUPERSEDED | OPEN - closes with US0913 (D0264) | Open | - | planning: SUPERSEDED - repair-plan gate: repair ledger deleted in batch 2; superseded only once US0913 ships (D0264) |
| BG0680 | bug | HELD | SUPERSEDED | OPEN - closes with US0914 (D0264) | Open | - | planning: SUPERSEDED - repair_state counting: repair ledger deleted in batch 2; superseded only once US0914 ships (D0264) |
| BG0681 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | config.py show --key crashes on a date value: defect on a surviving user command |
| BG0682 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | artifact.py revision writes MD037-failing rows: breaks commits on the core artefact path |
| BG0683 | bug | HELD | SUPERSEDED | OPEN - closes with US0913 (D0264) | Open | - | planning: SUPERSEDED - repair_gate ordering: repair ledger deleted in batch 2; superseded only once US0913 ships (D0264) |
| BG0684 | bug | HELD | SUPERSEDED | OPEN - closes with US0916 (D0264) | Open | - | planning: SUPERSEDED - two-role gate: per-unit two-role sign-off deleted in batch 2; superseded only once US0916 ships (D0264) |
| BG0685 | bug | HELD | SUPERSEDED | OPEN - closes with US0909 (D0264) | Open | - | planning: SUPERSEDED - plan-review verdict kinds in project_upgrade: plan review deleted in batch 2; superseded only once US0909 ships (D0264) |
| BG0686 | bug | SUPERSEDED | SUPERSEDED | swept | Superseded | - | lane-check pre-commit block test: D0260/US0879 removed lane-check from pre-commit |
| BG0687 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | a second Verify line is recorded but never run: false confidence on the surviving Verify-selector path |
| BG0688 | bug | UNSURE | UNSURE | untouched | Open | - | gate --require-close raw owed count: decided by whether close_owed/tag-check survive batch 3; if deleted, SUPERSEDED |
| BG0689 | bug | UNSURE | UNSURE | untouched | Open | - | tag guard ignores velocity half of close_owed: same decider as BG0688 |
| BG0690 | bug | HELD | SUPERSEDED | OPEN - closes with US0914 (D0264) | Open | - | planning: SUPERSEDED - critic.py repair re-judging: repair ledger deleted in batch 2; superseded only once US0914 ships (D0264) |
| BG0691 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | changelog.py shape: two modes disagree on unreadable/symlinked fragments; changelog fragments survive (low) |
| BG0692 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | SDLC_GATE_BOUNDARY env route omits the boundary marker so module-alone reads PASS over red at release (low; or delete the env route) |
| BG0693 | bug | HELD | SUPERSEDED | OPEN - closes with US0912 (D0264) | Open | - | planning: SUPERSEDED - testplan derive vs plan-review brief: both deleted in batch 2; superseded only once US0912 ships (D0264) |
| BG0694 | bug | UNSURE | UNSURE | untouched | Open | - | tag-check tests pin override not predicate: same decider as BG0688 |
| BG0695 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | conformance nudge tells users to groom Superseded/Won't Implement stories: misleading user-facing message (low) |
| BG0696 | bug | HELD | SUPERSEDED | OPEN - closes with US0923 (D0264) | Open | - | planning: SUPERSEDED - brief practice checks: brief provenance/practice checks deleted in batch 2; US0923 closes part (2), brief provenance matching, only; part (1), the whole-brief practice and claim-surface search, has no closing story and stays live (D0264) |
| BG0697 | bug | HELD | SUPERSEDED | OPEN - closes with US0913 (D0264) | Open | - | planning: SUPERSEDED - repair-plan gate fails open: repair ledger deleted in batch 2; superseded only once US0913 ships (D0264) |
| BG0698 | bug | HELD | SUPERSEDED | OPEN - closes with US0913 (D0264) | Open | - | planning: SUPERSEDED - repair-plan rounds: repair ledger deleted in batch 2; superseded only once US0913 ships (D0264) |
| BG0699 | bug | RETIRE | RETIRE | swept | Won't Fix | - | surviving mutant on a correct queue-show line: evidence-only finding, behaviour confirmed by CLI |
| BG0700 | bug | RETIRE | RETIRE | swept | Won't Fix | - | prose-keyword test of a doctrine rule D0257 rewrites |
| BG0701 | bug | UNSURE | UNSURE | untouched | Open | - | stop and close read different unanswered sets: decided by whether stop keeps the unanswered-set refusal after batch 3; if carried issues replace it, SUPERSEDED by US0876/D0257 |
| BG0702 | bug | SUPERSEDED | SUPERSEDED | swept | Superseded | - | unanswered-set remedies for stop-ship: D0257 makes stop-ship a listed known issue, not a hold |
| BG0703 | bug | RETIRE | RETIRE | swept | Won't Fix | - | surviving mutants in fail-closed handlers of the unanswered-set machinery: evidence-only |
| BG0704 | bug | HELD | SUPERSEDED | OPEN - closes with US0914 (D0264) | Open | - | planning: SUPERSEDED - Done guard reading repair closures: repair ledger deleted in batch 2; superseded only once US0914 ships (D0264) |
| BG0705 | bug | UNSURE | SUPERSEDED | untouched | Open | - | planning ruled it SUPERSEDED by the repair ledger's deletion, but nothing tracks the Findings-filed-to condition it describes, so it stays open |
| BG0706 | bug | UNSURE | SUPERSEDED | untouched | Open | - | planning ruled it SUPERSEDED by coverage going opt-in, but line coverage stays a refusing option under US0922, so the defect survives for a project that opts in |
| BG0707 | bug | RETIRE | RETIRE | swept | Won't Fix | - | corpus baseline CI-run line checked by shape: test nit on a corpus lane |
| BG0708 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | gate.py reads SDLC_VERIFY_TIMEOUT per call so the suite is not hermetic: flaky-test risk on the kept suite |
| BG0709 | bug | DELIVERED | SUPERSEDED | delivered | Fixed | - | fixed at HEAD by US0881 AC4 (commit 8daaa2fe: a red answer is re-read, the second judged); planning ruled it SUPERSEDED, but the fix shipped, so it moves to Fixed |
| BG0710 | bug | SUPERSEDED | SUPERSEDED | swept | Superseded | - | close cost printed before capture: US0871 per-unit capture feeds US0875's estimates; apply-signoff goes with per-unit sign-off in batch 2 |
| BG0711 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | test_complexity temp git fixture races teardown on CI and reddens main: CI once must be reliable |
| BG0712 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | check_budgets tolerance disagrees with strict criteria, commit passes and CI reddens: pick one number (low) |
| BG0714 | bug | UNSURE | SUPERSEDED | untouched | Open | - | planning ruled it SUPERSEDED by coverage going opt-in, but line coverage stays a refusing option under US0922, so the defect survives for a project that opts in |
| BG0716 | bug | DELIVERED | SUPERSEDED | delivered | Fixed | - | fixed by US0877 AC4: file_report rewrites an unsigned report of the same run in place under its own id; planning ruled it SUPERSEDED, but the fix shipped, so it moves to Fixed |
| BG0717 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | close's handoff link leaves MD012 blank line so the next commit fails lint; CR0592 carries a duplicate bullet |
| BG0720 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | close summary's 'Filed this run' names delivered units as findings: misreports known issues, the report's third question |
| BG0721 | bug | RETIRE | RETIRE | swept | Won't Fix | - | false positive in an advisory note-level duplicate lens |
| BG0723 | bug | RETIRE | RETIRE | swept | Won't Fix | - | [+constraint] check stated counts in prose against the tree: new check |
| BG0725 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | two spellings of the stop-ship constant in the report: fold into the batch 3 report rewrite (low) |
| BG0726 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | report labels every reviewer NO DECLARED SEAT on a project with no personas: consumer-visible mislabel (low) |
| BG0727 | bug | RETIRE | RETIRE | already terminal | Superseded | - | [+constraint] widen check_script_tests globs: benign today |
| BG0728 | bug | RETIRE | RETIRE | swept | Won't Fix | - | [+constraint] compare Affects with delivering commit: new check |
| BG0729 | bug | RETIRE | RETIRE | swept | Won't Fix | - | unasserted lens-count input: test gap in a figure the one-page report dropped |
| BG0731 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | filing a Low finding recreates a consolidation CR that D0217 ruled is not a CR: defect on the filing path (CR0592 is its product) |
| BG0732 | bug | MERGE | MERGE | already terminal | Superseded | BG0742 | BG0742 (same class: tests coupled to live corpus counts) |
| BG0734 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | dead blockquote skip in check_versions: decide dead code or wrong regex (trivial) |
| BG0735 | bug | SUPERSEDED | SUPERSEDED | swept | Superseded | - | 22-row checklist authority field: US0875 moved the checklist off the page; batch 3 deletes it |
| BG0737 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | a red Verified downgrade deletes the author's annotation: data loss on the kept Verify stamp path (low) |
| BG0738 | bug | MERGE | MERGE | swept | Superseded | BG0731 | BG0731 (the consolidation section disappears with the bucket) |
| BG0739 | bug | UNSURE | UNSURE | untouched | Open | - | close_owed Raised-in-batch parsing: same decider as BG0688 |
| BG0740 | bug | HELD | SUPERSEDED | OPEN - closes with US0926 (D0264) | Open | - | planning: SUPERSEDED - gate stood down in prose invisible to waiver disclosure: batch 2 deletes the stood-down gates, leaving nothing to disclose; superseded only once US0926 ships (D0264) |
| BG0741 | bug | RETIRE | RETIRE | swept | Won't Fix | - | advisory stale lens silenced by audit rulings: note-level lens |
| BG0742 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Fixed | - | corpus-coupled AC tests go red when the backlog is acted on: this very disposition sweep will trip them |
| BG0743 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | signed report digest covers in-place-edited decision prose: sign/check is surviving core path |
| BG0750 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | same-day waiver flips a filed report INVALID: owed in LATEST.md |
| BG0751 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | open findings use an inclusive window end: owed in LATEST.md |
| BG0752 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | per-commit selection follows direct edges only: owed in LATEST.md |
| BG0753 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | suite leaks temp dirs, /tmp ran out of inodes: owed in LATEST.md |
| BG0754 | bug | KEEP-LEAN | KEEP-LEAN | untouched | Open | - | commit over the 90s budget: the lean loop's own target, owed in LATEST.md |
| CR0424 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | RV artefact + review_prep: US0876 one-pass close; sprint-review ledger deleted in batch 2 |
| CR0441 | cr | DELIVERED | SUPERSEDED | delivered | Complete | - | four of five criteria shipped as EP0171 (US0470 to US0473: swap, add-epic, appetite resize, docs); the residue, add and drop stating their effect on the plan, is answered by the shipped forecast row for an added unit and the report's drops and adds against plan (US0870 AC3, US0875 AC3); planning ruled it SUPERSEDED, but the work shipped, so it is Complete |
| CR0496 | cr | RETIRE | RETIRE | swept | Rejected | - | exemption restore-condition ledger (EP0219) |
| CR0497 | cr | RETIRE | RETIRE | swept | Rejected | - | grandfathering records for gates being deleted (EP0220); v6 migrate instead |
| CR0499 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | shippable-increment question: D0254 goal verdict at close, D0257 stop-ship at sign |
| CR0503 | cr | HELD | SUPERSEDED | OPEN - closes with US0923 (D0264) | Proposed | - | planning: SUPERSEDED - review provenance: brief provenance deleted in batch 2; superseded only once US0923 ships (D0264) |
| CR0504 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | recurring review classes: US0887/US0888 failure-class store and graduation |
| CR0507 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | close asks two questions: US0876 |
| CR0509 | cr | KEEP-LEAN | KEEP-LEAN | untouched | Proposed | - | stale-base reviewer worktrees: keep US0722 only |
| CR0512 | cr | KEEP-LEAN | KEEP-LEAN | untouched | In Progress | - | bounded unit review: residual US0581; close the CR when it lands |
| CR0515 | cr | RETIRE | RETIRE | swept | Rejected | - | hand-rolled work detection ledger (EP0196) |
| CR0523 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | unreviewed span: US0872 per-unit review |
| CR0524 | cr | HELD | SUPERSEDED | OPEN - closes with US0918 (D0264) | Proposed | - | planning: SUPERSEDED - evidence debt verdicts: evidence surface deleted in batch 2; superseded only once US0918 ships (D0264) |
| CR0528 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | installed-copy drift: US0889 forward-ports at close |
| CR0529 | cr | MERGE | MERGE | swept | Superseded | CR0594 | CR0594 |
| CR0530 | cr | KEEP-VALUE | KEEP-VALUE | untouched | Proposed | - | parallelisable fraction (EP0230, trimmed to US0745) |
| CR0533 | cr | RETIRE | RETIRE | swept | Rejected | - | revert-each-hunk coverage proof: coverage opt-in in batch 2 |
| CR0534 | cr | KEEP-VALUE | KEEP-VALUE | untouched | Proposed | - | configuration visibility (EP0233, trimmed to US0759) |
| CR0535 | cr | RETIRE | RETIRE | swept | Rejected | - | contract reporter over refusals (EP0210) |
| CR0536 | cr | RETIRE | RETIRE | swept | Rejected | - | spec lanes over gate inventories (EP0234) |
| CR0539 | cr | RETIRE | RETIRE | swept | Rejected | - | lane-check ratchet (EP0235); D0260 |
| CR0543 | cr | HELD | SUPERSEDED | OPEN - closes with US0909 (D0264) | Proposed | - | planning: SUPERSEDED - plan_review adoption cutoff: plan review deleted in batch 2; superseded only once US0909 ships (D0264) |
| CR0544 | cr | RETIRE | RETIRE | swept | Rejected | - | [+constraint] new pre-execution review of repair approaches and procedures |
| CR0545 | cr | UNSURE | SUPERSEDED | untouched | Proposed | - | planning ruled it SUPERSEDED by BG0575 (commit 2588384b), but it decomposes into EP0236, whose child US0774 is UNSURE, so the request stays open with it |
| CR0546 | cr | KEEP-LEAN | KEEP-LEAN | untouched | Proposed | - | out-of-batch deliveries (EP0237, trimmed to US0777) |
| CR0551 | cr | KEEP-LEAN | KEEP-LEAN | untouched | Proposed | - | appetite on working time (EP0238, trimmed to US0783) |
| CR0552 | cr | UNSURE | UNSURE | untouched | Proposed | - | revert-check isolation: decided by revert-check's survival in batch 2 |
| CR0553 | cr | RETIRE | RETIRE | swept | Rejected | - | tighter exemption-reason refusals (EP0240) |
| CR0554 | cr | HELD | SUPERSEDED | OPEN - closes with US0936 (D0264) | Proposed | - | planning: SUPERSEDED - killed-elsewhere rows: mutation ledger deleted in batch 2; superseded only once US0921 ships (D0264) |
| CR0555 | cr | HELD | SUPERSEDED | OPEN - closes with US0911 (D0264) | In Progress | - | planning: SUPERSEDED - test-plan gate relocation: gate deleted in batch 2; superseded only once US0911 ships (D0264) |
| CR0556 | cr | HELD | SUPERSEDED | OPEN - closes with US0936 (D0264) | In Progress | - | planning: SUPERSEDED - bug independent judgement: US0872 plus two-role deletion in batch 2; superseded only once US0921 ships (D0264) |
| CR0558 | cr | HELD | SUPERSEDED | OPEN - closes with US0910 (D0264) | Proposed | - | planning: SUPERSEDED - derived-depth re-derivation: depth tiers deleted in batch 2; superseded only once US0910 ships (D0264) |
| CR0559 | cr | KEEP-VALUE | KEEP-VALUE | untouched | Proposed | - | one concept one flag name (EP0244) |
| CR0560 | cr | KEEP-LEAN | KEEP-LEAN | untouched | Proposed | - | known-issues page left stale by filing (EP0245) |
| CR0561 | cr | KEEP-VALUE | KEEP-VALUE | untouched | Complete | - | Python floor broken at 3.10 (EP0246); confirmed |
| CR0562 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | compulsory tick-verification row: US0876 close no longer refuses on checklist rows; batch 3 deletes the checklist |
| CR0563 | cr | KEEP-LEAN | KEEP-LEAN | untouched | Proposed | - | near-miss hint on a mistyped Verify selector's RED first run: small UX fix on the kept Verify path |
| CR0565 | cr | RETIRE | RETIRE | swept | Rejected | - | self-run gate (EP0248) |
| CR0566 | cr | RETIRE | RETIRE | swept | Rejected | - | [+constraint] claim-drift flag for numeric claims: new check (same class as BG0723) |
| CR0567 | cr | RETIRE | RETIRE | swept | Rejected | - | [+constraint] done-gate demands generated mutation run: mutation stays opt-in |
| CR0571 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | [+constraint] principal check on carried rulings: D0257 signer decides |
| CR0572 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | bulk ruling command: US0876 turns gaps into known issues without per-row rulings |
| CR0573 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | REJECT guard cutoff: US0872 replaced REJECT handling (fixed unit clears, round-2 REJECT carried) |
| CR0574 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | forced-past-REJECT listing: US0872 AC4 carries at cap and US0875 lists carried units |
| CR0576 | cr | RETIRE | RETIRE | swept | Rejected | - | release roll-up of not-stop-ship rulings: ruling tables are old-close ceremony; known-issues page discloses open findings |
| CR0577 | cr | RETIRE | RETIRE | swept | Rejected | - | [+constraint] stakeholder consult gate on batches |
| CR0578 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | plan-review round ceiling: plan review deleted in batch 2 (delivery cap is US0872) |
| CR0579 | cr | MERGE | MERGE | swept | Superseded | CR0552 | CR0552 (same lane; its fate follows revert-check's) |
| CR0580 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | handoff side door over the unanswered set: US0876/D0257 no longer hold on it |
| CR0581 | cr | KEEP-LEAN | KEEP-LEAN | untouched | Proposed | - | forced stop writes no handover: outcome word fixed by US0878 AC3/AC4; residual is a handover for the next plan |
| CR0582 | cr | HELD | SUPERSEDED | OPEN - closes with US0909 (D0264) | Proposed | - | planning: SUPERSEDED - plan-review REJECT closure: plan review and repair ledger deleted in batch 2; superseded only once US0909 ships (D0264) |
| CR0583 | cr | HELD | SUPERSEDED | OPEN - closes with US0911 (D0264) | Proposed | - | planning: SUPERSEDED - Test Plan mutant runner: test plans and mutation register deleted in batch 2; mutation run stays opt-in; superseded only once US0911 ships (D0264) |
| CR0584 | cr | RETIRE | RETIRE | swept | Rejected | - | rewrite 386 whole-module Verify selectors on closed artefacts: D0259 rules such rewrites ceremony |
| CR0585 | cr | RETIRE | RETIRE | swept | Rejected | - | shard the weekly corpus lane (EP0254) |
| CR0586 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | module-alone narrowing: US0881 |
| CR0587 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | goal review asks value: US0868 / D0253 one-sentence value goal with advisory seat read |
| CR0588 | cr | KEEP-LEAN | KEEP-LEAN | untouched | Proposed | - | run_state reader cannot tell unknown key from empty field: caused a false 'unsealed' report four times; run_state is surviving core |
| CR0589 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | rehearse the seal: US0878 sign checks tree and report; US0883/US0885 keep a signed page VALID |
| CR0590 | cr | UNSURE | UNSURE | untouched | Proposed | - | report absorbs the handoff: decided in batch 3 by whether the handover survives beside the one-page report (US0889 kept it) |
| CR0592 | cr | KEEP-LEAN | KEEP-LEAN | untouched | Proposed | - | consolidated Lows: triage bullets (re-run handover SUPERSEDED by US0889; retro blank line MERGE BG0717; allocation_lock fail-open and capacity_report crash are real core-path defects) |
| CR0593 | cr | SUPERSEDED | SUPERSEDED | swept | Superseded | - | [+constraint] refuse unit no goal clause covers: no clauses under D0253 |
| CR0594 | cr | KEEP-VALUE | KEEP-VALUE | untouched | Proposed | - | the record informs the work: leads the sprint after batch 2 |
| RFC0058 | rfc | KEEP-VALUE | KEEP-VALUE | untouched | In Review | - | stakeholder feedback: rule it down to one advisory consult at refine (US0838); retire trigger/gates/yield |

Amended 2026-09-25 (BG0772): the Action cells of CR0554, CR0556, EP0241, EP0242, US0731, US0793, US0794, US0795, US0796, US0800 and EP0227 name US0936 in place of US0921. US0921 was split: it shipped the gate's mutation lane, and the ledger verbs these items describe moved to US0936, so they close with US0936. Their Reason cells keep the ruling's wording.
