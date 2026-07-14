# BG0143: The new body-link pass flags links inside code spans and fenced blocks, so no artefact can document a broken link

> **Status:** Fixed
> **Severity:** Medium
> **Effort:** S
> **Affects:** tools/check_links.py
> **Verification depth:** functional - driven through the public guard and checked on its TRUE exit code, not its printed output (a guard that reports a failure and exits 0 is BG0134's defect). A probe artefact carrying a live dead link, the same link in a code span, and the same link in a fenced block reports ONLY the live one; a genuinely dead body link makes check_links exit 1, and the clean repo exits 0.
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

BG0138 added a body-link pass to `check_links.py`: every relative markdown link in a workspace artefact body must resolve. It does not honour CODE SPANS or FENCED CODE BLOCKS, so a link written as an EXAMPLE is treated as a live link and reported broken.

The consequence bites immediately and is self-referential: a bug report ABOUT broken links cannot quote the broken link it is reporting. BG0137 Steps to Reproduce contains the example `[BG-0001](BG0001-x.md)` - the exact wrong-depth link the bug exists to describe - and the guard fails the whole repo on it. Wrapping it in backticks does not help, because the pass does not look for them.

Proved with a probe artefact: a live broken link, the same link inside a code span, and the same link inside a fenced markdown block. All three were reported. Only the first is a defect; the other two are documentation.

This is the same class BG0132 detector got RIGHT: the filer pseudo-Verify check deliberately distinguishes a command written as prose from one written as an example. The link checker needs the same discrimination and does not have it.

The guard is otherwise good and its scoping decision was careful (the skill tree with its 56 template placeholders is deliberately excluded). This is a narrow gap in an otherwise sound pass, but it currently BLOCKS the commit gate, because the repo legitimately contains a documented example of a broken link.

## Steps to Reproduce

1. Create a workspace artefact whose body contains: a live broken link; the same link inside a code span (backticks); and the same link inside a fenced markdown block. 2. Run python3 tools/`check_links.py.` 3. All THREE are reported as broken and the exit code is 1. Only the first is a real defect. 4. In the live repo, BG0137 line 18 quotes the broken link it reports and fails the gate even after being wrapped in a code span.

## Proposed Fix

Strip fenced code blocks and inline code spans before scanning a body for links, exactly as the pseudo-Verify detector in `file_finding.py` already does for command-shaped text. A link inside backticks or a fence is an EXAMPLE, not a reference, and a documentation tool that cannot document its own subject matter is broken. Guard it with a test carrying all three shapes - live, code-span, fenced - asserting that only the live one is reported.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
