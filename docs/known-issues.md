# Known issues

The defects SDLC Studio knows about and has chosen to ship. This page is the disclosure
half of the release bar: a project that hides its open findings is asking to be trusted
rather than read.

## The bar v6.0 is held to

**Zero open Critical or High finding at the tag, and every open Medium ruled by one triage
decision.** A finding either reaches a terminal status with its own verifiers passing, or it
stays open under the triage target below, which one recorded decision rules for the whole list
rather than a waiver per finding.

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

**Medium and Low findings ship open, listed here by id, triaged to v6.1.** Each is a real
defect with a reproduction and, in most cases, a proposed fix. None of them stops the
lifecycle running. They are listed rather than closed, because closing a bug to make a
release look clean is the practice this tool exists to prevent.

Each id below is a file in `sdlc-studio/bugs/` in the source repository, carrying the
evidence, the reproduction and the proposed fix in full.

## Triaged to v6.1

| Id | Severity | Finding |
| --- | --- | --- |
| `BG0682` | Medium | artifact.py revision writes a bare _identifier into the Revision History, which markdownlint refuses as MD037 |
| `BG0691` | Medium | changelog.py shape judges unreadable and symlinked fragments differently in its two modes, and its git-failure refusals are unpinned |
| `BG0692` | Medium | gate.py never sets the boundary-suite marker itself, so SDLC_GATE_BOUNDARY=push reads [PASS] module-alone over a red boundary-only test |
| `BG0696` | Medium | critic.py's brief checks search the whole brief, so a unit's own text hides a dropped surface, and a REJECT marked as matching no brief can never b... |
| `BG0701` | Medium | Run-ending routes still read different sets: stop records from the parked derivation, the boundary stop ignores --retro, and stop cannot see the re... |
| `BG0705` | Medium | The Findings-filed-to line survives a reopen, is not reported in text output, and names only the filed subset of a partial repair |
| `BG0706` | Medium | The coverage gate charges another unit's added lines to a unit sharing its file, and a coverage ruling is voided by any edit to that file |
| `BG0708` | Medium | gate.py reads SDLC_VERIFY_TIMEOUT per call, so a previously hermetic suite now inherits whatever the environment sets |
| `BG0712` | Medium | a local guard that tolerates what a criterion refuses lets a breach pass the commit and redden CI |
| `BG0714` | Medium | 284 added lines of RUN-01M2SPNS are executed by no verifier in the run, and BG0706's proposed fix inherits most of the false charge |
| `BG0725` | Medium | two spellings of the stop-ship constant, and a hand-maintained verb list whose stale entries nothing can report |
| `BG0726` | Medium | the report renders NO DECLARED SEAT without asking whether the project declares any personas at all |
| `BG0734` | Medium | the blockquote skip in check_versions is unreachable, so it guards nothing |
| `BG0737` | Medium | the stale downgrade destroys an author's reason on a positive verdict, so the principle BG0733 shipped is violated on the sibling branch of the sam... |
| `BG0739` | Medium | close_owed reads the Raised-in-batch stamp by its last token while asserting it reads it exactly as sprint_report does, and the two now genuinely d... |
| `BG0740` | Medium | a gate stood down in prose rather than as a waiver row is invisible to the report's waiver disclosure, which is how the one the operator most neede... |
| `BG0752` | Medium | Per-commit test selection skips hooks, test infrastructure and code reached through another script |
| `BG0754` | Medium | A commit touching a widely imported script runs well over the 90-second budget |
| `BG0782` | Medium | About 57 test modules commit in a temporary git repo with auto-maintenance on, the race BG0711 fixed in one |
| `BG0783` | Medium | Review rounds are write-dead after US0918, so the ceiling and repair-regression readers of run-state rounds read nothing |
| `BG0784` | Medium | A seat card with no role line is silently bypassed for the shipped card, and the unknown-seat refusal names the wrong seats |
| `BG0785` | Medium | migrate leaves a v4-era project's conformance lane red on its pre-adoption stories and names no cutoff for them |
| `BG0786` | Medium | flow.py compute takes about 90 seconds on this repository, so its CLI grammar control times out at 120 under load and reddens the push gate |
| `BG0788` | Medium | Signed-report rounds are positional, so a hand-deleted verdict row goes unseen when a same-day later run re-reviewed the unit, and verdict rows car... |
| `BG0790` | Medium | An installed release candidate is never prompted to move to its final release, because version comparison ignores the pre-release suffix |
| `BG0792` | Medium | US0940 AC1's own Verify takes about three minutes, so the release gate's verify lane reads it red at the 120-second default |

26 findings: 26 Medium, 0 Low.

## Not carried

Three High findings were ruled `Won't Fix` on their own merits before this bar was set,
and one was superseded by later work. They are not in the list above because they are not
open, and a disclosure that pads its count is as misleading as one that trims it.

## How this list is kept

It is derived from the bug corpus by `tools/known_issues.py` when a release is cut, not
maintained by hand, and the pre-push hook refuses a tag whose page disagrees with the corpus.
Any open bug whose severity is Medium or Low appears here; a bug that reaches a terminal
status leaves at the next cut. Cut it with
`python3 tools/known_issues.py write --release <version>`.
