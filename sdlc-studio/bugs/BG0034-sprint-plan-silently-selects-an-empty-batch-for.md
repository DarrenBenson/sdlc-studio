# BG0034: sprint plan silently selects an empty batch for lowercase --crs/--bugs/--stories status args

> **Status:** Closed
> **Severity:** high
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

help/help.md documents lowercase status values (--crs proposed, --bugs open) but select_batch compares the raw arg against canonical_status (title-case 'Proposed'), so the batch is empty with no error - an untested determinism break between help prose and the case-sensitive script.

## Steps to Reproduce

From a repo with a Proposed CR, run sprint --crs proposed --goal done (the help/help.md form). select_batch compares st (canonical title-case) != status (raw lowercase arg), so every CR is skipped -> empty batch, count 0, no error. argparse help shows title-case and every test uses title-case, so the lowercase documented form is untested.

## Proposed Fix

Canonicalise the status arg against vocab in select_batch (target = canonical_status(status, vocab) or status; compare st != target); if it resolves to no vocab term, exit non-zero listing the valid vocabulary rather than matching nothing silently. Add a test_sprint.py case that lowercase --crs proposed selects the same batch as Proposed. Correct help/help.md to title-case. CHANGELOG entry same commit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Filed |
