# Known issues

The defects SDLC Studio knows about and has chosen to ship. This page is the disclosure
half of the release bar: a project that hides its open findings is asking to be trusted
rather than read.

## The bar v6.0 is held to

**Zero open Critical or High finding at the tag, and every open Medium ruled by one triage
decision.** A finding either reaches a terminal status with its own verifiers passing, or it
stays open under the triage target below, which one recorded decision rules for the whole list
rather than a waiver per finding.

**Medium and Low findings ship open, listed here by id, triaged to v6.1.** Each is a real
defect with a reproduction and, in most cases, a proposed fix. None of them stops the
lifecycle running. They are listed rather than closed, because closing a bug to make a
release look clean is the practice this tool exists to prevent.

Each id below is a file in `sdlc-studio/bugs/` in the source repository, carrying the
evidence, the reproduction and the proposed fix in full.

## The bar v5.1 was held to, kept as history

**Zero open High-severity bugs at the tag, and every Medium disposed of or ruled.** A
finding either reaches a terminal status with its own verifiers passing, or it stays open
carrying a dated ruling that says why it ships.

## The bar v5.0.0 was held to, kept as history

**Zero open High-severity bugs at the tag.** Every High finding raised against v5 was
fixed and closed before the tag was cut. The bar was originally zero open bugs of any
severity; it moved on 2026-08-11, because holding a release for findings that are real
but not release-blocking had cost a month and was buying nothing a disclosure could not
buy honestly.

## Triaged to v6.1

| Id | Severity | Finding |
| --- | --- | --- |
| `BG0691` | Medium | changelog.py shape judges unreadable and symlinked fragments differently in its two modes, and its git-failure refusals are unpinned |
| `BG0696` | Medium | critic.py's brief checks search the whole brief, so a unit's own text hides a dropped surface, and a REJECT marked as matching no brief can never b... |
| `BG0701` | Medium | Run-ending routes still read different sets: stop records from the parked derivation, the boundary stop ignores --retro, and stop cannot see the re... |
| `BG0706` | Medium | The coverage gate charges another unit's added lines to a unit sharing its file, and a coverage ruling is voided by any edit to that file |
| `BG0712` | Medium | a local guard that tolerates what a criterion refuses lets a breach pass the commit and redden CI |
| `BG0726` | Medium | the report renders NO DECLARED SEAT without asking whether the project declares any personas at all |
| `BG0734` | Medium | the blockquote skip in check_versions is unreachable, so it guards nothing |
| `BG0737` | Medium | the stale downgrade destroys an author's reason on a positive verdict, so the principle BG0733 shipped is violated on the sibling branch of the sam... |
| `BG0739` | Medium | close_owed reads the Raised-in-batch stamp by its last token while asserting it reads it exactly as sprint_report does, and the two now genuinely d... |
| `BG0740` | Medium | a gate stood down in prose rather than as a waiver row is invisible to the report's waiver disclosure, which is how the one the operator most neede... |
| `BG0752` | Medium | Per-commit test selection skips hooks, test infrastructure and code reached through another script |
| `BG0754` | Medium | A commit touching a widely imported script runs well over the 90-second budget |
| `BG0817` | Medium | The bug-close guidance says briefed with critic.py brief but never says to hand the reviewer the brief whole, so agents relay a trimmed or broken b... |
| `BG0824` | Medium | init guided's personas stage seeds the legacy flat personas.md, which the persona registry and sprint plan --serves never read |
| `BG0825` | Medium | ULID ids are printed as their hyphenless comparison key, so plan, brief, carry and the signed report name ids no file carries |
| `BG0826` | Medium | The scaffolded retro carries neither the run id nor a Known issues carried table, so the run's rulings cannot be found or written |
| `BG0827` | Medium | The review brief asks the reviewer to judge origin 'at the base ref' but never names the base ref |
| `BG0828` | Medium | The one-call closes do not check the review brief: artifact.py close records a verdict with no brief and no warning, and transition --brief accepts... |
| `BG0829` | Medium | A unit carried at the review cap is filed as an ungroomed bug that sprint plan cannot take, and every carry prints that the operator was notified |
| `BG0830` | Medium | A verdict or delegated-token record written after the seal lands on the sealed run without a warning |
| `BG0831` | Medium | The configuration reference documents keys the code does not honour: sprint.split_above, review.policy carry-forward, and review.max_rounds |
| `BG0832` | Medium | reference-review.md step 3a ships a private project's consultation cast as its example, names amigos with no resolver, and the neutrality lane miss... |
| `BG0833` | Medium | The engagement floor judges a decomposed CR by its own criteria, so a CR reconcile derives Complete from planned children is refused as unplanned |
| `BG0834` | Medium | persona generate --team lets a pre-supplied or headless default stand as an answer, so its report claims questions were asked and accepted when non... |
| `BG0835` | Medium | Token capture looks for the session transcript in a directory named by replacing only '/', so a project path holding '.' or '_' reads NOT ATTRIBUTABLE |
| `BG0836` | Medium | No command writes a lesson class's graduated state, so every graduation CR carries a criterion only a hand edit can meet |
| `BG0837` | Medium | The pre-push gate judges the working tree, not the commits being pushed, so an uncommitted fix turns a red push green |
| `BG0838` | Medium | retired_surface excuses a live retired name by the shape of its sentence, so a live instruction passes as history |
| `BG0839` | Medium | An eval worker session loads the personal skill ahead of the candidate copy, and nothing in the harness says so or prevents it |
| `BG0840` | Medium | BG0818 did not converge in review: round 2 REJECT findings |
| `BG0841` | Medium | The review cap has no per-unit exception path, so an operator-granted extra round can only land by force |
| `BG0842` | Medium | migrate reports 2 index drift items on a v4.1 project whose gate reconcile lane fails on 28, because project upgrade counts two of reconcile's nine... |
| `BG0843` | Medium | migrate names no engagement-floor cutoff, so a v4.1 project's gate fails the engagement floor on 349 shipped units before and after the upgrade and... |
| `BG0844` | Medium | An upgraded project never gets the sdlc-studio/.gitignore that init writes, so gate.py leaves runtime state in git status on every run |
| `BG0845` | Medium | migrate's conformance cutoff on a v4.1 project exempts the 98 units after the project's own adoption point, because a verdict row with no Author co... |

35 findings: 35 Medium, 0 Low.

## Not carried

4 findings at a barred severity were ruled `Won't Fix` on their own merits: `BG0124`,
`BG0139`, `BG0583`, `BG0713`.

They are not in the list above because they are not open, and a disclosure that pads
its count is as misleading as one that trims it.

## How this list is kept

It is derived from the bug corpus by `tools/known_issues.py` when a release is cut, not
maintained by hand, and the pre-push hook refuses a tag whose page disagrees with the corpus.
Any open bug whose severity is Medium or Low appears here; a bug that reaches a terminal
status leaves at the next cut. Cut it with
`python3 tools/known_issues.py write --release <version>`.
