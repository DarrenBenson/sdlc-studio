# US0853: re-triage BG0463's twenty batch-boundary findings against HEAD and file the survivors

> **Status:** Ready
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
- **Verified:** no

### AC2: a finding ruled STILL TRUE is filed as its own unit with criteria, not left as a bullet

- **Given** the subset ruled still true
- **When** each is carried forward
- **Then** it becomes its own artefact through `file_finding.py`, with its own criteria, `Affects` and size - which is precisely what BG0463 could not offer, and the reason it was closed as unbuildable. Nothing carries forward as a bullet inside another artefact
- **Mutant:** re-file the survivors as a second aggregate - the new artefact inherits the old one's defect exactly, cannot produce a test plan, cannot reach a terminal gate, and welds several files into one atomic block whose planning cost was already measured once
- **Verify:** shell python3 -c "import pathlib,re,sys; t=next(pathlib.Path('sdlc-studio/bugs').rglob('BG0463*.md')).read_text(encoding='utf-8'); ids=set(re.findall(r'\b(?:BG|CR)\d{4}\b', t)); survivors=[i for i in ids if any(pathlib.Path('sdlc-studio').rglob(i+'*.md'))]; print('carried-forward artefacts:', sorted(survivors)); sys.exit(0 if survivors else 1)"
- **Verified:** no

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-20 | sdlc-studio | Created via `new` (deterministic) |
