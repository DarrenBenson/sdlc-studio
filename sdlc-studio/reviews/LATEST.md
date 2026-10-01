<!-- close-status:begin -->
> **RUN-01M3T8N1 closed goal-reached.** 9 unit(s) in the batch. **The run is SIGNED** - nothing is owed on this run.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->
> **RUN-01M3VF2J, the whole groomed backlog in one run: achieved.** Goal: "Every open finding
> closes: Maya and Jonah get honest commands, safe installs and upgrades, and leaner sprint
> machinery." 40 of 40 units approved by one independent QA seat each (34 in the batch, six
> discharged by their rejecting reviewer after a carry at the round cap); 34 of 34 verify
> green. Run unattended under D0290 in two file-disjoint build lanes.

## What landed

- **Honest commands.** No CLI reports success it did not get (US0969); ids print as their files
  spell them (BG0825, BG0877); `config show --sources` (US0759); `verify_ac run --unit` and the
  near-miss hint (US0804, US0966); a fields-file key spelled as the verb's flag (US0805); the
  finding writers keep every criterion and verifier (US0970); docs and comments tell the truth
  (US0973); derived figures read honestly (US0972); a fresh project's first plan is quiet but
  still reports a hook that diverges, including through a worktree or `~` hooksPath (US0971).
- **Safe installs and upgrades.** install.sh takes the latest verified release (US0968);
  install and upgrade never damage a consumer's files (US0976); a v5 upgrade reads clean and a
  failed migrate step names its unreadable file (US0974); migrate names retired surface in a
  project's own docs (US0975); install.ps1 targets Copilot globally (BG0855); js-yaml,
  brace-expansion and markdown-it held at patched releases (BG0866, BG0876, npm audit 0).
- **Leaner machinery.** The signed report replaces the handoff page; its writers and
  `gate.py --require-handoff` are retired (US0967, US0978); the revert-check gate lane and the
  batch-span API are gone (US0784, BG0861); `review.policy` retired and disclosed (BG0831);
  the pre-push gate judges the pushed commit in its own worktree (BG0837).

## What is owed

- **Filed from this run, all groomed for the next sprint:** BG0870-BG0873, BG0878, BG0882,
  BG0885-BG0889. One more (`.py` optional in the retired-surface scan) is filed after the close,
  as the run hit its 20-finding triage cap.
- Review was the run's cost centre: 17 of 40 units rejected in round 1 and six carried at the
  cap, every blocking finding real; see RETRO0129.
