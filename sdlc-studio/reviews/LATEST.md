<!-- close-status:begin -->
> **RUN-01M3891F closed running.** 11 unit(s) in the batch. **Sign-off is OWED and is the operator's** - the two-role gate holds Done.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M3891F, Sprint 2 of back to basics: fast gates and lessons that graduate.** Goal:
> "Commits clear in about a minute, and the sprint learns from repeated mistakes without being
> told." 11 of 11 units delivered (42 points), each reviewed once by a fresh reviewer under the
> two-round cap. Verdict: partial.
>
> Closing review of record: RETRO0122.

## What landed

- **Lessons learn.** A lesson is a failure class in `sdlc-studio/lessons.jsonl` (LC-001 to
  LC-006, seeded from the review). Retro Try items and cited REJECTs count repeats once per run
  and unit; the classes reach the plan, the build brief and the critic brief; a class that
  repeats twice after it was recorded graduates to a CR, and one quiet for five runs retires. A
  project with no store reads the seed bundled with the skill (US0887, US0888, D0261).
- **Gates got cheaper.** Seven dead per-commit lanes are gone (US0879); a commit runs only the
  test modules its change reaches, in parallel (US0880); a push runs the full suite once, in
  about 284s against 607-881s, and CI runs it once (US0881). Switched-off mutation evidence no
  longer blocks, and re-registration no longer evicts other units' rows (US0882).
- **The report is honest about itself.** A hand-edited filed page reads INVALID (US0883), only
  the close files a report (US0884), and its time window no longer races its own paperwork
  (US0885). BG0744, BG0745 and BG0748 are Fixed; nothing Critical or High is open.
- **The close does its own housekeeping**: it forward-ports the skill and keeps one handover per
  run (US0889). Sprint 1's superseded criteria are retired (US0886).

## What is owed

- **A code commit is still over the minute.** One reaching a widely imported script took
  165-258s under this machine's load against the 90s budget, reported and not refused (BG0754).
- Per-commit selection follows direct edges only: hooks, test infrastructure and code reached
  through another script are caught at push, not at commit (BG0752).
- The test suite leaks temporary directories; /tmp ran out of inodes mid-run (BG0753).
- Two report-window races remain in waivers and open findings (BG0750, BG0751).
- CR0592 collects the Low findings, including six older criteria that still describe push
  behaviour US0881 moved to the release boundary.
