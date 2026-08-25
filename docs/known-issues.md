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

9 findings: 9 Medium, 0 Low.

## Not carried

Three High findings were ruled `Won't Fix` on their own merits before this bar was set,
and one was superseded by later work. They are not in the list above because they are not
open, and a disclosure that pads its count is as misleading as one that trims it.

## How this list is kept

It is derived from the bug corpus by `tools/known_issues.py`, not maintained by hand, and
`tools/tests/test_known_issues.py` fails when the two disagree. Any bug at `Open` whose
severity is Medium or Low appears here; a bug that reaches a terminal status leaves.
Regenerate with `python3 tools/known_issues.py --write`.
