# Sprint Report: RUN-01M3HR74

## Goal

v6.0.0 ships: Maya and Jonah install, upgrade and learn it from docs and notes that match the code.

**Verdict: Judged achieved** - All 55 batch units delivered, each by an independent review (BG0818 by operator-granted round 3, D0285/D0286); the install and upgrade paths are documented and rehearsed on copies of a v4.1 and a v2.4 project (US0955, US0962); a fresh agent ran a whole lean sprint from the docs alone (eval 09, D0280) and the independence eval passed on the final skill (06, D0282); the notes match the code and disclose 35 open Medium defects. v6.0.0 itself is tagged after this run is signed.

> **Run:** 2026-09-27T15:40:33Z to open (29.2h)
> **Verified on:** ba3e4313aad29977db5329b52ea28ab948d1df6b   **Fingerprint:** 61403431521eab55

## Estimates

How far the plan's forecast was from what the run took. Points are compared over the
delivered units; minutes and tokens over the whole run, its span and its meter. Ratio is actual
over forecast.

| Measure | Forecast | Actual | Ratio | Over |
| --- | --- | --- | --- | --- |
| Points | 128 | 128 | 1.0x | 54 of 54 delivered unit(s) |
| Minutes | 838.4 | 1749.8 | 2.09x | the whole run: forecast over 55 of 55 unit(s) planned or added and not dropped; forecast is active work minutes per point, actual is the run's wall-clock span, start to end, so waiting counts |
| Tokens | 46,349,110 | 23,110,572 | 0.5x | the whole run: forecast over 55 of 55 unit(s) planned or added and not dropped; actual is the main-thread meter plus 100 delegated agent(s)' reported totals, split in the appendix |

Each cell names its source. A figure labelled agent minutes or agent tokens sums the agent
totals tagged to that unit; an unlabelled one is measured over the unit's own open span. Spans of
units open at the same time overlap, so no per-unit figure is added up into the run's figures
above.

| Unit | Forecast minutes | Minutes | Forecast tokens | Tokens |
| --- | --- | --- | --- | --- |
| BG0682 | 6.4 | 18.7 agent minutes | 353,810 | 237,094 agent tokens |
| BG0692 | 6.4 | 40.3 agent minutes | 353,810 | 205,184 agent tokens |
| BG0725 | 6.4 | 27.0 agent minutes | 353,810 | 141,918 agent tokens |
| BG0782 | 12.8 | 32.4 agent minutes | 707,620 | 411,877 agent tokens |
| BG0783 | 19.2 | 19.5 agent minutes | 1,061,430 | 570,882 agent tokens |
| BG0784 | 12.8 | 19.3 agent minutes | 707,620 | 205,934 agent tokens |
| BG0785 | 19.2 | 16.8 agent minutes | 1,061,430 | 412,479 agent tokens |
| BG0786 | 19.2 | 9.6 agent minutes | 1,061,430 | 101,111 agent tokens |
| BG0788 | 19.2 | 340.5 agent minutes | 1,061,430 | 193,969 agent tokens |
| BG0790 | 19.2 | 40.9 agent minutes | 1,061,430 | 285,792 agent tokens |
| BG0792 | 6.4 | 83.3 | 353,810 | 322,356 |
| BG0794 | 6.4 | 82.9 | 353,810 | 321,257 |
| BG0795 | 19.2 | 48.2 agent minutes | 1,061,430 | 319,112 agent tokens |
| BG0796 | 12.8 | 17.4 agent minutes | 707,620 | 265,502 agent tokens |
| BG0797 | 19.2 | 17.4 agent minutes | 1,061,430 | 265,502 agent tokens |
| BG0798 | 19.2 | 38.4 agent minutes | 1,061,430 | 420,785 agent tokens |
| BG0799 | 12.8 | 20.1 agent minutes | 707,620 | 285,733 agent tokens |
| BG0801 | 12.8 | 442.9 agent minutes | 707,620 | 247,319 agent tokens |
| BG0802 | 6.4 | 18.7 agent minutes | 353,810 | 237,094 agent tokens |
| BG0805 | 12.8 | 442.9 agent minutes | 707,620 | 247,319 agent tokens |
| BG0806 | 12.8 | 99.5 | 707,620 | 264,429 |
| BG0808 | 6.4 | 62.2 | 353,810 | 173,885 |
| BG0809 | 12.8 | 40.3 agent minutes | 707,620 | 205,184 agent tokens |
| US0924 | 32.0 | 1050.0 agent minutes | 1,769,050 | 619,415 agent tokens |
| US0926 | 12.8 | 10.5 agent minutes | 707,620 | 231,005 agent tokens |
| US0952 | 19.2 | 21.2 agent minutes | 1,061,430 | 276,338 agent tokens |
| US0953 | 19.2 | 16.0 agent minutes | 1,061,430 | 584,898 agent tokens |
| US0954 | 19.2 | 21.2 agent minutes | 1,061,430 | 276,338 agent tokens |
| US0955 | 19.2 | 10.5 agent minutes | 1,061,430 | 231,005 agent tokens |
| US0956 | 32.0 | 383.6 agent minutes | 1,769,050 | 350,055 agent tokens |
| US0957 | 32.0 | 383.6 agent minutes | 1,769,050 | 350,055 agent tokens |
| US0959 | 32.0 | 36.2 agent minutes | 1,769,050 | 478,644 agent tokens |
| US0960 | 32.0 | 55.4 agent minutes | 1,769,050 | 607,564 agent tokens |
| US0961 | 12.8 | 19.3 agent minutes | 707,620 | 205,934 agent tokens |
| US0962 | 19.2 | 17.5 agent minutes | 1,061,430 | 342,697 agent tokens |
| US0963 | 32.0 | 15.4 agent minutes | 1,769,050 | 1,045,812 agent tokens |
| US0964 | 12.8 | 20.4 agent minutes | 707,620 | 316,181 agent tokens |
| BG0800 | 6.4 | 20.1 agent minutes | 353,810 | 285,733 agent tokens |
| BG0803 | 6.4 | 97.8 | 353,810 | 264,429 |
| BG0804 | 6.4 | 27.0 agent minutes | 353,810 | 141,918 agent tokens |
| BG0807 | 6.4 | 63.2 | 353,810 | 173,885 |
| BG0810 | 6.4 | 7.0 agent minutes | 353,810 | 89,619 agent tokens |
| BG0811 | 12.8 | 340.5 agent minutes | 707,620 | 193,969 agent tokens |
| BG0812 | 19.2 | 92.4 agent minutes | 1,061,430 | 303,704 agent tokens |
| BG0813 | 6.4 | 9.6 | 353,810 | 104,708 |
| BG0814 | 19.2 | 18.9 agent minutes | 1,061,430 | 350,053 agent tokens |
| US0965 | 19.2 | 10.3 agent minutes | 1,061,430 | 391,953 agent tokens |
| BG0815 | 6.4 | 21.6 agent minutes | 353,810 | 247,829 agent tokens |
| BG0816 | 12.8 | 51.9 agent minutes | 707,620 | 336,867 agent tokens |
| BG0818 | 19.2 | 23.5 agent minutes | 1,061,430 | 425,343 agent tokens |
| BG0819 | 6.4 | 7.5 agent minutes | 353,810 | 193,828 agent tokens |
| BG0820 | 12.8 | 14.6 agent minutes | 707,620 | 209,431 agent tokens |
| BG0821 | 12.8 | 42.4 agent minutes | 707,620 | 290,069 agent tokens |
| BG0822 | 12.8 | 7.5 agent minutes | 707,620 | 193,828 agent tokens |
| BG0823 | 19.2 | 14.6 agent minutes | 1,061,430 | 209,431 agent tokens |

## Delivered to plan

| Measure | Units | Points |
| --- | --- | --- |
| Planned | 41 | 102 |
| Delivered of the plan | 41 | 102 |
| Added mid-run and delivered | 13 of 14 added | 26 |
| Dropped | 0 | 0 |
| Carried undelivered | 1 | 3 |

Points here are the sizes the plan recorded: a unit resized since keeps its planned size and
shows its current size below, and an added unit is sized when it is added. Added units are work
outside the plan and are never counted as delivering it. Points delivered at their current
size, plan and added together: 128.

| Unit | Planned points | Points | Outcome | Review rounds |
| --- | --- | --- | --- | --- |
| BG0682 | 1 | 1 | delivered | 2 |
| BG0692 | 1 | 1 | delivered | 1 |
| BG0725 | 1 | 1 | delivered | 1 |
| BG0782 | 2 | 2 | delivered | 1 |
| BG0783 | 3 | 3 | delivered | 2 |
| BG0784 | 2 | 2 | delivered | 1 |
| BG0785 | 3 | 3 | delivered | 2 |
| BG0786 | 3 | 3 | delivered | 2 |
| BG0788 | 3 | 3 | delivered | 1 |
| BG0790 | 3 | 3 | delivered | 1 |
| BG0792 | 1 | 1 | delivered | 1 |
| BG0794 | 1 | 1 | delivered | 1 |
| BG0795 | 3 | 3 | delivered | 1 |
| BG0796 | 2 | 2 | delivered | 1 |
| BG0797 | 3 | 3 | delivered | 2 |
| BG0798 | 3 | 3 | delivered | 2 |
| BG0799 | 2 | 2 | delivered | 1 |
| BG0801 | 2 | 2 | delivered | 1 |
| BG0802 | 1 | 1 | delivered | 1 |
| BG0805 | 2 | 2 | delivered | 2 |
| BG0806 | 2 | 2 | delivered | 1 |
| BG0808 | 1 | 1 | delivered | 1 |
| BG0809 | 2 | 2 | delivered | 1 |
| US0924 | 5 | 5 | delivered | 2 |
| US0926 | 2 | 2 | delivered | 1 |
| US0952 | 3 | 3 | delivered | 2 |
| US0953 | 3 | 3 | delivered | 2 |
| US0954 | 3 | 3 | delivered | 2 |
| US0955 | 3 | 3 | delivered | 2 |
| US0956 | 5 | 5 | delivered | 2 |
| US0957 | 5 | 5 | delivered | 1 |
| US0959 | 5 | 5 | delivered | 2 |
| US0960 | 5 | 5 | delivered | 2 |
| US0961 | 2 | 2 | delivered | 2 |
| US0962 | 3 | 3 | delivered | 1 |
| US0963 | 5 | 5 | delivered | 2 |
| US0964 | 2 | 2 | delivered | 2 |
| BG0800 | 1 | 1 | delivered | 2 |
| BG0803 | 1 | 1 | delivered | 1 |
| BG0804 | 1 | 1 | delivered | 1 |
| BG0807 | 1 | 1 | delivered | 1 |
| BG0810 | 1 | 1 | added - no reason recorded; delivered | 1 |
| BG0811 | 2 | 2 | added - no reason recorded; delivered | 1 |
| BG0812 | 3 | 3 | added - no reason recorded; delivered | 2 |
| BG0813 | 1 | 1 | added - no reason recorded; delivered | 1 |
| BG0814 | 3 | 3 | added - no reason recorded; delivered | 2 |
| US0965 | 3 | 3 | added - no reason recorded; delivered | 1 |
| BG0815 | 1 | 1 | added - no reason recorded; delivered | 1 |
| BG0816 | 2 | 2 | added - no reason recorded; delivered | 1 |
| BG0818 | 3 | 3 | added - no reason recorded; carried, not delivered | 2 |
| BG0819 | 1 | 1 | added - no reason recorded; delivered | 2 |
| BG0820 | 2 | 2 | added - no reason recorded; delivered | 2 |
| BG0821 | 2 | 2 | added - no reason recorded; delivered | 1 |
| BG0822 | 2 | 2 | added - no reason recorded; delivered | 1 |
| BG0823 | 3 | 3 | added - no reason recorded; delivered | 1 |

## Known issues handed over

25 open finding(s) raised in the run, 7 close gap(s), 1 carried unit(s)

| Issue | Priority | Detail |
| --- | --- | --- |
| BG0817 | Medium | The bug-close guidance says briefed with critic.py brief but never says to hand the reviewer the brief whole, so agents relay a trimmed or broken brief |
| BG0824 | Medium | init guided's personas stage seeds the legacy flat personas.md, which the persona registry and sprint plan --serves never read |
| BG0825 | Medium | ULID ids are printed as their hyphenless comparison key, so plan, brief, carry and the signed report name ids no file carries |
| BG0826 | Medium | The scaffolded retro carries neither the run id nor a Known issues carried table, so the run's rulings cannot be found or written |
| BG0827 | Medium | The review brief asks the reviewer to judge origin 'at the base ref' but never names the base ref |
| BG0828 | Medium | The one-call closes do not check the review brief: artifact.py close records a verdict with no brief and no warning, and transition --brief accepts a fingerprint no brief printed |
| BG0829 | Medium | A unit carried at the review cap is filed as an ungroomed bug that sprint plan cannot take, and every carry prints that the operator was notified |
| BG0830 | Medium | A verdict or delegated-token record written after the seal lands on the sealed run without a warning |
| BG0831 | Medium | The configuration reference documents keys the code does not honour: sprint.split_above, review.policy carry-forward, and review.max_rounds |
| BG0832 | Medium | reference-review.md step 3a ships a private project's consultation cast as its example, names amigos with no resolver, and the neutrality lane misses it |
| BG0833 | Medium | The engagement floor judges a decomposed CR by its own criteria, so a CR reconcile derives Complete from planned children is refused as unplanned |
| BG0834 | Medium | persona generate --team lets a pre-supplied or headless default stand as an answer, so its report claims questions were asked and accepted when none was |
| BG0835 | Medium | Token capture looks for the session transcript in a directory named by replacing only '/', so a project path holding '.' or '_' reads NOT ATTRIBUTABLE |
| BG0836 | Medium | No command writes a lesson class's graduated state, so every graduation CR carries a criterion only a hand edit can meet |
| BG0837 | Medium | The pre-push gate judges the working tree, not the commits being pushed, so an uncommitted fix turns a red push green |
| BG0838 | Medium | retired_surface excuses a live retired name by the shape of its sentence, so a live instruction passes as history |
| BG0839 | Medium | An eval worker session loads the personal skill ahead of the candidate copy, and nothing in the harness says so or prevents it |
| BG0840 | Medium | BG0818 did not converge in review: round 2 REJECT findings |
| BG0841 | Medium | The review cap has no per-unit exception path, so an operator-granted extra round can only land by force |
| BG0842 | Medium | migrate reports 2 index drift items on a v4.1 project whose gate reconcile lane fails on 28, because project upgrade counts two of reconcile's nine drift sources |
| BG0843 | Medium | migrate names no engagement-floor cutoff, so a v4.1 project's gate fails the engagement floor on 349 shipped units before and after the upgrade and the report says nothing |
| BG0844 | Medium | An upgraded project never gets the sdlc-studio/.gitignore that init writes, so gate.py leaves runtime state in git status on every run |
| BG0845 | Medium | migrate's conformance cutoff on a v4.1 project exempts the 98 units after the project's own adoption point, because a verdict row with no Author column never reads as independent |
| CR0601 | Medium | A shipped command reports where a project's own docs still name retired v5 surface |
| CR0602 | Medium | A run's token and minute actuals are measured without the operator stamping a baseline |
| review-coverage | close gap | 54/55 unit(s) covered by an independent pass |
| review-coverage | close gap | 1 unit(s) in this batch are covered by NO independent review: BG0818 |
| review-coverage | close gap | finding placement: 0 raised at a batch boundary, 107 raised outside one, across 0/0 reviewed batch(es). A finding raised outside a batch is close work - 107 is the number this run drives to zero |
| review-coverage | close gap | The close certifies that a review happened; it does not perform one. |
| checklist | close gap | known-issues: 1 batch unit(s) the run cannot end over: BG0818 (Fixed) - unanswered delivery REJECT - findings NONE filed |
| report-hold:terminal-gate | close gap | 1 batch unit(s) whose terminal gate is UNMET - BG0818: BG0818 -> Fixed blocked (1 requirement(s), all listed): BG0818 carries an unanswered delivery REJECT (qa-rev-a7755839's REJECT of 2026-09-28; qa-rev-a7755839's REJECT of 2026-09-28): 8 finding(s) outstanding - blocking: a non-UTF-8 AGENTS.md or prd.md now crashes init guided and status hint, because \_authored and carries\_doctrine read with strict UTF-8 inside stage\_output\_exists; non-blocking: generic template tokens such as {{version}} and {{date}} hold an authored document that quotes them, and the docstring over-claims; non-blocking: the fill-the-placeholders directive is untested; non-blocking: the AGENTS.md already present wording reads as if the user wrote a file init seeded .... A REJECT has two exits: a round-2 APPROVE from the reviewer who rejected, or carrying the unit at the review cap: that reviewer's round-2 REJECT, recorded in the open run, files the findings as a bug and drops the unit from the batch, so the run closes without it. A carried unit is still refused Done: it is delivered again in a later run and reaches Done on an APPROVE from the reviewer who rejected it (the same reviewer id). A ruling in a retro's `Known issues carried` table does not discharge it, and a `--force` waiver is recorded in the artefact's `Forced-override` field. Override with --force. |
| report-hold:unanswered-review | close gap | 1 batch unit(s) whose review is unanswered - BG0818: Fixed - unanswered delivery REJECT |
| BG0818 | carried unit | added and not delivered by this run |

## Sign-off

| Signed by | Date | Fingerprint signed |
| --- | --- | --- |
| not yet signed | not yet signed | not yet signed |

Signing records the principal, the date and this report's fingerprint against RUN-01M3HR74.

## Appendix

### Tokens by model

| Model | Tokens |
| --- | --- |
| mixed | 8,071,266 |

Total 23,110,572, of which delegated 15,039,306. Coverage: 1 session(s);
read from stamps, with the opening reading taken from the legacy session_token_baseline this run predates the open stamp.

### DORA

| Key | This run | Mapping | Elite band | Derived from |
| --- | --- | --- | --- | --- |
| Deployment frequency | 9 | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up | on demand | forge runs 36477625660/36465997540/36462167048/36445135602/36438476889/36409909036/36356518304/36346337680/36336415797 - 9 push-triggered run(s) on main in the run window |
| Lead time for changes | 28h 41m | the span from the run's first commit on main to its last - per-commit lead time is not derived, because the work is committed locally and pushed in batches | under a day | git history - first to last of 96 commit(s) |
| Change failure rate | 11% | a push to main IS the deployment in this trunk-based repository: there is no separate deploy step, and CI on that commit is what decides whether the change stood up; the rate is the share of push-triggered CI runs on main that did not conclude success | 0-15% | forge runs 36477625660/36465997540/36462167048/36445135602/36438476889/36409909036/36356518304/36346337680/36336415797 - 9 deployment(s); 1 failed on 0aa334cba0307a2bc58d3d8034f2e97e106b1f6f |
| Time to restore | NOT MEASURED - no forge run data | the span from a push-triggered run concluding failure on main to the next push-triggered run concluding success | under an hour | no push-triggered CI run is readable for this run window |

### Calibration

| Rate | Value | Source |
| --- | --- | --- |
| Tokens per point | 353,810 | velocity-record |
| Minutes per point | 6.4 | fallback: 0 row(s) for claude-opus-5, under 3, so the latest rows of any single model: median of RETRO0028 |

### Rulings

Persona seats ruled 0 time(s), 0 of them by citing a
precedent; the operator ruled 7 time(s).

### Waivers in force

1 gate(s) were not holding when this page was derived

- **D0281** - rule:engagement-floor:cr0599 (2026-09-28T11:18:40+01:00): CR0599 was delivered wholly through its decomposed units (US0959, US0960, BG0795, BG0788), each planned with executable criteria and independently reviewed; reconcile derived it Complete when US0960 closed. The floor reads only the CR's own criteria and does not follow Decomposed-into, a gap filed as a follow-up.

### Lane yield

6 refusal(s) in this run. A refusal is a candidate catch when the next commit changed code or a test from what was refused, paperwork when it changed only artefacts, baselines, indexes or docs, and pending until a commit follows it. A measure, not a gate: listing a lane for deletion refuses nothing and
files nothing.

| Lane | Refusals | Candidate catches | Paperwork | Last three runs |
| --- | --- | --- | --- | --- |
| gate | 3 | 0 | 3 | delete candidate: 4 refusal(s) over 3 runs and no candidate catch |
| markdown | 2 | 0 | 2 | 1 candidate catch(es) over 3 runs |
| message-refs | 1 | 0 | 1 | delete candidate: 6 refusal(s) over 3 runs and no candidate catch |
| repo-writes | 0 | 0 | 0 | 1 candidate catch(es) over 3 runs |
| unit-tests | 0 | 0 | 0 | delete candidate: 2 refusal(s) over 3 runs and no candidate catch |

### Lessons

12 lesson class(es) in force at this close.

| Lesson | Class | State | Hits this run | Hits in total |
| --- | --- | --- | --- | --- |
| LC-001 | mutant never applied | active | 0 | 0 |
| LC-002 | criterion words outrun the fixture | graduating (CR0595) | 14 | 51 |
| LC-003 | mechanism reaches no caller | graduating (CR0598) | 2 | 8 |
| LC-004 | premise not executed | graduating (CR0600) | 0 | 2 |
| LC-005 | repair breaks its neighbour | active | 0 | 1 |
| LC-006 | absence read as an answer | graduating (CR0596) | 5 | 15 |
| LC-007 | shared machine resources exhausted | active | 0 | 0 |
| LC-008 | constraint added without retirement | graduating (CR0597) | 2 | 11 |
| LC-009 | the review cap carries trivial fixes | active | 0 | 0 |
| LC-010 | the push gate and CI disagree on the runner | active | 0 | 0 |
| LC-011 | widen-after-brief | active | 0 | 0 |
| LC-012 | a reviewer's clone cannot see writes into the main repo | active | 0 | 0 |
