# CR-0001: Documentation accuracy - command-vs-script scope and metadata convention

> **Status:** Complete
> **Priority:** Medium
> **Type:** Documentation
> **Requester:** Darren Benson
> **Date:** 2026-06-20
> **Affects:** sdlc-studio/prd.md, .claude/skills/sdlc-studio/reference-outputs.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

Resolve the three content-accuracy findings from the RV0001 unified review (P1,
P2, T1). All are documentation corrections; no behaviour changes.

## Problem

The brownfield extraction and review surfaced three doc-vs-reality gaps:

- **P1** - the PRD §3 Feature Inventory lists a script in the Location column for
  commands whose headline behaviour is actually Claude-orchestrated, so a reader
  could think `reconcile.py` applies fixes, `review_prep.py` runs the CODE leg, or
  `status.py` renders `--full`. The scripts are narrower (detect / prep / pillars).
- **P2** - §3 says all features are "Complete" while epics and stories are
  "Ready", with no statement that these measure different things (implementation
  vs extracted-spec validation).
- **T1** - `reference-outputs.md` states "all artifacts use YAML frontmatter",
  but the parser (`lib/sdlc_md.py`, `METADATA_FIELD_RE`) and every numbered-artifact
  template use `> **Field:**` blockquote headers. The doc is the outlier.

---

## Proposed Changes

### Item 1: Clarify command-vs-script in the PRD feature inventory (P1)

**Priority:** Medium **Effort:** Low

Add a note under the §3 table explaining that the Location column names the doc
and the deterministic script that backs each command, and that orchestration
(auto-fix, `--verify`, the CODE leg, `--full`, cadence) is the command around the
script. Point to the EP0005 stories for exact per-script scope.

### Item 2: Distinguish Complete from Ready (P2)

**Priority:** Low **Effort:** Low

Add a note that feature statuses describe the implementation, while the extracted
spec is tracked at epic/story level as Ready until test-validated.

### Item 3: Correct the metadata-convention doc (T1)

**Priority:** Medium **Effort:** Low

Rewrite `reference-outputs.md#frontmatter` to document the `> **Field:**`
blockquote-header convention the scripts parse, noting that project-level docs use
bold `**Field:**` lines and that SKILL.md's YAML frontmatter is a separate,
format-required case. **Back-port:** this edits skill source, so the same change
must be applied to the installed copy at `~/.claude/skills/sdlc-studio/`.

---

## Impact Assessment

### Existing Functionality

None. Documentation only; no script, template, or command behaviour changes.

### Affected Modules

| Module | Impact | Change Type |
| --- | --- | --- |
| sdlc-studio/prd.md | §3 notes added | Modified |
| reference-outputs.md | `#frontmatter` section corrected | Modified |
| Installed copy (~/.claude) | Same T1 edit must be forward-ported | Modified |

### Breaking Changes

None.

---

## Acceptance Criteria

- [x] PRD §3 has a command-vs-script note; no cell implies a script does Claude work.
- [x] PRD §3 states the Complete-vs-Ready distinction.
- [x] `reference-outputs.md#frontmatter` describes the blockquote-header convention and matches `lib/sdlc_md.py`.
- [x] `npm run lint` and `npm test` stay green; reconcile drift = 0.
- [x] Back-port of the T1 edit to the installed copy is recorded as a follow-up.

---

## Out of Scope

- The reference-doc-vs-script scope gaps in `reference-review.md` / `help/status.md`
  / `reference-reconcile.md` themselves (e.g. git-log vs mtime in review_prep).
  Tracked separately; this CR corrects the brownfield PRD and the canonical
  metadata convention only.

---

## Close Reason

> *Filled when CR is closed*

**Outcome:** Complete
**Rationale:** P1, P2 and T1 corrected (PRD §3 notes; `reference-outputs.md`
metadata convention). `npm run lint` exit 0, `npm test` 181 OK, reconcile drift=0.
**Follow-up:** the T1 edit changed skill source, so the same change must be
forward-ported to the installed copy at `~/.claude/skills/sdlc-studio/reference-outputs.md`.

---

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | CR raised from RV0001 findings (P1, P2, T1) |
| 2026-06-20 | Darren Benson | Fixes applied; verified green; CR Complete |
