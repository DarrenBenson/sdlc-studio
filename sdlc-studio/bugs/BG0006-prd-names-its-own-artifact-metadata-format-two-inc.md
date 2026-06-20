# BG-0006: PRD names its own artifact metadata format two incompatible ways (YAML frontmatter vs blockquote headers)

> **Status:** Fixed
> **Severity:** High
> **Reporter:** Project Audit
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

Functional Requirements claims every artifact has YAML frontmatter, but Data Models and the parser of record (lib/sdlc_md.py) and all real artifacts use blockquote metadata headers.

## Problem

prd.md:209 states artifacts have 'YAML frontmatter', while prd.md:277-281 states metadata 'is carried as > **Field:** value blockquote headers ... the parser of record reads the blockquote headers'. Real artifacts (epics, stories) use blockquote headers, no YAML frontmatter block. The PRD names its primary data model two incompatible ways.

## Proposed Fix

In prd.md:209 replace 'YAML frontmatter' with 'blockquote metadata headers (> **Field:** value)' to match §7 and the parser of record. If frontmatter is a genuine accepted alternate, state that explicitly and reconcile with the §7 open question rather than asserting it as the universal rule.

## Evidence

prd.md:209 'YAML frontmatter' vs prd.md:277-281 'blockquote headers ... the parser of record reads the blockquote headers'

## Impact

Untestable core spec: an implementer cannot tell which metadata format is authoritative, and the document fails its own traceability standard by disagreeing with itself on the primary data model.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Project Audit | Filed from the 2026-06-20 project-profile audit (lens: prd) |
