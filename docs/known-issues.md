# Known issues

The defects SDLC Studio knows about and has chosen to ship. This page is the disclosure
half of the release bar: a project that hides its open findings is asking to be trusted
rather than read.

## The bar v5.1 is held to

**Zero open High-severity bugs at the tag, and every Medium disposed of or ruled.** A
finding either reaches a terminal status with its own verifiers passing, or it stays open
carrying a dated ruling that says why it ships.

## The bar v5.0.0 was held to, kept as history

**Zero open High-severity bugs at the tag.** Every High finding raised against v5 was
fixed and closed before the tag was cut. The bar was originally zero open bugs of any
severity; it moved on 2026-08-11, because holding a release for findings that are real
but not release-blocking had cost a month and was buying nothing a disclosure could not
buy honestly.

**Medium and Low findings ship open, listed here by id, triaged to v5.1.** Each is a real
defect with a reproduction and, in most cases, a proposed fix. None of them stops the
lifecycle running. They are listed rather than closed, because closing a bug to make a
release look clean is the practice this tool exists to prevent.

Each id below is a file in `sdlc-studio/bugs/` in the source repository, carrying the
evidence, the reproduction and the proposed fix in full.

## Triaged to v5.1

| Id | Severity | Finding |
| --- | --- | --- |
| `BG0679` | Medium | With review.repair_plan_gate on, a repair bug set straight to Closed or Verified skips the gate |
| `BG0680` | Medium | repair_state counts a repair row once per rejection sharing its date, so closed and fixed counts are doubled |
| `BG0681` | Medium | config.py show --key crashes on a key whose value holds an unquoted YAML date, the path BG0670 left |
| `BG0682` | Medium | artifact.py revision writes a bare _identifier into the Revision History, which markdownlint refuses as MD037 |
| `BG0683` | Medium | repair_gate's review-before-repair ordering check (US0312 AC4) is dead on the wired path |
| `BG0684` | Medium | transition's two-role gate ignores a Definition of Done that stands the review.two-role tag down |
| `BG0685` | Medium | project_upgrade reads plan-review verdicts with no kind, so a repair-plan APPROVE counts as a repair story's spec review |
| `BG0686` | Medium | BG0493 AC2's test reads a fixture hook, so deleting the real pre-commit hook's lane-check block survives |
| `BG0687` | Medium | A criterion's second Verify line is recorded but never run, so a both-states requirement cannot be enforced by its selectors |
| `BG0688` | Medium | gate --require-close still counts close-owed's raw owed rows, refusing an override the tag guard and the detector now honour |
| `BG0689` | Medium | The release tag guard never reads close_owed's velocity half, so a retro owing its velocity row does not refuse the tag |
| `BG0690` | Medium | critic.py repair re-judges stored findings through the code-span guard, and its typed closure scanner unescapes any backslash before a greater-than... |
| `BG0691` | Medium | changelog.py shape judges unreadable and symlinked fragments differently in its two modes, and its git-failure refusals are unpinned |
| `BG0692` | Medium | gate.py never sets the boundary-suite marker itself, so SDLC_GATE_BOUNDARY=push reads [PASS] module-alone over a red boundary-only test |
| `BG0693` | Medium | testplan derive and the plan-review brief still name different unauthored sets: blank cells, table order and a criterion with no row |
| `BG0694` | Medium | tag-check's tests pin the override case, not the blocking predicate, so a later-day close-time repair can be refused again with the suite green |
| `BG0695` | Medium | conformance's ungroomed nudge counts retired skeletons and tells the user to groom Superseded and Won't Implement stories before planning them to Done |
| `BG0696` | Medium | critic.py's brief checks search the whole brief, so a unit's own text hides a dropped surface, and a REJECT marked as matching no brief can never b... |
| `BG0697` | Medium | The repair-plan gate fails open on a zero-finding plan, an unparseable config and an unreadable round file, and its refusals name no remedy or cras... |
| `BG0698` | Medium | Repair-plan rounds can be overwritten by concurrent records, a re-record after approval counts as a failed round, and the escalation notice counts... |
| `BG0699` | Medium | sprint queue show's not-materialised line is pinned by no test, and next, plan and queue show hold the discovery partition in separate copies |
| `BG0700` | Medium | The doctrine stop-ship guard passes inverted sentences and a second rule under the same anchor |
| `BG0701` | Medium | Run-ending routes still read different sets: stop records from the parked derivation, the boundary stop ignores --retro, and stop cannot see the re... |
| `BG0702` | Medium | The unanswered set's ways out are picked by substring and offer dead ends for a stop-ship ruling, and the set is rendered and recorded in drifting... |
| `BG0703` | Medium | The unanswered-set predicate's fail-closed handlers and the handoff behaviours around it survive mutants no test kills |
| `BG0704` | Medium | The Done guard reads a filed closure naming the unit itself as a repair, and lists repaired findings as outstanding when the only APPROVE is the au... |
| `BG0705` | Medium | The Findings-filed-to line survives a reopen, is not reported in text output, and names only the filed subset of a partial repair |
| `BG0706` | Medium | The coverage gate charges another unit's added lines to a unit sharing its file, and a coverage ruling is voided by any edit to that file |
| `BG0707` | Medium | the corpus baseline's CI-run line is judged by shape alone, so a hand-typed run id reads as a re-measure |
| `BG0708` | Medium | gate.py reads SDLC_VERIFY_TIMEOUT per call, so a previously hermetic suite now inherits whatever the environment sets |
| `BG0709` | Medium | the pre-push red-main check trusts the forge's ordering, so a stale first row demands acknowledgement of a two-month-old red |
| `BG0710` | Medium | the close prints the run's cost before the step that captures it, so every close reports the sprint as not attributable |

32 findings: 32 Medium, 0 Low.

## Not carried

Three High findings were ruled `Won't Fix` on their own merits before this bar was set,
and one was superseded by later work. They are not in the list above because they are not
open, and a disclosure that pads its count is as misleading as one that trims it.

## How this list is kept

It is derived from the bug corpus by `tools/known_issues.py`, not maintained by hand, and
`tools/tests/test_known_issues.py` fails when the two disagree. Any bug at `Open` whose
severity is Medium or Low appears here; a bug that reaches a terminal status leaves.
Regenerate with `python3 tools/known_issues.py --write`.
