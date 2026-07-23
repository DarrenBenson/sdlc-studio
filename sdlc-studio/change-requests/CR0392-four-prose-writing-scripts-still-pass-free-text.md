# CR-0392: Four prose-writing scripts still pass free text through a shell argument and lack the --fields-file path

> **Status:** In Progress
> **Decomposed-into:** EP0146
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/scripts/close_owed.py,.claude/skills/sdlc-studio/scripts/telemetry.py,.claude/skills/sdlc-studio/scripts/sprint.py
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

US0305 gave `file_finding.py` a --fields-file so prose reaches an artefact as data, and US0306 swept artifact.py alongside it. The sweep could not reach four further writers, because each belonged to a different lane in the same batch: critic.py (--note, --verdict), `close_owed.py` (--note), telemetry.py (--summary, --verdict) and sprint.py (--goal, --note). They are recorded in `KNOWN_PROSE_WRITER_GAPS` with reasons, and that registry is test-enforced in both directions - a stale entry fails when a writer gains the safe path, and a new writer added without it fails too - so the debt cannot expire quietly. It is still debt. The hazard is the one CR0384 was filed for and which this project has actually paid: a backtick in a shell-passed argument performs command substitution and silently empties the field, and it was a bug's Steps to Reproduce, the field most likely to contain shell commands, that was mangled. L-0154 on this project says a defect found in one writer must be swept across every sibling writer; four siblings remain unswept.

## Impact

Any agent or operator filing through these four commands with prose containing a backtick, a dollar-parenthesis, or a trailing backslash. The failure is silent and fails open: the field is emptied or altered, the command exits 0, and the artefact looks complete. mutation.py also trips the registry heuristic through its window open --note, but that writes a short label to transient .local state rather than an artefact body, so it is a different and much smaller exposure.

## Acceptance Criteria

- [ ] Each of critic.py, `close_owed.py`, telemetry.py and sprint.py accepts a --fields-file carrying every free-prose field as data, sharing the one helper `file_finding` already exposes rather than growing a second idiom.
- [ ] `KNOWN_PROSE_WRITER_GAPS` is empty of these four once they are converted, and its test still fails if a new prose writer is added without the path.
- [ ] The flag path survives for compatibility on each, and reports a detected shell hazard rather than silently altering a field.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
