# BG0105: rebaseline_apply used a Python 3.13-only API; CI (3.12) red on both v4 pushes

> **Status:** Fixed
> **Verification depth:** functional (portable read/write, CRLF tests green, CI failure class eliminated by construction)
> **Severity:** Medium
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

`Path.read_text`/`write_text` only accept newline= from Python 3.13. The schema-v3 rebaseline backfill used them to preserve CRLF terminators; local dev runs 3.14 so every local suite pass was green, while CI pins 3.12 and failed all four Backfill/NoFabricatedHistory tests on both pushed commits (rc.1 and the docs push). The declared floor is 3.10. Fixed with open(..., newline='') which has accepted newline since 2.6; comment now names the floor so the next 3.13-ism gets caught in review.

## Steps to Reproduce

CI run 29117412379: TypeError: `Path.read_text()` got an unexpected keyword argument 'newline' x4

## Proposed Fix

open()-based read/write with newline='' in `rebaseline_apply`; grep confirms no other newline= Path calls outside tests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Filed |
