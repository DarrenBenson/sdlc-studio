# CR-0009: Make best-practices guides sliceable and load-once; a TypeScript code plan misses the DOM guidance it delegates to javascript.md

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Requester:** Adversarial Audit
> **Date:** 2026-06-20
> **Affects:** reference-code.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

The per-language best-practices guides carry zero section anchors so code plan/implement can only load them whole (go.md 416, javascript.md 372, sql.md 371 lines) and can re-load the same guide twice per story; the js/ts split means a TS plan loads typescript.md but silently misses the DOM/selector guidance typescript.md itself delegates to the un-loaded javascript.md.

## Problem

reference-code.md instructs reading a per-language guide at both plan time (line 66) and implement time (235-238); a grep for '{#' anchors across go.md/python.md/javascript.md returns zero, so the workflow can only load the entire guide, and code plan and implement issue the same instruction so one story can re-load the same 400-line guide twice. Separately, typescript.md (229 lines) opens 'For browser/DOM patterns shared with plain JavaScript, see javascript.md', but the loader (PLG line 103) pulls exactly one language file, so a TS code plan loads typescript.md and silently misses the DOM/selector best-practices in javascript.md (372 lines). (postgresql.md/sql.md split overlapping query-optimisation content similarly.)

## Proposed Changes

### Item 1: Make best-practices guides sliceable and load-once; a TypeScript code plan misses the DOM guidance it delegates to javascript.md

**Priority:** Medium **Effort:** TBD

Add section anchors to the best-practices guides (e.g. {#error-handling}, {#testing}, {#conventions}) and change the code workflow to load only the slice relevant to the story's surface area, or cache the guide once at plan time and have implement reuse it. At minimum add an anchored 'Quick conventions' header so the workflow can pull a 30-line summary instead of the full guide. For the web pair, have the loader pull both javascript.md and typescript.md whenever language resolves to TS (so the delegated DOM guidance is present), or merge them into one best-practices/web.md; apply the same single-file approach to the sql/postgresql pair. (Note the file-merge half is an RFC-shaped capability change, deferrable; the anchors + dual-load fix is the bounded core.)

## Impact Assessment

### Existing Functionality

Each code plan/implement of a Go or JS story pays a 370-420 line whole-file load that cannot be narrowed, the same guide can load twice per story, and a TypeScript plan silently misses the DOM/selector best-practices typescript.md explicitly delegates - avoidable per-command context plus a correctness gap. Token and quality risk medium.

## Acceptance Criteria

- [x] The best-practices guides carry section anchors (e.g. `{#testing}`, `{#conventions}`) so the code workflow can pull a slice rather than the whole file.
- [x] When the story language resolves to TypeScript, the loader pulls both `javascript.md` and `typescript.md`, so the delegated DOM guidance is present.
- [x] (The file-merge into `web.md` is RFC-shaped and deferred; anchors + dual-load are the bounded core here.)

## Out of Scope

- Implementation is downstream; this CR records the audit finding.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (backlog-closeout) | Complete (bounded core) - TS/PostgreSQL dual-load in reference-code.md + {#quick-conventions} anchors in the 4 pair guides; file-merge deferred (RFC-shaped) |
| 2026-06-20 | Adversarial Audit | Filed from the 2026-06-20 audit (lens: token-economy / over-engineering; evidence: reference-code.md:65-66 and :235-238 (plan and implement both 'Read best-practices/{lang}.md'); grep -c '{#' = 0 for best-practices/go.md, python.md, javascript.md; typescript.md header delegates DOM patterns to javascript.md while PLG line 103 loads exactly one language file) |
