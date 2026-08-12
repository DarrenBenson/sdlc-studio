# CR-0545: Everything after the tag is un-tooled: no command publishes a release, so the runbook has no row for the step and the assets the install path verifies against have never been produced

> **Status:** Proposed
> **Created:** 2026-08-12
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/release_cut.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/help/release.md
> **Priority:** P1
> **Type:** Improvement
> **Size:** M

## Summary

`release_cut.py` carries three verbs - `changelog-cut`, `record-green`, `tag-check` - and stops at the tag. Nothing publishes. `reference-sprint-toolchain.md` has no row matching release, tag or publish, so the runbook that AGENTS.md tells every session to read BEFORE starting a step is silent on this one, and the step is therefore hand-driven every time by whoever is holding the release.

The cost is not hypothetical and it is already paid twice. The v4.1.0 GitHub Release carries zero assets (`gh release view v4.1.0 --json assets` returns an empty list), so the `.sha256` sidecar both installers verify against has never existed for any version - BG0575. And v5.0.0 was tagged and pushed with no Release published at all, which matters more than it reads: `version_check.py:62` polls `releases/latest`, so until somebody remembers to publish by hand, every installed copy of the skill on every machine still reports v4.1.0 as current and prompts nobody to upgrade. A version that is tagged but not published is, to the tool's own update mechanism, unreleased.

This is the shape the repository files against itself elsewhere: a step that matters, performed by memory, with no command to run and nothing to refuse when it is skipped. LL0027 - when a rule matters, gate it in the command people actually run - applies to a step nobody can even name.

The fix pairs with BG0575 rather than merely resembling it. BG0575 needs release assets to exist, and repairing it by uploading two files by hand would leave the NEXT release broken in the same way, which is the defect again one version later.

## Impact

Anyone releasing this project, and every consumer of a release they cut. The publish half shipped
under BG0575 - `.github/workflows/release.yml` builds and uploads the assets on a tag, and the
runbook gained a Release section - so what remains here is the part that REFUSES rather than the
part that acts: nothing checks, after a release, that the assets a verified install depends on are
actually there. A workflow that fails silently, a tag pushed while CI is disabled, or a release cut
by hand all land in the same place the last two did, and the first symptom is a user's install
refusing.

`tools/release_assets.py check --tag <v>` is the check and exits non-zero naming each missing file.
It is not yet wired into anything that runs on its own.

## Acceptance Criteria

- [ ] Given a tag whose Release is missing any of its four assets, when the release boundary runs,
  then it refuses and names each missing file. Mutant: delete one sidecar from a published
  Release; the boundary must redden.
- [ ] Given `release_cut.py` is a SHIPPED script and `tools/` is repo-only, when the check is
  wired, then no shipped script imports a repo-only module. Mutant: import `release_assets` from
  `release_cut.py`; a consuming project's gate must still run.
- [ ] Given a project with no release automation of its own, when it runs the release step, then
  it is told what to build rather than failed for lacking this repository's workflow.

## Design Options

- **A: a `publish` verb on `release_cut.py` that builds the assets from the tag, uploads them and creates the Release, run by a human at the boundary. B: a GitHub Actions workflow triggered on the tag or release event that does the same, so the assets cannot be forgotten and the recurring cost is not borne by a person. C: both - the workflow as the normal path, the verb as the manual fallback for a tag pushed without CI.**

## Recommendation

B, with the gate that BG0575's adversarial plan review ruled load-bearing: a hand-run upload of four assets (tar.gz, zip and a sidecar each) is exactly the step that gets skipped, and BG0575's whole fix depends on those assets existing. The review's ruling was conditional - publish the assets from a workflow and the approach holds; leave it as a runbook line and the approach should be abandoned for the weaker one, because a repair certain to be forgotten is worse than a smaller repair that persists. Extend `release_cut.py tag-check` to refuse a tag whose Release carries no asset pair, so the gate lives in the command the release already runs rather than in a document. Add the runbook row in the same change, because the runbook is what sessions are told to read - the script catalogue is not.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-12 | sdlc-studio | Created via `new` (deterministic) |
