<!-- close-status:begin -->
> **RUN-01M7QMZ0 closed partial.** 8 unit(s) in the batch. **The run is SIGNED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

**RUN-01M7QMZ0, run seventeen, is SIGNED (2026-11-18).** It delivered CR0742
(harness-agnostic, enterprise-ready documentation) ahead of D0519's plan (D0529): EP0377's seven
stories and BG1599, 25 points, all on independent APPROVEs, for $54.60 ($2.18 per point) against a
$79.42 forecast. At the close the operator authorised an expired waiver of the goal's missed seat
review (D0533, cause filed as BG1601) and delegated this run's signature (D0535), and the
orchestrator signed over RPT0036 after a rehearsal in a throwaway clone. The website run
RUN-01M7R7KN, in the website's own repository, then delivered CR0742's change 5 and is signed
(2026-11-19, under that repository's delegation decision): the site's home page now says SDLC
Studio runs in the reader's own harness and models, and it is live on both web hosts.

> Goal: "A reviewer reading only the front door knows SDLC Studio runs in their own harness,
> models and change process." Judged **partial**: the repository's front door is done, but
> CR0742 names the website home page as the third surface, and it lives in the website's own
> repository, so it is delivered by a change request run there next.

## What landed

- **Harness compatibility page** (docs/harnesses.md, US1316): six harnesses by seven
  capabilities, each cell sourced or marked untested, each harness-specific feature with its
  fallback; it says the gates are scripts and the skill installs no git hooks.
- **Enterprise page** (docs/enterprise.md, US1317): harnesses, models and contracts, where data
  goes (every network call the installers and scripts make), cost controls with figures from
  signed RPT0035, and the control map; no certification claimed.
- **README first screen** (US1318): harness-agnostic and human in the lead first, one
  alphabetical install table with a verification command per row, sponsorship under
  Acknowledgements with "does not require Anthropic products"; 1,498 words.
- **Metadata** (US1315, US1319): package.json description and keywords, the GitHub About text
  and exactly CR0742's ten topics (applied with `gh repo edit`), SKILL.md's compatibility line,
  llms.txt and the `--agentic` help row; BG1599 limits the parallel-waves claim to harnesses with
  sub-agents and worktree isolation and gives reference-epic.md the one-at-a-time step.
- **Sweep guard** (US1320): a test refuses "Claude Code skill", "Claude-Code-only" and statements
  that Claude Code, Claude or Anthropic is required, across every public page.
- **Evidence page** (US1321): a Model column for every signed run through RPT0035; the reports
  record no harness, which CR0743 adds.

## What is owed

- **Runs eighteen onward** are replanned from D0519's backlog next.
- **Filed from the website run:** BG1602 to BG1607 and CR0745. BG1605 is why that run's cost
  went unmeasured (a run driven from a session started in another repository takes no token
  stamp), and BG1607 is a sign that rewrote an unrelated retro there.
- **Filed in the run, not taken:** BG1591 to BG1598 and BG1600, ruled not-stop-ship (D0532,
  RETRO0150); CR0743 (the report records the harness) and RFC0068 (a neutral skill path).
- **Carried from run sixteen:** BG1570 to BG1578, BG1581 to BG1585, BG1587 to BG1589, BG1590,
  CR0740 and CR0741; four sweep questions (BG1404, BG1103, BG1181, BG1201) wait for you.
- **Carried from run fifteen:** BG1495 to BG1497, BG1499, BG1500, BG1502, BG1504, BG1505,
  CR0713, CR0673, CR0710, US1168, and the after-tag bugs BG1508, BG1510 to BG1514 and BG1301.

## Learned the hard way

- A criterion that prescribes public wording can carry a claim the request forbids: US1319's
  prescribed "where the harness has sub-agents" was untested for four harnesses, and only the
  review caught it (BG1599, D0531). Read such a criterion against the CR's Constraints at refine.
- A phrase guard catches the phrases it lists and misses their cousins: three units were
  rejected or flagged for synonyms, modals and list forms next to the listed ones (LC-018).
- The self-check refuses a claim whose surface is a page path (BG1591): brief builders with the
  allowed surfaces until it lands (LC-021).
