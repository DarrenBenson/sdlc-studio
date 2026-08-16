<!-- section: Changed -->
- **The skill suite runs in parallel, in two phases, and the split is guarded (BG0579).**
  Measured on 16 cores: the skill suite falls 597s to 220s and the full run 951s to 460s, twice,
  at an identical 6,560 passed. Everything runs across all cores, then the `serial_only`
  partition runs alone.
  Exactly ONE test cannot run beside others, and it is neither flaky nor slow: it snapshots
  `git status` across the whole repository, so any concurrent worker doing legitimate work makes
  it wrong. Three parallel runs each failed that same test and nothing else, and it passes alone
  in both modes - so the unsafe set is measured and named rather than assumed. It is MARKED, not
  deselected: the two phases partition the suite, so a test that gains or loses the marker still
  runs.
  The first verdict the split wrote said `GREEN (1 passed)` for a run of 6,556 - the runner took
  the last `N passed` line, which after the split was the serial phase alone. That number feeds
  the suite-claim lane, so it would have read as a green over a false claim in the understating
  direction. The count is summed now, and a test mutates it back.
  `pytest-xdist` is an optimisation and never a dependency: without it the runner falls back to
  one serial pass, so CI and a fresh clone are unaffected.
