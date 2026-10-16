<!-- close-status:begin -->
> **RUN-01M4R168 closed running.** 18 unit(s) in the batch. **The run signature is OWED and is the operator's** - `sprint sign` seals the batch in one signature.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M4R168, the first 6.2 run.** Goal: "Maya's ledger and signed runs keep what was
> decided, and her gates say up front what they need and cost." 18 units, each independently
> approved at its band's depth; one QA seat per unit, re-checked by the reviewer who rejected.
> Every push was judged on devserver1 by the full push gate first (D0366, expiring with this
> run); main is green.

## What landed

- **The ledger keeps authorised rounds.** `critic.py record --ruling DNNNN` takes a review round
  past the cap that an accepted decision names the unit for (BG1003, BG1044). BG0993's rounds 3
  and 4 are recorded under D0352 and D0353 and BG0993 is Fixed (D0354); US1004's full-depth
  round ran under D0368.
- **Signed runs stay sealed.** Sign leaves a carried unit where it stood (BG1025), with its pins
  and claims tested (BG0944, BG0945); verdict contracts round-trip (BG0950, BG1032).
- **Gates say up front what they need and cost.** `tools/gate_prereqs.py check` names each
  missing prerequisite and its install route (US1003); CI and the checker read one list,
  `requirements-dev.txt`, held to exact pip forms (US1004, BG1053, BG1056); the push refuses in
  seconds when the suite cannot be green (US1005) and states no fixed first-run figure (US1006,
  BG1045).
- **Hooks and tests:** the keepalive check (BG0976), the stub interpreter (BG0978), the
  module-alone lane test (BG1031), and a fixture that aged into staleness and turned main red on
  2026-10-14 (BG1047).

## What is owed

- **The run's signature:** `sprint.py sign --report <the close's page> --principal <operator>`.
  The author cannot sign.
- **The lessons log (BG0989, BG1060).** The full log (441 lessons) is still studypc's
  gitignored `sdlc-studio/.local/lessons.md`. The close ran without it on the operator's ruling of
  2026-10-16 to carry the gap: its extract started a short `sdlc-studio/retros/LESSONS.md` holding
  RETRO0134's lessons, and the digest was left as it stood (a known issue on the report). On
  studypc: move `.local/lessons.md` over that file, re-run `retro.py extract --id RETRO0134`
  (idempotent, it re-adds the three), then `lessons.py summary`, and commit.
- **The unified review** (`/sdlc-studio review`) is cadence debt: 196 artefacts changed since
  the last; the close reports it, not blocks on it.
- **Known issues carried, all not-stop-ship** (RETRO0134): BG1030, BG1033-BG1043, BG1046,
  BG1048-BG1052, BG1054, BG1055, BG1057-BG1060 and CR0638-CR0641. The Mediums are BG1050 (a
  control character in a reviewer id tears its row), BG1051 (the close's report clips refusal
  lines), BG1052 (a band rise after review is found only at the close), BG1054 (corpus-verify
  lacks pytest-xdist), BG1058 (the dry run names an answered unit), BG1059 (a retro's Batch field
  is never checked against the run) and BG1060 (extract starts a log the digest outlives).
- **Next run (D0365):** CR0635's remote gate (EP0288, US1075-US1078), which retires D0366's
  interim host script, then EP0274's token meters.

## Learned the hard way

- A test that enumerates a tool's spellings never converges; four rounds each found one more
  pip form. Hold the input to exact allowed forms instead, and claim only those (BG1056).
- `git stash create` snapshots the working tree, not the index. Build a judged commit with
  `git commit-tree "$(git write-tree)" -p HEAD`.
- A retro committed before its close leaves a velocity gap that turns the push suite red
  (BG1055); commit it with the close.
- A retro scaffolded before a `batch add` silently omits the late units from the close's
  measurement; read its Batch line against the run state before closing (BG1059).

## History

- RUN-01M45FV6 (RPT0019, signed 2026-10-05): sign seals only a page that still checks
  (BG0940); config show reads every shipped default (BG0943). Triage since then is in its retro
  and the decisions log (D0345-D0350).
