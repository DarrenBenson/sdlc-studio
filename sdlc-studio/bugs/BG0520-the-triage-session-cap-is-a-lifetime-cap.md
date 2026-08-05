# BG0520: the triage session cap is a LIFETIME cap: the session key defaults to a constant, so the counter never resets and filing eventually refuses for good

> **Status:** Fixed
> **Verification depth:** functional
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/triage_noise.py, .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py
> **Evidence:** Hit live during RUN-01KZ79C1 on 2026-08-04 while filing BG0519, the recorded narrowing of BG0513. Two findings had been filed in this session; the counter stood at 20 from earlier sessions sharing the 'default' key. Worked around by exporting SDLC_TRIAGE_SESSION=RUN-01KZ79C1, which is the documented third exit and the only one that works.
> **Created:** 2026-08-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`triage.session_cap` is documented as a per-session budget: one session may file at most N findings. But `_session_key()` returns `os.environ.get("SDLC_TRIAGE_SESSION", "default")`, and nothing in the skill ever sets that variable - not the sprint, not the run, not any entry point. So every session in a project's whole life shares the key `default`, `session_count` keeps matching, and the counter monotonically climbs to the cap and stays there.

At that point `file_finding` and `artifact.py new` refuse EVERY finding, permanently, on a project that has done nothing wrong. Observed on this repo at exactly 20 with the state file reading `{"session": "default", "count": 20}`, mid-run, while filing the residue of a unit whose own criteria required the residue to be filed. The refusal is loud and well-worded, which is the only reason it was not mistaken for something else.

The refusal names three exits - triage the backlog, raise the cap, or set the environment variable - and only the third actually works, because the count is not reduced by triaging and raising the cap only moves the wall. That makes the message's first suggestion misleading at the moment it is read.

## Steps to Reproduce

1. On a schema v3 project, file findings until the count reaches `triage.session_cap`.
2. Start a genuinely new session - new process, new day, new agent invocation. Do not set `SDLC_TRIAGE_SESSION.`
3. `file_finding.py file --type bug ...` - refused with 'triage session cap reached (20 findings filed this session)'.
4. `cat sdlc-studio/.local/triage-session.json` - `{"session": "default", "count": 20}`. The count survived the session boundary because the key did not move.

## Proposed Fix

Give the session key a value that actually changes when a session does. The open run is the natural candidate and is already recorded: keying on the run id makes the cap per-run, which is the semantics the docstring describes and the unit an operator reasons about. Outside a run, a date-stamped key would at least bound it to a day rather than to a project's lifetime. Whichever is chosen, `session_count` must return 0 across a real session boundary without the operator being told to export anything - a budget you have to know a magic variable to reset is one that fires as a wall.

Also correct the refusal message: do not offer 'triage the backlog' as an exit when triaging does not decrement the counter.

## Acceptance Criteria

- [x] **The counter reads zero across a real session boundary with nothing exported.** File to the cap under one run, open the next, and `session_count` is 0 - the key moved because the run did. *Mutant:* keep the `default` fallback - the count survives the boundary, which is the whole defect. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py::SessionKeyTests::test_the_count_resets_across_a_run_boundary
- [x] **Within one run the cap still fires.** *Mutant:* key on something unique per call - the cap never fires and the noise control is gone while the reset criterion still passes. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py::SessionKeyTests::test_the_cap_still_fires_within_one_run
- [x] **Outside a run the key is bounded to a day, not to the project's lifetime.** There is NO fallback to a constant: a constant is what made a per-session budget a lifetime one. *Mutant:* restore it for the no-run case - the wall returns by the back door for exactly the sessions that file most. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py::SessionKeyTests::test_no_open_run_keys_on_the_date
- [x] **The explicit environment override still wins where it is set**, over an open run, because it is the documented exit and consuming projects may rely on it. *Mutant:* consult the run first - an operator who named a session is silently given the run's. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py::SessionKeyTests::test_an_explicit_session_variable_still_wins
- [x] **The refusal message no longer offers an exit that does not work.** It names the key in force, so the reader can see what has to move; it drops "triage the backlog", which decrements nothing and was false at the moment it was read; and it says plainly that raising the cap moves the wall rather than removing it. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py::SessionKeyTests::test_the_refusal_names_only_exits_that_work
- [x] **The writer and the reader resolve the SAME key.** Found while fixing this: a counter stamped under one key and read under another never matches, so the cap never fires - the opposite failure, and just as silent. *Mutant:* drop `root` from the writer's call - it stamps the date key while the reader resolves the run id, and the count reads 0 forever. *Verify:* pytest .claude/skills/sdlc-studio/scripts/tests/test_triage_noise.py::SessionKeyTests::test_the_writer_and_the_reader_resolve_the_same_key

## Impact

Every project that adopts schema v3 eventually stops being able to file findings, and the failure mode arrives silently over time rather than at adoption. It bites hardest exactly where it does most damage: mid-run, when a unit's own criteria require its residue to be filed, the tooling refuses to record it. The pressure it creates is to stop filing findings, which is the opposite of what the cap exists to encourage.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Filed |
