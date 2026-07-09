# CR-0204: normalise the eleven test files with mid-file `__main__` guards (36 classes silently dropped on direct runs)

> **Status:** Proposed
> **Priority:** Medium
> **Type:** tooling
> **Date:** 2026-07-09
> **Created-by:** sdlc-studio file

## Summary

Eleven test files keep 36 TestCase classes after a mid-file `if __name__` guard: test_doc_freshness.py:97, test_lessons.py:658, test_artifact.py:590, test_gate.py:296, test_next_id.py:168, test_audit.py:421, test_github_sync.py:974, test_project_upgrade.py:410, test_verify_ac.py:947, test_validate.py:468, test_reconcile.py:1228. Measured (RV0007): test_validate.py direct run executes 49 of 71 tests and reports OK; test_doc_freshness 8 of 11. RETRO0016 recorded the append-truncation incident and the 'append at true EOF' lesson but no fix artefact was ever filed - the layout remains a standing tripwire for agents (rfind append truncation, already happened once) and humans (green direct runs that lie).

## Acceptance Criteria

- [ ] All `__main__` guards moved to true EOF in the eleven files; discover count unchanged (1455)
- [ ] Direct 'python3 <file>' run count equals the discover count for each file
- [ ] Optional: a tools/ check rejects non-terminal `if __name__` in test files

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | audit | Raised |
