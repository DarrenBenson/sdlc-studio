# US0051: Textual mutation engine: declared fault classes, language profiles, anchored apply/restore

> **Status:** Ready
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Epic:** EP0011
> **Persona:** Dani (Engineering amigo)
> **Story Points:** 5
> **Depends on:** -

## User Story

**As a** skill maintainer enforcing assertion integrity
**I want** a deterministic textual mutation engine with a declared, bounded fault-class set
**So that** the changed surface can be fault-injected identically on every run, in any language a profile covers, with uncovered surfaces reported un-checked rather than passed

## Design (settles RFC-0022 D1-D3 within the accepted direction)

- **Fault classes (D2), the declared v1 floor:** `invert-guard` (negate an `if` condition),
  `stub-return-null` (a `return X` delivers the language's null), `unset-delivered-field`
  (an assignment delivers null instead of its value), `no-op-mapper` (a function body
  short-circuits to `return None` - Python profile first).
- **Language profiles:** pattern tables keyed by file extension (`.py`, `.js`/`.ts`, `.go` for
  invert-guard). A class with no pattern for a file's language is **un-checked** for that file -
  recorded, never silently passed.
- **Anchor (D3):** a mutation is identified by `(file, fault class, occurrence index)` over the
  pattern's line-ordered matches, so the same code + same set yields the same mutation list.
- **Apply/restore:** one mutation at a time; the original file content is restored after each
  run even on error (try/finally) - the engine must never leave a mutant on disk.

## Acceptance Criteria

### AC1: deterministic mutation enumeration

- **Given** a target file and the declared fault-class set
- **When** the engine enumerates mutations twice
- **Then** the two lists are identical (file, class, occurrence, line), ordered by line
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::EngineTests::test_enumeration_is_deterministic

### AC2: each fault class mutates its Python form

- **Given** a Python file containing a guard, a return, an assignment, and a function body
- **When** each class's mutation is applied
- **Then** the guard is negated, the return delivers None, the assignment delivers None, and the mapper body short-circuits - one mutation at a time
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::EngineTests::test_each_class_mutates_python

### AC3: apply/restore round-trip is loss-free

- **Given** any applied mutation
- **When** the engine restores
- **Then** the file is byte-identical to the original, including after a runner exception
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::EngineTests::test_restore_is_byte_identical

### AC4: uncovered language reports un-checked, never passed

- **Given** a file whose extension has no profile for a fault class
- **When** the engine enumerates
- **Then** that (file, class) pair appears in the un-checked list with a reason
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::EngineTests::test_uncovered_language_unchecked

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | sdlc | Created via `new` (deterministic) |
| 2026-07-04 | claude | Authored at design: D1-D3 settled per accepted RFC-0022; points + ACs + Verify lines |
