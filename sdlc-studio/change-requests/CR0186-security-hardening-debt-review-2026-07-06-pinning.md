# CR-0186: Security hardening debt (review 2026-07-06): pinning, installer integrity, sync redaction, state hygiene

> **Status:** Complete
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0018](../epics/EP0018-tooling-hardening-and-review-debt.md)
> **Priority:** Low
> **Type:** Improvement
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** M

## Summary

Themed consolidation of the Low-severity defensive-security hardening findings from review
RV0006. Each is defence-in-depth, remediation-only; none is exploitable in normal operation.

## Motivation

The security leg confirmed a genuinely clean core (gh-only, no committed secrets,
`yaml.safe_load` throughout, argv-list subprocess calls, sanitised slugs). What remains is
standard supply-chain and hygiene hardening, consolidated per the review's noise rule rather
than raised as separate bugs.

## Proposed Changes (each with evidence)

1. **Pin GitHub Actions to commit SHAs** (CWE-829). `.github/workflows/lint.yml:13,16,31,53`
   pin `actions/checkout@v7`, `setup-node@v6`, `setup-python@v6` by tag. All GitHub-owned, so
   low risk. Pin to full SHAs with a version comment (Dependabot keeps them fresh); optionally
   pin the CI pip installs (`coverage`, `pyyaml`, `bandit`) to majors.
2. **Installer integrity beyond TLS** (CWE-494). `install.sh:214-224` and
   `install.ps1:193-203` download a GitHub tarball and extract with no checksum/signature; the
   `skill-update` flow re-runs the installer, so it is the self-update trust anchor. Publish
   per-release SHA-256 checksums (or `gh attestation`/sigstore) and verify before extracting;
   at minimum verify the archive path prefix during extraction.
3. **Redact/confirm before publishing artefact bodies to GitHub** (CWE-200).
   `github_sync.py:99-110` runs `gh issue create --body rec.body` (the whole markdown file)
   with no dry-run-by-default, per-file consent, or secret scan; the neutrality guard protects
   tracked skill files, not workspace artefacts. Add a lightweight secret/PII pattern scan on
   the body and require `--yes` (or default to dry-run + summary) when the target repo is
   public.
4. **Do not commit runtime state** (CWE-538, hygiene).
   `.claude/skills/sdlc-studio/.local/version-check.json` is tracked; `.gitignore` ignores the
   workspace `.local/` but not the skill-install `.local/`. `git rm --cached` it and add
   `.claude/skills/sdlc-studio/.local/` to `.gitignore`.
5. **Constrain the verify_ac `http` verb in restricted mode** (CWE-918).
   `verify_ac.py:312-326` fetches story-supplied URLs via curl with no scheme/host restriction.
   In any `--no-shell`/restricted mode (BG0056/BG0057), constrain `http` to http/https and an
   optional host allowlist from `.config.yaml`.
6. **Document the mutation.py `--test` boundary** (CWE-78, accepted-by-design).
   `mutation.py:222` runs the operator `--test` command via `shell=True` (argv-only, correctly
   process-group-killed on timeout). Document that `--test` must be a fixed project-level
   command (e.g. `.config.yaml` `quality.test_command`), not derived from artefact content, for
   agent-driven runs.

## Acceptance Criteria

- [ ] Actions pinned to SHAs; CI still green.
- [ ] Both installers verify a per-release checksum before extraction.
- [ ] `github_sync` push scans for secrets and requires confirmation (or dry-run default) on a
      public target repo.
- [ ] `version-check.json` untracked and the skill-install `.local/` gitignored.
- [ ] Restricted-mode `http` verb enforces scheme/host limits; mutation `--test` boundary
      documented.

## Dependencies

| Artefact | Relationship |
| --- | --- |
| BG0056, BG0057 | Items 5 depends on the restricted/no-shell mode those introduce |
| BG0058 | The lint.yml permissions block (Medium) is filed separately; item 1 here is the pinning half |

## Risk

Low. Hardening only; the installer checksum work must ship the checksums alongside the release
or it blocks legitimate installs - sequence the publish before the verify.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Consolidated 6 Low security findings from RV0006 |
