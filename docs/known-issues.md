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
| `BG0463` | Medium | Twenty non-blocking findings from the RUN-01KYTKA1 batch-boundary review: stale counts, dead code, unmarked truncation, over-claiming docstrings an... |
| `BG0490` | Medium | four bug repairs are Fixed with half their title undelivered and no recorded narrowing |
| `BG0493` | Medium | four more verifiers pass on a delivery that has been made inert |
| `BG0567` | Medium | the upgrading-project baseline compares against this tree minus one branch, not against the base ref, so a regression the epic introduced elsewhere... |
| `BG0578` | Medium | test-file attribution is decided by name frequency, so mentioning one more module silently changes a file's owner |
| `BG0581` | Medium | the goal-review brief states a reachable end state without knowing the rung, so it promises Review for a design rung that ends at Ready |
| `BG0584` | Medium | the tick-verification checklist row is rung-blind, so a grooming run cannot answer it |
| `BG0587` | Medium | two answers to the grooming question inside one close |
| `BG0589` | Medium | the close pre-flight counts advisory rows as unmet prerequisites |
| `BG0590` | Medium | sprint close appends a handoff bullet that fails the repo's own markdown lane |

10 findings: 10 Medium, 0 Low.

## Not carried

Three High findings were ruled `Won't Fix` on their own merits before this bar was set,
and one was superseded by later work. They are not in the list above because they are not
open, and a disclosure that pads its count is as misleading as one that trims it.

## How this list is kept

It is derived from the bug corpus by `tools/known_issues.py`, not maintained by hand, and
`tools/tests/test_known_issues.py` fails when the two disagree. Any bug at `Open` whose
severity is Medium or Low appears here; a bug that reaches a terminal status leaves.
Regenerate with `python3 tools/known_issues.py --write`.
