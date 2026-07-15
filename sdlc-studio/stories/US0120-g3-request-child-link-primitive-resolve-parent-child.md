# US0120: G3 request-child link primitive: resolve parent<->child both ways, write links on both sides, reconcile verifies

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Epic:** EP0033
> **Points:** 5

## User Story

**As an** agent decomposing a request into work
**I want** one shared primitive that resolves a request's children and a child's parent, and a reconcile check that a declared link resolves both ways
**So that** the derived-status, two-backlog and UNDECOMPOSED gates (US0122/US0123/US0124) all answer "what did this request produce" the same way, and a one-sided link is caught as drift.

## Acceptance Criteria

### AC1: children_of resolves each level of a request -> product chain

- **Given** an RFC -> CR -> epic -> stories chain on disk, linked with `Parent:` (and a story's `Epic:`)
- **When** `sdlc_md.children_of(root, id)` is called at each level
- **Then** an RFC returns its CRs, a CR returns its epics, an epic returns its stories, and a childless id returns `[]`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::LinkPrimitiveTests
- **Verified:** yes (2026-07-15)

### AC2: the taxonomy names which types are requests

- **Given** the two-backlog split (RFC/CR are requests; epic/story/bug are product)
- **When** `sdlc_md.is_request(type_)` is called
- **Then** it is true for cr/rfc and false for epic/story/bug - the one predicate the planner and status share
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::TaxonomyTests
- **Verified:** yes (2026-07-15)

### AC3: reconcile reports a link declared on one side only as link-asymmetry

- **Given** a chain where a child names a `Parent:` that does not exist, or names a parent that does not list it back, or a request's `Decomposed-into:` names a child that does not resolve
- **When** `reconcile.link_asymmetry_drift(root)` runs (wired into `reconcile detect` on the full sweep)
- **Then** each one-sided link is reported as a `link-asymmetry` drift item, and a fully symmetric chain is clean
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::LinkAsymmetryDriftTests
- **Verified:** yes (2026-07-15)

### AC4: link-asymmetry is a registered, hinted drift kind

- **Given** the new drift kind
- **When** the reconcile drift-kind conformance test and the remediation-registry test run
- **Then** `link-asymmetry` is in `DRIFT_KINDS`, is emitted by a detector, and carries a remediation hint
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::DriftKindVocabularyTests
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-15 | sdlc-studio | ACs written; link primitive + reconcile link-asymmetry check delivered |
