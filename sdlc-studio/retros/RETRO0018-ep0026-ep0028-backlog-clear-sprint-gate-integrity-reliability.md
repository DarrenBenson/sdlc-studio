# RETRO-0018: EP0026-EP0028 backlog-clear sprint: gate integrity, reliability tier, era completion + DX

> **Date:** 2026-07-10
> **Batch:** EP0026 (gate integrity, 10) + EP0027 (reliability tier, 11) + EP0028 (era completion + DX, 9) - the whole RV0007 backlog, cleared to empty
> **Goal:** done (deliver the entire open backlog before the v4.0 tag)
> **Delivered:** 30 / 30   **Blocked:** 0

## Delivered

- **EP0026 gate integrity (10 units).** The meta-layer now verifies itself: `gate.py` runs `gate.py`,
  the provenance-stamp writer that gates shell verifiers exists on the ingest path, CI runs `gate.py`,
  and the eval gate the release template mandates is back in the rc checklist. Closed with a full-diff
  critic APPROVE and evals 4/4; the two-Claude harness caught BG0099 that unit tests missed.
- **EP0027 reliability tier (11 units).** Crash-safe, resumable, honest under failure: copy-then-swap
  installers, the concurrency floor completed (lock + atomic writes across every create path), push
  adopts an existing issue instead of duplicating, and a themed Low-severity hardening batch.
- **EP0028 era completion + DX (9 units).** The schema-v3 default now behaves end-to-end
  (BG0086/87/88/93/97/99): ULID identity, story-to-ULID-epic wiring, migrate scaling past 1024 files,
  short-id entropy, config degrade, JSON exit codes, a lint-safe finding filer. Plus three CRs -
  CR0211 (retros/reviews reconciled like every type), CR0210 (one CLI argument grammar), and CR0208
  (a 10-AC quality/docs debt sweep: dead-code fold, fenced-block awareness, cmd_plan/cmd_push
  decomposed from cognitive 73/85 to 10/9, provenance guard widened, `--format json` parity,
  check_links root-docs pass, scope-safe `--target auto`, two new v4 eval scenarios).

## Blocked / deferred

- None. Every unit reached its terminal status; a handful of larger sub-items inside the reliability
  and debt batches were explicitly deferred with a note in-artefact (batch-op amortisation, gh
  pagination, mutation SIGKILL sidecar), not silently dropped.

## What went well

- **The eval harness earned its keep twice.** It caught BG0099 (v3 greenfield story-wiring, invisible
  to unit tests) during EP0026, and the fresh-worker run of the two new v4 scenarios (05 schema-v3
  identity, 06 independence gate) confirmed both surfaces behave correctly for a naive agent - 2/2.
- **Adversarial critics with a no-git-state guard.** After a critic's `git stash` briefly reverted
  live edits early in the sprint, every subsequent critic carried "NEVER run git stash/checkout/reset;
  compare with `git show HEAD:<path>`". Zero collisions after that. The CR0208 closing critic traced
  the cmd_plan/cmd_push decomposition line-by-line and confirmed no behaviour change.
- **Dogfooding closed its own loop.** CR0211 was built, then used to create THIS retro
  (`artifact new --type retro`, indexed automatically) - the first retro that was not hand-authored.

## What was hard / what stalled

- **Provenance tags kept tripping the widened guard.** Extending the style guard to `scripts/lib` and
  `templates/**` (CR0208 AC6) surfaced ~16 live `(CRxxxx)`/`(RFCxxxx)` leaks, and my own commit
  messages/docstrings re-introduced a few - several commit round-trips were spent stripping them. The
  guard doing its job, but a reminder to write provenance in git/CHANGELOG, never in shipped prose.
- **The broad anchor-less link check was a dead end.** CR0208 AC7 first tried checking every bare
  `.md` link in the skill tree; it flooded false positives (templates and doc examples legitimately
  link to consuming-project files that do not exist here). Scoped it to the root docs, where links
  are real - the honest, drift-free subset.
- **AC2 was the one genuinely risky change.** Decomposing two 70-85 cognitive functions is where a
  silent behaviour change hides; leaned entirely on the existing sprint/github-sync suites plus a
  line-by-line critic rather than trusting the refactor.

## Lessons

- **A guard is only real when it covers the whole surface.** CR0208 found the provenance guard, the
  hook trigger, and check_links each bounded to a subset (scripts-not-lib, scripts-not-templates,
  skill-not-root). Widen coverage deliberately and strip what it then catches in the same change.
- **Fenced examples are not directives.** A `- **Verify:**` line inside a fenced code block reaching
  shell execution is a real hazard; parsers over shipped markdown must be fence-aware. Worth carrying
  to any project whose docs mix examples with executable directives.
- **Two-layer independence is defensible.** The primitive (`critic.py record`) logs a self-review with
  a warning; the orchestrated close and the terminal gate refuse it. The eval confirmed a self-review
  cannot reach a terminal status - defense-in-depth, not a single choke point.

## Metrics

- Units: 30 delivered / 30, 0 blocked · 49 commits (RV0007 -> this close) · Tests: 1562 skill + 117
  tools green · reconcile drift 0 throughout · Critic rejects during the sprint: several (BG0073
  migrate-resume identity loss, CR0209 annotate 5-finding first cut) - each caught pre-merge and fixed.
