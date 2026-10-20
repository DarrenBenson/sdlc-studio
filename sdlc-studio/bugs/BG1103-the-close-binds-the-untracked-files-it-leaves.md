# BG1103: The close binds the untracked files it leaves into the signature without naming them, so tidying one refuses the sign

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_close_names_bound_untracked.py, changelog.d/BG1103.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M59TRM, 2026-10-20: the close at a00ee476 recorded close_tree 099f3de3 with sdlc-studio/retros/LESSONS.md untracked. After it was deleted on the operator's ruling, sprint.tree_moved_since_close returned ['sdlc-studio/retros/LESSONS.md']. It was restored with `git show 099f3de3:sdlc-studio/retros/LESSONS.md`, and the sign then sealed the run.
> **Created:** 2026-10-20
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-20T15:39:20Z

## Summary

sprint close records its tree with `git add -A`, so an untracked file present at the close is part of the tree the signature is bound to. The close does not say so. RUN-01M59TRM's close left the extract's short sdlc-studio/retros/LESSONS.md untracked and said not to commit it (D0371). Deleting it before the signature made `sprint sign` refuse, because the file had changed since the close. Recording an operator ruling in decisions.md between the close and the signature refuses the same way. The refusal is loud and names the file. What is missing is any warning at the close.

## Steps to Reproduce

Close a run whose tree holds an untracked file, delete that file, then run `sprint.py sign --report <its page> --principal <operator>`: it refuses, naming the file as changed since the close. The close's output never named it as bound.

## Proposed Fix

When the recorded tree holds untracked files, the close names each one and says the signature binds it. The close's awaits-signature line says the tree must stay unchanged until the run is signed.

## Acceptance Criteria

- [ ] **AC1** A close over a tree holding an untracked file names that file as bound into the signature, and a close over a tree with none names no file
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_names_bound_untracked.py

## Impact

A ruling or a clean-up made between the close and the signature breaks the seal. It is caught only at the sign, or, as here, by an author who checks the tree by hand first.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-20 | Claude Opus 5.5 | Filed |
