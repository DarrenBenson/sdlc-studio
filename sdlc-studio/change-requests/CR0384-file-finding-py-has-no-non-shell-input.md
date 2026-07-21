# CR-0384: file_finding.py has no non-shell input path, so the field most likely to contain commands is the one most likely to be executed

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py,.claude/skills/sdlc-studio/scripts/artifact.py
> **Date:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Every field of a filed finding is passed as a shell argument, and the fields that matter most - Steps to Reproduce and Proposed Fix - are precisely the ones whose content is COMMANDS. An agent writing a faithful reproduction naturally includes backticked shell in it, and inside a double-quoted shell argument a backtick is command substitution. The prose is therefore executed rather than stored. There is no non-shell input path: no --steps-file, no --json, no stdin.

## Impact

Every agent filing a finding, which is the intended primary caller. This is not hypothetical and it is not rare: it happened TWICE in a single sprint while filing this sprint's own follow-ups. BG0240 was filed with two reproduction commands silently deleted from its Steps section, leaving an artefact that reads complete and is not - the worse of the two outcomes, because nothing signalled it. BG0242, whose subject is git environment safety, contained the literal text `git commit -a` in its steps; filing it EXECUTED git commit -a twice against the live repository. Both were blocked by the pre-commit gate and nothing was committed, so the damage was zero - but the damage was zero because a different guard happened to be red, not because filing is safe. The same call in a repo with a green gate would have committed a half-finished working tree mid-sprint. Note the sharp edge: the reproduction steps for a bug about destructive commands are the most dangerous possible payload, and that is exactly the bug someone is most likely to file.

## Acceptance Criteria

- [ ] A finding can be filed with no field passing through a shell: a --fields-file taking JSON, or reading a JSON document on stdin
- [ ] The documented and recommended path for an agent is the non-shell one, in reference-scripts.md and in the tool's own help
- [ ] A field arriving with an unbalanced backtick, a $( or a trailing backslash is reported rather than stored silently, so a mangled filing is visible at file time instead of being discovered when somebody reads the artefact
- [ ] A test files a finding whose Steps section contains backticks, a $(...) form and the literal text of a destructive git command, then reads the artefact back and asserts the stored text is character-for-character what was supplied
- [ ] The same test asserts no side effect occurred: the repository index and HEAD are unchanged after the filing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Raised |
