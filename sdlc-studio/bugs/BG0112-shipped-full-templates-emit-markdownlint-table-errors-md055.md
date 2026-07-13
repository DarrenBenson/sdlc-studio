# BG0112: shipped full templates emit markdownlint table errors (MD055/MD056/MD060) from the creator

> **Status:** Open
> **Target:** v4.1
> **Severity:** Low
> **Created:** 2026-07-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Dani Okafor; persona; v1

## Summary

Found while delivering BG0108 (2026-07-13). The shipped plan / test-spec / workflow / bug full templates emit MD055, MD056 and MD060 table-style lint errors as created. This is the same family as BG0108 - a deterministic creator producing output that a house guard rejects - but it is a markdownlint mismatch rather than a validate.py one, so BG0108's create-then-validate round trip does not catch it. Every artefact of these types created from the full template starts life failing lint:md.

## Steps to Reproduce

1. artifact.py new --type plan --title X --template full. 2. Run markdownlint against the created file. 3. MD055/MD056/MD060 table errors on the template's own tables.

## Proposed Fix

Fix the table syntax in templates/core/{plan,test-spec,workflow,bug}.md, and extend BG0108's round-trip test with a markdownlint leg so creator output is checked against BOTH deterministic guards, not just the validator.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-13 | audit | Filed |
