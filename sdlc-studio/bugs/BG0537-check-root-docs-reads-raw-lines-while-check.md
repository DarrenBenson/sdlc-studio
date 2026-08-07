# BG0537: check_root_docs reads raw lines while check_body_links blanks code spans, so a link inside backticks is an example in one directory and a broken reference in another

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/check_links.py, tools/tests/test_check_links.py
> **Evidence:** RUN-01KZCAJX, 2026-08-07. Found when the pre-commit `links` lane refused a commit whose only markdown change was the CHANGELOG regroup, naming CHANGELOG.md:606 -> file.md and CHANGELOG.md:1035 -> ../epics/EP0001-x.md. Both are examples inside backticks. Mutant `revert the ROOT_DOCS loop to path.read_text().splitlines()` applied and shown to kill three of the four new tests, the control surviving; restored byte-identical; `python3 tools/check_links.py` then reports all links resolving.
> **Created:** 2026-08-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`check_links.py` has two file-existence passes over markdown links. `check_body_links` runs its input through `_without_code` first, and that helper's docstring gives the reason: a link inside backticks or a fence is an EXAMPLE, not a reference, and without the blanking an artefact cannot DOCUMENT a broken link. `check_root_docs` - the pass that covers README, AGENTS, CLAUDE, CONTRIBUTING, SECURITY, INSTALL and CHANGELOG - iterates `path.read_text().splitlines()` raw.

So the identical text means two different things depending on which directory it sits in. A bug report under `sdlc-studio/` may quote the broken link it is about; a CHANGELOG entry describing the same thing fails the gate.

That is not hypothetical. The v5.0.0 changelog section describes a link guard that had been blind to bare cells, and quotes the form it DID match as `` `[text](file.md#anchor)` `` - inside backticks, as an example. A second entry quotes `` `[EP0001: Title](../epics/EP0001-x.md)` `` while describing an epic-census parser. Both were reported as broken links, and the commit carrying them was blocked.

## Steps to Reproduce

1. Add to any root doc - README.md will do - a line containing a markdown link inside a code span, pointing at a file that does not exist: ``The passes match `[text](file.md#anchor)`.`` 2. Run `python3 tools/check_links.py`. 3. It reports `README.md:N -> file.md [file missing]` and exits non-zero. 4. Put the same line in an artefact body under `sdlc-studio/` and it passes, because that pass blanks code spans first.

## Proposed Fix

Feed `check_root_docs` through `_without_code`, which already exists in the same module and already preserves line COUNT so a reported line number still points at the line the reader will open. One line.

The wider point is the one worth keeping: two passes over the same question that disagree about what counts as a link. The repo records this shape as a lesson - two paths that must agree on meaning, and do not - and the fix is not only to align them but to hold the alignment with a test that fails when one drifts. Four tests now cover it: a code span, a fenced block, a live broken link (the control - blanking must not blank what the pass exists to find), and line-number fidelity.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `check_links.py` has two file-existence passes over markdown links.
- [ ] **AC2** The proposed fix lands, pinned by a test: Feed `check_root_docs` through `_without_code`, which already exists in the same module and already preserves line COUNT so a reported line number still points...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-07 | sdlc-studio | Filed |
