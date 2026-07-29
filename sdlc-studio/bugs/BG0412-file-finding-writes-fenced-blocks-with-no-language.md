# BG0412: file_finding writes fenced blocks with no language, so the deterministic filer produces artefacts the commit gate refuses

> **Status:** Fixed
> **Verification depth:** functional (tests red-first; each repair verified by applying its own mutant and watching it redden, bytecode purged, python3 -B)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Evidence:** Filing BG0408 and BG0411 from a `--fields-file` document: the filer exited 0, and the very next commit was blocked by MD040/fenced-code-language on lines 18 of both files.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** close friction, RUN-01KYNKDP; human; v1

## Summary

`file_finding.py` is the deterministic path - the whole point is that an agent does not hand-author an artefact and does not hand-author its index row. It exits 0 and reports `filed BG0408 -> ...`. The commit that follows is then refused by the markdown lane, on the file the filer just wrote.

A fenced block in a finding's `summary` or `steps` is copied through verbatim, so an opening fence of three bare backticks reaches the artefact and MD040 refuses it. The author's options are all bad: hand-edit the artefact the deterministic filer just wrote (which is the practice this tool exists to end), pre-mangle the finding document to suit a lint rule it does not know about, or drop the evidence block - and the block is usually the measured output that makes the finding checkable.

The general shape: a generator and a validator in the same repo disagree about what is valid, and the generator is the one that reports success. Every filing that carries measured output pays a blocked commit and a manual repair.

## Steps to Reproduce

1. Write a `--fields-file` document whose `summary` contains a fenced block opened with three bare backticks (no language).
2. `file_finding.py file --type bug --fields-file FINDING.json` - exits 0, reports the id.
3. `git add -A && git commit` - the markdown lane fails with MD040/fenced-code-language against the filed artefact.

## Proposed Fix

The filer should emit markdown its own gate accepts. When it copies a fenced block through, give an unlabelled opening fence a default language (`text`) - it is the same normalisation `_prose_safe` already performs for metadata-line forgery, applied to a different mechanical hazard.

Do the normalisation in the shared writer rather than in `file_finding` alone, so every generator that renders author prose into an artefact inherits it.

The broader rule worth stating: a generator in this repo should be held to the guards its output must pass. Whatever the fix, a test should assert that an artefact the filer writes passes the markdown lane - otherwise the next rule the lane gains reopens this.

## Acceptance Criteria

- [ ] An artefact filed from a document containing an unlabelled fenced block passes the repo's markdown lane without hand-editing.
- [ ] The author's fence content is preserved verbatim; only the missing language is supplied.
- [ ] A closing fence is never given a language, and a block that already declares one is untouched.
- [ ] The normalisation lives in the shared artefact writer, so every generator rendering author prose inherits it.
- [ ] A test asserts that a filed artefact passes the markdown lane, so a new lint rule cannot silently reopen this.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | close friction, RUN-01KYNKDP | Filed |
