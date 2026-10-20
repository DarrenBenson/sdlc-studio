<!-- close-status:begin -->
> **RUN-01M59TRM closed partial.** 10 unit(s) in the batch. **The run is SIGNED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M59TRM, the second 6.2 run.** Goal: "Rowan's push is judged on a configured gate host,
> and the gate's documents and weekly run tell the truth." Eleven units planned (31 points),
> one QA seat per unit. Nine reached Done or Fixed, and BG1099 was added and fixed. Two hit the
> review cap and are carried. First-review approval was 1 of 10, against 9 of 19 the run before
> (RETRO0135, CR0650). Every push was judged on devserver1 through the hook itself.
> Signed on 2026-10-20 over RPT0021 by the operator; the agent entered the command at the
> operator's instruction ("I sign it off").

## What landed

- **The push is judged on a gate host.** With `sdlc.gateHost` set, the pre-push hook sends
  exactly the commit pushed to a repository kept on the host for this clone, and judges it there
  (US1075). Runs on one host are serialised behind a lock, and an abandoned push stops its run
  (US1076, carried). `remote-gate.sh doctor` says whether a host can judge a push (US1077).
  `tools/run-suite.sh` runs on the host against the working tree, and `--check` reads its verdict
  (US1078). Each was proven live on devserver1: a push judged in about ten minutes, and
  `run-suite.sh all` green with 8157 passed.
- **The documents tell the truth about the gate.** The TRD and TSD name the three hooks, the
  boundaries, the manual pre-tag steps, the gate's `.local` writes, its declared budget (US1084),
  every dependency, CI job and lint check (US1085), and the gate host (US1086, carried).
- **The weekly run reads true.** corpus-verify installs pytest-xdist and pdftotext, US0985 AC2
  reads the cut's record, and the per-verifier ceiling is set from a measured runner figure
  (BG1054). US1084's rewording that broke US0253 AC3 is fixed (BG1099).
- **The committed lessons log passes MD026** (BG1061). A second Primary, Rowan Achterberg, owns
  the repository-tooling interface (US1079), and the product seat judges by interface (BG1066).

## What is owed

- **Two units carried at the review cap,** going into run three (D0381): US1076 as BG1078 (its fix
  is on main; its test repair was the unconverged part) and US1086 as BG1095 (its documents are
  accurate; its fall-back test reads a fixed phrase list).
- **The lessons log (D0371).** It is still on studypc, which was off at this close, so the close
  refuses at its lessons step. Copy studypc's `sdlc-studio/.local/lessons.md` into this clone's
  `sdlc-studio/.local/` (not to the committed path), so the migration normalises its headings
  (BG1061), then `lessons.py summary`.
- **Known issues carried, all not-stop-ship** (RETRO0135): BG1070-BG1076, BG1078-BG1098,
  BG1100-BG1102 and CR0650. The Mediums are BG1078 and BG1095 (the carried units), BG1087 (mutation scoping under a
  user's diff.mnemonicprefix), and BG1101 (a probe-fixture race that refused one push).
- **Next run (D0381, superseding D0378):** CR0650 first (the author's self-check as a gate),
  then BG1078 and BG1095, then BG0962, BG1000, CR0645-CR0649 and US1080-US1083. The operator
  approves the plan before delivery starts, and 6.2.0 is tagged once that run is signed.

## Learned the hard way

- A test of prose by phrase list never converges. Every round a reviewer found a paraphrase it
  missed (US1084, US1085, US1086). Judge structured content (a table cell's set, read from the
  source) instead.
- A rule nobody's command enforces gets broken under time pressure, even by the agent who wrote
  it down: the full suite skipped before a push, a regression filed as a flake (BG1077). Gate it
  (CR0650, LL0027).
