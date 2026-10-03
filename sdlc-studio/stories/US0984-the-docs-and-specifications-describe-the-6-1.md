# US0984: The docs and specifications describe the 6.1 code

> **Status:** In Progress
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/existing-users.md, README.md, sdlc-studio/prd.md, sdlc-studio/trd.md, sdlc-studio/tsd.md, .claude/skills/sdlc-studio/help/verify.md, tools/tests/test_lean_docs_v61.py, changelog.d/US0984.md
> **Epic:** EP0273
> **Points:** 3
> **Persona:** Jonah Reyes

## User Story

**As a** team lead with a project on 6.0.0 (Jonah)
**I want** the upgrade page, the README and the specifications to describe the code 6.1 ships
**So that** I upgrade from one page and nobody on the team builds against a gate, ledger or command that is gone

## Acceptance Criteria

- **AC1:** Given docs/existing-users.md, then inside its opening 'Upgrading to v6' section a subsection takes a 6.0 project to 6.1: reinstall, `migrate` then `migrate --apply`, each config key that `migrate` reports removing from a 6.0 project named (the test runs `migrate.py` on a 6.0 fixture carrying `review.policy` and reads the keys from its report), the retired `handoff.py generate`, `artifact.py new --type handoff` and `gate.py --require-handoff` each beside its replacement (the signed report; `sprint.py plan --worklist RPTxxxx`), and the HO files already written staying readable; and README's upgrade answer points a 6.0 user at that subsection. Fails on: HEAD's page, which addresses only a v5 or older project, so a 6.0 user learns `--require-handoff` is gone by being refused; a subsection naming the handoff retirements with no replacement; a key `migrate` removes that the page never names
  - **Verify:** pytest tools/tests/test_lean_docs_v61.py::Docs61Tests::test_the_upgrade_page_takes_a_60_project_to_61
- **AC2:** Given sdlc-studio/prd.md, trd.md and tsd.md, each read outside its history section ('Revision History', or the PRD's 'Changelog'), when the retired-surface list this repository's front door is held to (`scripts/tests/retired_surface.py`), widened by the 6.1 retirements (`handoff.py generate`, `--type handoff`, `--require-handoff`, `carry_forward`, `run_state.batches`), reads each one, then it names nothing as current; every gate lane the TSD's artefact-gate table names is one `gate.py` registers; every module the TSD's unit coverage map names exists under `scripts/`; and every `.local/` file the three name is one a shipped script or a `tools/` script reads or writes. Fails on: the TSD left at its 2026-07-17 revision, which describes the mutation gate and its ledger (`.local/mutation-runs.json`, which nothing writes), a `mutation` gate lane `gate.py` does not register, the verification-depth gate and `carry_forward` in its coverage map; the PRD's summary still listing 'the two-role review' and 'mutation evidence'
  - **Verify:** pytest tools/tests/test_lean_docs_v61.py::Docs61Tests::test_the_specs_describe_the_shipped_code
- **AC3:** Given the help and reference pages (`help/*.md`, `reference-*.md`), then each command 6.1 added or changed is named in at least one of them as it now runs: `verify_ac.py run --unit`, `config.py show --sources`, `sprint.py lane return --tokens` and `--minutes`, `refine.py add --into`, `sprint.py plan --worklist RPTxxxx`, `handoff.py show` as read-only, and `migrate` reporting retired commands in a project's own docs; and none of them, nor README, docs/INSTALL.md or SKILL.md, teaches `handoff.py generate`, `artifact.py new --type handoff` or `gate.py --require-handoff` outside a clause saying it is retired. Fails on: a 6.1 flag shipped with only its changelog fragment describing it, as `verify_ac.py run --unit` is at HEAD (no help or reference page names it); a help page restored to teaching `handoff.py generate` as the run's last step
  - **Verify:** pytest tools/tests/test_lean_docs_v61.py::Docs61Tests::test_each_61_command_change_is_in_its_help

## Notes

- Measured 2026-10-03 at 6589fbf0 with the shipped `retired_surface.live_mentions`: TSD 6 live mentions (mutation gate x3, the verification-depth gate, the Verification depth heading, `carry_forward`), PRD 4 (two-role review, mutation evidence, the 'Mutation gate' row, one in its Changelog section, which AC2 excludes), TRD 0, README 0, docs/INSTALL.md 0, docs/existing-users.md 0. The TSD's gate-lane table names a `mutation` lane; `gate.py` registers none (`DEFAULT_CHECKS`, `ON_DEMAND_CHECKS` and the release lanes). `.local/mutation-runs.json` is named by the TSD and written by no script. So the TSD's staleness predates 6.1 (v6.0 retired the ledger and the depth gate); D0325 asks for the specs to match the shipped code, so it is in scope.
- `sprint plan` reports the TSD stale because the scripts changed after its last commit (`tsd_staleness`, a commit-time comparison). That verdict clears only once this unit's TSD edit is committed after the last script change, so it is not a Verify line here; AC2 checks the content instead.
- Measured current, so not in Affects: docs/INSTALL.md (US0968 and BG0852 already describe the latest-release default and the Copilot global target), help/handoff.md, help/sprint.md, reference-config.md. The only help gap found is `verify_ac.py run --unit` (US0804), hence help/verify.md.
- Two existing tests constrain the page: `tools/tests/test_lean_upgrade_page_docs.py` requires the first `##` section to be 'Upgrading to v6' and every retired surface (including `review.policy`) named only inside it, so the 6.0 path is a `###` subsection there; `scripts/tests/test_existing_users_page.py` executes the first fenced bash block after 'Upgrade steps', so keep that block first.
- After BG0929 (this sprint), `migrate` reports `handoff.py generate` and `--require-handoff` where a project's markdown docs use them in code, and does not scan CI yaml or scripts; the page says so.
- The specs' Version fields move to 6.1.0 in US0985, the release commit, not here.
- Name the mutant first: each test's docstring names HEAD's page, HEAD's TSD and HEAD's help/verify.md as the controls it must refuse, and runs `migrate.py` as the user does rather than reading a hand list of keys.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-03 | engineering seat (grooming) | Groomed for EP0273 under D0325: user story, three criteria with Verify lines, Affects and the measured staleness of the specs and docs |
| 2026-10-03 | engineering seat | Note re-groomed for BG0929 (QA seat, goal-review round 87) |
