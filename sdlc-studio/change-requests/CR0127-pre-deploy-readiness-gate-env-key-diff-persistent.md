# CR-0127: pre-deploy readiness gate: env-key diff, persistent-volume assertion, remote heredoc, crypto round-trip

> **Status:** Complete
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/reference-deploy-readiness.md
> **Depends on:** -

## Summary

Distilled from a second consuming repo's release lessons (v1.2.1-v1.4.0) and a consuming repo's durability
incident. The same deploy-time failures recur across projects because the skill's
`reference-deploy-readiness.md` describes post-deploy verification but has no **pre-deploy
checklist** that catches these classes before they reach production:

1. **Env-var default drift silently breaks deploys.** a second consuming repo v1.2.1 replaced a hardcoded port
   with `${AGENT_CREW_PORT:-3000}`; prod `.env` lacked the key so the default kicked in and the
   smoke test timed out. Remedy: diff `.env.example` against the prod `.env` and refuse to deploy if
   required keys are missing.
2. **Durability contracts betrayed by non-persistent paths.** a consuming repo shipped "durable task
   persistence" tested against a tmpdir; in prod the default checkpoint dir resolved to a
   non-bind-mounted container path, so every restart wiped it. Remedy: a startup assertion that the
   durability target is on a persistent volume, or a schema that forces an explicit operator-set
   path. Add to every such feature's ACs: "restart the container; verify data survives." This is the
   deploy-side sibling of [[LL0006]] (deploy meta-files gap class).
3. **Remote-command quoting is a recurring footgun.** `set -e` inside `bash -c '...'` over ssh does
   not propagate failures, and layered awk/sed quoting mangles. Remedy: standardise on
   `ssh ... bash -s <<'EOF'` heredoc form and explicit `$?` checks; never `bash -c "..."` for
   multi-command remote blocks.
4. **Ops helpers that mirror a crypto routine must mirror the serialisation format byte-for-byte.**
   a second consuming repo stored a token base64 while the canonical decryptor expected all-hex, breaking the
   dashboard in production. Remedy: any helper touching encrypted state round-trips against the
   canonical decryptor before being trusted.

Each is generic deploy-readiness wisdom, not a project fact. The aim is a reusable pre-deploy
checklist (and, where mechanisable, a gate) in the skill, so a consuming project inherits the
defences instead of rediscovering them in production.

## Acceptance Criteria

- [ ] `reference-deploy-readiness.md` gains a **Pre-Deploy Checklist** section covering: env-key
      diff (`.env.example` vs target env, refuse on missing), persistent-volume assertion for any
      filesystem durability contract, remote-command heredoc discipline, crypto serialisation
      round-trip for ops helpers
- [ ] the persistent-volume item prescribes the AC pattern "restart the container; verify data
      survives" for any feature whose durability contract writes to the filesystem
- [ ] the env-key-diff item is expressed so a project can wire it as a release-script gate (refuse
      deploy on missing required keys), not just a manual step
- [ ] cross-links to [[LL0006]] (deploy meta-files gap) and `reference-operator-heuristics.md`
- [ ] **deterministic where possible** ([[LL0008]]): the env-key diff and the persistent-volume
      assertion are specified as mechanical checks a project wires into its release script / startup
      (refuse/abort on failure), not manual checklist prose; items that can only be advisory (e.g.
      crypto round-trip discipline) are named as such with the reason
- [ ] CHANGELOG `[Unreleased]` entry ([[LL0004]]); link checker green

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-27 | field | Created via `new` (deterministic) |
