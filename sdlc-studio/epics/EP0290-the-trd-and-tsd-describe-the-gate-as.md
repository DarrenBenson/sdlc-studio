# EP0290: The TRD and TSD describe the gate as it runs: the hooks, the boundary gates, the toolchain, CI and the gate host

> **Status:** Draft
> **Derived Point Total:** 7
> **Parent:** CR0644
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0644. Delivers the work CR0644 requested.

## Story Breakdown

- [x] [US1084: The TRD and TSD name each hook, what it runs, where the full suite runs and what a tag push does not run, read from the hooks themselves](../stories/US1084-the-trd-and-tsd-name-each-hook-what.md)
- [ ] [US1085: The TRD's stack and the TSD's framework rows name every dependency the clone installs, and the TSD names each CI job and its trigger](../stories/US1085-the-trd-s-stack-and-the-tsd-s.md)
- [ ] [US1086: The TRD and TSD describe the gate host a clone can configure, the fallback and the local override](../stories/US1086-the-trd-and-tsd-describe-the-gate-host.md)

## Acceptance Criteria (Epic Level)

- [ ] The TRD and TSD describe the commit gate (pre-commit, then commit-msg running selected suites against an advisory 90-second budget), the push gate (prerequisites, the red-main acknowledgement, `--boundary push` with the full suite) and the tag gate (`--boundary release`), each pointing at the hook's own `--list` rather than restating its lanes
- [ ] The TRD's tech stack and the TSD's framework rows name pytest with xdist, coverage 7.10 or later, PyYAML, Node 20 with markdownlint-cli and bandit, citing requirements-dev.txt as the one dependency list and the 3.10 floor job
- [ ] The TSD has a scheduled stage naming the corpus and corpus-verify jobs and their baselines, and records `gate.py --release`, `release_cut.py record-green` and `tag-check` as manual pre-tag steps (D0375)
- [ ] Neither document says the gate writes nothing: both say it writes only gitignored `.local` run state, and the gate's cost row cites its measured budget rather than 'sub-second'
- [ ] The remote gate EP0288 ships is described in the same sections in the run that ships it

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | sdlc-studio | Created via `new` (deterministic) |
