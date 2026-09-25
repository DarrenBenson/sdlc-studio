# BG0754: A commit touching a widely imported script runs well over the 90-second budget

> **Status:** Open
> **Measured at close:** RUN-01M39MC0 close (2026-09-24, load 0.7): a one-line gate.py change committed through both hooks in a clone of 016f29c7 took 93s against the 90s budget (229s at sprint start); its unit suites took 43s over 14 modules, and the rest is the pre-commit lanes, still sequential because US0891 was carried (BG0759). AC1 misses by 3s and AC2 is unmet while US0891 is open, so this stays Open until BG0759 lands
> **Severity:** Medium
> **Points:** 1
> **Affects:** .githooks/pre-commit
> **Evidence:** US0880 hand-back and commit 315ec358 (247s), RUN-01M3891F
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0880 reports the commit's time against 90s and never refuses. A change to gate.py or sprint.py selects the modules that import it, and `test_sprint.py` alone takes about 50s, so such a commit took 218-390s under load (US0880's own: 247s).

This is a measurement, not a delivery unit. Five of its six causes are removed: US0890, US0892, US0893, US0894 and US0895 are Done at 65cdf1ca. The sixth is US0891, carried as BG0759. Code lands through BG0759 alone, which is why `Affects` names only the hook it changes. BG0754 closes on the measure below once BG0759 lands. Do not put it in a `sprint plan` batch: its criteria are manual by design, since a wall-clock assertion on a shared machine is not a stable test.

## Steps to Reproduce

1. Change `gate.py`. 2. Commit. 3. The hook prints `over budget ... reported, not refused`.

## Proposed Fix

Remove the measured causes rather than split `test_sprint.py` (a split saves at most 5s and repoints 148 Verify selectors): cache the decisions scan (US0890), run the pre-commit lanes concurrently (US0891), hand xdist one test at a time (US0892), keep boundary-only tests out of the commit run (US0893), walk the corpus once in `close_owed` (US0894), and take the eight advisory gate lanes off the per-commit path (US0895).

## Acceptance Criteria

- [ ] **AC1** Given BG0759 landed on main, a quiet machine (load under 1) and a throwaway clone with `npm ci` run and the hooks enabled, when a one-line change to `gate.py` is committed through both hooks, then the commit-msg hook's `this commit took Ns` line reads 90 or less; the same figure is the last `total.selected` entry in the clone's `sdlc-studio/.local/gate-timings.json`. It read 93s at the Sprint 3 close and 229s at Sprint 3's start.
  - **Verify:** manual - `d=$(mktemp -d) && git clone -q . "$d/c" && cd "$d/c" && npm ci --silent && bash tools/enable-hooks.sh && echo '# budget probe' >> .claude/skills/sdlc-studio/scripts/gate.py && git commit -am 'chore(BG0754): probe the commit budget' 2>&1 | grep -E 'this commit took' ; python3 -c "import json; print(json.load(open('sdlc-studio/.local/gate-timings.json'))['total.selected'][-1])"`, run after BG0759 lands; record the figure and the load average in `Measured at close`
- [ ] **AC2** Given the six measured causes, then US0890 and US0892-US0895 are Done (true at 65cdf1ca) and US0891 is delivered through BG0759, with `test_sprint.py` not split.
  - **Verify:** manual - `grep -m1 'Status' sdlc-studio/stories/US089[0-5]-*.md sdlc-studio/bugs/BG0759-*.md` reads Done for the five stories and Fixed for BG0759

## Impact

US0880 reports the commit's time against 90s and never refuses.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Proposed fix reworded at Sprint 3 planning from measurement: the previous fix was refuted or would add a hand-kept pin (LC-008) |
| 2026-09-25 | QA seat | Groomed for Sprint 4: still open (93s at the Sprint 3 close; US0891 is still In Progress, its work carried as BG0759); criteria kept manual, with the exact measuring command; not a batch unit, since it closes on the measure once BG0759 lands; Affects narrowed to the hook BG0759 changes; 5 points resized to 1 |
