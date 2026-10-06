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

- **BG0944** (Low): three behaviours the run shipped have no test that fails when they break.
- **BG0945** (Low): BG0940's changelog entry over-claims what sign does after a late ruling.
- Both filed under D0338 for the next sprint; v6.2.0 is cut when more has accumulated (D0342).
- The website run (D0341) follows this one: BG-01M4254Y and BG-01M425QW in sdlc-studio-web.

## Triaged since the close (D0345)

- Nine bugs filed from the lens gap analysis, a consuming project's 6.1 migration and homelab
  (BG0946-BG0954). Eight reproduce against HEAD and are groomed; none is a regression.
  BG0951 closed Won't Fix (a model-size tier read as review depth).
- Open skill backlog: ten bugs, 19 points, all passing `sprint.py breakdown`. BG0949 and
  BG0952 share `unresolved_questions` in sdlc_md.py, so one wave.
- Order unchanged: the website run first, then a skill sprint over the ten.
