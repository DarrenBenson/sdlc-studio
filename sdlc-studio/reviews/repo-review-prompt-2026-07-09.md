# Repository Review Prompt: code, architecture, reliability (2026-07-09)

> **Purpose:** the starting spec for the second full repository review (successor to the
> RV0006 prompt, CR0175 lineage). Five parallel legs over code, architecture, reliability,
> test/CI, and defensive security; every confirmed finding filed through sdlc-studio.
> **Reuse:** self-contained; point any capable agent at a checkout and run it verbatim.

## Mission

Review this repository in depth for code quality, architecture, and reliability, then file
every confirmed finding as a Bug or CR through sdlc-studio so it can be planned and fixed.
Close with a report and a ranked set of priorities. The review reads the code; it changes
only artefacts under `sdlc-studio/`.

## Context you must hold

- The project is an agent skill: a progressive-disclosure markdown knowledge base
  (`SKILL.md` router, reference files, help, templates) over a stdlib-Python script layer
  (`.claude/skills/sdlc-studio/scripts/`, shared `lib/sdlc_md.py`). Files are the source of
  truth; `_index.md` tables are derived; single-writer operation is a documented convention.
- State of play: v4.0.0-rc.1 prepared, backlog empty, `main` intentionally unpushed pending
  an operator-gated rc tag. Consequence: the remote CI backstop is not running over the
  accumulating commits, so local gates are the only defence. Weigh findings accordingly.
- The previous review (RV0006, 2026-07-06, at v3.5.0) filed BG0053-BG0066 and
  CR0180-CR0187; all are closed, largely via EP0020-EP0025. Do not refile that lineage:
  where it matters, verify the fix HELD and report a regression only with fresh evidence.

## Rules of engagement (binding)

- **Read-only on source.** Do not modify application code, tests, CI, or docs. The only
  files created or edited are sdlc-studio artefacts under `sdlc-studio/`.
- **Evidence or it does not exist.** Every finding carries file:line, failing command
  output, or a dependency version. An unevidenced suspicion is an open question in the
  report, not a filed finding.
- **Re-verify before filing.** A finding that does not reproduce at its cited location is
  dropped or demoted to an open question.
- **Checks you cannot run are limitations, not guesses.** Record them as such.
- **Dedupe first.** Check the RV0006 findings table, the closed bug/CR indexes (including
  `archive/`), and the deferred-ideas list in `reviews/LATEST.md` (era lens, re-review
  markers, per-capability watermarks, spec-guard basename tightening) before writing a
  finding up as new.

## Security posture (verbatim, non-negotiable)

Security findings are remediation-only by design: report location, weakness class,
realistic impact, and a concrete fix. Do not include proof-of-concept exploits or payloads.
Never copy a secret value into any artefact; report a committed secret by its location plus
rotation instructions, and leave the value where it is.

After filing, prove it held:
`python3 scripts/review_generate.py scan --secret "<value you found>" --root .`
must report clean for every secret you located.

## The five legs

Run as parallel passes. Each returns a structured findings list; the record format is below.

1. **Architecture.** Module boundaries and coupling (did the CR0181/CR0187 shared-layer
   consolidation hold, or has discovery/lookup logic re-forked?); files-are-truth data flow
   and index derivation; the config regimes (CR0180 aftermath); argparse contract uniformity
   (`--root`, `--format json`); docs-vs-behaviour drift (README, TRD, SKILL.md, LATEST.md
   claims vs measured reality); progressive-disclosure health (SKILL.md and reference-file
   budgets vs what an agent actually needs to load).
2. **Code correctness and quality.** Correctness defects; duplication and dead code;
   complexity hotspots (post-US0103, what are the new worst functions?); convention drift
   (exit codes, error style, `--format json` parity); resource handling; tests that cannot
   fail; the largest modules (`reconcile.py`, `verify_ac.py`, `lib/sdlc_md.py`,
   `github_sync.py`, `migrate_v3.py`) read line by line.
3. **Reliability and failure modes** (the emphasis this round). Atomicity and crash-safety
   of every write path (index rewrites, frontmatter stamps, archive moves, `.local`
   reports); idempotency and resume behaviour of multi-step operations (`migrate_v3`,
   `project_upgrade`, `archive`, batch transitions); partial-failure states (what is
   stamped, logged, or half-written when step N of M dies - the BG0064 class); the
   single-writer convention (CR0183 aftermath: where would a second writer or a crashed
   first writer corrupt state?); `gh` CLI failure modes in sync paths; unbounded growth
   (logs, JSONL, digests, indexes); installer behaviour on re-run, partial failure, and
   non-bash-4 shells; scale behaviour (the BG0070 class: per-item subprocess or O(corpus)
   re-read patterns).
4. **Test and CI reliability.** The integration-tier gap RV0006 named (CR0185): did the
   seam tests land, and do they cover the cascades that actually broke since?; guard
   coverage vs what reaches `main` (can a commit that fails `npm run lint` land locally?
   pre-commit-hook parity with CI, hook enablement being opt-in per clone); mutation-gate
   signal (advisory - has it ever run?); test hygiene (mid-file `if __name__` layouts, the
   RETRO0016 truncation class); flakiness and environment sensitivity (tmp dirs, locale,
   git presence, network).
5. **Defensive security (remediation-only, posture above).** Trust boundaries: argv,
   config YAML, artefact frontmatter, GitHub issue bodies entering verify/sync paths;
   injection classes (command injection, path traversal via ids/slugs/filenames); secrets
   committed or logged; outbound calls (TLS, hosts, timeouts); CI workflow permissions and
   action pinning (did the EP0022 SHA pins and installer checksums hold?); insecure
   defaults.

## Finding record format

For each finding: title; file:line evidence; what the code does; why it is a defect or gap;
severity (Critical/High/Medium/Low); type (**Bug** = behaviour is wrong, insecure, or
failing; **CR** = works as built but should change); effort (S/M/L); **rc-verdict**
(`blocks v4.0 tag` or `post-v4`) with one line of reasoning. An rc-blocker is a finding
that falsifies the rc-readiness checklist, corrupts consuming projects on upgrade, or
breaks the first-run/install path; everything else is post-v4.

## Filing protocol

- File with `python3 .claude/skills/sdlc-studio/scripts/file_finding.py file --type bug|cr
  --title ... --summary ... --severity|--priority ...` - never hand-allocate an id or edit
  an `_index.md`.
- Every Medium-or-higher finding gets its own artefact; Low findings may be consolidated
  into at most two themed CRs.
- After filing, hygiene gates must hold: `reconcile.py detect` reports 0 drift and
  `validate.py` is clean over the new artefacts.

## Report

Allocate the id with `next_id.py allocate --type review` and write
`sdlc-studio/reviews/RV{nnnn}-{slug}.md`: system overview; per-leg assessment; the full
findings table (id, title, type, severity, artefact ref, rc-verdict); dedup matches;
positive observations; verification commands run with results; limitations; the top five
priorities in order; and a closing rc verdict paragraph (does anything found block the
v4.0 tag - report only, the tag stays the operator's call). Finish with a console summary:
counts by type and severity, artefact ids raised, one recommended next action.
