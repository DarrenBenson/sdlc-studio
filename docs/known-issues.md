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
| `BG0659` | Medium | a code span whose value ends in a space cannot be recorded in any review ledger - markdownlint MD038 refuses the row |
| `BG0661` | Medium | revert-check cannot see a unit whose fix and evidence share one file - it reverts the tests with the change and reports green |
| `BG0662` | Medium | nothing checks a changelog fragment's SHAPE until the release cut, and 59 of 119 had drifted past it |
| `BG0664` | Medium | the pre-push boundary gate runs NO boundary-only test, so the marker's own promise is false at the boundary it names |
| `BG0665` | Medium | seven of thirteen `review.*` settings are absent from the file that calls itself the single source of truth, and two of them are named in refusals... |
| `BG0666` | Medium | an UNAUTHORED Test Plan row is exempt from the quality guard an authored one must pass, so leaving the placeholder buys a clean derive |
| `BG0667` | Medium | the root-effect control's real-tree marker is bound to an id range this project has already outgrown, so its evidence window closes as ids advance |
| `BG0668` | Medium | tag-check refuses on a close the close-owed predicate says is not owed |

8 findings: 8 Medium, 0 Low.

## Not carried

Three High findings were ruled `Won't Fix` on their own merits before this bar was set,
and one was superseded by later work. They are not in the list above because they are not
open, and a disclosure that pads its count is as misleading as one that trims it.

## How this list is kept

It is derived from the bug corpus by `tools/known_issues.py`, not maintained by hand, and
`tools/tests/test_known_issues.py` fails when the two disagree. Any bug at `Open` whose
severity is Medium or Low appears here; a bug that reaches a terminal status leaves.
Regenerate with `python3 tools/known_issues.py --write`.
