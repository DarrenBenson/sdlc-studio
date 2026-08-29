# Known issues

The defects SDLC Studio knows about and has chosen to ship. This page is the disclosure
half of the release bar: a project that hides its open findings is asking to be trusted
rather than read.

## The bar v5.0.0 was held to

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
| `BG0490` | Medium | four bug repairs are Fixed with half their title undelivered and no recorded narrowing |
| `BG0493` | Medium | four more verifiers pass on a delivery that has been made inert |
| `BG0567` | Medium | the upgrading-project baseline compares against this tree minus one branch, not against the base ref, so a regression the epic introduced elsewhere... |
| `BG0578` | Medium | test-file attribution is decided by name frequency, so mentioning one more module silently changes a file's owner |
| `BG0591` | Medium | status and close_owed give opposite answers about the same units |
| `BG0601` | Medium | The dry-run class sweep compares only the first two probes of each pair |
| `BG0603` | Medium | Stacked Verify lines are refused at Draft and Ready but not on an Open bug |
| `BG0608` | Medium | The budget line still LEADS with the seconds comparison BG0594 proved uninformative, so the reader's eye lands on +130% and the real verdict sits i... |
| `BG0612` | Medium | Three limbs that survived the closure of BG0599 and BG0602: an edit-verb gap, an unpinned checklist roster and an import-time blind spot |
| `BG0614` | Medium | the mutation ledger keeps several LIVE rows on one (unit, criterion, row) key, and the join takes whichever was iterated last |
| `BG0627` | Medium | eleven other fields-file consumers carry the same `or ""` guard, so a falsey value is reported as a missing field across five more modules |
| `BG0628` | Medium | conformance reports a unit NON-CONFORMANT when it could not run the verifier at all, so the same corpus scores 304, 671 or 732 depending only on wh... |
| `BG0630` | Medium | the test-plan gate is skipped on In Progress to Done, so a unit that entered before its rejection was recorded reaches terminal without it ever bei... |
| `BG0631` | Medium | a repair row names neither the rejection nor the phase it answers, so it is joined by date alone and one day's repair discharges every rejection re... |
| `BG0632` | Medium | a retro's index carries no Title column, so `retitle` would rename the file and leave the index and its inbound link pointing at the old name with... |
| `BG0633` | Medium | transition.py annotate is a THIRD writer of Severity and carries no vocabulary, so the class BG0624 closed at two entry points is still open at the... |
| `BG0634` | Medium | the repair record truncates a finding label INSIDE a code span, leaving an unbalanced backtick that fails the repo's own markdownlint and blocks th... |
| `BG0635` | Medium | the close's convergence series counts ADVISORY gate lanes as outstanding blockers, so the review-repair loop can never converge and every close eve... |

18 findings: 18 Medium, 0 Low.

## Not carried

Three High findings were ruled `Won't Fix` on their own merits before this bar was set,
and one was superseded by later work. They are not in the list above because they are not
open, and a disclosure that pads its count is as misleading as one that trims it.

## How this list is kept

It is derived from the bug corpus by `tools/known_issues.py`, not maintained by hand, and
`tools/tests/test_known_issues.py` fails when the two disagree. Any bug at `Open` whose
severity is Medium or Low appears here; a bug that reaches a terminal status leaves.
Regenerate with `python3 tools/known_issues.py --write`.
