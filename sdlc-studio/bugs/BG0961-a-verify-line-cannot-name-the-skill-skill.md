# BG0961: A Verify line cannot name the skill: <skill> is a shell redirect, not a path

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/reference-verify.md, changelog.d/BG0961.md
> **Evidence:** Field report, 2026-10-07, grooming Sprint 0 stories on sdlc-studio-lens. validate.py instructions forbids a tool-specific skill path in committed instructions (BG0853). A story Verify line that has to run a skill script has nowhere legal to point. Reproduced at HEAD: verify_ac.run_verifier('shell test -f <skill>/scripts/verify_ac.py') returns ok=False, stderr '/bin/sh: line 1: skill: No such file or directory'.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** Grok 4.7; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T08:41:35Z

## Summary

BG0853 made the skill placeholder the only path a committed AGENTS.md may use, and said not to bake one machine's install path into a shared file. verify_ac never expands that placeholder. A Verify line is also committed and shared, and it is executed by the shell. In the shell the placeholder is input redirection, so a check of the form "test -f <skill>/scripts/verify_ac.py" fails looking for a file named skill. A consuming project's check that is itself a skill command (validate.py instructions, engagement_floor.py check) has to probe ~/.claude and ~/.agents inside the verifier instead.

## Steps to Reproduce

1. From a project root, run verify_ac on the expression: shell test -f, then the skill placeholder, then /scripts/verify_ac.py. 2. The result is ok=False, exit 1, stderr "skill: No such file or directory". 3. The file does exist under the skill directory this process loaded.

## Proposed Fix

Before a shell verifier is executed, replace the skill placeholder with the skill directory this process loaded (loaded_skill_dir). Do not write that absolute path back into the story. A Verify line keeps the placeholder, and the shell never sees the angle brackets.

## Acceptance Criteria

- [ ] **AC1** A shell verifier that checks the skill's verify_ac.py via the skill placeholder passes when verify_ac runs it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::HardeningTests::test_run_verifier_shell_pass_and_fail_resolves_the_skill_placeholder
- [ ] **AC2** After `verify_ac.py run` stamps such a criterion Verified, its Verify line still reads the placeholder; no absolute install path is written into the artefact
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::HardeningTests::test_the_placeholder_is_never_written_back
- [ ] **AC3** A skill directory whose path holds a space is substituted quoted, so the shell sees one argument; a check that should fail still fails
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::HardeningTests::test_a_skill_path_with_a_space_is_quoted

## Triage

- Reproduced at fb1ce886: `run_verifier('shell test -f <skill>/scripts/verify_ac.py', 30, '.')` returns ok=False, exit 1, stderr "skill: No such file or directory". `sdlc_md.loaded_skill_dir()` already exists to substitute. Never expanded; not a regression.
- `reference-verify.md` should name the placeholder as the portable way for a Verify line to reach a skill script, so a consuming project stops probing install directories.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | Grok 4.7 | Filed |
| 2026-10-07 | Claude Opus 5.5 (triage) | Groomed: reproduced at fb1ce886 (`run_verifier` exits 1 with 'skill: No such file or directory'); criteria added for write-back and quoting; reference-verify.md and a changelog fragment added to Affects |
