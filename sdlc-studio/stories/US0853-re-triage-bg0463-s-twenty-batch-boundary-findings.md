# US0853: re-triage BG0463's twenty batch-boundary findings against HEAD and file the survivors

> **Status:** Review
> **Delivers:** CR0557
> **Created:** 2026-09-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/bugs, sdlc-studio/change-requests
> **Epic:** EP0257
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** re-triage BG0463's twenty batch-boundary findings against HEAD and file the survivors
**So that** CR0557 is delivered by work that can be planned and checked

## Acceptance Criteria

BG0463 aggregated twenty non-blocking findings from the RUN-01KYTKA1 batch-boundary review in
July and was closed as unbuildable: its items are bare `- [ ]` bullets with no `**ACn**` ids, so
no test plan can be derived from it and no terminal gate can read it. The observations are not
worthless - twenty from an independent pass rarely are - but they have sat for months, and this
project has a recorded case of five closed bugs that were never defects.

### AC1: each of the twenty is re-run against HEAD and ruled, and the ruling names what was observed

- **Given** BG0463's twenty findings, and HEAD
- **When** each is re-read and its premise re-executed against the current tree
- **Then** each carries a dated ruling of `still true`, `already fixed`, or `never was a defect`, and an `already fixed` ruling names the change that fixed it while a `never was` ruling says what the original observation actually saw. Twenty rulings, not one aggregate verdict
- **Mutant:** rule the twenty as a block from the aggregate's age - "these are months old, close them" reaches the same count with none of them read, and the observations an independent pass found are discarded on a date rather than on a premise
- **Verify:** shell python3 -c "import pathlib,re,sys; t=next(pathlib.Path('sdlc-studio/bugs').rglob('BG0463*.md')).read_text(encoding='utf-8'); n=len(re.findall(r'(?im)^.*\b(still true|already fixed|never was a defect)\b.*$', t)); print('rulings found:', n); sys.exit(0 if n >= 20 else 1)"
- **Verified:** yes (2026-09-21)

### AC2: a finding ruled STILL TRUE is filed as its own unit with criteria, not left as a bullet

- **Given** the subset ruled still true
- **When** each is carried forward
- **Then** it becomes its own artefact through `file_finding.py`, with its own criteria, `Affects` and size - which is precisely what BG0463 could not offer, and the reason it was closed as unbuildable. Nothing carries forward as a bullet inside another artefact
- **Mutant:** re-file the survivors as a second aggregate - the new artefact inherits the old one's defect exactly, cannot produce a test plan, cannot reach a terminal gate, and welds several files into one atomic block whose planning cost was already measured once
- **Verify:** shell python3 -c "import pathlib,re,sys; buckets=[q for q in pathlib.Path('sdlc-studio').rglob('*.md') if re.search(r'(?m)^> \\*\\*Consolidation:\\*\\*', q.read_text(encoding='utf-8'))]; bad=[q.name for q in buckets if 'BG0463' in q.read_text(encoding='utf-8')]; print('survivors still carried as bullets inside:', bad) if bad else None; sys.exit(1 if bad else 0)"
- **Verified:** no (2026-09-21)
- **Verified:** PARTIAL (2026-09-21) - met for 13 of the 15 survivors, and NOT met for claims 8 and 15. Both are genuinely Low severity, and `triage_noise.should_consolidate` routes every Low finding into a themed consolidation CR by DESIGN - it is config policy (`low_consolidation`), not an accident - so they landed in CR0592 as bullets, which is the shape this criterion's own mutant names. Delivery review raised it and was right on the criterion's words. The criterion over-reached: it demanded a shape the shipped filer will not produce for Low findings, and satisfying it would have meant either inflating two severities or switching off a deliberate mechanism mid-run. Recorded as unmet rather than argued away; BG0731 already carries the underlying conflict between that mechanism and D0217.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | rule the twenty as a block from the aggregate's age - "these are months old, close them" reaches the same count with none of them read, and the observations an independent pass found are discarded on a date rather than on a premise | each of the twenty is re-run against HEAD and ruled, and the ruling names what was observed |
| AC2 | re-file the survivors as a second aggregate - the new artefact inherits the old one's defect exactly, cannot produce a test plan, cannot reach a terminal gate, and welds several files into one atomic block whose planning cost was already measured once | a finding ruled STILL TRUE is filed as its own unit with criteria, not left as a bullet |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-20 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-21 | delivery | Re-triage complete. TWENTY-FOUR claims found, not twenty - BG0463 states them as semicolon-separated clauses, and every previous count, including this story's own criteria, counted paragraphs. 15 still true, 5 already fixed (each naming what fixed it), 1 never was a defect, 3 unfalsifiable as written. The 15 survivors are filed as BG0723-BG0730 and CR0592, grouped ONLY where one remedy genuinely covers several claims - never as a second aggregate, which is the mutant AC2 names. Filing them also surfaced BG0731: two Low-severity survivors were auto-consolidated into a new bucket CR0592, recreating the artefact D0217 retired the day before. |
| 2026-09-21 | delivery review r2 | AC2's verifier replaced so the gate reads what the record says. Delivery review approved the PARTIAL disposition but warned it depends on the close treating a non-`yes` `Verified:` line as unsatisfied - and it does not: `Verified:` is PROSE, only the `Verify:` selector's exit code counts, and the old selector passed because it merely checked that referenced ids resolve, which a consolidation bucket satisfies. So an honest self-report of a miss was being laundered into a green. The verifier now tests AC2's actual claim - that no survivor is carried as a bullet inside a consolidation artefact - and so it FAILS, which is the truth. Filed as BG0733. |
