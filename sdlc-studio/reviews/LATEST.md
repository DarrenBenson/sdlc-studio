<!-- close-status:begin -->
> **RUN-01M7EYR3 closed running.** 16 unit(s) in the batch. **The run signature is OWED and is the operator's** - `sprint sign` seals the batch in one signature.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

Signed on 2026-11-15 over RPT0031 (fingerprint 41f6af509193a323), sealed goal-reached. The
operator, away on a ten-hour flight, authorised the orchestrator to sign every run it closes
meanwhile and to open the next (D0479, widening D0475); the orchestrator entered `sprint sign
--principal "Darren Benson"` on that authorisation.

> **RUN-01M7E52T, run twelve.** Goal: "A head of engineering takes a release to the change board
> on the run's own evidence, every cost row forecast." 25 units, 58 points (52 planned, 6 added
> in-run: D0478, D0480, D0481), all delivered on independent APPROVEs, five after one repair
> round and US1156 after a carry answered in-run (BG1439). Machinery share by theme 6 points
> (about 10%), by path about 33 (about 57%). Cost 48.9M priced tokens, 843k per point, $131.75
> ($2.27 per point) against run eleven's 845k and $2.28.

## What landed

- **Evidence**: one command builds a release's change evidence pack from committed records,
  naming each change's accountable person and refusing an agent (US1155, US1156, BG1439,
  BG1442, BG1441); a versioned evidence annex documents every committed record a consumer
  parses, with a recomputable fingerprint and a version stamp on each page (EP0275); a declared
  component map gives each story a risk class, the plan flags a mismatch and a high-class unit
  takes a second review seat whose yield the retro reports (EP0307).
- **Cost**: the plan forecasts priced, dollar and wall-clock cost and the report shows forecast,
  actual and ratio for every cost row, or why not (US1150, US1151); a multi-unit lane's builder
  total is split by points so every unit is priced (BG1397); a delegated total records its model
  (US0999); BG1391, BG1393 and BG1394 close three cost-honesty gaps.
- **Release blocker cleared**: BG1420 (High) is Fixed on its rejecting seat's round-3 APPROVE
  after BG1425 bounded the signal relay's wait, so `known_issues.py bar` no longer holds the tag.
- **Also**: retitle works in an installed skill (BG1019); `lessons.py class-add` (BG1268).

## What is owed

- **Carried, not stop-ship** (RETRO0145): BG1428-BG1436, BG1438, BG1440, BG1443, BG1444,
  BG1446 from the reviews, and BG1447-BG1454 with CR0705 from the run's tooling frictions.
  CR0703 (the dollar forecast runs about 49% high for Opus) and CR0704 (CR0692's part 2: group
  the pack by risk class) are open requests, carried unruled.
- **Pushed**: pending - the push gate's full suite runs next.
- **Run thirteen**: groomed and Ready (EP0287's slice and EP0309, 49 points), opening now under
  D0479.

## Learned the hard way

- A unit that adds a script, a verb or a long reference page needs its registry files in
  Affects (surface page, mechanics-verb list, catalogue heading, root census, reading guide, line
  ceiling); five lands were refused for one of them after a full hook run (CR0705).
- A lane's per-commit selection can miss a guard: main went red twice on tests no lane ran
  (BG1442, BG1437, BG1445). Run the full suite after each wave and before the close.
- A rebase conflict found after `lane land`'s hook run costs the whole run (BG1449): rebase a
  waiting lane over a landed one on the same files before handing back.
