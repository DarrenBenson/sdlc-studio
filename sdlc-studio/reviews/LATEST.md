<!-- close-status:begin -->
> **RUN-01M45FV6 closed goal-reached.** 2 unit(s) in the batch. **The run is SIGNED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M45FV6, the 6.2 groundwork sprint.** Goal: "Maya signs only a report that still
> checks VALID, and config show reads every shipped default." The skill's whole open backlog
> (D0341), landing on main unreleased (D0342). The goal review re-groomed both units before the
> run opened (D0344); one QA reviewer per unit.

## What landed

- **Sign seals only a page that still checks (BG0940).** A ruling logged between the close and
  the sign is written to the decisions log but no longer counted into the closed run, so the
  filed page stays VALID; `sprint sign` re-derives the page with the report check's own reading
  before it writes the seal and refuses one that moved, naming the figure. AGENTS.md's refusal
  table names the new check.
- **Config show reads every shipped default (BG0943).** A project section holding only
  comments no longer replaces the defaults' section when merged, so `config.py show` and
  `config.get` see every declared key. The cause differed from the bug's first diagnosis; the
  build found it by executing the premise.

## What is owed

- **Filed 2026-10-07, triaged the same day:** from planning Sprint 0 on sdlc-studio-lens,
  BG0959 (Medium, the engagement floor's `adopt_after` rejects a ULID cutoff), BG0960 (Low, a
  missing-verifier refusal tells you to add Affects and Points), BG0961 (Medium, `<skill>` in a
  Verify line is a shell redirect); from closing a consuming project's run, BG0962 (High,
  closing-review reads verdicts only from the frozen batch ledger, so a frozen REJECT blocks a
  run whose units are all approved). All four reproduce at fb1ce886, none is a regression, and
  all are groomed.
  BG0962 is fast-tracked as a single unit now; the other three join the next sprint (D0348).
- **BG0944** (Low): three behaviours the run shipped have no test that fails when they break.
- **BG0945** (Low): BG0940's changelog entry over-claims what sign does after a late ruling.
- Both filed under D0338 for the next sprint; v6.2.0 is cut when more has accumulated (D0342).
- The website run (D0341) follows this one: BG-01M4254Y and BG-01M425QW in sdlc-studio-web.

## Triaged since the close (D0345)

- Nine bugs filed from the lens gap analysis, a consuming project's 6.1 migration and homelab
  (BG0946-BG0954). Eight reproduce against HEAD and are groomed; none is a regression.
  BG0951 closed Won't Fix (a model-size tier read as review depth).
- BG0955 fixed: the row archive (2c72fe8e) had turned main red through a test reading only
  the live index. The same archive broke `test_epic_index_derived` (BG0957, masked on CI) and
  left archived rows no writer reaches (BG0956). BG0958: `mutation.py` misreads diffs under
  `diff.mnemonicPrefix`.
- CR-0611 (harness token meters) filed and refined into EP0274, 26 points (D0346).
- Next skill sprint (D0348, superseding D0347), after the website run: the sixteen open
  bugs and EP0274, about 56 points, every unit groomed. US0986 builds before the rest of
  EP0274; BG0949 and BG0952 share `unresolved_questions`, so one wave.
