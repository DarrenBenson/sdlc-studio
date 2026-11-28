# Script Catalogue - Audit, review & critic

<!-- Load when: you need the full detail for a script in this group. The lean
     index with all groups is reference-scripts.md. -->

Detail pages for the **audit, review & critic** scripts. See
[reference-scripts.md](reference-scripts.md) for the full index across all groups.

## Scripts

### `ac_scope.py`

Authoring lint (advisory): `check` flags a story whose acceptance criteria mention a
distinctive capability keyword owned by a **different** epic's title (e.g. an EP0001 story
asserting an "account token" when accounts are EP0006) - such a story is un-Done-able in its
own epic and should be split or re-scoped. Heuristic and read-only; false positives are
expected (the operator decides); never auto-edits. Run by the authoring loop's closing
consistency pass.

### `spec_guard.py`

Spec-edit guard (schema v3 only, dormant on v2). A delivery must not silently falsify the
source of truth. `spec_edits(root, changed_files)` reports which changed files are
requirements/spec documents (config `review.spec_paths`); `check(root, changed, story_text)`
adds whether any AC cites a spec change and flags an `untraced` edit (a spec doc edited with no
citing AC) - the signal the critic charter treats as a blocking finding. The
traceability judgement stays with the critic; the pre-check only guarantees the edit is
surfaced. `check --changed a,b,c --story <file>` on the CLI.

### `constitution.py`

Project-constitution principle gate. Asserts the machine-checkable
principles declared in `sdlc-studio/constitution.md` - each `rule:` maps onto an
existing detector (integrity/conformance/validate/reconcile). Advisory by default;
`constitution.enforce: true` makes a violation exit non-zero.

- `check`: report (and, when enforced, fail on) principle violations

Full methodology: `reference-doctrine.md#constitution`.

### `schema_check.py`

One CI-runnable command over the schema-v3 team-schema rules, emitting STABLE rule ids so the
output is a reference implementation the wider crew audit linter can consume:

- `check`: run all rules; exit 1 on any error-severity finding, 0 on a clean repo. `--format
  json` gives `{ok, rules, findings}` with `{rule, file, message}` per finding.

Rules (all era-gated to schema v3, so a v2 project reports nothing): `authorship-structured`,
`authorship-type`, `authorship-unresolved`, `evidence-present`, `duties-separated`,
`id-format`, `index-derived`. These same rules are enforced in the blocking `gate` via
`validate` and the `index-derived` check; `schema_check.py` is the focused, stable-id view.

### `review_prep.py` (read-only, except `close`)

- `close --rv RVxxxx [--latest-body FILE|-]`: the review close, tool-carried - stamps
  `review-state.json` for every present leg and derives `reviews/LATEST.md` from the
  supplied anchor body. Refuses when the dated RV record does not exist, and refuses an
  anchor that never cites the RV id: the anchor derives from a record or not at all
- `prep`: deterministic inputs for the five-leg review (artifact staleness,
  persona definition-vs-PRD usage, count and AC-verification inputs, and `required_legs` -
  for each of the four required document legs, `{present, path, waiver}` so an absent leg is
  machine-visible and a downgrade-without-a-waiver is detectable). Gathers inputs only; the
  verdict stays with Claude. Full workflow: `reference-review.md`.

### `disclosure.py`

Progressive-disclosure + Claude Code best-practice check, **advisory**. Flags reference-/
help- files missing a `Load when:` trigger or orphaned from every index (SKILL.md / help/references.md
/ help/help.md), plus best-practice items from `best-practices/claude-skill.md` (scripts executable +
expose `--help`, templates use `{{placeholder}}`, SKILL.md has a When-to-Use section). Skill-dev only
(no-op for consuming repos). Wired into the gate as NON-BLOCKING; `--strict` opts into a non-zero exit.
The token lever: a doc with no load-trigger and no index entry gets pulled in without discipline.

### `readiness.py`

Tranche pre-flight readiness (deterministic). `check` grooms a batch for readiness - weak-AC, unmet-deps, already-terminal, link-integrity, **already-satisfied** (a Ready unit whose executable ACs all pass in the verify-report - a close-candidate, not work to build, unless it is carried on an unanswered delivery REJECT: `transition` refuses that close, so it stays ready for the batch with a `carried: re-review by <reviewer id>` note, to be re-reviewed by the reviewer who rejected it), **weak-verify** (a non-executable Verify line, reusing `verify_ac lint`) and **cross-epic-ac** (an AC owned by another epic, reusing `ac_scope`) - before the triage STOP, so work never starts on a unit that would pass the gates vacuously or be reverse-engineered at implement time.

`profile --name <name>` resolves an adversarial lens profile: the packs under
`templates/audit-profiles/` (`skill`, `repo`, `code`) plus the reference-declared
`project` default, reporting the pack's lenses and its refute threshold. A name no
profile declares is refused non-zero, naming the ones that exist, so a mistyped
profile can never run an empty lens set; `profile --list` names them all. The repo
pack carries the binding remediation-only security posture for its
defensive-security leg.

A `Depends on:` referent resolves through the shared cross-repo resolver (`lib/xrepo`, the same one `blocker_sweep` uses): in-repo first, then across the sibling repos a `product-manifest.yaml` names. So in a multi-repo product, a dependency **delivered in another repo meets the dependency** rather than reporting `unmet-deps`. A repo the operator has not cloned never stops the search - the remaining repos are still searched, so the verdict follows the disk state and not the manifest's ordering. The three outcomes stay distinct claims: `unmet-deps` (the referent exists and is not delivered, or is dead), **`unresolved-deps`** (no repo resolved the id AND at least one named repo was not on disk, so the dependency could not be checked either way - the repo and path are named, and the unit is never silently passed), and no finding. Single-repo projects have no manifest and are unaffected.

### `backfill_audit_runs.py`

Lifts the audit run id out of a finding's `Raised-by` prose into a readable `Audit-run` field, so a class recurring across runs is counted from the record rather than reconstructed with a regex over free text. `plan` reports the mapping read-only; `apply` stamps the field, records the lens as explicitly UNKNOWN, and seeds each run into the register as `backfilled`; `check` is the standing sweep and exits non-zero when any finding names a run in prose its field does not carry. It relocates a datum somebody already wrote and derives nothing: a `Raised-by` line naming two ids is resolved only where the prose says which filed it (`run <B>` against `<A> carry-over`, the shape all twelve real cases use) and REFUSED otherwise, because a coin toss between two ids is a fabricated provenance. The lens is never guessed - `detector-owed` treats the unknown sentinel as unattributable rather than as a lens of that name, or one placeholder shared across five runs would report a detector owed on every one of them. Idempotent; writes only the artefacts it stamps and its own register shard.

### `audit_cost.py`

Pre-flight cost estimate for an adversarial `audit` run, so a large fan-out is confirmed before it spends millions of tokens rather than flagged only after it launches. Given the lens count (and optional rounds/votes/candidates-per-lens), `estimate()` models the agent count (finders = lenses x rounds; refuters = candidates x votes; +1 merge), the token budget (agents x a calibrated per-agent rate) and the wall-time, and flags the run **large** (confirm) or **small** (runs without ceremony). Calibrated to the measured reference run (7 lenses -> ~190 agents / ~6.8M tokens / ~35 min); an order-of-magnitude guide, not a promise. Used by the audit pre-flight gate (`reference-audit.md#audit-preflight`). Pure stdlib; read-only.

### `command_audit.py`

Audits the skill command surface against the process spine (raise -> break down -> sprint+review; the top-level documents are the levers; reconcile/review/audit are support). Enumerates every command deterministically - the SKILL Type Reference, the `help/help.md` catalogue, and `scripts/` - and disposition each as **keep** or **review** from three structural signals: the curated SPINE category it serves (an unmapped command is a review candidate), catalogue DRIFT (a command in the help catalogue but not the Type Reference, or vice versa), and TOOLING health (with `--check-tools`, whether the backing script's `--help` runs - a script that exists and fails is a broken tool). It does not retire anything - it produces the evidence a cleanup acts on. `--write` writes `sdlc-studio/reviews/command-audit.md` (a per-spine table plus recommended actions); `--strict` exits non-zero on a broken tool. Complements `doc_coverage.py` (which gates the reverse: every Type-Reference command has a help entry, every script a reference entry).

`--dead-flags` is a separate mode: it reports a **flag whose parsed destination no line acts on**, across the skill's `scripts/` and the repo's `tools/`, and exits non-zero when it finds one. The analysis follows the value rather than counting mentions - a destination read through `getattr(args, name, default)` and forwarded as a keyword argument is alive only if the receiving parameter is acted on, which is the shape a documented-but-dead flag hides in. Positionals are not judged (argparse enforces their presence whether or not a line reads the value). Three shapes are reported **not judged** with the reason, never dead: a namespace handed to a callee the analysis cannot resolve, a `getattr` whose attribute name is computed, and a module that declares flags on a parser it never parses (the shared `add_*_arg` helpers).

### `critic.py`

The independent-critic verdict ledger. `record` writes a committed verdict to `sdlc-studio/reviews/critic-verdicts.md` stamping both the **reviewer and the author** (the authoring seat / delegation id); `verdict_for` reads it. `is_independent` proves `reviewer != author`; `is_pre_gate` flags units closed before the gate (the visible `pre-gate` marker, grandfathered). Conformance's `critiqued` stage requires a committed APPROVE that is independent or pre-gate.

The ceremony's scaffolding is deterministic too: `brief --unit USxxxx --seat qa [--tier full|light]` assembles the seat-review prompt (charter reference, the unit's canonical ACs, the Affects-derived diff scope, the review depth, the exact VERDICT/ISSUES/BLOCKING return contract, and after it the absolute path of a fresh file under the main checkout's `sdlc-studio/reviews/verdicts/<unit>/` for the reviewer's own block, with the `UNIT:` and `BRIEF:` lines it opens with, all three kept out of the fingerprint) - pipe it to the reviewing subagent verbatim; unknown unit or seat refused naming the alternatives. `record --from-verdict FILE|-` parses that file or a returned block, the footer printing the command that reads the file (a missing or non-APPROVE/REJECT verdict is refused loudly, BLOCKING content folded into the issues; a `RULINGS:` line, and prose after `BLOCKING: none`, kept on the row as one `RULINGS:` item that `parse_findings` never reads as a finding and `row_rulings` returns), so a verdict is never hand-transcribed into the ledger. The row's ninth cell, `Source`, binds it to those bytes: `sha256:<first 16 hex digits of the file's exact bytes> <basename>` when a brief here issued that file for the unit (a note in `.local/briefs.jsonl` names the path, so a file briefed in another clone does not count), else `-`, with `record` saying on its own line, after the `recorded` line `sprint lane accept` parses, that the verdict was transcribed (stdin, `--verdict`, or any other file, even one in the same folder). The file is read once and left byte-identical; commit it with its row. `show` reads the first as "from the brief's verdict file (writer unread)", naming `sdlc-studio/reviews/verdicts/<unit>/<basename>`, and `-` as "transcribed", and `--format json` carries the same as `provenance` and `verdict_file`. The column is padded in before `Issues`, so `row_identity` still digests the first eight cells and no identity a run record froze moves; a 6.3.0 or earlier reader skips every nine-cell row as malformed, so it sees no verdicts. The judgement stays with the seat; only the plumbing is mechanical.

The footer's record command names both seats as `<holder> (<role>)`, the holder being the name on the project's card for that role (`<role> seat` when it has none): `--reviewer` the seat briefed, and `--author` the seat `sprint lane brief --seat <role>` (default engineering) recorded on the open run as building the unit, or the engineering seat, with a note saying no lane recorded the builder. When the seat briefed is the one that built the unit, a second note says a verdict recorded as printed is a self-review. `recorded_seat(cell)` reads a Reviewer or Author cell's seat from its first `(<role>)` or `(<role> seat)` group only, never from the words around it. On a project that declares seats, every delivery writer warns on stderr when the author carries no such group, and records the row as given.

A REJECT has two exits, and `critic.py record` writes both: a round-2 APPROVE from the reviewer who rejected, or that reviewer's round-2 REJECT at the cap (`review.max_rounds`), which files the findings as a bug and drops the unit from the open run's batch. A carried unit is still refused Done; it is delivered again in a later run and reaches Done on an APPROVE from the same reviewer id. `repair` is retired: it exits 2 naming the two exits and writes nothing, and the old `sdlc-studio/reviews/repair-record.md` is read by nothing.

`brief --rejoinder [FILE|-|ledger]` emits the RE-REVIEW brief after a REJECT's repairs: the prior VERDICT/ISSUES/BLOCKING quoted verbatim, then the diff scope refreshed, the demand to re-execute the previously named probes and mutants and to rule each prior finding CLOSED, OVER-CLAIMED or MOVED on the contract's RULINGS line, and the delivery return contract. It prints the fingerprint footer on stderr that `record --brief` consumes, naming the record command. A malformed prior block is refused loudly. With no value, or `ledger`, it reads the prior verdict from the ledger: the latest unanswered REJECT in the unit's current delivery from a reviewer of the briefed seat (any reviewer on a project that declares no seats). A row bound to its issued file is quoted from that file's bytes, found through its `Source` cell; a transcribed row, or one whose file is missing or changed, is rebuilt from its cells (VERDICT, every finding with its `BLOCKING:` mark, RULINGS) and introduced as rebuilt, not as the reviewer's words. No such REJECT, or several reviewers holding one, exits 2 naming the unit and the seat, with nothing on stdout. A plain brief for a seat holding one names `--rejoinder` on stderr.

`approach record --unit <id> --verdict go|changes --note <path> [--changes FILE] --reviewer <id> --author <id>` records a seat's review of a builder's approach note, before any code, as one row of `sdlc-studio/reviews/solution-reviews.md`: the round (with `review.solution_review.panel` set, the reviewing seat's rows for the unit so far plus one, and otherwise the unit's rows so far plus one, counted under the ledger lock), the verdict, the note's digest (the first 12 hex digits of the sha256 of its bytes), the note's path relative to the project root, both ids, the date and, for CHANGES, the changes file's text. It exits 2 and writes nothing for a unit `review.solution_review` does not name (both of its settings ship off, so every unit until a project sets one), a GO with `--changes`, a CHANGES without them or with an empty file, a note that names no file, a reviewer of the author's identity or none, and a value no cell can hold. With `review.solution_review.panel` set it also exits 2 and writes nothing for a reviewer that names no `(<seat>)`, so sits in no seat; one that sits in a seat the unit's panel does not seat, naming the panel and each skipped seat and why; and a `(persona)` reviewer who is not the unit's Persona, since only the unit's own Persona sits in the persona seat; a malformed panel is refused, never read as empty. It does not check the note's content. `solution_review_reason` and `approach_agreed` are the readers for other scripts to call: the second is ok, with `review.solution_review.panel` unset, only when the unit's latest row is a GO against the note's digest now; with it set, only when the latest row of every seat the panel seats on the unit is a GO against the note's digest now, and never when it seats nobody.

`approach brief --unit <id> --seat <role> --note <path>` prints, on stdout, the brief for the seat reviewing that note: the seat's review render, the unit's Affects and criteria, the decisions that bind it (found by id only: each `D` and four digits named in the unit, its epic, or the request its `Delivers` or its epic's `Parent` names, with the row's text from `sdlc-studio/decisions.md`), the note verbatim, what to judge, the rule to spot-check by execution in a scratch copy only, that the seat will not review the code, and the two `approach record` commands. It exits 2 with nothing on stdout for a note that names no file, lacks one of the five level-2 headings (`## Reading`, `## Design`, `## May break`, `## Tests`, `## Sentences`, each of which may lead with more words), or whose `## Tests` section does not name every criterion id. A unit `review.solution_review` does not name is still briefed, with a note on stderr that `approach record` will refuse its verdict. It writes nothing. `brief` tells a seat that reviewed the unit's approach (by the `(<role>)` of a ledger row's Reviewer cell) on stderr that its code review must go to a fresh context that has not read the note, and its stdout carries nothing of the solution review.

`approach brief --seat persona` frames the stakeholder persona the unit's Persona field names: it opens by naming the persona and the card at the path `sdlc-studio/personas/index.md` gives, to be read whole, asks the persona's own questions, and names `<name> (persona)` as the reviewer in its record commands. It exits 2 with nothing on stdout, naming the remedy (register the persona, correct the story's Persona field, or take `persona` off the panel), for a unit with no Persona, a missing registry, a name the registry does not hold, a card that names no file, and a card the persona standard holds under `personas.standard: block`; under `report` it prints, with one stderr line naming the card. With `review.solution_review.panel` set, the brief of a seat the panel seats also names the other seated reviewers as separate reviewers, its round, its own latest CHANGES quoted as `>` lines, and its reply file `sdlc-studio/.local/solution-review/<id>-<seat>-r<round>.md` in place of REVIEW.md; a seat the panel does not seat gets the brief as with the panel unset, and a stderr line that `approach record` will refuse its verdict. `approach panel --unit <id> --note <path>` prints one line per seat the panel seats, in its order, with the reviewer, round, latest verdict, `approach brief` command, reply file and the `approach spend` command to run when that seat's agent returns, a line per skipped seat and why, that each brief goes to its own agent, and, when the panel seats nobody, that the approach cannot be agreed; with the panel unset it says one seat's GO agrees the approach. It exits 2 with nothing on stdout for what the brief refuses for the unit and note, a malformed panel, and a seated persona that cannot be framed, so no roster names a persona brief that would be refused; it does not check the seat cards, whose own brief refuses a held one. Neither verb writes anything.

`approach spend --unit <id> --seat <role> --agent <id>` reads that seat agent's own transcript and adds its priced reading to the unit's delegated spend in the open run; a later reading of the same transcript replaces the earlier one, which corrects a mistyped seat; the seat word is recorded as given and not checked against the panel; it refuses the builder's own transcript; it writes no verdict row, checks no verdict and records no minutes; it exits 1 recording nothing when the agent has no readable transcript or no run is open.

`evidence` and `sprint-review` are retired: each exits 2 naming `record`, and the old `sdlc-studio/reviews/critic-evidence.md` is read by nothing, so a unit's delivery verdict is the one record of its review. There is no per-unit sign-off: the operator signs the run once with `sprint.py sign --principal`, which refuses a principal who is a unit's author or a reviewer recorded on it. `signoff-record.md` is frozen history that nothing reads or writes.

### `persona_resolve.py`

Resolves the worker amigo for a delegated sub-agent, most-specific-first: a project-authored practitioner amigo (`sdlc-studio/personas/amigos/<seat>.md`), else the skill default (Dani / Sam / Lena), else generic. `resolve` prints the framing the orchestrator appends *after* the contract; `--skip-personas` emits nothing (byte-equivalent generic). The stance never overrides the concrete contract, and the worker is always a separate instance from its reviewer.

The consult surface (used by `refine` and `triage`): `resolve-consult --role <role>` resolves the seat a consult critiques through (review render; a matched project seat missing it is a hard error); `panel --ceremony refine|triage [--question ...]` resolves the whole Three-Amigos panel for a ceremony, lead-first (refine engineering-led, triage QA-led), and names the seats questions go to. `consult()` and `amigo_panel()` are the library entry points refine/triage call; `record_consult()` writes the `> **Consulted:**` line and `## Amigo Consult` section onto the request/Issue as an audit trail (idempotent; a no-op without questions).

### `escape.py`

Traces a bug that escaped to production back to the unit and review that let it through. `trace --bug BGxxxx` reads the bug's `Shipped-in` release and its `Affects`, lists the story and bug ids named in the commits that release's tag holds and the previous tag does not, and proposes those whose `Affects` share a file with the fix, most shared files first, each with the verdict the ledger recorded (its latest APPROVE, else its latest row), the round and the reviewer's seat. It writes nothing. `--confirm UNIT` sets the bug's `Escaped-via` to that unit and stamps the verdict as `Escaped-verdict`, refusing a unit that is not proposed. A bug with no `Shipped-in`, a release that is not a tag, or one whose commits name no unit on disk exits 2 and proposes nothing. A release is read through `release_tag`, the git tag its name means in either spelling (`6.4.0` finds `v6.4.0`). Both creators resolve `--shipped-in` through it, storing the tag's spelling and refusing a version with no tag behind it, and print a note when `--escaped-via` names a unit no commit of that release names, since `--confirm` accepts only a unit the release shipped.

`failure-rate [--since YYYY-MM-DD] [--until YYYY-MM-DD] [--settle-days N] [--format text|json]` derives change failure rate: the releases with at least one linked incident divided by the releases counted, read from `sdlc-studio/reports/releases.jsonl`, the record `release_cut.py changelog-cut` writes. An incident is an issue whose `## Root Cause` section is written (the test applied to an escaped bug), linked to a release through each bug it was triaged into, named in its `Decomposed-into` or naming it as `Parent`, that carries `Escaped: yes` and a `Shipped-in` (`v1.1.0` and `1.1.0` are one release). The window defaults to the 90 days ending today, both days included. A release younger than `--settle-days` (default 14) at the window's end, or today if earlier, is pending and counted neither way, even when an incident names it. It prints the rate (a whole number when exact, else to one decimal) with its count, the window and the settling period, then the releases counted, the failed ones with their incidents and bugs, the pending ones, and any linked bug whose release no record holds, which moves no figure. No release record in the window, every release pending, or no incident recorded prints `not measured:` with the reason and exits 0, never 0%. A record line that does not parse, a record with no `YYYY-MM-DD` date, a release recorded twice, a date flag that does not parse, `--since` after `--until` or a negative `--settle-days` exits 2. It writes nothing. `escape.failure_rate(root, since, until, settle_days)` is the one calculation, for any other script to call rather than compute its own.

### `persona_memory.py`

Keeps each persona's evidenced learnings in a committed file beside its card, `sdlc-studio/personas/memory/<persona>.md`, keyed by a seat's declared role (`qa`) or a user persona's card stem. `add --persona <key> --title ... --body ... --evidence <id>` (or `--fields-file FIELDS.json` for the title and body, stored verbatim) records a learning as proposed, stamped with its evidence, the date, a `Review-by` horizon (`personas.memory.validity_days`, default 90) and an `M-NNNN` id unique across every memory file. It exits 2, writing nothing, on no evidence, a cited id that resolves to nothing (an artefact, a decisions row, a run a report names, or `<unit> r<round>` the review ledger holds), a key that names no persona or names both a seat and a card, and a memory directory an ignore rule keeps out of the repository. `list --persona <key> [--query <text>]` and `recall --persona <key> --query <text>` read that persona's file only, each learning with its state and horizon (`--format json`). A review brief and a `persona_resolve.py` framing carry the seat's live learnings: approved, within the horizon, ranked by shared files then recency, capped at `personas.memory.inject_max` (default 5). The loop is in `reference-persona-learning.md`.

### `persona_review.py`

Holds every persona card (`sdlc-studio/personas/*.md`) and seat card (`sdlc-studio/personas/seats/*.md`) to the persona standard, [best-practices/persona.md](best-practices/persona.md). `check [--card PATH] [--format json]` prints each finding with its rule, `blocks` or `reported`, and the standard heading it checks, from the script's one rule table (`RULES`): the findings of `validate.py personas` and `validate.py seats`, plus `persona-evidence` (an Evidence section citing at least one id that resolves) and `persona-registry-role` (a card's Cast role against `personas/index.md`). It exits 1 when any finding blocks, 0 otherwise, and 2 when `--card` names no persona or seat card. `validate.py seats` and `validate.py personas` print `blocks resolve` beside a blocking rule, read from the same table. Other scripts call `persona_review.check(root, card=None)`, which returns the findings as dicts. `check` is read-only.

`brief --card PATH --seat ROLE` briefs a seat other than the card's own to review the card: the seat card to adopt, the standard page, the card, each finding `check` reports for it with its severity, and the `record` command. It exits 2, printing no brief, for the card's own seat (a seat never reviews its own card) or a seat no card fills. `record --card PATH --outcome pass|fail --reviewer "Name (role)" [--run-by NAME] [--rule RULE]...` appends one row to `sdlc-studio/reviews/persona-reviews.md` (Card, Hash, Outcome, Reviewer, Seat, Run by, Date, Rules), writing its header on the first record. Hash is `persona_gen.body_hash`, the card without its generation stamp or reviewed marker, so a stamp changes no recorded hash. Seat is the reviewer's first `(role)` group, a role the seat roster holds. Run by is the person who ran the review, defaulting to the repository's `git config user.name`; the row is evidence that they asserted the review, not proof it happened. A PASS on a card still carrying its provisional stamp turns the stamp into the dated reviewed marker `persona_gen.py accept` writes. It exits 2, writing nothing, for a FAIL naming no rule, a rule the standard does not hold, a reviewer naming no `(role)` group or a role no seat card declares, no `--run-by` and no git user name, a `--run-by` that is only a `(role)` group, the card's own seat, or a PASS while a blocking rule still fails on the card.
