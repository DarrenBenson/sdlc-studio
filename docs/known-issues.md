# Known issues

The defects SDLC Studio knows about and has chosen to ship. This page is the disclosure
half of the release bar: a project that hides its open findings is asking to be trusted
rather than read.

## The bar v6.1 is held to

**Zero open Critical or High finding at the tag, and every open Medium ruled by one triage
decision.** A finding either reaches a terminal status with its own verifiers passing, or it
stays open under the triage target below, which one recorded decision rules for the whole list
rather than a waiver per finding.

**Medium and Low findings ship open, listed here by id, triaged to v6.2.** Each is a real
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

## Triaged to v6.2

| Id | Severity | Finding |
| --- | --- | --- |
| `BG0940` | Medium | A ruling logged between the close and the sign changes the filed page, and sign seals it without re-deriving |

1 findings: 1 Medium, 0 Low.

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
