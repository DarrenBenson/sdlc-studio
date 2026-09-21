# US0840: a consult artefact carries each persona's verdict and a disposition per finding, so a consult can be counted rather than remembered

> **Status:** Superseded
> **Superseded-by:** US0858, US0859
> **Delivers:** RFC0058
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/consult.py, .claude/skills/sdlc-studio/scripts/tests/test_consult.py
> **Epic:** EP0256
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** reviewer of record reading what a consult produced
**I want** each persona's verdict and exactly one disposition per finding in a shape a script can read
**So that** a consult can be counted rather than remembered

## Acceptance Criteria

D3 - what a consult artefact must carry for a gate to count it - is OPEN. This story assumes the
shape the two consults already written use (`sdlc-studio/reviews/consult-*.md`): a stamped
`> **Units:**` line, one verdict row per persona under `## Verdicts`, and one row per finding under
`## Dispositions`, extended with a column naming the persona who raised it, which US0842 needs and
neither existing artefact carries. `scripts/consult.py` does not exist; this story builds it as a
reader. Nothing here gates - it parses and counts, and US0838's refine refusal stays the only gate
in EP0256.

### AC1: every consulted persona carries a verdict from the closed set, and a missing one is named

- **Given** a fixture consult artefact naming three personas with verdicts Approve, Concerns and Reject, and a copy of it with one persona's verdict cell emptied
- **When** `consult.py parse <path> --format json` runs through `main` on each
- **Then** the first returns three rows, each naming the persona, the cast role and a verdict from exactly {Approve, Concerns, Reject}; the second exits 2 naming the persona whose cell is empty; and a third copy whose verdict cell reads `Approve with notes` also exits 2, naming the value it could not place in the set
- **Mutant:** read an unrecognised or empty verdict as Approve, or drop that persona's row - a consult that lost a persona then counts as a full panel, and US0842's yield counts a verdict it never received
- **Verify:** superseded by US0858 AC1 - that unit owns this verifier

### AC2: a disposition is one of the closed set, and a FILE disposition names an id that resolves

- **Given** a fixture artefact whose dispositions table holds one valid row per disposition - FOLD, FILE naming an id present in the tree, DECLINED with a reason, OPERATOR RULING OWED - plus three built to fail: an empty disposition cell, a cell reading `will consider`, and a FILE row naming an id that resolves nowhere
- **When** `consult.py parse` runs
- **Then** the four valid rows are returned with their disposition, each of the three is returned marked `unanswered` with the reason that made it so, and the count of unanswered rows is part of the result, because US0841 reports on it
- **Mutant:** accept any non-empty cell as a disposition - `will consider` then answers a Reject, and the unanswered list US0841 prints is permanently empty whatever the consult found
- **Verify:** superseded by US0858 AC2 - that unit owns this verifier

### AC3: coverage is the stamped unit list, never re-derived from the tree

- **Given** a fixture artefact whose `> **Units:**` line names an epic and two of its stories, in a tree where that epic has since gained a third story and one named story has been deleted
- **When** `consult.py units <path>` runs
- **Then** it returns exactly the two stamped story ids and the epic, the later story is absent, and the deleted id is reported beside the list as unresolvable rather than dropped from it
- **Mutant:** read the epic's children at parse time instead of the stamped line - a consult then silently covers every unit added after it ran, which is the one thing a coverage record exists to prevent
- **Verify:** superseded by US0859 AC3 - that unit owns this verifier

### AC4: each verdict row's cast role is read from the persona card, so the anti-persona is identifiable

- **Given** a fixture tree carrying three persona cards, one holding `| **Cast role** | Negative |`, and two artefacts naming the same three personas but heading their sections differently - as `## Verdicts` with a free-text perspective column, and as `### Negative (anti-persona) Perspectives`, the two shapes already in `sdlc-studio/reviews/`
- **When** `consult.py parse` runs on both
- **Then** both return the same cast role per persona, read from the card rather than from the document; and a fourth persona named in the artefact with no card in the tree carries cast role `unknown` and is named in the output, never defaulted
- **Mutant:** infer the cast role from the section heading the artefact renders - the two consults already written head that section differently, so on one of them the anti-persona US0842 must count separately is read as an ordinary user
- **Verify:** superseded by US0859 AC4 - that unit owns this verifier

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-21 | decomposition | Superseded by US0858, US0859 (5 + 3 points) in RUN-01M306PY under D0222. It sat at the 8-point ceiling where this project's own tooling says estimation reliability falls off. Every criterion is carried VERBATIM into exactly one part - nothing dropped, nothing widened - so the scope is provably unchanged and only the sizing moves. |
