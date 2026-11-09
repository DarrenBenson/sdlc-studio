<!-- close-status:begin -->
> **RUN-01M6RZQZ closed partial.** 17 unit(s) in the batch. **The run is SIGNED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M7061X, run nine and the first 6.4 run.** Goal: "Abena Osei becomes Primary, Copilot,
> Grok and Composer runs are priced, and waves resume from a short brief." Planned at 18 units and
> 53 points (D0446); delivered 17 units, 49 points (44 counting US0986 and BG1205 once), each on an
> independent QA APPROVE. A declared maintenance run (D0445): by theme 3 points machinery (6%); by
> path loop machinery 32 points (65%), cost metering 5 (10%), other 12 (24%).

## What landed

- **Human in the lead (RFC0063 WS1, CR0689).** Abena Osei, a head of engineering in an audited
  organisation, is the shipped skill's Primary with six End goals (US1146, D0436, D0443); Maya
  Okafor moves to Secondary and Jonah Reyes's card changes only in its cast lines. Graham Doyle
  joins as the Served change approver and Trevor Hale narrows (US1147, carried at the review cap as
  BG1318 and fixed in-run). The PRD leads with "Human in the lead" and gains O10-O13 (US1148).
- **Cost a team can read.** Grok and Composer are priced from xAI's and Cursor's own pages (US1143),
  a Copilot run per token in AI credits (US1144), and request billing only where a project keeps it
  (US1145). The meter reads the running harness's store (US0986 with BG1205).
- **A wave resumes from a short brief (CR0670's first slice).** `lib/resume_brief.py` derives the
  next action and a brief of at most 8k tokens from disk (US1140), `sprint.py handoff` and
  `sprint.py resume` use it (US1141), the brief places mid-run findings as the report does (BG1312),
  and reference-sprint.md defines the wave boundary (US1142).
- **6.3's carried units reached Done** on round-2 APPROVEs from the seats that rejected them:
  US0986, US1130 and US1133 (with BG1264). Lane fixes for schema-3 ids: BG1302, BG1303. BG1320
  fixed a test-import collision the run itself introduced.

## What is owed

- **Descoped to run ten:** US1134 (its quiet-hooks change reaches eight test modules beyond its
  Affects; re-grooming note on the story, D0453) and BG1300 (its tests need a temporary HOME, which
  the worktree guard refuses until the operator's permission rule is in place, D0454).
- **US1147** stays Ready with qa-seat-US1147-r1's round-2 REJECT unanswered; BG1318 fixed its
  defect, and it reaches Done when that seat approves a redelivery (D0433's pattern).
- **Known issues carried, all not-stop-ship** (RETRO0142): BG1309-BG1311, BG1313-BG1317, BG1319,
  BG1321-BG1327. Filed before the run opened: BG1304-BG1308.
- **Cost:** priced from the session meter at the close; the orchestrator ran in the long 6.3
  session, its largest share. Run ten should start in a fresh session from `sprint.py handoff`.

## Learned the hard way

- Groom a change to a shared surface with every test that pins it, and each unit's changelog
  fragment, in its Affects (US1134, US1141, thirteen fragments added mid-run).
- Fast-forward a lane's worktree to main before landing it, and run mutants with
  PYTHONDONTWRITEBYTECODE=1 (US1145 refused twice; BG1325).
