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
- Second round, 2026-10-07, after the operator asked every project to file what it hits:
  ten bugs and a CR from other sessions (BG0965-BG0967, BG0969, BG0971, BG0973, BG0975,
  BG0977, BG0981, BG0982, CR-0614) and nine bugs and two CRs from this session's own frictions
  (BG0964, BG0968, BG0970, BG0972, BG0974, BG0976, BG0978-BG0980, CR-0612, CR-0613). All
  reproduce at 8b844a80, none is a regression, all are groomed; about 28 points of bugs,
  scheduled in D0349. BG0981 and BG0982 needed criteria written; BG0967 and BG0974 are the two
  halves of one markdown-safing fix.
- Next skill sprint (D0350, superseding D0349), after the website run: every open bug
  BG0944-BG0988 (43) with EP0274, and CR-0612 to CR-0617 once refined. BG0962's code is
  shipped but the bug stays Open for a fresh review (two REJECTs at the cap). US0986
  builds before the rest of EP0274; BG0949 and BG0952 share `unresolved_questions`, and
  BG0967 and BG0974 one safing pass.
- BG0989 (High) is Fixed and on main (978083c6): the lessons log is committed at
  `sdlc-studio/retros/LESSONS.md`, and `lessons summary` refuses to regenerate the digest from a
  log missing lessons it lists. This repository's own log is still on another machine, so a
  close here is refused at the lessons step rather than wiping the summary: copy that log back
  (to `retros/LESSONS.md`, or to `.local/lessons.md` and run any `lessons` command), commit it,
  then close. BG0992 (Low) holds the round-2 review's non-blocking findings.
- BG0994 (High) fixed main's red noise gate, which BG0989's migration line had tripped from
  seven legacy-path fixtures; approved, pushing alone (e77cd2d5).
- BG0993 (High, D0351 fast-track): whether a sprint run is open lived in each machine's
  `.local`, so another machine could plan a parallel run and could not sign the first. The close
  now commits the run's record awaiting its signature, `plan --write` refuses while one awaits,
  `sign` works from any clone, and a copy older than its record takes it up instead of writing
  over it. QA approved it at round 4 (D0352 and D0353 authorised rounds past the cap); it stays
  Open under D0354 because the ledger cannot record those rounds (BG1003). Its lows are BG1004
  (a versioned record) and BG1001. Four rounds: I patched a cross-checkout race one ordering at a
  time with a reopen-count proxy, and broke the full-suite rule once (BG1000 is the hook gap).
- Third round, 2026-10-08, filed by other sessions: BG0995-BG0999 reproduce at current code,
  none a regression; CR-0618 and CR-0619 (CR-0619 to refine with BG0950), and CR-0620 to
  CR-0623 from the homelab retrospective on review seats and persona goals (CR-0620 with
  CR-0622; CR-0621 and CR-0623 with BG0966). Not yet scheduled.
- From three consuming projects' assessments of the skill, relayed by the operator: CR-0624
  (gate `revert-check` at the terminal transition), CR-0625 (`validate seats` checks a card
  against the cast) and CR-0626 (a proportional path for a small change), with new evidence
  and criteria on CR-0619, CR-0620 and CR-0621.
