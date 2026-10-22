# BG1114: critic.py brief spends 19 of its 20 seconds walking the artefact corpus, because it reads the files' history without the corpus cache that lane brief opens

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_corpus_cache.py, changelog.d/BG1114.md
> **Evidence:** CR0651 drafting, 2026-10-21: an in-process profile of critic.brief for US1087.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T05:42:17Z

## Summary

Measured in-process on 2026-10-21 (US1087's brief): `critic.brief` took 19.9 s, 19.0 s of it in `reconcile.file_history_section`, of which `unit_corpus` took 18.4 s. Without an open `sdlc_md.corpus_cache()`, every `find_by_id` and `artifact_files` call inside it walks and reads the whole tree, which is quadratic (`sdlc_md.corpus_cache`'s docstring measures one such sweep at 777,732 file opens). `sprint.py lane brief` holds the cache open; `critic.brief` does not, so every review brief, and every rejoinder, pays the walk.

US1089's QA review (2026-10-22) adds: the self-check gate runs after `brief()` has rendered the whole brief (critic.py:3757-3768), so an author refused for a missing record still pays the walk first. Running the gate before rendering would save that too.

## Steps to Reproduce

`time python3 .claude/skills/sdlc-studio/scripts/critic.py brief --unit US1087 --seat qa >/dev/null`: about 20-30 s on this workspace.

## Proposed Fix

Hold `sdlc_md.corpus_cache()` open for the read-only part of `critic.brief`, as lane brief does. The brief writes nothing, so the cache cannot serve it a stale view.

## Acceptance Criteria

- [ ] **AC1** When `critic.brief` reads the unit's file history, the corpus cache is open: with `reconcile.file_history_section` patched to record `sdlc_md.corpus_cache_active()`, a brief records True, and the cache is closed again once the brief returns
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_corpus_cache.py::CriticBriefCorpusCacheTests::test_the_brief_reads_history_inside_the_corpus_cache

## Impact

Each review brief costs about 20 s, and more on a loaded machine; a run with fifteen units and rejoinders pays it about thirty times.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
