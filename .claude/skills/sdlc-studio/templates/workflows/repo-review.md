<!--
Template: Repository Review Prompt (`review generate`)
Purpose: The model-driven host-repo review an agent runs against an existing codebase, filing every finding through sdlc-studio artefacts. Zero prior workspace required.
Load: Emitted by `scripts/review_generate.py prompt`; referenced from help/review.md.
Related: reference-audit.md (adversarial audit), reference-refactor.md (code review), scripts/file_finding.py (file a finding), scripts/review_generate.py (bootstrap + secret guard)
-->

# Repository Review

Review this repository for architecture, code quality, and defensive security,
then file every finding through sdlc-studio so it can be planned and fixed. The
review reads the code; it changes only artefacts under `sdlc-studio/`.

## Before you start

Run `python3 scripts/review_generate.py bootstrap --root .` once. It creates the
`reviews/`, `bugs/`, and `change-requests/` folders and their indexes if the repo
has never run sdlc-studio, so the review has somewhere to write. It is idempotent.

## Rules of engagement (binding)

- **Read-only on source.** Do not modify application code, tests, or CI. The only
  files you create or edit are sdlc-studio artefacts under `sdlc-studio/`.
- **Evidence or it does not exist.** Every finding carries file:line, failing
  command output, or a dependency version. An unevidenced suspicion goes in the
  report as an open question, not a filed finding.
- **Checks you cannot run are limitations, not guesses.** Record them as such.

## Security posture (verbatim, non-negotiable)

Security findings are remediation-only by design: report location, weakness class, realistic impact, and a concrete fix. Do not include proof-of-concept exploits or payloads. Never copy a secret value into any artefact; report a committed secret by its location plus rotation instructions, and leave the value where it is.

After filing, prove it held:
`python3 scripts/review_generate.py scan --secret "<value you found>" --root .`
must report clean for every secret you located. The value belongs in your working
memory only, never on disk.

## The three legs

Run these as parallel passes; each returns a structured findings list (title,
file:line evidence, what the code does, why it is a defect or gap, severity,
suggested remediation, size in points on the modified Fibonacci scale).

1. **Architecture** - module boundaries and coupling, data flow and mutable-state
   ownership, error-handling consistency, config and secrets approach, concurrency
   and resource management, API-surface stability, test-architecture shape,
   observability, documentation drift, performance hotspots.
2. **Code quality** - correctness defects, unclosed handles or missing context
   managers, duplication and dead code, complexity hotspots, convention drift,
   dependency health, assertion-free or cannot-fail tests.
3. **Defensive security** - input validation at trust boundaries (argv, config,
   artefact frontmatter), injection classes (command injection, path traversal),
   secrets committed or logged, outbound requests (TLS, SSRF), insecure defaults,
   CI/CD workflow permissions and unpinned actions. Apply the security posture
   above to every finding on this leg.

## Filing

- Verify each finding at its cited file:line before filing; one that does not
  reproduce is dropped or demoted to an open question in the report.
- **Bug** = behaviour is wrong, insecure, or failing. **CR** = works as built but
  should change. File with `scripts/file_finding.py file --type bug|cr ...` - never
  hand-allocate an id or edit an `_index.md`. Every bug and CR carries
  `--affects "<files>"` and `--points N` (modified Fibonacci): you have the file:line in front
  of you now, and a finding without them cannot be planned (the filer refuses it).
- Every Medium-or-higher finding gets its own artefact; Low findings may be
  consolidated into at most two themed CRs.

## Report

Give each review leg a living seat, not an anonymous voice: resolve the fitting amigo with `scripts/persona_resolve.py resolve --seat <engineering|qa|product> --render review` and adopt its charter as the leg's lens (QA for reliability/test legs, Engineering for architecture/code, Product for docs and operator-facing surfaces).

Create the report with `scripts/artifact.py new --type review --title "..."` - it
allocates the id, writes the scaffold, and appends the `reviews/_index.md` row in one
step (never hand-author the file or its index row; `reconcile` covers the review index
for row-presence drift). Fill `sdlc-studio/reviews/RV{{nnnn}}-{{slug}}.md`: system
overview, per-leg assessment, the full findings table (id, title, type, severity,
artefact ref), dedup matches, limitations, and the top five priorities in order.
Finish with a console summary:
counts by type and severity, the artefact ids raised, and one recommended next
action. Close with the team offer: `persona generate --team` can grow a
project-native working team from the repo just analysed
(`reference-persona-generate.md#team-standalone`) - offer it, never auto-run it.
