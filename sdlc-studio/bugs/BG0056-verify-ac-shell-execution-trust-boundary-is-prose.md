# BG0056: verify_ac shell execution trust boundary is prose-only: externally ingested Verify lines reach shell=True

> **Status:** Closed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Severity:** High
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** M

## Summary

`verify_ac.py` executes story-embedded `Verify:` lines as shell commands. The trust model
that keeps this safe ("never run verifiers on a story whose AC block came from un-reviewed
external content") is documented in prose only; there is no technical control on artefact
provenance, and an ingestion path from GitHub issue bodies exists.

Weakness class: CWE-78 (OS command injection at a data/code trust boundary). Remediation-only
per the review rules of engagement - no exploit steps recorded.

## Evidence

- `.claude/skills/sdlc-studio/scripts/verify_ac.py:165` - `subprocess.run(command,
  shell=True, ...)` for the `eval` verb.
- `verify_ac.py:193-200` - `shell=isinstance(cmd, str)`.
- `verify_ac.py:303-309` - the `shell <cmd>` verb plus the fallback that treats the whole
  expression as a shell command.
- `verify_ac.py:312-326` - the `http` verb builds a curl+jq shell pipe from a story-supplied
  URL.
- Trust model documented prose-only: `reference-verify.md:155-162`.
- Ingestion path: `github_sync.py:438-444` instructs the agent to ingest a GitHub issue body
  (`--from-issue`) into a story template; anyone who can get an `sdlc:story`/`sdlc:cr` label
  applied to an issue controls that body.

## Impact

Content originating outside the repo (GitHub issue bodies, or prompt-injected text an agent
copies into a story) can reach shell execution with the operator's privileges when
`reconcile --verify` runs. Enforcement of the documented boundary is entirely procedural, and
the primary "reviewer" in the autosprint flow is itself an LLM.

## Steps to Reproduce

Not recorded (remediation-only). The trust boundary is evidenced by the code paths and the
ingestion workflow above; no proof-of-concept is needed to fix it.

## Proposed Fix

Add a technical control matching the documented model: stamp externally ingested artefacts
(e.g. a `Provenance: external` frontmatter field written by the ingest workflow) and make
`verify_ac` refuse - or require an explicit `--allow-external` flag - to execute
`shell`/fallback/`eval` verifiers on stamped files. Optionally add a `--no-shell` mode
restricting execution to the structured DSL verbs (argv lists) for CI use.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Evidence verified; filed from RV0006 security leg (remediation-only) |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Fixed with a failing-first regression test on branch sprint/rv0006-bugfixes; transitioned to Closed |
