# Changelog

All notable changes to SDLC Studio will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [5.0.0] - 2026-08-06

> The `## [5.0.0]` section below was cut on 2026-07-26 by `96597c63` and never tagged;
> roughly 900 commits landed behind it. It is a DRAFT rather than a released section, so
> its body is folded back into Unreleased here and one dated 5.0.0 is cut from the whole.
> Nothing is discarded - the earlier body follows the newer one, in its original order.

### Removed

- **`gate --verify-batch`, a flag that was parsed and read by nothing (US0479).** It was accepted, passed to `run_gate` as `verify_batch`, and consulted nowhere: `--release` implies batching and assigns the verify lane itself, so the option promised a behaviour no invocation of the gate has ever produced. An option that is accepted and ignored is worse than an absent one, because it is chosen. The flag, its dead parameter and every line of documentation naming it are gone, and a repo-only guard asserts no tracked skill file mentions it - alongside a control string that IS present, so a scan that silently matched nothing cannot read as a pass.

### Fixed

- **TSD help example matches the 90% coverage default.** `help/tsd.md`'s Quality Gates example showed unit coverage `>=80%`, contradicting the tool's own default (`config.coverage.unit` is 90, the template renders it, and `reference-tsd.md` sets and justifies 90% throughout). The example now reads `>=90%`, so a reader copying it lands on the recommended target rather than below it.
- **A third independent review judged the repairs and rejected three of them; all three are now closed.** The reviewer named one shape across every rejection: a repair is behaviourally right on the path it was written for, and silently wrong on the path where its helper is absent, broken, or never ran. **BG0413**: the python half of the exit-code contract was well pinned and the SHELL half had no test at all - three hook mutants (read exit 2 again, drop the non-empty-note belt, stop setting `fail=1`) all survived the full 589-test tools suite, one of them committing green while printing `commit BLOCKED`. `tools/tests/test_precommit_scope_collapse_lane.py` now drives the real tracked hook in a hermetic repo and kills all three, and it also pins the promise that a missing or mis-invoked `gate_timing.py` never blocks. **BG0460**: the previous fix traded a guaranteed false negative for a false positive - `close_preflight` has early returns that never call `run_gate`, and "no gate blocker" could not tell that from a clean pass, so the preview stated `ok gate: run by the preflight against the real tree` about a gate that had not run. The preflight now reports `gate_ran`, an unreached or raised gate is `unevaluated`, and three mutants over that flag die. **BG0455**: the new sign-off block fell through to `return True` where every other uncertainty path returns False, so a critic that raised dropped the unit from the stop's refusal - the defect BG0455 was filed to end, reintroduced through its own repair, with the fail-closed mutant surviving the entire 5,669-test suite. It fails closed now, and the "shared" matcher (a third byte-identical copy behind a broad `except`) is replaced by `critic.is_awaiting_signoff`, promoted to a public name so a cross-module caller cannot silently diverge from it.
- **Two independent adversarial reviews rejected seven of the nine units delivered in RUN-01KYX375, and the repairs are the substance of the sprint.** The reviewers worked in isolated worktrees from fresh contexts, applied 25 mutants between them, and every finding below carries an executed reproduction. The headline is a REGRESSION the first delivery introduced: adding `gate` to the derived dry-run step set while unconditionally marking it `unevaluated` made `clean` unreachable, so `close --dry-run` could never report clean and always exited 1 - `dry run CLEAN` became dead code and US0555's whole purpose was gone. The gate's verdict now comes from the preflight that already ran it against the real tree, which is what the criterion asked for and what the original comment (left in place, contradicting the new block) already said. Two of the tests written to hold that unit SURVIVED mutation against the full 5,658-test suite: one asserted `status in {"ok","refuse","unevaluated"}` - the set of every possible status - and the other was satisfied by the digits "10" appearing in an unrelated retro message from a sibling unit in the same commit. Both are repaired and both mutants now die. `_awaits_signoff` failed open twice: it dropped a unit whose two-role bar was fully met out of the stop's refusal (losing real remaining work silently, the one direction its own docstring forbids), and it was inert for every v3 ULID - taking the opposite decision to the provenance fix landed in the same run on the identical question. It now consults the recorded sign-off, treats an unrankable id as past the cutoff, and shares critic's status matcher instead of carrying a third spelling. The provenance backfill mirror had no test at all while the commit message claimed it was covered by a killed mutant; two tests now hold it. Two acceptance criteria were verified by tests that could not fail: BG0372's AC1 asserted only that a column name existed, which was already true at the commit its own history calls "Marked Fixed while delivering nothing", and US0558's AC4 never imported `sprint`, so no change to the close could redden it. Both re-pointed.
- **Six of batch 3's nine guards could not fail on the defect they name, and are rebuilt (independent review of US0452-US0460).** The deterministic parts held: every "derived from the code" claim genuinely reddens when the code moves, and all 38 `Verify:` lines resolve. The PROSE guards were the problem, and the worst was the most embarrassing kind.

  **US0455** asserted the fail-loud contract with `assertRegex(passage, "(fail|abort|non-zero)")` over the WHOLE of personas.md - so the contract sentence could be deleted outright and the suite stayed green on an unrelated "fix failures before tagging". The PRD clause survived being reduced to "the nightly backup must not fail". The module's own docstring claimed to have avoided exactly that. The positive assertion is now a phrase that MEANS the contract and must name `gh` in the SAME located passage, and the graceful denylist covers every phrasing rather than one spelling - `gracefully degrades`, `degrades gracefully IF`, `silently no-ops` and `soft no-op` all walked past it.

  **US0459**'s retraction allowance waved through any LINE containing "no longer", "corrected", "amended" or "falsif" - demonstrated live in three files. Retraction is now scoped by ADJACENCY: the retractor must sit immediately before the phrase, so a word later in the sentence cannot license an assertion. The same adjacency rule replaced the equivalent hole in the availability guard's negation handling.

  **US0456**'s denylist hardcoded a newline mid-phrase, so any markdown reflow re-admitted the claim, and it was case-sensitive - half the denylist was armed against one specific line wrap. It is now whitespace- and case-insensitive with qualifier adjacency, so "Nearly every script..." is accepted and "every script..." is not. And the TSD still DENIED the existence of the sweep it names, three lines above naming it; that sentence is gone and its passage is now covered.

  **US0454**'s timing lane guarded nothing: no `measured:` marker existed anywhere in the repo, and the timing store is gitignored, so arming it would have reddened every fresh clone. Two real markers now ship against the TSD's own recorded suite durations, and an absent measurement is REPORTED rather than failed - "never a pass" is honoured by saying so, not by refusing a commit for lacking a measurement nobody could have taken.

  **US0453** read one syntactic form and skipped five band-shaped claims whose noun was too generic to register. A path-aware form now reads the census from the row's own glob, so all five are held; bands inside fenced examples and URLs are no longer false positives.

  **US0452** could be silenced for a whole file by a BLOCKQUOTED `> **Status:** Archived` line of the kind tsd.md already carries - dropping a live version home and its drift together. Only the document's own top-level status now speaks for it. Its fail-loud path was also asserted only against an injected exception, and the real fallback returned `[]` for an unreadable root; that fail-open is closed.

  Two gaps in the repo's own record of its gates, in a batch about spec truth: `npm run lint` had no `lint:spec-claims` at all, and `AGENTS.md`'s guard table documented neither new checker. Both closed, and the lane test now asserts all three homes rather than one string in the hook.
- **Five of batch 2's nine repairs were defective, two of them stop-ships (independent review of BG0401-BG0414).** BG0404, BG0407 and BG0401's four named guards verified; the rest did not.

  **The sign-off gate was DEADLOCKED (BG0406).** The skip refused a sign-off for any unit at `Review` - which is exactly the state this repo's two-role rule holds a unit in UNTIL that sign-off lands. Only an already-terminal unit could be signed off, inverting the central gate into retrospective paperwork. The rule is now WITHDRAWN DELIVERY, not "not yet terminal": a retracted verification depth, or a status that is neither terminal nor awaiting sign-off. `Review` is explicitly eligible, because that is the whole point of the gate. And the summary line no longer claims work it did not do - a run whose units were all skipped exits non-zero instead of printing "N unit(s) written" with rc 0 over a record holding fewer.

  **The lane brief still tracebacked (BG0405).** The guard went into `lane_dispatch` while the identical unguarded read sat three statements later in `cmd_lane`, so the artefact's own reproduction produced `RunStateError` and issued no brief. The test written for it exercised the LIBRARY function, not the command it names - this project's own recorded scar. Both remaining reads in `cmd_lane` are guarded, and the test runs the command.

  **A wrong path became a DEAD path (BG0402).** `_recorded_clause_verdicts` was changed to require `seat["clauses"]` while `_seat_from_dict` whitelisted four fields and silently stripped it, so no writer in the shipped code could produce one: the goal panel reported UNANSWERED on every close, permanently, and all six new tests asserted over a fixture shape the product cannot write. The writer now carries per-clause answers through, proven end-to-end via the CLI.

  **BG0411's AC1 was false.** `_is_artefact_file` checked only the `.md` extension, so `BG288-repro.md` - the "scratch note" the bug report itself names as sufficient - restored the false green in full. A declared id now resolves against the ARTEFACT INDEX and must live under the declared directory, which is what the Proposed Fix asked for and what no filename can forge.

  **BG0414 blocked on precisely what its docstring promised it never would**: a retro naming no units has nothing to compare, and the close returns 1 at the first failing step, so every such close hard-stopped. A nil result is now reported, not failed.

  **BG0403's second half was untested** - deleting the done-gate blocker's `cause` key survived all 600 sprint tests and the one-CR-per-unit fan-out returned in full.

  Four of the replacement tests were themselves vacuous on first write and were rebuilt - the worst asserted "a unit at Review is eligible" using a BUG, which has no Review status, so it read as "cannot say" and passed however the rule behaved.
- **Every gate the close runs is now recorded, so its cost report is not a fraction of the truth (US0639).** `close_preflight` ran a full gate on every attempt and recorded none of them: the ledger held one close row of 77.6s for a run whose close attempts spanned 21m27s. The pre-flight now appends its own measured row, and the close cost counts every gate that actually ran rather than only the chain's.
- **A pre-flight verdict is never reused by the chain's wider gate (US0639).** The pre-flight scopes conformance to the run's batch; the chain's gate does not. Only a `full` run is reusable now - an allow-list rather than a deny-list, so a third mode added later cannot quietly inherit reusability it never earned.
- **The pre-flight's read-only invariant is stated precisely rather than relaxed (US0639).** It performs no step of the close: no retro scaffolded, no summary regenerated, no verdict recorded. Its one write is a measurement of work already done, and the test asserts every other path in the tree is byte-identical while the ledger's delta is exactly one row of the expected shape.
- **The close pre-flight runs the compulsory checklist it is about to be judged on (US0638).** The pre-flight checked run-state, the sprint goal, the goal verdict, review coverage, the retro, the gate and the installed copy - and never the checklist, which is step 6 of the close chain. So a close cleared the pre-flight, ran the chain, and stopped at step 6 on rows that had been readable from the first attempt. One run's attempts read `1, 1, 1, 1, 0` outstanding across six rounds, three of them reporting a single gate item and then dying on the checklist.
- **Asked of the checklist, never restated beside it (US0638).** The pre-flight calls `sprint_report.checklist` and translates its ruling; it decides nothing itself. The test adds a row the pre-flight has never heard of and asserts it is reported, so an implementation that enumerated the known rows would redden. A stop-ship ruling is held separately from an unanswered row, because the remedy is the opposite one.
- **A checklist that cannot be composed is a blocker, not an exception (US0638).** The pre-flight's whole value is one pass, and a resolver that raised would have taken every other blocker with it.
- **`--file-and-close` can file a stale periodic review as the ceremony debt it is.** It
  previously classed that lane a hard correctness blocker and refused, so a close with nine
  independently reviewed, signed-off units could not proceed by ANY route - the plain close
  blocked on the ceremony and the documented bounded exit would not file it. A close with no
  exit is worse than either behaviour alone.
- **A real correctness lane is still refused**, so this does not become a way to file away a
  red gate. The classification is read from the LANE's own declaration rather than a list of
  lane names in the exit - a second list drifts from the first and would silently class
  tomorrow's lane as correctness.
- **Every Progressive Loading Guide cell that presents a path is now resolved, and five of them named files that were not there (US0486).** The existing link passes match `[text](file.md#anchor)`, so they were blind to a BARE cell and to any non-markdown path - which is how five cells shipped naming `modules/trd/c4-diagrams.md` while the tree holds `templates/modules/trd/c4-diagrams.md`. A remembered prefix the tree does not use is the `path-from-memory` class the process pack names, sitting in the guide that tells a reader what to load.

  126 of the guide's 150 cells now name a checked path: 29 anchored (still checked for file AND anchor) and 97 bare. Templated forms, script invocations and prose are classified OUT explicitly, so an exemption is a decision on the page rather than a pattern that quietly matched nothing.

  **The checker's first cut demonstrated the very defect it exists to catch.** It located the section with `find("Progressive Loading Guide")`, which matched a sentence in the intro rather than the heading - so the block ended at the next heading, the sweep read ZERO cells, and it reported clean. A renamed heading and an emptied table now each raise, and both have their own fixture because they are different states.

  **Not applicable is distinguished from absent by accident.** A root with no `SKILL.md`, or one with no guide section, is a no-op, because a consuming project need not have the section and this binary runs against theirs. A test pins that THIS repository has the heading, so a rename here reddens rather than becoming silently not-applicable.

  AC2 said 30 anchored cells; the measured figure is **29**, and the test pins the measurement rather than the claim.
- **A freshly minted epic was born drifted, and the shipped template taught a column set nothing writes (US0478).** Two definitions of an epic row existed and neither knew about the other: `templates/indexes/epic.md` declared `| ID | Title | Status | Owner | Stories | Target |`, this repository's live index declares `| ID | Title | Status | Stories | Deps | Created | Updated |`, and `row_from_header` had a branch for none of those four - so every mint filled them with `--`. Both mint paths now pass the derived cells through `row_from_header`, so a new epic's row equals what the derivation would write (`Stories` a censused `0`, `Deps` left not-stated), and the template declares the canonical columns, with a test comparing the two without restating either as a literal. Wiring a story to an epic also refreshes that epic's `Stories` cell on **both** paths - single and `new_batch` - because minting a story changes a number in another artefact's row, and leaving it to the next `reconcile` means the index is stale from the moment the story lands. The batch path is asserted separately: it is the one that skipped the wiring.
- **RFC-0009's partial supersession by RFC-0038 is recorded on BOTH sides (US0476).** RFC-0038 declared what it superseded and the superseded RFC said nothing, so a reader arriving at RFC-0009 saw `Accepted` and no hint that two of its rows had been replaced. A one-sided record is worse than none, because it reads as settled. Five elements now carry it: the status token, a `Partially superseded by:` header linking RFC-0038, the `D5` and `WS3` rows each marked on their own line, the index Title-cell note, and RFC-0038's own declaration naming RFC-0009 back.

  **The story's AC cited a convention that did not exist.** It said the index note should follow "the shape RFC0034's row already uses" - and RFC-0034's row carried no note at all, while RFC-0038 declared it superseded RFC-0034's D1 and D5. That is the same one-sided record, one row over, so the convention is established here and applied to both rows rather than to the single instance in the story's title.

  The sweep is DERIVED from RFC-0038's own declaration, so every RFC it partly supersedes is held to having an index note. The decision ids are parsed out of the header prose rather than hard-coded, so naming a sixth id without marking its row reddens the test instead of passing by agreeing with itself.
- **Every audit lens names a detector that resolves, and the column is read by name rather than by position (US0464).** `readiness.py` read the signature as `cells[4]`, so a pack carrying Signature as its fourth column - which is now three of the five - yielded an empty signature, and an empty signature parses as not-mechanical: a real detector read as a declared absence. `drawn_from` and `signature` resolve by header name, and the packs deliberately ship at three widths so the shipped corpus exercises it rather than only a fixture.

  **The detector set covers the runners a project can actually name**, not just `python3`: `bash`, `npm run <script>` and `rg` too. A bare `npm` is refused, because `npm` alone runs nothing. Each shape names its target differently and one rule cannot serve them - `python3 <path>` and `bash <path>` name it first, `rg <pattern> [path...]` names it last after a pattern that may be quoted. Signatures are split as a shell splits them, so a quoted pattern stays one token.

  **A shipped detector resolves against the INSTALLED SKILL, not the audited root.** This was the defect that mattered: resolving everything against the root meant all eight mechanical signatures were refused in any project but this one, and the whole argument for putting the contract in shipped code is the consuming project. A path under `.claude/skills/sdlc-studio/` now resolves wherever the skill lives, and the shipped packs validate clean from a foreign root. Two detectors that could never travel were replaced: `bash tools/check_action_pins.sh` and `npm run lint:budgets` named this repository's own files.

  **A target no finder could run is refused by shape, not merely by existence.** An absolute path resolved on the machine that wrote it and nowhere else - the detector-from-memory case the check exists for, passing the check. So were a `..` escape, a directory where an interpreter needs a file, and a shell pipeline whose later stages nothing resolved. A search may still target a directory tree, because that is what a search does.

  **A literal `|` in a table cell is honoured as markdown's `\|` escape.** Splitting on every pipe tore a cell in half whenever its content needed one, so an `rg` alternation became a fragment and was then refused for naming no target - the pattern was fine and the parser was eating it.

  **`manual` needs a reason, and a length floor alone was not one.** `manual - xxxxxxxxxxxxxxxxxxxx` cleared twenty characters while stating nothing, so distinct words are required too, and a placeholder is refused however long it is. The reason is measured WITHOUT the `manual` token, so the documented token does not pay for the substance it introduces.

  **The contract runs in the gate, as the `lens-signatures` lane**, in both `npm run lint` and the pre-commit hook, and is reachable as `readiness.py profile --validate`. A rule enforced only in this repository's unit tests is enforced nowhere for the consuming projects `reference-audit.md#audit-extend` invites to append rows - which now states what a signature must satisfy, rather than being cited for a requirement it never made.

  Fifteen signatures were authored across `code`, `repo`, `skill` and `test`, which carried none: five name a real detector and ten declare `manual` with a reason. The shipped secret scan was widened after it was shown to match only identifiers beginning `secret` - it found nothing in the tree and would have missed `api_key`, `password` and `token`.
- **The porting doctrine is stated in ONE direction, and it is the direction the tooling implements (US0460).** The TRD's Deployment Topology and Environment Strategy passages and the personas.md Skill Maintainer card all said the installed copy at `~/.claude/skills/sdlc-studio/` was the source of production fixes and that this repo back-ported from it. `tools/forward-port.sh` has always said the opposite - `SRC` is the repo tree and the target defaults to the installed copy - and the operator confirmed the script. **The repo is the source; the installed copy is a derived mirror**, and the mirror is a deployment step rather than an upstream: it is what every other project on this machine loads, so a fix that has not been mirrored is in force nowhere. Both documents now say that and name `forward-port.sh --check` as the drift gate.

  The guard derives the direction FROM THE SCRIPT, so swapping `SRC` and the target reddens it instead of leaving two documents unchallenged. The inverted wording is held to an ABSENCE rule over each whole block, not a majority rule, so a repair cannot go green by adding one correct sentence above four inverted ones - and a positive control proves the rule can fail, because an extractor returning nothing would satisfy every absence assertion in the file.

  Two stale facts beside it: five bare router line counts (`~195` in personas, `~260` in the TRD, against a real 270) are replaced by the 500-line ceiling and the name of the checker that enforces it, so there is one number with one owner rather than a figure that rots on every router edit; and the claim that only the scripts carry unit tests is now refused while the repo's own `tools/` suite exists, gated on that suite's existence rather than on someone noticing.
- **The falsified token-observation premise is replaced by the measured one, everywhere it was asserted (US0459).** Nine live files stated that a script cannot observe token spend. `lib/run_state.py`'s `session_tokens` falsifies it: it reads the harness-tracked total straight out of the transcript. The surviving limit is narrower and is now what the documents say - the measured total is a **lower bound**, because `delegated_total` is SUPPLIED rather than observed and sidechain spend is invisible, so a breaker fired on it would halt on a number the actor it constrains can under-report. The D0020 decision STANDS on that corrected reason; the row records the amendment rather than being quietly rewritten.

  The guard derives the ban FROM THE CODE. If the measurement were ever removed the old claim would become permissible again, rather than staying banned by a sentence in a test - proven by a mutant that stops `session_tokens` measuring and reddens the guard.

  It also needed a rule that was not obvious: **a quotation marked as retracted is allowed; an unmarked assertion is not.** An amendment has to be able to say what it corrected, and a rule banning the phrase outright would force a decision record to hide its own superseded rationale to make a guard green. Immutable history - the changelog, closed change requests, handoffs, retros - is allowlisted for the same reason.
- **The TRD's shipped-surface enumerations are DERIVED from the code, not restated from memory (US0458).** Four lists had drifted from what they describe. The command-surface type list omitted nine of the router's types - including `migrate`, which section 6 simultaneously said the router carried, so the document answered one question two ways. The gate-tier passage named 14 lanes against a registry of 17, leaving `window`, `batch-size` and `changelog-fragments` absent from the document that claims to enumerate them. Both drift-kind passages named the same stale five against a tuple of 17. Each list now cites the shipped definition (`gate.DEFAULT_CHECKS`, `reconcile.DRIFT_KINDS`, the router's own Type Reference table) and is held to it, so adding a lane or a drift kind without a TRD edit reddens the guard.

  A caveat also described closed work as outstanding: "the `count-mismatch` finding does not yet meet this bar; closing it is CR0132". CR0132 is Complete. The denylist that removes the sentence is JUSTIFIED by the backlog rather than asserted - the guard resolves the id and reads its status, so the sentence is only refused while the work behind it is genuinely done, and an id that resolves nowhere fails loud with the id named rather than being skipped as clean.

  Every block is extracted by its own heading and a renamed heading FAILS: an extractor returning nothing would satisfy every set comparison in the file, because every set is a superset of the empty set.
- **ADR-011 states the breakdown gate's REAL firing rule, and carries its amendment (US0457).** The ADR read as an unconditional refusal - with any ungroomed unit, `sprint plan` exits non-zero and prints no plan at all - while the code had already been made goal-aware by D0062 and exempted one rung. A reader deciding whether to groom before planning got the wrong answer from the document, and the `Status: Accepted` line carried no sign the decision had been qualified at all.

  The ADR now records the amendment with its date and decision id, states that `design` is the only exemption, and states the fail-safe direction the function's own docstring commits to: an ABSENT, EMPTY or unknown goal BLOCKS, so the escape cannot open merely because the rung could not be read. The exempt set is declared in a machine-readable marker and compared EXACTLY against `sprint._ungroomed_blocks_at`, so exempting a second rung in the code reddens the guard - the first version searched the prose for a backticked rung name and passed however the gate behaved, because every rung is named somewhere in the paragraph.

  The Consequences now name the counterweight the close really emits: a design rung's close renders `grooming_report` through `render_grooming_report`, stating how many units the rung actually groomed. Unwiring that call reddens the guard, because an exemption with no report behind it is an exemption nobody audits. The TRD Revision History cites D0062 with a date no earlier than the decision's, and a decisions log from which D0062 has been removed fails naming the row it could not resolve.
- **One availability contract, stated the same way everywhere and derived from the code (US0455).** Four passages answered one question and three of them were wrong. `github_sync.gh()` raises when `gh` is off PATH and the entry point returns 127 - it FAILS LOUD. The PRD's Availability clause, ADR-004's first Positive consequence and the personas capability list all said sync "degrades gracefully when `gh` is absent"; only the TSD's NFR row had it right. A caller reading any of the three would have expected a silent no-op and mistaken an unsynced workspace for a synced one.

  All four now state the shipped contract: with `gh` absent the sync aborts non-zero, names the missing CLI, and callers handle that exit. Graceful degradation is deliberately not implemented, and the rewording is traceable to D0071 rather than to an editorial choice - the guard resolves that decision row and reads which branch it took, so a passage cannot be quietly reworded without a ruling behind it.

  The verdict is COMPUTED from the observed exit code with `gh` monkeypatched off PATH, so removing the abort would permit the graceful wording again rather than leaving it banned by a sentence in a test. The rule is a pure function over passage text, proven to fail on the exact defect rather than only to pass on the repaired tree - and ADR-004 is extracted by its own heading, because a correct sentence anywhere in the TRD would otherwise satisfy it.
- **`sprint close --apply-signoff` derives parent requests, not only epics (US0445, CR0422).** After the fan-out marks a batch's epics terminal, the close tail now also derives any parent CR/RFC whose children are all resolved to its successful terminal (Complete for a CR), naming each in the close output. It asks the same all-children-terminal predicate the request terminal gate enforces and goes through `transition` (index, cascade, telemetry), so a delivered request is no longer left for a manual `reconcile apply`. Safe and idempotent on a batch with no parent request.
- **The sprint close's review-currency lane judges the review RECORD, not only the anchor's commit time (US0436, EP0162).** `_review_current` dated `reviews/LATEST.md` by its last commit, so a review that ran but re-stamped the anchor byte-identically kept its old commit time (git saw no change) and read STALE - the remedy printed, "run `review`", was the thing just done, and only a substantive edit to an already-correct anchor cleared it. An artefact is now stale only when the anchor commit-time AND the review record (`.local/review-state.json`'s `last_reviewed`, which `review_prep.staleness` already reads) both say so: the record can make an already-reviewed artefact current, but never a genuinely-changed one, and an absent record falls back to the commit-time behaviour unchanged. The close lane and `review_prep.staleness` no longer give opposite verdicts on identical state, and `reference-sprint.md` states the invariant: a close never requires an edit that invalidates a lane it has already passed.
- **A sprint close scopes conformance to its batch, so out-of-batch debt no longer blocks an in-batch close (US0434, EP0162).** On a clean tree the conformance lane has no diff to narrow to, so it judged the WHOLE workspace: a fully delivered batch could be held open by a different author's unit in a different epic, and the only ways past were to force a false Done or grandfather the debt past `conformance.adopt_after`. `detect_conformance` now takes an explicit `scope_ids`; when the close passes its run's batch through `run_gate(conformance_scope=...)`, the per-unit ledger charges only the units the close owns, while the repo-global stages stay at full strength so scoping can never hide a repo-wide failure. A `--release` run is unaffected - a tag is still judged on everything.
- **Nine guards that failed silently, found by an independent review of RUN-01KYNKDP.** Every
  one answered a safety question in the unsafe direction and said nothing: `release_cut`'s
  close-owed check swallowed every error, so deleting one tracked file disarmed the only live
  release guard; a well-formed but WRONG declared gate id narrowed the tree to nothing, a false
  green from a typo; declaring a FILE walked past the content-read floor; `structural=None`, the
  documented "unanswered question runs the suites", answered `no`; `file_finding`'s
  `_land_unhomed` interpolated raw prose, so a finding's `steps` could forge a metadata line, and
  its heading test read the whole body so a finding merely MENTIONING a heading was refused;
  `critic record --units <ghost>` wrote verdicts for ids that do not exist at exit 0;
  `_killing_test` matched unittest's own `FAILED (failures=2)` footer, attributing every kill to
  a fabricated node; and the mutation run's pipe tied the read to EOF, so a suite backgrounding
  anything blocked the full timeout per mutant and `survived` flipped to `error`.

<!-- section: Removed -->
- **US0553 is REVERTED, not repaired.** It recorded a full-suite green on the premise that
  `sprint close` runs the suites at step 4 of seven. It does not - `gate.main` runs seventeen
  lanes and none runs a suite; the suites are run by the commit hook. So the close stamped a
  green over whatever sat in the working tree and the next commit skipped its tests: a false
  green written by the mechanism built to refuse false greens. A test now asserts the PREMISE, so
  if a gate lane ever genuinely runs the suites the decision can be revisited on evidence rather
  than on belief.
- **A skipped test no longer stamps an acceptance criterion green (BG0317).** An all-skipped `pytest` run exits 0 without printing "no tests ran", so the default verify path recorded a pass from a test that never executed - while the batch path, reading the same run, correctly refused it. The default path now treats a run whose counts are entirely skipped as vacuous and not a pass, with its own remedy line. The equivalent hole in the unittest, jest, vitest and go runners is filed as BG0348.
- **Seven tools no longer report success they did not achieve (BG0321-BG0326, BG0329).** A `gh` failure read as "no merged PRs"; a crashed cross-epic checker read as "every unit ready"; a dangling symlink reported "synced"; an unreadable artefact reported clean, and the gate lane that consumed that verdict ignored the blocking flag; a failed remote query silently minted an id already in use; a deleted suite-read file dropped out of the test-relevance measurement; an origin-drift pre-flight reported clean when the fetch itself failed, and now words a failed fetch and a failed comparison separately because only one of them is cleared by `--no-fetch`; and an eval scenario printed "gate pass" while a behaviour it forbade was never graded at all.
- **Unfilled scaffolds are visible wherever they sit in an artefact (BG0304).** The placeholder sweep read metadata and the acceptance-criteria section only, so the `**As a** {{role}}` block every story is minted with was invisible and 39 reached Done carrying it. The sweep now covers the whole body outside fenced blocks. It immediately found 62 findings across 31 already-terminal artefacts, including 12 bugs with no symptom, steps or fix recorded at all; those are held in a baseline recorded per FINDING rather than per artefact, so a new blank in an old record still fails, and are filed for backfill as BG0347.
- **An illustration inside a fenced block can no longer become a live shell verifier (BG0305).** `parse_story` tracked fences with a rule that treated any three-character run as a closer, and then with one that still accepted a closer carrying an info string. Both released the block early, so a `- **Verify:**` line shown as an example in documentation was parsed as a real verifier and executed by `verify_ac run` and the release lane. Fence tracking now lives in one shared CommonMark implementation (`sdlc_md.fence_step`) that both the acceptance-criteria parser and the placeholder sweep call: a block closes only on the same marker at the opening length or longer, followed by nothing but spaces. The mirror harm is closed too - a genuine Verify line after a real closer is no longer swallowed.
- **Three gates that stood down quietly now refuse (BG0314, BG0315, BG0316).** An acceptance criterion with no `Verify:` line at all reached Done, so omitting a verifier was cheaper than declaring an honest manual one - and a `**Verified:**` marker did not rescue it either, because the release lane counts a bare criterion unspecified whatever sits beneath it; both gates now reach the same verdict on the same file, with a differential test pinning that. `--force` claimed the bypass was "recorded as an override" and recorded nothing; it now writes a `Forced-override` field. A one-call close now pre-flights before it writes, so a refused close leaves no stamp and no verdict row.
- **Gate-hardening sprint - repairs from the closing review (EP0164).** The manual-AC Done gate now accepts only a passing `**Verified:** yes` marker as evidence: a `no` or `stale` marker blocks like a red verifier, closing a re-opened bypass where any marker satisfied the gate. The close tail's parent-request derivation is scoped to this run's units and the epics it just derived (matching the epic derivation), so a close never sweeps and names unrelated derivable requests.
- **Guided onboarding - robustness repairs from the closing review (EP0163).** `read_onboarding` treats a corrupt or shape-invalid checkpoint as absent instead of raising, so the read-only orientation path (`status`/`hint`) can never crash on a mangled `.local` file and `init guided` self-heals into a fresh checkpoint. The TSD stage's "detected stack" clause is now pinned to brownfield by a regression test (a greenfield directive must not claim a stack).
- **The sprint report and the close cost stopped disagreeing about one ledger (US0639 regression).** US0639 added a fifth execution mode, `preflight`, and `sprint_report._RAN_MODES` was an allow-list that never learned of it: six rows carrying 623.2 measured seconds were reported as "none carries a duration" while `close_cost` read the same six rows and reported 623.2s. Because delivery is derived by subtraction, 600 seconds of measured, attributed gate time was credited to delivery. The rule is now stated as an exclusion - the one mode that ran nothing - so a mode added later counts by default, which is the direction it should fail in (LL0043).
- **A light verdict recorded through `critic.py record` now reaches the coverage gate (US0641).** The verb's `--tier` and `--tier-explicit` never reached `record_verdict`, and the failure was fail-open: an unrecorded tier writes the absent marker, coverage reads absent as covered, and the whole tiering gate disarmed silently. Pinned end to end across the module boundary rather than at each half.
- **A historical human sign-off can no longer read as a machine's after migration (US0644).** The Capacity column has a third spelling of absent - the `-` the migration pads with - and only the un-padded one was pinned. `CAPACITY_ABSENT` declares both and `signed_by_seat` is the single predicate every reader asks, so the answer cannot drift between them.
- **The disjointness guard is tested where it is reachable, and each CLI refusal names its own reason (US0643).** The test asserted only a non-zero exit, and two of the three refusals return a byte-identical message because the assigned-signer check fires first - so deleting the guard passed 1,114 tests. AC4 is restated on the artefact: it demanded a distinction the design makes impossible, since the panel assignment holds the signer disjoint from the adversarial seats.
- **The operator summary's cost derivation and carried-findings list are pinned (US0645).** Reducing the whole derivation to four constants passed 124 tests, and a commit carrying exactly that mutant reached `main` and passed the pre-commit gate green. Each field must now track its input, and the carry-forward half of AC3 is exercised with a real filed finding.

<!-- section: Added -->
- **CR0533 - coverage by reversion.** Revert a production hunk, run the unit's verifiers: if the suite stays green, nothing depends on that hunk and the criterion it claims to satisfy is pinned by nothing. Proposed on measurement rather than principle - two independent seats applied 71 mutants of their own devising to a batch whose author had applied 45 self-chosen ones with a 100% kill rate, and 12 survived. Mutation asks whether a test can tell a wrong implementation from a right one, and the author picks the mutants; reversion asks whether it can tell the implementation being there from absent, and the hunks come from the diff.
- **The mutation engine applies a mutant where it enumerated it (BG0533).** `enumerate_mutations` excluded multiline-string interiors when counting occurrences and `mutated_text` re-counted without that exclusion, so a pattern inside a docstring above the real occurrence shifted the ordinal between them: the mutant was REPORTED at one line and APPLIED at another. A verdict attributed to a line the tool did not edit reads exactly like evidence and is evidence about nothing - and a false KILL is a green mutation score for code that was never mutated, on the instrument the whole evidence story leans on. Both readers now resolve through one routine, and `mutated_text` REFUSES outright when the line it would edit is not the line recorded - a check independent of how the anchor is computed, so it holds even if a second counting site returns.
- **`verify_ac run` refuses a unit whose criteria it could not read (BG0530).** It printed `ac=0 pass=0 fail=0`, exit 0 - a line byte-comparable to a clean pass - for **311 of 534 bug files**, and **74% of the BG0500+ era**. Nothing detected the drift because the failure mode was exit 0. Three states are now distinguished because they have different fixes: a section that parses to nothing is REFUSED, criteria that parse with no verifier at all are REFUSED (the shape that would otherwise SURVIVE this fix, and where widening the parser moves the unreadable ones), and no section at all is REPORTED, since 232 filed findings never claimed a verifier and nothing else in the tree refuses them.
<!-- section: Added -->
- **`verify_ac corpus-scan` (BG0530).** The three blind states counted by shipped code rather than a throwaway script, so the before and after figures of any fix come from the same routine. Today: 534 bug files - 191 readable and verifier-bearing, 75 unreadable, 36 parsed with no verifier, 232 with no section.
- **The writer emits the shape the parser reads (BG0530).** `file_finding.py` wrote criteria as bare `- [ ] <prose>` bullets carrying no `ACn` marker, which `sdlc_md.AC_BULLET_RE` cannot match - so the module that WRITES a bug's criteria and the module that EXECUTES them disagreed for 400 bugs, undetected, because the failure mode was exit 0. Pinned by a fixture built by CALLING the filer rather than by a hand-written example that happens to match.
- **The release verify lane states its scope (BG0530).** It walks `sdlc-studio/stories` only, so no bug's acceptance criteria has entered the release gate in any version - 534 files, 55% of the delivery corpus, silently outside a pass reported on "the AC layer". It now names the count it did not walk, derived from the tree so the number moves when the scope does.
- **The one-run-slot gate no longer stands down a step early (BG0527).** `run_state._is_spent` treated a recorded `sprint_goal_verdict` as proof a run was history, but the goal verdict is written BEFORE the close chain rather than by it - so every run passed through a window in which its outcome still said `running`, its units were still at Review, and the guard protecting its close had already released the slot. `_CLOSE_ARTEFACTS` now holds only what the close itself writes.
- **BG0188's property, under a better remedy (BG0527).** BG0188 established that a new batch must not be accumulated onto a judged run, and minted a fresh run instead; that silently discarded the owed close and stranded the judged run's units. The slot is now REFUSED with the run named, which keeps BG0188's two harms out - the batch is not accumulated and the verdict is not clobbered - without introducing a third.
- **A judged batch is frozen, including against an overlapping re-plan (BG0527).** Removing `sprint_goal_verdict` from `_CLOSE_ARTEFACTS` shut the disjoint door and opened the overlapping one: a re-plan sharing a unit accumulated onto the batch the goal verdict had already judged, so the verdict came to describe work it never saw - BG0188's own harm arriving by the other door, previously masked because that path minted a fresh run. An identical re-plan is still a no-op. Found by an independent seat; AC4 is restated on the artefact rather than the guard weakened.
- **A stale warning-ratchet baseline no longer reports `clean` (BG0524).** It printed `clean` whenever nothing was NEW and then contradicted itself on the very next line, listing recorded instances no artefact still carries. The premise was corrected before any code: `validate.py` deliberately does not hold the gate on stale - a repaired instance is good news, and refusing the commit that repaired it would teach an author to stop repairing - so the exit code was right and the WORD was wrong. Separately recorded: US0480 AC4's verifier asserts the stale entries and never the exit code, so it passes while the code contradicts the criterion it verifies.
- **`sprint.affects_check: block` now decides something, and decides it before the write (BG0521).** Three defects, one predicate. `plan` printed "advisory - nothing is refused" whatever the mode, so `block` and `warn` were byte-identical while `help/sprint.md` said the setting "decides what a finding does". `batch add` consulted the mode AFTER `add_to_batch`, so the operator was told "refused" about a unit the done-gate could already see - a refusal that was a message rather than a refusal. And `--format json` skipped the check entirely, holding a machine caller to a weaker rule than a human one. All three now ask one reader, `_affects_blocking`, and the refusal happens before the unit is written.
- **The triage session cap is a per-session budget again, not a lifetime one (BG0520).** `_session_key()` returned a constant and nothing in the skill ever set the environment variable it read, so every session in a project's whole life shared one key: the counter climbed monotonically to the cap and stayed there, and filing was then refused permanently on a project that had done nothing wrong. The key is now the explicit variable, then the open run's id, then the date - and there is no fallback to a constant, because a constant is what made this a lifetime cap.
- **The refusal names only exits that work (BG0520).** It offered three and one of them - triage the backlog - decrements nothing, so it was false at the moment it was read, which is the moment an operator has nothing else to go on. The message now names the key in force so the reader can see what has to move, and says plainly that raising the cap moves the wall rather than removing it.
- **`close_owed detect` no longer announces a debt it has already discharged (BG0518).** The exit code was computed from `unaccounted` and the headline from `owed` - two readers of one question. `owed` deliberately keeps every uncovered terminal unit, including those a recorded `Close-repair-override` fully accounts for, because visible and countable is the point of an override. So on a fully-overridden set the first line read `a sprint close is owed (run the retro, then gate --require-retro RETROxxxx)` while the process exited 0. A gate branching on the code was right; every human and agent reading the line was told the opposite, and pointed at work that was not owed and could not honestly be done - there is no batch left for that retro to account for. Both now derive from one predicate, `is_owed`, so they cannot drift apart again. When everything is accounted for the headline says so and names no discharge command, and the units are still listed below with the reason each carries.
- **The agreement is pinned as a property across all three states (BG0518).** Overridden, close-time-repair-only, and genuinely unaccounted: for each, the test asserts that the headline's claim and the verdict match, so a future branch that reports a debt without holding the exit code fails here rather than in somebody's session. The shipped command is driven too, not only the library functions - a library test is not a lane test (LL0040) - and its exit code is read as a return value rather than through a pipe. Writing the controls first was load-bearing: the obvious control, "the same fixture without an override", turned out not to be an unaccounted unit at all but a close-time repair, which by CR0527 is reported and deliberately does not hold the exit code.
- The close-loop cap no longer stops a loop that has already converged. `loop_termination`
  tested the attempt count before it looked at what the attempts contained, so a run whose
  latest round reported zero outstanding - every blocker cleared, the next round certain to
  complete - was told to hand off with an outstanding set that was empty, and raising the cap
  only moved the number at which a finished loop was refused. Convergence is read from the
  latest round only: a loop that cleared its work and then broke it again still stops, and the
  divergence detector is untouched.
- **The close attributes a refusal the gate named (BG0516).** `_GATE_FAIL_RE` required the colon immediately after the lane name while `gate.py` prints `[FAIL] {check}{lane_stamp}: {detail}`, inserting `[0.4s]` before it - so EVERY timed lane was dropped, which is all of them in a real run. The close then reported "the refusal could not be attributed" one line after the gate had named the failing lane plainly, and burned its rounds retrying until the loop guard quarantined the run. The parser is now pinned to the renderer by a test that builds its input with `gate.lane_stamp` rather than typing a literal, so the next change to the lane format cannot break the close silently. `[FAIL]` stays anchored: a pattern widened to any bracketed word reports an advisory lane as a failure.
- **An unattributable blocker names what it saw (BG0516).** "I could not attribute this" and "nothing was found" are different facts, and reporting the second sends the reader to the wrong place. Any `[FAIL]`-shaped line the parser cannot place is now quoted, so a lane whose format moved is visible rather than silent.
- **The charter queue has an exit (BG0515).** `Spent` shipped in the charter vocabulary and in the versioned schema contract with no code path setting it, so a charter stayed Queued forever and re-materialised at the head of every later `sprint next`. An operator who had already run it could only cancel, which records a withdrawal - a different and misleading fact. `sprint plan --write --charter <id>` now marks it Spent as part of opening the run.
- **One writer, and the choice is recorded (BG0515).** Opening a run is what spends a charter, and `plan --write` is the one command that opens one, so the transition lives there rather than in `next`. A second writer in `next` would give the lifecycle two places that could disagree about whether a charter was consumed. The status write goes through `transition`'s own entry point, so the charter index is synced by the same code that syncs every other index rather than by a private second path.
- **A charter that is not Queued is left alone, and the run says so (BG0515).** Re-spending a Withdrawn charter would rewrite a decision somebody made. The run is already open by the time this runs, so an unspendable charter is REPORTED rather than failing the run - and the test asserting it is what kills the mutant that re-spends anything named.
- **`sprint queue show` is readable during a run, which is when it is used (BG0514).** It delegated to the materialiser, which refuses first on the single-run-slot rule - so with a run open, the one moment the queue exists to be inspected, it reported that nothing was runnable instead of what the head charter would select, and suppressed the charter's goal review with it because both sat inside the same success branch. The resolution is now its own function and the slot guard stays where it belongs, on `sprint next`, which WRITES: merging a charter's batch into an open run would make that run's approved batch a set nobody approved. Showing what a charter would select cannot open anything, so the read no longer inherits the write's precondition.
- **The regression test has a run OPEN, which is the condition the original criterion lacked (BG0514).** US0489's verifier passed over this defect for a whole unit because its fixture had no open run - the state the command is for. The new tests hold both directions: `queue show` resolves with a run open, `next` is still refused with one, and `next` still resolves without one. Read-only is asserted as a byte census over every file in the tree, so a status rewritten in place is caught as well as a file created - the split rests on that read being a read.
- **A red suite leg now names the test that failed, and keeps its own log (BG0513).** `tools/run-suite.sh` captured every run's full output to a `mktemp` file and removed it on an EXIT trap, sending only `tail -25` to stderr. unittest prints its `FAIL:` headers well above the closing `FAILED (failures=1)` line, so the tail carried the COUNT and never the NAME - which is why an intermittent red in the full runner went unnamed across five invocations, the evidence captured and destroyed on each one. Failing test names (both runners: unittest's `FAIL:`/`ERROR:` headers and pytest's `FAILED` short-summary lines) are now printed before the tail, and the full output is kept under `sdlc-studio/.local/suite-logs/` with its path recorded as the verdict's new `log` field. The log is per-RUN rather than one rolling file, because a rolling log belongs to whichever run wrote last and the moment you read it is precisely the moment a later run has already happened; ten are kept. It lives under `.local/`, which `tree_state` drops from its index, so preserving it cannot move the tree hash the verdict binds to. Delivered NARROWED - see BG0519 for the residue.
- **The scrub-site sweep no longer walks the worktree scratch it throws away (BG0513).** `ScrubSiteSweepTests._sites` post-filtered `REPO.rglob("*")`, so an excluded directory was descended into and discarded afterwards: measured on this repo that walked 112,025 paths to keep 3,377, with `.claude/worktrees/` - whole checkout copies left behind by parallel delivery - making up 90% of the walk. Three tests call it, so the cost was paid three times per run and grew with whatever the skill leg had left behind, which is the direction that makes the tools leg slower inside the full runner than alone. The walk now prunes excluded directories instead of filtering them, asking the existing `_skipped` predicate so the exclusion rule keeps one definition rather than two that drift. `_sites` drops from ~2.15s to 0.05s per call. A prune and a post-filter return the same files, so the test asserts on what was VISITED rather than on the result.
- The ungroomed census now covers every unit type, not stories alone. `sprint breakdown` and
  `sprint plan` asked `conformance.story_is_ungroomed` only of stories, so a bug with no
  acceptance criteria at all - the state `transition` refuses outright - was certified groomed,
  as was one whose every criterion was the text `file_finding` derives from the finding's own
  prose. A 17-unit batch reported `0 ungroomed` while 33 of its 58 points could not reach a
  terminal status. Over the live backlog the same census now reports 16 of 48 units ungroomed,
  each named with which of the three shapes it is in (`no-criteria`, `placeholder`,
  `derived-only`) because each has a different fix. The "has criteria" question is answered by
  the same `validate._has_criteria` the transition gate consults, and the derived-criterion
  shapes are read from `file_finding`'s own form table rather than copied, so neither pair can
  drift into disagreeing.
- **A plan-review verdict records WHICH pre-code artefact it judged (BG0510).** It was keyed by unit and phase alone, which is sound while only one kind of plan review exists and stops being sound the moment a second one does: one approval would discharge both gates and neither reviewer would have read the other's artefact. Found while planning EP0207, whose proposed test-plan gate read "an APPROVE row in plan-review-verdicts.md" - satisfied by a design-plan approval with no test plan ever written. Nothing in the tree was wrong; the ledger's shape made the mistake the default for the next author.
- **The one live gate asks for its own kind (BG0510).** `plan_review.gate` requests `spec`, so the column is load-bearing rather than decorative. An unknown kind is refused at write time, because a misspelt value creates a gate that can never be satisfied and that nobody can see; a kind on the delivery phase is refused too, since a delivery verdict judges the diff.
- **The legacy table is padded, never rewritten (BG0510).** Every recorded cell keeps its value and its position and the added cell reads `spec` - a fact about those rows, since only one kind was ever reviewed, and what keeps every historical approval counting.
- **A collapsed suite no longer leaves a reusable green verdict behind (BG0507).** The `commit-msg` hook wrote the suite verdict as soon as both lanes passed, and only afterwards ran the scope check that sets `fail=1` when the suite COLLAPSES - far fewer tests run than the surface demands. So a collapsed run blocked the commit and still left `status green` at that HEAD; because `pre-commit` skips the suites when a current green verdict covers the surface, the byte-identical retry landed the collapsed suite having run no tests at all. This is the third door into the same fail-open, after BG0423 (written unconditionally) and BG0489 (written between the lanes). The write now sits below everything that can still set `fail`, and the rule to keep is that the verdict is the LAST thing a passing hook does.
- **The rule is now pinned as a property, not as its third instance (BG0507).** Three findings, one shape: something could still set `fail` after the verdict was on disk. Alongside the executing test for the collapse door, a structural check asserts that no `fail=1` assignment appears below the verdict write at all - so door four fails when it is written rather than when it is exploited (LL0043). The collapse itself is pinned by EXECUTING the hook against a fixture whose `gate_timing.py scope` exits 3, because both prior repairs were green under a source-order grep; the fixture asserts both lanes passed, which is what makes it the third door rather than a restatement of BG0489. The retry half of the claim is closed at the other end too: with no verdict recorded, `gate.py --suite-decision` answers `run - no readable suite verdict is recorded`, against `skip` when one is present.
- A repeated single-valued metadata field is now an error, naming the field and every line it
  appears on. `extract_field` searches, so a repeated `> **Name:** value` was read first-wins
  while `transition` rewrote only the first on a correction - leaving a losing line that still
  read as live metadata to a human and could contradict the gate. The fields that may repeat
  are declared in `sdlc_md.PLURAL_FIELDS` rather than inferred from the corpus, so `Parent`
  stays plural by design and a wrongly repeated field cannot make itself exempt.
- **The claim-drift lane no longer fires on every criterion verified by a `unittest -p` pattern (BG0505).** `_SURFACE_RE` matches a bare filename as readily as a path, and `touched` holds repo-relative paths, so the old `any(s in touched ...)` membership test could never match one. Since `-p` takes a pattern rather than a path, the shipped way to name a Python test was precisely the form that could not pass - a guaranteed false positive, and it reported BG0504's own criterion over a file the same diff changed by 76 lines. Surfaces are now compared through `_names_a_touched_file`: a name carrying a separator still compares as a path, and only a bare name falls back to matching basenames, so `scripts/gate.py` is never satisfied by a change to `tools/gate.py`. The lane ships advisory expressly so its yield can be measured before it is allowed to block, which is why a systematic false positive mattered: it inflated the very number that decision reads.
- **Archiving an index no longer reddens the repo guards that read it (BG0504).** `reconcile detect` advises archiving once a live index passes `indexes.archive_after`, and taking that advice broke seven checks under `tools/tests/`. `test_epic_index_derived` and `test_supersession_records` both read `sdlc-studio/<type>/_index.md` with a bare `read_text` and treated it as the whole corpus, so moving 177 epic rows and 55 RFC rows to `archive/v5.0.0/` dropped the epic sweep from 207 rows to 30 - under floors of `> 150` and `> 100` that exist to prove the sweep is not silently matching nothing - and left RFC-0009's and RFC-0034's supersession notes reported as missing while they sat intact one file over. Both guards now read the live index unioned with its `archive/**` sub-indexes, the same union `reconcile.parse_index` has always performed and for the same stated reason. The uncorroborated-row check is split to match: its advisory half is compared against the live table (the one `apply` rewrites, and so the detector's real scope), while the six recorded counts are pinned over the whole corpus, so an archived row that lost its value still fails. A new criterion asserts the sweep finds rows the live table does not hold, which is the mutant the class needed - reverting the union kills 5 of the 7 tests. The subjects under test were never wrong: `epic_index_derivable_drift`, `epic_index_uncorroborated_advisory` and `reconcile detect` all returned correct results throughout.
- **`reconcile detect` now reports an epic left live over a finished breakdown (BG0503).** The cascade only ever ticked a box: `transition._cascade_epic` rewrites the story's line in its parent's Story Breakdown and returns, and nothing derived the parent's own Status from its children. So the direction that masks *unfinished* work was caught - `breakdown-ticked-early` exists for exactly that - and the direction that masks *finished* work was caught by nothing. Fifteen of this repository's thirty open epics had every child Done, every box ticked, and still read `Draft`, over a `detect` reporting `drift_items=0`; anything reading the delivery backlog to decide what was left was reading a number overstated by half. The new `epic-status-stale` kind reports it, and is DETECT-ONLY on purpose - closing an epic is a status transition and `transition.py set` is where an epic's gates live, so `reconcile apply` deliberately does not write this one and the fix names the command instead. Silent where the epic asserts nothing: no breakdown, a `Deferred` child, or a declared id resolving to no file, since an unresolved child is unknown rather than finished. The TRD's two drift-kind enumerations name it as well, which its own guard required before the suite would go green - the document cannot answer that question two ways, and the kind that is not in the spec is the kind nobody reviewing the spec knows ships.
- **A close sealed with `--file-and-close` now prints its close report (BG0502).** The report was emitted from `cmd_close`'s success path and the `--apply-signoff` tail, and this route returns before both - so the one exit designed for a close that could NOT complete cleanly was the one that reported least, though it is exactly where the operator most needs an account of what shipped, what is carried and what was deferred. It now reports on that route too, after the filing lines so the report is read in the context of the deferrals rather than before them, with a DEFERRED section naming each filed artefact and marked `(filed, not waived)` - the same distinction the retro and the review anchor carry as `(deferred, not waived)`, repeated where the operator actually reads. The section appears only on a close that deferred something: one reading "none deferred" on every ordinary close trains the eye past it, and this is the line that matters on the one route where it is ever non-empty.
- `batch add-epic` and `batch swap` no longer price stories at zero. They hand-rolled the points
  parse, and the shared reader they were meant to route through could not read the field either:
  `read_points` asked for `Points`, which does not match the `**Story Points:**` spelling 20
  stories in this corpus carry. The reader now knows both spellings, canonical first so a record
  carrying both keeps its meaning, and the callers route through it.
- **The runbook guard runs in the gate people actually run (BG0500).** `tools/runbook.py` enforces the sprint-toolchain runbook's step order, its per-step command coverage and its verb freshness - and it appeared in neither `.githooks/pre-commit` nor `package.json`, so it ran only when the whole tools suite ran. That is LL0027 exactly, and it bit the one document AGENTS.md tells every agent to read before each sprint step: the file most able to rot quietly between suite runs. It is now a pre-commit lane and a member of the `npm run lint` chain, so a contributor without the hooks enabled checks what the hook checks.
- **The repo's written account of its own gates names it (BG0500).** AGENTS.md keeps a roster of pre-commit lanes because a guard nobody has written down is one nobody notices losing; `runbook.py` was missing from it. The tests hold all three halves apart - the hook invokes the guard, the npm chain runs it, and the roster names it - so wiring one and forgetting another reddens rather than passes.
- **Panel escalation now reads both review ledgers, and fires from all three recording commands (BG0499).** A unit's rounds live in two files, and the question "has this stopped converging" spans them: `critic.py record` appends to `critic-verdicts.md`, while `sprint review-batch` and `critic sprint-review` both append batch rows to `sprint-review-record.md`. The escalation was consulted only from `review-batch` and decided from the file the *other* command writes, so two REJECT rounds recorded through the command that owns the escalation escalated nothing, and a panel using `record` alone notified nobody - it fired only in the single combination where somebody used both commands on one unit. A round is now any recorded adversarial verdict naming the unit, from either ledger, read through one function that all three commands call. The first repair wired two of the three and its own prose claimed that was all of them; independent review found `sprint-review` still silent, which is the argument for counting the callers rather than remembering them. A refused `record` escalates nothing, because a refusal writes no round and noise on this channel is what makes an operator stop reading it. The reader is deliberately not folded into `unit_review_rounds`, which feeds `seat_verdicts` and the coverage predicate: those ask which seat holds what verdict on one unit, and a batch row cannot answer that, because its reviewer reviewed a span rather than a seat's slice. The rule itself moved next to the ledgers it judges, with the old name kept as a shim - one rule with two homes is the shape that produced this, and the looser copy is the one that runs.
- A second `class FileAndCloseTests` in `test_sprint.py` shadowed the first, so the ELEVEN tests
  on the earlier class stopped being collected. Python does not complain about a redefinition -
  it replaces the class object - and the suite stayed green with a quietly smaller count.

  The symptom was misread for hours: `US0282` and `US0283` reported `verifier exited 0 but ran
  NO tests`, whose message offers "renamed or deleted test, stale -k pattern" as the diagnosis.
  Every named test was still in the file; the class holding them was not there at runtime.

  The second class is renamed for what it covers, all eleven return and pass, and a new AST
  guard refuses any test module that defines a module-level class name twice - across both suite
  directories, parsed rather than grepped, since a grep cannot tell a definition from a mention.
- `critic.py signoff` counted a SKIPPED unit as written. Over a batch of units in a status that
  is neither terminal nor awaiting the reviewer of record, it printed `14 unit(s) SKIPPED and
  NOT written` on stderr and `14 unit(s) written` on stdout, over a record holding zero rows for
  them. The skip path returns rather than raising, so the batch runner never saw a failure.

  The exit code and the stderr list were already correct, which made it worse rather than
  better: the two lines disagreed in one output, and a reader trusting the headline number was
  told the opposite of what happened. The count is now derived by excluding the skipped set, so
  it is a statement about the record rather than about the loop.
- **The velocity row reports what a sprint WROTE beside what was ACCEPTED (BG0495).** It counted only terminal points, so a run that wrote 148 and had 72 rejected published 76 and read as a slow sprint rather than a rejected one. Status cannot separate the two - a rejected story returns to `Ready`, indistinguishable from one nobody started - so the written figure is drawn from recorded delivery verdicts, which is evidence the diff exists. A unit nobody reviewed is not counted, or `written` would be `planned` renamed.
- **An elapsed span with no recorded idle is labelled a calendar span (BG0495).** One 15.3h interactive run reported `0.0h idle from 0 recorded gap(s)` while containing six nine-minute suite runs and long periods with nobody at the keyboard. Zero gaps is no measurement of idle, not an absence of it, and the gap count now travels with the figure so the row can say which it has.
- **The delivery figure is marked an upper bound, as the ratio beside it was already marked a lower one (BG0495).** Delivery is total minus overhead, so every unattributed minute lands in it. The two qualifiers are derived from one `bound` rather than written beside each other.
- **VELOCITY.md gained a Written column without disturbing a single historical row (BG0495).** Its schema is written out three times - the header, the row writer and the reader - and nothing made them agree; adding the column to the header alone shifted every cell after it, so the estimate column read back the actual. A test now pins that the header and the writer enumerate the same columns.
- A skill-relative `Affects` path no longer resolves to a consuming project's own file of the
  same name. `resolve_affects` nested base outside candidate, so the prefix-stripped candidate
  was tried at the project root before either skill base - a project holding its own
  `templates/core/story.md` therefore won the resolution of the skill's path of that name. The
  stripped candidate is now offered to the skill bases only. A project that genuinely vendors
  the skill still resolves to its vendored copy.
- **A suite verdict now binds to the working tree, and `--check` reads which suite ran (BG0492).** A verdict is necessarily taken at its parent commit, so recording `head_sha` alone authorised every edit made after the suite ran - and an uncommitted working tree is the normal state mid-session. With a green verdict at HEAD, staging a syntactically broken file and claiming "Both suites green." passed. The verdict now carries a `tree_hash` over three inputs, each for a case the others miss: the commit, `git diff HEAD` (staged and unstaged both - the original reproduction stages the file, so reading the unstaged diff alone sees nothing), and the content of untracked files, because a new module is the commonest mid-session change and is untracked until somebody adds it. Ignored files are excluded, and the verdict's own directory on top of that: the verdict is written into the tree it describes, so counting it would make every verdict differ from its own tree the instant it was written, and a guard that refuses always is a guard that gets switched off. Separately, `--check` never read the `suite` field, so a verdict from `run-suite.sh scripts` satisfied a claim about both suites - the exact phrasing the commit-msg lane matches. An unqualified `--check` now means the whole tree and requires `all`; `--check scripts` asserts the narrower thing, and an `all` verdict satisfies it, because coverage is the test rather than equality. A verdict predating the tree binding is refused as unreadable rather than accepted, and a machine with no `sha256sum` or `shasum` is refused rather than waved through, since an unverifiable green is the shape the check exists to remove.
- **The suite verdict's tree digest was inert on this repository, and is now pinned against that shape.** The first repair excluded the verdict's own directory with a `git add -- ':(exclude)<path>'` pathspec. That form FAILS when the path is also gitignored - git refuses with "the following paths are ignored by one of your .gitignore files" - which is precisely this repository's configuration, so the digest came back empty here while all six fixtures passed, none of them ignoring `.local`. The verdict then recorded an empty `tree_hash` and every claim of greenness was refused as unbindable: the fix was inert exactly where it ships. The path is now dropped from the throwaway index instead, which is silent whether it is tracked, untracked or ignored, and a test asserts a NON-EMPTY digest in a fixture that ignores the directory - the assertion the other tests could not make, since they compare digests to each other and two empty strings compare equal.
- **The commit-msg suite verdict is now proven by running the hook, not by grepping it (BG0489).** The code half had already landed: the verdict write sits below both lanes, so a failing `tool-tests` lane leaves nothing behind for a byte-identical retry to reuse. What had not landed was a test that could tell. Every existing guard on this mechanism is a `text.index` over the hook's source, which is why the fail-open survived one repair and then came back in a different position - a grep for `if [ "$fail" -eq 0 ]` was green on both broken shapes. The hook is now executed against a fixture repo whose skill lane passes and whose tool lane is a genuine red unittest module, and the assertion is on the verdict FILE a later commit would read: none written when the tool lane fails, `green` written when it passes. The control case is what stops the refusal being satisfied by a hook that records nothing, and what proves the fixture reaches the lanes at all - reaching them needs the handoff `pre-commit` leaves at `$git_dir/sdlc-gate-suites`, and a test that forgot it would pass vacuously on every mutant.
- `verify_ac lane-check` credited a criterion only when the named test node's own source
  entered the shipped entry point, so a class that shells the CLI once in a `_run` helper and
  calls `self._run(...)` from every method was reported as never entering the lane. That is a
  correct and common shape - it is the shape of this repo's own `SwapTests` - and the detector
  was telling tested work it was untested, including three units from the sprint that shipped
  it. It now resolves ONE level of same-file helper: the functions the scoped node calls are
  read, and entry inside one of them counts.

  One level, not a call graph. Whole-file matching is what made the first version useless,
  reporting 0 findings over 615 units, and a deeper walk restores that permissiveness by
  another route.

  Corpus yield over the same 615 units: **186 -> 167**. The recorded figure in `US0605` is
  restated, since it is the number the decision to let this advisory lane block will rest on.
- No change. `BG0485` recorded two goal-review defects - a seat's `no` read as `partial`, and a
  whole-goal answer fanned across every clause - that commit `e9dd8317` had already fixed four
  days before the bug was filed. Both were reproduced as non-reproducing by driving
  `_recorded_clause_verdicts` against the recorded steps, and both are pinned by existing
  coverage. The unit is closed against that evidence rather than reimplemented.
- **`critic.py brief` now emits the fingerprint it is the only source of.** `brief_fingerprint`
  had exactly one caller - the `--brief-file` branch of `record` - and the command that ISSUES
  a brief never called it. So the value `record` demands could not be obtained from any command
  a reviewer runs, while the shipped paperwork stated that `critic.py brief` emitted it. The
  claim was false when written. Its acceptance test computed the fingerprint in-process, which
  is a library test and cannot see that the lane is missing; the replacement runs the CLI.
- **A `--brief` value is checked to be a fingerprint.** `--brief x` was accepted, so the
  provenance gate was met by inventing a value - recording provenance for a prompt that was
  never issued, which is the exact thing the field exists to make detectable. A value matching
  no brief the repo can currently produce is NOTED rather than refused, because the brief
  embeds the artefact's own state and legitimately moves when the unit is transitioned.
- **The untagged-finding guard in the coverage predicate is pinned.** Deleting it left the
  entire suite green, and every REJECT row in the shipped log carries untagged findings that
  predate the origin axis - so the mutant would have started covering real units at the Done
  gate with nothing going red. The behaviour was correct; the cover was absent.
- **Three docstrings falsified by their own diff are corrected** -
  `critic.sprint_covers_independently`, its restatement in `sprint.py`, and
  `carry_forward.py`'s header - all of which still said coverage requires an APPROVE. The
  claim-drift lane shipped in the sibling epic fired on none of them.
- **The claim-drift lane no longer reads append-only ledgers as prose.** A verdict row records
  a judgement somebody made on a date; it asserts nothing about behaviour, so it cannot be in
  drift with a diff by construction. The lane fired on the verdict log every time a diff
  touched `critic.py`, because every row carries a reviewer id containing the word `critic`.
  Ordinary paperwork in the same diff still fires - excluding ledgers must not become excluding
  the changelog fragments the lane exists for.
- **claim-drift no longer reports what it cannot name, or matches on a digit alone
  (BG0479, BG0481, BG0480, BG0482).** Replayed over the 40 commits ending at `3570c94a` the
  advisory lane produced 215 findings, 135 of them (63%) naming no code at all - printing
  `carries ''` because a hunk whose added lines held no integer made every removed integer
  read as "replaced" by nothing. Two rules now stand between a diff and a finding: there must
  be a real replacement, and the prose must name something the changed code names rather than
  merely sharing a digit. The same replay now yields 74 findings, none with an empty anchor.
  Hunk CONTEXT lines feed the subject test, because the `def` a one-line change sits under is
  usually the only place the subject is named.
- **The yield accumulator moved to `sdlc-studio/.local/`,** following the precedent
  `gate-timings.json` already set. It was writing to a tracked path the hook never staged, so
  every commit left the tree dirty with a file the author had not touched. Counts recorded
  before the move are carried over rather than restarted.
- **The lane's own paperwork said the scan was "deliberately narrow: only lines the diff
  ADDS".** `_standing_prose`, which reads the whole standing `changelog.d/` corpus on every
  run, landed in the same sprint and left that claim false in both the module comment and the
  changelog fragment - the drift shape this lane exists to catch, in the lane's own
  description of itself.
- **US0597's AC3 was ticked `Verified: yes` over a verifier that could not fail on its
  subject.** It asserted `runs == 1` against a record the test itself had just written in a
  temporary directory, while the evidence file the criterion names had never been created.
  The replay record now exists and carries both arms, the corpus it was taken over and the
  units it covers; the verifier asserts each of those separately, and that the after arm is
  actually below the before arm.
- **The placeholder rule is about FRESHNESS, not type.** A Draft story's criteria scaffold was
  a warning while a freshly-minted CR's was an ERROR - so `artifact.py new --type cr`, the path
  the docs call recommended, produced an artefact that blocked the very next commit, and the
  author had to hand-edit what the tool had just written. That is the hand-authoring the
  deterministic path exists to avoid, induced by it. A request at its opening status is
  not-yet-written for the same reason a Draft story is; past that, it errors.
- **`artifact.py new` now says when it has minted something unfinished.** Reporting unqualified
  success sent authors away from a document that still needed writing, and they met that fact
  later as a refusal from a different command.
- `refine` no longer mints stories carrying unfilled `{{...}}` User Story fields, and now prices
  the grooming it creates. The role, capability and benefit are derived from the story's own
  title, its resolved persona and the request it delivers, at both mint sites. The result line
  reports how many minted stories still owe authored criteria and states plainly that the work
  is not covered by the points, which size the delivery each story describes. The count is
  `sprint breakdown`'s own census, so what `refine` reports and what `sprint plan` refuses on
  cannot disagree.
- **`tools/tests/conftest.py` puts that directory on `sys.path` for every module at once.** A
  sibling fixture imported by bare name resolved under `unittest discover` and NOT under
  pytest - which `verify_ac` invokes to check a criterion - so a story's own verifier could not
  run while the same module passed in the suite.
- A per-file insert fixes one module and has to be remembered by the next author; this is the
  second filing of the same import gap. A guard - in `test_test_census.py`, the module that already reasons about test-file health - collects the whole directory under pytest, so a
  module arriving without a resolvable import fails immediately. Mutation-verified: deleting
  the conftest kills it. The two existing per-file inserts are kept and annotated, because a
  direct `python3 tools/tests/test_x.py` run collects no conftest.
- **`decisions.py` collapses a rationale into a single table cell where the row is composed.**
  A multi-paragraph rationale pasted straight in split the row and the table stopped being a
  table (markdownlint MD055/MD056); it happened to this project's own decision log and had to
  be repaired by hand. Collapsed at the writer, not asked of every caller - this function knows
  it is building a cell and the callers do not. Refusing a multi-line rationale would be worse:
  the rationale is the valuable part, and a writer would shorten it to satisfy the tool.
- **A field may DECLARE that it quotes a shell hazard rather than having suffered one.** An
  artefact documenting the mangling defect necessarily contains the mangled text, so the
  detector flagged the very report written to explain it - and the filing had to be reworded to
  describe the evidence rather than show it, which is the opposite of what a defect report is
  for.
- **Declared, never inferred**, and never empty. A heuristic guessing which prose is
  illustrative would exempt the real cases too; a marker with no reason after it is a switch,
  and a switch with nothing beside it is what turns a detector off by habit. An undeclared
  hazard is still reported, which is the control.
- **A run records the commit its delivery is measured FROM, stamped when the run opens.**
  `sdlc-studio/.local/sprint-base-ref.txt` was written once and never rewritten, so it held a
  sha two weeks older than the run reading it. That ref decides whether a finding is a
  regression this unit caused or something already true: a fortnight early, unrelated work
  reads as new and blocks the review - and a defect the unit really did introduce can read as
  pre-existing and be waved through.
- **A re-plan does not move it.** Moving the yardstick mid-run would silently reclassify every
  finding already made, turning work judged a regression into pre-existing.
- **An unrecorded base ref reads empty, never a guess.** A consumer must be able to refuse
  rather than believe a fallback; falling back to HEAD would make every diff empty instead of
  obviously wrong.
- **The commit gate's test selection reached nothing, so every commit ran the whole suite (BG0467).** `commit-msg` deleted the pre-commit handover and then read the computed selectors out of that same file forty lines later, so `selectors` was always empty, the run recorded `verdict-mode full`, and neither suite runner accepted a selector in any case. Several hundred lines of selection logic - `select_tests`, `suite_read_map`, `_import_graph`, `test_relevant_paths` - ran on every commit, produced an answer, and the answer was discarded. The recorded timing history shows it plainly: `total.tests` reads 6,152 to 6,174 across all ten runs, which is the full suite every time, while the two unit suites are 86% of a 557s gate. The handover is now read before it is deleted, both runners take a selection as dotted module names on `PYTHONPATH`, and absence still means run everything - a missing list is an unanswered question, never an answer of "nothing to run".
- **The scope floor and the newly-working selection no longer fight (BG0467).** The floor refuses to record a total when a run covers less than 80% of the historic peak, which is how a truncated or half-imported suite is kept out of a budget series that only means anything between comparable runs. The instant selection began working, every selected commit looked exactly like that: the first one reported `total NOT recorded - 1171 tests against a peak of 6174`, so the budget would have stopped being written at the moment the gate got cheaper. A selected run is now exempt from the PEAK comparison and records into its own `total.selected` series, so neither reading erodes the other. The loader-error check is untouched and still refuses: that is a fact about the run rather than a threshold, and a selected run whose module failed to import is exactly as broken as a full one.
- **The gate budget reports the run that actually happened (BG0467).** With selection working, a selected commit records into `total.selected`, and the budget line went on reading `total` - so a commit that ran in 226s was reported as `OVER - 554s`, which is the previous full run's duration. A budget line naming a number this commit did not pay is worse than none, because it is believed. The report now reads the series the run used, marks a selected total as such so its drift is not taken for a like-for-like comparison against the full-run baseline, and returns to the full series the moment a full run records. The series a total went into is written at the point it is written, rather than inferred afterwards from two histories' lengths - an inference that cannot tell "selected ran last" from "selected ran once, a while ago".
- **A v3 id is no longer exempted from the provenance check by an accident of parsing, and the close's finding-placement count is scoped to the run (BG0466).** `id_number` returns None for a v3 ULID by design, and `or 0` turned that into a score of 0 - under every cutoff - so the whole family of ids the product now mints by default was exempted as pre-adoption legacy, and an exemption rendered identically to a pass. An id carrying no ordinal is now checked rather than exempted, at both the check and the backfill, which is the direction `reachable_end_state` already takes for an unrankable id; a numbered id under the cutoff is still exempt, pinned as a control. Separately, the out-of-batch finding count's run-scoping predicate only truthy-tested the run's start time and never compared it, so the line reading "this run" was really "this repo, ever" - it now compares the artefact's own date against the run window, and an artefact whose date cannot be established is counted rather than dropped, since of the two ways to be wrong only one flatters the run being measured.
- **A rendering path that accepted a hardcoded constant, and a sweep that missed the file it named (BG0465).** Both found by the closing full-diff review of this sprint's own delivered bugs. The close's finding-placement line computes how many findings were raised outside a batch, and its verifier pinned the rendering with ONE fixture and one single-value assertion - so replacing the computed value with the literal `2` survived all 623 tests of the module, at every scope. The verifier now uses two fixtures whose counts differ, which a constant cannot satisfy. Separately, the sweep that moved three hand-rolled `stem.split("-")[0]` id parses onto the shared reader named `handoff.py` in its own Affects and its own summary, and never touched it: a v3 `HO-<ulid>-slug` key parsed to the bare prefix `HO`, so the document never resolved. Repairing it surfaced why the original sweep had gone round it - `extract_record_id` answers for the types in `ARTIFACT_TYPES` and only those, returning None for a handoff, a retro or a review. `stem_record_id` is now the shared parse for those families, so there is one idiom to reach for rather than a hand-rolled split per caller.
- **The handoff key defect in two more readers of the same family, one of them a blocking close lane (BG0465).** A rejoinder review of the repair above ruled it OVER-CLAIMED and was right. `gate._handoff_present` located a handoff by stripping the hyphens out of its id and globbing the result, so a v3 key globbed a name nothing on disk carries: a handoff that existed AND was linked from its retro reported MISSING from a lane whose verdict blocks a close, and the link check one step further down searched for the same stripped form. Both now derive from the document actually found. The regression test for the earlier half re-implemented the locator inline rather than calling it - under a docstring saying it did not - so the repaired line had no cover at all and the mutant that found the defect survived the whole module; it now drives `handoff.refresh` and the gate lane. And a comment claiming the sweep stopped v3 artefacts reading as pre-adoption legacy was false: `id_number` returns None for a ULID by design, so they still are. The comment now states what the code does, the change it did make is pinned by a test, and the exemption is filed rather than papered over.
- **An author can no longer retire the review that blocks their own work (BG0464).** `critic.verdict_for` skipped any verdict row whose `superseded` flag was truthy, of any grade, and the close's coverage gate reads it - so a unit carrying a live independent REJECT lost that REJECT and reported as "covered by an independent pass". `record_supersession` refuses to write such a record: it demands a trust boundary and refuses an authoriser who is the row's own author. But the verdict log is a text file, a hand append walks round the tool, and `_is_principal_superseded` exists as precisely that read-time backstop - consulted only by the sign-off gate. The sign-off gate and the coverage gate were enforcing different independence rules, and the weaker one guarded the honesty check. The grade of correction required now scales with the direction the mistake fails: retiring an APPROVE weakly costs an approval and the gate refuses, so it stays unconditional, while retiring a REJECT weakly removes the only record that blocks the unit and now needs a principal-grade supersession - a named boundary, an authoriser who is neither the author nor an in-session reviewer of that unit.
- **A truncated render says what it dropped (BG0463).** The close checklist's impediments row rendered the first twelve blocked units and stopped, with no marker - so an operator could not tell a batch with twelve blockers from one with forty, and a silent cap reads as "that is all there was". Its sibling review-coverage row already appended `(+N more)`; the same fact was rendered two ways in one report. Pinned by a fixture-backed test with twenty blocked units on disk, because the row derives them by reading each unit's status rather than taking a list - a dict fixture skipped silently and asserted nothing.
- **A pattern that enforced nothing is gone, and the real route is named where it stood (BG0463).** `_RESOLVED_Q_RE` was defined in `lib/sdlc_md.py` and never referenced, so the "moved under Resolved Questions" route worked purely by OMISSION from the open-questions pattern - while a compiled pattern sitting beside it read as though something implemented it. Deleted, with a comment stating how the route actually works.
- **`cycle_drift` no longer takes a parameter it never reads (BG0463).** Every caller already passed nothing; the signature promised a root it ignored.
- **The version guard's discovery test can now tell discovery from the hardcoded fallback.**
  It asserted that `trd.md` and `tsd.md` appear in `discover_spec_homes()`, and both are
  members of `SPEC_FILES`, which the function unions in unconditionally - so it passed
  identically with the whole scan deleted. A verifier that cannot fail on its subject.
- The replacement uses a version-declaring file OUTSIDE `SPEC_FILES` and asserts that it is
  outside, so the union cannot satisfy it. Mutation-verified: replacing the body with
  `return sorted(SPEC_FILES)` kills the new test and would have survived the old one. All
  three homes this repo actually has are in `SPEC_FILES`, so the discriminating case had to be
  built rather than found.
- **The checklist's own drift guard no longer certifies rows it never checked (BG0461).** `cycle_drift` returns three buckets and the guard verifying it asserted two - while the third was non-empty on the shipped tree, because `retro.py` built its subparsers inside `main()` and published no `build_parser()`, so two of the eighteen rows were reported unverifiable and a caller reading the first two buckets saw green. `retro.py` publishes its parser now, the bucket is empty, and the verifier asserts all three. The `uncovered` half walked the `sprint` verbs alone though six rows hold a stage in `critic`, `retro`, `lessons` or `handoff`: it walks every script the rows name, with per-script exemptions that over-report rather than under-report, so a ceremony verb nobody exempted fires the guard instead of slipping past it. Planned POINTS are now summed from the planned units' own artefacts and reported beside the delivered figure, which the criteria asked for and nothing computed - and the fixture behind that assertion no longer uses one drop plus one add, a shape that made the batch as approved and the batch as it stands the same number so deleting the reconstruction entirely survived it. Finally a waiver must name a real checklist item - the scope tail was never validated, so a waiver of an item that does not exist recorded cleanly and was read by nothing while the close stayed blocked by the very item the log said had been waived - and it must record WHO authorised it, because a compulsory close item set aside by nobody in particular is a decision with no decider.
- **The close dry-run accounts for every chain step (BG0460).** `DRY_RUN_ACTION_STEPS` was a hand-maintained restatement of `_CLOSE_CHAIN` that had lost `gate`, so that step reached the report as neither `ok`, nor `refuse`, nor among the unevaluated - and a step whose silence is indistinguishable from a pass is the one thing a preview must never produce. The set is now derived from the chain, so a step added there cannot leave a hole here. The gate is not re-run against the scratch copy - the preflight has already run it against the real tree - so its verdict is taken from there: `ok` when the preflight ran it and found no gate blocker, and `unevaluated` when the preflight returned before reaching it. A first attempt marked it `unevaluated` unconditionally, which made `clean` unreachable and every dry run exit 1; an independent seat caught that, and a second caught the opposite error of reporting `ok` for a gate that never ran. The report's step count is derived from the chain too, retiring an "all seven steps" claim that had outlived the seven-step chain by three.
- **`sprint close` no longer reports a scaffolded retro as `valid` (BG0418, BG0459).** `retro validate` has always printed an EXAMPLES report for a retro still carrying the shipped template's worked demonstrations, and always exited 0 for them, because a scaffold-shaped retro is structurally valid. The close kept only the exit code, so it printed `retro-validate: RETRO0086 valid` over a document in which nothing had been replaced - the operator was told the opposite of the truth by a check that had correctly noticed it. The rule is now stated rather than inferred: any leftover is reported on the close's own output, and a retro still carrying EVERY demonstration line the template ships is REFUSED, since that is the difference between a document somebody wrote and a scaffold nobody opened. `close --dry-run` routes through the same probe and says the same thing, so a preview cannot clear a close that then refuses.
- **Five sprint-checklist rows now establish what they report (BG0458).** The row that answers "was everything we committed to delivered?" read the RETRO's batch rather than the run's plan, so a planned unit the retro never listed was invisible to it and the page asserted "none - every planned unit was delivered" while planned-versus-delivered beside it read 1/2; it is now derived from the plan, names an unaccounted unit as such, and keeps carry-over and unaccounted disjoint so the counts add up. `held` was read from an append-only list that `decision resolve` never cleared, so a unit whose question was answered and which then shipped rendered "held (operator decision pending)" AND counted delivered on the same page - `resolve` now clears both lists it writes, and the row additionally requires the decision to be outstanding and the unit unfinished. The known-issues row FAILED OPEN: a run record with no start time, an unreadable carried table, or a retro that could not be located all returned empty and rendered as ANSWERED "none carried" over a workspace with open findings on disk; each is now UNANSWERED and says which, matching the distinction its sibling impediments row already drew on the same page. The review row counted distinct reviewer NAMES rather than seats, so two reviewers in one seat reported two lenses and escaped the under-covered mark - it counts seats now, while two reviewers with no declared seat still count separately. And the impediment row names the blocker it reads through the shipped `Blocked By` / `Depends on` convention, or says NO RECORDED BLOCKER, because an operator told that something is blocked and not what to unstick has been told half of it.
- **Two repairs that were over-claimed, found by re-reviewing them (BG0458, BG0461).** An independent seat ruled seven of the nine original findings CLOSED and two MOVED. The not-delivered row no longer read the retro instead of the plan - but a planned unit that was HELD and absent from the retro was emitted under both headings, so one undelivered unit rendered "1 held, 1 UNACCOUNTED" beside "1/2 unit(s)": two problems stated where there was one, in the row whose whole job is making that arithmetic readable. The buckets now partition strictly, dropped over held over unaccounted over carried, and both boundaries are pinned. And the waiver scope check was more permissive than the store it guards: the validator stripped the scope tail before checking while the subject normaliser stripped only the outer ends, so `rule:sprint-checklist: cost` passed validation, was written with the space intact, and the lookup - reading the unpadded key - never found it. The waiver recorded cleanly, read as accepted, and covered nothing, which is the exact defect the scope check had just been added to end. Subjects are now normalised segment by segment. Three further repairs were correct but unpinned - the unaccounted bucket, the carried-table exception limb, and the planned-points absent-versus-zero sentinel all survived being deleted - and each now has a test that discriminates it.
- **A ruling verb no longer buys an exemption from the destination it names, and the corpus-read pin measures the thing it claims to (BG0456).** Two guards that reported green over something they never checked, both found by independent review of work already delivered. `unresolved_questions` matched a ruling verb before either destination check ran, so `- [x] deferred, resolved by BG9999` - a ruling citing an artefact nothing in the workspace holds - was accepted, while the identical citation without the verb was refused; the same short-circuit made `_decision_cited`'s existence check unreachable for the natural `ruled by D9999` phrasing, leaving a written check standing beside the defect it was meant to prevent. Both routes out of an open question now consult one destination check. An absent decisions table is separated from a table that does not hold the id, so a project keeping no decision log is not held to one. Separately, the pin claiming a corpus read cannot regress to per-unit was inert for its whole life: its fixture performed a constant six lookups whatever the corpus size, so cached and uncached runs were both linear in the unit count and the asserted ratio sat at 2.0 either way - neutering the cache cost a ninefold read increase and moved the assertion by nothing. The fixture now scales its lookups with the corpus, which makes the uncached case quadratic and the ratio a real boundary.
- **`sprint stop` can tell a unit awaiting a signature from one nobody built (BG0455).** Its notion of "remaining" was status-based, so a unit standing at Review counted as buildable - but on a project setting `review.two_role_after`, Done needs a reviewer-of-record sign-off the authoring session is explicitly refused, so nothing the run could do would move it. Stopping RUN-01KYPZ1G named 14 such units as `could have proceeded` and demanded `--force`. That cost more than friction: `--force` exists to price what parking a run threw away, so the record overstated the loss, and reaching for the expensive escape became routine. `blocked_by_pending` now reports `awaiting_signoff` separately, reading the same rule `reachable_end_state` applies at plan time rather than restating it, and the stop states the held units out loud instead of dropping them silently. A genuinely unbuilt unit still refuses the stop.
- **The confinement write detector no longer reads `list.remove` as a filesystem write (BG0454).** `remove` was keyed on the bare attribute name at an arity `list.remove(x)` and `set.remove(x)` share exactly with `os.remove(p)`, so a read-only module was censused onto the writer roster. Over-inclusion is the right default for this detector - a false positive normally costs one allowlist line - but the remedy the sweep offers is exactly that line, and an exemption for a module that writes nothing reads precisely like a real one, so the roster's meaning erodes one honest-looking entry at a time. `remove` now requires a filesystem-module receiver; `unlink`, which has no mainstream collision, stays over-included. The narrowing immediately exposed a false exemption that had stood since it was written: `conformance.py` was allowlisted as "removes only its own scratch file" when its only `remove` was `required.remove("critiqued")` on a list. The rotted-entry guard caught it and the entry is retired.
- **Three readers of an artefact key now share one idiom (BG0452).** `stem.split("-")[0]` yields `CR` for a v3 key like `CR-0001-add-auth`, so the forecast reader and the readiness reader silently returned "not verified" for every id the product now ships by DEFAULT. It survived because every existing test used a v2 key: the tests agreed with the code about a shape the product no longer ships, which is why the fix covers BOTH schema versions rather than the reported one. Both readers move to `sdlc_md.extract_record_id`. The third site needed the opposite answer: `RETRO` is a meta prefix `ID_RE` does not recognise, so `extract_record_id` returns None for every retro there is, and the resolver now delegates to `retro.find_retro` - the shared resolver whose own docstring says it exists so the gate and this script cannot disagree about which file they mean. That divergence was latent rather than observed, and is recorded as such.
- **The grooming gate reads the acceptance criteria it is gating (BG0449).** `sprint plan`'s breakdown gate asked only for `Affects` and `Points`, so a story that declared files and a size was certified GROOMED however empty its criteria were. Four stories carrying the template's literal ungroomed banner and three `{{placeholder}}` scaffolds were listed among the groomed units of a plan recording `mode: enforce, blocking: true, ungroomed: [], ok: true` - and 15 points were planned into a sprint on that green, in the mode whose entire purpose is to refuse them. `conformance.story_is_ungroomed` already read BOTH shapes correctly and nothing asked it; the gate now does, for stories only, under the EXISTING `grooming.acs` check that the shipped Definition of Ready template already declares and a project can stand down like every sibling. Both shapes matter: the banner is removed by hand during grooming, and the scaffold is what remains if someone deletes the banner without doing the work.
- **The availability guard matches the `gh` TOOL, not two letters (BG0447).** `states_fail_loud` ended `and "gh" in passage.lower()` - a substring test on one of the commonest letter pairs in English, satisfied by `nightly`, `highlighted`, `though`, `walkthrough`, `high` or `eight`. The guard's own round-1 REJECT had been that a whole-file letter match cannot discriminate, and the repair reintroduced the identical defect in the half added to fix it. The match is word-bounded now, with a control proving the forms the docs actually use - bare, backticked, possessive, parenthesised - are still accepted, so a guard that could not discriminate is not traded for one that fails on correct documentation.
- **The test census stopped reporting an all-clear over zero files (BG0445).** `tools/test_census.py` matched its skip list against the ABSOLUTE path, and the list contains `worktrees`, so any census root beneath `.claude/worktrees/` skipped every file: the count was zero and the lane passed over nothing - inert in exactly the environment this repo runs its reviewers and parallel delivery agents in. The list names directories INSIDE the census root, so it is now matched against the relative path, and the guard asserts a non-empty census for EVERY name in the skip list rather than only the one a reviewer happened to hit (`node_modules` and `.git` were waiting behind it), with a control proving a genuinely vendored test is still excluded.
- **There is now ONE independence predicate instead of four that disagreed (BG0443, BG0444).** `critic.is_independent` ended `bool(author) and reviewer != author` and never tested that a reviewer EXISTS - an empty reviewer is not equal to a recorded author, so the expression was True and the row passed as independently reviewed, with four gate consumers using that predicate alone. Separately, `sprint_covers_independently` tested only non-empty-and-distinct, so it accepted the `PRE_GATE` migration sentinel that `is_independent` refuses; `sprint.review_coverage` compensated by AND-ing the second predicate on and `conformance.py` did not, so the same row cleared Done in one module and was refused in the other. Both are instances of one shape: four predicates, correctness depending on each caller remembering which combination to AND, and nothing checking that the four agreed. `critic.independence(reviewer, author)` is now the single authority, returning the reason as well as the verdict; every predicate delegates to it, `record_verdict` floors an empty reviewer as it already floored the author, and a public `same_identity` serves the callers asking a different question. A sweep asserts no module rebuilds the test from critic's private parts - it found four such sites neither bug report named.
- **The close's finding-placement metric is measured again, not hardcoded to zero (BG0442).** `sprint._findings_outside_batches` opened with a function-local `import run_state`, shadowing the module-scope binding; `lib/run_state.py` begins with a relative import no top-level import can satisfy, so it always raised, a blanket `except Exception` returned 0, and the diagnostic went to a debug channel that is a no-op unless `SDLC_DEBUG=1`. It was unreachable code returning a constant, silently, on every default run - printed under the words "the number this run drives to zero", so the line read identically for 0 close-time findings and for 10,000. The metric is the one that makes the sprint goal's central claim falsifiable.
- **The isolated-checkout rule reaches the reviewer, and a mutation result carries the tree it was measured in (BG0440).** The rule was documented and enforced in exactly one direction: `mutation.py run` refuses a target with uncommitted changes, which protects the AUTHOR, and nothing protected the tree from the REVIEWER. Four reviewers dispatched concurrently over one working tree left a live mutant behind in it, found only because the tree was otherwise clean; over uncommitted work it would have been indistinguishable from that work. `critic.py brief` now states the requirement in the prompt every delegated reviewer receives, names the mechanism (`Agent(isolation: 'worktree')`) rather than the abstract rule, and forbids `git stash` and `git checkout --` by name - both are tree-wide, so one reviewer's cleanup reverts another's mutant mid-run and a result reported SURVIVED may never have been on disk when its test ran. A brief naming the instruction without that reason is refused, like every other standing practice. `mutation.py run` also records whether it ran in a linked worktree, the main worktree, or a checkout git cannot describe, and prints the qualifier beside the KILLED/SURVIVED counts: an undescribable checkout reads UNESTABLISHED rather than shared, and a confirmed isolated tree prints nothing, because a warning shown on every run stops being read.
- **The audit-run register's two readers agreed on nothing.** `run_row` returned the FIRST
  matching row while `register` folded by dict assignment and kept the LAST, so a duplicated
  run id reported a different provenance depending on which reader was asked - and a seeded run
  could be silently overwritten by a plain `record` appended after it. Both now fold last-wins,
  stated in both places.
- **A duplicate run id carrying a different provenance is refused**, naming the run and both
  values. The same provenance still records: re-writing an identical measurement is harmless,
  and refusing it would break the append-only contract for no gain.
- **A provenance line naming two filing runs is refused, not settled by document order.**
  `filing_run` returned on the FIRST `run <id>` match, so its Ambiguous refusal was reachable
  only when no run id appeared at all - and two candidates were resolved by which came first in
  the sentence. That is precisely the guess the refusal exists to prevent, and a fabricated
  provenance is worse than an absent one.
- **The carry-over marker matches both word orders and the id pattern is case-folded.**
  Measured over the 1438 `Raised-by` lines in this corpus, 13 write `<id> carry-over` and none
  writes `carry-over from <id>`. The second word order is therefore defensive rather than
  observed - an earlier draft of this entry claimed the corpus was half-and-half, which
  measurement refutes. The case-fold is the half that was already earning its place: an id in
  any other case simply did not match, and a pattern that silently matches nothing is how the
  disambiguation quietly stopped happening.
- **The carry-over criterion now uses inputs that need disambiguating.** Its fixtures named one
  `run <id>` beside a bare carried id, so the candidate list had one entry however the
  carry-over matched - the criterion stayed green while the branch it exists to check was
  deleted outright. Every fixture now names two filing runs, with the ambiguous control beside
  them, and the "half the corpus writes the second form" rationale is corrected to the measured
  zero of 1450 the fragment already recorded.
- **An Affects path naming shipped payload now resolves against the LOADED skill dir**, which
  the docstring already promised and the code never looked at. A path such as
  `.claude/skills/sdlc-studio/templates/audit-profiles/<x>.md` resolved only where the skill is
  vendored into the tree - this repo and nowhere else. In every consuming project it silently
  resolved to nothing, and an Affects that resolves to nothing reads as an ungroomed unit.
- The skill dir is DERIVED from the module's own location rather than assumed, because the
  skill runs from an installed copy everywhere but here. A genuinely absent path still resolves
  to None, so greenfield declarations keep reading as absent and the grooming gate still
  catches a declared file nobody has written.
- **The loading-guide sweep read which column holds a label from the table's own header,
  instead of assuming column 0 always does.** That assumption holds for the guide's first
  table and is false for its second, which is headed `| Path | Purpose |` - so its path cells
  sat in column 0 and were never examined, by a check whose entire purpose is to examine them.
  Measured against the shipped guide, the fix newly reads four cells including a real path
  (`templates/config-defaults.yaml`) the sweep had been blind to.
- **Every signature detector is now exercised through the shipped parser**, one assertion per
  runner. Measured over `templates/audit-profiles/*.md`, the packs use `python3` (8 rows) and
  `rg` (1); `bash` and `npm` appear in none - so two of the four shapes reached the parser only
  through a fixture built for them, and `all(mechanical)` over the packs passed with either
  removed.
- **The tuple is deliberately NOT narrowed.** It is wider than this repo's own packs use
  because a consuming project writes its own signatures, so the honest fix is coverage rather
  than removing vocabulary somebody else needs. Mutation-verified: dropping any one of the four
  runners is now killed.
- **`.verify-lint-baseline.json` is under the shrink-only guard, with a reader that can parse
  it.** It was absent from the tuple because the line-splitting reader could not have read it -
  so nothing held it to shrink-only, and a permanent extensible exemption sat where a ratcheted
  one was documented. Line-splitting that document returns 153 fragments of JSON punctuation
  where there are 43 real keys, which compares equal to itself and ratchets nothing while the
  guard reports green.
- **A file declared a baseline that parses to nothing is now caught**, because that is exactly
  the state this found: present, green, holding nothing.
- **The `verify-ratchet` lane's flags are asserted at BOTH invocation sites**, as its sibling
  lane already was. Without `--ratchet` the lint reports and never refuses; without `--bugs` it
  judges stories only and half the corpus is silently exempt. This is the lane that already
  lost `--bugs` once with the whole suite green.

The filing's third defect - grouping on the resolved argv rather than a normalised string - is
carved out to BG0486. Regrouping reshapes the baseline this unit just brought under the
ratchet, and doing both at once would leave neither measurable.

- **Test selection now reaches a module by the script it LOADS, not only the one it is named
  after.** The naming route matched `x.py -> test_x.py` and nothing else, while the class is
  broader - `test_two_backlogs.py` loads `refine.py`. The index is derived from the loader
  calls the modules actually make, never from a hand-kept table that would drift.

### Measured, and smaller than it looks

`test_two_backlogs.py` was already selected for a change to `refine.py` before this fix - but
only because it measures empty and is swept in as unattributable, not because any route reached
it. The immediate selection delta is NOT quantified here. It was stated as "one module, for `status.py`"; an independent pass measured 11 of 12 sampled scripts gaining at least one module, and a re-derivation through `select_tests` returns the whole suite for every script, so no single figure survives all three. The direction is agreed - the fix selects MORE, never less. What this closes is the
LATENT failure: the moment such a module gains resolvable reads it stops being unattributable
and would be silently dropped for changes to the very script it tests.

- **The dead-flag detector no longer reports a false positive on a module-global namespace (BG0430, BG0439).** `_track_namespaces` registered the target of `X = parse_args()` against the ENCLOSING FUNCTION's scope, and `global ARGS` was not modelled at all - so a read from a sibling function walked the scope chain out to Module, found nothing, and the destination fell straight through to `dead`. A false positive on a blocking lane, with no warning attached, over a mainstream Python idiom the detector's own docstring did not list among its bounds. A `global` target is now registered on the module as well as on the declaring function, since `_is_namespace` stops at the first scope that BINDS the name and the declaring function does bind it - registering on the module alone would have fixed the sibling reads and broken its own. A `global` inside a NESTED function does not leak outward, which is the false-negative direction. Separately, the pre-commit lane's `enforces` line stated the INVERSE of the rule ("no flag whose parsed destination any line acts on"), which reads as forbidding flags that are used; it is the text an operator meets at the moment the lane refuses, so a remedy describing the opposite rule sends the reader to undo the wrong thing.
- **A module with colliding function names is reported UNJUDGED rather than silently clean (BG0429).** `_functions` keys every function by bare name over the whole module, so the last definition the AST walk reaches wins - and two ordinary verb handlers each with a local helper of the same name is enough to resolve a forwarded value into the wrong body. A fixture of exactly that shape reported `0 dead flag(s), 0 not judged` for a genuinely dead flag, which is silently clean and worse than either honest answer; with the helper bodies swapped it reported a LIVE flag as dead, and a flag deleted on a mis-resolved body is a documented switch removed for the wrong reason. Resolving properly needs a scope key; refusing to judge a collided module is the honest interim and uses the detector's own three-state design - dead, live, or not judged with the reason. Five modules in the scanned set carry duplicate names and now read unjudged instead of clean; the lane still reports zero dead flags and a module without collisions still fails on a real one.
- **A supersession waiver was keyed on whoever declared it, and a phantom pair was waived with a false reason (BG0428).** The key was documented as directional (`superseder>superseded`) so that waiving "A replaced B" could not also waive the opposite claim about which design won - and then a `reverse in waivers` fallback made the lookup direction-agnostic, which was load-bearing because ten of the eleven live pairs were keyed the other way round. The emitter now names which artefact superseded which, so the key is directional in fact as well as in prose, and the fallback is gone. Separately, ids were scraped from the whole field including its parentheticals, so `> **Superseded-by:** X (shipped via Y; residual folded into X)` read Y as a second superseder and manufactured a pair that never existed - it reached the tolerated set with a reason asserting something untrue about an artefact that superseded nothing, clearable only by writing a false declaration. Parentheticals are now stripped as `decomposed_ids` already did for exactly this reason, and the tolerated set drops from eleven pairs to ten.
- **Four defects in the epic-index and supersession sweeps, each found by an independent adversarial review (BG0427).** (1) `apply` decided per row and wrote per epic ID, so on a multi-view index one row's fillable verdict acted on another row's held cell - apply printed "left alone" and then wrote over that very cell, returning the same key in `synced` and `held`. The write is now keyed by line, and a reported cell names its row (`EP0001.Stories@L12`). (2) The header was located with `startswith("| ID |")`, which resolved to nothing for a padded, unspaced or indented header - a silent no-op on a fully drifted index - and on a two-table index lent the first table's offsets to the second table's rows. Tables are now identified by their separator row and each row resolves against its own table. (3) An unparseable `## Dependencies` row was read as "declares none", so an epic minted from the full template declared no dependencies on the strength of an unrendered `{{dependency}}`; a cell naming two ids also silently dropped one. An explicit `| None |` row is still a declaration, and only genuinely unresolvable content is now unknown. (4) A corrupt supersession waiver file had its state computed and never read, so every tolerated pair reported as a fresh finding with nothing saying the file could not be parsed - the outcome the reader's own docstring and the shipped reference both promised against. It now refuses once, naming the file.
- **The epic story census could not read the link form the shipped story template writes, so a wrong count was committed (BG0426).** `epic_story_count` compared the `Epic` field whole (`field == epic_id`) while every other reader of that field in the family extracts the id (`transition`, `verify_ac`, `sprint`, `ac_scope`, `mutation`). The shipped `templates/core/story.md` writes `> **Epic:** [EP0001: Title](../epics/EP0001-x.md)`, and 34 story files use that form - so the census counted none of them. Two consequences, both landed: a story count of `7` was written into a row whose true count is `18`, justified by a census that could not see two thirds of the evidence; and three rows were held as "uncorroborated" that simply had stories the reader could not see. The census now extracts and normalises the id, the three counts are corrected in the index, and the held set drops from eight rows to six. The reason recorded for the remaining six was also wrong - they are not epics whose story files were deleted (no story file has ever been deleted in this repository's history) but epics whose rows record an `**Estimated Story Count:**` from before stories were individually tracked.
- **`main` was one line over its own test-noise ratchet, so the noise gate was enforcing nothing (BG0425).** The baseline is frozen as a ratchet - the gate fails the moment a change adds a leak, and the number may only be lowered - but the shipped suite at HEAD leaked 130 lines against a baseline of 129, so the lane was red on `main` and could no longer tell a new leak from the standing debt. Measured twice, at HEAD and with the change applied, to prove the extra line was pre-existing rather than newly added. Ten `main(["build", ...])` call sites in `test_digest.py` were leaking a `digest: wrote N closed-artefact digest(s)` line each with nothing capturing stdout; capturing them took the count to 120, and the ratchet is lowered to match rather than raised to accommodate.
- **Test selection dropped a script's own test module the moment that module measured any read path (BG0424).** `select_tests` reached a test module by two routes - the import graph, and the statically measured read set of each suite module's source - and neither reaches a script loaded through `spec_from_file_location(name, dir / f"{name}.py")`: the f-string resolves to nothing, so there is no import edge and no measured read. Those modules were selected only as a side effect of measuring EMPTY and being swept in wholesale as unattributable. Adding two ordinary path reads to such a test took it out of that sweep and out of the selection for changes to the script it tests, so a commit touching that script would have run every suite except its own. The naming convention the repo already enforces (`x.py` is tested by `test_x.py`) is now a third selection route, independent of both the graph and the measurement - so it holds however a test loads its subject and whatever that test happens to read.
- **A green suite verdict is no longer recorded beside a failing lane.** The write ran
  unconditionally after `skill-tests`, so a FAILING lane still recorded `status green` - and
  the next attempt over an unchanged surface trusted it. That is the fail-open behind a gate
  that blocked a commit and passed the byte-identical retry twice in one session. A gate that
  fails intermittently trains an operator to retry rather than read, which is how the third
  red - the real one - gets discounted.
- **A blocked commit now leaves its suite output in `sdlc-studio/.local/gate-suite-last.log`.**
  Neither earlier false red was ever diagnosed, because the output lived only in the hook's
  console and the retry erased it. Evidence that does not survive the retry is not evidence.
- **The green verdict is now written BELOW both suite lanes, not between them.** Guarding the
  write on the lane result was only half of it: sitting between the lanes, the flag it read
  carried the skill lane's verdict alone, so a green skill lane beside a failing `tool-tests`
  lane recorded `status green` just the same, and the byte-identical retry reused it and ran
  no tests. The same fail-open, reached through the other lane. A failing `tool-tests` lane
  now leaves its output behind too - it is a suite lane, and the criterion says any of them.
- **The blocked-commit-leaves-its-log criterion is bounded to the skill lane's own capture.**
  Adding the tool lane's capture gave the hook a second occurrence of the log path, and a bare
  `index()` fell through to it when the skill lane's was deleted - whose guard contains the
  original guard as a substring, so the assertion passed while a commit blocked on the skill
  lane left no log at all. Found by the round-two pass on this repair.
- Four delivered mechanisms whose verifiers passed with the mechanism removed are now held by
  tests that fail without them: the close dry run evaluates every action step past a refusal
  (not only the preflight's blockers), the close proves it emits its own cost line by running a
  close, `critic`'s batch verbs prove no write was ATTEMPTED rather than that none landed, and
  `reconcile.detect_all` is pinned to the corpus cache it holds open - the previous tests each
  opened their own cache in a fixture, so they proved the mechanism and never its caller. Every
  mutant was demonstrated to survive the old coverage before the repair and to die after it.
- **`sprint close` no longer reports a scaffolded retro as `valid` (BG0418, BG0459).** `retro validate` has always printed an EXAMPLES report for a retro still carrying the shipped template's worked demonstrations, and always exited 0 for them, because a scaffold-shaped retro is structurally valid. The close kept only the exit code, so it printed `retro-validate: RETRO0086 valid` over a document in which nothing had been replaced - the operator was told the opposite of the truth by a check that had correctly noticed it. The rule is now stated rather than inferred: any leftover is reported on the close's own output, and a retro still carrying EVERY demonstration line the template ships is REFUSED, since that is the difference between a document somebody wrote and a scaffold nobody opened. `close --dry-run` routes through the same probe and says the same thing, so a preview cannot clear a close that then refuses.
- **The verb that writes `Status: Done` now enforces the bar it writes (BG0417).** The Definition of Done states the two-role clause and `conformance.py` implements it properly - but conformance is a lane that runs LATER, over a status a different tool has already written. `transition.py` never consulted it: no call, no config read, no reference to the evidence half anywhere in the module. A unit could be moved to Done with no independent review whatsoever, and the only trace was a report somebody had to run and read. That is the mechanism behind every Done story carrying no independent verdict - they did not slip past a gate, the gate they are said to have passed was never asked. (The count of 25 that circulated with this bug is NOT supported by the tree: a claims-lens census found 21 units with neither a per-unit independent verdict nor sprint cover, all pre-cutoff, and none in the D0074 cohort failing the critiqued stage.) `transition set <id> Done` now refuses a unit past `review.two_role_after` that lacks either half, naming them separately because an absent adversarial pass and an absent sign-off need different actions from different people. It delegates to `conformance` for both the predicate and the vocabulary, since a second copy of the rule is a second place for it to drift. Forward-only in both directions (no cutoff, or a unit at or below one, is unaffected byte-for-byte), fails CLOSED on an unreadable ledger because this gate exists precisely because silence was being read as a pass, and `--force` remains available and recorded.
- **A reopen now retracts the green it overturns (BG0416).** Reopening a unit is a human overturning a machine verdict, and nothing in the machine heard it. BG0372 was reopened because its tests "asserted a constant and a header the writer never emits" - and those tests still passed, so the verify-report still recorded the unit green and `sprint plan` still priced it as BUILT-NOT-CLOSED at zero points. Leaving a terminal status now rewrites `Verification depth` into a stated retraction that keeps what it claimed (never inventing one for a unit that claimed none), invalidates the unit's verify-report entry so the overturned verdict cannot be read as current, and `_built_not_closed` refuses a retracted unit whatever the report holds - so the two mechanisms cannot disagree. The build-forecast exclusion also states the points it removes, so a forecast below the batch total explains the difference where it is printed. BG0372 and BG0359 are corrected on disk.

  The filed diagnosis was WRONG about the mechanism and is corrected on the artefact rather than quietly rewritten: it blamed the surviving depth field, and `_built_not_closed` never reads that field. Checking the premise before repairing it turned a hygiene fix into a real one.
- **The sprint plan and the gate budget can no longer report different costs for the same gate (BG0415).** The budget lane read the recorded per-commit series and reported 554s against a 380s ceiling; `sprint plan`, pricing the same gate for the same sprint, read `gate_budget.baseline_seconds` and quoted 317s - 44% low, in the direction that under-prices the ceremony, and compounding with every commit in the batch. `execution_cost` now reads the same measured series the budget lane reads, falling back to the declared baseline only when no run has been recorded (so a consuming project that does not run this gate still gets a priced plan), and names which source it used along with the drift between them. A plan produced while the gate is over its ceiling states that verdict with the measured seconds and the budget, because planning is the one moment gate cost can still be traded against scope. The regression test moves the recorded series and asserts the plan's figure moves with it, rather than pinning the current constant - which the stale read would have satisfied just as well.
- **The one-source fix read the wrong series, and independent review caught it (BG0415).** `budget_report` reads `total.selected` when the last run was selected; `measured_gate_seconds` read `total` unconditionally. On this repo, whose commits run selected, the budget lane reported 100s and the plan 554s for the same gate - the disagreement the bug was filed about, inverted rather than ended, with the changelog headline false as written. The planner now keys on the same `total.last_series` marker the budget lane uses and names which series it read, so a selected figure cannot be mistaken for one comparable with the full-run baseline. Two consequences went with it: the plan announced an OVER-ceiling breach the budget lane did not hold, and priced the per-commit line at 554s against a measured ~100s - over-pricing by 5.5x the line whose error compounds with every commit. The ceiling boundary is now bracketed two-sided. AC4 was ticked while D0089 records that neither of its branches was taken; it is unticked and stated as carried, because carrying is not resolving.
- **A suite that stops running most of itself now BLOCKS the commit instead of declining to record a timing (BG0413).** `scope_ok`'s 0.8 floor judged whether a run was comparable enough to time, and its entire consequence was that a number did not reach `gate-timings.json` - so a close that deleted eight test classes ran 510 of 5,645 tests, reported green, and landed. A deleted test cannot fail, and nothing else in the repo can notice. A second and much lower `COLLAPSE_FLOOR` now grades a collapse separately from a drift: `gate_timing.py scope` exits **3**, and the commit-msg hook fails the commit rather than printing a note. Three, not two: python itself exits 2 for an argparse error and for a missing script file, so a caller reading 2 as `collapsed` blocks the commit whenever the tool is absent or mis-invoked. The existing 0.8 floor keeps its generous behaviour unchanged, because tests are legitimately deleted and a floor that fires on real deletions trains the bypass it exists to prevent. A deliberate bulk removal states itself in `sdlc-studio/.scope-collapse-ack.json` with the expected count and a reason, and the ack is spent on the removal it describes - a stale one, a reasonless one, or an unreadable one licenses nothing. A zero count is reported as its own state, since "the suite ran nothing" and "the runner's output format changed" have the same verdict but different fixes.
- **The collapse guard's first delivery was rejected by independent review, and the repairs matter more than the original (BG0413).** Five defects, each with an executed reproduction. The exit code was **2**, which python itself returns for an argparse error and for a missing script file - so an absent or mis-invoked `gate_timing.py` blocked the commit with a blank red line, breaking the hook's stated promise to degrade honestly, and it left `tools/tests/test_precommit_window_guard.py` RED on main. The collapse signal is now **3**, a code python will not produce on our behalf, and the lane additionally requires a non-empty verdict message. The acknowledgement escape set `ok = True`, which cleared the 0.8 timing floor as well as the collapse grade and let a one-test run's duration into the budget series where it read as a 100% improvement - BG0239's exact regression through the new door; an ack now clears the collapse grade and nothing else. A collapsed count was appended to the history, so ten retries of the instructed "commit again" evicted every real count and left the peak at the collapsed value, disabling the guard permanently (and with a zero count, the 0.8 floor with it) - a collapse no longer records, while a drift still does. The loader-error test used a count at the peak, so the `not loader_error` term was never exercised and survived being mutated away. A non-object ack was accepted.
- **The deterministic filer no longer mints artefacts the deterministic gate refuses (BG0412).** `file_finding` wrote an author's fenced block through verbatim, so a finding whose evidence quotes a command block arrived with a bare ``` opener - which markdownlint MD040 rejects. Two of the previous run's own findings hit it, and the only way past was to hand-edit the file the filer exists to stop anyone hand-writing. `sdlc_md.normalise_fence_languages` now supplies a language to every unlabelled block that CLOSES, called over the whole body by both artefact writers (a fenced block can only be recognised across the lines that open and close it, which no per-field normaliser sees). Three things it deliberately does not do, each a live defect if got wrong: a CLOSER is never labelled (CommonMark 4.5 - a language on a closer stops it closing, releasing the block early and turning the illustration below into live document content); a block already carrying an info string is untouched; an UNCLOSED opener is left bare rather than made to look deliberate. The guard is the markdown lane itself, not a unit assertion about the chosen shape.
- **A declared gate id must now name a real artefact, and a withheld narrowing says so out loud (BG0411).** Requiring a declared id to resolve did close the reported false green, but it resolved by matching the id pattern against any BASENAME under the directory - so one stray `BG288-repro.png`, a screenshot or a scratch note, made a typo'd `BG288` resolve and restored the false green in full. The check validated a filename pattern, not the artefact it claimed to require; resolution is now restricted to markdown artefacts. The second half was worse in a quieter way: the only report of a withheld narrowing went through `sdlc_md.debug`, a no-op without `SDLC_DEBUG=1`, in a change whose stated thesis was that a guard must never fail silently. `withheld_narrowings` reports both causes on the normal output path, naming the declaration and why it did not resolve. The declared ids are also resolved only after the filters that can discard the entry, so a declaration thrown away immediately no longer pays for a full directory walk first.
- **Silence now withholds the listing-only narrowing instead of granting it (BG0407).** The unanimity rule built its electorate from `suite_read_map`, which cannot see a path assembled at run time - 59 of 170 suite modules here measure an empty read set. Such a module was not counted as a reader, so its CONTENT read was silenced by another module's declaration, and the rule presented as closing the hole closed only the visible half. The contradiction sat inside one file: `select_tests` read an empty read map as an unanswered question and always included the module; `listing_only_scopes` read the identical silence as "not a reader, so the declaration is unanimous", and the unsafe reading ran first. `unmeasurable_modules` is now the one place that silence is interpreted and both callers use it, so the two cannot drift. When a narrowing is withheld the count and the reason are reported, so the cost is attributable to the modules whose reads need making visible rather than showing up as a gate that mysteriously never gets faster.
- **A sign-off no longer records approval of work that does not exist (BG0406, partial - the bug stays open for the rest).** `critic signoff --from-run` takes the run's APPROVED BATCH as its scope and wrote a row for every id in it without consulting status. Closing the previous run wrote three such rows: two bugs that had been reopened precisely because they delivered nothing, and a story reverted to Blocked. The note attached to them was batch-scoped, so it stated no falsehood about those units specifically - but the ROW reads as approval of work that does not exist, which is the same defect as a status asserting a repair that did not happen: a record meaning less than it appears to. A non-terminal unit is now SKIPPED and named on stderr, because a silent skip would be the same defect pointing the other way. A unit whose status cannot be read reports cannot-say and proceeds, since refusing a sign-off because a file could not be parsed would make the check more important than the thing it guards.
- **An unreadable run state is reported, not raised, by the two callers documented as never blocking (BG0405).** `run_state.read` raises on an unparseable file by design - unreadable is not the same fact as absent - but `lane_dispatch` read it ABOVE the guard that exists because a seam read must never block a dispatch, so a corrupt run state produced an unhandled traceback where a brief used to be issued. The seam scope now degrades to the units named in the call and says so: UNKNOWN, not empty. The same class reached `close_goal_judgement`, which is documented as never blocking a close and read the run state twice unguarded, through `prediction_miss` and `lanes_in_flight`; both now report the unreadable state as a line rather than raising out of the judgement.
- **A close with no run id no longer reports the whole ledger as its own cost (BG0404).** `close_cost` filtered on `run_id is None or row['run_id'] == run_id`, so a None run id short-circuited the filter and summed every close ever recorded - over-reporting by 6x on seconds and 143x on elapsed, in the one report whose stated purpose is measurement honesty. A run with no id now reports NOT ATTRIBUTABLE, which is neither zero nor the whole ledger. The reuse lookup is separately corrected: a reuse saves seconds a PREVIOUS run paid for, and it was being resolved against rows already filtered to the current run, so it could only ever fail - a measured saving was reported as unknown with its source row two lines above it in the same file. A reuse that genuinely cannot be traced is still reported unmeasured rather than zero.
- **Blocker grouping survives both id eras, and one owed action files one artefact again (BG0403).** Putting the detail in the group key stopped two blockers with different causes merging, and destroyed the property the grouping exists for in two separate ways. The unit-id mask was a local pattern that knew only the v2 four-digit form, so on a schema-v3 project three identical sign-off blockers produced three groups, each naming NO units - and the per-unit acceptance criteria the same change added were therefore empty, so the artefact covered units it could not name. The mask is now the shared id grammar, so a third era is covered on the day it is declared rather than on the day someone remembers a local copy exists. Separately, a done-gate refusal quotes the unit's own failing criterion, which differs per unit, so three units failing the gate filed three change requests for one owed action. A blocker may now state its CAUSE explicitly - what is owed, which is the same for every unit - while the per-unit detail is still carried into the artefact's body where it belongs.
- **A goal clause is no longer answered by guesswork (BG0402, closing the two halves left open).** `_recorded_clause_verdicts` carried a SECOND reading of a seat's answer, mapping everything that was not "yes" to `partial` - so a seat answering NO, the strongest signal a review can give, was recorded as a partial success while `verdict_polarity` sat unused in the same module. It also FANNED one plan-time answer about the whole goal across every clause, manufacturing per-clause evidence nobody gave, and doing so most confidently where a goal has several clauses and the seat was thinking about one of them. Only answers a seat recorded PER CLAUSE are now read as per-clause verdicts; a clause nobody answered reads UNANSWERED, which the panel already knew how to report; and the polarity is read once, through the shared function, so a third spelling of "no" is understood everywhere at once or nowhere. An unclear answer leaves the clause unanswered rather than being rounded into a verdict.
- **The mutation report's kill attribution is exercised through the production path.** It sat
  inline in `run_gate`, so the only available guard was `'row["test"] = killer' in
  inspect.getsource(...)` - a grep that stays green with the assignment dead. Extracted to
  `attribute_kill`, the value is now asserted: both mutants (the scalar made inert, `killed_by`
  emptied) are KILLED.
- **A content review must name the GOAL it answers.** Recording one against an empty goal was
  accepted, which is exactly what the surviving call-site mutant produced - an answer with no
  question, which cannot be scored at the close and reads exactly like one about the sprint.

### Re-measured rather than assumed

All five surviving mutants in the filing were re-run before any work. Two were already fixed
(the inert index guard, and `close_goal_judgement` unwired) and are recorded as such rather
than re-fixed. Two survived and are fixed here.

- **The release tag guard failed open one frame lower down (BG0408).** The previous repair caught
  what `close_owed.owed` RAISED. It raises for a corrupt baseline and for nothing else: the reads
  underneath it, `read_text_safe` and `walk_glob`, swallow their own I/O errors by design, so an
  unreadable delivery tree returned an empty unit list - indistinguishable from a clean one.
  `chmod 000` on the stories directory turned a correct refusal into "no close is owed". The
  swallow stays, because one bad artefact must not abort a walk over a thousand, and it gains a
  witness: `sdlc_md.degradation_log()` collects what each read degraded, and the tag guard refuses
  on a non-empty answer. A helper that degrades silently converts every guard above it into a
  fail-open guard.
- **The mutation run stopped hanging by orphaning the child (BG0410).** With a pipe, a
  backgrounded child held the parent to the timeout, which then killed the whole session. With a
  temp-file sink, `wait()` returns as soon as the direct child exits - so the kill hung off a
  branch the change had made unreachable, and every mutant left its orphans behind. The group is
  now reaped on EVERY exit path, from the pid captured while the child is alive rather than an
  `os.getpgid` lookup after `wait()` has reaped it. `mkstemp` and `Popen` moved inside the `try`
  (a Popen failure leaked a descriptor and a temp file on every call), `close` and `unlink` no
  longer share one suppression, and `_OUTPUT_CAP` - one occurrence in the file, its own definition
  - is read at call time so the constant that documents the bound now imposes it.
- **Six repairs reverted with no test going red (BG0409).** Both `file_finding` halves shipped
  with no test at all; `release_cut`'s raising branch had a test that called the real helper
  against a path which does not raise; `mutation`'s method-doubling half was asserted only in the
  pre-3.11 unittest form, which is the one form no current interpreter emits; `gate`'s
  protected-prefix and `isdir` guards were redundant for their single fixture, so neither was held
  alone; and the `killed_by` evidence test hand-wrote the key it then asserted. Each now has a
  discriminating test, verified by applying the mutant and watching it fail.

<!-- section: Changed -->
- **An existence probe no longer vetoes a listing-only declaration (BG0400).** A read of a
  directory is not one thing. `(repo / "sdlc-studio").is_dir()` asks about the shape of the
  checkout; `SKILL_DIR.glob("*.md")` asks what is inside. Only the second can be falsified by
  filing an artefact, and counting the first as a content read let one probe in one module outvote
  a correct declaration for the whole repository - so a commit touching no code paid the full unit
  suites. The path stays in the read map, so deleting the directory still selects the module that
  probes it; what it loses is a vote on a question it does not ask. A module that probes AND reads
  the contents keeps its vote. The subtraction has one implementation, `gate.content_readers`,
  which the rule and its tests share: both tests previously re-derived the reader set by hand and
  so asserted the suspension as though it were the rule.
- **No supplied field is discarded by the finding filer (BG0399).** The change-request renderer emitted Summary, Impact and Acceptance Criteria and nothing else, so a `steps` or `fix` supplied at filing reached no section and vanished without a word - the class `artifact.py` was repaired for, still live in the second filer, and the field it ate was the Proposed Fix of a change request about wasted time. Every supplied prose field is now landed in its own section, a field the type already homes is not duplicated, an unsupplied one adds no empty heading, and a backstop refuses the filing outright if anything still reaches nothing. The rule is asserted across every renderer and every field rather than case by case, because the omission was one renderer nobody re-read.
- **A listing-only declaration is scoped to the modules that made it (BG0398).** A declaration is ONE module's statement about its OWN read, and it was honoured tree-wide: a second module's content read of the same directory went silent, so an edit it asserts over answered `test-relevant: no` while its own assertion would have failed. A directory is now listing-only only when EVERY module that reads it declares it, and `.githooks` joins the protected set - it is a directory-level content read, and a narrowing needs its floor stated rather than inferred. **Consequence, stated rather than absorbed:** this repository has two readers of `sdlc-studio` and one declarer, so the narrowing is correctly withheld and the saving US0554 delivered is SUSPENDED. The second reader's dependency is a fixture path the static scanner over-attributes to the real tree; that is filed as BG0400 rather than papered over by adding a declaration that would not be true.
- **The `index-derived` gate lane sees field drift (BG0397).** `apply_type` gained a `fields` result - the projected index cells - and `index_derived_issues` went on testing four keys, so the one lane whose job is to assert the index is derived was green over 109 stale cells, and the commit gate asserted it too. The keys are now derived from `apply_type`'s own WRITE CONDITION rather than restated beside it, and a guard reads that condition from source: a key added there and not to `ROW_MUTATING_KEYS` reddens, which is the property the enumeration could not have.
- **A stale in-flight lane marker is reported whatever unit it names, and again at the close (BG0395).** The warning was filtered to the units in the current dispatch, so a lane that died on US0001 went unmentioned when the operator briefed US0002 - which is the restart case the marker exists for, and the only one in which the operator has not already noticed. Nothing else read the markers and `close_run` leaves them set, so the close now names any unit still marked in flight: a run could otherwise be signed off while the working tree carried work nobody had attributed.
- **Blocker grouping keys on the detail as well as the remedy, and the filed artefact lists every blocker it covers (BG0394).** The key was (stage, id-stripped remedy) while the cause and the artefact's summary came from the first member, so two blockers sharing a remedy and differing in what was actually wrong merged - the second detail never reached the artefact, while the close printed that they were "listed inside the artefact that covers them". The grouping that matters is preserved: one owed sign-off across twenty-three units is still ONE artefact. The filed change request now lists every blocker it covers and carries a criterion per unit, so it cannot close while the rest are still owed.
- **A goal panel nobody answered returns no verdict, and a verdict key matching no clause is refused (BG0393).** The function raises on an empty seat list precisely because "an empty panel returns a verdict nobody gave" - and then returned `partial` for a panel where no seat answered a single clause, reaching the same place by another route. Separately, verdicts were keyed by the stripped clause text, so a key differing by case or a trailing space dropped a seat's `missed` without error and it became `partial`; an unmatched key is now refused, exactly as an unrecognised verdict word already was. A partly answered panel still reports, so silence on one clause cannot blank a real judgement.
- **A plan-side content review survives the plan being written (BG0392).** `record_content_review` needed no open run and wrote onto the blank state, while `open_run` treats a state carrying no run id as spent and replaces it - so the natural order, review the plan then write it, wiped the prediction without a word and `prediction_miss` was permanently None. Recording with no run open is now refused, naming why, which is the behaviour `record_lane_start` already had: a review nobody can read later was not recorded, whatever the file said.
- **A one-unit lane brief names its seams with the open run's whole batch (BG0391).** `lane_dispatch` computed the seam map over the ids passed to that call, and the shipped documentation dispatches one unit at a time - so the feature worked only when the entire batch was briefed in a single command, which is precisely the case where a lane is not the one-unit reader the design is premised on. Seams are now mapped against the open run's approved batch and the brief still filters to the unit it is for, so the scope widened without the brief widening into noise.
- **The seam map stops reporting four kinds of false all-clear (BG0388, BG0389, BG0390, BG0396).** Owner matching was a naive substring, so `Preserves: tests/test_critic.py` owned the seam on `critic.py`; it now matches at path boundaries through `critic._verifier_names`, the sibling that documents and fixes this exact rule three files away. A `Preserves:` line was honoured anywhere in the document, so one under `## User Story` cleared a seam; declarations are now read from the criterion blocks via `verify_ac`'s own parser, which is what the field's contract always said. Affects paths were intersected as raw strings, so the same file written repo-relative and skill-relative - 149 against 1 in this corpus - was not a seam at all; they are resolved through `sdlc_md.resolve_affects` first. And `refine seams --units US9999` printed the all-clear at exit 0; it now uses the planner's own worklist reader and refuses an id that resolves to nothing, because a seam map over a batch that silently shrank is an all-clear about units nobody looked at.
- **The blocking-priority floor is derived from tiers and one cut, so it fires on the words this project files under (BG0387).** The floor was the literal tuple `p0/p1/critical/blocker`. This corpus files 104 `Severity: High` bugs and 168 `Priority: High` CRs against 2 Critical and 13 P1, and an adversarial reviewer writes `major` - so the floor that exists to block a close on a defect a release cannot carry never fired once. `PRIORITY_TIERS` orders the vocabularies by tier (`high` and `major` are the SAME tier: they are one severity written by a filer and by a reviewer, and ranking them makes the cut depend on which word was typed), and `review.blocking_priority` moves one cut rather than requiring a list of synonyms to be kept in step. A decorated value (`**High**`, `High (severity)`, `Sev-1`) is normalised before comparing - comparing it raw is the other half of why it never fired - and an unrecognised cut falls back to the shipped default, because a floor nobody configured must not silently become no floor at all.
- **`caller-check` takes a batch, and says how many units it checked (BG0386).** `--unit` was declared with a bare `nargs="+"`, so a repeated `--unit A --unit B` kept only B and argparse said nothing: the command answered about one unit while the caller believed it had answered about the batch. That produced a `caller-unnamed 5 -> 0` which reached a retro and two commit messages before the library call was checked and showed 17 of 23. `action="extend"` accumulates across repeats, `--units` takes a comma-separated list, `--from-run` takes the open batch, and every run now prints the count of units it covered - a clean result has to name the scope it is clean over.
- **Five mechanisms that reached no caller are now reached from the commands that consume them (BG0385).** RUN-01KYMJEM built `goal_panel`, `judge_defects_against_goal`, both ends of the bookend content review and `prediction_miss` - green tests, killed mutants, and nothing called any of them. The per-clause verdict that close recorded was assembled by hand, so the panel's author-exclusion never fired once. `sprint close` now runs the panel over the goal's clauses, judges every open defect against them, reports the prediction miss, and runs `caller-check` OVER ITS OWN BATCH - the repo's own detector for this class, which had never been run over a batch, which is why an operator's question found this and the tool did not. `sprint plan --content-review` and `sprint close --content-review` record the two ends of the bookend, and a goal with no plan-side answer is reported UNANSWERED rather than assumed. The lane reports and never refuses: the mechanisms inform a sign-off, and a reporting lane that can block a close is a lane that gets switched off. The five units now declare their `Caller:`, so the check that would have refused them at delivery passes.
- **A bug's acceptance criteria are no longer discarded at filing (BG0384).** Both creation paths lost them, in different ways. `artifact.py` gated its criteria writer on an enumeration - `('story', 'cr', 'epic')` - and the bug scaffold had no Acceptance Criteria section, so supplied criteria vanished at exit 0. `file_finding.py` was worse: `derived_criteria` correctly declines to derive when the author supplied their own, but nothing then rendered the authored ones, so the block fell through to the thin-evidence note and wrote *nothing here states what fixed would look like* over criteria that did. A bug now renders its criteria on the same terms as an epic, the filer writes authored criteria ahead of derived ones and ahead of the stated absence, and a supplied field the chosen type genuinely cannot store is refused by name rather than written away - checked against the rendered document rather than a list of type/field pairs, so a type nobody thought of is covered on the day it is written. Four bugs filed this session reached the tree criteria-less and have been restored from the fields files they were filed from.
- **An artefact-only commit no longer pays for both unit suites (BG0383).** `gate.test_relevant_paths` measures what the suites read, and `test_root_census.py` censuses the whole artefact workspace - so it recorded the bare entry `sdlc-studio`, `_minimal` absorbed the four narrow reads beneath it (`retros`, `trd.md`, `personas.md`, `prd.md`), and every path under `sdlc-studio/` answered relevant. Filing a change request cost about 334 seconds of suites over code no test asserts on. A census reads the tree's SHAPE: a file appearing, vanishing or moving changes its answer and the words inside one never can, so a test module may now declare `GATE_LISTING_ONLY` for a directory it lists rather than opens, and such an entry is relevant only to an add, delete or rename. The declaration is opt-in (an undeclared whole-tree read behaves exactly as before), it is ignored unless the module genuinely reads that directory, and it can never cover `scripts/`, `templates/` or `tools/`. `_minimal` now keeps narrower entries alive underneath a listing-only one, so a file the suites genuinely open keeps its content relevance. The pre-commit hook pipes `--name-status` so the change kind reaches the measurer, and `--test-relevant --format json` reports which entry matched - the collapse was previously invisible from the tool and had to be found by reading the read map by hand.
- **The seat brief names the goal under review, not the last one (BG0381).** `seat_brief` took no goal argument, so `goal-review brief --goal` was accepted, documented and silently discarded, and both branches let run state override unconditionally - including a CLOSED run. The seats were briefed on one goal while their verdict was recorded against another, and `plan --write` could not catch it because by then both sides named the same string. Precedence is now the caller's goal, then the plan's, then an OPEN run's - the stale-plan guard three lines away already recorded that reasoning; the goal was simply never held to it.

<!-- section: Added -->
- **A Sprint Goal is recorded and judged clause by clause (US0541, US0544).** A goal with more than one commitment was judged with one word, so a goal reached in two parts of three had to be reported as achieved or missed - both wrong. `goal_clauses` splits on semicolons and dashes always, and on commas only when the sentence carries the Oxford `, and` an operator uses to enumerate commitments, so a goal nobody wrote as separable parts comes back as ONE clause rather than being shredded. The verdict record carries the clause verdicts BESIDE the single word, and the close prints each. A run whose units all reached terminal while the goal was not achieved now says so in the headline: every number in that state looks like success, which makes it the most misreadable close there is.
- **A sprint carries its goal in its name (US0548, US0549, US0550).** `sprint_name` renders `sprint-<run id>-<goal slug>`, so a list of sprints says what each was for without opening it. The run id stays first and canonical and `run_id_from_name` reads it back out of any spelling - a goal is routinely reworded between the plan and the close, and a name resolving only through its slug would orphan every reference the moment it changed. A run with no recorded goal is named by its id alone; inventing a slug for a goal nobody wrote is the same error as reporting an unmeasured figure as zero.
- **The caller check reports a unit it cannot judge, instead of passing it (BG0379).** `mechanism_files` subtracts every `Affects` path a unit's own verifiers name - the rule that stops a test file counting as its own mechanism. A unit whose criterion points at a shell verifier INVOKING its only code file therefore has an empty surface, and `caller_findings` skipped it entirely: the check exited 0 whether the Caller declaration said something, said nothing, or was deleted. A unit that declared code and had every entry subtracted is now reported as `caller-indeterminate` with what to do about it, while a documentation-only unit is still not asked for a caller.

<!-- section: Added -->
- **A review round records how long it took, and the overhead ratio spends it (US0534, US0535).** No round carried a duration, so the review-and-repair component could only measure the span BETWEEN round stamps: nothing before the first round, and zero for rounds stamped together at close. The largest overhead component of the last two sprints was therefore reported UNMEASURED while the ratio, which derives delivery by subtraction, credited that time to delivery. A round now carries `started_at`, `ended_at` and `seconds`; an explicit figure wins, else it is derived from the stamps, else it stays UNMEASURED - never 0, because a zero is a measurement and inventing one is the error. A sum of real durations is exact; a mix of timed and untimed rounds stays a labelled floor.
- **A Sprint Goal verdict comes from a panel the author is not on (US0542).** `critic.goal_panel` returns a verdict per goal clause with the evidence each seat relied on, and REFUSES a panel containing the author rather than warning about it - the two-role rule protects every unit's sign-off and left the goal judgement itself unprotected. Disagreement between seats reports `partial` rather than the majority word, so a dissent cannot vanish into a number.
- **Both markdown lanes read one derived enumeration (BG0374).** The pre-commit hook's set was derived from `git ls-files`; the npm lanes were still the root glob plus one hand-added dot-directory, so `npm run lint` - which CI runs - remained blind to the three tracked files under `.github/` that the whole class started with. `tools/lint-md.sh` is now the single place that decides what "every markdown file" means, and both `lint:md` and `lint:fix` delegate to it. Two lanes with two enumerations is the same defect waiting to recur on whichever one is not updated next.
- **The review-currency carve-out is asserted across every delivery type (BG0373).** The concern was that the repair still reasons in stories, leaving the hand-edited status change reachable through a bug or a change request. It did not reproduce: the type is derived from the shipped table and the vocabulary, terminal set and in-flight states are read per type, measured across all three before any repair was attempted. What the finding's own Proposed Fix asked for, and what was genuinely missing, is the assertion - the property was pinned by a story fixture only, which cannot tell a type-general rule from one that happens to work for stories.
- **The overhead ratio now survives to `VELOCITY.md`, where a trend can actually be assembled (BG0372).** The ratio and its unattributed remainder were declared in `VELOCITY_COLUMNS`, computed by `_overhead_terms`, placed in the row dict - and then dropped, because `VELOCITY_HEADER` carried neither column and the row renderer's format string wrote neither. The measurement answered its question once per sprint and forgot it, which is the exact failure it was built to end. The header and the renderer now carry both, and `velocity_history` reads them back, so the round trip is closed. The criterion that was meant to hold this built its own header string and asserted the reader found the columns in it - proving the reader and saying nothing about the file the writer emits, with both criteria reading `Verified: yes` over the gap. It now pins the shipped constant and asserts a written value survives a read back. The legacy row fixtures derive their width from that header too, so adding a column can no longer shift every cell after it.
- **The overhead ratio reaches the velocity record (BG0372).** The delivery-against-overhead split was computed and reported at the close and written nowhere, and `VELOCITY.md` is the only file a figure survives in to be compared across sprints - so a measurement whose entire purpose is to show a TREND answered its question once per sprint and forgot it. The ratio and the unattributed remainder now join the velocity row, read from the report that owns the computation rather than recomputed, and absent rather than zero when the run could not attribute them: a 0 in that file reads as a sprint with no overhead, and the next plan reads that file as evidence.
- **The repeat report and the proposal path act on one pinned read (BG0371).** Each took its own read of the violation counts, so a violation recorded between them answered one question two ways and the proposal inherited whichever view it happened to see. Both now accept a pinned result and the close reads once. Half the finding did not reproduce and is recorded as such: violations are appended to a JSONL that `repeats` reads whole, so a count is the run's accumulated history rather than one call's sample - which is now pinned by a test so it stays true.
- **A recorded waiver is reported even when no judged unit carries it (BG0369).** The conformance lane's units are STORIES, and the waiver report is built from them - so a waiver scoped to a bug or a change request, or one whose scope resolves to nothing, emitted no line at all and sat silently in force. That is precisely the outcome the report exists to prevent. An unattributed waiver is now named with its stage and its decision, and a waiver a judged unit does carry is still reported once, per unit, because a line that fires on every run becomes noise and gets read past.
- **The pairing of a derived type directory with its index is pinned (BG0368).** The concern was that deriving the tree from the shipped type list might create directories only, leaving every newly covered type in the state a directory-with-no-index had just been established as. It did not reproduce - both derivations read one table and an index is created per type - and that was verified before any repair was attempted. What was genuinely missing is the assertion: nothing held the two together, so they could drift apart in silence. That guard is the delivery.
- **One ISO-8601 stamp reader, not four (BG0364).** `transition.py` and `loop_guard.py` each carried their own `%Y-%m-%dT%H:%M:%SZ` pattern - the form this project writes, and NOT the form the standard library writes - so the offset-bearing stamps that are live in this tree were refused there while telemetry accepted them. `run_state` was a fourth implementation, found while fixing the two the finding named. `sdlc_md.parse_iso8601` is now the single reader and all four delegate to it. A naive stamp is still refused: it names no instant, and calling it UTC would invent the one fact it is missing.
- **A scoped gate run is neither recorded as the baseline nor compared with it (BG0363).** The cost baseline was written on every CLI run, `--only` and `--skip` included. A scoped run covers a fraction of the lanes, so recording one LOWERED the number the next full run is judged against, and that run then read as a regression against a figure that never measured the same thing. The same defect read from the other side was the more misleading of the two: a fraction of the lanes compared with a full-run baseline reports a saving nobody made, and it looks like good news. A scoped run now says it is scoped instead of printing either.
- **Every index cell is derived, and `detect` counts a stale one (BG0380).** `reconcile` synced three cells - title, points, persona - from a hand-picked list, so a bug's Severity, an RFC's Status or a CR's Priority could disagree with its row while `drift_items` read 0, and the standalone `fields` verb that saw title drift was run by neither `detect`, `apply` nor the gate. `status.py` reads the index, so every backlog figure taken in that state was wrong. The row's own header is now the schema: a column is projected when the artefact carries a field of that name, so a column added to a type is covered without an edit. `status` keeps its dedicated writer (which knows about emphasis, the vocabulary and when to decline), and columns projected from OTHER artefacts are excluded by name. Three clobber routes the widening made reachable are each pinned: an off-schema row is skipped whole rather than written into by position, a second data block with its own header uses its own columns, and a projected value containing a literal pipe is re-escaped. 109 stale cells were repaired on this repo, including 79 bug rows carrying a severity in the Created column.
- **The criteria floor fires at the transition VERB, not only at the gate (BG0378).** A unit could not LAND at a terminal status with no acceptance criteria, but `transition set` still performed the change and the refusal arrived later, from a different tool, phrased as a validation error - defence at the gate rather than at the verb, leaving the working tree in the state the rule forbids. The verb now refuses, reading validate's own predicate rather than a second copy, and reports it alongside the other unmet requirements so one attempt names everything. Only a DELIVERED-terminal status: a unit ruled `Won't Fix` or `Superseded` was never built and owes no contract.
- **A close-down is owed for work that was BUILT, not for work that was ruled (BG0382).** `close_owed` accepted every status the terminal set contains, and that set mixes `Done`/`Fixed` (reached by delivering) with `Won't Fix`/`Superseded`/`Duplicate` (reached by deciding). A story ruled `Won't Implement` therefore demanded a retro accounting for work that never happened - an advisory no correct action can discharge, on the surface that exists so a skipped close is seen. The distinction is recognised by wording in `sdlc_md`, shared with the criteria floor above rather than kept as a second list of statuses.
- **A waiver whose scope names no unit is refused at record time (BG0361).** `record_waiver` validated the rule half of a subject and not the scope tail, so `rule:conformance:critiqued:pre-two-role` recorded clean and covered nothing: the close it was written to unblock stayed blocked while the log said the question was settled. The tail is now checked against the consumer's own grammar (`conformance.scope_tail_error`, imported rather than re-derived), and D0074's inert scope is corrected to the cohort its rationale always named.
- **A killed mutant records the test that killed it (BG0357).** `US0507` ships a consumer that nominates a test no mutation of its own module can kill, and it requires each killed mutant to carry its killer. `mutation.py` - this repository's only producer of mutation evidence - sent the runner's streams to `DEVNULL`, so the key was never emitted and the consumer took its refusal branch against every real report: loud rather than falsely green, but the capability was unreachable. The output is now captured and the failing node id parsed, for pytest and unittest alike, because a parser knowing one runner would attribute nothing for the other. Output naming no test attributes NOTHING rather than guessing: a fabricated attribution would be evidence about the wrong test.
- **A bug's acceptance criteria are executable, and the three guards agree about it (BG0356, BG0360).** `verify_ac run` walked stories alone, so a bug carrying authored criteria could not run them - a delivery lane's return rule (verify your unit before returning) was unrunnable for every bug in a batch, and the AC-verify Done gate, the release lane's unspecified-AC refusal and the close reconcile all spoke only for stories. Meanwhile `validate` warned that a bug's command-shaped `Verify:` was "executed by nothing" while `verify_ac` was about to execute it, and the creators refused to write one at all: three sites deciding the same question independently, two of them giving the author opposite advice about one line. A story and a bug are both DELIVERY units - planned, sized, held to the criteria floor, reaching a terminal status by being built - so a criterion on either has something to gate; a CR or RFC is a REQUEST, decomposed rather than delivered. That split now lives once, as `sdlc_md.EXECUTES_VERIFIERS`, and the runner, the validator and the creators all read it. `run --id`, `--from-run`, `--worklist` and `--ids` resolve bugs from the sibling `bugs/` directory, and a batch id with no unit file behind it refuses rather than being skipped as "not a story" - a silent skip is read by the completion gate as a unit that had nothing to fail.
- **Two more v2-only id readers now read both eras (BG0354).** `reachable_end_state` SKIPPED a unit whose id carries no comparable number, reporting a v3 ULID unit as reaching Done when the sign-off gate may well cap it - a fail-open in the one report that tells an operator how far a batch can get. An unanswerable comparison is now treated as past the cutoff. The commit-msg hook's paste-ready `Refs:` hint matched four digits only, so `BG-01JQK3F8` became `BG01JQ` - a hint producing a trailer that names a different, real artefact. It now uses the same grammar the engagement floor reads.
- **The constitution gate no longer pays for a Done-only conformance sweep no principle reads (BG0351).** Measured cold in fresh processes, the per-commit artefact gate was 32.9s and the constitution lane 26.6s of it - 81%, and the pre-commit hook described that gate to its reader as "fast, ~1s". Profiled, the 26.6s was 107 `pytest --collect-only` subprocesses inside `verify_ac.unresolvable_stamps`, reached because the two conformance-backed rules asked for the whole-workspace sweep, which computes the Done-only stages for every Done story. Those rules read `specified` and `verifiable`, the Definition-of-Ready signals, which are computed for every unit whatever the scope; checked over all 530 units, the two sweeps give identical answers. The rules now ask for the cheap ledger, detectors shared by more than one rule run once per check (the integrity census was running twice), and the memo is cleared at the start of every check so a second run can never be answered from the first tree. The hook's cost comment now states the measured figure and points at the gate's own `gate cost:` line, with a test refusing any claim that the whole artefact gate takes a second.
- **An all-skipped run is no longer stamped green for unittest, jest, vitest or go (BG0348).** The all-skipped hole was closed for pytest only, so a run whose every selected test was skipped still exited 0 and still passed the AC for every other family: unittest prints `Ran 1 test` then `OK (skipped=1)`, jest `Tests: 3 skipped, 3 total`, vitest `Tests 3 skipped (3)`, and none matches a zero-count signature. `unittest` is this repository's own default runner, so the silent pass was live on the path the project itself uses. Each family now has its own signature, read from its own summary: unittest compares the run count against the skip count, jest and vitest require their totals to be nothing but skips and todos, and go judges the per-test outcome lines that `-v` prints. A legitimately mixed run is untouched - `3 passed, 1 skipped` means a test ran. The reader gets the skipped remedy (un-skip it) rather than the re-point-the-selector one, because the Verify line is fine. Non-verbose `go test` prints `ok pkg` whether every test passed or every test skipped, so that one case remains undetectable and is documented as such.
- **Thirty-one terminal artefacts no longer carry an unfilled body scaffold (BG0347).** Widening the placeholder sweep from the acceptance-criteria section to the whole body found 62 findings the narrow check had never looked at: 12 closed bugs still carrying raw `{{symptom}}`, `{{steps}}` and `{{fix}}`, 11 epics whose Summary was `{{what this epic groups}}`, 7 change requests with their impact unfilled. A closed bug that never said what went wrong is indistinguishable from one nobody investigated. Every blank now STATES that the field was never filled and points at what does carry the record's substance - the title, the decomposition, the commits referencing the id. Deliberately not reconstructed: inventing what an author would have said is the false-evidence class this project files bugs about.
- **Two ratchet stories no longer specify incompatible designs (BG0345, BG0346).** One story described a count-based baseline recomputed from the corpus being judged - which can never fail, because the expected value is derived from the actual - while its sibling described a set-based baseline carrying a reason per entry. They now agree on the set form, and the burn-down is scoped to the same corpus as the ratchet it serves rather than a narrower one.
- **An artefact may quote the shell syntax it is reporting on (BG0344).** The tree-wide shell-hazard corpus assertion scanned stored artefact prose and could not tell quoting from damage, so evidence that quoted a command substitution or a lone backtick, because the defect being reported was about shell syntax, read as a field a shell had eaten and turned every committer's gate red. It happened twice on 2026-07-27 and both artefacts were resolved by rewording the evidence, trading fidelity for a green gate. Inline code spans are now masked before the corpus is fingerprinted, using a new shared `sdlc_md.mask_code_spans` that pairs backtick runs of equal length the way CommonMark does. The masking substitutes a word-like token rather than deleting, because deleting a span closes the spaces that flanked it and would manufacture the exact hole the fingerprints hunt for. The command-line path is deliberately unchanged: a value that arrived through a shell stays strictly checked whatever its backticks enclose, and only stored prose, which the filing path reads off disk and which crosses no shell, gets the quoting reading.
- **The pre-commit markdown lanes take their file list from the index, not from a glob (BG0341).** markdownlint's `**/*.md` cannot enter a dot-directory, and the hook answered that by naming one, `.claude/**/*.md` - so three tracked files under `.github/` (the pull-request template and two issue templates) matched neither glob and were linted by nothing per commit and nothing per push. Reproduced: a file at `.github/broken.md` violating MD032 lints clean under `markdownlint '**/*.md'` and fails when named directly. Both lanes now partition `git ls-files -z -- '*.md'` into the payload tree and everything else, so every tracked dot-directory is covered without per-directory enumeration and a newly staged file is linted by the commit that adds it. `.claude/worktrees/` stays excluded. The Node-absent SKIP message no longer claims CI covers what it skips: `npm run lint:md` still globs, so for those files the skip is total.
- **The provenance-tag style guard gathers the scripts and templates trees with find (BG0340).** `lint-style.sh` enumerated `scripts/*.py` and `scripts/lib/*.py`, so the shipped `scripts/hooks/close_guard.py` and every future subdirectory were exempt, and its YAML term covered only `templates/config*.yaml`, exempting `version.yaml` and `product-manifest.yaml`. A provenance tag in any of them passed both the pre-commit style lane and CI. Both trees are now gathered with `find` (the templates markdown already was, because that tree nests, and the scripts tree nests just the same), so a new subdirectory is covered without list maintenance. `scripts/tests/` is carved out deliberately and pinned by a test, rather than by omission: a test docstring naming the artefact it derives from is traceability in the one place no consuming agent reads it against its own project.
- **A tracked file the neutrality guard could not read is no longer reported clean (BG0339).** `check()` caught `OSError` per file and continued, so a file that could not be opened at all was scanned as if it were empty and `main()` printed "no blocklisted project names in tracked files" and exited 0. That is precisely the silent pass `_tracked_text_files` refuses by name three lines above, where a failed `git ls-files` raises rather than report a clean scan of nothing. The read failure now gets the same treatment: unreadable files are collected and the scan ends in a refusal naming each one and the error, stating how many findings were present in what it did manage to read. Decoding cannot fail (it uses `errors='replace'`), so the caught error is only ever a file that was never read.
- **The jest batch cache selects tests the way `jest -t` does (BG0337).** The cache resolver claimed to mirror `jest -t` but matched by Python substring containment, where `-t` is a `testNamePattern` regex. A pattern such as `renders the total$` therefore resolved against every name merely containing it, so the cached verdict was computed over a different set of tests from the one jest would have run - and under `--release` that cache stands in for the authoritative run in a blocking lane. Matching is now `re.search`, and a pattern Python cannot compile returns no verdict at all so the caller falls through to the authoritative per-AC subprocess.
- **The review-currency close-bookkeeping carve-out reads a status change's direction and values (BG0336).** A changed line counted as the close's own bookkeeping whenever it merely contained one of five substrings, so a hand-flip of `Status` from Draft or Blocked straight to Done, and a reopen of a terminal status, were both waved through as "the close recording a verdict already reached" - and `gate --require-review` printed PASS over a status change no reviewer ever judged, for every status edit since the last review. Only a move into a terminal status, from a non-terminal one, out of the implementation states the delivery loop actually parks a unit at, is now exempt; each of those three facts is read from a declared vocabulary (`terminal_statuses`, the type's status vocab, `transition._IMPL_TARGETS`) rather than a list kept at the call site. An unknown type, an unreadable value, a `Status` line added or removed rather than changed: all fall back to substantive, because an exemption granted on an unanswered question is the failure this lane exists to prevent. The close's other stamps are untouched and still exempt.
- **The manual-evidence Done gate no longer disarms itself when it cannot read the story (BG0335).** `transition._acs_missing_evidence` returned two empty lists on any exception, and two empty lists are exactly what a fully-evidenced story looks like - so a broken `verify_ac` import or a story the parser choked on told the Done gate "nothing is owed" when the truth was "nothing was looked at", and an all-manual story reached Done with nothing checked. The helper now reports the failure alongside the two lists, and the gate turns it into a refusal that names the underlying error. `--force` still overrides deliberately.
- **The Product seat's worked example quotes a real End goal (BG0333).** Its first Craft Goal is that every story traces to a REAL End goal, "not a guess" - and the example demonstrated that behaviour by tracing to a sentence the Primary persona's card does not contain. A worked example is how a seat is learned, so an example doing the thing the seat refuses teaches the refusal away. It now quotes End goal 2 verbatim and by number, and a guard asserts every End goal any seat quotes appears on a persona card - a containment test, so it cannot be satisfied by writing the expected sentence twice.
- **The TSD states the script tier as a SET, not a count (BG0332).** It pinned "58 scripts and the six-module `lib/`" against a tree carrying 70 and 5 - about a fifth short, in the only inventory bounding the unit-test scope, in a document whose own rule is not to pin drifting numbers. Restated as the set with the census named, matching the convention the TRD already adopted, and `tools/tests/test_spec_counts_are_not_pinned.py` holds both specs to it - comparing against the census rather than against a second number written in the guard, since a guard carrying its own copy of the count is the defect it exists to catch. The revision history keeps the old numbers, because a number that WAS true belongs in a record.
- **The gate's reconcile lane counts every drift source `reconcile detect` counts (BG0331).** The lane summed `detect_type` plus one sweep-assembled kind, so `meta-index`, `epic-breakdown` (including ticked-early, the direction that masks unfinished work), `epic-points`, `link-asymmetry`, linked-epics and `undecomposed` were exempt by omission: a tree on which `reconcile detect` exits 1 passed the pre-commit hook and CI, and the documented gate disagreed with the executed one. The sweep is now a single function, `reconcile.detect_all`, that `cmd_detect` and the gate lane both read, so neither can hold a smaller idea of what drift is; the "awaiting another gate" carve-out is derived from each item's `blocked_by` rather than from a second call to the one detector that sets it today. The correctness costs about 20s a commit, because the newly-counted detectors re-read the artefact corpus per unit; the gate states the total and names the dominant lane on every run.
- **The engagement floor reads both id eras, so a schema-v3 project is actually judged (BG0328).** Every floor entry point matched `(US|BG|CR)-?\d{4}` - the v2 four-digit form and nothing else. A v3 short-ULID id matched nothing, and neither did a five-digit id (the trailing word boundary refuses the fifth digit), so the pending lane dropped such units before judging them, the git leg read a mixed-era batch subject as solo and handed the whole shared file set to the v2 id, and the multi-id commit-message rule never fired: the floor reported clean while checking nothing. The grammar now mirrors `sdlc_md.ID_RE` narrowed to the judged types, with a companion pattern for normalised ids. The multi-id nudge also prints ids as written rather than normalised, because a v3 id's dash is load-bearing and `Refs: BG01JQK3F8` would have been a pasted remedy that did not satisfy the rule printing it.
- **The neutrality guard scans every tracked file, not a hardcoded suffix list (BG0327).** `check_neutrality.py` selected files by an allowlist of twelve text suffixes, so 46 tracked files were silently exempt from a checker whose whole contract is "no private name in any tracked file": every `templates/automation/*.template` (instantiated into every consuming project, so the highest-risk leak site of all), all 31 `retros/evidence/*.jsonl` logs, the extensionless `.githooks` scripts, `CODEOWNERS`, `LICENSE` and `.version`. A leak in any of them committed and shipped green. The selector is now a denylist (`_scannable`): every tracked path is scanned unless it is the checker's own source, a lockfile, or a suffix that is binary by definition, with a null-byte sniff for a payload that is binary in fact rather than by suffix. An allowlist exempts whatever nobody thought to enumerate; a denylist fails towards scanning.
- **RFC0052 tells one story (BG0320).** It carried a Superseded status naming no superseder (unlike RFC0019 and RFC0054, which name theirs), a triage line saying DELIVERED, and its sole decision still Open - three contradictory records, any two of which leave the third to rot. A delivered RFC is not a superseded one: the status is Accepted, and D1 records which options shipped and the artefacts that delivered them.
- **The two-role review gate no longer stands down for v3 ULID units (BG0318).** `review.two_role_after` is a sequential cutoff compared against `id_number`, which has no number to give for a short-ULID id - so `two_role_applies` was False for every v3 unit and both halves (adversarial evidence, reviewer-of-record sign-off) defaulted satisfied, unchecked, on exactly the newest work a forward-only cutoff exists to cover. The comparison now lives in one shared `two_role_applies_to` used by both the stage computation and the required-stage list, and it fails closed: an id with no sequential number is by construction later than any cutoff, so the gate applies. A project with no cutoff configured is unaffected.
- **A tag is refused while any delivery unit owes a close (BG0311).** The specs documented `--require-close` as a blocking push-or-release guard and it ran at NEITHER moment: the lane bound only when a flag nobody passed was given, `--release` did not imply it, the prescribed pre-release command is a plain `gate.py --release`, no pre-push hook exists and CI ran the plain gate - a ceremony with no detector, which is the exact failure the lane was built to close. `release_cut.tag_check` now refuses, naming the units. The TAG rather than `--release`: that flag is a documented contract consuming projects depend on, and quietly adding a blocking lane changes their gate too. The tag rather than every push: this project commits straight to main in small green units, so blocking a mid-sprint push would train the bypass.
- **Every spec's version tracks the product version, and a checker reads it (BG0310).** Both specs stated "the document version tracks the product version" and declared 4.1.0 after 5.0.0 was cut; `check_versions.py` never referenced them and the doc-freshness lane covers `LATEST.md` only - a rule the documents state about themselves that nothing enforces is true until the day it matters. The PRD, TRD and TSD are now authoritative homes for the version check, held only when they DECLARE one (absent is "not a home", so a project that never adopted the convention is not failed by it), and both the plain and blockquoted spellings are read. The guard immediately found a third drifted spec the finding had not named.
- **No spec claims the suite runs in under a minute (BG0309).** Both anchored scaling and gate-design claims on "2,500+ tests in under a minute" against recorded runs of 215-265s and 80-90s - stale by about 3x on time - while AGENTS.md documents the hook skipping the suites precisely because they are too slow to pay per commit. The performance characterisation of the primary gate now points at the live measurement (`tools/gate_timing.py estimate`) and says minutes, and the NFR row points at the gate's own budgeted, per-lane cost rather than a pinned figure.
- **The specs agree on whether the cost instrument is falsified (BG0308).** The TSD told its reader the token forecast "is currently falsified out-of-sample (0.55x)" citing a PRD section that documents the opposite: complexity was falsified, Fibonacci points replaced it and cleared a pre-registered bar. The two specs contradicted each other on whether the shipped instrument is known-broken or validated. The TSD now describes the shipped points model and names what was falsified and replaced.
- **No live document points a reader at the retired `review generate` (BG0307).** RFC0033 folded it into `audit` and the retirement shipped - the script is gone and `help/review.md` redirects - yet the PRD still marked the feature Complete with the deleted script in the Location column the PRD itself defines as naming the backing script, and the Secondary persona was defined around "points `review generate` at the inherited repo". Anyone designing the brownfield on-ramp from the registry was sent to a command that cannot be run. The PRD row, the persona narrative and the registry line now name `audit --profile repo` and the files that actually back it.
- **Shell-hazard scan exempts code blocks (BG0301).** The fingerprints in `file_finding.py` over-flagged legitimate technical prose: a two-space column-alignment gap read as a collapsed command substitution, and a fenced-code marker (or a lone backtick) made the backtick count odd. Because the tree-wide catch-rate gate asserts zero false positives, one such artefact turned every committer's gate red until the prose was reworded. Fenced and indented code blocks are now stripped from a field before any fingerprint runs - a code illustration is not a stored command - with regression fixtures that genuinely trip each rule unstripped, so the exemption is proven rather than assumed.
- **`manual` is no longer a Done gate-bypass (BG0300).** A story whose acceptance criteria are all `manual` used to reach Done with the verify gate checking nothing - so the more irreversible the work, the less it was gated. The Done gate now requires each manual AC to carry a `**Verified:**` marker (evidence a human observed the outcome, and when) and refuses the transition when one is bare, naming it. The gate still never tries to evaluate a manual criterion; it requires the evidence that a human did. `verify_ac` never stamps a manual AC, so this marker cannot be auto-satisfied by running the verifier.
- **`sprint plan` no longer crashes on every invocation in a project whose TSD declares test levels (BG0299).** `cmd_plan` builds `data["batch"]` as unit records (dicts), but `_print_test_strategy` handed them straight to `test_strategy`, whose contract is a list of ids - so `norm_id` was called on a dict and every plan died with `TypeError: expected string or bytes-like object, got 'dict'` before printing a line, on both text and json output. The caller now projects the records to ids at the boundary, keeping the honest `list[str]` contract. The crash slipped through every existing plan test because a fixture without a `## Test Levels` TSD makes `test_strategy` early-return before it iterates the batch; the regression test now seeds one so the batch loop actually runs.
- **`reconcile` swept eight of the nine artefact types, so the issues index was censused by
  nothing (BG0330).** `DEFAULT_TYPES` and `SCOPE_TYPES` were hand-written and omitted `issue`, and
  no `--scope` named it either, so status-mismatch, missing-row, orphan-row and count drift under
  `sdlc-studio/issues/` were exempt from detect, apply, the index-derived check and the commit gate
  - while the per-type machinery worked perfectly and only a transition-time `apply_type` ever
  called it. Both lists are now DERIVED from `sdlc_md.ARTIFACT_TYPES` (the convention `archive.py`
  already followed), `--scope issues` exists, and two guards compare each list against
  `ARTIFACT_TYPES`, so re-hardcoding either one, or adding a tenth type without a scope, reddens
  rather than quietly exempting a whole index.
- **The guided classifier called a repo full of source greenfield unless it carried one of six
  manifests (BG0312).** `classify_path` keyed entirely off the DETECT marker list, so a C/C++,
  Ruby or PHP tree, or a Python project with only a `setup.py`, read as an empty repo and the PRD
  stage sent it down the greenfield INTERVIEW instead of generating its PRD from its own code -
  the exact wrong fork the guided flow exists to avoid. A manifest-less repo now falls through to a
  census of the source files themselves: a wide extension set (the question is whether code exists,
  not which stack it is), version-control, dependency and build directories pruned so a vendored
  tree is never mistaken for this project's source, returning on the first hit and bounded, so it
  stays cheap on the orientation path.
- **The agents stage skipped a missing starter template in silence (BG0334).** `stage_agents` passed
  over an absent template with a bare `continue`: the file appeared in neither `created` nor
  `skipped`, so the first stage of onboarding drafted nothing, said nothing, and the operator
  confirmed it. It now refuses, naming the missing starter, and refuses BEFORE writing anything, so
  there is never a half-drafted stage to confirm. The two verifiers that should have caught it were
  strengthened at the same time: one asserted the bare substring `epic` (satisfied by the word
  'epics' in the surrounding prose) and never mentioned the story command, the other asserted
  `AGENTS.md` but not the `CLAUDE.md` import its criterion claims - and Claude Code reads CLAUDE.md,
  not AGENTS.md.
- **Five markdown parsers still toggled on any three-character fence run (BG0349).** The naive
  toggle treated every `` ``` `` as a closer, so a four-backtick block released on its inner fence
  and everything below it was read as live document. All five now call the ONE shared CommonMark
  tracker, `sdlc_md.fence_step`: `iter_tables` (the widest - it governs the table-row counting
  reconcile consumes, which is the index-corruption class), `persona_registry`,
  `file_finding._strip_code_blocks`, `persona_resolve.seat_name`, and both fence walks in
  `tools/check_links.py`. Two rules a toggle cannot express: a block closes only on the same marker
  at the opening run length or longer, and a closing fence may carry no info string.
- **The finding filer names a test file the declared footprint leaves out (BG0343).** `Affects` is
  where the FIX lands, not where the evidence was read, and this project's doctrine says a fix
  arrives with a test - yet 54 artefacts filed from one audit declared a single source file and not
  one named a test. An understated footprint causes silently the same three harms a fictional one is
  refused for: it mis-groups the unit in the plan's collision analysis, under-reads it in the
  engagement floor and misreports it in gate's changed-surface pass. The filer now reports, at
  filing time, each declared source file whose companion test EXISTS on disk and which `Affects`
  does not name - including the package-sibling suite one directory up (`scripts/lib/x.py` tested
  by `scripts/tests/test_x.py`). It names the path rather than inventing one, so it stays silent
  where no test exists, and it warns rather than refuses, because losing the finding in hand is
  worse than an understated footprint.
- **An all-skipped run was still stamped green for unittest, jest, vitest and go (BG0348).** The
  earlier repair closed the hole for pytest only. Every other family exits 0 on a run where nothing
  executed and prints a summary carrying real counts, which none of the zero-count signatures match:
  `Ran 1 test` beside `OK (skipped=1)`, `Tests: 3 skipped, 3 total`, `Tests 3 skipped (3)`, and a
  `go test -v` whose every outcome line is `--- SKIP`. `unittest` is the one that mattered most - it
  is this repository's own default runner, so the silent pass was live on the path the project
  itself uses. Each family now has its own all-skipped signature, read from that family's own
  summary and nothing else. A legitimately mixed run is untouched, because the counts are compared
  rather than pattern-matched: `Ran 4 tests` beside `skipped=1` means three tests really ran, and
  unittest counts are summed across the blob so one empty run beside a real one is not vacuous. A
  `todo` counts with the skips, since it never ran either. The reader gets the skipped remedy
  (un-skip it) rather than being told to re-point a selector that is fine. Non-verbose `go test`
  prints `ok pkg` whether every test passed or every test called `t.Skip`, so that one case carries
  no signal and is documented at the signature rather than papered over.
- **The jest batch cache matched patterns by literal substring where `jest -t` is a regex
  (BG0337).** The resolver's docstring claimed to mirror `jest -t`, but selected assertions with
  Python containment, so a metacharacter-bearing pattern computed its verdict over a different test
  set from the one jest would run - and under `--release` the cache stands in for the authoritative
  run in a blocking lane. `renders the total$` now selects only the anchored match instead of
  everything containing the phrase. A pattern Python cannot compile is not a verdict either: the
  resolver returns `None` and the caller falls through to the authoritative per-AC subprocess, which
  owns the answer.
- **The id allocator read a meta id past 9999 as its first four digits (BG0338).** `RETRO10000` came
  back as 1000, so the allocator computed its maximum from numbers no file holds and handed out an
  id already on disk - with a different title slug the `path.exists()` guard does not fire and the
  duplicate lands. `sdlc_md.id_number` was widened to 4-7 digits for exactly this class and the
  sibling reader was left behind; both now admit the same range, and a longer digit run is refused
  outright rather than truncated to its first seven digits, which would only move the same defect.
- **Every artefact index asserted a `Last Updated` date no writer maintained (BG0342).** Five
  indexes claimed a freshness up to five weeks older than rows they already carried, and `detect`
  reported no drift, because the stamp sat outside every check - a false assertion in the ledger
  files agents are told to trust. The header is now derived like any other index cell: a stamp
  behind the newest date on its own rows is `stale-index-stamp` drift, `apply` restamps it from the
  rows and says so, and because every mint appends through the shared index writer (which finishes
  by calling `apply`), a new row leaves the header current. It is judged against the rows and never
  against the clock - a clock-stamped header would re-drift every index in every project at
  midnight; a header level with or ahead of its rows, or an index carrying no stamp, is not flagged.

### Breaking (opt-in; the next release is semver-major 5.0.0)

- **The two-backlog workflow and the Fibonacci sizing model are a breaking change - but opt-in
  (EP0037, RFC0040).** The hard gates (plan refuses a request, terminal status derived from
  children, `undecomposed` drift, CR-creation Size demand) are OFF by default, so an existing
  project upgrades with zero disruption and keeps its old flow until it sets `two_backlog.enforce:
  true`. The upgrade path is three steps - `migrate_v3.py sizing` (convert requests/containers to a
  T-shirt Size deterministically; report the delivery units that need re-sizing and the accepted
  requests that need refining), `refine` the accepted requests, then turn `enforce` on - documented
  in `reference-upgrade.md#two-backlog-migration`. The sizing migration only ADDS a `Size:` line and
  the workflow is one config line, so the upgrade is reversible.

### Added

- **`sprint_report.py operator-summary` - the decision-grade page an operator leads from (US0645).** What shipped and who signed it, what was rejected and in what repair state, what is carried and under which filed id, what it cost, and the one or two judgements most worth overturning. Human in the LEAD rather than in the loop: the seats judge at their speed, the operator reads and reverses at theirs.
- **Every field is a READ of the ledgers, and no channel carries anybody's prose into it (US0645).** A seat writing its own summary is a seat marking its own homework, and the operator would be leading from an account with a stake in the answer. The test varies a verdict's free text and asserts the summary does not move.
- **A component with no record reads UNMEASURED, never zero (US0645)** - omitting it would let a run that measured nothing read as a run that cost nothing. The summary is generated identically for a human sign-off and states the capacity, because a second code path for the human case is a path that drifts.
- **A sign-off records the CAPACITY it was given in: `human` or `seat` (US0644).** A panel sign-off was distinguishable only by string-matching the `panel(...)` marker inside the free-text chain - a fact a reader can find and a filter cannot rely on. The point of recording a seat's signature is transparency about who judged, and transparency a machine cannot read is transparency in name only.
- **An absent capacity never reads as `seat` (US0644).** The direction this must not fail in is a machine's signature being taken for a person's, and every row without the column predates seat sign-off entirely.
- **A row short by the new trailing column is still read (US0644).** Widening the table with an exact-width reader would have silently un-signed every unit signed before it, and the two-role gate would have started refusing them - a quiet loss found by mutation rather than by review.
- **`sprint plan --write` assigns the sign-off panel when the project has adopted one (US0643).** Panel sign-off ships fully built - the two roles held disjoint, the signer read from the run rather than named at signing time, the brief-provenance interlock, three distinct contexts enforced - and was reachable only if somebody remembered to run `persona_resolve.py panel --ceremony signoff` by hand first. A run that forgot it reached its close and could not be signed off at all, so the whole path stayed theoretical. LL0027: a gate belongs in the command people actually run.
- **An unassignable panel refuses at PLAN time and leaves no run behind (US0643).** Discovering it at the close strands a delivered run behind a sign-off nobody can give, and a half-opened run is worse than none - the next plan of any other batch is refused as disjoint against it.
- **A project on the shipped `operator` policy is untouched (US0643)** - no assignment, no change to the plan's output. An upgrade never moves the bar under anybody.
- **The refusals are pinned through the shipped verb (US0643)**, including the assigned-signer check that lives in the CLI path and is invisible to any test calling `record_signoff` directly - with the positive control beside them, because a path that refuses every panel sign-off passes every refusal test for the wrong reason.
- **The review tier is derived from the unit's risk band, recorded on the verdict, and READ by the coverage predicate (US0641).** `route.py` said it in its own header - "Advisory only - no gate reads a tier" - and that had been true since the score was built: a deterministic 0-100 difficulty with bands and a confidence, stamped on every unit at plan time and consumed by nothing but `plan_review`. `critic brief --tier` existed and was cosmetic, substituting one sentence into a prompt that was never recorded, never read and never checked. All three steps now land, and the third is what makes the other two worth anything.
- **A light verdict does not cover a unit the band tiers full (US0641)**, and the gate names the tier shortfall rather than reporting a missing approval that is sitting in the log. An explicitly chosen light tier does not stand the gate down either - a gate an operator can disarm with an undeclared flag is not a gate.
- **Nothing is applied backwards (US0641).** A verdict carrying no tier covers, in both spellings of absent: the `-` marker the current writer uses and the missing cell on a row that predates the column. The rule would otherwise re-open every closed unit in the corpus for a fact nobody could have recorded.
- **The band distribution is asserted against the real corpus, not a fixture (US0641).** A band that always resolves the same way is a config key wearing the appearance of a gate, and every other test would pass. The sample is strided across stories and bugs because the first N bugs by id are the oldest ones and banded uniformly - a sample that would have reported this gate degenerate when it is not.
- **`plan_review.enabled` decouples the plan-review gate from the schema version (US0640).** The gate hard-returned `dormant (schema v2)` with no config key at all, so the one hard, deterministic, risk-proportional gate in the codebase - the model the rest of the ceremony work copies, and the one `--force` cannot bypass - was reachable only by adopting the v3 id format, the inbox status and spec-guard across every artefact a project holds. It is a review policy and has nothing to do with the shape of artefacts.
- **One shared enablement predicate, not a second copy (US0640).** `config.feature_enabled` now holds the knob-then-schema resolution that `triage_noise.active` had spelled out, and both adopters call it. Two copies are two answers to the question "is this on", and they drift the moment either is touched. The test proves the sharing by replacing the shared predicate and asserting BOTH adopters follow.
- **An unset knob changes nothing for any existing project (US0640), and the dormant reason names whichever thing actually decided** - the knob when a project stated one, the schema version otherwise. Reporting "schema v2" to a project that deliberately set `enabled: false` would send a reader to a migration they do not need.
- **The duplicate groups no collection can answer are derived and named one by one (US0637).** A group whose selector `selector_resolves` answers `None` for cannot be split into discriminating halves, because nothing can say what either half selects. Those groups are now derived AT LINT TIME by asking the resolver, never read from a list in a document - so a group that becomes answerable, or stops being, moves in and out of the set without anybody editing prose. Each member is printed on its own line with the verb that makes it unanswerable and every AC claiming it: a reader told "6 groups are exempt" cannot tell an exemption that still holds from one that quietly stopped being true, and a count cannot be taken apart. An unanswerable group is no longer also told to split into discriminating halves, which was advice its author could not take.
- **`retro.py accuracy` reports passes spent on test-plan review beside passes spent on code review (US0634).** Read from the two verdict ledgers and from nowhere else: this is the claim EP0207 makes, so a figure anybody could type in would be an assertion wearing a measurement's clothes. Only the run's own units count, and only the `test-plan` kind - a spec review billed as a test-plan review would measure work nobody did.
- **A phase that was not in force reports that, never 0 (US0634).** A run predating the cutoff spent nothing because the ceremony did not exist; a run that held plan reviews and spent nothing on them would be extraordinary evidence. A bare 0 says the second while meaning the first, and no ratio is invented from an absent denominator.
- **A criterion whose mutant cannot be named is refused at grooming (US0633).** `sprint breakdown` reports it read-only and `sprint plan --write` refuses, on the same terms it already refuses a unit lacking `Affects` or `Points`. A bare `unnameable` is MALFORMED rather than a declared exemption, and the reason is measured for substance so `-` and `n/a` do not buy one: a state that costs nothing to enter is the state every awkward criterion ends up in.
- **`mutation.py run --story <id> --from-plan` (US0632).** Each planned mutant is joined to the mutation ledger and reported killed, survived or `not-run`. A row never executed is its own state and never folds into a pass: a plan written and never checked is the same paperwork problem one level up. The join is on a `criterion` recorded at registration, never on the mutant's prose - a substring match would credit one criterion's execution to another's row, and a matching rule that is convenient is a gate that is optional. The WORST verdict per criterion wins, so a later kill cannot cancel an earlier survivor.
- **A planned mutant that is unexecuted or alive refuses the terminal transition (US0632).** Reported by `transition.py requirements` before the work rather than discovered as a refusal after it, and the message names the CRITERION whose test failed to notice, because the finding is about the test. Behind the dated `review.test_plan_after` cutoff on the same terms as the two-role gate: a gate that refuses an existing backlog wholesale is one that gets switched off wholesale.
- **A reason-less `unnameable` no longer clears the delivery gate (US0632).** US0633 makes the marker cost something at grooming; exempting a malformed one here refunded that cost one lane later and made it a free pass at the gate it matters most at.
- **US0632 AC3 is CARRIED UNMET, and its narrowing retracted (US0632).** The delivered version claimed the anchor-uniqueness limb was undeliverable because the engine selects by AST node. That is false: it counts regex occurrences, and only the enumerator excludes multiline-string spans, so a mutant reported at one line is applied at another. Two seats proved it by execution. The property is deliverable, this unit does not claim it, and the real desync is filed as BG0533.
- **The AC3 retraction is now real in the fields the tooling reads (US0632).** Marking a criterion undelivered in prose while leaving `**Verified:** yes` on the line `verify_ac` reads is not a retraction - the tool re-stamped it green from a test that does not exercise the property, so every mechanical reader still saw it met. The undelivered limb is split into its own criterion carrying NO verifier, so the tooling reports it unverified because it is. A seat caught this; it is the same class as BG0530, committed in prose about my own work hours after filing it.
- **`critic.py brief --phase plan-review` (US0631).** The pre-code brief: the seat charter, the unit's criteria as law, and the test-plan rows as the object of review. It carries NO diff scope, and the absence is the point rather than an omission - there is no diff yet, that being the premise, and a brief that asks for one teaches the reviewer to wait for code. The claim-inventory pass is absent for the same reason: it rules on prose in a diff. A `--tier` is refused, because `record_verdict` already refuses one on this phase and a brief that accepted it would promise a depth the ledger cannot record. Where no plan exists the brief says so and names the command that derives one, rather than presenting an empty section a reviewer could approve.
- **The plan-review provenance loop closes through the shipped verbs (US0631).** `brief --phase plan-review` returned before printing its fingerprint, while `record` refused without one and told the reader to use "the fingerprint it printed"; and the matcher asked for a DELIVERY brief whatever phase was being recorded, so a correct plan fingerprint was flagged as unrecognised while a delivery one was accepted as provenance for a plan review. Both seats found it independently. It is verbatim the scar AGENTS.md cites, in the phase added to prevent it.
- **A unit reaching implementation without a REVIEWED test plan is refused by the command that starts the work (US0630).** `transition.py set --status "In Progress"` holds it, and `transition.py requirements` states the demand before any code is written rather than after it - a gate discovered by finished work is a tax, and a tax is what gets forced. "No plan" and "plan not reviewed" are DISTINCT refusals: the two have different fixes, and being sent to the wrong one of "write a plan" and "get it reviewed" is not a small error when the claim is that reviewing the test is cheap.
- **The test-plan gate is keyed to its own review kind (US0630).** It sits beside the spec plan-review gate and neither discharges the other, which is exactly what BG0510's `Kind` column shipped for. A spec approval does not clear it - that reviewer never saw a test plan - and neither does a self-review. Behind the dated `review.test_plan_after` cutoff, so an existing backlog is not retro-refused.
- **The test-plan and planned-mutant gates fail LOUD (US0630, US0632).** Both swallowed every exception and returned None, which is PASS - so the one condition under which either was least able to judge was the one under which it approved everything. A seat made the verdict ledger unreadable and watched a refusal become exit 0 with nothing on either stream. Two sibling gates in the same file already fail loud for this exact reason.
- **An unreadable `.config.yaml` no longer switches both new gates off (US0630).** `project_override` swallows every config fault and returns the default, so a malformed, non-UTF-8, unreadable or directory-shaped config read as "this project set no cutoff". The sibling `_two_role_gate` already solved this with `_config_unparseable`, and its comment names the same four shapes - the repair reached parity with that gate's ledger half and skipped its config half. A project that DECLARES the rule and then cannot be read has not waived it.
- **`verify_ac.py testplan derive` (US0629).** A unit's test plan is derived from its acceptance criteria rather than assembled by hand, naming per criterion the production change its test must fail on. The row count is checked by TWO INDEPENDENT READERS - `parse_story` reads the whole file for `### ACn`, `sdlc_md.count_acs` reads only the Acceptance Criteria section and also counts bare checkbox items - because counting criteria from the list the rows were built from makes the equality tautological and the mutant that deletes it survives every fixture. A duplicate criterion id is refused outright: a plan keyed by criterion cannot carry two rows under one id without one criterion going unplanned.
- **A mutant field must name a production edit, on four checkable properties (US0629).** Blank, no path drawn from the unit's own `Affects`, no edit verb, or more than 60% meaningful-token overlap with the criterion's own `Then` clause. The path is EXCLUDED from that overlap: naming a file is separately required, so counting those tokens as novel substance lets a restatement buy headroom under the ceiling with the very words it was obliged to write. With them counted, US0629's own discriminating pair reads 57%/33% and the restatement passes; excluded, it reads 67%/40% about the stated ceiling and the threshold is the thing under test rather than the examples.
- **`testplan derive` never overwrites a plan it cannot read (US0629).** It harvests `| ACn | mutant |` rows only, so a plan authored as prose yielded none and the section was replaced with placeholders at exit 0. A seat ran it against US0629's own artefact and watched 178 lines become 79 - an independently-reviewed plan destroyed by the command meant to protect it. It now refuses and says why. The overlap ceiling is also the first REFUSED value rather than the last accepted one, and a criterion with no `**Then**` bullet - the house bug template's shape - measures its overlap instead of silently scoring zero.
- **Re-running a finished close over an unchanged tree is now a no-op that says so (US0619).** The close was run three times on one run and repeatedly on the next, and from outside that read as a sprint that was never being closed. It was: each close was undone by the next repair, and each re-run re-derived an account that could differ from the one before it. The close now stamps a digest of the tree its account describes, and a later close over that same tree reports the run already accounted for, writes nothing, and exits zero - so re-running is free and an operator who is unsure whether the ceremony finished can CHECK rather than guess, which is exactly the behaviour a close-time gate makes people want. "Unchanged" means the TREE, not `HEAD`: a close is followed by commits - its own paperwork - so a check keyed on the commit id would report "changed" after every close and never short-circuit, and would report "unchanged" while an uncommitted repair sat in the tree. The digest is a real git tree object built in a throwaway index, so it is a function of content alone and staging cannot move it. A run still open is never short-circuited, because its first close has not happened; a genuinely changed tree re-runs normally, since this is an idempotence guarantee and not a lock; and a digest that cannot be computed declines to short-circuit, which errs towards doing the work.
- **An unavoidable close-time repair can be recorded as a reasoned, per-unit override (US0618).** US0616 refuses the inline repair and US0617 makes the residue readable; this is the deliberate way through for the case where deferring genuinely is not an option - a defect that makes the close itself wrong, for instance. It is written in the retro as `> **Close-repair-override:** <UNIT> - <why>`, travelling with the record rather than in a command flag, on the same reasoning as the velocity override beside it: an escape nobody can read afterwards is a silent pass. A BARE marker is not an override, by that same existing rule - an exception has to cost a sentence, or it becomes the routine the rule was written against. It is per unit, so one exception cannot license the next, and an override naming no unit forgives nothing rather than forgiving everything, which is the blanket exemption this is specifically not. Recorded overrides are counted and printed with their reasons on every run: an override nobody sees is indistinguishable from the inline repair the rule forbids.
- **`sprint close` and `sprint stop` now refuse while the tree carries a repair to one of their own batch units (US0616).** The close writes an account of the batch and then stamps the ledger that says the batch is accounted for, so anything reaching terminal after that stamp is unaccounted by construction - and a repair made *inside* the ceremony invalidates the account written moments earlier. RUN-01KYZKY5 hit it twice in one close, and from outside it read as a sprint that was never being closed. It was, repeatedly, and each close was undone by the next repair. The refusal names the unit, the offending path, and both ways out: commit it as batch work before the ceremony starts, or file it and let the next run carry it - a refusal that leaves the operator to work out the remedy is the shape that gets bypassed. `stop` is gated on the same terms because a stop writes the same account, and the last run was stopped rather than closed, so a gate covering only `close` would have left the route actually taken ungated. Scoped to the batch's own declared `Affects`, never to any dirty file: a guard that stopped every close over an unrelated edit would be switched off within a sprint, and then it would guard nothing. `--dry-run` reports the condition instead of refusing it. The rule now sits in `reference-doctrine.md` and `reference-sprint.md` as well, each naming the command that enforces it - a rule stated with no gate behind it is a known-weak rule, which is why the statement and the gate ship as one unit.
- **`sprint review-batch --fields-file` reads the findings from a JSON document**, so prose
  carrying backticks or `$(` is stored verbatim rather than executed by the shell. A review's
  findings are exactly the text most likely to contain both - this project mangled its own
  twice in one run, and once quoted the mangled output back into an artefact.
- It uses `resolve_prose_fields`, the loader every other writer already shares, so the
  fields-file spelling cannot drift from theirs. The flag path is unchanged: this is an
  addition, not a migration.
- **`status.py points` answers how much delivery work is left, in POINTS, by type and by
  status.** The routine question had no home: `status` reported counts, `sprint breakdown`
  reported grooming state with no points anywhere, and only `sprint plan` summed them - a batch
  planner, not a backlog query. So it kept being answered by a script written on the spot, and
  the first hand-written one silently counted a `Won't Implement` story.
- **Terminal units are excluded from the ONE shared authority** (`sdlc_md.is_terminal_status`),
  so the census cannot disagree with what the rest of the tooling calls finished. The buckets
  are the answer rather than the total: a single number cannot say whether the points are Ready
  to plan or sitting at Review awaiting a sign-off.
- **`sprint plan` prints the toolchain**, beside the carried lessons and for the same reason:
  both are things an agent is meant to have read, and both get skipped unless the command that
  runs anyway prints them. An absent runbook is REPORTED, not omitted - a plan that drops it
  silently reads exactly like one that never had it.
- **`tools/runbook.py` fails when the runbook names a command that no longer exists**, or
  drops a step of the cycle. A runbook that has rotted is worse than none: it sends an agent to
  a renamed tool, which is the moment they stop trusting it and go back to hand-rolling.
  Commands are resolved against the shipped surface rather than listed a second time.
- **`reference-sprint-toolchain.md` - the toolchain ordered by STEP, not by script.**
  `reference-scripts.md` is the catalogue and answers "what does X do"; nobody planning a
  sprint has that question. The one they have is "what is next, and which command performs
  it", and answering it from memory is where hand-rolling comes from.
- **Every entry names the hand-rolled shape it replaces**, so it is findable from the WRONG
  instinct as well as the right one - `npm test | tail` beside `run-suite.sh`, a hand-written
  review prompt beside `critic.py brief`, a census script beside `status.py points`. An entry
  useful only to somebody who already knows the tool exists is useless to whoever needs it.
- A closing rule: a step with no command is a FINDING to file, never an invitation to
  hand-roll it.
- **`run-suite.sh --check` refuses a greenness claim the record does not support** - an absent
  verdict (never read as pass), one recorded at an earlier commit than HEAD, or one recording
  a non-zero exit. Each refusal says which of the three it is.
- **The commit-msg hook checks a message that CLAIMS the suites are green against that
  verdict.** Scoped to messages making the claim rather than to every commit: a gate demanding
  a six-minute suite before every commit is one people bypass, and a bypassed gate protects
  nothing. The lane REFUSES where it stands rather than setting a flag, because the section
  below it initialises `fail=0` and would wipe it - and with no pre-commit handover the hook
  exits before that section is reached at all.
- **`tools/run-suite.sh scripts|tools|all` runs a suite and writes its verdict to
  `sdlc-studio/.local/suite-verdict.json`** - suite, exit code, counts, duration and the HEAD
  it was taken at - while printing a single line. `npm test 2>&1 | tail -15` reports TAIL's
  exit status, not the suite's, and that cost two false claims in one session: a commit
  reported as landed when the hook had refused it, and a suite reported green with a real
  failure in it. The pipe exists because six minutes of output does not fit in one read, so
  the fix removes the incentive rather than asking anyone to resist it.
- The verdict is written on a RED run too, and overwrites: skipping the write on failure
  would leave the previous GREEN verdict in place, which is worse than none because it is
  stale and looks current. An unknown suite name is refused rather than defaulted, and writes
  nothing - an absent verdict is honest, a wrong one is not.
- **`best-practices/testing.md` states the entry-point rule beside name-the-mutant-first:**
  name the door the test goes in through, before the first assertion. If the criterion
  describes a command, the test must enter that command - a library import standing in for one
  is not evidence for a claim about it, however green.
- **`tools/best_practice_rules.py` makes it a runnable check**, exiting non-zero when the
  practice does not state the rule, so it is enforceable by a gate rather than only where
  a test runner happens to look.
- **The guard's own paperwork cannot satisfy it.** The check is scoped to
  the passage's own section, because a whole-file search goes green on a Revision History row
  describing the change being made (BG0457).
- **The lane-check runs in the pre-commit gate, ADVISORY**, scoped to the unit ids the commit
  touches so it costs nothing on a commit that touches none. It ships reporting-only on the
  same terms as claim-drift: a new blocking check on a gate already over its ceiling earns its
  place on a measured number rather than on assertion.
- **Its yield accumulates under `sdlc-studio/.local/`**, following the precedent that fixed
  BG0481 - a hook-written record on a tracked path dirties the working tree on every commit
  with a file the author never touched and the hook never stages.
- **`verify_ac.py lane-check` reports a unit that changes a command where NONE of its
  verifiers enters the shipped entry point.** US0577 shipped `brief_fingerprint` with a
  passing acceptance test and a feature that did not work: the test computed it in-process
  while the command that issues a brief never called it. A library test cannot see a missing
  lane, because the wiring is exactly the part it does not exercise.
- **Detection is by execution over the verifier's own source** - does it call the entry point
  or run the script - never by naming convention, which a rename satisfies. Where the selector
  names a node, that node's source is read rather than the whole file.

### Measured, not asserted

Two earlier scopings were rejected on their numbers before this one shipped. Whole-file
matching reported **0 findings over 615 units** - a detector that never fires, because one
`main()` call anywhere in a several-thousand-line module marked every criterion in it clean.
Per-criterion scoping reported **563 of 615**, because most individual tests legitimately
exercise a library function. Scoped per UNIT it reports **167 of 615**, and a sampled finding
was confirmed genuine: US0131's verifier calls `refine.refine(...)` directly, so the criterion
would pass even if the command never called it.

That figure was **186** as first shipped; `BG0487` removed 19 false positives where the test
entered the CLI through a shared helper. The number is restated rather than left standing,
because it is the number the decision to let this lane BLOCK will rest on.

- **The close REPORTS to the operator** - shipped, carried, cost and what the reviews found -
  rather than leaving a file to be discovered. Being informed is the operator's half of
  human-in-the-lead: if they are not a step in the machine, the machine has to reach them.
- **An absent figure is named absent, never dropped.** A missing line reads as nothing to
  report, and "not attributable" and "nothing happened" are different facts - only one of them
  means somebody should go and look. A close with no captured cost still prints a COST section
  saying so.

### Fixed

- **The close report now actually reaches the operator.** Its emitter read the review rounds
  through `critic` without importing it - every use elsewhere in that module is a deferred
  local one - so a non-empty batch raised `NameError`, the advisory `except` swallowed it, and
  the report printed only for an empty batch, which no real close has. The one input the
  feature exists to serve was exactly the one it failed on. Both criteria called the renderer
  directly, so neither could see it; the caller is now driven by a test of its own.
- **A forecast is not a spend.** The cost line read `token_forecast.actual` off run state,
  where the plan writes a plain integer, so it raised `AttributeError` for every run that
  carried a forecast. Both shapes are read now, and an absent actual stays absent rather than
  being reported as the spend.
- **The absent-cost criterion now reads the COST section, not the whole report.** Its
  assertion scanned the document for "not attributable", "not captured" or "none", and the
  empty SHIPPED, CARRIED and FINDINGS listings all say "none" - so blanking the cost line left
  the criterion green while the section rendered empty, which is the exact omission it
  forbids. A verifier a neighbouring section can satisfy is not checking its own subject.
- **The report is emitted from the close's own success path.** It hung off the
  outcome-promotion branch, which a plain close reaches only through the handoff step's
  "already generated" skip - a first close never takes it - and which then returns early
  anyway, because that same step has by then stamped the run goal-reached. So a completed
  close still told the operator nothing, and the first repair had fixed a `NameError` inside
  a function the close does not call. Its criterion is now driven through
  `main(["close", ...])`: a fixture the production caller is never presented with is not a
  lane test, however many mutants it kills.
- **A unit the panel rejects twice, or one whose seats disagree, escalates to the operator.**
  Two rejections, not one: a first REJECT is the loop working, and escalating on it would fire
  on every ordinary finding until the operator stopped reading the channel.
- **A split panel is never resolved by majority.** The disagreement IS the finding - resolving
  it discards exactly the information the panel was convened to produce, and does so where
  nobody sees it. Both sides are named in the escalation.
- **Escalation NOTIFIES; it never waits.** Human-in-the-lead means the decision reaches the
  operator, not that the machine blocks on input that will not arrive. Unattended, an
  escalation that waits is indistinguishable from a hang.
- **A panel-signed unit is distinguishable from an operator-signed one, forever.** The panel
  marker and the seats it rested on are written into the sign-off CHAIN, not a note - a panel
  sign-off that reads as an ordinary one destroys the only thing recording it buys, exactly as
  the delegated-agent marker already does. `is_panel_signoff` reads it back.
- **The close report splits the two rather than totalling them.** A combined count reads as
  complete whether a human or a panel accepted every unit, and those are different facts about
  who took responsibility - which is precisely what a reader comes to that row for.
- **`review.signoff` decides who may satisfy the reviewer-of-record half, and defaults to
  `operator`.** A project that upgrades must not silently lose its human reviewer: the
  independence bar is this product's central claim, and one that moves without somebody
  deciding to move it is worth nothing. A panel sign-off attempted under the default policy is
  refused, and the refusal names the setting that would allow it. An unknown value is refused
  rather than coerced.
- **A panel may not ratify a review that carries no brief provenance.** Without the interlock
  the panel LAUNDERS the missing provenance instead of catching it: the sign-off half would
  rest on a hand-written prompt carrying neither the seat charter, the bounded diff scope, nor
  the acceptance criteria as law. The refusal names the unit, prints the `critic.py brief`
  command that fixes it, and states that this is a TOOLING failure rather than a judgement
  call - which is what tells an unattended loop it may not simply retry.
- **The interlock binds the panel, never the operator.** A human principal reads the evidence
  themselves and can see it is unbriefed; blocking them would withhold exactly the units most
  worth their attention, which is the opposite of human-in-the-lead.
- **`persona_resolve.signoff_panel` assigns the adversarial seats and the SIGNING seat
  disjointly**, and refuses a signer drawn from the reviewing set: a seat cannot ratify
  evidence it filed. That failure would otherwise be invisible in the record, because both
  halves of the two-role gate would be present and correctly filled in. On this repo's seats
  the split resolves to Sam Eriksson and Dani Okafor reviewing, Lena Marsh signing.
- **The assignment is RECORDED on the run and read back, never re-resolved.** Recomputing at
  sign-off time would let a caller re-roll the panel until it landed on a seat that suited the
  answer, and nothing in the record would show it. An absent assignment raises rather than
  inviting one to be invented.
- **The claim-drift premise is replayed against the real commit, and the replay disproved it three times (US0597).** An engineering seat refused the sprint plan until this story existed, on the grounds that both epics' measurement criteria were owned by no story - so the mechanism would ship on a claim nobody had checked. It was right, and the corrections are the substance of the unit. **BG0471's contradiction was never in one diff**: the stale changelog line was written in `10b6fd54` and the code moved 2 to 3 in `67fc683f`, which never reopened the fragment, so a single-diff lane was structurally blind to it - the lane now also reads the unit's own `changelog.d/` paperwork, a small purpose-built directory rather than a repo-wide scan. **File-level comparison dilutes to nothing**: `gate_timing.py`'s own repair mentions 2 in a dozen places, so 2 appeared on both sides of the diff and never read as replaced, and the first replay returned zero findings - detection moved to the hunk, the smallest unit in which "this line used to say X" is a fact rather than an aggregate. **Prose that narrates a change honestly is not drift**: "the exit code was 2 and is now 3" names both values and is current, and the first firing replay's loudest hits were all that shape - a finding now requires the old value without the new one. None of the three was visible from a synthetic fixture.
- **The claim-drift lane runs in the commit gate, advisory, with its yield recorded (US0585).** It reports where a diff's code and the diff's own prose disagree, and it cannot fail a commit: a new blocking check on a gate already ~40% over its declared ceiling earns its place on a measured number rather than on assertion (D0105). The decision to make it blocking is deliberately out of the sprint that ships it - the lane arrives here, so a sprint's worth of yield cannot exist yet - but `record_yield` accumulates runs, findings and runs-with-findings into the evidence directory so that later decision has something to read. AGENTS.md's lane roster names it, and a test pins that naming, because a guard nobody has written down is one nobody notices losing. The design changed under test: a first version asked whether the prose named a number the code side lacked, and a real 23KB staged diff sank it immediately, since a large diff contains very nearly every small integer. The criterion says "still states the OLD value", so the signal is now the literal the diff moved AWAY from - which is both what BG0471 was and what discriminates. A number the diff kept is not treated as replaced.
- **A criterion ticked over a surface its own diff never touches is flagged at delivery (US0584).** BG0472 is the specimen: two of BG0460's criteria were recorded met while `git diff` disproved both - one over a story byte-identical to the base ref, one over verifiers that never called the function they name. Both ticks passed the close, and an independent seat found them by reading the diff. `ticked_over_untouched` reads the surface a ticked criterion names, from a `Verify:` line or from the criterion's own text, and reports it when this diff does not contain that file. A criterion naming no surface at all is reported as `unjudgeable` rather than dropped, because an unanswerable check must never read the same as a satisfied one. An UNTICKED criterion claims nothing and is not judged, so a story declaring work it has not done yet is left alone.
- **`check_spec_claims.py --claim-drift` flags a diff whose code and whose own prose disagree (US0583).** Every blocking finding of RUN-01KYX375's corrected review loop was this shape: a changelog fragment or docstring stating a value the code in the same diff had moved past. BG0471 is the specimen - the collapse signal moved from exit 2 to exit 3 and two prose sites kept saying 2, one of them the docstring of the very test asserting 3. Each was decidable from the diff alone in seconds and instead cost an adversarial review round. The scan reads prose from two places: lines the diff ADDS, and the standing `changelog.d/` corpus read whole on every run. The second is deliberate and is the expensive half - BG0471's shape is a fragment written weeks earlier that a later commit quietly made false, which a diff-only scan cannot see. What keeps the lane from becoming noise is not narrow input but a discriminating match: a finding needs a real replacement and a shared subject between the prose and the changed code, not merely a shared digit. The findings are ADVISORY and print on a channel that does not touch the exit code (D0105) - the existing spec-claim errors keep the blocking contract they have today, because a new blocking lane on a gate already 40% over its ceiling has to earn its place on measured yield rather than on assertion.
- **The shipped doctrine states the review SCOPE rule** (`reference-doctrine.md` rule 19), so
  a consuming project inherits the bound and not only the ceremony. A review judges that
  unit's declared `Affects` against the run's base ref; every finding is classified
  regression, new or pre-existing by execution rather than impression; and only the first two
  may hold the gate. Rule 18 said where the review runs and nothing said what it may look at,
  which is how a review of a five-point unit becomes an audit of the repository.
- **A runnable guard pins it, and its own paperwork cannot satisfy it.**
  `tools/doctrine_review_scope.py` checks the claim and exits non-zero when the doctrine's
  rules do not make it, so the rule is enforced by something that can run in a gate rather
  than living only where a test runner happens to look. The check is scoped to the numbered
  rules section, because a whole-file substring search goes green on a Revision History row
  that merely describes the change being made - the defect BG0457 records. The test builds
  that adversarial case directly rather than asserting the scoping works.
- **Every finding on a verdict declares its ORIGIN, and an unclassified one is refused.**
  Each item in `--issues` carries `[regression]`, `[new]` or `[pre-existing]`, decided by
  execution rather than impression, and `critic.py record` refuses a verdict carrying an
  untagged finding - naming which one. An unsorted finding is the one a close cannot price
  against the batch that caused it. A clean pass recording `none blocking` stays legal, so
  the rule cannot be satisfied by a gate that refuses every clean review.
- **The seat brief's return contract asks for the tags,** with the three origins spelled out
  and the instruction to decide by `git log -S` or a re-probe at the base ref.

### Changed

- **In-repo docs point at guided onboarding.** `help/hint.md` now records that a guided onboarding walk pre-empts the next-step ladder (matching what `status`/`hint` implement); the greenfield and brownfield runbooks open with `init guided` as the one-command path, keeping their manual step lists as under-the-hood detail; and the README documentation index points at the new sdlc-studio.com pages (the specification layer including the PVD, personas and the Three Amigos, and the greenfield/brownfield walkthroughs).
- **A low-band unit gets a bounded brief: the claim-inventory pass runs at full tier only (US0642).** It reads every Resolution, docstring, comment and CHANGELOG line in scope and rules on each - a finding generator by construction, and the largest block in the prompt. On a low-band unit it costs more than the unit does.
- **The depth line and the omitted sections come from one decision (US0642)**, so a brief cannot announce a lighter pass while carrying the full inventory. What a light brief KEEPS is stated rather than left to whatever survived: the seat charter, the bounded diff scope, the canonical acceptance criteria and the return contract - the four things that make it a briefed review rather than a hand-written prompt.
- **Bounding the light tier does not weaken the full one (US0642).** The refusal that a full brief must enumerate all four prose surfaces still fires, pinned with a positive control so the four refusals cannot pass because the guard refuses everything.
- **The close-owed ledger now tells a close-time repair from an unaccounted unit (US0617).** A close writes a retro accounting for its batch and then stamps the baseline, so anything reaching terminal after that stamp is uncovered - and a repair made *during* the close is exactly such a unit. The ledger therefore re-opened the moment a careful close did its job, twice in one close of RUN-01KYZKY5, and the operator's reading was that the sprint was never being closed. It was, repeatedly, and each close was undone by the next repair. The two states are now named apart, because "fixed after the account was written" and "nobody accounted for this" are different facts. The classification is DERIVED from what is already on disk - the most recent retro's `Date` and the unit's terminal date, which `transition.py` records in a telemetry file named for the day it happened - so nobody has to declare which kind a unit is; a flag somebody must remember to pass records the honest case and misses the careless one, which is the whole population this ledger exists for. Both conditions are load-bearing: without the date test every uncovered unit would be excused, and without the run-finished test the *next* sprint's ordinary delivery would be excused too, since it also postdates the last retro. Nothing is forgiven - both states stay in the owed set - but only an unaccounted unit holds the exit code, because gating on a close-time repair would refuse the ceremony precisely when the close had been careful, which is the unconvergeable close from the other side.
- **A stale repo-wide unified review no longer hard-blocks a sprint close whose own units are
  all independently covered.** It is reported as CADENCE DEBT instead, naming the artefacts and
  saying the repo-wide review is still owed. The periodic ceremony runs on its own schedule
  over the whole tree; a sprint that reviewed every one of its units is not made less correct
  by that ceremony being overdue, and it did nothing to cause the staleness.
- **The coverage question fails CLOSED.** No open run, an unreadable state, or a single
  uncovered unit all keep the lane blocking - so this can only ever go advisory when the
  evidence positively says the batch was reviewed, and the exemption is not reachable by
  deleting a file.

Measured on a real close: nine units, each with independent adversarial evidence, an APPROVE
verdict after repair, a confirmation pass and a sign-off - and the close still stopped, on 59
artefacts of staleness that entirely predated the run.

- **The review-repair loop STOPS when it stops converging.** The growing-set detector already
  existed and only reported: a loop that announces it is diverging and then runs another round
  has reported nothing, and unattended it burns a night going backwards. `loop_termination`
  turns the same signal into a decision, and `_record_close_attempt` acts on it.
- **Two rules, both at their boundary.** A declared round cap (`review.max_rounds`, default 4)
  ends the loop; so does an outstanding set that grew two rounds running. One growing round
  alone does not - a repair exposing its neighbour is ordinary (`lessons/LL0052`), and stopping
  on it would end loops that were about to converge.
- **Only a regression or a newly introduced defect holds a unit's gate.** A review whose
  findings are all `[pre-existing]` now COVERS the unit: the findings are reported with their
  origin, and the repository's existing debt does not block this increment. A `[regression]`
  or `[new]` finding still blocks, unchanged.
- **The blocking and non-blocking sets are rendered apart,** with the non-blocking set stating
  why those findings do not block, so a reader can tell what held the gate from what was
  merely noticed. One undifferentiated list is how a pre-existing observation gets repaired at
  close time as though it were this batch's debt.

An UNTAGGED finding is not treated as harmless: it counts as neither blocking nor
pre-existing, and `record` refuses it upstream. A REJECT carrying no itemised findings at all
still does not cover, because the safe reading is that the reviewer rejected for a reason they
did not write down.

- The `origin` axis is deliberately SEPARATE from the existing `class` axis
  (`fresh` / `repair-regression`). They answer different questions - `repair-regression` means
  the repair broke it, `origin: regression` means this unit's diff broke it - and the word
  appearing on both is why they are not merged. An independent engineering seat found the
  collision at goal review; without the separate name a second classifier would have been
  built on top of one CR0510 reports as effectively dead.
- **`critic.py record` refuses a verdict carrying no brief provenance.** The refusal names
  `critic.py brief --unit <id> --seat engineering|product|qa` as the way to obtain one, and
  shows both `--brief <fingerprint>` and `--brief-file <saved brief text>`. Briefing a
  reviewer with the shipped tool was doctrine, and doctrine is what got skipped: a review
  round was run from four hand-written prompts while the seat brief existed, carrying neither
  the charter, nor the bounded diff scope, nor the acceptance criteria as law. A rule that
  matters belongs in the command people actually run (`lessons/LL0027`).
- **Standing the rule down is a recorded decision, never an omission.** Setting
  `review.require_brief_provenance: false` accepts an unbriefed verdict AND states on the
  output that the requirement was switched off rather than met, so the two are different
  events in the record.
- A recorded review verdict now carries a fingerprint of the brief the seat was given.
  `critic.py brief` emits a fingerprint alongside the brief text, and `record_verdict`
  stores it in a new `Brief` column, so a verdict can be traced to the prompt that produced
  it. Two seats briefed on the same unit fingerprint differently, so the field identifies
  which brief was used rather than merely asserting one existed.

### Changed

- The verdict table gains a `Brief` column. Rows written before it exist are read unchanged
  and report an absent fingerprint - the same value a hand-written prompt records, which is
  correct, because that is exactly what those rows cannot distinguish about themselves.
  A verdict recorded without going through `brief` is therefore visibly unbriefed.
- **Doctrine rule 21: a fix's author is not sufficient evidence for that fix (US0567).** Every other change is held by a test written before anyone knew which way the implementation would go; a repair's test is written afterwards, by the person who just decided what the answer is. So a repair carries a mutant applied to its own changed lines whose death was observed. The rule names `transition.py` as what enforces it rather than leaving it as advice, the Definition of Done template carries the clause under a registered `[check: repair.mutation-evidence]`, and the carried lesson cites the gate instead of restating its terms so the two cannot drift.
- **The close reports what it itself cost (US0559).** `close_cost` reads the execution ledger and the close prints its gate seconds, the runs behind them, the verdicts reused and the seconds those saved, and the wall-clock elapsed across the ceremony - on both the sign-off brief and the `--apply-signoff` path, so the next reduction is judged against a number rather than a recollection. Every figure is a measurement or it is absent: a run whose seconds were never recorded is counted as UNMEASURED and contributes nothing to the total, a reuse whose source run is not on the ledger is named rather than credited with zero saving, and a close with a single event reports no span rather than `0m00s`. Reading any of those as zero would let the close that measured least report the cheapest.
- **`sprint close --dry-run` reports every refusal all seven steps would raise, in one pass, writing nothing (US0555).** The close stops at its first unmet prerequisite, so a close took as many attempts as it had gaps and each restart re-ran the steps before it. `close_preflight` answers the prerequisites read-only and always did - but three of the chain's steps exist to DO something, and one of those, the retro's CONTENT, is the class that actually refused. The dry run performs the action steps against a scratch copy of the workspace: it scaffolds the retro there and judges what `close` would mint, so a content gap is reported before a retro exists. The real tree is never opened for writing and the copy is removed. A step whose probe cannot be evaluated is reported as UNEVALUATED, never as passing, and a pass carrying one is not called clean - a preview that reported an unanswered step as green would be the one way this could actively mislead.
- **A census attributes suite cost per module, and nominates tests no mutation can kill (US0506, US0507).** `tools/test_census.py` reports test count and time against the module each test covers, so the expensive areas are visible rather than guessed, and names any test it cannot attribute instead of dropping it. The removal-candidate half is consumer-only until the mutation runner records which test killed each mutant (BG0357), and refuses loudly rather than guessing when that attribution is absent.
- **The plan-time test strategy now states the EXECUTION policy, and the close reports what it actually cost (US0497-US0499).** The strategy answered "what proof does each unit owe" and said nothing about what runs, how often, or at what price - so the largest single cost in a sprint was set by a habit living in a commit hook that nobody proposed and nobody signed off. `sprint plan` now states the per-commit mode, the close and release runs and an estimated cost for each (priced from the declared `gate_budget` baseline, and named NOT MEASURED rather than printed as zero when no baseline exists), and reports a declared `test_execution.*` policy that the commit hooks do not implement - the hook's behaviour is read from the hook, never restated beside it, and an unreadable hook is reported as UNRECONCILED rather than as agreement. The strategy is persisted into `sprint-plan.json` and read back at the close, so what is judged is what was agreed; a run planned before this exists still gets an answer, named as a re-derivation. The sprint report carries a `Test execution:` line counting full, selected and reused runs against the declared policy, attributed to the run's own window, and says NOT CAPTURED - never a total of zero - when nothing was recorded.

<!-- section: Fixed -->
- **The sprint close no longer invalidates itself, and a retry over an unchanged surface reuses its verdict (US0500, US0501).** The close writes the review anchor and the handoff, which made them newer than the anchor's last review, which failed the review-currency lane on the next attempt - so one close took four attempts and about sixteen minutes of test execution to record a decision already made, and filing an honest finding during a close cost another full gate. Artefacts the close itself wrote are now recorded as its own output and attributed as such: a review-currency refusal naming only those is reported as the close's own paperwork and the ceremony continues, while a stale artefact the close did not write, any other failing lane, and a refusal this cannot parse all still refuse - and the message names which blockers are in the WORK. A finding filed during a close is recorded as carried into the next run. The close's gate verdict is recorded against a content hash of the test-relevant surface with the close's own output subtracted, so a retry over an unchanged surface reuses it and says so; a changed surface, a red verdict and an unhashable surface each pay in full.
- **The gate reports its own cost against a budget, every run (US0496).** Each lane is timed, and the run prints its elapsed cost, the declared budget (`GATE_BUDGET_S`, 45s, overridable with `gate.budget_seconds`), the lane that dominated the total and the direction of travel against the previous run. An over-budget run states the overage plainly with the dominant lane named, because a total with no lane named sends a reader to bisect the gate by hand. The first measured run says what it was for: 33.6s over this workspace, 26.5s of it in the `constitution` lane.
- **A full-suite run is confined to a boundary - push, release and sprint close (US0495).** Everywhere else the gate runs the selection. Declare the moment with `gate.py --suite-decision --boundary push` or the `SDLC_GATE_BOUNDARY` environment variable, for a step that runs the gate through a wrapper it cannot pass flags to; an unrecognised boundary is refused rather than downgraded to the cheap path, because a caller who asked for everything and silently got a selection would be wrong about their coverage. A boundary also declines a green verdict earned by a partial run, so selection trades when the coverage is paid and never whether. The policy is stated in `help/gate.md`, and `tools/tests/test_help_coverage.py` pins the page against `gate.BOUNDARIES` so a boundary cannot be added without documenting it.
- **The gate selects the tests a change can reach, instead of running all of them (US0494).** `gate.select_tests` follows the repo map's import graph transitively from the changed files, and attributes a changed non-source file (a reference doc, a hook, a shipped artefact) to the suite modules whose source is measured to read it. `repo_map.py` gained `basename_index`, `import_candidates` and `dependents_index`, so the reverse graph and the in-degree hub score resolve an import through one rule rather than two. A selected run reports how many test modules it excluded and why. Anything neither route resolves widens the run: an unanswerable changed-file probe, a file in the surface no module claims, and a change that reaches no test at all all run everything, because a selection of zero tests reported as a pass is a vacuous green.
- **The unit suites are skipped when the test-relevant surface is unchanged since the last green verdict (US0493).** `gate.py --suite-decision` hashes the measured test-relevant surface by content and compares it with a recorded verdict (`--record-suite-verdict RUN-xxxx`, `.local/gate-suite-verdict.json`), so consecutive paperwork commits and a retried close cost nothing instead of paying the full price for a tree the tests already passed on. Measured over one working day on this repository: the suites ran about 52 times for about 218 minutes against about 35 minutes of delivery, a large share of them over a byte-identical source tree. Every unknown runs the suites - an absent, unreadable or malformed record, a red one, a record carrying no hash, or a surface that cannot be hashed - so a broken cache degrades to the slow answer and never to a false green. The pre-commit hook reads the `suite-decision: run|skip` sentinel and names the reuse rather than skipping in silence.
- The charter queue lifecycle is documented beside the run lifecycle in `help/sprint.md`, with
  every queue verb shown as a runnable invocation rather than named in prose, and the reasoning
  for materialising late recorded where a reader expecting frozen queued plans will look for it.
  The coverage check derives the verbs it expects from the parser's own help table, so a verb
  added later is covered without editing the check.
- `sprint call` finishes a run at a point rather than abandoning it: the unstarted remainder is
  descoped and the close chain then runs against the Sprint Goal, so a called sprint is closed
  rather than left open. The remainder returns to the **backlog**, never forward to the next
  charter, so no two sprints are coupled and the next run never inherits a batch it did not
  approve. It forwards the close's own flags - `--retro`, `--goal-verdict`, `--note`,
  `--apply-signoff`, `--principal` - so the close's messages never name a flag this verb
  rejects. Each descoped unit keeps its own status, because the drop judges the batch and not
  the work. A descope needs a reason, matching what `batch drop` already requires.
- A sprint charter carries its own goal review, under `## Seat review` on the charter itself
  rather than in `.local/`. Local state does not travel: a charter pulled into another working
  copy now arrives carrying the review that justified it. `sprint next --runner` records who ran
  it beside who reviewed it, and states plainly when they are the same identity. Separation is
  recorded, never enforced. A charter whose goal was never reviewed is reported before it runs,
  in wording that distinguishes an unexamined plan from a review that found nothing.
- The sprint charter queue is inspectable and editable: `sprint queue show` lists it head first
  and reports what the head resolves to against the backlog right now, and `queue reorder`,
  `queue cancel` and `queue clear` correct a plan without hand-editing state. Cancelling
  withdraws rather than deletes and keeps its reason, so the queue's shape stays explicable. A
  charter with no rank sits in authoring order and sorts after every ranked one - absence is not
  rank zero, so ranking one charter does not reshuffle the rest. Only the head is resolved,
  because resolving the tail would be arithmetic over a backlog the earlier runs will change.
- `sprint next` materialises the head sprint charter against the backlog **as it stands at that
  moment**, so a queue holds intent rather than a frozen batch: units created since the charter
  was written are included, and units delivered since are not. It refuses, leaving the queue
  untouched, when a run is already open, when the head charter carries no resolvable scope
  query, or when the scope selects nothing. A charter's `Scope query` speaks `sprint plan`'s own
  selector vocabulary rather than a second grammar.
- A sprint charter is a first-class artefact (`SC` prefix, `sdlc-studio/charters/`): it carries
  the goal a run drives to, the rule that selects its batch, and an optional appetite, so a run
  can be opened from it without asking again. Its prefix, create status and terminal set derive
  from the shared registry rather than being restated beside the charter code, and the versioned
  schema contract documents all three. A charter missing its goal or its scope rule is refused
  before an id is allocated, because one that cannot answer those stops the queue at the moment
  it reaches the head.
- **A gate lane for a flag whose parsed destination no line acts on (US0485).** `command_audit.py --dead-flags` follows the parsed value rather than counting the sites that mention a destination, which is the distinction the earlier specification for this could not make: `verify_batch` was mentioned three times in `gate.py` - defined, read through a defaulted lookup, and forwarded as a keyword argument into a `run_gate` parameter no line of the body read - so every mention-counting rule called it live. Validated against that module as it stood before the flag was deleted (reported dead, nothing unjudged), and pinned as a fixture of the three lines verbatim so the defence holds after the deletion. Positionals are not judged: argparse enforces their presence whether or not a line reads the value, and reporting one also printed a switch that does not exist. Three shapes are reported NOT JUDGED with the reason rather than dead - a namespace handed to a callee the analysis cannot resolve, a `getattr` whose attribute name is computed, and a module that declares flags on a parser it never parses - because a fabricated verdict is worse than an absent one, and each of the three named live flags as dead while it was being built.
- **`reconcile` reports a supersession recorded on one side of the pair only (US0484).** A superseded design that never records it keeps reading as live from the direction a reader arrives from, so the pair is now checked from both ends as `supersession-asymmetry`. The declaration is matched on its **verb**, not against a list of field names: the corpus carries eleven distinct spellings (measured - the specification said six), and five of the missing ones carry the verb in free prose inside the bold run, which a field-name allowlist reads as an absence and reports as drift that does not exist. The template's combined `Supersedes / Superseded by:` field takes its direction from its value, since recording both directions manufactured a reversed phantom pair for every one of the fifteen it ships in. Detect-only, like `link-asymmetry`: which side is authoritative is a judgement about which design won. Legitimate asymmetry - a partial supersession replacing named decisions of an artefact that stays live in the rest - is recorded in `sdlc-studio/.supersession-waivers.json`, a ratchet whose entries need a stated reason and whose set may only shrink; a corrupt or `pairs`-less file reads as corrupt rather than as "nothing waived", so a malformed waiver cannot bury a real finding under every tolerated one.
- **`sprint plan` validates the units in its batch, not only their index rows (US0481).** A unit whose own `Verify:` lines target a file its `Affects` omits carries that wrong declaration into the collision analysis and the engagement floor, both of which read `Affects`. The plan now names the unit and the missing path, from one shared resolver that `batch add` calls too.
- **Joining a batch late is not a way past the check (US0481).** `sprint batch add` runs the same resolver over the unit it adds, so a unit that arrives after the plan was printed is held to what every other unit in that batch passed. Pinned by driving the shipped `batch add` verb rather than the helper, because the wiring is the part a library test does not exercise.
- **Scoped to the batch, never the corpus (US0481).** A defect in work nobody is planning cannot block a plan, and a check that refused on the standing tail would be switched off within a day - the tail is held by `validate.py warning-ratchet` instead. The test puts an offending unit on disk and outside the batch, and asserts it is not judged.
- **`sprint.affects_check` decides what a finding does, defaulting to `warn` (US0481).** Reporting rather than refusing is the shipped default because a declaration naming a file the unit will CREATE is legitimate; `block` is for a project that has paid its tail down and wants it kept at zero. An unknown value falls back to `warn` rather than to the stricter mode. The default is stated in `help/sprint.md`, and the test asserts the help page and the code agree rather than checking each against the author's memory of the other.
- **The Affects/Verify warning family is ratcheted by INSTANCE, and the tolerated set may only shrink (US0480).** It stood at 371 instances and was purely advisory, so a new one was indistinguishable from the standing tail and nothing stopped the tail growing. `validate.py warning-ratchet` compares the live set of instance identities - `(artefact, rule, the specific path or command the warning names)` - against `sdlc-studio/.validate-warning-baseline.json`, and refuses naming the instance rather than reporting that a number moved.
- **A count could not have done this, and the tests say why (US0480).** A swap that repairs one instance and introduces another leaves the total flat and is still refused, because the comparison is over identities and consults no recomputed total anywhere. Two `pseudo-verify` instances paid down elsewhere cannot mask one new `affects-undeclared`, because the rule is part of each entry's identity rather than a per-kind tally a surplus could offset. A repaired entry is reported STALE and removable - it can never be spent again to admit a different instance.
- **A baseline the ratchet cannot trust never reports clean (US0480).** Four distinct non-zero states: `not-baselined` (an absent reference is not an empty one), `corrupt` (loud, never a silent pass), `stale`, and `reasonless` - a tolerated instance nobody justified is exactly the silent tolerance this replaces. Identity is read from the finding's own `targets`, which the checker now attaches structurally, rather than parsed back out of its message, so the prose a human reads cannot drift from what the gate compares.
- **The verdict reaches a lane that refuses a real commit (US0480).** A `warning-ratchet` lane runs in `.githooks/pre-commit` and in the `npm run lint` chain, invoking the checker directly - not through `gate.py._validate`, whose `severity == "error"` filter would swallow a warning-severity refusal. Pinned by executing `git commit` against a fixture repo with the shipped hooks enabled: the commit does not land, HEAD does not move, and the lane and the offending instance are both named. The control commits the same tree once the instance is recorded, so the refusal is attributable to the instance rather than to the fixture.
- **The epic index's derived cells have one importable definition, and a census behind them (US0477, foundation).** `sdlc_md.EPIC_INDEX_COLUMNS` is the single answer to what an epic row is, because two parties consulted their own: the shipped `templates/indexes/epic.md` declared `Owner`/`Target` while all 191 live rows carry `Deps`/`Created`/`Updated`. The live set wins on 191 rows of evidence.

  `epic_story_count` censuses the story files naming an epic, so `0` is a derived fact rather than a placeholder. `epic_declared_deps` has **three** states and the third is the point: named dependencies, a declared-but-empty section (the epic says it has none), and **no section at all** (nobody has said). It returns `None` for the third and `derive_epic_row_cells` then omits the cell entirely, so a caller writes nothing rather than turning an absence into a declaration - which matters because **181 of this repository's 191 epics** state no Dependencies section.

  **Now wired as the `epic-index-derivable` drift kind, and the nine-row question is settled by a rule rather than by a decision.** The measured dry run said the derivation would fill 182 rows from `--` (pure gain) and overwrite nine, eight of them downward - EP0001-EP0009 dropping to `0` or `1`, because those old epics' stories are no longer on disk and their hand-typed counts cannot be substantiated. What `apply` writes is now decided by the DIRECTION of the disagreement, not by whether the cell looks empty: a placeholder is filled, a count the census **exceeds** is filled (the row was merely stale, and the tree holds every story it claims and more - that is EP0008, 6 to 7), and a count the census **falls short of** is reported as `advisory (epic-index-uncorroborated)` and left alone. So the eight downward rewrites never happen, no operator decision is needed to introduce the kind, and no blocking lane goes red on a repository nobody had broken.

  The direction test is also what keeps the rule usable rather than merely safe. A newly minted epic's row carries a censused `0`, which is a real value - so a placeholder-only rule would have locked the derivation out of its own cell, and the first story wired to that epic could never move it. The story census is memoised on a `stat` signature, taking 3.3s off a lane that runs on every commit.
- **Every sprint verb is documented as a runnable INVOCATION**, not as a word that happens to
  appear in a sentence. The in-flight controls - `goal-review record`, `batch swap|drop|add`,
  `stop`, `reopen` - now have a section of their own in both `help/sprint.md` and
  `reference-sprint.md`, so a reader working through the reference does not have to leave it to
  learn how to change a run that is already open. The read-only verbs (`breakdown`,
  `preflight`, `goal-verdict`, `lane`) are shown too.
- **The verifier is derived from the PARSER**, so a verb added tomorrow is covered without
  editing the test, and it extracts only from FENCED blocks - a verb named in prose is not an
  invocation, and scraping prose would assert that the English around a command parses.

### Fixed

- **Two documented invocations the shipped parser does not accept**, found by this unit's own
  verifier: `/sdlc-studio sprint prd.md --goal design` (the PRD is a `--prd` argument to
  `plan`, not a verb) and `/sdlc-studio sprint checklist` (there is no such verb; the checklist
  is `sprint_report.py checklist`).
- The `reference-sprint.md` line ceiling was raised DELIBERATELY, in the same commit as the
  prose it admits, and set to the file's exact length - a ceiling with headroom is one that
  stops noticing growth.
- `sprint appetite resize --units N --minutes M --reason "<why>"` moves an open run's accepted
  appetite. A run that turns out bigger than planned has two honest endings - stop at the
  planned ceiling, or raise it deliberately - and one dishonest one, where the appetite is
  quietly rewritten so the close reports a run that fitted.

  The STANDING pair the batch was sized against is left untouched, so raising the accepted
  number makes the overage true rather than hiding it: the resize prints the over-commitment
  line immediately, and `sprint close` reports the run against the standing ceiling. A reason is
  compulsory, and the change is recorded in `appetite_changes` with the pair it moved from - the
  number alone says a ceiling moved and not why, and the why is the whole content of the
  decision.

  The run breaker reads the resized number, so a raise actually extends the run rather than
  moving a value in a file. A resize with neither number, with no reason, or on a run that is
  not open, writes nothing.

  `sprint appetite` is declared a mechanics verb rather than a ceremony stage, so the checklist
  drift guard - which refuses a sprint verb holding no checklist row and not declared - passes
  on the honest answer instead of a stage nobody performs. That guard caught this verb at the
  gate, which is what it is for.
- `sprint batch add-epic --epic EP0010 --status Ready` adds an epic's stories at a named
  status to the open run's batch as ONE priced set. It prints the points the batch just grew
  by, which is the number the appetite is judged against; adding the same stories one at a
  time reaches the same batch but leaves the ledger reading as several unrelated decisions.
  Units already in the batch are named and not priced again, so the growth figure stays
  honest. The selection is read from the tree at call time rather than from a snapshot, so a
  story added to the epic between two calls is picked up. An epic with nothing at that status
  fails loud and writes nothing - silently adding nothing reads exactly like adding
  everything, and the operator would only find out at the close.
- **`sprint batch swap --out A,B --in C --reason ...` trades units in ONE recorded call.**
  Drop-then-add reaches the same batch, but the ledger then carries two unrelated changes and a
  reader cannot tell a trade from a cut followed later by an unrelated addition. The swap is
  the intent, so the record says so - alongside the individual changes, not instead of them.
- **The outgoing side is checked before anything is written.** A half-applied swap leaves the
  batch in a state nobody chose, and the operator's next move would be to guess which half
  landed; a refused swap leaves the run state byte-unchanged.
- **An unbalanced swap WARNS with the points delta and still applies.** The operator asked for
  the trade and a swap is rarely balanced to the point; refusing would make the command useless
  for the case it exists for. A balanced one says nothing, because a warning on every swap is
  noise an operator learns to skip.
- **A swap without a reason, and a one-sided swap, are both refused** - the first because a
  swap changes what the run is FOR, the second because a drop and an add already record
  themselves as such. Ids take the house grammar: `--out A --out B` and `--out A,B` are read
  identically, through the shared splitter rather than a second one that would drift.
- **`help/sprint.md` is bound to the shipped sprint surface, not written beside it (US0468).** Five checks derive what the page must carry from `build_parser` and `lib/run_state` rather than from a list in the test: every subcommand must appear in INVOCATION form (`/sdlc-studio sprint <verb>` or `sprint.py <verb>`), the batch-mutation section must name every key the `batch_changes` ledger writes, and the appetite section must name every field `appetite_record` records. A verb added, a flag renamed or a ledger key changed now fails here instead of leaving the page quietly describing a tool that no longer exists.
- **The check is proven to discriminate against the real pre-rewrite page (US0468).** The fixture is the actual page from before the rewrite, taken from history, not a contrived one - it misses twelve verbs in invocation form while eight of them still appear as ordinary words, so a bare-substring check reported full coverage of a page that documented none of them. The story enumerated twelve verbs; the parser now carries eighteen, because `call`, `next`, `queue`, `lane`, `appetite` and `review-batch` landed after it was written, so the set is derived and the enumeration read as the lower bound it is.
- **The run lifecycle is documented where an operator meets it (US0468).** New sections cover what a batch change puts on the record, why a drop is not `Deferred` (a drop removes the unit from the batch the done-gate reads and leaves its status alone; Deferred keeps its place and still blocks the close), what `stop --force` writes, the appetite's accepted-versus-standing pair and why a resize is reported as an overage rather than a run that fitted, and that a rolling run regenerates its plan at each boundary rather than queueing plans up front.
- **`--autonomous` has a row in the argument reference (US0468).** It sat on no parser and in no reference table, resting only on a prose section, while the sprint page's own examples used it. `--appetite-minutes`, `--appetite-units`, `--cycles` and `--stop-on` gained rows in the same pass.
- `status` now names the open run on its first line: id, ladder rung, Sprint Goal, batch size and
  remaining count, with `rung` and `sprint-goal` under distinct labels so neither reads as the
  other. `remaining` is `handoff build`'s own count rather than a second definition, so the
  dashboard and the handoff cannot disagree. Three states are distinguished - a run, no run, and
  a run-state file that does not parse - because reporting the third as the second orphans the
  run it failed to read. In `--format json` the `run` key is present and explicitly null when no
  run is open.
- **The ungroomed-criteria marker ROUTES as well as reports.** It now names the shape
  (`templates/core/story.md`) and the verifier guidance (`reference-verify.md`), so the answer
  arrives with the problem instead of the author guessing at a shape and a reviewer correcting
  it afterwards - which is the grooming cost this project keeps paying unpriced. Both targets
  are asserted to exist, because a marker routing to a missing file is worse than one that
  routes nowhere.
- **`help/refine.md` ships**, and it states plainly that a refined story arrives ungroomed and
  that authoring its criteria is real work NOT priced by the story's points.
- **The help-page lane is derived from the Type Reference**, so a command added there without a
  page is caught. A waiver is checked: one naming a command that now has a page is reported
  STALE, so the list can only shrink. Three pre-existing gaps (`decisions`, `repo`, `migrate`)
  are recorded with their reasons rather than left silent.
- **A missing page, a stale waiver and an unreadable tree all fail loud.** Each is a different
  way for the check to report clean over nothing, and a silent pass is what let a missing page
  ship in the first place.
- **The Progressive Loading Guide carries a grooming row** whose paths are asserted to resolve.
- **No artefact reaches a terminal status still asking an Open Question (US0465).** Sixteen had: fourteen stories at Done, EP0010 at Done and CR0019 at Superseded, and every one read as settled work. Nothing enumerated them and no gate refused them. `sdlc_md.unresolved_questions` is now the ONE implementation, called by both `validate` and the transition gate, so the two cannot disagree about what a resolved question is - two readings of one rule is two rules and the looser one wins.

  A question is resolved by either route the templates offer and by nothing else: a ruling (moved under a `Resolved Questions` heading, or recorded on the item in the forms this corpus uses, including a decision-row id that EXISTS), or a follow-up artefact whose cited id RESOLVES. **A tick with no destination is refused**, because that is precisely how a question stops being visible without being answered. The bar is the terminal status, derived from the type map rather than an enumerated Done - so a CR reaching Superseded is held like a story reaching Done - and the gate sits at the VERB as well as in validate, because a refusal that arrives later from a different tool leaves the tree in the state the rule forbids.

  Three classes of FALSE POSITIVE were found while sweeping and are excluded, each for a stated reason: `- [ ] None - behaviour fully extracted from scripts/x.py` is the template saying there are none; `Ruled by D0052: ...` is a ruling recorded on the item, and demanding the heading would be demanding a layout rather than an answer; and `{{question}}` is an unfilled template that validate's placeholder rule already owns, so reporting it here would double-report it and refuse a transition for the wrong reason. The first version of this guard would have forced ten already-correct artefacts to be "fixed".

  The twenty-one genuine questions are now OWNED, not answered. CR0019's three are ruled moot by its supersession - a real answer, since a superseded design's alternatives cannot now be chosen. The other eighteen cite **BG0421**, which records that the delivery made a choice and nobody recorded whether it was the right one. Writing a ruling for each from what the code now does would have been inventing the decision after the fact, at scale, into the permanent record.
- **`readiness.py detector-owed` names the lenses a recurring class has now paid for twice (US0463, AC1-AC4).** A lens filed under two or more separate REGISTERED audit runs whose signature declares no mechanical detector is detector-owed: a judgement the model has been billed for twice, which a script should take over. One whose detector already ships is reported detector-exists, with the command to run and skip on, so an existing script is never re-commissioned.

  **Survival across runs, never volume within one.** Five findings from a single run is the lens working, and counting findings instead of distinct runs would have turned every productive lens into a false debt.

  **An unregistered run id is not a second run.** Counting a citation the register does not hold would let a one-character typo manufacture recurrence by the back door - the same defect the filing-time validation exists to stop, arriving from the other side. Such citations are reported rather than silently dropped.

  **Three exit states, and cannot-judge DOMINATES.** 0 clean, 1 owed, 3 cannot-judge. A workspace with three owed lenses and forty unattributable findings reports cannot-judge, because otherwise the forty vanish behind a verdict that reads like an answer. It is 3 and not 2 because `cmd_profile` already returns 2 for an unknown profile and argparse uses 2 for a usage error, so a caller could not otherwise tell "I could not judge this workspace" from "you typed the flag wrong". Expect cannot-judge on a corpus that predates attribution: 108 of 980 findings carry it, so the first real run says so plainly rather than reporting clean.

  A verdict resting on ids asserted from prose is weaker than one resting on measured runs, so each row carries the provenance of the runs behind it rather than flattening the two together.

  **`--file` mints one sized CR per owed class, and never a second.** The unit names both runs and both findings as the evidence its detector must catch, and carries a `Detector-for-lens` field that sits deliberately OUTSIDE the lens/profile/run triple - the unit spans two runs, so it has no single `--audit-run`, and under all-or-none it would file with none of the three and become invisible to the next run. Idempotence matches on that field rather than a title substring, so rewording the unit does not cause it to be filed again.

  Nothing is filed for a detector-exists lens, and `--file` REFUSES on a cannot-judge verdict rather than minting units from a workspace the verb has just said it cannot read. The filed id is re-derived from the written path, because the filer reports a display form (`CR-0001`) while a later scan reads the record id from the filename (`CR0001`) - two spellings of one identity is not a basis for an idempotence check.
- **A filed finding records the audit lens, its profile and a resolvable run: `file_finding.py file --lens --profile --audit-run` (US0462).** 108 findings already hide their run id inside `Raised-by` prose, so counting a class across runs meant a regex over free text rather than reading a field. The three land as `Audit-lens` / `Audit-profile` / `Audit-run` metadata beside the existing provenance stamp.

  **The register has a real writer, and it is not under `.local/`.** The reader was very nearly added with nothing behind it: `audit_cost.py` already appended one git-tracked row per finished audit run, so it gains a `run_id` and `audit_cost.py record --run-id` is the register's writer. Mirroring `mutation.series_path` would have put it in `sdlc-studio/.local/`, which `.gitignore` excludes - the register would then be empty on every clone but the one that wrote it while the findings citing it stayed tracked, so every `--audit-run` would be refused and a detector-owed verdict would read cannot-judge for the whole corpus, permanently, everywhere else. The mutation series' shape is mirrored; its path is not.

  **A row records whether it was `recorded` or `backfilled`**, mirroring `mutation.PROVENANCE_REGISTERED`. The five historical `wf_` ids were minted by nothing and lifted from prose written for another purpose, and laundering them into the same authority as a measured run would make a detector-owed verdict rest on unverifiable strings.

  **All three or none, never some - except that the profile is DERIVED.** A lens name must resolve to exactly one pack - now ENFORCED rather than assumed, because with two owners the derivation picked the alphabetically-first while a supplied `--profile` was accepted for either, so the same finding got different records depending on whether the operator typed the flag. An ambiguous lens is refused. Demanding the profile is asking for input the operator can get wrong; supplied, a lens/profile MISMATCH is refused, which is strictly stronger than requiring all three, because that rule accepts a consistent-looking pair naming the wrong pack. A filing carrying none of the three stays legal, since all 980 existing findings carry none - bugs, CRs and RFCs alike, since all three render the same fields.

  **Every check runs before an id is minted**, beside `check_mutation_run` and ahead of the advisory lock, so a refusal costs no id and holds no cross-process lock while it parses packs. An undeclared lens, an unregistered run and a mismatched profile are each refused by name.

  The flags reach both paths a caller can use. `cmd_file` builds its flags dict by hand, so a new argparse flag absent from it is parsed and silently dropped - and `load_fields_file` RAISES on any key outside `FIELDS_FILE_KEYS`, so `--fields-file`, the one path that does not cross a shell, would have refused the document outright. Both are wired and both are held by tests that drive the real command, as is the register's own writer - `cmd_record` could stop passing `run_id` with the whole suite green, which is the same defect one file over.

  **Repairs from an independent review, which returned REJECT on the first cut.** Three defects were
  behavioural rather than test gaps. A **Low-severity finding on a v3 project** consolidates into a
  shared CR that carries no per-finding lens, so the attribution was validated pre-mint and then
  discarded in silence; `triage_noise` already had the loud precedent for `tranche` and a third
  field family had been added to the filer without extending it. A **corrupt ledger shard** made
  every recorded run invisible - identical to never-recorded - and the refusal then told the
  operator to record the run again, appending a duplicate to an already-broken file: the register
  now reports `ok`/`empty`/`corrupt` as three distinct states, mirroring `read_dup_baseline`, while
  the estimator keeps its lenient read because a median degrades gracefully and a register does not.
  An **unrelated half-written pack** refused every attributed filing in the project, naming a file
  the operator had never mentioned, so `resolve_profile` is now guarded per pack as
  `cmd_validate_profiles` already did forty lines away.

  Smaller: `--profile` alone was accepted and silently dropped, and its refusal named `--audit-run`,
  a flag nobody had supplied; a profile no pack declares is now refused by name with the packs
  listed. `--provenance` gained a CLI flag, since `backfilled` had no operator-reachable writer -
  a reader with nothing behind it, one level down. The three keys moved into
  `sdlc_md.SINGLE_LINE_FIELDS` rather than a second copy of the rule inside the filer, because
  `audit_run` is free-form and a markdown link in it can red the repo's own links guard.
- **The duplicate-verifier class stops growing: `verify_ac lint --ratchet` (US0461).** `duplicate_verifiers` reported shared selectors and never refused one, so the class could grow indefinitely - and two ACs sharing a selector cannot both discriminate, because a regression in either fails both and neither says which. The ratchet refuses a group the baseline does not record, and it runs as a `verify-ratchet` lane in both `npm run lint` and the pre-commit hook.

  **The comparison is over the SET of groups, never the count.** A change that splits one baselined group and introduces a new one leaves the total unchanged, and a count-based guard passes it - which is precisely the guard a rising total would already have caught, so it would have added nothing. A recorded group that is no longer duplicated is refused too: a tolerated set that keeps a fixed entry can spend it again to admit a new one, and then the ratchet only ever loosens.

  **`--bugs` scans `sdlc-studio/bugs`, as `stamps --bugs` already did**, and this half earned its place immediately: of the 43 shared selectors in the workspace, **23 were parked in bugs where the scan had never looked.**

  Three DISTINCT untrustworthy states, because the remedy differs and none may read as a clean scan: an absent baseline wants a first stamp, an unreadable one wants a human, and a stale entry wants removing. An exemption is machinery rather than an assumption - an entry needs a reason a human wrote and every AC it names must resolve, and `--stamp` deliberately mints an EMPTY reason and exits non-zero, so a stamp cannot manufacture an exemption nobody decided on.

  The 43 pre-existing groups are recorded as tolerated with the reason stating what they are: real debt at the ratchet's introduction, not judged-legitimate cases. Splitting each selector so its criteria discriminate is owed work, and removing an entry is the only permitted direction.

  **Two fail-opens found by an independent review, both closed.** The AC cap was applied only to an entry's RECORDED list and never compared to the group's LIVE one, so a selector baselined at 2 ACs was accepted spread across 30 - the exact class `duplicate_verifiers` names. And an entry was silenced by a one-character reason plus any resolvable artefact id of any type, so `{"acs": ["EP0169 AC1"], "reason": "-"}` kept the lane green. One stronger rule replaced both: a tolerated entry must name EXACTLY the ACs that currently share its selector, and only a story or a bug carries ACs that can share one. A reason now needs substance rather than a non-blank character.

  **A case-only twin of a selector escaped entirely.** The DSL lowercases the verb before dispatch, so `PyTest x` and `pytest x` run the identical command - grouped case-sensitively they were a group of one under each spelling, and `len(acs) > 1` never fired. Grouping is on the normalised key, and normalisation is applied to the BASELINE side too: it had been applied only to the live side, which `duplicate_verifiers` already normalises, so the one side a human hand-edits was left raw and a key with a double space was reported as both new and stale.

  **The refusal path itself carried no test.** Mutants that made the verdict ignore the entry errors, or replaced the validation loop with `pass`, left all 263 tests green - the entry checks were asserted only through the helper, never through `dup_ratchet` or the command a lane invokes. The cap's value was supplied to its own test by the production constant, so 8 could be set to 1000 and stay green. Both are pinned now, and the positive control asserts its fixture actually produced a group, having previously passed with the detector stubbed to return nothing.
- **The TSD's per-script test contract stops being prose (US0456).** The document said "Every script has a matching `test_<script>.py`" and, in a second place, that every script and shared-library module has a dedicated test module. Neither was true - `carry_forward`, `triage` and `lib/tiers` have none - and the TSD itself admitted two hundred lines away that "no sweep enumerates the scripts and fails a build on a module that arrives without a test". `tools/check_script_tests.py` is that sweep, and it runs as a `script-tests` lane in `npm run lint` and in the pre-commit hook.

  It derives the module set from disk INCLUDING `scripts/lib`, because a `scripts/*.py`-shaped glob silently drops the shared library - the exemption-by-omission that would lose `lib/tiers` without anyone deciding to. The indirect-only exception list is now a fenced block in the TSD that the checker parses, so the document is the declaration and the tool is only its reader; there is no second copy of the set to drift.

  **Both directions fail.** A module the sweep finds untested that the list omits is an undeclared coverage gap. A module the list names that has since GAINED a dedicated test is a stale exemption - and a stale exemption is how a real gap hides beside a fake one. `refine` and `lib/run_state` were on that list and are not any more, because both now have dedicated tests.

  The two absolute claims are refused by a denylist over their own LOCATED passages, so a renamed heading fails loud rather than matching nothing and reporting clean; and an unreadable scripts or tests directory refuses naming which one, rather than printing a zero-exception result it never measured.
- **`transition.py set <ID> <STATUS>` accepts the natural positional form (US0446, CR0423).** The obvious first attempt - `transition.py set US0443 Review` - now works, mapping onto `--id`/`--status`; the flag form is unchanged. Giving the same value both positionally and via a flag is refused with an error that names the correct form, rather than the raw argparse noise that used to greet the natural invocation.
- **Guided onboarding - documented in the init help (US0444, EP0163).** `help/init.md` now leads with `init guided`: the one command that walks a new user from an empty or existing repo through AGENTS.md, PRD, TRD, TSD, personas and decomposition to a first sprint plan, one draft-then-confirm stage at a time, on both greenfield and brownfield projects. The earlier greenfield first-mile RFC (RFC0019) is marked Superseded, its intent now realised and generalised by the guided flow.
- **Guided onboarding - `hint` walks you to a first plan (US0443, EP0163).** While guided onboarding is under way, `hint` points at `init guided` and names the next stage, taking precedence over the ordinary pipeline ladder. The single next step always resumes the flow you can leave and come back to, until you reach a first sprint plan; once onboarding is complete or absent, the normal hint resumes.
- **Guided onboarding - decompose and first-plan stages complete the flow (US0442, EP0163).** The final two stages direct the agent-driven steps that turn the spec into delivery: decompose the PRD into epics and sized stories (`epic`, `story`), then plan the first sprint (`sprint plan`). Confirming them completes onboarding, and `init guided` reports the flow complete - the operator lands exactly where delivery begins.
- **Guided onboarding - the personas stage (US0441, EP0163).** The guided flow seeds the personas doc and directs growing a project-specific engineering team from the PRD and risk signals (`persona generate --team`) for the operator to accept or edit - so the team that both builds and reviews the work exists before the first sprint. Confirming advances the flow to the decompose step.
- **Guided onboarding - the TRD and TSD stages (US0440, EP0163).** The guided flow now seeds the technical-design (`trd.md`) and test-strategy (`tsd.md`) documents from the template (never clobbering an existing one) and directs each to be generated from the PRD - the TSD also from the detected stack on a brownfield project. This is what guarantees the test strategy the sprint plan later reads actually exists, rather than a plan reading a document that was never written.
- **Guided onboarding - the PRD stage forks on the project's path (US0439, EP0163).** The PRD stage seeds the `prd.md` scaffold (never clobbering an existing one) and directs the path-appropriate method from the onboarding classification: a greenfield project is interviewed (`prd create`), a brownfield one is drafted from its code (`prd generate`, validated downstream by `code verify`). The operator never chooses a command - the flow forks for them, and `init guided` surfaces the directive.
- **Guided onboarding - the AGENTS.md stage (US0438, EP0163).** The first stage of `init guided` drafts `AGENTS.md` and its `CLAUDE.md` import from the tool-neutral starter (idempotent - an existing, possibly edited, file is never clobbered), so every agent that touches the repo inherits the discipline from the start. The runner now advances only on `init guided --confirm` and records `--skip` as a deliberate, visible skip - draft-then-confirm, the flow moving on the operator's word.
- **Guided onboarding orchestrator skeleton - `init guided` (US0437, EP0163).** The resumable spine of the new onboarding flow: a checkpoint at `sdlc-studio/.local/onboarding.json` records each stage (agents, prd, trd, tsd, personas, decompose, plan) with a status, and re-running `init guided` resumes from the first still-pending stage rather than restarting. `init` classifies the repo as greenfield (empty) or brownfield (an existing stack marker) so the PRD stage can fork on it, and the stage runner advances only on confirmation, records a skip as a deliberate `skipped` (never silently), and `--reset` returns every stage to pending. The per-stage draft-then-confirm actions plug into this in the stories that follow.
- **A sprint close whose outstanding set is GROWING now names the way out - honestly (US0435, EP0162).** The close already recorded each attempt's outstanding count and named a growing set as "chasing a moving target", but named no exit - so a close that re-broke one lane while fixing another left only the moves the gate exists to stop: a forced false Done, or a grandfather bump. When the count rises across attempts the trend line now names `--file-and-close --retro <id>` for the DEFERRABLE (ceremony) items it can actually file, and says plainly that any remaining hard correctness blocker(s) must be cleared first - because file-and-close refuses a red gate lane, so a blanket offer would dangle a dead-end for the moving-target case (all `gate` blockers) that most often triggers it. A set of only hard blockers is told to clear the lanes, naming that a growing set of correctness lanes is the case the batch-scoped conformance and record-based review-currency checks exist to stop. The offer is made only when growing, never on a first or converging attempt.
- **`sprint batch drop <id> --reason` and `sprint batch add <id>` mutate an open run's approved batch (US0433, EP0162).** A batch chosen on day one used to bind the close forever: there was no verb to pull a unit or add one, and the nearest workaround - transitioning to `Deferred` - does not release the done-gate, because Deferred is a status on the WORK and leaves the unit in the batch the gate reads. `batch drop` removes the unit from the batch (so the done-gate and sign-off lanes stop demanding it) and records the change in the run's `batch_changes` with its reason and timestamp; `batch add` puts a unit in under the same gates. Drop judges THIS BATCH, Deferred judges the WORK - the two are no longer conflated, and the operator no longer hand-edits `run-state.json` for a routine sprint event.
- **A seam between two units has an owner before the work starts (US0538, US0539, US0540).** Thirteen of the seventeen round-one majors in RUN-01KYKVZM were seam defects: four directly contradicting pairs in one batch, every one of which passed its own acceptance criteria, because a delivery lane reads ONE unit and review is the first actor in the loop that reads two. `refine seams` now maps the pairs of a batch that share a declared file and reports those nobody owns; a criterion owns a seam with `- **Preserves:** <what must not regress>` naming the shared surface or the sibling unit. The map reaches every lane brief - the neighbouring property is the one thing a lane can never learn from its own unit - and the close reports seam coverage, naming any seam that shipped unowned. Measured on RUN-01KYKVZM: 52 seams, none owned.
- **The close compares declared proof against delivered proof (BG0358).** RUN-01KYJZGZ named six units owing mutation-plus-unit proof, recorded zero mutation runs, and closed clean with both suites green and the gate passed - no lane, gate or close ever compared the two sides, so an obligation voided for a sound reason removed the strategy's central proof with nothing to notice the trade. The report now names each unit that reached terminal with an undischarged declared obligation. Measured on RUN-01KYJZGZ: 24 of 33.
- **A lane that never came back is reported at the next dispatch (BG0355).** A lane dying mid-flight leaves real code in the working tree behind a unit still marked Ready, and a restart cannot tell a delivered unit from an untouched one because the revision row is written BEFORE the work. Briefing a unit now records an in-flight marker that a return clears, and the next brief warns that the tree may already carry the work.

<!-- section: Fixed -->
- **One changelog rule that parallel lanes can obey (US0536, US0537).** The doctrine said to ship the paperwork in the same commit and left HOW to the reader, so an author following it reasonably reached for `[Unreleased]` - one region of one file, which two lanes cannot both edit. The fragment path is now stated as the rule for a lane, and `unreleased_hand_edit` refuses a direct edit while naming the fragment command, the file to write and the compose step. An edit to a released section is untouched: that history stays hand-editable.
- **The carried-lesson set is one file read one way (BG0365).** It was held in three places: `lessons.CARRIED_FILE` named `CARRIED-LESSONS.md`, `sprint` named - and the tree carried - `LESSONS-TOP.md`, and the writer parsed a bullet list the file does not use. So a curation written by a retro and the set a lane was briefed on were two different files, and the writer read zero lessons out of a file the readers read five from. One constant, derived by the reader; one parser, reading the numbered-section shape the file uses with the older bullet form still accepted.
- **An unreadable batch reads as unreadable, not as nothing delivered (BG0362).** A Batch line written as prose yields no unit ids, and the report stated the sprint delivered nothing - an empty measurement presented as a finding. The two readings call for opposite responses, so the report no longer picks the alarming one by default.
- **The overhead ratio says where the unattributed time went (BG0366).** Delivery is derived by SUBTRACTION, so every minute of overhead the instruments failed to attribute is credited to delivery and the ratio flatters the loop exactly in proportion to how poorly it is measured. Naming the missing components is not the same as saying their time was counted as delivery; the line now says both.
- **The goal review is a bookend (US0545, US0546, US0547).** The seats reviewed whether a goal was ACHIEVABLE; nobody asked whether the chosen content would deliver it, or - at the other end - whether what was delivered did. Both ends are now recorded. A `partial` or `no` that names nothing missing is REFUSED: the value of the question is the list of what the content does not cover, and an unexplained doubt is one nobody can act on and the close cannot score against. The close question carries the undelivered units and the defects raised WITH it rather than relying on recall, and the two answers are shown side by side with a prediction miss reported where the plan said yes and the close did not - a question whose answer is never checked gets a confident yes every time.
- **An open defect is judged against the goal, not against a guessed severity (US0543).** A defect that falsifies a goal clause blocks the close; one that does not is recorded LEAVABLE with its priority and the reasoning, never silently dropped - shipping with a known defect is a decision, and one nobody wrote down is indistinguishable from not having noticed. A release-stopping priority blocks whatever the clause reasoning says, because a clause argument can be made for almost anything and "the goal was met anyway" is not an answer to a user who cannot work around it.
- **The bounded exit files one artefact per cause (US0551, US0552).** One owed sign-off across twenty-three units is ONE thing to fix, and it arrived in the discovery backlog as twenty-three identical change requests - a cost paid twice, once at the close and again by whoever had to work out they were one. Blockers sharing a stage and a remedy (unit ids stripped) are filed as a single artefact listing every unit it covers, blockers with genuinely different remedies stay separate so grouping cannot hide one behind another, and the close states how many artefacts it filed for how many blockers across how many distinct causes.
- **The persona registry is resolved by the path that mints work (CR0425, CR0426).** `personas/index.md` declared a Primary, a Secondary and a negative persona that nothing downstream read: of 246 stories created after the registry was declared load-bearing, none named one. A shared reader now parses it, `artifact.py` resolves `--persona` through it (the declared Primary by default, a warning on an unregistered name, a refusal under `--strict`, and a warning but never a refusal for the negative persona), and the `new`, `batch` and `refine` paths are proven by test to agree. The PRD's Target Users section now names the registry's personas instead of the superseded set, and `personas.md` is an explicitly-labelled legacy appendix that no live document routes a reader to.
- **A REJECT can now be ANSWERED, and coverage reports three states instead of two (EP0205, CR0506).** `sprint_covers_independently` was satisfied only by an APPROVE and no verb recorded what was done about a rejection, so a batch that was independently reviewed, rejected, repaired and mutation-verified reported with the same word as one nobody opened. Measured three times in four days across **41 units**: on one run the preflight said "28 of 44 covered by no independent review" while 18 of those 28 carried a REJECT whose every finding had been repaired in-run. The number was wrong by 18 out of 19, and wrong in the direction that hides the one real gap inside a crowd of false ones.
  - `critic repair` records a repair against a unit's live REJECT, naming each finding it closes and the evidence closing it - a re-applied mutant, a test that now reddens, or the artefact the residue was filed as. It is **append-only and never overwrites the verdict**: what the reviewer found stays true and what was done about it becomes visible beside it, and `critic show` prints both, because the whole value is that a reader of the verdict sees the disposition without knowing a second command exists.
  - A repair naming a finding the verdict never raised is refused, and so is one with no author - a repair is a claim about work somebody did, and an unattributed claim cannot be questioned.
  - A repair closing fewer findings than the rejection raised is **PARTIAL** and names the outstanding ones individually. Completeness is derived per finding and never read from the repair's own prose, so a repair claiming it closed everything is still partial if a raised finding has no closure.
  - Coverage distinguishes **approved / repaired / unreviewed**, and both failure directions are closed: reading the middle state as unreviewed manufactures work, and reading it as approved would clear the gate on an unrepaired rejection. Only a COMPLETE repair reaches the repaired state. Conformance reports it in its own words rather than the `missing critiqued (independent APPROVE verdict)` it used for repaired units and for units nobody had opened alike.
  - A finding closed by FILING is recorded distinctly from one closed by fixing, with the artefact id - and an id resolving to no artefact is refused, because a reference nobody can follow records the appearance of a disposition rather than one. Both dispositions are legitimate; being unable to tell them apart afterwards is not.
  - The close preflight states the counts separately and NAMES the units nobody reviewed. It also splits an unanswered rejection from a unit never opened: those are different facts, and collapsing them would be the same defect one level down.
- **A sprint now has ONE compulsory checklist, and it is the sprint report (CR0505, EP0192).** What a run dropped, what crept into it and what it carries were known only to whoever ran it: the record was scattered across artefact statuses, commit messages and prose, nothing stated the compulsory set, so no lane could hold it and the close became an interview. `sprint_report.py` now composes one row per STAGE of the cycle - the pre-plan reconcile, the goal's seat review, the grooming gate, the run opening, the batch-boundary reviews, the closing review, the goal verdict, the retro, the lessons, the sign-off, the handoff - each stating `ran`, `not-run` or `waived`, beside the figures a close otherwise re-derived by hand: planned against delivered, dropped / held / carried over each with its reason, scope creep as a count and a ratio, who reviewed what under which seat and over how many lenses, the impediments still standing, the carried known issues, and the cost. `sprint close` runs it as a chain step that REFUSES on an unanswered item and names it, `sprint_report.py checklist --id RETROxxxx` asks the same question on its own, and closing without an item needs a recorded waiver (`decisions.py waive --subject rule:sprint-checklist:<item>`) on the same terms as a conformance waiver. Three properties are load-bearing. All but one row is DERIVED: a checklist that asks an agent to retype what the tree already holds is filled in with what the agent remembers. The exception is each carried finding's stop-ship ruling, which is a judgement, so it lives in the retro's new `## Known issues carried` table and an open finding with no row reads UNRULED - "we carried it" and "nobody looked" must never render the same, and a `stop-ship` ruling holds the close. The checklist cannot drift from the cycle: `cycle_drift()` fails when a `sprint` ceremony verb has no row and is not declared mechanics, derived from the shipped CLI rather than from the checklist, so the two can genuinely disagree. And it is not a deadlock: the sign-off and handoff rows are reported but never held, because the close produces them itself and a gate whose only exit is the step it blocks is not a gate.
- **`sprint plan` records its pre-plan reconcile verdict on the run (EP0192).** The check ran on every plan and left no trace, so a close could not show that its batch had been selected against a drift-free census - and a stage whose evidence does not exist cannot be certified, however reliably it happens.
- **The adversarial review moves to the delivery batch boundary (EP0190, from CR0500).** Where the review runs decides what its findings cost. Run at the close, every defect it finds is close work by definition: it arrives after the sprint is nominally over, is repaired fast and late by whoever still holds the context, and lands in guards and release paths. One measured run delivered in five hours and took six and a half to close, of which only about 18% was gate and suite time - the rest was repair generated by a close-time review.

  `sprint review-batch` is the review point. `--open <ids>` starts a delivery-batch span on the run state; recording the pass closes it, delegating the independence proof to the existing `critic.record_sprint_review` rather than reimplementing it (a second copy of those rules is a second place for them to drift). The review's surface is THAT batch's units, so a pass over batch 1 leaves batch 2 uncovered - which is the point.

  `sprint close` gains `review-coverage` as the FIRST chain step: it REFUSES a batch carrying units no independent pass covered, names every one, and prints the invocation that would clear it. Refusing first costs seconds instead of refusing after a retro scaffold and a full gate run. **The close asserts that coverage exists; it does not perform the review.** A self-review clears nothing - and because `critic.record_verdict` records a reviewer/author pair without refusing an identical one, the coverage predicate does that reading itself.

  Any finding filed while a span is open is stamped `Raised-in-batch` and recorded against that span, so a run can report WHERE its defects were found; filed with no span open, the artefact states that rather than being attributed to the last one. The close prints the split, because "defects are found inside the sprint" is only falsifiable if the number is recorded.

  The placement ships as doctrine (`reference-doctrine.md` rule 18), as a Definition of Done section, and in `help/sprint.md`, so a consuming project inherits the placement and not only the lesson.
- **The specs' derivable claims are now checked against the repo (EP0167).** Three claims a reader takes as fact were held by nothing.

  **The version guard's coverage follows the repo (US0452).** It carried a hand-maintained list of spec files that had never been extended to `trd.md` or `tsd.md`, so two spec files could drift for as long as anyone cared to look. Homes are now DISCOVERED: any tracked markdown declaring a version is held, so a new home is covered on the day it declares one. Discovery uses the tracked listing where git can give it and a tree walk where it cannot, degrading toward checking MORE rather than toward a clean scan over nothing, and refusing outright when the tree itself is unreadable. Two exclusions, both principled: a SUPERSEDED document records what was true then, and holding it to the current version would force falsifying the record to go green; and an artefact REPORTING a version mismatch quotes a version, so holding it to the current one would make that report unfileable.

  **Countable claims are checked against a census (US0453).** `tools/check_spec_claims.py` reads the growth-tolerant bands the specs carry - "60+ scripts", "50+ reference files" - and compares each with a count taken at run time. The expected value is never stored, so adding or removing a script cannot put the guard out of date. A claim naming a census the tool does not know, or carrying a number it cannot parse, is REPORTED and fails: a silent skip is indistinguishable from a pass, which is the failure this exists to remove. It runs as a `spec-claims` lane in the gate people already run.

  **Timing claims are checked against recorded measurements (US0454).** A marked timing claim is compared with the MEDIAN of the recorded series - not the best run, because a bound justified by the fastest measurement ever taken is a bound nobody experiences, and this project has already had to correct one performance figure built from a cherry-picked pair. An absent measurement is reported UNVERIFIABLE, never treated as agreement.
- **Filed: a sprint has no compulsory checklist and no report document (CR0505, operator-directed for the next sprint).** A run's record is scattered across artefact statuses, commit messages and prose, so what was dropped, what crept in and what is carried are known only to whoever ran it. Measured on an 11-unit batch: the review ran outside the shipped seat ceremony and nothing noticed; 17 unplanned artefacts were filed against 11 planned units; two units held on an operator decision were recorded in conversation only; and the stop-ship ruling on eleven carried known issues existed nowhere until it was written by hand. The CR asks for ONE artefact that is both the compulsory checklist and the sprint report, with every item DERIVED where the tree already holds it - a checklist that asks an agent to retype delivered points gets filled in with what the agent remembers - and a close that REFUSES on an unanswered item, because the three previous attempts to make a practice compulsory by writing it down were all skipped.
- **Filed: closing review is doing the work development should have done (CR0504).** Measured on an 11-unit, 47-point batch delivered green with mutation evidence: five independent reviewers returned REJECT on all five groups, 14 MAJOR findings, one of them a wrong number already committed. Five defect classes account for all 14, each attested two or three times in that one batch - a new reader of a shared field diverging from the idiom every other reader uses; a test that can agree with the code by construction; prose promising what no code path implements; no shape census of the real corpus before writing a parser; and a new gate lane not carrying the guards its siblings carry. The CR asks for the two mechanisable classes as detectors rather than checklist items, because a checklist only a diligent author reads is what these five instances already had.
- **Filed: the seat-based review ceremony is complete, mechanical and entirely optional (CR0503).** `critic.py brief --seat` assembles a seat-framed prompt and refuses to issue one missing any standing practice - the claim inventory, per-item repair verdicts, mutate-the-author's-tests, isolation re-testing, regression cover, two reviewers per round on distinct lenses - and `evidence --from-verdict` parses the returned block so no verdict is hand-transcribed. Closing an 11-unit batch, all of that was bypassed in favour of hand-written briefs to generic subagents, and nothing refused or warned. The load-bearing ask is that an evidence row record HOW it was obtained; without that marker the rules carry exactly the enforcement the bypassed ones had.
- **A bug reaching `Fixed` is held to an oracle, the way a story is at `Done`.** Having
  criteria is not the same as anything speaking for them: eight terminal bugs carried 31
  unticked boxes and zero `Verify:` lines and passed every check, which is a status the
  artefact's own body contradicts. EITHER oracle satisfies the gate - a tick is a human saying
  they checked it, a `Verify:` line is the machine saying so - because demanding both would
  refuse the ordinary judgement call a bug fix often is.

### Fixed

- **BG0402 no longer stands at `Fixed` while declaring itself unfinished.** Two of its four
  criteria were labelled NOT YET FIXED; they are carved out to BG0485, where their status is
  honest, and what remains describes what actually shipped.

Measured before shipping: 273 of 465 terminal bugs here (58%) carry no oracle. Scoped to BUGS -
a story at `Done` already passes the AC-verify gate, which EXECUTES its criteria and is the
stronger oracle; applying this on top refused stories that gate accepts, caught by 20 failing
fixtures before it shipped.

The gate is on the TRANSITION, so the eight artefacts already terminal keep their status and
their debt stays visible in their bodies rather than being retro-blocked.

- **The dead-flag analysis records exactly which destinations it cannot judge**, one
  `module:dest` per line in a shrink-only baseline. `unresolved` is module-scoped, so ONE
  escape the analysis cannot follow demoted every unread destination in that module - including
  ones the escape had nothing to do with - and nothing counted the difference. A module with a
  single `somewhere_else.setup(args)` call reported `1 not judged, exit 0`; deleting that line
  reported the same flag DEAD.
- **Both directions are reported**: a pair absent from the baseline (the hole widening) and a
  pair now judgeable (the baseline gone stale). A COUNT would be satisfied by one clearing
  while another appears - the hole moving while the number stands still.

Recorded rather than narrowed: scoping the demotion to destinations an escape could plausibly
reach needs dataflow this analyser does not have, and guessing would un-demote real cases.
Measured, the hole is 8 destinations across 3 modules.

- **A guard refuses a NEW hand-copied list of shipped scripts in a test file.** A hand-written
  mirror is a second copy and goes stale the way every second copy does - silently, and in the
  direction that makes the tests pass while covering less. Seven such mirrors were found in one
  suite. Verified adversarially: a seventh copy was written in on purpose, killed, and removed.
- **The one deliberate INVENTORY is exempt by declaration and says why.** `EXPECTED_LANES` IS
  the assertion; derived from the hook it checks, it would agree with any hook including one
  that had lost a lane. Without that note the next reader derives it and deletes the assertion,
  so the distinction is recorded as a decision rather than left to habit.
- The one pre-existing hit was a PROBE set, not a mirror - its assertion is that more than one
  writer appears - and it is declared as such rather than derived.
- **The close now asks the estimate question its own template promises (BG0414).** The retro template reserves a generated block for the estimate-versus-actual comparison and its prose asserts the question is asked every sprint rather than only when someone remembers. Nothing ran it. The largest sprint on record therefore contributed no row to the calibration every later forecast is drawn from, and an empty block reads as "no comparison to make" - indistinguishable from "the comparison was never run". `retro-accuracy` is now a step of the close chain, placed after the retro passes its own content check so derived content is never written onto a malformed document, and included in `close --dry-run`'s preview so its completeness claim stays true. It blocks only when the write itself fails, which means the retro or the ledger is malformed and the operator needs to know before the close records anything else; a batch with no recorded forecast has nothing to compare and says so rather than failing.
- **A grandfathering baseline may only shrink, and now a guard says so (BG0367).** `validate.py` documented both baselines as "captured from the checker's own output, never hand-written, and removing a line is one-way, so the recorded count can only fall" - and nothing enforced it. Read as plain sets, adding an id was a supported way to bypass the floor entirely, turning an exemption meant to be TIME-BOXED into a permanent and extensible one. The new guard compares each baseline against its committed state in git, which is where the previous state lives - a high-water mark written into the repo would itself be a number someone could edit - and guards itself against `git show` silently failing, which would make every assertion pass vacuously.
- **A writer's `--fields-file` can carry metadata as well as prose (US0418, EP0156).**
  `resolve_prose_fields` gains a `metadata_keys` argument: `allowed` now names every field the
  writer accepts - prose and metadata - so one committed, re-runnable document is the whole
  invocation, while the shell-hazard check covers the prose keys (everything not declared metadata,
  a fail-safe default so a forgotten prose field stays checked). An unknown key is still refused by
  name, and a caller that passes no `metadata_keys` is unchanged - the whole allowed set is treated
  as prose, exactly as before.
- **The commit-msg gate reports work a commit sweeps in under another unit's name (US0417, EP0156, CR0416).** A `git add -A` running for one unit while the next is being written stages the second unit's files too, and nothing could catch it: the multi-id rule demands a `Refs:` trailer only when the subject names two ids, and the floor attributes a commit's files to the ids the message declares - so one unit was credited with another's work and the swept-in unit read as delivered by nothing. The signal was available and unused, because every file already has an owning unit. The gate now names a unit whose files this commit modifies but whose id the message never mentions, and prints the `Refs:` line to paste. Two signals: the path carrying the id (a unit's artefact or changelog fragment - nothing inferred) and a file exactly one unit declares in its `Affects`. A file several units declare, or none, is never reported. Advisory only - it prints and the commit lands, even under the `--strict` flag the hook uses, because ownership is read from a declaration and only the multi-id rule may refuse.
- **`reconcile detect` reports a unit a delivered one appears to have already done (US0415, EP0156, CR0414).** The existing `built-not-closed` check reads the verification report, so it fires only where a unit's executable acceptance criteria all pass - and an ungroomed skeleton has no `Verify:` lines, so the one check built for "this is already done" was structurally blind to the case that matters most: work minted before it was groomed, satisfied by a later sprint, and never noticed. The new `already-delivered` lane reads no verifier at all. It reports a non-terminal unit only where a terminal one shares a declared file AND matches its title wording, because a shared `Affects` alone is already the planner's clustering signal; a pair already wired together (`Parent`/`Decomposed-into`/`Delivers`/`Epic`) is suppressed, since a decomposition shares its parent's title by construction. Advisory, never drift: the exit code answers a mechanical question, and whether two units mean the same thing is a judgement.
- **`artifact.py new` reports a probable re-filing before it mints (US0413, US0414, EP0156, CR0413).** The creator this project tells agents to reach for had no duplicate check at all, so a defect already on the backlog was re-filed in silence. It now compares the new title against every artefact of the same type - **terminal ones included**, because re-filing something already fixed is the case that wastes the most time - and names the candidate id, its status and the file the two share. Advisory by default (filing is never blocked by a heuristic, or the heuristic becomes a reason not to file); `--strict` refuses instead, and refuses before an id is allocated, so no file and no index row survive it. The thresholds were measured against this repo's own backlog rather than chosen: containment over the shorter title's distinctive words, because Jaccard scores the pair that motivated the check at 0.21 and would have missed it.
- **The retitle keeps inbound links alive and records the change (EP0150).** A retitle finds
  every inbound reference through the `check_links` inbound scan and repoints each to the new
  slug, or refuses and NAMES the ones it cannot safely rewrite (a row in immutable archived
  history), so a rename never leaves a dangling link. On success it writes a dated Revision
  History row recording the previous title through the shared `transition.append_revision_row`
  machinery, so the change is legible on the artefact rather than a filename disagreeing with
  history for no stated reason.
- **A deterministic retitle for the last field that had no writer (EP0150).**
  `artifact.py retitle --id X --title "..."` rewrites an artefact's three title surfaces -
  the H1, the filename slug and the index row's link target and Title cell - as one operation,
  all-validate-then-write: it refuses before any write if the H1 is absent, the new slug
  collides with an existing file, or the index row is missing, naming the blocked surface and
  the fix (a blocked retitle leaves all three byte-identical). The index side is synced by a
  new `reconcile.retitle_index_row`, so the third surface is written from the place status and
  counts already are, not a hand-edit.
- **`verify_ac.py run` refuses `--fresh` combined with a batch scope (US0395).** A rebuild
  keeps only the entries the run produced, so scoped it would silently delete every verdict
  outside the scope - including the `verified_at` and `ac_fingerprint` fields the completion
  gate reads to tell a fresh green from a carried-forward one. The combination now exits 2
  before any work, names both ways forward (drop the scope, or drop `--fresh`), and leaves
  the report byte-identical. `--fresh` on an unscoped run still rebuilds.
<!-- section: Changed -->
- **The scoped-run merge is pinned by its own tests (US0395).** A scoped run leaves every
  out-of-scope entry untouched field for field, freshness stamps included; and a scoped run
  and a whole-workspace run over the same stories now have an equivalence test comparing
  their per-story entries and the exit code they derive - the scope decides which stories
  are judged, never how one is judged.
- **`verify_ac.py run` takes the batch as a scope (US0394).** Three batch forms join the
  existing single-story `--id`: `--ids US0001,US0003` (comma-separated, repeatable,
  case-insensitive), `--worklist <file>` (the sprint planner's tranche shape - markdown
  bullets and `#` comment lines tolerated, repeats de-duplicated, so one file drives both),
  and `--from-run` (the story units of the open run's approved batch, refusing when no run
  is open rather than falling back to a whole-workspace run). Verifying a sprint's units
  is now one process instead of a whole-workspace run or one invocation per story. An id
  that resolves to no story file exits 2 naming it - never a silent skip a completion gate
  would read as green. The selectors are mutually exclusive.
- **Installed-copy drift is surfaced in the status hint and the close pre-flight (US0389).** A repository that carries a forward-port drift check now has its verdict reported where an agent already looks: one advisory line on `status hint` and `status pillars` naming how many files differ and the command that mirrors them, and one named blocker in `sprint close`'s pre-flight carrying the same remedy, so a close cannot sign work off while the copy every other project loads still holds the previous version. The verdict has a single owner, so the two surfaces cannot disagree. Guarded by the check's presence: a project with no drift check, no installed copy, a deliberately pinned one, or a check that errors or times out is silent, and the advisory never breaks the hint.
- **`forward-port.sh --check` reports drift in the installed copy (US0388).**
  The installed skill copy is what every other project on the machine loads, so the window
  between a fix landing in the repo and the mirror running is a window in which a fix
  believed shipped is in force nowhere - and nothing reported it, so it rested on someone
  remembering to ask. `--check` writes nothing, prints the itemised list and the count of
  differing files, and exits non-zero when that count is not zero. The count is over files:
  a directory rsync also itemises as a consequence of the files inside it does not inflate
  the number the operator is asked to act on. It honours the exclusions the mirror honours,
  so the consuming copy's `.local/` state and its bytecode and test caches are not drift.
  Two states are reported rather than failed: no installed copy at the target path, and a
  copy holding a `.local/forward-port.pin` marker.
- **Root-resolution census over the whole script family (US0383).** Every script in `scripts/` is now classified by how it turns `--root` into a project - anchored on the shared resolver, unanchored with a filed follow-up naming it, or a deliberate non-root surface with its reason stated - and `tests/test_root_census.py` re-measures the family on every run and holds the recorded census to that measurement. A script added with no entry fails the sweep, and a record claiming an anchor a script does not have fails too. First measurement: 5 anchored, 59 unanchored (26 of them writers), 5 non-root, over 69 scripts.

<!-- section: Fixed -->
- **`next_id.py` allocated against the cwd rather than the workspace (US0383).** All three verbs (`allocate`, `scan`, `collisions`) took the family default `--root .` as the current directory, so a run from a subdirectory scanned an empty tree and handed back an id the workspace above it already held - a collision minted by the one tool whose job is to prevent them. They resolve through `sdlc_md.resolve_root` now, which is why the allocator was repaired ahead of the rest of the census.
- **One project-root resolver for the whole script family (US0382).** `sdlc_md.resolve_root` / `discover_root` / `under_root` are now the single sanctioned way a script turns `--root` into a path and anchors a relative output on it: a NAMED root is honoured verbatim, the family default `.` is discovered upward to the nearest directory holding an `sdlc-studio/` workspace rather than assumed to be the cwd, and an absolute output path is passed through untouched. `verify_ac` keeps the names its three importers already use, but they now delegate to the shared implementation instead of holding a second copy. The rule is stated in `reference-scripts.md`'s script contract and in `best-practices/script.md`.
- **The mutation run proposes a per-target covering command from its own reference scan (US0380, CR0377).** `mutation.py run --suggest-test` (or omitting `--test`) prints, per target, the referencing test files the scan found and a command that selects exactly them, with the honest caveat that reference-scan coverage is a heuristic - a test that names the target is not proof it exercises it. A run executed with the derived command produces zero out-of-selection warnings for its targets by construction: the same scan `_selection_warnings` reads backward to flag a referencing test outside the selection is now read forward to build the command, so the covering command lists the very files whose absence would warn. An uncovered target yields a null command and is named, never a fabricated pass. The hand-supplied `--test` path is unchanged and remains the default.
- **A mutation run over a surface with no mutatable sites records an empty surface as a first-class outcome, and the gate reads it distinct from not-run and PASS (US0379, CR0376).** An absence and a negative result are different facts: an empty surface (a docs-only change is the canonical case) has nothing to mutate, so `run_gate` short-circuits - no baseline, no window, no mutant, no test run - and writes a report carrying `empty_surface: true` with `baseline: not-run`, distinct from a refusal (a red baseline judged nothing) and from a measured pass (mutants applied and killed). The per-run series names it `nothing-to-mutate`, apart from `measured` and `no-evidence`. `mutation.py run` exits 0 with the reason named rather than a silent non-pass, and the gate's mutation lane reads the report as "nothing to mutate" - so a docs-only close is green with the reason on the record, never a clean sweep over zero mutants.
- **Skill entry points surface an applied mutant instead of silently executing one (US0377).** A mutation evidence run rewrites live source one file at a time for minutes at a stretch, and the in-flight sidecar that marks the window exactly was read by nothing: any script invoked in that window could run a mutated sibling, misbehave, and have the mutant's wrong behaviour attributed to the tool. `status` now prints a loud stderr warning naming the mutated file and the single-writer rule, then completes normally - a read is degraded evidence, not blocked. `artifact` and `transition` refuse outright with exit 2, naming the file and how to clear the sidecar, and write nothing: a write made through a mutated tool is one nobody can trust afterwards. The mutation run's own processes are exempt via a marker it sets on itself and on the environment its suites run under, so the run that applies the mutants is never blocked from cleaning up after itself, and a sidecar stranded by a killed run still recovers unchanged.
- **`critic supersede` retires a wrong verdict row without editing the append-only log (US0374).** A row can record an event that did not happen - a reviewer mis-entered, a verdict filed against the wrong unit - and until now the only remedy was hand-editing the one file whose value is that nobody edits it. `critic.py supersede` (alias `correct`) appends a `SUPERSEDED` record naming the retired row, the reason and the authoriser; the row stays in the table byte for byte, and later verdicts still land inside it. The record is prose, not a table row, because the parser reads every pipe-delimited line in the file. Refused loudly, writing nothing: a row that matches nothing or matches several (narrow it with `--reviewer`/`--verdict`, CLI exits 2), a missing reason or authoriser, and an authoriser who is the row's own author - the party that wrote the wrong row cannot retire it on its own say-so. The row's reviewer *is* allowed to authorise, because a row naming the wrong reviewer is the case this exists for.
- **An acceptance criterion corrected during delivery is recorded as an AC defect, distinct from an ordinary revision (US0370, CR0365).** A criterion that specified the WRONG behaviour and was amended is a spec failure, not a normal edit - the most expensive class of defect this project has found (US0375's AC asked the sign-off gate to ignore a superseded row, which IS the independence-gate bypass, and a passing test defended it). `critic.classify_revision` returns `ac-defect` only when a Revision History change both references a criterion and carries a correction-of-wrong-spec verb, or an explicit `AC-DEFECT` tag; adding, rewording, renumbering, or fixing a typo stays an ordinary `revision`. `critic.ac_defects(story)` returns the AC-defect rows a story's history holds so a close count can name them separately. An absence and a negative result are different facts: a story with no amendment carries no AC defect. Documented in `reference-verify.md`.
- **A third retro disposition, `fixed-in: <sha or unit>`, records a finding fixed within the sprint (US0366, CR0362).** Filing defers a finding to future work and declining defers it to none; a fix closes it now and reads as neither. `retro.dispositions_in` classifies a `fixed-in:` row as `fixed` (its `fixed-in:` prefix winning over a bare artefact-id read, the same precedence the `declined:` prefix already holds), and a bare `fixed` with no reference stays undecided - silence wearing a decision's clothes. `retro.validate` exports a `fixed` list, the gate's retro leg names it in its disposition detail, and the close counts (`retro.py validate` and `dispose`) name the three states separately: a sprint that repaired eleven findings no longer reads as having declined eleven. The retro template documents the disposition.
- **The shell-hazard detector now sees a substitution that already COMPLETED, and its miss rate is measured rather than implied (US0362).** The three shipped shapes all detect a metacharacter that survived, so the detector was silent on exactly the corruptions it was commissioned against: the backticks and everything between them are gone and the stored text carries no metacharacter at all. Three post-damage fingerprints were added - a collapsed double space, a space before clause punctuation, and a preposition left against punctuation - each reported, never repaired, because only the author can reconstruct what was removed. Measured against the four real corruptions, now recorded as a corpus in `tests/test_shell_hazard_rate.py`: it catches 3 of 4. The fourth lost a backticked token from the START of a sentence and left grammatical text behind, which is undetectable in principle. Measured against every prose field of every artefact in this repository - 1,668 fields, 856,277 characters - it reports one finding, and that finding is a real corruption the artefact quotes on purpose. The fields-file path remains the fix; this is defence in depth.
- **Prose reaches four more writers without crossing a shell, and a fields document can now arrive on stdin (US0361).** `decisions.py`, `lessons.py`, `ledger.py` and `handoff.py` gained `--fields-file`, routed through the one shared `file_finding.resolve_prose_fields` loader the converted writers already use, so a backtick in a rationale, a lesson body or a handoff title is stored as written rather than executed. A `--fields-file` of `-` reads the document from stdin, so a document another process produced no longer has to be spilled to a temporary file first. The four were invisible to the prose-writer sweep rather than recorded as gaps: it looked for six flag spellings and they take prose under `--rationale`, `--body`, `--reason` and `--title`, so the sweep now enumerates those too and `mutation.py`'s recorded gap names the second flag the widening exposed.
- **An over-appetite batch is recorded, and the close and retro report the over-commitment, not
  the raised ceiling (US0359, US0360, EP0124).** `run_state` now keeps BOTH the standing appetite
  (the sprint capacity) and the accepted one the run was planned with, flagging the overage per
  axis - so a batch accepted with `--appetite-units` past its standing appetite never reads as
  though it fitted. `sprint close` states the over-commitment (`N units against a standing appetite
  of M`), and the run's retro records the same trace with the note that the ceiling was raised to
  accept it, so a later reader asking why the run overran finds it.
- **The corpus report says which findings the change introduced (US0358).**
  Every finding is classified against a baseline revision - the same enumeration and the
  same rule set, run at that revision - and the summary line names the count of each class.
  A finding is fingerprinted by file, rule and offending text, never by line, so unrelated
  content inserted above a pre-existing finding does not relabel it; matching is counted
  rather than set-based, so a second copy of an existing defect is reported as introduced.
  A baseline that cannot be read (a shallow clone, a missing ref, no tag to derive one from)
  yields `unattributed` and says so, never `pre-existing`: failing the other way would
  quietly forgive every finding. The lane exits non-zero on an introduced or unattributed
  finding and zero when every finding predates the baseline. Measured on this repo: 526
  findings, of which 35 arrived after v4.1.0.
- **A whole-corpus markdown lane, enumerated from the tracked file list (US0357).**
  `tools/lint_corpus.py` lints every tracked `.md` file under the strict root
  `.markdownlint.json`, payload included. The change request's premise turned out to be
  false - nothing here linted only changed markdown - and the real hole was a config split:
  a `**/*.md` glob cannot match a path inside a dot-directory, so everything under
  `.claude/` was only ever reached by the lane running the payload config, which switches
  MD025, MD035, MD040, MD051, MD055, MD056 and MD060 off. That is how an unescaped table
  pipe in the shipped help sat green for an unknown number of commits. Enumeration now comes
  from `git ls-files` (dot-directories visible, `node_modules/` and agent worktrees not),
  and a missing markdownlint is an error rather than a clean report. Wired as `npm run
  lint:corpus` and a scheduled/dispatch-only `corpus` CI job - deliberately nothing in the
  pre-commit gate, which already runs ~197s against a 120s budget.
- **`conformance` and `validate` gain a diff-scoped mode, and the pre-commit gate uses it (US0354).** Both scripts take `--changed`, and the gate's `conformance` and `validate` lanes now judge only the artefacts the working tree touched, so a commit that changes nothing about a workspace's pre-existing backlog debt is no longer held hostage by it - the pressure that makes someone reach for `--no-verify`, which disarms every lane rather than the noisy two. Measured on this repo, the two lanes fall from 19.6s to 0.7s. Three rules keep the narrowing honest: every scoped run states what it judged, what it left advisory (by id) and which stages it did not judge; nothing is dropped from the report, only from the count that decides the exit code; and a repo-wide failure - the census, the story index, doc-coverage, the DoR/DoD check tags, the id-named-file sweep - is still counted and still blocks, so scoping cannot become a way to hide one. A git probe that cannot answer (no git, no commit, a root that is not the repository top level) falls back to the WHOLE workspace and says so, because unknown never means "nothing changed". `--release` restores both lanes to the whole workspace from the same function, so a commit is judged on what it changed and a tag on everything, with no second set of rules. The changed-file probe is now one shared idiom (`gate.changed_paths`), read by the mutation-surface lane as well.
- **`refine apply` and `refine add` take the whole breakdown as a file (US0353, CR0343).** `--breakdown FILE` reads a JSON or YAML breakdown - `epic-title` (or `into`) plus `stories` of title, points and affects - instead of repeated `--story` flags. A bulk decomposition was long fragile command lines whose faults surfaced one at a time at mint time; the file is checked WHOLE and every fault is reported in one refusal with nothing written, so a breakdown can be reviewed as data, version-controlled and re-run. A story entry may also be the same `title|points|affects` string the flag takes. The two input forms are alternatives: passing both is refused, because a file under review that disagrees with the command that ran is worse than either alone.
- **The plan emits a report-only file-disjoint lane partition, and exports it as per-team
  worklists (US0349, US0350, EP0118).** Every `sprint plan` now also reports lanes split so no file
  appears in two, from the same `Affects`/Verify files the clusters use - it selects, orders and
  forecasts nothing, only showing how the work would divide across teams or worktrees. A unit that
  declares no `Affects` is unplaceable and named, never dropped into a lane (an undeclared file is
  invisible to a collision check). `sprint plan --export-lanes DIR` writes each lane as a
  `--worklist`-readable file, with collision-freedom asserted on the exported artefacts and the
  caveat stated in each: disjointness is only as good as the declared `Affects`.
- **Every process lens cites the recorded incident it derives from.** Each lens's `Drawn from` cell names shipped lessons that resolve against `lessons/_index.md` with their files present, and a test refuses a project-local `L-` lesson or an artefact id (a bug, a run) as provenance, since the pack ships and such an id opens nothing in a consuming project.
- **Each process lens names the signature that finds it, and says so where there is none.** The lens parser carries a fifth `signature` column as its own field and derives whether it is mechanical, so a mechanical signature opens with a documented detector (`python3`, a skill script) and names only paths on disk, while a lens no search can single out declares the absence in a fixed `manual - <reason>` form rather than implying a check that does not exist.
- **A `process` audit lens pack, sibling to `test`.** Where `test` attacks the claims code makes about itself, `process` attacks the way a delivery was produced: five lenses (path-from-memory, count-by-hand, accepted-without-running, repair-without-plan, skipped-preflight), each drawn from a failure this project actually produced. It resolves as a named profile, is catalogued in both the reference and help, is wired to the shared 2-of-3 refute panel, hands the finder the file-or-decline discipline, and is refused rather than run clean when its lens table is empty.
- **The fixed per-sprint cost is MEASURED from the project's own whole-sprint actuals (US0337, EP0114, CR0391).** `retro.fixed_sprint_cost` fits `actual = fixed + marginal x points` across the velocity record's whole-sprint rows (Measured 0, ceremony included), names the retro ids it rests on, and reads UNMEASURED - with no figure, not the seed, not zero - where fewer than two sprints qualify. A per-unit build sum (Measured equals Units) omits the ceremony the term prices, so it does not count toward the two and is named as excluded.
- **The gate's `changelog-fragments` lane gains the structural check and a hand-edit guard,
  binding in both the standard and the release gate (US0331, CR0405).** The structural fault and
  a hand-edit are committed rather than tagged, so the lane now runs in the standard gate too,
  under its existing name; the stray-fragment reading stays release-only. While `changelog.d/`
  is live, a staged edit that adds content to `[Unreleased]` with no fragment consumed in the
  same commit fails, naming CHANGELOG.md and the `changelog.py` command that would have made the
  edit. An edit outside `[Unreleased]` - a release cut's rename, a correction to published
  history, the file header - is never refused.
- **`changelog.py` checks CHANGELOG.md's own `[Unreleased]` headings for the shapes a bad
  hand-insert produces (US0330, CR0405).** `structure_errors` fails on subsections out of the
  canonical order, a subsection repeated inside the release (naming both line numbers, the
  exact reparenting shape), or an empty subsection, and passes a well-formed file. It is scoped
  to `[Unreleased]`: released history below it is frozen and stays hand-editable. `compose` now
  inserts a created section at its canonical position rather than at the head, so the
  deterministic writer cannot emit a file its own check would reject.
- **The unresolvable-`Affects` refusal names the closest unique basename match (US0325, EP0110, CR0400).** A wrong directory prefix is a typing hazard, not a knowledge gap - the same wrong prefix was typed six times in one session by an author who knew the rule - so the refusal now holds the answer the tool can already see. A basename carried by exactly one file in the repository is named as the likely correction; one carried by several lists the candidates and states it cannot choose between them; one matching nothing says so plainly, so the author is never sent to a file the tool invented. The suggestion is built where the predicate lives, so every writer's refusal carries the same named candidate. Help, never a correction: nothing is rewritten on the author's behalf.
- **`artifact new` and `refine apply` refuse an unresolvable `Affects` before an id is allocated, minting nothing (US0324, EP0110, CR0400).** A story whose declared paths all resolve to nothing was written without a word by the two commands artefacts are actually created with; measured on one run, five of 23 stories minted through `refine apply` carried a wrong path. The check now runs at the moment the value is typed: a refused `artifact new` writes no file, adds no index row and burns no id (the next successful mint takes the one it would have), and `refine apply` stops the WHOLE batch before the epic exists rather than rolling back after minting two - a bad path in the last story of a decomposition mints nothing at all. A recorded grooming opt-out (`sprint.breakdown: judgement`) downgrades the refusal to a warning at both ends.
- **One resolvable-`Affects` predicate serves every writer and the grooming gate (US0323, EP0110, CR0400).** `file_finding.unresolvable_affects` is the single seam that decides whether a declared `Affects` resolves; `file_finding.file`, `artifact new`/`batch`, `refine apply` and `sprint.breakdown` all bottom out in it, so a path one command mints is never one another refuses, and a fourth writer added without the check is caught rather than passing silently. The predicate refuses only when a path is declared and NONE resolves - a file the unit will CREATE alongside an existing one is the ordinary case and stays legitimate, exactly the rule the grooming gate already applied.
- **The claim pass is ordered before the logic review and the two kinds of finding are reported separately (US0322, EP0109).** `review_prep.py` gains `review_phase_order` (claim-pass precedes logic-review) and `assess_review_round`, which reports a round recording logic findings with no claim pass run as INCOMPLETE and counts prose and logic findings apart - so a prose-only round is visibly a different kind of round from a logic one, convergence told from churn.
- **An unverifiable claim is reported UNVERIFIABLE and counted apart from TRUE (US0321, EP0109).** `critic.py summarise_claim_pass` keeps UNVERIFIABLE its own category, reports how many claims rest on trust, and marks a pass VERIFIED only when at least one claim was settled against the code. `render_claim_pass` renders an all-UNVERIFIABLE pass as NOT VERIFIED - nothing was checked - so it cannot read the same as a clean pass that looked and found nothing wrong.
- **The reviewer brief directs a claim-inventory first pass over all four prose surfaces (US0320, EP0109).** The brief now enumerates every assertion in Resolutions, docstrings, comments and CHANGELOG entries, each marked TRUE, FALSE or UNVERIFIABLE. `critic.py assert_brief_claim_pass` refuses a pass omitting any of the four surfaces (an omitted surface is exempted) or the ruling vocabulary; `validate_claim_inventory` refuses an inventory leaving any enumerated claim unruled, naming it. Documented in the `reference-review.md` closing-review-brief section.
- **A repair review is briefed with the previous round's findings enumerated and returns a per-item CLOSED / OVER-CLAIMED / MOVED verdict (US0319, EP0108).** `critic.py` gains `enumerate_repair_findings` (each prior finding listed item by item, refusing an empty set), `validate_repair_verdict` (refuses a verdict leaving any finding unruled or ruled off the vocabulary), and `repair_open_findings` (everything not CLOSED is still open - a MOVED defect survived, and counting it closed is how a repair masks the defect beside it).
- **The shipped reviewer brief carries the three standing adversarial practices, each with its reason (US0318, EP0108).** `critic.py brief` now weaves in per-item repair verdicts (rule each previous finding CLOSED, OVER-CLAIMED or MOVED), mutating the author's TESTS not only the code, and isolation re-testing of a surviving mutant - each paired with the reason it exists. `assert_brief_practices` refuses a brief missing any of the three, and a practice named without its reason still counts as missing. `reference-review.md` documents them under a new closing-review-brief section; the survivor practice directs isolation before any conclusion is drawn.
- **A message and the verdict it describes are driven by ONE test over one battery (US0317, EP0107).** `mutation.py`'s glob probe battery is now the single module constant `MATCHER_PROBE_BATTERY`, which `everything_reason` probes to derive the scope sentence and the gate lane's matcher is asked over to reach the verdict - two copies of that list is how the previous oracle came to agree with the matcher only on the shapes it had chosen. A reusable `message_verdict_disagreements` helper in `test_mutation.py` drives both sides over the one battery and names any input where they disagree; its `MessageVerdictAgreementTests` prove a derivation deliberately inverted to deny the verdict beside it goes red even when it keeps the pinned word `glob`, the exact shape a bare `assertIn("glob", msg)` let through five times. `best-practices/testing.md` states the pattern as heuristic 6 and names the counter-example it replaces.
- **The best-practice guides state that a guard's message is DERIVED from the guard, and name the counter-example (US0316, EP0107).** `best-practices/script.md` now carries the rule - a user-facing sentence about what a guard, gate or check will do is computed from the guard's own predicate, not written alongside it - and names the enumeration that impersonates a derivation: a list of the spellings a matcher happens to treat one way is a restatement wearing a function's clothes, where probing the real predicate is what makes it a derivation. `best-practices/documentation.md` links to that one statement rather than copying it. A new doc-invariant module `test_docs_derivation_rule.py` locks all three: the rule is present and no sentence denies it (a polarity scan, honest about being one), both halves of the counter-example are named or the check fails, and the rule appears exactly once across the two guides with a link whose anchor resolves.
- **`tools/forward-port.sh`: the dev-repo rsync to the installed copy as a guarded
  one-liner (CR0330, EP0070).** Dry-run by default printing the itemised diff, `--yes`
  to apply; the canonical exclusions (`.local`, `__pycache__`) are baked in so a
  `--delete` sweep can never destroy the installed copy's local state; a non-dev-repo
  cwd or a target inside the repo (the reversed direction) is refused loudly. AGENTS.md
  points at the script instead of an inline incantation. Dev-repo-only tooling.
- **`critic brief --rejoinder`: the re-verdict loop's scaffolding made deterministic
  (CR0329, EP0069).** Emits the re-review brief from the prior verdict file - the prior
  VERDICT/ISSUES/BLOCKING quoted verbatim, the diff scope refreshed, the structural demand
  to re-execute the previously named probes and mutants before approving, and the same
  return contract. A malformed prior-verdict file is refused loudly.
- **`sprint close`: the hand-carried close ceremony as one deterministic command (CR0328,
  EP0068).** Orchestrates goal-verdict (recorded or reused, refused when unjudged), retro
  validate + extract, lessons summary, `gate --require-retro --require-review`, handoff and
  reconcile with fail-loud stops naming each remedy; re-runs resume idempotently. Ends by
  printing the sign-off decision brief composed from the committed records - deliveries,
  verdict + REJECT history, gate and mutation results, forecast vs measured telemetry spend.
  Absent retro content, an unset goal, or an unjudged goal-verdict are refusals with the
  command to run, never defaults.
  Closing-review repair: the brief's mutation note names a red-baseline report WORTHLESS
  and surfaces errored/truncated counts instead of a neutral killed/survived line.
- **init writes the DoR/DoD defaults and offers a stack-derived tailoring pass (RFC0043
  slice 3, CR0326, EP0067).** `init run` seeds `definition-of-ready.md` /
  `definition-of-done.md` from the shipped templates; with `--detect` it prints tailoring
  suggestions derived from the detected profile (language, Dockerfile deploy surface) -
  applied only with `--accept-tailoring`, never automatically, and the tailored result
  always passes the check-id registry validation.
- **The gates read the DoR/DoD documents (RFC0043 slice 2, CR0325, EP0066).** `sprint plan`
  grooming resolves the story-level DoR; `transition -> Done` and conformance's review
  stages resolve the story-level DoD; `gate --require-retro`/`--require-review` resolve the
  sprint-level DoD (RFC0042's close-down enforcement restated as the sprint-DoD close
  clause); `gate --release` resolves the release-level DoD. Absent documents keep today's
  behaviour byte-for-byte; a removed tag downgrades that criterion to human-judged,
  reported visibly in the gate output, never silently.
  Closing-review repair: the critiqued stage's two halves (critic verdict, two-role
  sign-off) now compose independently, so a DoD downgrading one never disarms the other.
- **DoR/DoD documents with a check-id registry (RFC0043 slice 1, CR0324, EP0065).**
  Editable `definition-of-ready.md` / `definition-of-done.md` templates (story / sprint /
  release levels) whose enforceable criteria carry `[check: <id>]` tags resolving through
  one registered vocabulary (`lib/sdlc_md.py`); `validate check` fails loud on an unknown
  id, untagged criteria are explicitly human-judged. The documents state the
  non-negotiable rule: under pressure cut scope, never weaken the bar.
- **Two-role review gate (RFC0044 D1+D3, CR0323, EP0064).** The adversarial seat pass is
  recorded as evidence (`critic.py evidence`, own log, `--from-verdict` supported), and the
  reviewer-of-record sign-off (`critic.py signoff`) must come from a principal the author does
  not control - a named delegate needs its separate trust boundary and the chain is recorded;
  the author or an authoring-session subagent as delegate/principal is refused loudly, with a
  conformance backstop for hand-edited rows. `critic.py signoff-brief` embeds the decision
  brief (deliveries, verdict + REJECT history, evidence, gate/cost notes) with
  approve/hold/delegate paths. Opt-in forward-only via `review.two_role_after`; with it set,
  conformance `critiqued` requires evidence + independent sign-off past the cutoff.
- **RFC decision paperwork, tool-carried (CR0327, EP0061).** The creators
  (`file_finding file`, `artifact new`) accept `--parent RFCxxxx`: the parent must resolve
  before anything is minted, and BOTH link directions (the child's Parent, the parent's
  Decomposed-into) are wired in the same mint - a link asymmetry can no longer be created.
  `rfc resolve --rfc --decision --resolution [--refs]` marks exactly the named decision row
  Resolved with the operator's text and appends a revision row, every other row
  byte-identical. The triage ceremony is decide -> resolve -> spawn.
- **Shared test-module loader (CR0317, EP0060).** `scripts/tests/loader.py` `load_script`
  is the one authority for importing a script under test (idempotent, sys.modules-registered,
  monkeypatch-through-the-module safe); `test_flow.py` adopts it as the exemplar. The ~8-line
  importlib incantation duplicated across the suite has a single home.
- **The critic ceremony's deterministic scaffolding (CR0316, EP0059).** `critic.py brief
  --unit --seat [--tier]` assembles the seat-review prompt (charter, canonical ACs,
  Affects-derived scope, return contract) so every review starts from the same complete
  brief; `record --from-verdict FILE|-` parses the returned VERDICT/ISSUES/BLOCKING block,
  refusing malformed input, so a verdict is never hand-transcribed. Judgement stays with the
  seat; the plumbing stops costing improvisation.
- **Per-unit CHANGELOG fragments (CR0315, EP0058).** A unit's entry lives in
  `changelog.d/<unit>.md`, committed with the unit - no shared-file contention, no hold-back
  dance. `changelog.py compose` folds fragments into `[Unreleased]` and consumes them
  (all-validate-then-write; malformed fragments refuse by name); the release gate's new
  `changelog-fragments` lane fails a cut while a stray fragment exists; the doc-coverage
  changelog check accepts a pending fragment as the entry. This very entry shipped as the
  convention's first dogfood fragment.
- **refine seeds story ACs from the request (CR0309, EP0057).** `refine apply` copies the
  request's `- [ ]` acceptance criteria into the first minted story as AC scaffolds (the
  criterion is the title and the Then; Given/When and the Verify stay explicit
  placeholders - seeding transcribes, it never fakes executability, and validate keeps
  flagging until the author fills them). Multi-story breakdowns get a redistribute note;
  `--no-seed-acs` restores the bare scaffold.
- **The review close, tool-carried (CR0307, EP0056).** `review_prep.py close --rv RVxxxx
  [--latest-body FILE|-]` stamps review-state.json for every present leg and derives
  reviews/LATEST.md from the supplied anchor - refusing when the dated RV record does not
  exist and refusing an anchor that never cites it. A review can no longer live only in the
  overwritable anchor (the near-loss that motivated this), and the CRITICAL state stamp the
  workflow used to spell out as hand-steps is one command.
- **`sprint plan` offers sequential or parallel delivery, and only when the batch genuinely decomposes (EP0154, CR0411).** The plan now states whether the batch may be built in parallel isolated worktrees or must go sequentially, names the file-disjoint groups a parallel build would fan out to, and gives the reason the alternative was or was not available. Parallel is withheld for a one-unit batch, an all-coupled batch, or any unit with no declared `Affects` (unknown blast radius). Test files count as coupling: a shared test module conflicts on merge exactly as a shared source module does, so a test-file-only overlap denies the parallel offer. The offer is deterministic for a given batch and repo state. New `reference-delivery.md` records the contract.
- **`goal-review brief` emits a deterministic seat brief, recorded with the verdicts (EP0153).** The brief a review seat is given before it judges the Sprint Goal is now composed from the plan and run state - the batch, its grooming state (placeholder ACs, shared-file clusters, reachable end state) and this project's own failure modes from the lessons registry - so the same batch and goal produce the same brief. Record it with `--brief "<text>"` so a thin verdict can be told from a thin brief, and supply seat verdicts and notes through `--fields-file` (JSON) so a note quoting a command in backticks is stored verbatim rather than mangled by a shell.
- **`goal-review record` distinguishes an amendment from a material change (EP0152).** A goal reworded at a seat's request is recorded with `--amend-from "<prior>" --requesting-seat <role>`: that seat's verdict carries forward to the amended goal (it is discharged), the round records the prior wording and the requesting seat, and the remaining seats are reported as `needs_reconsult`. A `--material` change carries nothing forward and every seat re-reviews. The amendment/material call is the operator's declaration, recorded on the round, not the tool's guess.
- **The forecast prices the rung, not just the build (EP0151, CR0407).** A `--goal design`, `plan` or `triage` run does not build the units it grooms, so the token forecast now NAMES the rung it prices and reads UNMEASURED for the marginal term on any rung other than `done` rather than borrowing the build rate - a design run that writes no code is no longer priced as a build. On the close side, a non-`done` rung records its token actual but leaves tokens-per-point BLANK, so the magnitude-wrong figure a design rung once published (834,008/pt over a handful of terminal points) never reaches the file the planner re-measures its rate from.
- **`critic signoff`, `close_owed baseline` and `sprint goal-verdict` accept `--fields-file` (EP0146, CR0392).** Their free-text notes (a sign-off note, a baseline note, a goal-verdict rationale) now read from a JSON document through the shared `file_finding.resolve_prose_fields` loader, so prose carrying shell metacharacters is stored verbatim rather than interpreted by a shell. On the flag path the same loader reports any detected shell hazard on stderr (non-blocking); on the fields-file path it reports none, because that prose crossed no shell. `shell_hazards`/`report_shell_hazards` gained a `keys` parameter so a writer's own prose fields are checked, not only the finding filer's default set.

<!-- section: Fixed -->
- **The prose-writer registry no longer defers any writer it can resolve (EP0146).** critic.py, close_owed.py and sprint.py move to `SAFE_INPUT_WRITERS`; telemetry.py is reclassified safe-by-nature (its only prose-flag match, `show --summary`, is a boolean, so it takes no free prose - the earlier "note prose on the command line" reason was wrong).
- **`sprint plan` tells built-not-closed from unbuilt (EP0130).** A Draft story whose executable ACs all pass in the verify-report is a delivery that was never closed, not work to build. The plan now flags such a unit BUILT-NOT-CLOSED, excludes it from the build forecast rather than pricing it as new work, and - when every unit in the batch is already green - says so plainly and points at the close path instead of a build. A failing, stale or unrun unit is priced normally, so the flag never fires on genuinely unbuilt work.
- **A REJECT can be carried forward as filed findings, under a declared policy (EP0113, CR0404).** A REJECT blocked; now a project may declare `review.policy: carry-forward`, under which the sprint ships provided every finding is FILED as an artefact or explicitly WAIVED with a reason - the same fail-forward idiom `reference-review.md` already mandates for a missing review leg, with narrative downgrade refused in both directions. `block` stays the default so an upgrading project's close does not change, and an unrecognised policy is refused rather than defaulted. The close records the policy in force and lists the findings carried, each naming the units it was found against so it survives the close of the sprint that produced it.
- **The repair-plan gate: a REJECT is answered by a written plan, reviewed before any code is written (EP0106, RFC0053).** The repair was the only step in the delivery loop with no review before execution, and the step where a round's fix seeded the next round's finding. Now a REJECT produces a plan with one entry per finding (the change, the approach, what it might break); an independent pass reviews the plan, briefed with the four questions the loop keeps failing; the verdict is pinned to the findings it answered so a later finding invalidates it; a repair records which plan it executed; and a repeat-class repair must decide whether the design is retained or changed rather than proposing another instance forever. Opt-in per project via `review.repair_plan_gate`, off by default.
- **The plan measures its rate from the velocity record, and refuses rather than averaging
  across models (BG0248, US0290, CR0284).** `tokens_per_point` reads `retro.measured_rate` over
  VELOCITY.md first, falls back to the per-unit evidence log, and reaches the seed last. The
  previous join needed per-unit actuals that an interactive sprint never writes: 208 forecast
  records on this repo carried plan-time points and exactly 3 carried an actual, all from the
  runner era, so the counter promising "your own rate in two more units" described a state that
  could never arrive. A record spanning two models is REFUSED with its reason carried to the
  plan, because a rate averaged over two models describes neither.

- **The velocity record is part of the close, and its gaps are reportable (US0288, US0289,
  CR0284).** `close_owed` treats a missing velocity row as owed and `close_guard` blocks on it;
  `retro velocity --gaps` names every retro with no row. VELOCITY.md is backfilled for 24
  historical sprints through the normal writer, every unrecoverable Actual left blank beside a
  stated reason rather than rendered as a zero.

- **The token capture says which half is measured and which is supplied (BG0252).** The session
  transcript carries no sidechain records, so a fan-out sprint's delegated agents were invisible
  while the published figure was labelled "the run's own spend". The basis now names the main
  thread explicitly, delegated totals are recorded with `supplied` provenance beside `measured`,
  and the sum is published as a LOWER BOUND.

- **The forecast names what it excludes (BG0254).** The seed is unchanged at 25,000 - it is not
  refitted against a single sprint. The forecast now declares that it prices the BUILD, and shows
  a whole-sprint excess measured from the velocity record (1.63x to 6.59x across four retros),
  with an explicit note that this is proving cost plus any build under-estimate, since the record
  cannot split them.

- **Collision analysis derives files from Verify lines, and a contradicted `Affects` is reported
  (US0291, US0292, CR0347).** Test files are almost never declared, so the file parallel work
  most often shares was the one the analysis could not see; paths are now derived through the
  verifier parser itself. A declaration the artefact's own content contradicts - a path not on
  disk, or a file its Verify lines target but it omits - is reported per unit rather than only
  when every path fails. `validate` and the planner share ONE predicate so they cannot disagree.
  Advisory throughout: a path to a file the unit will create is legitimate, and a derived path
  never satisfies the `Affects` requirement.

- **The seats review the Sprint Goal, and an unreachable goal is named at plan time (US0297,
  US0298, CR0354).** `sprint goal-review record|show` captures a seat verdict on achievability
  and definition of done, blocking where a project declares seats. A goal unreachable by
  construction - `review.two_role_after` making Done unattainable inside the authoring session -
  is derived and reported before the work rather than discovered at the close.

- **A sprint stops only when nothing can proceed, and a stop is priced (US0299, US0300,
  CR0378).** The loop continues while any unit the pending question does not block remains;
  blockage is the transitive closure over declared `Depends on:` edges only, never a shared file.
  A stop records its cause, the units it blocked and the units that could have proceeded. The
  idle-gap deduction lives once in `telemetry.py` and is CALLED by both `sprint` and `retro`, so
  one sprint can no longer have two elapsed figures.

- **The mutation gate is judged on its own yield (US0301, US0302, US0309, CR0379).** Each run
  appends applied/killed/survived/unchecked and measured wall-clock to a series; artefacts filed
  from survivors link back to the run that found them; an `equivalent` verdict carrying a
  mandatory reason excludes a mutant from yield while keeping the exclusion visible. The sprint
  report renders cost against yield for the run and its trailing history, deriving cost per
  finding only where both halves exist and naming a run with no evidence instead of printing
  zeroes.

- **A declared rewrite window, enforced at the commit (US0307, US0308, US0310, CR0388).** A
  mutation or review window is a first-class declarable object surviving SIGKILL; an unreadable
  record reads OPEN, never closed. The pre-commit hook REFUSES a commit staging any path an open
  window claims. Built against the corrected mechanism - a shell redirect through a symlink farm,
  no mutant involved - so the guard depends on neither recognising a mutant nor the suite going
  red, which a surviving mutant leaves green by definition.

- **A non-shell filing path (US0305, US0306, CR0384).** `file_finding` and `artifact new` accept
  `--fields-file`, so prose reaches an artefact as data. The field most likely to contain shell
  commands is a bug's reproduction steps, which is exactly the field a shell mangles. The flag
  path survives for compatibility and now reports a detected hazard rather than silently emptying
  a field. The prose-writers still lacking the path are held in a registry whose stale entries
  fail a test, so the remaining debt cannot quietly expire.

- **A `test` audit lens profile (US0303, US0304, CR0382).** The qualitative backstop to the
  mutation gate: a surviving mutant proves a test cannot fail and says nothing about a docstring
  that lies. Four lenses, each citing a shipped lesson recording a failure this project produced.

- **`migrate --apply` seeds a missing AGENTS.md instead of reporting it as a human task (US0293,
  US0294, CR0352).** Seeding a file that does not exist is strictly safer than editing artefacts
  that do, which apply already did. An absent instructions file is marked seedable and its
  message names the command; severity and exit code are unchanged, because CI reads them.

- **The agent-instructions check verifies the working model, not just the pointers (US0295,
  US0296, CR0353).** Four rules test that the file establishes how the project is actually
  developed - delivery through stories and sprints, tool-allocated ids, executable ACs gating
  Done, review independent of the author - each citing the template section that supplies it. An
  opt-out is a `.config.yaml` key that is READ, with a test proving it changes behaviour.

- **The close review counts its rounds and stops at a ceiling (CR0358: US0261).** Each
  sprint-level review is recorded as a round on the run state. Past `review.max_rounds`
  (default 3) a further round is refused, naming the count, the ceiling and the override
  rather than leaving the reader to find the exit; buying another round is explicit and is
  recorded, so the retro can read that the ceiling was passed and where. The default is three
  because that is where this project's own history stops paying: one run reached five rounds
  and rounds 2, 3 and 4 each carried a defect the previous round's repair had created. A
  review recorded with no run open is still recorded - the evidence is never dropped - but
  nothing is counted against a run that has no identity to count against.

- **A finding is classified against the previous round's repair surface (CR0358: US0262).**
  A round-N finding landing in code round N-1's repair touched is reported as a repair
  regression, distinctly from a fresh finding, because the two call for opposite responses:
  one says the review is still earning its cost, the other says the repair loop is
  manufacturing the defects the review is being paid to catch. Matching is file AND line, not
  file alone - single files here run to thousands of lines, and a file-level match would call
  nearly everything a regression. Comparison is against the latest round only, since an
  earlier round's surface has already been re-reviewed. A finding that cannot be located is
  reported unclassified with its reason, never folded into the fresh count.

- **A repair regression escalates instead of buying another patch round (CR0358: US0263).**
  Revert, redesign and accept-and-file are offered by name with the consequence of each, and
  another patch round is deliberately not among them: when the patching is the cause, more of
  it is the one response the evidence rules out. Revert names the round and files it would
  undo, so the choice is not blind. `accept-and-file` mints a real artefact through the shared
  filer and reports its id, never a prose note claiming something was filed. The autonomous
  path records the question on the existing deferred-decision queue and blocks - a circuit
  breaker that picks its own answer is not a circuit breaker.

- **What the review rounds have cost, shown when the next one is offered (CR0358: US0264).**
  Each round records its token cost; the report gives the per-round figures and the cumulative
  total, so "is the next round worth buying" is asked against a number. An unmeasured round is
  named and the total marked PARTIAL rather than the round being summed as zero, which would
  read cheaper than the run was. A measured zero is a different fact from an unmeasured round
  and reads differently.

- **The reviewer's brief carries the work, not the framing (CR0358: US0265).** The brief holds
  the diff and risk surface but not the prior verdict prose, severity labels, round number, or
  any asserted conclusion. It deliberately narrows the request it came from: the probes a prior
  verdict named still travel, as a neutral checklist with the demand to re-execute them, because
  that re-execution is what makes a re-review trustworthy - removing prior verdicts wholesale
  would have deleted it. A prior verdict whose probes cannot be extracted is refused loudly
  rather than silently dropping the demand, which would leave a re-review weaker than the review
  it replaced. Neutrality is checked mechanically, excluding the return contract - that
  necessarily names both verdict words because it is the reply format, and offering the
  vocabulary as a required choice is not priming.

- **Deferred operator decisions - a run stops once, with structured questions (CR0369:
  US0280, US0281).** `sprint decision defer` sets a unit needing an operator decision aside
  on the run state while the batch continues; `decision list` asks everything accumulated
  together - the question, named options with their consequences, and the recommendation
  marked with its reason - never prose the operator must parse a choice out of; `decision
  resolve` is the only path that writes an answer, recording the ruling to the run state and
  the decisions ledger. The autonomous path (`defer --block`) records the question and marks
  the unit Blocked, never silently defaulting it.
- **A blocked close has a bounded exit (CR0371: US0282, US0283).** `sprint close
  --file-and-close` files every remaining ADMINISTRATIVE blocker (ceremony debt) as a real
  CR linked to the run, names the deferrals in both the retro and the review anchor, and
  closes with the new outcome `closed-outstanding` - stated plainly, nothing waived. A hard
  correctness blocker (a red gate lane, a refusing Done gate) refuses the whole exit. Every
  close attempt now records its outstanding count on the run state, and a re-run reports
  whether the set is shrinking or growing, so a close chasing a moving target is visible
  rather than inferred.
- **`reconcile` derives a request terminal when its children are all resolved (CR0364).** The
  two-backlog workflow says a request reaches its successful terminal by DERIVATION, and
  `transition` enforced the guard half - it refuses a premature close - but nothing ever performed
  the closure once it was earned. A project that ENFORCES the workflow therefore accumulated
  delivered requests still reading as open work: on this repo, 34 of 59 open CRs, with every
  delivering epic already Done, while `reconcile` reported zero drift. `detect` now reports the new
  `request-derivable` kind and `apply` closes it through `transition`, so the index row and every
  cascade still run. The detector calls the same `_request_terminal_gate` the close is checked
  against, so the two cannot drift apart - and what `apply` asserts is precisely what the gate
  would already have allowed. A childless request stays the separate `undecomposed` case, one
  unresolved child blocks it, a dropped child (Won't Implement / Won't Fix / Rejected) counts as
  resolved, and the whole thing is a no-op where the workflow is unenforced.
  - **The preflight tells the truth about refusals.** G2 is not the only gate on the road to a
    terminal, so `--dry-run` now takes the same road as the real sweep - it calls `transition` with
    `dry_run=True` rather than assuming G2's verdict is final. Short-circuiting made the preflight
    promise 36 derivations where the real run delivered 35, which is the one number an operator
    reads precisely to avoid that surprise.
  - **A refused derivation is data, not a printed aside.** `apply_derivable_requests` returns
    `{synced, unapplied}`; the refusal is counted like every other unapplied action, so the command
    exits non-zero, and it appears in the `--format json` payload. Previously a blocked run exited
    0 and was entirely absent from JSON, so a programmatic caller read it as clean.
  - **A drift item never advertises a remedy that cannot work.** Where a later gate still refuses
    (an RFC carrying an open decision, which `--force` deliberately cannot bypass), the item names
    that gate and says `reconcile apply` CANNOT clear it, instead of pointing at a command
    guaranteed to refuse.
  - **The close does not deadlock behind it.** `sprint close`'s reconcile step and
    `--apply-signoff`'s final reconcile both refused to finish while ANY drift existed, and the
    remedy they printed - `reconcile apply` - provably cannot clear a gate-blocked derivable
    request. Found live: the sign-off and Done transitions for a fully reviewed batch were
    stranded behind an RFC awaiting a decision nobody in the run could make. Both steps now
    report such an item and continue. The exemption is narrow - ordinary drift, and a derivable
    request that IS clearable, still block.
  - **The gate sees the new kind.** It counted only `detect_type` output, so `gate` reported PASS
    on a tree where `reconcile detect` exited 1. Only items `apply` can actually clear are counted:
    one blocked behind another gate is reported without blocking, because a gate that cannot be
    satisfied gets bypassed rather than fixed.
- **The `lessons-summary` gate lane can always be satisfied (BG0216).** The digest renders each
  lesson as `- **{id}: {title}**` and the parser found the title by scanning to the first `**`, so
  a lesson whose own text began with emphasis split at the wrong marker and read back with the
  bold in a different place. `summary_status` then reported the SAME lesson as both added and
  removed, and `lessons summary` regenerated a byte-identical file every time: a BLOCKING lane
  with no satisfying state, which deadlocked a real sprint close. The comparison now normalises
  emphasis away, so it is insensitive to where the markers land and still sensitive to every part
  of a lesson the digest carries - a test pins that a one-word edit is still detected, because a
  digest that stopped noticing real edits would be the worse defect.
- **`artifact.py close --dry-run` runs the same gate ladder as the real close (BG0214).** It
  returned a synthesised target before `transition` was ever called, so it answered `would close`
  for a story the real close refused, and exited 0 where the real path exits 1. Two pre-flights
  over the same transition gave opposite answers, and the one an agent reaches for first was the
  wrong one. The preview now goes through `transition(..., dry_run=True)`, which fires its gates
  for exactly this purpose and writes nothing. Three existing tests had to be corrected: they
  passed only because the preview consulted no gate, so the fixtures were closing artefacts the
  real run would have refused. The regression test uses a story the AC-verify gate REFUSES, since
  a fixture with a clean ladder cannot tell an honest preview from a blind one. The ORCHESTRATED
  close needed the same treatment in the other direction: it annotates `Verification depth` and
  only then transitions, so a preview that skipped the annotation judged a state the real run
  never gates on, and refused what it accepts. `transition` gains a dry-run-only `pending_fields`,
  applied to the in-memory text so the gates see what the real run will see; it is ignored unless
  `dry_run`, so it can never introduce a write of its own.
- **`sprint preflight` reports every unmet close prerequisite in one read-only pass (CR0359).**
  The close is a chain that stops at its first failure, and the sign-off prerequisites are not
  part of the gate block at all - they surface only once the whole chain has passed. So a close
  took as many invocations as it had unmet prerequisites, each paying a full gate run, and it read
  as the tool moving the goalposts. Every fact was available before the first attempt. The new
  command reports the gate lanes, the retro's missing sections, an unjudged goal and the per-unit
  sign-off prerequisites (critic verdict, adversarial evidence, independent reviewer-of-record)
  together. It is read-only by construction - it scaffolds no retro, regenerates no summary and
  records no verdict - which is also why it cannot just run the chain with a dry-run flag: three
  of the chain's steps exist to DO something, and a preview that performed half a close would be
  a worse answer than none. `close` runs it and prints the same list up front, as a REPORT: the
  chain still decides what stops the close, so nothing that succeeded before now fails. The
  sign-off rules are asked of `critic` itself rather than restated, and the Done transition is
  previewed through `artifact.close(..., dry_run=True)` rather than described, so the pre-flight
  and the close cannot disagree about the same unit. Batch ids are resolved through the same
  `_batch_story_units` the sign-off uses, so an id with no artefact behind it is not reported as
  owed work. The report sits ABOVE the close's own early refusals: placed after them, an unjudged
  goal returned before it ran and hid everything else, which is the serial discovery it exists to
  end, reintroduced by its own placement.
- **The pre-commit gate runs cheapest-first and short-circuits (US0268).** The markdown lanes now
  run before the unit suites, and the suites are skipped entirely once a cheaper lane has failed -
  the commit is blocked either way, so paying ~132s of tests to be told about a blank line was
  pure waste. Reordering alone would have changed nothing: `run()` records a failure and returns
  0, so every lane ran regardless; the expensive block needed its own guard. Measured end to end,
  a commit whose only defect is markdown now reports in 35s. The skip is named, like the docs-only
  one beside it, because a guard that quietly does not run reads exactly like one that passed.
  `tools/tests/test_precommit_lane_order.py` pins the order, the short-circuit, its named skip,
  and that no lane was lost or duplicated in the reorder. The suite's leaked-line baseline drops
  233 to 134, by capturing leaks rather than raising the number.
- **`sprint plan` briefs the gates each unit will meet (US0266).** The plan now names, per unit,
  the close requirements still unmet, and lists the checks every commit meets. Both halves are
  generated - the first by running the real transition gates, the second from `gate.DEFAULT_CHECKS`
  - so neither can drift from what it describes. Scoped to the batch: only the types present and
  only requirements actually unmet, because an irrelevant checklist is how a relevant one stops
  being read. Repo-local guards (house style, commit-message trailers) are deliberately not
  enumerated, since the skill cannot know a consuming project's own hook.
- **`transition requirements` - ask what a transition needs before doing the work (US0267).**
  Reports the unmet requirements standing between a unit and a target status, and writes nothing.
  Derived, never restated: it runs the real gate ladder and reports what that refuses, so there is
  no second copy of a requirement to drift from the guard enforcing it. A hand-maintained list
  would be the very failure this removes, reintroduced one layer up - a test proves the derivation
  by changing the gate's wording and watching the reported text change with it.
- **Second-round review polish (RUN-01KXWWM3).** The repair round was APPROVEd with five MINOR
  findings; four are fixed here and one is filed. `refine._ac_heading`'s punctuation strip was
  unpinned by the whole suite - every existing test used a LONG criterion, where truncation removes
  the punctuation as a side effect, so reverting the strip stayed green while producing exactly the
  MD026 headings it exists to prevent; a short-criterion test now pins it. `close_owed` made two
  full-tree `find_by_id` scans per epic where one does. A failure while restoring `ended_at` printed
  "outcome not stamped goal-reached" when the outcome HAD been stamped, so the two steps now report
  separately. And `_ac_heading` is a behaviour change rather than the pure refactor it was presented
  as - stripping before the length test keeps a last word that truncation used to drop - now stated
  at the call site. **BG0211** files the remaining one: the strict union means an epic whose
  breakdown declares a dead or non-delivery id is owed a close no close can give, latent today (zero
  such epics) and in the over-reporting direction.

- **Repairs from the closing review of RUN-01KXWWM3.** One MAJOR and six MINOR, none a
  misbehaviour of the shipped code and every one a claim wider than its evidence. The MAJOR: the
  `type_ != "epic"` guard - the single check keeping the close-owed relaxation from becoming a
  blanket exemption - was unpinned by the **entire** suite, while the commit claimed all four
  branches were mutation-killed by their own tests; it now has a test that fails when the guard is
  removed. Coverage and derivation also disagreed about what a child is (`children_of` versus the
  declared Story Breakdown), so an epic could be forgiven off a strict subset of the children its
  own closure derived from; the breakdown parser moves to `reconcile.declared_breakdown_ids` as the
  single answer and both id sets must now be covered. `refine._ac_heading` kept a private copy of
  the heading-strip rule while `sdlc_md.heading_title` claimed to be the one definition, so it now
  routes through it. The epic-criteria fallback for a body with no `## Revision History` emitted two
  consecutive blank lines (MD012) - a generator writing markdown that blocks the commit carrying it,
  the same defect fixed elsewhere this sprint. Promoting a run's outcome re-stamped `ended_at`,
  stretching the archived elapsed span that `retro` reads, so the original end time is put back. And
  the outcome promotion was reachable only from `--apply-signoff`: `_close_handoff` short-circuits
  when a handoff already exists, and that skip covered the outcome as well as the artefact, which is
  exactly how the cited run kept `stopped`; a plain `sprint close` now corrects it too.

- **Close-owed can reach zero again: a derived epic inherits its children's coverage (BG0210).** An
  epic does not reach terminal by being worked - `apply-signoff` derives it once every child is
  terminal, in the close tail, after the retro is written - so no epic is ever named in a retro's
  `Batch`. The detector required a unit to be named there, so every clean close manufactured
  close-owed debt for the epics it had just derived, and no further close could clear it because
  each close derives its own. About 38 epics were in that state, most of the reported total, so the
  headline number was largely false; a detector reporting a permanent, growing, unclearable debt is
  one people learn to skim past, which is the failure it exists to prevent. An epic is now accounted
  for when the retro accounted for the children whose closure derived it. Recording the epics in the
  `Batch` instead was the obvious alternative and is wrong: `retro accuracy` sums points across the
  batch and an epic's Derived Point Total is the sum of its stories, so it would double-count every
  sprint's velocity. Not a blanket exemption - a childless epic inherits nothing and an epic with one
  unaccounted child stays owed, both mutation-pinned. On this repo the rule forgives **35** epics,
  and every survivor is genuinely uncovered. (An earlier draft of this entry quoted "44 to 12" and
  "about 38 epics": those compared readings taken from two different trees, so the delta was
  inflated by the units this sprint itself closed. Measured on one tree the count is 48 to 13.)

- **A completed close records the outcome its verdict earned (BG0208).** The run-state `outcome`
  field was written on every failure path - blocked, budget spent, an operator stop - and forgotten
  on the success path, so a run that stopped earlier and then completed its entire close chain with
  a verdict of `achieved` kept `outcome: stopped`. Run state is archived per cycle, so that is the
  permanent record, and every consumer of the archive (`sprint report`, velocity, boundary
  regeneration, the close-owed detector) then read a goal-reached sprint as an abandoned one. A
  close that completes with an `achieved` verdict now stamps `goal-reached`. Only that verdict
  promotes: following the fact that a close RAN rather than what it judged would make every close
  report success, which is the same defect inverted. `partial` and `missed` leave the recorded
  outcome alone, because the vocabulary has no term for "closed cleanly, goal not met" and inventing
  a fifth is a schema change rather than a bug fix. Both directions are mutation-pinned.

- **One definition of a generated H1, so the MD026 fix stops being re-made per generator
  (BG0204).** `sprint close` with no `--retro` scaffolds the batch retro and titles it from the
  run's Sprint Goal. A goal is a sentence and ends in a full stop, so the H1 did too, and
  markdownlint MD026 then blocked the very commit carrying the retro - hit at a real close, where
  the heading had to be corrected by hand before the paperwork could land. This is the same defect
  fixed once in the handoff H1 and once in the seeded AC headings, each generator fixing its own
  copy while the others stayed broken. The rule now lives once, as `sdlc_md.heading_title`, beside
  the other shared writers; `handoff` delegates to it and the retro scaffold calls it. Proven shared
  rather than merely moved: removing the strip from the helper reddens tests in **both** callers.

- **`refine` no longer gives one story its siblings' acceptance criteria (BG0205).** Decomposing a
  request seeded the FIRST minted story with the request's entire criteria list and left every
  sibling a bare `{{define}}` scaffold, under a note saying to redistribute them while grooming. The
  note documented the behaviour without its cost: the wrong criteria read as authored, so a groomer
  who trusts them writes tests for the wrong story, while the sibling that lost its criteria looks
  merely empty rather than mis-seeded. Two grooming agents hit it in one batch and both
  redistributed by hand. A multi-story breakdown cannot know which criterion belongs to which story,
  so it no longer guesses: every story keeps its scaffold, and the request's criteria are carried to
  the **epic** as an `Acceptance Criteria (Epic Level)` section, which is where a whole request's
  completion bar belongs. A single-story breakdown is unchanged - that story IS the request, so it
  still takes the criteria. The `redistribute_note` flag is gone with the behaviour, because a note
  excusing wrong criteria is not a substitute for not writing them. Reproduced and re-verified in a
  clean workspace outside this repo: four criteria decomposed into three stories previously put all
  four on story one, and now put none on any story and all four on the epic.

- **Repairs from the closing adversarial review of RUN-01KXVYGR.** Two MAJOR and four MINOR
  findings, every one a false negative in something this sprint shipped, and each contradicted by
  prose written to justify it. `reconcile.apply_linked_epics` split table rows on every pipe, so an
  escaped `\|` in a cell shifted the columns and it wrote the epic id over the **Date** cell,
  destroying it, while leaving the real cell untouched so the row re-drifted next run; rows are now
  split on unescaped pipes only. The green-run noise detector excluded any indented line and any
  capitalised one, so `print("  " + msg)` disarmed it - two real leaks in this repo's own suite were
  invisible for that reason alone, and the recorded baseline of 68 was a measurement of the blind
  detector rather than of the suite. The true count is **233**, and the exclusion list now matches on
  shape rather than on a word. The RFC accept gate hardcoded a three-column row, one heading level
  and the single leading word `Open`, passing four real shapes; widening it immediately surfaced two
  further Accepted RFCs whose decision tables are six and five columns wide - nine of their ten open
  rows are now closed against the file's own Decision section, and the tenth is recorded as an
  override naming CR0346 rather than invented. `run_state.archived` raised from its sort key on a
  malformed cycle index, losing every intact record, which is exactly what its docstring promised not
  to do. Two branches that survived removal against the whole suite - the boundary's
  outcome-preservation guard and `close_run`'s archive call - now have discriminating tests.

- **The RFC accept gate's fail-closed path actually fails closed now (round 4 of the closing
  review).** The fallback added in round 3 re-scanned the document with fence skipping disabled but
  kept the section rule, so a `#` comment inside the unterminated fence ended the decisions section
  and hid every row after it. That is round 1's bypass copied verbatim into the path written to
  prevent it: the code carried a comment promising a false negative was impossible while returning
  "no open decisions" for the exact document it exists to catch, and an RFC with an Open decision
  reached Accepted. The two structural signals fail together - an unterminated fence means the
  document's shape cannot be trusted, and a `#` line inside it is as likely a shell comment as a
  heading - so the fallback now drops the section rule as well, reporting every unsettled row
  anywhere in the file. That trades a rare false positive for the impossibility of a false
  negative, and the cost is paid on VALID documents rather than only broken ones: CommonMark
  closes an open fence at end of document, so a file whose last block is an unclosed appendix
  fence is well-formed markdown that every parser accepts. An operator meeting the false positive
  records a `Decision-Override`. Separately, the CommonMark `(char, length)`
  matcher that was round 3's headline fix had **no discriminating test**: every fence test asserted
  the gate blocks, and the fallback blocks by itself, so reverting the matcher to a naive toggle
  left all 107 tests green. It is now pinned by the one case the fallback cannot satisfy - a
  well-formed nested fence holding an example row, where the correct answer is to pass. Verified on
  all 47 shipped RFCs: no verdict changes.

- **A rolling multi-sprint policy: fix the policy once, regenerate the plan at every boundary
  (EP0076).** An operator wanting an unattended evening of delivery had to return at every sprint
  boundary to re-plan, and queueing several plans up front does not work - the backlog is generated
  by the work, so a frozen queue rots while it waits. `sprint plan --write --cycles N --sprint-goal
  "..."` now records a **standing policy** (cycle count, goal, capacity, order rule, stop
  conditions) on the run state and refuses an incomplete one rather than defaulting it: fewer than
  one cycle, no sprint goal, or combined with `--worklist`/`--prd` is an exit-2 refusal that writes
  no policy at all. `sprint boundary --retro RETROxxxx` then crosses one boundary as four ordered
  gates - the cycle's full close chain (reported against the cycle it closed), a fetch and
  origin-drift comparison at **every** boundary rather than only the first plan, a regeneration of
  the batch from the live backlog under the policy (so a bug the last cycle raised is eligible and
  a story it finished has dropped out, and the lessons its close just wrote are in the next plan's
  digest), and a dry-run preview of batch, order, forecast and capacity before anything executes.
  Three causes stop the run through **one shared stop path** - a close-down that does not complete,
  divergence from origin under `--strict`, and a regenerated batch the breakdown gate refuses - each
  writing a handoff that names the cause and the cycles left unrun, recording the stop on the run
  state, and executing no unit of the next cycle's batch. Each cycle mints its own `run_id`,
  forecast, sprint goal, verdict and retro, and **run state is now archived per run** to
  `sdlc-studio/.local/run-archive/<run_id>.json` before the next cycle overwrites the live file, so
  an N-cycle run reads back as N auditable sprints instead of one blurred session. The live
  run-state file keeps its existing shape, so every module that reads it is unaffected. The whole
  feature is opt-in: without `--cycles` a sprint behaves exactly as before.

- **The command surface is grouped by the process spine, and the two catalogues agree (EP0081).**
  `help/help.md` no longer lists commands in the order features were added; the "All Commands"
  catalogue now carries one section per stage - Raise, Break Down, Sprint and Review, Levers,
  Support, Utility - with the document levers reached before the support and utility tooling. Which
  section a command sits in is no longer editorial: `test_help_structure.py` binds every catalogued
  entry to `command_audit.SPINE`, so a command placed under the wrong heading, listed twice, or
  dropped from the page fails a test rather than being found by a reader. Four working commands
  that lived in the help catalogue but not the SKILL Type Reference - `lessons`, `retro`, `review`
  and `repo` - are promoted into it; that absence was the drift, and it fails `doc_coverage`
  repo-wide for every unit while it lasts. `upgrade` is folded behind `migrate` instead, since
  `reference-upgrade.md` names `migrate` the front door that orchestrates it: it leaves both
  catalogues but keeps its help page and gains a redirect, so an operator following an old habit
  lands on the replacement rather than a dead route. `command_audit.py` learns to read those
  redirects - a signpost is not a catalogue entry, so folding is distinguishable from leaving a
  command in place - and reports the folded set. The checked-in `command-audit.md` is regenerated:
  39 commands, 0 unmapped, 0 drift, 0 broken tools.

  `sprint report --id RETROxxxx [--tokens N] [--elapsed-hours H] [--format json]` routes to the
  report composer, threading every flag and returning its exit code unchanged, so the end-of-sprint
  page no longer needs an operator who already knows `sprint_report.py` exists. `sprint close` now
  draws the same page immediately before the sign-off decision brief, so what the sprint delivered
  and cost sits on the page the reviewer of record judges. The report step is read-only and
  advisory: it cannot fail a close, an uncomposable report is noted rather than fatal, and a
  resumed close redraws it without writing anything. `report.enabled: false` gates only the
  drawing - the chain, the brief and the exit code are unchanged. That switch is now stated
  consistently as a page-versus-data gate in `rendering_enabled`, the `cmd_show` gate, the notice
  it prints and the scripts catalogue: the text page is withheld, json data remains available via
  `--format json`, and measurement is never gated. The json path is covered by tests against a
  disabled config rather than left to a reader of the source.

- **The audit estimate learns from what audits actually cost, and the capped tail is carried
  rather than counted (EP0073).** `audit_cost.py` gains a `record` subcommand that appends a
  finished run - its scope, the estimate it was given, and its measured agents, tokens and wall
  minutes - to a committed evidence ledger under `sdlc-studio/retros/evidence/`, sharded by UTC
  day so two people recording on different days merge cleanly. Once the ledger holds a usable
  run, `run` derives candidates-per-lens and tokens-per-agent from the MEDIAN of those runs
  instead of the constants frozen at one 2026-07-15 reference run, and the output names which of
  the two bases it used, so an assumption is never read as a measurement. Candidates per lens is
  not recorded directly - it is recovered by inverting the estimator's own agent model, and a row
  that does not invert is dropped whole rather than half-used, so both medians rest on the same
  runs. The pre-existing `audit_cost.py --lenses <n>` invocation keeps working unchanged.
  Alongside it, `reference-audit.md` now requires the verification cap to write every dropped
  candidate out in full to `.local/audit-carryover-<date>.json` rather than log a count, the
  close-out report to name that file and the one scoped `audit --carryover` command that verifies
  just those candidates, and the finder harness to take a carry-over file as its candidate pool
  and run no finder lenses at all. A measured run dropped 42 of 122 grounded candidates into a
  session-local journal that died with the session; the tail is now carried work with a route
  back in.

- **One weakness-hunt, one name: `review generate` folds into `audit --profile repo` (EP0078).**
  Two commands hunted for the same weaknesses under different names, and only one of them put its
  findings through the refute panel. The three legs of the repository on-ramp - architecture,
  code-quality, defensive-security - now ship as a declarative lens pack at
  `templates/audit-profiles/repo.md`, panel-wired like every other profile, and the binding
  remediation-only security posture moved into the pack verbatim rather than living as a constant
  in a script. A `code` pack ships alongside it (correctness, security-smells, pattern-violations,
  ac-drift), completing the four profiles the audit was promised. `audit.py profile --name <name>`
  resolves a pack and reports its lenses and refute threshold; a name no profile declares is
  refused non-zero naming the ones that exist, so a mistyped profile cannot run an empty lens set.
  `scripts/review_generate.py`, its suite and its prompt template are deleted with no alias left
  behind, and the README, docs, SKILL description and help pages all point at the replacement -
  `review` now means the PRD/TRD/TSD consistency pass and nothing else.

- **The green-run noise gate actually runs, and its detector matches what leaks (US0253).**
  `tools/skill-tests.sh` held the noise leg but was wired into nothing - neither CI nor `npm test`
  invoked it - while the TSD described it as holding the line. Its detector matched one shape,
  `ERROR` or `WARN` followed by an absolute path, and caught 0 of the 68 lines this suite actually
  leaks: lowercase `error:`, `warning:`, `usage:`, and tool-prefixed messages. Detection moves to
  `tools/test_noise.py` so it is unit-tested against the real shapes, judged after unittest's
  progress dots are stripped because an escaped print usually shares a line with them. The skill
  suite is now invoked THROUGH the gate (`npm run test:skill`, the pre-commit hook, and a named CI
  step), so no path around it skips the check. The 68 lines are a recorded baseline that fails on
  an increase, not an amnesty: demanding zero before the leg could run is why it ran nowhere.

- **`gate --release` binds the strict version check as one exit code (US0254).** Version
  consistency and the release gate were two commands, so a tag could be cut from a green gate while
  `check_versions --strict` had never run, or had run and had its exit code dropped. A blocking
  `versions` lane now joins the pre-tag gate; `--strict` is the flag that adds the CHANGELOG
  comparison, so a mismatch there fails the cut. It is invoked as a subprocess rather than imported
  because `check_versions.py` is a repo-only development tool while the gate ships to consuming
  projects - one without it reports the lane N/A rather than failing on a tool it never had, and
  never silently passes.

- **The request index's Linked Epics column is censused from the files (US0256).** The column
  shipped as a placeholder and stayed one: every CR in this workspace that had been decomposed -
  63 of 63 - still showed `--` while its file named real epics. A column nothing derives is a
  column nobody can trust. `reconcile detect` now reports the disagreement and `apply` writes the
  cell from each request's `Decomposed-into`, locating the column by header rather than position
  so an older index cannot have its Type or Date rewritten. `refine` writes the cell where the
  link is made, so the drift does not simply reaccumulate between reconciles. A request that was
  never decomposed has no epic to name, so its placeholder is honest and is not flagged.

- **Artefact-body reads in the tree-walking scanners route through `read_text_safe` (US0252).**
  Eleven bare reads across `verify_ac.py`, `status.py` and `deploy.py` would abort a whole scan on
  one non-UTF-8 artefact from a crashed session. Index reads stay bare and loud, because a corrupt
  index is a real error rather than one bad row. Two JSON reads stay bare behind an inline
  `bare-read-ok` marker stating the reason, and the census refuses an exemption that gives none.
  Reading a story body safely would have turned a corrupt story into a clean `ac=0 pass=0` exit 0,
  so the body reader also names the unreadable file on stderr: a vacuous pass is worse than the
  crash it replaces.

- **The write-confinement suite covers a roster of shipped writers, not a hand-picked few
  (US0255).** Eleven writers now carry a snapshot asserting both that nothing outside their
  declared targets changed AND that the declared target was actually written, so inaction cannot
  read as confinement. An AST detector reads the write surface of every script - most writers go
  through the shared `atomic_write` helper rather than `write_text`, which a grep-based sweep would
  miss - and every detected writer must be cased or allowlisted with a stated reason. Thirty-two
  are currently allowlisted: that list is the remaining debt, not a claim of coverage.

- **The finding filer writes a decision row that says something (US0245).** Every RFC filed by
  `file_finding.py` carried one fixed sentence - `Act on this finding or keep status quo` - while
  the finding's real options sat two lines above it under Design Options. A row that poses no
  question gets closed by nobody, which is how accepted RFCs accumulated an unanswered decision
  each; RFC0010 condemned the row in June and the changes cited as fixing it never touched the
  generator. D1 is now written from the options: two or more become the choice between them, one
  becomes whether to take it, and a finding with none poses its own subject. The boilerplate string
  is gone, so the accept gate no longer has to catch rot the filer manufactures.

- **The accepted-RFC tranche now records what actually shipped (US0246).** Eight RFCs sat in
  Accepted carrying an unanswered decision row, most of them the generated boilerplate `Act on this
  finding or keep status quo`. Each row is closed against the code that came out of it, naming the
  concrete mechanism and the delivering epic or CR, with a revision-history row recording the
  closure. The count is the one the new check measures, not the one the parent request listed: that
  enumerated five and the workspace holds eight. The story's own criterion is a census over every
  Accepted RFC rather than a list of the eight, because a listed check silently exempts whatever is
  added next - which is exactly how the request came to be three short.

- **An RFC cannot reach Accepted while a decision row is still Open (US0244).** `reference-rfc.md`'s
  accept step has always forbidden it, but only in prose, and a rule with no mechanism fires when
  somebody remembers: eight RFCs are Accepted, decomposed and delivered while carrying an Open
  decision. `transition.py` now refuses the transition, naming each Open row. The sanctioned escape
  is a recorded `> **Decision-Override:** <reason>` rather than `--force`, matching the plan-review
  convention - a skip that leaves its reason in the file is auditable afterwards, a flag is not.
  `validate.py` carries the same check as a standing rule, because a gate on the transition alone
  leaves every file that predates it untouched while still reporting the workspace clean; an
  Accepted RFC with an Open row is an error, or a warning when an override is recorded. The status
  cell is read as free text and judged on its leading token, so `Open - the mechanism detail for
  the blocking lane` still counts as Open: a reader demanding the bare word missed a real row and
  called the file clean, which is worse than the prose rule it replaces because it also looks like
  proof.

- **A sprint-level adversarial review satisfies the per-unit `critiqued` gate for the units in its
  range (EP0080, US0247, RFC0046 option B).** The closing full-diff pass judges the whole sprint
  diff at once, so `critic sprint-review --units ... --reviewer <seat> --author <id> --verdict
  APPROVE --findings ...` records one independent verdict covering a batch. Conformance's `critiqued`
  stage then reads it as coverage for a covered unit that has no individual verdict - both the
  verdict half and the two-role evidence half - so the close no longer demands a redundant per-unit
  evidence row for every unit the one pass reviewed. It never overrides a per-unit REJECT (which
  still repairs per unit), the per-unit reviewer-of-record sign-off is still required, and a
  self-review (reviewer == author) or an empty pass is refused. `--apply-signoff` resolves a covered
  unit's author from the sprint-level review when it has no per-unit verdict, and the sign-off
  principal must differ from the sprint-level reviewer too (two-role separation at sprint scope). The
  close sign-off brief reads a
  covered unit as reviewed by that pass rather than reporting it "(no critic verdict recorded)"
  (US0248), and `reference-sprint.md` documents the coverage model.
- **`sprint close --apply-signoff --principal "<you>"` fans a recorded approval into the close
  (EP0077, US0236).** Instead of hand-running `critic signoff` and `transition` for every unit, one
  command records your reviewer-of-record sign-off per story unit and transitions each Done (AC-verify
  gated, cascading its parent). Story-scoped (bugs are already terminal), and it stops loudly at the
  first refusal - an authoring-session subagent principal, or a unit whose Done gate is red - leaving
  completed units done. It refuses without an explicit `--principal`. After the per-unit fan it runs a
  close tail (US0237): the run's velocity row is written to `VELOCITY.md` (via `retro accuracy --write`,
  keyed by retro id so a re-run upserts) and a final reconcile asserts drift 0 - so a closed sprint no
  longer needs a forgotten manual velocity step. The whole flow is idempotent (US0238): a re-run after a
  mid-cascade stop resumes, skipping already-done+signed units, with no duplicate velocity row or double
  telemetry.
- **`sprint close` scaffolds the retro through the deterministic path (CR0345).** `--retro`
  is now optional: run `sprint close` with no retro and it scaffolds one via `artifact.py new
  --type retro` (allocated id + template + index row, Batch/Goal pre-filled from run-state),
  then stops so you fill it and re-run with the id it prints. A `--retro` naming an existing
  retro proceeds as before and self-heals a missing index row (`reconcile.apply_meta`), so a
  retro made any other way never stalls the close at the reconcile step; a `--retro` naming a
  non-existent retro is refused (the sequential allocator cannot mint a chosen id). This makes
  the deterministic scaffold the default path and removes the hand-authored-retro-missing-row
  friction.
- **`reference-schema.md`: the artefact format is now a versioned public contract (EP0084,
  RFC0047).** A single self-describing reference documents the six on-disk surfaces external
  tooling reads - id grammar, directory layout, per-type header fields, status vocabulary and
  transition gates, the Verify-line DSL, and the derived index format - so a consumer parses the
  `sdlc-studio/` tree against a promised contract instead of vendoring field knowledge. It names
  `validate.py` as the executable definition, states that health judgements stay upstream and
  that `_index.md` is derived output, and marks `.local/` runtime JSON explicitly uncontracted
  (US0258). The `schema_version` config key is the contract stamp a consumer pins (defaulted in
  `config-defaults.yaml`, documented in `reference-config.md`), with a compatibility policy -
  additive changes bump the minor version, renames/removals bump the major with a `migrate` path
  (US0259). A drift guard (`scripts/tests/test_schema_contract.py`) fails the suite when the
  documented status vocabulary or the version stamp diverges from what the code enforces, so the
  published contract cannot rot silently (US0260).
- **`refine apply --into EPxxxx`: share a batch epic instead of minting singletons (CR0322,
  RFC0045).** A small request can decompose its stories INTO an existing open epic - a shared themed
  container - rather than accreting a one-story epic each. The joining request's `Decomposed-into:`
  points at that epic, the epic carries one `Parent:` line per request it delivers so the link
  resolves both ways for each, and its `Derived Point Total` rolls up; a terminal, non-epic, or
  unknown `--into` target is refused with nothing minted. `--epic-title` and `--into` are mutually
  exclusive. The link core (`children_of`, the link-asymmetry gate) now resolves multiple parents,
  so a batch epic delivering several requests satisfies the two-backlog symmetry and derivation
  gates unchanged. Every refined story records its originating request in a `> **Delivers:**
  <request>` field, so in a shared batch epic (whose stories deliver different requests) the
  request-to-story mapping is machine-resolvable, not only in the title; the story's `Parent:`
  stays the epic, so derivation is untouched.
- **Deterministic flow metrics - the zero-token schedule instrument (CR0310, EP0052).** New
  `scripts/flow.py compute` reports per-unit cycle time (Created -> delivered, resolved from git
  history anchored on the status header line, with a revision-row fallback), weekly throughput
  (delivered statuses only - a Superseded unit is closed, not delivered), and work-item age for
  every non-terminal unit. A unit whose dates cannot be resolved is NAMED unmeasurable, never
  guessed. Advisory only, feeds no gate; the cost instrument (points x measured rate) is a
  separate axis.
- **The Sprint Goal - a product outcome on the plan, judged at the close (CR0311, EP0053).**
  `sprint plan --sprint-goal "..."` records one unifying product-outcome sentence on the plan and
  run state (prompted when interactive; absent is recorded as none, never invented). The closing
  review judges the increment against it via `sprint goal-verdict --verdict
  achieved|partial|missed --note "..."` (refused when no goal was set), and the sprint report
  displays the goal and verdict beside delivered points and cost - guarded by the same
  batch-must-name-this-sprint's-units rule as the elapsed read, so a stale run state says nothing.
- **DORA four keys, deterministically (CR0312, EP0054).** `deploy.py metrics` computes
  deployment frequency and change failure rate from the deploy ledger, lead time for changes
  from git author times between deploy events (the git read lives in `flow.py` - deploy keeps
  its never-shells-out safety contract), and MTTR from High/Critical bug dates. Advisory, with
  each definition printed; an absent source is UNMEASURABLE by name; a workspace with no ledger
  reads not-applicable and is never nagged.
- **The small-batch guard - an advisory diff-size gate lane (CR0313, EP0055).** With
  `batch_size.max_lines` / `batch_size.max_files` configured, the `batch-size` lane measures each
  open-run batch unit's delivered diff (via its Refs-trailed / subject-named commits) and WARNS -
  never blocks - on an outlier, naming the unit, points, measured size and thresholds. The AI
  batch-size failure mode (DORA 2024/25: agents amplify batch size; undisciplined growth degrades
  throughput and stability) made visible at review time. Off by default.
- **Blocked-age and ageing flags (CR0310 slice 2, EP0052).** `flow compute` reports a Blocked
  unit's blocked-age distinctly from its total age (unresolvable transitions named, never
  guessed), and `status` gains an opt-in ageing advisory: with `flow.ageing_days` set, each
  In Progress unit older than the threshold and every stuck Blocked unit is named inline.
  Absent config = silent (a flag appearing uninvited on a live workflow is a break).
- **Monte Carlo completion forecasting - the probabilistic schedule read (CR0310 finale,
  EP0052).** `flow.py forecast --units N` samples measured weekly throughput (zero-delivery
  weeks included - dropping them is silent optimism) in a seeded, reproducible simulation and
  reports 50/85/95% confidence completion dates. Refuses under four weeks of history or an
  all-zero window, naming the sample size - never a guessed date. The sprint report now shows
  the flow axis (median cycle, throughput) beside cost, and
  `reference-sprint.md#schedule-and-cost` fixes the vocabulary: points = cost, flow = schedule,
  velocity descriptive, nothing feeds a gate.
- **The sprint report: what a sprint delivered, cost, and velocity (EP0048, RFC0035, absorbing
  CR0273).** New `sprint_report.py show --id RETROxxxx` composes - deterministically, at no model-token
  cost - the delivered points, the actual spend, the estimate-vs-actual, the velocity, the lessons and
  the tickets raised. Supporting changes to the estimator core, all additive and honesty-guarded:
  - **Per-attempt telemetry** - a record can carry an `attempts` list of `{model, tokens}`, so an
    escalation (cheap model rejected, re-run on a dearer one) is visible and priceable. Non-destructive:
    a legacy record reads as one implicit attempt (`attempts_of`), so the existing evidence needs no
    migration.
  - **True cost with rework** - `telemetry.unit_cost` sums cost over every attempt, priced OFFLINE from
    a `pricing.<model>` config table (rough estimate defaults, editable per project). An unpriced model
    is UNPRICED - its tokens counted, its dollars never guessed. No avoided-cost / savings headline (a
    counterfactual is a model, not a measurement).
  - **Points-per-elapsed-sprint velocity** (from CR0273) - the PRIMARY planning read (ceremony
    included, from the run-state's own batch); a SECONDARY points-per-worker-hour for tuning. Both
    DESCRIPTIVE, fed to no gate, and honest: a stale run-state from a different run is ignored (it must
    name this sprint's units), and an interactive sprint reads UNMEASURED unless `--elapsed-hours` is
    supplied.
  - **Rendering gated by `report.enabled`; recording never gated** - a token-conscious project can turn
    the report page off, but telemetry keeps recording (a report can be drawn later; a measurement not
    taken is gone). Also hardened: `sdlc_md.iter_artifact_files` and one more artefact-body read now
    tolerate a non-UTF-8 file. RFC0035 Accepted (children Done); it ABSORBS CR0273 (Superseded).

- **Backlog triage as a ceremony inside `plan` (EP0047, RFC0037, absorbing CR0264).** Breakdown asks
  whether a UNIT is plannable; triage asks whether the BACKLOG is worth planning FROM. New
  `backlog_triage.py` runs deterministic lenses - DUPLICATE/SUBSUMED (open artefacts with overlapping
  `Affects` and similar wording), OVERSIZED (a delivery unit above the 8-point ceiling - blocks,
  decompose it), STALE (open, untouched for months, nothing depends on it), ORPHANED DEPENDENCY (a
  `Depends on:` naming a terminal or absent artefact). The judgement lenses are surfaced in the plan
  the operator already reads (reporting-only) and as a `status`/`hint` advisory; the mechanical
  oversized lens blocks. `file_finding` runs the cheapest lens at FILING - a new finding overlapping
  an open artefact is warned with the candidate named, before the id is minted (never a refusal),
  the same overlap primitives so the filing-time and plan-time lenses agree. One day of dogfooding
  had produced three duplicate pairs in a backlog of eleven, all caught by a human rather than tooling.

- **The sprint close-down is now mechanically detectable and enforceable (EP0046, RFC0042).** The
  close (retro + lessons + close gate) was mandated but only ran when someone invoked
  `--require-retro` - a silent control that lapsed under pressure and stopped the lessons
  compounding. New `close_owed.py` answers "is a close owed right now?" deterministically: a
  delivery unit that reached terminal since a one-time grandfather baseline
  (`.close-owed-baseline.json`) with no retro's `Batch` accounting for it. It surfaces three ways -
  a soft `advisory:` line on `status`/`hint`, a blocking `gate --require-close` lane for the
  push/release moment (bound like the other close lanes, never in the plain gate), and an optional
  `hooks/close_guard.py` Stop hook that reminds the agent of an owed close before a turn ends
  (default-allow on any doubt, never a hard-lock). A sprint is complete only when the close gate is
  green and shown, never at "deployed". The historical tail is grandfathered at adoption, never
  enforced retroactively.

- **`reconcile apply` creates a missing index from its template (EP0043, CR0277).** A
  `missing-index` drift used to be detect-only - an operator had to hand-author the index. Now
  `reconcile apply` materialises a missing pipeline or meta index (reviews/retros) from
  `templates/indexes/<type>.md` via `write_empty_index` and appends the census rows; dry-run reports
  would-create. Surfaced dogfooding the homelab audit.

- **An audit cost estimate + pre-flight gate (EP0044, CR0276).** New `audit_cost.py` estimates a
  run's agents/tokens/wall-time from the lens count and flags it large or small (calibrated to the
  measured reference run: 7 lenses -> ~190 agents / ~6.8M tokens). `reference-audit.md` documents a
  pre-flight gate: present the estimate and confirm above a threshold before the fan-out, so a
  multi-million-token adversarial run is not sprung on the operator; a small scoped audit runs
  without ceremony.

- **Interactive sprints get a real tokens-per-point (EP0045, CR0278).** The retro doctrine treated an
  interactive sprint's tokens as UNMEASURED, conflating "the runner telemetry did not capture it"
  with "unmeasurable". The harness tracks the token count deterministically. `retro.py accuracy --id
  RETRO --tokens N` now records the harness-tracked sprint total and computes a real tokens-per-point
  over the delivered (terminal) units' Points. The template, `retro.py` and `reference-retro` reword
  "UNMEASURED (interactive)" to "not-yet-captured"; the descriptive-never-a-target guard is kept.

- **Fixed: old-flow CRs no longer false-flagged as un-refined (BG0151).** `children_of` read only the
  two-backlog `Parent:`/`Epic:` links, so a CR decomposed the legacy `cr action` way (its epics carry
  `> **Change Request:** CR-XXXX`, not `Parent:`) looked childless - making `status`/`hint`
  `discovery_awaiting` and `migrate` report already-decomposed CRs as awaiting refinement. False
  positives on every old-flow project. `child_parent` now recognises the legacy `Change Request:`
  epic->CR link. Found dogfooding ../homelab (24 false "awaiting" -> 16, 12 false migrate -> 4).

- **`migrate` - one command that reviews every artefact and upgrades where safe (EP0042, RFC0041).**
  An operator upgrading a consuming project had to know to run `project upgrade`, `migrate_v3
  sizing`, and `reconcile` separately, and even then no pass reviewed the open RFCs/CRs/epics/stories.
  `migrate` is the orchestrator (RFC0041 option C): it runs those pieces in order, adds an
  artefact-review sweep, and emits ONE report split into **deterministic** (what it auto-applied -
  version stamp, config, a container's Effort/Points -> `Size` conversion) and **needs a human**
  (each item with the exact command - an accepted childless request -> `refine`, a childless Issue
  -> `triage`, a delivery unit sized in legacy Effort -> a re-size). It auto-applies only the
  deterministic, reversible set and never guesses a judgement (there is no honest Effort->Points
  map). Dry-run by default; `--apply` writes the safe set. Reuses the existing tools rather than
  duplicating them.

- **Fixed: `project upgrade` no longer stamps a bogus `skill_version: "unknown"` (BG0150).** When the
  installed skill's `SKILL.md` carried no parseable `version:` (a partial install), `apply()` fell
  back to `"unknown"` and wrote it into `sdlc-studio/.version` - which read as "the version is
  missing" and corrupted the metadata skill-update/migrate compare against. It now warns loudly and
  SKIPS the stamp instead of fabricating a value; the normal path is unchanged.

- **A command-surface audit and the two backlogs surfaced at `hint` and `status` (EP0041, CR0272
  slice 1).** New `command_audit.py` enumerates every command deterministically - the SKILL Type
  Reference, the `help/help.md` catalogue, and `scripts/` - and dispositions each **keep** or
  **review** from three structural signals: the process-spine category it serves, catalogue drift
  (a command in one place but not the other), and tooling health (`--check-tools` runs each backing
  script's `--help`). `--write` produces `sdlc-studio/reviews/command-audit.md` with a per-spine
  table and recommended actions - the evidence a later cleanup slice acts on (this run flagged 5
  help-only commands to promote/retire and confirmed all 61 tools run). And the dual-track is now
  visible from the first commands an operator reaches for: `hint` names how many Discovery items
  await refinement/triage, and the main `status` dashboard shows the Discovery/Delivery split (not
  only `status backlog`). CR0272's remaining scope (retiring/folding the flagged commands and
  rewriting the help around the spine) is a later slice this audit informs.

- **The Three Amigos are baked into refine and triage (EP0040, RFC0039).** The consult machinery
  (`resolve_consult`/`frame`) existed but was unwired - refine and triage only printed bare role
  strings. Now a `--question` resolves the panel to the actual **named seats** (the project's own
  seat cards, else the shipped defaults Dani Okafor / Lena Marsh / Sam Eriksson), frames each with
  its review render, and surfaces the questions to that panel - **engineering-led** for refine (a
  request is largely a build breakdown), **QA-led** for triage (is it reproducible? what is the real
  defect?). The consult is recorded on the request/Issue as an audit trail: a `> **Consulted:**`
  metadata line and an idempotent `## Amigo Consult` section listing the questions. `--skip-personas`
  forces the generic path (no seats, no framing, byte-equivalent), and a project seat card that
  claims a role but lacks its review render is a hard error caught **before** anything is minted (the
  ceremony fails empty, never half-decomposes). New shared library in `persona_resolve.py`
  (`consult`, `amigo_panel`, `seat_name`, `record_consult`) plus a `panel --ceremony refine|triage`
  CLI. The panel resolution and the independence floor (a seat never signs off its own work) are the
  same ones the author≠reviewer critic gate holds.

- **The discovery track gains a defect side: the `issue` type and the `triage` ceremony (EP0038,
  RFC0039).** An **Issue** is the raw defect report - a symptom in the Discovery backlog, not yet
  reproduced or scoped - carrying a Severity and a T-shirt Size but no points (it is not a delivery
  unit). `triage.py apply --issue <id> --bug "title|points[|severity[|affects]]" ...` decomposes it
  DIRECTLY into the bugs that deliver its fix (one level - a bug is already the delivery unit - the
  mirror of `refine` turning a request into an epic + stories), wiring each bug's `Parent:` and the
  Issue's `Decomposed-into:`; `triage show` surfaces the report and confirms it is triageable. The
  whole breakdown is validated up front, including a dry-run pre-flight of every bug through the
  grooming gate, so a bad bug fails loud and empty rather than leaving an earlier one half-minted. A
  triaged bug is minted as an individual bug (`artifact.new(..., consolidate=False)`), so on a
  schema-v3 project a Low-severity triaged bug is a bug, never folded into a finding-consolidation CR.
  The new `is_discovery(type_)` predicate (RFC/CR/Issue) is the one every backlog-side gate now
  consults: `plan` refuses an Issue (G1), `status backlog` buckets it under Discovery, `reconcile`
  flags an accepted childless Issue as `undecomposed` (needs triage), and an Issue reaches Resolved
  only by derivation from its bugs (G2). `is_request` stays the narrow RFC/CR set (`refine`'s
  domain), so a request is refined and an Issue is triaged - never conflated. An Issue that is
  really a change is filed as a CR and refined, not smuggled in as a story. New help: `help/issue.md`,
  `help/triage.md`. The `Parent:`/`Decomposed-into:` link writers moved to `lib.sdlc_md` (shared by
  both ceremonies) before triage became the second caller.

- **`refine show` works on an already-decomposed request, to inform a `refine add` (CR0275).** Once a
  request is delivered in slices, planning the next slice needs to see its content AND its existing
  epics; `refine show` now accepts a decomposed request and lists its `Decomposed-into:` epics
  (steering to `add`), staying read-only. `refine apply` keeps its strict not-yet-decomposed
  precondition - `show` and `apply` still agree on a first decomposition, they differ only on whether
  seeing an already-refined request is allowed.

- **`refine add`: a large request grows its next epic with the tool, not by hand (EP0036, CR0274).**
  `refine apply` decomposes a request once; `refine add --request <id> --epic-title "..." --story ...`
  appends a FURTHER epic + stories to an already-decomposed request, for a request delivered in slices
  (one epic per sprint - RFC0039, RFC0040). The append to `Decomposed-into:` is de-duped and
  order-preserving, so an earlier slice is never lost, and it shares `apply`'s up-front validation and
  atomic mint (a bad breakdown or a mid-create failure mints nothing). Dogfooded: `refine apply`
  decomposed CR0274 into the epic that then built `add`.

- **The two-backlog workflow is now enforce-on-request, so an upgrade is safe (EP0034, RFC0040).**
  `sdlc_md.two_backlog_enforced(root)` reads `two_backlog.enforce` from the project's `.config.yaml`,
  defaulting OFF. The HARD gates consult it - `plan` refuses a request (G1), a request's terminal
  status is derived from its children (G2), `reconcile` flags an accepted childless request as
  `undecomposed`, and CR creation demands a T-shirt Size - so an existing project pulling this skill
  keeps its old flow (plan a CR, complete it whole, size a CR with points) until it opts in with one
  line of config. The soft, always-on parts (the sizing vocabulary itself, `link-asymmetry` which
  only fires on links a project chose to write) are not gated. This repo dogfoods it on. The
  precondition for a safe, breaking, semver-major release.

- **`refine`: a request becomes an epic and stories, with the links wired (EP0035, RFC0039).** The
  hand-decomposition the two-backlog gates otherwise ask an operator to do (CR0271 -> EP0033), made a
  command - and the migration path for an upgrading project (an old childless CR becomes stories).
  `refine show --request <id>` surfaces the request's content and confirms it is refinable; `refine
  apply --request <id> --epic-title "..." --story "title|points[|affects]" ...` validates the whole
  breakdown up front (a non-request, an already-decomposed request, an off-scale point, or a
  malformed title is refused and NOTHING is written - a mid-create IO error rolls back), then creates
  the epic (T-shirt sized from the point total, `Parent:` the request) and its stories, writes the
  request's `Decomposed-into:`, rolls the epic's `Derived Point Total`, moves the request to its
  working status, and surfaces `--question` items for a Three-Amigos consult.

- **Two backlogs: a request must become work before it can be delivered (CR0271, EP0033 - in progress).**
  Dual-track (discovery feeds delivery): RFCs and CRs are the DISCOVERY backlog (the options funnel);
  epics, stories and bugs are the DELIVERY backlog (sized work). A request enters the delivery backlog
  only by being decomposed. `sdlc_md` now owns the primitive the gates share: `is_request(type_)` names
  which side of the line a type is on, `children_of(root, id)` answers "what did this request produce"
  from a file census (a child names its parent with `Parent:`, a story with its existing `Epic:`; a
  request lists its children with `Decomposed-into:`), and `reconcile` verifies every declared link
  resolves BOTH ways - a `link-asymmetry` drift kind flags a link asserted on one side only, or pointing
  at an id that resolves to nothing (US0120). `reconcile` also flags an accepted-but-childless request as
  `undecomposed` (US0124), `status backlog` splits the Discovery and Delivery backlogs (US0123), and
  `transition` derives a request's successful terminal from its children - a CR is Complete only when its
  stories/epics are resolved, never by assertion (US0122). The last gate (plan refuses a request) lands
  under the same epic.

- **Size by what a thing IS: T-shirts on requests, points on delivery units (CR0268, CR0269).** A CR and
  an RFC are REQUESTS - sized before they are broken down - so they carry a T-shirt `Size` (S/M/L/XL),
  not points. A story and a bug are delivered directly and carry `Points`. An epic carries a T-shirt
  Size AND a `Derived Point Total` that `reconcile` recomputes from its stories, so the roll-up can
  never silently drift (an estimated total can be checked against nothing; a derived one is a fact
  reconcile keeps true). The grooming gate is now type-aware - it demands the right size for the type -
  and velocity counts story points only; a T-shirt is never summed, because it is not a measurement. A
  CR still carrying legacy `Points` reads and grooms, so the transition breaks nothing.

- **Evidence records carry the project, so cross-project data is collatable and never blindly pooled
  (CR0270).** Every forecast and actual is stamped at write time with the project, resolved from the git
  remote (stable across a rename or a different clone). The 400+ existing records were backfilled
  value-for-value. `retro collate` reads several projects' evidence and computes tokens-per-point WITHIN
  each `(project, model)` cell, and REFUSES any figure pooled across cells - the LL0035 cohort confound
  made structurally impossible. This is the precondition for tuning the rate from several projects: a
  measurement without its project can never be attributed after the fact.

- **Sizing is now Fibonacci story points, validated by blind experiment (RFC0038, CR0265-CR0267).** A
  blind re-estimation of 21 delivered units - recovered as filed, sized in modified Fibonacci by three
  independent estimators with no access to outcomes - found points predict cost at **r = +0.68 pooled,
  +0.78 on units of 8 or below**, POSITIVE within every sprint, where every computed metric had failed
  (`max_cognitive` scored +0.03) and a naive `files_affected` flipped sign between sprints. Points
  replace `Effort` S/M/L (which scored +0.35). `Points:` on the scale 1, 2, 3, 5, 8, 13, 20 is demanded
  by the filer and both `artifact` creators from one shared definition; a value off the scale is
  REFUSED, because a 7 is exactly the false precision the widening Fibonacci gaps exist to prevent.

- **`sprint plan` refuses a unit above 8 points (CR0266).** A point was a stable unit of cost from 2 to
  8 (22k-27k tokens each) and broke above it: the 13s came in at 14k per point, over-estimated, and all
  three blind estimators returned them low-confidence saying "should be split". Above 8 the estimate is
  not worth having and the unit must be decomposed - a triage decision, not an estimation one. The
  ceiling is configurable (`sprint.points_split_above`). Closes BG0147: the dead `max_cognitive`
  tie-break no longer orders the batch.

- **WSJF is Cost of Delay / Points, and runs without seat scores (CR0266).** CoD maps from Priority on
  the same Fibonacci scale (Critical 13, High 8, Medium 5, Low 3), so a small High can outrank a big
  Critical under `--order wsjf` - the whole economic point of Weighted Shortest Job First. The default
  order stays `priority`, so this is opt-in. Seat scores remain an optional CoD override.

- **The token forecast is sum(points) x a MEASURED tokens-per-point rate (CR0266, CR0267).** The rate is
  derived from the project's own `VELOCITY.md` history (actual tokens over points delivered), segmented
  per model and refused across them, never a stored constant. It ships with a documented seed (~25,000,
  from the blind experiment) that the plan labels as a seed and that a project's own evidence replaces
  once it has five measured sprints. No base term - fitting one does measurably worse. Velocity is
  recorded in points, and a delivered unit above 8 points is flagged in the retro with its own
  tokens-per-point, so the decomposition rule is answerable from each sprint's numbers.

- **The evidence records WHO estimated and WHAT delivered, and refuses to average across either
  (CR0263, CR0261).** A forecast now carries the `estimator` (from the artefact's `Estimated-by:`,
  never inferred from whoever filed the ticket) and the `effort_gate` era (`compulsory` / `voluntary`,
  read from the grooming gate itself rather than restated). An actual carries the `model`, now also
  stamped on the artefact as `Delivered-by:`. Accuracy is segmented per estimator and per model, and
  **a batch delivered by more than one model records NO pooled ratio at all** - one ratio across two
  models describes neither of them. The report names the classes an estimator systematically
  under-calls, because a directional bias is correctable and a bare correlation is not.

- **`unknown` is a first-class Effort value (CR0263).** Nobody has to invent a size to get past the
  grooming gate. `EFFORT_SIZE` has no numeric entry for it, so it cannot be silently coerced: it
  satisfies the gate, and is named and EXCLUDED from every ratio, exactly as UNMEASURED and UNFORECAST
  already are. An *absent* Effort is still refused - silence is not an answer, but "I do not know" is.
  This is the fix for a contaminant that had already bitten the project: scoring an undeclared Effort
  as zero inflated its apparent correlation with cost from 0.48 to 0.58, because the field only exists
  on later, larger units. The presence of a field is not a measurement of anything.

- **The coercion question is asked, and the tool refuses to answer it (CR0263).** BG0136 made `Effort`
  compulsory, and a compulsory estimate may be a careless one. The report compares voluntary against
  compulsory eras - and prints **NOT ANSWERABLE**, because only 5 of 29 units have an Effort recorded
  at plan time, and the compulsory cohort IS the latest cohort, so the gate's effect cannot be
  separated from the calendar's. An offline reconstruction is directionally consistent with the hazard
  (voluntary n=12 r=0.54, compulsory n=4 r=0.32) and is **not** quoted by the tool, because n=4 says
  nothing. A report that says "I cannot tell you" is worth more than one that guesses.

- **The specs describe the product again (CR0252).** The PRD and TSD self-declared v2.0.0 against a
  v4.1.0 product; all three specs now cover the engagement floor, the breakdown gate, sprint capacity
  and the run appetite, the sizing and velocity loop, ULID identity, the generated team, the learning
  loop, the mutation gate and the release gate, with five new ADRs (engagement floor, ULID identity,
  generated team, learning loop, breakdown gate) each recording the alternatives rejected and the
  consequences, including the negative ones. Where the specs describe estimation they now say plainly
  that the token forecast is a **falsified hypothesis, not a calibration**. The refresh found eight
  things that were WRONG rather than merely missing: the PRD listed five open enforcement gaps that
  have all shipped, quoted "17 open audit-filed bugs" against a real backlog of nine, said "10
  scripts" where there are 58, and the TSD pinned "181 tests" in six places where the suite runs
  2,194.

- **The breakdown step is now unavoidable: `sprint plan` REFUSES an ungroomed batch (CR0260).** A unit
  is groomed when it declares both the files it will touch (`Affects:`) and a size (`Effort:` S/M/L, a
  story's `Points:`, or a seat score). If any unit in the batch lacks either, `plan` exits non-zero and
  prints **no plan at all** - a plan over unsized units is false authority, and the flat forecast, the
  fake-parallel wave and the unsizeable bug all look exactly like a real plan. The refusal names each
  unit, what it lacks, and the command that fixes it. Enforcement lives in `plan` because that is the
  command people actually run: `--goal design` has always been specified to produce an estimated
  backlog and has never once been invoked. The escape is a recorded decision, never an omission -
  `sprint.breakdown: judgement` makes the lane report instead of block, and an absent config BLOCKS.

  The planner also now derives **shared-file clusters** from the `Affects` it already parses, so two
  units touching the same file are no longer reported as safely parallel. It caught two false-parallel
  pairs in this repo's own backlog on its first run, one of which was the CR that introduced it.
  A Large CR that no story cites is flagged for decomposition, because only a story's Done is gated on
  executable acceptance criteria.

- **A sprint capacity budget, and the plan-time check and the run-time breaker are now one number
  (CR0259).** `capacity.tokens` / `capacity.minutes` / `capacity.units` give the operator a
  per-sprint ceiling. `sprint plan` sizes the batch against it and flags an over-budget batch AT
  PLAN TIME, instead of the operator discovering it when the run breaker halts the sprint mid-flight.
  The appetite is resolved once, at plan time, and stamped on the run state, so `loop_guard` reads
  back the same ceiling the plan showed and the two cannot disagree. Over-budget is a WARNING and
  never a gate, even under `--strict`: a script cannot observe token spend, so the token half is a
  forecast and is quoted with a plausible band rather than as a bare number. The band widens on an
  observed miss and never narrows - a sprint that agrees with the model is not evidence of precision.

- **The filer refuses a command-shaped `Verify:` in a CR or bug acceptance criterion (BG0132).**
  Only STORIES carry executable verifiers. The convention had drifted into writing `Verify: <command>`
  into CR/bug AC prose, which looks executable and is never run - so a wrong one is a permanent false
  RED and a loose one is a false GREEN. Both had already happened: one grepped for an env var under
  the wrong name, and one (`rg -qi 'effort' sprint.py`) PASSED on unrelated prose while the feature it
  claimed to check did not exist. `file_finding.py` and `artifact.py` now refuse one at creation, from
  a single shared authority so the two paths cannot disagree, with an error that says why nothing runs
  it and what to write instead. `validate.py` warns on the ones already in the tree; all 49 of them,
  across 18 artefacts, are rewritten as honest statements of the observable outcome. Prose that uses
  the word verify honestly is deliberately untouched.

- **The retro now asks whether the estimates were any good (CR0258).** `retro.py accuracy` reports
  the plan's token forecast against what telemetry measured, per unit and per batch, and `--write`
  records it in the retro and appends the sprint's row to `retros/VELOCITY.md` - a committed history,
  so the next plan can see how the estimator has actually performed instead of trusting its
  constants. Two honesty rules are enforced in code: a unit with no telemetry is reported
  **UNMEASURED** and excluded from both sides of the ratio (silence is not a measurement, and every
  report states how many of the batch it speaks for), and nothing auto-recalibrates - the report
  stops at reporting, because auto-fitting constants to a handful of units fits noise and dresses it
  as evidence. `telemetry.latest_actuals()` reads the last **non-null** value per field, so the bare
  close-record the loop appends after an instrumented one no longer erases the measurement.

- **The human `Effort:` estimate now reaches the planner (CR0257).** `sprint.py` reads a unit's
  declared `Effort:` (S/M/L) and uses it as the WSJF job size when the review seats have not scored
  the unit, and as a complexity stand-in for the token forecast when the unit names no files - so a
  Large CR with no `Affects` no longer forecasts the same flat floor as a Small one. The size chain
  is seat score, then declared effort, then a neutral default; an unreadable value is treated as
  undeclared, never guessed. A unit with real complexity is never inflated by its effort, so the
  measured forecast model is untouched. Bugs can now carry an `Effort:` too (`file_finding.py
  --effort`, and the bug template), because the fix's job size sizes the sprint whether the work
  arrived as a CR or a bug.

- **LL0025 - a narrow sample can make a variable look constant; widen the range before concluding.**
  Three measured units came in flat within 9% (42.7k-46.8k tokens) and a High bug was filed saying
  the metric did not track work. Two larger units then landed at 84k and 98k - it tracked work fine.
  The three samples had all sat in one narrow band (11-15 tool uses), where a large fixed cost
  dominates and the variable component is invisible. The failure was not "too few samples" but **too
  narrow a range**: five samples clustered at one end of the input space say almost nothing about the
  slope. State the range a conclusion covers ("constant across 11-15 tool uses"), not a claim it
  never tested ("does not track work").

- **The review now starts FROM the lessons (CR0242, completing it properly).** `review_prep.py`
  front-loads the mechanical inputs a review needs so it "starts from data instead of re-deriving
  it" - and the ranked lessons are now part of that payload, as review lenses. The adversarial
  audit seeds its lens set from the registry too (`reference-audit.md` step 0). CR0242 had been
  marked Complete with only `sprint plan` wired, which is exactly LL0008 - reporting a success not
  achieved - committed inside the change about nobody reading LL0008. A test now pins all three
  read-points so the claim is provable rather than asserted.

- **A recorded lesson disposes of a retro finding.** Found by dogfooding: the first retro written
  with the new tooling disposed of a finding by recording `LL0024`, and the gate refused it.
  Refusing pushes such findings toward a decline (which loses the lesson) or a make-work CR (which
  is the noise the decline path exists to prevent). Some findings are not tickets - the right
  outcome is a habit, and a habit's durable form is a lesson.

- **Operational and incident lessons have a home (RFC0032, CR0245).** The lessons template now
  carries a heavier operational shape - an incident narrative, a tickable runbook written for
  someone following it under pressure at 3am, and a decay note saying what to re-verify before
  trusting it. This is the category with the most expensive failures and, until now, the least
  support: an infrastructure project wrote a 750-line ops-lessons document *outside* the workspace
  because the registry had nowhere to put deploy, incident and DR lessons. It then outgrew the
  agent's memory store and was evicted to a file no tool reads. Teams route around what does not
  fit them.

- **The learning loop is doctrine, with an opt-out (RFC0032 D5, CR0246).** Doctrine rule 17: a
  retro is checked on its content, every finding is dispositioned, and its lessons are lifted into
  the store the next sprint reads. Same shape as the engagement floor, and the same reasoning - a
  process step gated on judgement is the step that gets skipped. Set `lessons.loop: judgement` to
  make the lane advisory; it still reports, it never blocks. The claim behind the default, that
  closing the loop cuts repeat defects, is **registered as a claim to be measured, not asserted**:
  it is mandated on the engagement floor's reasoning and not yet on its evidence, and that
  distinction is kept honestly rather than quietly elided.

- **The cross-project lessons registry finally has an automatic reader (RFC0032 D2-D4, CR0242).**
  It had none. `sprint plan` carried a lessons digest, but that digest sourced the *project* tier;
  the `LL` registry was reachable only by explicitly running `lessons recall` - a prose
  instruction, and prose instructions are the ones that get skipped. So a class could be written
  down, paid for, and written down again without ever reaching the agent about to repeat it. The
  ranked registry is now printed in the plan, unasked, in the output the agent already reads. A new
  project inherits it as its day-one lens, which is the only tier that can help a team *before*
  they have made the mistake. `PLAN_DIGEST_MAX` raised 20 -> 50; the elided tail stays loud.

- **`lessons rank` - the summary is a live instrument, not a diary (RFC0032 D6, CR0244).** Ranked by
  **recurrence** (how many artefacts cite the lesson - computed from the files, never asserted),
  **recency**, and **structural-fix demotion**: a lesson whose class a shipped guard now makes
  impossible is demoted, not deleted, so it stops crowding out the ones that can still bite you.
  Declare the guard with a `Guard:` field. On this repo's own registry the ranking puts **LL0008**
  ("a deterministic tool must fail loud, never report success it did not achieve") **second, cited
  34 times** - the exact class behind today's installer bug, a deploy that reported success over a
  stale container, and a truncated secrets file. It was written down the whole time. Nothing was
  showing it to anyone.

- **The retro has a deterministic spine: `scripts/retro.py` (RFC0032, CR0247).** The retro was the
  only enforced ceremony with no script behind it, so the gate had nothing to interrogate but the
  filesystem. `retro.py validate` is a content check (required sections, at least one real lesson,
  every finding dispositioned); `dispose` reports each finding as filed, declined or undecided; and
  `extract` lifts the retro's `## Lessons` bullets into the project lessons log, idempotently, so a
  lesson written in a retro reaches the digest the next sprint actually reads. Previously it
  reached nothing.

- **The retro is documented at last (CR0240).** `help/retro.md` and `reference-retro.md` now exist.
  The retro was the one ceremony the close gate blocked on and the one ceremony with no help file,
  no reference file and no command in the router - so what belonged in a retro was folklore. The
  skill's own `doc_coverage` guard caught this the moment `retro.py` landed, which is the guard
  working exactly as intended.

- **The retro template asks the question that turns a retro into work (RFC0032 D1, CR0243).**
  A new `## Actions raised` section asks, in as many words: *are there any CRs or Bugs you want to
  raise to address any of the issues found?* Every finding takes a disposition - **filed**, or
  **declined with a reason**. Both are green, so honesty costs exactly what noise costs and there
  is nothing to game. What does not pass is silence. The evidence that this works: 8 of 9 retros in
  a consuming project carry a `## Lessons` section *because the template prompts for one* - and
  those same 9 retros reference exactly 1 artefact id between them, because nothing ever asked.

### Changed

- **The 108 findings that hid their audit run inside `Raised-by` prose now carry it as a field: `backfill_audit_runs.py` (US0568).** Counting a class across runs meant a regex over free text where a field read will do. The pass relocates a datum somebody already wrote and invents nothing else - `plan` reports, `apply` stamps and seeds, and `check` is the standing sweep a guard runs.

  **Two rules the prose already settles, so neither was a judgement call.** Twelve findings name TWO ids, in the shape `adversarial audit <A> carry-over, run <B>`: `B` filed it and `A` is the earlier run it carried over from, which the sentence says outright. All twelve match, so none needed a choice made for it - and the carry-over id comes FIRST, so taking the first id would have attributed twelve findings to the wrong run and made one run look like two. A line the prose does not disambiguate is refused rather than resolved by order.

  **The lens is NOT derived.** `detector-owed` groups by lens, the prose carries none, and guessing 108 lenses from sentences written for another purpose would be inventing evidence at scale. Each backfilled finding records its lens as explicitly unknown, and that placeholder counts as UNATTRIBUTABLE rather than as a lens of that name - otherwise 108 findings sharing one placeholder across five runs would read as a detector owed on every one, a verdict manufactured out of nothing. The sentinel has one definition in the shared library, because the writer that stamps it and the reader that decides attribution by it must agree.

  **Seeded rows are stamped `backfilled`, never `recorded`.** These are harness workflow ids lifted from prose, minted by nothing this project runs.

  Five run ids, not the three the request named: the two it missed were the two with the fewest findings, which a spot check would have missed the same way, and the request's own closing sweep would then have failed on the real corpus. The per-run counts are pinned against the live tree so a sixth id reddens a test rather than being skipped.

  `detector-owed` now scans RFCs as well as bugs and CRs, because the RFC template renders the same attribution fields and a reader scanning fewer directories than the writer stamps would make an attributed RFC invisible to every verdict.

  The new script was held to the house conventions its own guards enforce, which it initially failed three of: it anchors `--root` through the shared resolver before dispatch, carries a row and a count in the root census, and has a real write-confinement case rather than an allowlist entry - its fixture finding is a CR rather than a bug, since two sibling cases mint `BG0001` and seeding the bugs directory would have shifted their ids.
- **The retro scaffold passes its own validator (US0558).** The shipped template omitted `## Carried lessons` entirely and left every other checked section as a `{{placeholder}}`, so a freshly scaffolded retro failed `retro validate` three ways and the carried-set shape and the `fixed-in:` / `declined:` vocabulary were each learned from a separate rejection - every one of them after a full gate run. The template now DEMONSTRATES each shape: a carried set of exactly the limit as bullets, and all three accepted dispositions filled in rather than described. That trades one failure for another, since a retro nobody filled in would now pass, so every worked example carries a marker and `retro validate` reports any left in place - on both the pass and the fail path, because a structurally valid retro whose content is still the template's is a different failure from a malformed one and blocking on it would refuse a legitimate close.
- **A missing required argument is refused once, before anything is written (US0557).** `critic signoff` needs `--author`; it was learned from a refusal, one unit at a time, at a cost of nineteen wasted spawns. The requirement now lives beside each verb rather than on argparse alone, so one refusal names EVERY argument the verb needs and arrives before the first write. A guard holds each refusal message against the parser itself, so a message can never send a caller to a flag the command does not accept.
- **`critic record`, `evidence` and `signoff` each take a whole batch in one invocation (US0556).** Recording three facts about nineteen units cost fifty-seven process spawns, each paying interpreter start, imports and a read-modify-write to record one line. `--units` names a batch, `--from-run` takes the open run's approved batch - refusing when no run is open rather than degrading to acting on nothing and reporting success - and a repeated `--unit` accumulates instead of keeping only its last value, which is BG0386's defect stated as a contract. The single-unit form is unchanged. Exit codes distinguish the two outcomes a caller acts on differently: nothing written is a refusal (2, as the single-unit form has always returned), a partly written batch is 1 and names both the units that landed and those that did not.
- **A listing-only declaration can name the ids its structural read depends on (US0554).** `GATE_LISTING_ONLY` was a directory, so a module whose census asks about a handful of named artefacts made EVERY new file under that tree structural - and filing an artefact is most of what a sprint close does. A declaration may now be `{"path": ..., "ids": (...)}`; a structural change is then relevant only for the ids it names. The fail-safe direction is preserved four ways: a bare-string declaration, an unreadable `ids` value, an empty id set and a file whose name carries no id all keep the old whole-directory meaning, so the narrowing is opt-in and getting it wrong is slower rather than blind. Two modules reading one tree take the union of their ids, and a bare declaration beside a scoped one wins outright - one module's narrowing never speaks for another's read. `test_root_census.py` declares the single id it reads, and a guard holds that list against the census record in both directions, so an id added to one and not the other fails instead of going quietly unprotected.
- **The gate prints each lane's own seconds, not only its total and dominant lane (US0533).** The per-lane figure had been recorded since the cost report was added and no reader ever saw it: the text report named the lane that dominated, which says where the worst of the cost went but not what the second and third cost - and that is what a decision about where to spend effort needs. CR0465's own 25 seconds were invisible for exactly this reason. A lane that was not timed prints nothing rather than `0.0s`, because untimed is not instant and a zero would send a reader looking anywhere but the lane that has the cost.
- **`reconcile detect` reads the artefact corpus once per run instead of once per lookup: 22.3s to 1.3s (US0531, US0532).** Every sweep detector walks the artefact tree, and `find_by_id` and `children_of` were asked per unit - 650 and 72 times over this workspace, each one a fresh walk that opened and read every file. One `reconcile detect` opened 777,732 files, and reconcile is a gate lane, so that was paid on every commit. `sdlc_md.corpus_cache()` memoises the walk, a by-id index and a parent-to-children index for the duration of one read-only sweep. It is OPT-IN and scoped to a `with` block, never a module-level memo: the cache cannot see a write and `reconcile apply` sits beside the sweep it exists for. Nesting is a no-op so an inner block cannot hand the outer one a second, emptier cache, the block closes on an exception, and a `trust_names` walk bypasses it in both directions because its results differ from an ordinary walk's by construction. The by-id index keeps the FIRST match in `ARTIFACT_TYPES` order - the answer the linear walk gave - so a duplicate id cannot resolve to a different file just because the lookup got faster.
- **RETRO0083's delivered figure is corrected a third and final time, and computed rather than restated.** The run delivered **133 of 148 planned points across 44 of 48 units**, plus 9 points of repair discovered and delivered in-run (BG0400, BG0408, BG0409, BG0410), giving a 52-unit accounted batch. The figure was written as 143/47, then 138/45, and each correction was drafted from memory of the previous one rather than derived from the artefacts, so each carried the next error forward: the first counted BG0372 and BG0359 (both later reopened for delivering nothing), the second still counted US0553 (reverted, standing Blocked). The current figure is computed from the Status field of all 52 files. The retro's estimate-versus-actual block is now populated and a VELOCITY.md row written, clearing the two close obligations the last run left open; the row records 107 points rather than 133, because velocity counts only terminal units and ten stories stand at Review awaiting sign-off.
- **AGENTS.md states the front-door rule:** exercise every claim through the shipped entry
  point before asking for review. A review should confirm the work, not discover that it does
  not run. A library test cannot see a missing lane, because the wiring is the part it does
  not exercise - `brief_fingerprint(brief(...))` passed in-process for a whole sprint while
  `critic.py brief` printed nothing and the paperwork said otherwise. The rule is recorded as
  known-weak until CR0520 ships `verify_ac lane-check` to gate it, because a rule with no gate
  behind it is one that gets skipped (LL0027).
- **The triage noise controls have their own switch, and this project has finally turned them on (CR0510).** A session cap and low-severity consolidation have shipped for some time and were reachable only through a `schema_version: 3` bump - which also switches on plan-review, spec-guard and the inbox status, so adopting a cap on filings meant adopting four unrelated things. The result was that the project which built them had never once run them: 801 findings filed in a month, roughly 26 a day, against a cap of 20 sitting unused; 27 of 29 open bugs were skeletons; and the low-severity fold was being hand-rolled, one artefact in this tree being twenty findings bundled together by hand. `triage.enabled` now decides it, falling back to the schema version when unstated - so every consuming project behaves exactly as before, and a project that wants the controls can have them without an unrelated migration. The cap remains a loud REFUSAL rather than a silent drop, naming how to proceed.
- **US0629 AC2 is restated in mechanically decidable terms, before anything was built against it (BG0525).** It asked `derive` to refuse a mutant that is "that criterion's own text with the polarity flipped", and an independent seat reviewing the TEST PLAN produced the mutant that defeats every proxy: a field naming a real file, naming a real edit, and being the criterion with its polarity flipped. The replacement asks four checkable things - a non-blank field, a path drawn from the unit's own `Affects`, an edit verb, and no more than 60% meaningful-token overlap with the criterion's `Then` clause - and carries its own discriminating pair (71% refused, 24% accepted, differing in one property) plus a near-miss ACCEPT, without which a guard that refuses everything passes every refusal row.
- **The threshold is a stated number with a stated basis (BG0525).** It follows `_reason_substance`, which measures substance after filler comes off and carries the scar of a one-character `-` passing a non-blank check. Implementing the old wording would have produced BG0523's class exactly: a criterion marked Verified against a verifier pinning a proxy rather than the property.
- **The test-census attribution guard is a visible ratchet rather than a cliff (BG0469).** It asserted that more than 80% of test files attribute to a sibling module, and was sitting at 0.8045 - 179 files, 144 placed - so a single new cross-cutting test tipped it. The guard gave no warning it was one file from firing, which is how a threshold fails as a surprise rather than as a signal. It now carries a declared `UNATTRIBUTED_BASELINE` alongside a looser collapse floor: the floor still catches attribution breaking down, and the baseline makes the remaining gap countable and shrinkable. 29 of the 36 unattributed guard a hook, a document or a contract, which the name-or-reference convention cannot place by construction. Lowered when a file gains a home, never raised to accommodate a new one.
- **Six guards now state what they check, and what they do not.** Independent review established that a number of guards assert something weaker than the criteria verifying them claim, and the repairs are carried. What is not carried is the over-claim itself: a guard that says more than it checks is the defect it was built to prevent, wearing its own name. The TRD surface guard now records that its set comparison has ONE direction and is structurally unable to catch a document naming a lane the code lacks - measured, with three surviving mutants named. The token-premise guard records that its whole-file substring is satisfied by the Revision History row describing the change being asserted. The ADR-011 guard records that its word-presence check is already satisfied by an unrelated sentence, and that its wiring check reads source text, so a comment naming the call satisfies it. On the sprint checklist: the not-delivered row says it reads the retro's Batch rather than the run's planned set; the known-issues row says an empty result and a scan that could not run are indistinguishable to it; the review row says it counts distinct reviewer NAMES, not seats; the impediments row says it does not read the blocker; and `cycle_drift` records that it walks the `sprint` verbs only and that its unverifiable bucket is non-empty today. The shipped sprint doctrine no longer says the checklist and the cycle "cannot part" - it says the guard narrows that drift rather than closing it.
- **The evidence lessons from five consecutive REJECTs are shipped, not just observed (BG0422).** A sprint returned five REJECTs across five reviews with the production code right in most of them - an evidence problem rather than a code-quality one, and the two need different remedies. `best-practices/testing.md` now carries the rule that closes the dominant class: name the mutant in the test's docstring BEFORE writing the test, and if it cannot be named there is nothing to test yet. All eight mechanisms that produce a test which passes whether the feature is present or absent are named individually, because each needs a different habit to catch, along with the two rules that follow (test the surface the user invokes; for every reader you add, name its writer) and the honest limit of a pre-implementation design review - it catches the two structural classes and cannot see a test that does not exist yet, so it is not a general cure. `reference-agentic-lessons.md` states the review-before-commit sequencing the same sprint built a mechanism for and then ignored five times. Recorded cross-project as LL0050.
- **The RFC index column is named `Decomposed into`, for what its cells actually hold.** It
  read `Spawned CRs` while most cells held EPIC ids - a column whose name contradicts its
  contents, which a reader has to know the history of to interpret. Renamed in the shipped
  TEMPLATE as well as this repo's index, because the header is fixed by the template and a
  rename here alone would drift back on the next project that generates one.
- The rename is only safe because the drift check reads a SET of header aliases: keyed to one
  spelling it would have silently exempted the column it exists to check. Both spellings stay
  in the set, so a project that has not renamed is still checked.

The drift half of this bug was already delivered and wired into `reconcile`; it reports zero
on this corpus today. What remained was the header.

- **The pre-commit gate budget is re-declared against the measured cost (US0432, CR0420).** The
  120s ceiling was set when the suites were half their current size, so every commit reported OVER
  and the signal became noise. It is re-declared to 380s against a 317s measured baseline (skill +
  tool suites + cheap lanes), with ~20% headroom - so a normal commit reads under budget while a
  genuine regression still flags, with the drift measured from the new baseline.
- **The delivery-mode disjointness check treats build tooling and shared config as coupling
  (US0416).** A unit touching the commit hooks, the `tools/` guards, the gate, `package.json`,
  `install.sh`, the CI workflow or the shared project config is never offered as parallel-safe -
  two worktrees editing different tooling files still share the one gate that runs across both, so
  a merge-clean split is not a safe one. The build-tooling set is declared explicitly, never
  inferred from a filename shape, and the contract is documented where the delivery mode is.
- **`reference-cr.md` and `reference-rfc.md` state what `refine` actually produces (US0412, EP0155, CR0412).** Both now describe the plannable-but-ungroomed contract: refine mints a unit that is plannable now (an `Affects` is present - the story's own, inherited, or seeded from the request) whose acceptance criteria still need grooming, and both name the `sprint.breakdown: judgement` opt-out. The two-backlog promise - a refined request is delivery work - is stated as it is rather than as an aspiration.
- **A refined story's acceptance criteria are labelled an ungroomed grooming placeholder, and the ungroomed count is machine-visible (US0411, EP0155, CR0412).** A story `refine` mints without seeded criteria used to carry a bare `### AC1: {{define}}` scaffold that read as thin authored content. It now carries an explicit marker stating the ACs are a grooming stub, so a reader tells a groomed story from an ungroomed one at a glance. `conformance` counts the stories carrying the marker (`summary.ungroomed`, a per-unit `ungroomed` flag, and a CLI line), so an operator sees how much grooming a refined backlog still owes rather than meeting a full-batch refusal at plan time. The marker never reads as a specified AC, so an ungroomed story stays honestly unspecified.
- **`refine` requires or inherits an `Affects` per story, so a minted story is plannable the moment it exists (US0410, EP0155, CR0412).** A bulk refine over dozens of requests supplied only title and points, so `refine apply` minted stories with no `Affects` that `sprint plan` then refused as ungroomed - a backlog that read as sized delivery work could not be planned at all. A story now takes its `Affects` one of three ways, all resolved before anything is minted: its own path list; the `inherit` keyword (`title|points|inherit`, or `inherit:paths` to narrow the request's footprint); or, given none of its own, SEEDED from the request's `Affects` (marked for confirmation) when the request declares one. A story with nothing to inherit and none supplied is refused, naming the story and how to supply it - refine never mints a unit nobody can plan, and never half-decomposes. A recorded grooming opt-out (`sprint.breakdown: judgement`) downgrades the refusal to a warning. The requirement applies to newly-refined stories at mint time only; the existing backlog is untouched.
- **The sprint guidance states the batch-size trade-off from the measured rows and prescribes no
  number (US0397).** `reference-sprint.md` and `help/sprint.md` now name the trade-off - fixed cost
  falls per point as the batch grows, review convergence cost rises with it - grounded in this
  project's own measured velocity rows and naming how many sprints it rests on. It prescribes NO
  batch-size number: with this few measured sprints there is no defensible optimum, and inventing
  one would repeat a mistake this project has twice had to undo.
- **The review guidance requires a round of at least two reviewers on distinct lenses, one of
  them the claims lens (US0396).** `reference-review.md` and `reference-sprint.md` now state that a
  round is at least two reviewers with distinct lenses whatever the diff size - a small diff is not
  a licence to drop to a single pass - and that one lens is always the claims lens. Where a round
  runs with one reviewer anyway, the review record says so, so an under-covered round never reads
  as a full one.
- **Three plan-surface messages read straight (US0386, US0387, US0390).** A zero-remaining handoff
  now states nothing carried over and offers no `--worklist`, so a clean close reads as good news
  rather than a false action item above the warnings that need reading. The run-opened line names
  the Sprint Goal and the `--goal` ladder rung with distinct labels (`rung=...`, `sprint-goal=...`),
  so `rung=done` is never misread as the Sprint Goal failing to take. The no-batch-selected error
  shows a usable example status per selector (`--bugs Open`, `--crs Proposed`, `--stories Ready`),
  so the first retry is a working invocation.
- **The mutation documents describe the ledger the gate actually reads, not the whole-blob
  report rule it superseded (US0384, US0385).** `help/mutation.md` and
  `reference-scripts-verify.md` said the lane reports STALE on a rev change or any edited
  target, which has not been the rule since coverage moved to `mutation-runs.json`. Both now
  name the ledger beside the report, state that an entry is keyed on that file's content hash
  at run time so evidence survives commits to other files, state the 200-entry bound and its
  cumulative dropped total, distinguish a `measured` run from a `registered` self-report, and
  give the per-file verdict - a matching hash is covered, a hash that no longer matches is
  stale, no entry is uncovered - with the degraded whole-report fallback and the lane's
  advisory status stated on both pages. `trd.md` gains the ledger's state-file row and
  `tsd.md`'s mutation and gate-lane tables carry the per-file verdict; the reconcile pass
  checked 19 mutation claims across the two specs and records a verdict for each, including
  the 11 it verified and left alone, in US0385.
- **The harness token capture records which model spent the tokens, and the interactive close
  writes it to the velocity row (US0376).** `harness_tokens` reads the transcript model alongside
  the total - a single id, or `mixed` when the session spanned two - and the interactive close
  writes it to the Model cell, so `measured_rate` books each interactive sprint in the correct
  (project, model) cell instead of the unrecorded-model bucket. A runner sprint's per-unit models
  still win; the harness model fills only the interactive gap.
- **A superseded verdict row is retired for every gate that reads it, and still visible to every reader (US0375).** `verdict_for` skips it and falls back to the latest live row, so a unit whose only row is superseded has no verdict rather than an approval; the sign-off gate no longer counts its reviewer among the authoring session's own, so a principal wrongly recorded as a reviewer can sign off instead of being stranded at Review for ever. `read_verdicts`, `critic show` (text and json) and the sign-off brief still return and print the row, flagged with its reason and authoriser, so the audit trail keeps both facts: that it was recorded, and that it was retired.
- **The commit-message rules are checked ahead of the expensive test lanes (US0372).** The gate costs about 205s when scripts are staged, and a one-line commit-message defect was refused only after all of it had run, then paid for again on the retry. Git invokes `pre-commit` before the commit message exists - at that point `COMMIT_EDITMSG` is absent or still holds the previous commit's message - so no ordering of lanes inside that hook could ever put the message rules first. The two unit suites, with the timing, scope and budget recording that wraps them, therefore moved into `commit-msg`, behind the message check. `pre-commit` still owns the selection rule and hands its verdict over in a one-shot record inside the git directory, so the docs-only skip, the cheaper-lane short circuit and the per-commit budget total (now the sum across both hooks) all behave as before. Measured on this repo: a message refusal fell from 212s to 33s, and no lane is lost or duplicated.
- **The pre-commit unit-suite selector measures the test-relevant set instead of naming three
  directories by hand (US0368).** `gate.py --test-relevant` derives the set from what the shipped
  suites actually read - the hooks, the workflow file, `install.sh`, `package.json`, reference
  docs, help pages and shipped artefacts, none of which the old `scripts/`, `templates/`, `tools/`
  regex covered - so a commit touching a doc a test asserts over no longer takes the docs-only fast
  path and skips that test. A hand list is a lower bound; the measurement is over-inclusive on
  files and precise on directories, so it never skips a suite that was needed.
- **The LATEST.md over-ceiling refusal states the overage and names the longest sections (US0365).**
  `doc_freshness` now reports how many lines the anchor is OVER its ceiling (for example, 2 over
  the 80-line ceiling) rather than leaving the reader to subtract, and names the longest sections
  by line count so the trim can be aimed rather than guessed.
- **The safe form for prose is documented family-wide, and a consuming project now inherits it (US0363).** The script contract in `reference-scripts.md` gains the rule as its own numbered clause: `file_finding.resolve_prose_fields` is the one loader, all nine prose-taking writers take `--fields-file FIELDS.json`, and `--fields-file -` reads the document from stdin. The flag path still works and still reports a field that arrives already mangled, stated as defence in depth rather than the fix - measured against the recorded corruptions it catches three of the four with no false positive over the project's own artefact prose, and the fourth is undetectable in principle. `templates/agent-instructions.md` carried no line at all, so a consuming project inherited none of this; it now carries one.
- **The test suites and the scripts catalogue follow the `audit`-stem rename (US0346, RFC0033 D1).** `test_audit.py` -> `test_readiness.py` and `test_audit_check.py` -> `test_schema_check.py`, with two new classes (`RenameTests`, `RenameDocsTests`) pinning that no shipped file reaches for the retired module names, the renamed modules resolve and change no verdict, and the public `audit` command is untouched. `reference-scripts.md` and `reference-scripts-review.md` now catalogue `readiness.py` and `schema_check.py`, and the `scripts/audit.py`/`scripts/audit_check.py` references in `reference-sprint.md`, `reference-audit.md`, `reference-schema.md`, `help/sprint.md` and `help/audit.md` point at the new names, so no doc sends an agent to a script that no longer exists.
- **The two deterministic `audit`-stem scripts are renamed, freeing the verb for the user-facing weakness-hunt (US0345, RFC0033 D1).** `audit.py` (sprint tranche pre-flight readiness) is now `readiness.py` and `audit_check.py` (the schema-v3 CI linter) is now `schema_check.py`. The move is internal only - the user-facing `audit --profile repo` command is unchanged, its profile-resolution engine simply lives under the new module name. Every Python importer moved with the files (`handoff.py` and `artifact.py`, the real in-repo callers; the story's `gate.py`/`sprint.py` framing describes the documented pre-flight and CI steps, which are not code imports), and byte-identical output for the same input was verified command-by-command against the pre-rename baseline: only the two `--help` usage lines change, naming the new scripts.
- **The shipped seed basis names the condition its "no base term" finding was measured under (US0339, EP0114, CR0391).** The seed no longer asserts flatly that a fitted base term does worse; it states the result was measured on per-unit actuals with no sprint ceremony, review rounds or close - a finding about the build, not a whole sprint. The condition travels with every forecast basis, seed or local, and `reference-sprint.md`'s estimator account carries the same qualification, so the doc cannot be cited against the fixed per-sprint term the same release ships.
- **A fitted fixed term is never applied automatically (US0338, EP0114, CR0391).** The plan states how many sprints the fit rests on and keeps a fit below `FIXED_MIN_SPRINTS` (3) out of the total, reporting it as NOT APPLIED with the minimum required and the count the project has - a line through two points is not spent as calibration. Every quoted fixed term, applied or not, states its sprint count. At or above the minimum the term enters the total and the plan says so.
- **The token forecast carries an explicit fixed per-sprint term beside the per-point term (US0336, EP0114, CR0391).** The total is `fixed + sum(Points) x marginal rate`, and the plan shows both terms on their own lines rather than a single product. Halving the batch no longer halves the forecast: the fixed term is amortised over fewer points, so a small batch is not priced as though the ceremony, review rounds and close were free.
- **help/sprint.md documents the single run slot (US0329, EP0111).** A new "One run slot" section states that a project holds one run, that a disjoint batch is refused rather than merged, and that an overlapping re-plan accumulates - naming the same two routes (close, or a `--write` re-plan) the refusal prints.
- **A run whose only close artefact is a FAILED close attempt is open-and-protected, not absorbable (US0328, EP0111).** `close_attempts` is deliberately not a close artefact, so a mid-close run stays `running` and is covered by the disjoint guard - the run most likely to be worked around no longer silently absorbs the next batch. A truly closed run (carrying `ended_at`) is still archived and replaced. The refusal states that a close attempt already ran and how many items it left outstanding.
- **The disjoint-batch refusal names the open run and both ways forward (US0327, EP0111).** The message carries the open run's id, its `running` outcome and its batch size, and states two routes as runnable commands - close the open run, or re-plan it deliberately - so the operator acts without opening the run state.
- **`sprint plan --write` refuses a disjoint batch against an open run instead of fusing it (US0326, EP0111, CR0401).** A project holds one run slot. A batch sharing no unit with the open run is refused - the command exits non-zero and `run-state.json` is byte-identical afterwards, so no partial write survives. An overlapping re-plan still accumulates into the same run with no new flag. This holds one run to one Sprint Goal and one closing verdict, rather than producing a fused run whose goal describes a fraction of it.
- **Forecast in days and sprint-sessions, not ISO weeks (CR0314, EP0063).** `flow forecast`
  defaults to day-bucket sampling (zero days included, dates at day precision); a new
  `--bucket sprint` samples measured per-sprint throughput from the velocity history and
  reports sprints-to-complete plus hours at the measured elapsed-hours-per-sprint median,
  refusing under three sprints of history and naming unmeasured hours. The ISO-week bucket
  stays available via `--bucket week` or `flow.forecast_bucket`. Every refusal guard
  (seeded, min-history, all-zero, non-positive, horizon) holds in every bucket.
- **Spec-truth refresh: PRD/TRD/TSD/RFC reconciled with shipped `main` (EP0071, RUN-01KXR6XS).**
  A batch of documentation-alignment stories corrected specs that had drifted from shipped
  behaviour:
  - **US0201/US0203 (PRD + TRD).** PRD §3/§10/§11 and TRD §10/§12/§13 now describe the shipped
    cost model - modified Fibonacci Points on story/bug, T-shirt Size on CR/RFC/epic, forecast =
    sum(Points) x the measured tokens-per-point rate (r = +0.68, RFC0038), recorded at plan time
    to `telemetry.forecasts` - instead of the falsified file-complexity predictor and the two
    loop defects (BG0133/BG0136), now fixed. The version check and `git fetch origin` are
    enumerated in the PRD Security NFR / §8, the feature inventory, and TRD rule 6 / §9 as the
    second and third outbound network paths beside `gh`.
  - **US0206 (TSD).** Corrected two false claims: the blocking 80% CI coverage gate (reconciled
    with the ~90% aspiration) and the blocking bandit security scan are now recorded, where the
    TSD had asserted neither was wired.
  - **US0207 (RFC0034).** Marked D1/D5 superseded by RFC0038 with cross-links in both RFCs and
    the rfcs index; D2-D4 remain live and underpin the shipped model.
  - **US0202 (PRD §3).** Populated every `[Unreleased]` row's Epic column and added rows for the
    EP0033-EP0047 features; where a feature had no owning epic (delivered by a CR/RFC sprint) the
    governing id is cited, with a preamble note for the exception.
  - **US0204 (PRD §9 + config).** Corrected `require_ac_verification` (shipped default `false`, the
    table said `on`); added `quality.done_requires_verified` (the true hard-by-default Done gate)
    and `two_backlog.enforce` (deliberate default-off) to the PRD table, `config-defaults.yaml` and
    `reference-config.md`; retired `SDLC_ENGAGEMENT_STRICT`; added `SDLC_AUTHOR`,
    `SDLC_VERIFY_HTTP_HOSTS`, `SDLC_TRIAGE_SESSION`, `SDLC_DEBUG` to the env-var table.
  - **US0205 (TRD ADR-008).** States the real ULID guarantee (6+2 chars, ~1-in-1024 per ~17-minute
    bucket, glob-retry backstop) with a cross-machine residual-risk paragraph naming `next_id.py`'s
    collision detector; "collision-free" softened to "collision-resistant".
  - **US0208 (TRD §3/§5 + critic.py).** `critic record` moved to the writer list with the
    append-only-ledger exception documented; `read_verdicts` now warns on a torn row instead of
    silently dropping it (red-first test).
  - **US0209 (TRD §6).** Adds the `issue` type, the `Blocked` story status, the inbox triage lane
    and a two-backlog subsection to the type registry.
  - **US0210 (TRD §5).** Rule 5's writer list gains `retro.py`/`handoff.py`/`archive.py`/
    `persona_gen.py`/`decisions.py`, declared non-exhaustive with a pointer to the script catalogue;
    ADR-009 no longer contradicts it.
  - **US0211 (TRD counts).** Drifted exact counts converted to growth-tolerant bands and the 4.0.0
    changelog line restated to what the freshness guard actually checks.
  - **US0212 (TRD §6).** Names the shipped migration surface (`migrate.py`, `project_upgrade.py`
    `--apply`, `migrate_v3.py`) and reconciles the `upgrade`-type-vs-`migrate`-command naming.

- **Story workflows resolve personas registry-first (CR0283, EP0049).** `reference-story.md`'s
  create and generate prerequisites now read the `sdlc-studio/personas/` registry (index.md +
  per-persona cards) as the primary source, with the flat `personas.md` as a documented legacy
  fallback - a registry-only project is no longer STOPped on a file it never created. Step 3's
  persona selection defaults to the declared **Primary** from `personas/index.md`, and a
  **Negative** persona is never a story target. `help/story.md` prerequisites and validation
  tables updated to match.
- **validate covers the legacy personas.md layout (CR0297, EP0051).** `check_personas` no longer
  gives a vacuous clean pass to a personas.md-only project: the legacy flat file (the one the
  story pipeline falls back to) now gets a `persona-layout` advisory plus a light structural
  check (`persona-legacy`: unfilled `{{...}}` boilerplate, no persona sections) - including when
  `personas/` holds only seats/stakeholders and story generation would fall back to it. Advisory
  severity only; a registry with design cards behaves exactly as before.
- **The per-unit token forecast is DROPPED. No plan-time predictor cleared the bar (CR0262).** The seed
  the forecast was built on - `max_cognitive`, the cognitive complexity of the files a unit touches -
  carries no signal: r = +0.03 against measured cost across 18 units. Both past recalibrations (5,000,
  then 600) were fitting a slope through noise, which is why the model over-forecast by 3.3x and then
  under-forecast by 0.55x and 0.39x on consecutive sprints. You cannot scale zero.

  A bar was set BEFORE measuring (leave-one-out r >= 0.50, beating `files_affected` alone, LOO ratio
  within 0.5x-2.0x for most units). **Nothing cleared it.** The best composite reached LOO r = 0.415 -
  and that number is generous, because its coefficients were refitted inside every fold and its feature
  set chosen with hindsight. Rather than ship a mediocre predictor, the per-unit estimate is gone.

  Two contaminants were found in the candidates that looked promising, and both matter. **`files_affected`
  flips sign within sprints** (+0.72, -0.34, +0.87; the pooled +0.44 is a between-sprint artefact) - a
  signal that reverses direction is not a predictor. And **the `Effort` field's apparent strength was
  partly a calendar**: scoring an undeclared Effort as zero inflates it, because the field only exists on
  later, larger units - the mere PRESENCE of the field scores r = +0.43. Treated honestly as missing, the
  human Effort value scores r = +0.35: still far better than the metric the code computes about itself,
  but not what a naive pooled correlation claimed.

  **Change-complexity is not derivable at plan time, and is not faked.** Before a change exists, every
  available complexity number is a property of the CONTAINER (file, coupling, churn), and none correlate.
  Substituting one is the bug being removed.

  The plan now leads with **batch history - what sprints ACTUALLY cost** - and quotes a flat measured rate
  (120,000 tokens per unit) with a wide band, saying plainly: read the history, not this number.

- **The router no longer reads an inapplicable signal as a zero (CR0262, absorbing BG0139).** A markdown
  file RESOLVES the code-complexity signal and yields no scored function - and that 0 is an absence, not a
  measurement. `complexity.assess()` now reports whether it was applicable at all; when nothing touched can
  carry a score, `code` and `risk` go MISSING, confidence drops, and the tier is bumped UP (the doctrine the
  module always documented and never reached). **CR0252 - a docs unit that cost 205,534 tokens - went from
  `14 / trivial / HIGH confidence` to `34 / low / LOW`.** Under routing it would have been sent to the
  smallest model, confidently. Code units are unchanged.

- **`appetite.minutes` / `appetite.units` of `0` now mean "inherit the capacity", not "unbounded"
  (CR0259).** A consuming project that left them at the default previously ran with no ceiling; it now
  inherits `capacity.minutes` (240) and `capacity.units` (8). This is a default-behaviour change, and
  it is the point of the CR - plan capacity and run appetite are one source with two consumers, and a
  run that silently had no breaker was the thing worth removing. The stop is clean, with a handoff, and
  the plan prints the ceiling and where it came from. Set the keys explicitly to choose your own.

- **The token forecast is calibrated against measured actuals for the first time (CR0257).**
  `TOKENS_PER_COGNITIVE` drops 5,000 -> 600; the 50,000 base stays (validated - the one
  complexity-0 unit measured 46,359). Six units delivered by instrumented subagents were measured
  end-to-end: the batch forecast was **1,285,000 against 384,278 actually spent - 3.3x over**. At 600
  it lands at 1.09x. The inflation was not harmless: a 10-unit batch was cut to 5 on the belief it
  was too big, when it was not. Two limits are pinned in tests so they cannot be quietly forgotten:
  this is a **hypothesis** fitted to six units (the next sprint is its falsification test - the value
  it replaces was never validated at all), and **complexity is a weak per-unit predictor**, so the
  forecast is a **batch** tool - two units of identical complexity cost 2.1x apart, because the
  complexity of the FILE is a poor proxy for the WORK done in it.

- **One archive writer, one layout (CR0248).** `reconcile.py` carried a second, CLI-reachable
  `archive` path that wrote a flat `<type>/archive/_index.md` with no live-index pointer, while
  `archive.py` wrote the per-release layout with one. Archiving via both split a type's terminal rows
  across two incompatible schemes, and the census survived either way, so nothing flagged the
  incoherence (LL0016). Reconcile's duplicate is removed - it now only READS the archive into the
  census; `archive.py` is the single writer. A guard test asserts the duplicate cannot silently
  return.

- **Per-type status vocabulary derives from one source (CR0249).** `artifact.SPEC` and
  `file_finding.TYPES` each re-hardcoded the statuses that `lib/sdlc_md.py` already declares, so a
  vocab change had to be made in three places or they drifted. Both now derive from `sdlc_md`, and a
  guard test fails if either creator re-hardcodes a divergent value. A pure refactor - no status
  added, removed or renamed.

### Fixed

- **`refine`'s SEEDED-Affects note no longer prints from the library (US0410 repair).** The note confirming a story's Affects was seeded from its parent was printed inside the `refine()` library call, so it leaked to the console under every passing test that refined a no-Affects story - 69 lines, which broke the green-suite noise ratchet. The note is now RETURNED (`result["seeded_notes"]`) and printed only by the CLI layer (`refine apply` / `refine add`), so the operator still sees it while the library stays silent.
- **A criterion that swallowed its own verifier is named at mint (US0381, EP0139, CR0381).** `--ac` pairs with `--verify` positionally, so writing the verifier inside the criterion as `criterion|pytest path::Node` used to be swallowed whole as prose - the command was rewritten into a code span and the artefact shipped with no `Verify:` line the runner could ever see. `artifact.py new` now warns by position, names where the verifier goes, and leaves an escaped `\|` alone. Advisory and positional: a correctly-paired `--ac`/`--verify` is untouched.
- **The TRD's census guard is anchored to the claim, so a stale count fails instead of reporting green (US0367, CR0302/CR0365).** The predecessor read the FIRST match of a count pattern anywhere in the file and compared it as a floor, so an exact claim that had rotted upward ("58 scripts", 67 present) satisfied `actual >= claimed` and passed on the very numbers it existed to catch. `doc_freshness.census_claims` now checks EVERY occurrence of a claim, not the first, and reads the comparison form off the claim's own wording - `60+ scripts` is a floor, `58 scripts` is exact - so a number written as exact is judged as exact, and a floor left 25% or more behind reality is reported stale too. No mtime and no "last verified" stamp is consulted: the verdict is computed from the measured value, so a stale number cannot buy a pass by sitting in a recently-touched or freshly stamped file. The census scan stops at a document's Revision History, which narrates the numbers it corrected rather than asserting them. A claim the document does not make is returned UNCHECKED and named in the report - a document whose counts were measured and matched is a different fact from one nobody looked at, and a silent green could not tell them apart.
- **`verify_ac run --story` accepts a story id (CR0308, EP0062).** The natural first
  invocation (`--story US0177`) resolves by id when no such path exists; a value that is
  neither a path nor a resolvable id errors naming both failed lookups. Existing path
  behaviour unchanged.
- **Closing-review fixes across the Sprint 1 engine changes.** The independent adversarial review caught seven defects that the per-story tests passed over: the `--goal design` forecast RELABELLED the marginal rate as UNMEASURED but still computed and printed the full build-rate tokens (now the marginal is genuinely dropped - rate is None and the units are unpriced); the token-forecast render swallowed built-not-closed units when the priced total was zero; a goal-review amendment naming a requesting seat that never reviewed the prior goal was accepted (now refused, since it carries nothing); `goal-verdict` accepted a whitespace-only note; `artifact retitle` could not match a v3/ULID id in the H1; a refine ungroomed mint glued its marker to the next heading (MD022); and the shell-hazard check skipped a flag value passed alongside a `--fields-file`. Each fix carries a value-asserting test (the reviews found several holes where a test asserted only a label).
- **`resolve_prose_fields` hazard-checks in the fail-safe direction (BG0298).** US0418's
  `prose_keys` argument named the CHECKED subset, so a caller that forgot to list a prose field
  would silently skip its shell-hazard check. It is inverted to `metadata_keys` (the fields that
  are NOT prose): everything not declared metadata stays checked, so a forgotten prose field is
  never silently skipped. Back-compatible - no `metadata_keys` still checks the whole set.
- **The two duplicate-detection entry points now agree on scope, not just algorithm (BG0297).**
  BG0294 unified the algorithm but the finding filer still scanned every artefact type while
  `artifact new <type>` scanned only the minted type, so a terminal cross-type near-match warned on
  one path and not the other. The filer now scopes to the finding's own type (a bug is compared to
  bugs), matching `artifact new` exactly; the type-agnostic form still scans every type.
- **The mutation test-file scan no longer descends into gitignored worktree copies (BG0296).**
  `_candidate_test_files` walked into `.claude/worktrees/agent-*/` (gitignored), padding the
  reference scan and `--suggest-test` covering command with dozens of stale duplicate test paths.
  It now filters gitignored paths out (one batched `git check-ignore`), rather than matching a path
  component named `worktrees` - which would reproduce the recorded scar of skipping the whole tree
  when run from inside a worktree. Best-effort: a git failure leaves the candidates unfiltered.
  (The original filing blamed guard-clause blindness; that was disproved - the tool mutates guards
  fine - and the bug was repointed to the real defect.)
- **`changelog.py compose` is dry-run by default (BG0295).** Compose is the release cut - it folds
  every `changelog.d/` fragment into [Unreleased] and DELETES them, consuming the whole pending
  set. Run out of habit while adding a single fragment it silently destroyed 115 others. It now
  reports what it would fold and touches nothing unless `--apply` is passed; the CLI names `--apply`
  so the footgun is disarmed at the surface an author types.
- **Duplicate detection has one implementation again (BG0294).** `file_finding.duplicate_candidates`
  used Jaccard over the open backlog while `artifact.duplicate_candidates` used containment over
  every artefact, so the repo answered "is this a duplicate?" two ways - and they disagreed on real
  data (the motivating pair scored 0.21 by Jaccard, missed, and 0.44 by containment, caught). The
  Jaccard scorer is deleted; both entry points now route through the one containment detector,
  terminal artefacts included.
- **A seeded acceptance criterion no longer repeats its own label or restates its heading as the `Then` (BG0291).** Where a request's criterion already opened with `AC1:`, the seed prepended a second label and produced `### AC1: AC1: ...`; the `Then` clause was the heading again, so the criterion stated its own name instead of an observable outcome - the vacuous criterion the verify DSL exists to refuse - while reading as authored work rather than work owed. The label is now stripped from the source before the seed adds its own, the `Then` is an explicit placeholder alongside Given/When and the Verify, and a criterion too long for a one-line heading is transcribed in full under its block so nothing is lost. A multi-story breakdown still seeds no story-level criteria at all: the epic carries them, because which criterion belongs to which slice is not derivable.
- **`validate` no longer refuses the ungroomed story `refine` just minted (BG0290).** `refine` marks an ungroomed story's acceptance criteria with a blockquote marker and `conformance` reads that as a legitimate pre-Ready state, but `validate`'s `no-ac` check skips blockquotes and reported the same bytes as having no acceptance criteria at all. Both guards run in the same pre-commit gate, so the refine that creates a backlog could not be committed and there was no groom-before-commit path - the story must exist to be groomed. The trigger is whether the REQUEST carries `- [ ]` criteria to seed from, so refining any accepted RFC (Design Options, no criteria) produced uncommittable stories. `validate` now reads the ungroomed test from its owner rather than holding a second copy of the rule. An acceptance-criteria section that is merely EMPTY declares nothing and is still an error.
- **Superseding a verdict retires the verdict, not the attribution, and a principal-authorised
  correction can restore independence (BG0284).** The emergency fix that made every superseded row
  count toward independence closed the two-role bypass but re-stranded the mis-filing it existed
  for: a verdict row wrongly naming a principal as reviewer could no longer be cleared. Supersession
  is now held to the sign-off's own rule - a mandatory `--boundary` and an authoriser who is neither
  the row's author nor an in-session worker on the unit (a reviewer on its evidence, or another
  verdict / sprint-review row). Only such a principal-authorised correction retires the attribution
  so the wrongly named principal can sign the unit off; every author-reachable one retires the
  verdict alone, so no blocked author can launder its own seat out of the gate. Re-checked at read
  time as a backstop against a hand-appended record.
- **A conflicted merge can be committed through the gate again (BG0281).** The commit-msg hook tests ran the hook in the OUTER repository, so while that repo was mid-merge - which happens whenever the pre-commit suite runs during a merge commit - they inherited its `MERGE_HEAD`, saw the hook's correct in-progress-operation early exit, and five tests failed. That made a conflicted merge un-committable without `--no-verify`. Each test now runs the hook in a hermetic fixture repo carrying a symlinked checker, so it reads the fixture's state, the refusal still executes (the isolation is not vacuous), and the intended mid-merge early exit is exercised deliberately.
- **Parallel delegation names the workspace, not only the files (BG0280).** A worktree isolates the TREE, not the scratchpad: agents sharing one temp directory overwrote each other's commit-message files between write and use, and a commit landed carrying a different agent's subject. `reference-delivery.md` and the agent-prompt template now state that any temp path must be namespaced per agent or kept inside its worktree, and that a unit changing the build tooling is coupled to the whole batch whatever its `Affects` says. Neither failure produces a merge conflict, which is the only outcome the file-disjointness check was built to predict.
- **The close now judges the state it leaves behind (BG0279).** The chain runs its gate while every unit still sits at Review, then `--apply-signoff` transitions them to Done - and conformance requires evidence at Done that Review does not. So a close could print `gate: ok` and still leave the tree red, and the next person to commit inherited a failure they had to prove was not theirs (three build agents did exactly that in one sprint). The sign-off tail now re-checks conformance AFTER the transitions, scoped to this run's own units, and names them with the remedy. Reported, never a refusal: the harm was silence, not the debt, and failing would strand a completed sign-off behind ceremony the sign-off never depended on.
- **The seat brief no longer describes the previous sprint (BG0277).** `goal-review brief` composed from the persisted `sprint-plan.json`, but the goal review it informs GATES `plan --write` - so on a new sprint the persisted plan is the previous run's by construction, and a seat was briefed on the wrong batch with nothing to warn it. The brief now takes the batch it is to describe (`--brief-worklist`) and composes from a dry plan of exactly that; without one it refuses to render a plan whose run has closed, naming it instead.
- **The ungroomed count sees the legacy scaffold, not only the new marker (BG0276).** `conformance` counted a story as ungroomed by the explicit marker `refine` writes today, so every story minted before that - carrying the bare `{{...}}` template scaffold - was invisible to it. The count reported ZERO ungroomed while 16 such stories sat in this workspace: confidently wrong in the safe direction. Both shapes now count, and a groomed story that merely quotes a placeholder in a real criterion still does not, so the false zero is not traded for a false alarm.
- **A successful close now refreshes the review anchor (BG0275).** Only the blocked `--file-and-close` path wrote `sdlc-studio/reviews/LATEST.md`, so a close that went WELL left the previous run's state standing - and the anchor a fresh context is instructed to read first went on claiming a sign-off was owed after it had landed. The close chain gained a `review-anchor` step that stamps this run's id, outcome, unit count and whether sign-off is owed or recorded, into a delimited block, leaving the hand-written narrative around it untouched.
- **`artifact retitle` is atomic-or-rolled-back, not a sequence of hopeful writes (BG0274).** The retitle advertised all-validate-then-write, and that guarantee held only on the refusal path: past validation the destination file, the unlink of the old name, the index row and each inbound-reference rewrite were independent unjournalled writes, so a fault partway through the loop left the artefact renamed, the index updated and the references half rewritten - the exact split-surface state validate-first exists to prevent. The write phase now journals the prior bytes of every file it will touch and restores them all if any single write raises, removing a destination that did not exist before rather than leaving a second copy of the artefact behind. The fault is reported as a refusal on the `write` surface, chained to the original error, and a rollback that cannot itself restore a file names that file instead of claiming a clean one.
- **`refine`'s `inherit:subset` is held to the same rules as bare `inherit`, and the keyword is matched in any case (BG0273).** The narrowed form returned its subset before the parent-declares-none check ran, so a story could "inherit" from a request that declares no `Affects` at all; it never checked the subset was WITHIN the parent's footprint, so `inherit:` could add a path the parent never declared and call it a narrowing; and the bare keyword was compared case-sensitively, so `INHERIT` fell through to the explicit path and minted a story whose declared `Affects` was the literal word - which the Affects parser reads as no paths, leaving the story unplannable. All three are closed: the keyword is lowered before matching, the declares-none refusal runs first for both forms, and every path a subset names must already be in the parent's `Affects`, judged by the one parser every writer uses (so a token it cannot read as a path is refused too).
- **`retro accuracy` reads the rung of the run the retro belongs to, not the run that happens to be open (BG0272).** `_run_rung` read the live run-state's `goal` unconditionally, and every new run re-stamps it - so re-reading an older retro after a newer run opened re-attributed the new run's rung to the old sprint. Because the rung gates the tokens-per-point rate, a design-rung sprint re-read under an open build run published the very rate the non-done rung exists to withhold, into the file the planner re-measures from. The rung now comes from the run record whose batch COVERS the retro's units - the live state first, then the archive newest-first - which is the coverage rule the elapsed and token reads already obey. A retro no recorded run covers still reads `done`, so the honest build case is not blanked by a lookup that found nothing.
- **A themed batch is no longer refused as unachievable (BG0270).** The goal-review gate folded two different seat answers into one blocking predicate, so `one_increment = no` - the honest classification of a themed batch (a tooling sweep, a bug-fix clearance) - refused the plan and, worse, reported those seats as having "judged it NOT achievable" when they had judged the opposite. `achievable = no` now blocks alone; `one_increment = no` is surfaced as a THEMED BATCH note the operator reads, so separating the two loses no information and no output states a verdict the seats did not give.
- **A refused plan leaves nothing behind (BG0268).** `sprint plan --write` wrote the forecast record and `sprint-plan.json` BEFORE calling `open_run`, so a batch `open_run` refused - a concurrent writer opening a run between the pre-check and the open - left both artefacts on the losing side of the race, while `run-state.json`'s own byte-identical guarantee held. `open_run` is the authority on whether a plan may proceed, so nothing the plan produces is persisted until it says yes; the sibling artefacts now match the guarantee run-state already gave.
- **A repair-plan verdict carrying no findings-hash no longer satisfies the pin check by omission (BG0267).** `plan_reviewed` guarded the pin with `if m and m.group(1) != current`, so a verdict with no `findings-hash=` token short-circuited past it and was reported as "pinned to the current findings" while nothing pinned it to anything. The untokened case now takes an explicit branch and is refused, naming the missing token and how to re-pin the verdict. Unreachable through `review_repair_plan`, which always writes the token - the hole was open to a verdict recorded straight through `critic record --phase plan-review` or hand-edited into the log, which is exactly what the pin exists to catch.
- **A second `Verify:` line in one acceptance criterion is refused instead of silently dropped (BG0265).** `parse_story` executes only the first and read the rest as ordinary bullets, so a stacked verifier was a sentence that looked like a check. Six sat in this workspace having never run, four of them on stories at Done and two counted inside a sprint's published claim of 84 criteria verified. The parser now records them, `verify_ac lint` refuses them while a story is still being authored and names each dropped expression, and a live-workspace census goes red if another appears. All six have been split into their own criteria and re-run - and all six pass, so that published claim was lucky rather than false.
- **A verifier that only reads prose is refused while a story is still being authored (BG0264).** `verify_ac lint` now REFUSES a `grep` or `file` verifier whose every target is a markdown file, on a story at Draft or Ready, and exits non-zero. This is the shape that passed four US0310 acceptance criteria against prose asserting their opposite: the author writes the sentence and the search for it in one sitting, so the check is true of the line just written and silent about the behaviour. A criterion genuinely about a document says `manual`, which puts it in the manual count where a reader can weigh it. Past Draft/Ready the refusal lifts, so linting over shipped history still runs.
- **A verifier that only reads prose is refused, and the guard no longer tries to enumerate what the runner reads (BG0264, BG0266).** Four review rounds defeated four enumerating versions in turn - target tokens as written, an invented flag split, a non-recursive drop this DSL never does, and a walk that trusted `rg --files` to be what rg reads. The burden is now inverted: a `grep`/`file` verifier is refused unless a readable, non-symlinked, non-markdown file it actually reads can be pointed at, so every uncertainty refuses rather than allows. This closes all nine known escape forms, and closes BG0266 (`file <directory>`, which runs `test -e` and passes forever) without a separate rule.
- **The goal review keeps its rounds, so a goal rewritten after a REJECT no longer reads as a first-time approval (BG0263).** `goal-review record` held one object and the second review overwrote the first. Rounds now accumulate (as the sprint review's `review_rounds` does), keyed by the goal each round judged; the gate still reads the latest round, and the round count reaches the run state so the close can say how many rounds the goal took to agree.
- **A seat verdict that judges the Sprint Goal NOT achievable now stops the plan (BG0262).** The goal-review gate was a presence test - any non-empty `achievable` string discharged it, so "no" and "yes" were interchangeable and the verdict's content was never read. `achievable` and `one_increment` are now parsed against a small vocabulary, and a negative verdict refuses `sprint plan` unless the operator records an explicit `--override-goal-review "<reason>"`, which is stamped on the run so the close judges the outcome against what the seats objected to.
- **The state anchor's two load-bearing claims are checked against the run, and the review
  ledger cannot be contradicted at the moment it is written (BG0261).** `doc_freshness` counted
  version, test count, disclosure count and length while LATEST.md said the run was NOT closed
  and a sign-off owed over a closed run, and narrated three adversarial rounds beside a ledger of
  six. It now reports a `signoff-drift` when the anchor calls a sign-off or closure outstanding
  once the run carries an end and `close_owed` reports none owed, and a `round-count-drift` when
  the round count it narrates differs from `len(review_rounds)` - neither satisfiable by editing
  the prose. `run_state` refuses the same contradictions at record time: a goal-verdict note
  naming a round count the ledger does not carry (the count is now derived onto the record's
  `rounds` field, not restated), a review round recorded against a run that already carries
  `ended_at`, and a reviewer label naming a round number other than the index it lands at.
- **Three doc-invariant claims made into values the tests compute, and a redundant probe battery pinned (BG0260).** Which THE BOUND escapes carry a fixture is now derived by enumerating the fixture map and comparing against the items THE BOUND names, so the false docstring claim that item 8 was the sole escape without one (items 1 to 3 lack one too) cannot return. The closing disclaimer a rewrite had deleted is restored, and a cross-reference test proves item 6's "the closing disclaimer below" resolves to a block that exists. `mutation.py`'s comment stops listing `*.` as a whole-tree glob (`fnmatch` matches it against none of the probes): example globs are now derived from the probe battery by `everything_glob_examples`, so a spelling that does not match every probe cannot be written. The probe battery is pinned wide: a prefix glob like `a*` is not announced as the whole tree, and shrinking the battery to one probe goes red.
- **`window open`'s whole-tree reason reports the evidence the probe produced, so an inverted clause is caught (BG0259).** The clause named one static cause per branch, and a test could only check that the word `glob` appeared - which survives inside its own denial: rewriting the glob branch to say the OPPOSITE while keeping `glob` left all six window-message tests green. The reason now enumerates the probes the matcher accepted, derived from a single `WINDOW_PROBES` battery, so the sentence varies with its input and a per-claim test drives the reason and the matcher over the same claim and asserts they agree. The battery gains a digit-leading probe so `[a-zA-Z.]*`, which matches every letter-or-dot probe but no path beginning with a digit, is no longer announced as the whole tree while the matcher lets such a path proceed.
- **The docs single-writer checker discloses its verdict by running, not by a hand-maintained escape list (BG0258).** THE BOUND enumerated escape shapes by hand and was wrong at three, four, five, six and seven, each round finding an escape the previous count denied, because the boundary is emergent from three interacting lists and no human can enumerate that reliably. `explain_sentence` now answers "would this sentence be caught" from the mechanism itself - which axis selected it, or that none did and which topic group missed; whether an enumerated asserting word was present; which cue set the polarity - and `_polarity` is expressed on top of it so guard and disclosure share one parse. `generate_escape_corpus` derives the escape corpus from the axes and their vocabulary rather than from a typed list, so a widened or added axis grows the corpus with no list to update. The numbered enumeration is kept only as the historical record of what was found by hand, no longer presented as a boundary. This does not make the scan complete; it makes its incompleteness derived.
- **A retro Batch field written as an id RANGE is refused instead of publishing a velocity row orders of magnitude wrong (BG0257).** The parser expands no ranges, so `BG0247-BG0256` matched only its endpoints and a whole-sprint token numerator landed over a partial points denominator. The parsed Batch is now cross-checked against the retro's own `Delivered: N / M` header and a disagreement refuses the accuracy run - naming both counts and the ids that parsed, and saying to name the units individually - before `record_velocity` writes. A refusal adds no row and disturbs no existing one; a fully-parsed Batch records as before.
- **A stamped-green acceptance criterion whose verifier selects nothing reads STALE, not green (BG0256).** A recorded pass went green for two days against a test that did not exist, because freshness compares the acceptance-criterion text and the text had not changed. `verify_ac` now resolves a stamped selector by collection rather than execution, so the check costs an import and no test body; `conformance` stops counting a Done story verified while any stamp rests on a dead pointer; and `verify_ac stamps` exposes the condition per story with a non-zero exit, naming the story, the criterion and the selector. A selector that cannot be collected at all is reported unanswerable rather than dead.
- **The stamp-resolution check collects each test file once, not once per criterion (BG0256).** Baking the per-criterion collection probe into conformance made it spawn `pytest --collect-only` for every stamped acceptance criterion across the workspace on every commit, turning an 8-second gate into 81. The collected node list is now cached per test file and every selector shape - exact node, class prefix, `-k` boolean - is resolved in-process against it.
- **`rfc decide` reads the real workstreams and stops re-inviting settled decisions (BG0177).**
  ws now counts the RFC's linked children (the same Decomposed-into/Parent authority the
  derivation gate uses), with the Workstream table as fallback; an RFC whose every decision
  row is resolved prints DECIDED (awaiting delivery), never READY-for-decision.
- **Repairs from RUN-01KY3MFX's SECOND review round, which rejected the first repair.** Five of
  the eleven round-1 findings were genuinely closed; three had been over-claimed and three had
  moved rather than gone. `window open` printed that commits would be refused when the guard had
  just been made path-scoped. The gate and the hook agreed on claim PATTERNS - all the agreement
  test compared - while diverging on record NORMALISATION, so a record with no owner made the
  hook say proceed and the gate say fail in one run; both now share one record-level
  normalisation and the test compares records. A `..` traversal claim matched nothing and so
  failed open; traversal is now resolved at open time and an unresolvable claim claims the whole
  tree. `close_window` picked the first record by sort order, so a holder could not close their
  own window and a mutation run could strand itself; it is owner-selected. The sprint report
  preferred the live run unconditionally, so a partial one-unit overlap beat a full archived
  match; it now scores by coverage. The documentation checker claimed negated prose failed
  structurally on its required half - false, since a contradiction added BESIDE the required
  sentence passed; it now carries a per-sentence polarity scan, and what it still cannot detect
  is written down rather than implied. The engagement floor's unreadable-index refusal was
  reached by no test at all: the fix for the false-clean finding was itself an unpinned branch
  reading as coverage, and its own Resolution called it mutation-proven.

- **Repairs from RUN-01KY3MFX's closing review (three independent instances, all REJECT).** A
  velocity row's estimator class is now compared by the PARAMETERS it takes rather than the
  VALUES they were measured at, so re-measuring the rate no longer reclassifies history and empty
  the whole-sprint excess. A refused velocity record carries its reason on every rate source, not
  only the seed. The sprint report joins the mutation series to the run being reported, so a
  sprint that ran none is named rather than given the previous sprint's cost. The whole-sprint
  excess now delegates coverage to the predicate the record already obeys, so a per-unit build sum
  is no longer published under a whole-sprint heading. The idle deduction is clamped to its
  intersection with the measured window, because a wait recorded after a run closed was being
  subtracted from a span that never contained it. The gate's window lane judges STAGED PATHS
  rather than the record's existence, so a declared window no longer freezes every commit while
  the hook says it merely scopes staging. Window records are discovered through one reader over
  both spellings; a claim the matcher cannot interpret, or an absolute one, now claims the whole
  tree instead of nothing. An `equivalent` mutant no longer counts as mutation coverage - it is
  evidence about the mutant, not about the tests. An unreadable staged index refuses instead of
  printing a clean.

- **`quality.epic_requires_test_spec` is now read by the code that documents it (BG0250).** Four
  documentation surfaces described it as the caller's opt-out and no Python read it, so a project
  setting it in good faith got no effect and no warning. The key is read, the default is
  unchanged, a non-boolean warns and falls back to enforcing, and the findings stay the findings
  whether or not enforcement is on.

- **The engagement floor can see the violation its own gating commit creates (BG0251).**
  "Shipped" was derived from `git log --grep`, so a unit no commit had yet mentioned was
  invisible and the gate green-lit commits that were non-compliant the instant they existed. The
  floor now folds the staged index into its file-count signal and the hook runs a `floor-pending`
  lane. The residual case - a unit named ONLY in the commit message - is NOT closed and is pinned
  by a test saying so, because a pre-commit hook is not given the message it is gating.

- **A run id is unique by construction, not by luck (BG0253).** `short_ulid` is six timestamp
  characters plus two random, so two consecutive mints collided about once in 1,024 and the
  commit gate failed at random. Run ids are now collision-checked against archived runs and the
  suffix extended on a persistent clash. The old test would also have passed a generator
  returning a constant 999 times in 1,000; it is now driven with exactly that.

- **The velocity Estimate column publishes the forecast that was recorded (BG0249).** It was a
  sum over RATED units, so an interactive sprint that rates none published 0 - an absence
  rendered as a plan-time estimate of zero, in 12 of 17 live rows, beside a real forecast that
  had in fact been recorded.

- **The WSJF advisory reports coverage, not age (BG0247).** With no seat score covering the batch
  it printed a staleness warning, implying scores were in use and merely ageing when none
  applied. It now leads with coverage. The bug's own premise was corrected rather than
  implemented: the ordering was never "priority instead of WSJF" - Cost of Delay is derived from
  Priority and the ranking is still CoD over points - the `priority fallback` wording caused the
  misreading and has been rewritten.

- **`init` no longer ships a literal placeholder in every new project's AGENTS.md (BG0255).** The
  filler substituted lowercase keys while the template carried an uppercase project-name
  placeholder, so the name was never filled in the first file a project adopting the skill reads.
  Fixed in the FILLER, case-insensitively, so a future template reaching for the natural
  uppercase form is not trapped, plus a postcondition that a known placeholder surviving a seed
  raises rather than ships.

- **The velocity history records where a token figure CAME FROM, and a reason survives the row it
  explains.** Three defects found by the closing review, all in the reporting the previous entries
  describe. (1) The `Note` column added for BG0244 was regenerated unconditionally, so re-recording
  a row destroyed its own reason - the fix had rescued the value and left the reason with exactly
  the behaviour it was filed to end. A recorded reason now survives its own row's rewrite, while a
  cell that has since been FILLED still drops it, because a reason explains a blank. (2) After the
  documented `--tokens 0` retraction the note claimed no total had been supplied, which the code
  knew to be untrue; it now states the cell is blank by instruction rather than for want of a look,
  and the retraction outranks preservation so neither fix swallows the other. (3) A new `Source`
  column records `per-unit`, `harness` or `supplied`, so a hand-typed total can no longer pass as a
  measured one under "what sprints ACTUALLY cost" - the same claim-versus-measurement distinction
  the mutation ledger already draws. Re-using an already-recorded actual keeps its original source,
  so a close re-run cannot relabel a capture as a claim. Historical rows carry no Source and are
  given none; the table is parsed by column name precisely so a column can be added without
  rewriting a row.

- **A self-reported mutation SURVIVOR is reported instead of quietly improving the gate.** Survivors
  reached the lane only through the mutation report, which `register` does not write, so registering
  a survived verdict moved a file from "no evidence" to "covered" while the survivor itself was
  never shown - reporting a failure made the gate QUIETER than reporting nothing, and the incentive
  ran backwards. The lane now names self-reported survivors and holds its finding count, while a
  registered kill still reads as evidence gained. `register` prints the finding as it records it.
  Measured-entry survivors are deliberately still left to the report lane, and that is now pinned
  by a test rather than only asserted in a comment.

- **The mutation ledger is bounded on both axes it can grow along.** `LEDGER_LIMIT` bounded the
  entry count while a per-entry mutant list grew without limit, so the docstring claiming "one
  truncation point, so every writer meets the same limit" was untrue of `register`, the writer it
  named. Measured before fixing: 500 registrations on unchanged content produced one entry of 501
  mutants and 76,097 bytes, with the existing limit never firing. A per-entry `MUTANT_LIMIT` now
  bounds the list and announces what it drops, while summary counts stay exact so the recorded
  tally remains true. Known residue: eviction is by age, not severity, so a survivor's description
  can be dropped while its count and the gate's report of it remain correct.

- **The plan's cost history includes interactive sprints instead of showing only the oldest data
  (BG0246).** `batch_history` gated on a `measured` column counting PER-UNIT telemetry, which an
  interactive sprint never has, so every one was dropped. The block titled "what sprints ACTUALLY
  cost - the real planning input" listed RETRO0025 to RETRO0028 at 128k-188k per unit and silently
  omitted RETRO0060 (2,390,624 over 9 units, 265,625 per unit) and RETRO0061. Planning read
  systematically cheaper than reality, from the oldest rows in the file, presented as current.
  Interactive sprints now contribute, with per-unit derived from the total, and **every row is
  labelled `per-unit` or `sprint-level`** so the two kinds of evidence are never confused. The
  accepted cost is printed beside them rather than buried in a decision record: a sprint-level row
  hides the variance between its units, so one unit may have taken far more than the figure shown.

- **Per-unit mutation evidence can be recorded by the practice that produces it (BG0245).** BG0238
  built a ledger that accumulates mutation evidence, but only `mutation.py` could write to it,
  while the practice is a builder hand-applying a mutant to the code a new test pins. A sprint
  that followed policy exactly therefore read 0/N: 75 mutants were applied in the previous run and
  coverage reported 0/4. A lane that reads red when the policy WAS followed gets ignored, which is
  worse than a lane that is merely absent. `mutation.py register` now records an already-applied
  mutant against the target's content hash. Crucially the ledger does not pretend a claim is a
  measurement: every entry carries its **provenance**, registered entries are reported as
  SELF-REPORTED by the gate lane, the two kinds are separate records so neither erases the other,
  and verdicts only a runner can observe (`error`, `unviable`) are refused from a self-report.

- **The velocity row publishes `-` rather than `0` when nothing was measured (BG0244).** `Actual
  (tokens)` was a sum over RATED units, which is 0 when none are rated - the normal case for an
  interactive sprint - so an absence was published as a measurement of zero, in the series the
  estimator reads. The `Tokens/pt` cell in the same row already refused, so one row made two
  contradictory statements. Three rows had been hand-corrected, and the third correction was then
  overwritten automatically by `apply-signoff` rewriting the same row, so the workaround was
  defeated by the ceremony that produced the error. The writer now clears a falsy actual, a `Note`
  column carries the not-attributable reason, and a reader-side guard means a historical `0` is
  never consumed as a data point: 7 rows printed `actual= 0` before and 0 do now.

- **A token delta can no longer be stamped on an unrelated retro (BG0243).** `run_attributed_tokens`
  read whatever run was open and `cmd_accuracy` never passed the retro id, so recording an older
  retro after a later `sprint plan --write` would have attributed the new run's spend to it. The
  retro id is now a required positional argument, so no caller can reach the capture without
  declaring what it is for, and the batch-coverage rule was EXTRACTED from the elapsed path rather
  than copied, so the two cannot drift into disagreeing about what a covering batch is.

- **35 unconfined git call sites in the test suite are confined (BG0242).** BG0230 confined the
  shared helper but 35 call sites across 8 modules never reached it, and `tools/skill-tests.sh`
  scrubbed for them only when the suite ran through that script - not under the plain `unittest
  discover` an agent typically uses. Containment was proven rather than asserted: a fresh victim
  repository per module, with its worktree deliberately diverging from its index, showed **5 of 8
  modules damaging the victim at HEAD** - three wiping its uncommitted state outright, reproducing
  the incident this class has now caused twice - and none afterwards. The ratchet is no longer a
  ceiling that may only fall but a zero-tolerance sweep, with an alias-aware detector: a naive
  `subprocess.run(["git"` grep found only 24 of the 35, because one module imports `subprocess as
  _sp`.

- **A test spec with no AC Coverage Matrix is a finding, not a clean result (BG0241).** BG0229
  fixed the absent FILE; this is the next vacuity in - a spec present, readable and valid UTF-8
  but carrying no matrix at all still reported clean at exit 0, indistinguishable from a matrix
  with nothing outstanding. It now exits 1, distinct from a complete matrix at 0 and an absent
  file at 2. The meaning was decided before the code: of the three readings, only "deliberately
  not applicable" is clean, and nothing absent can evidence a decision. The migration cost was
  measured before the default changed rather than discovered afterwards: 0 of 2 specs in this
  repo, and 30 of 178 across the workspaces on this machine, concentrated in four projects.

- **`lessons.py` and `loop_guard.py` write under the root they were given (BG0240).**
  `lessons summary --out` anchored a relative path on the cwd, and `loop_guard`'s state path
  honoured a named `--root` but not the discovery half, so both wrote strays beside the cwd and
  exited 0 while printing a relative path that hid where the file went. Both now use the same
  resolver `repo_map` adopted rather than a third idiom, and print the resolved path. A third
  instance was found in the same file and fixed with them: `cmd_budget` read run-state from the
  unresolved root, so fixing only the two filed cases would have left `record` writing under the
  discovered root while `budget` read the cwd.

- **Per-unit mutation evidence survives to the close (BG0238).** The mutation report was a single
  blob, last-write-wins, whose staleness was keyed on a whole-repo `git_rev`. That shape assumes
  one run per sprint at the close, so running mutation per unit during the build - which is what
  the lessons say to do - meant each run overwrote the last and every one went stale the moment
  the next unit committed. By the close, nothing from the sprint survived: 12 mutants died in
  RUN-01KY1WCR and not one existed outside prose, while the lane reported STALE and PASS and
  nothing said the claim was unbacked. Evidence now accumulates in a bounded ledger keyed on each
  target's CONTENT HASH rather than a repo-wide rev, so a file's evidence stays valid across later
  commits that touch other files - which is exactly what makes per-unit runs reach the close. The
  gate lane judges COVERAGE of the changed surface instead of freshness of one blob: hash matches
  is covered, hash differs is stale, no entry is uncovered, and it states the fraction and names
  the gaps. Evidence is read from the LEDGER alone, because the ledger is the only surface that
  applies the verdict rule. The report's `target_hashes` is a freshness stamp over the files the
  run was pointed at, written before any verdict exists, so a first cut that overlaid it as
  evidence had a refused run report its target covered while saying "nothing was proven" in the
  same sentence, and a run stopped by the cost ceiling report 3/3 files covered having mutated
  one. The whole-report checks remain as the degraded fallback, and are now reachable rather than
  merely present: with no per-file evidence the lane checks the report's own target hashes, then
  the whole-blob rev, and says STALE. Where per-file evidence does exist the aggregate is still
  attributed - a summary written before the current HEAD prints whose run it came from, since
  coverage is per file and survivor counts are per run. Advisory throughout, per RFC0048 D3. The
  ledger is bounded at 200 entries with a cumulative dropped count and a printed note, because
  silent truncation reads as "we kept everything".

- **A sprint's token cost is its own, not the whole session's (BG0236).** The close captured the
  harness meter's absolute reading, which is cumulative per SESSION. Close two sprints in one
  session and the second recorded everything the first had spent: RETRO0062 published 341,000
  tokens per point and RETRO0063 published 472,691, against a measured rate near 25,000. Both had
  to be blanked by hand after the fact, which is the argument for the fix rather than the
  workaround - the honest value was only recorded when somebody noticed, and the failure mode is a
  published number that reads as measured. `open_run` now stamps a session-token baseline when a
  run is minted (a re-plan leaves it alone), and the close captures the DELTA. Crucially there is
  no fallback: a run with no baseline, or closed from a different session, reports
  **not-attributable** rather than a number, because a plausible figure that is not this sprint's
  cost is worse than an absent one. Dogfooded honestly - this very run was opened before the fix
  existed, carries no baseline, and will report not-attributable at its own close rather than have
  one retrofitted.

- **A test fixture's git call can no longer be redirected at the parent repository (BG0230).**
  `gitutil.git_env` passed the ambient environment through unfiltered, so `GIT_DIR`,
  `GIT_WORK_TREE` and `GIT_INDEX_FILE` decided which repository a fixture acted on rather than its
  `cwd`. Reproduced with a purpose-built victim repo: a fixture's `git add -A` moved the victim
  from 3 tracked files to 2 and left the fixture's own index empty. This is the class the repo has
  already suffered twice, most recently inside RUN-01KY1WCR where an unscrubbed fixture wrote its
  own tree into the real repo's pending index under `git commit -a`. Two escape routes are closed,
  because closing one leaves the other open: the repo-locating variables are dropped so git
  resolves by discovery from `cwd`, and discovery itself is fenced with `GIT_CEILING_DIRECTORIES`
  so a fixture under a `TMPDIR` that sits inside a checkout cannot walk up into it. Rather than
  pinning today's copies of the scrub list, a sweep now fails on any code file naming two or more
  of those variables that is not registered - so a fifth copy cannot arrive unpinned. The
  remaining hole is bounded and declared rather than hidden: 35 bare `subprocess` git calls in 8
  modules bypass the helper entirely, frozen as a ratchet and filed as BG0242.

- **`refine`'s heading truncation and epic T-shirt derivation are pinned (BG0233).** Both were
  correct and neither was covered: inverting the truncation guard and stubbing the T-shirt mapper
  to return nothing both left the suite green. Tests only, no behaviour change. Every band edge is
  now pinned (0/1/3, 4/8, 9/20, 21/100) and the truncation boundary is pinned from both sides, so
  the two mutants that survived are each killed several times over.

- **A missing test-spec is refused instead of read as an empty one (BG0229).** `ts-check` routed
  its read through a helper that defaults to `""` on any `OSError`, so an absent file - or a
  directory - produced zero matrix rows and reported a clean matrix at exit 0. A typo'd `--spec`
  therefore passed as green, which is silence read as assertion integrity. An absent spec now
  raises from `ts_check` itself, so no caller can be handed `[]` for a spec that is not there;
  the command names the resolved path on stderr and exits **2**, distinct from exit 1 (a matrix
  with findings) and from exit 0. The two read failures stay apart on purpose: a spec that is
  present but not valid UTF-8 returns a finding naming the file rather than raising, so a
  tree-walking scanner still survives one wreck. A present-but-empty file is readable and remains
  a clean result rather than a refusal.

- **`repo map` writes its map under the root it was given (BG0228).** `build` resolved `--out`
  against the current directory and never applied `--root`, then printed a relative path that hid
  where the file had gone; `query` and `stats` had the same hole on `--map`. Run from anywhere but
  the root, the map was written beside the cwd and the later read looked in a different place
  again. All three now resolve through the same resolver rather than a second idiom - a named root
  taken verbatim, a default `.` discovered upward, a relative `--out`/`--map` anchored on the
  result and an absolute one honoured as given - and `build` prints the resolved path. The sweep
  this fix required found the same shape in two more scripts, filed as BG0240, and the missing
  convention behind all three as CR0383. **A behaviour change wider than the written scope**,
  surfaced by the closing review: adopting the shared resolver also changed what `build` INDEXES,
  not only where it writes. With the default `--root .` from a subdirectory it now discovers the
  project root upward and indexes the whole project, where before it indexed the current
  directory. That is the convention CR0383 argues for and it is deliberate, but it is a change of
  input surface rather than of output path, so it is recorded here instead of being left for
  somebody to discover from a differently-sized map.

- **`critic._read_rows` no longer returns a table's header as a data row (BG0227).** The header
  skip matched only a first cell reading `Unit`, so any table whose first column is named
  something else yielded its own header as a row of data. The code fix had already landed with
  US0261/US0262; what was missing was the pin, and the property survived only as a side effect of
  one length assertion in an unrelated test. Now pinned directly, including a near-miss guard: a
  data row whose first cell alone reads `Unit` is kept, which a first-column-name match would have
  discarded.

- **Two review-loop properties are pinned behaviourally rather than symbolically (BG0235).** The
  review ceiling was asserted only as a symbol, so changing its value broke nothing, and the
  neutrality check was asserted in aggregate, so a single class silently ceasing to fire still
  passed. The ceiling is now bracketed two-sided through the guard itself (two recorded rounds
  return, three raise, with no explicit ceiling passed), and each neutrality class is driven by
  text carrying only that class and asserted against the exact violation list, so an over-firing
  class fails too. Four mutants that previously survived - both ceiling values and each of the
  class regexes - are now each killed by a distinct test.

- **The gate budget ignores a commit whose suite only got invoked (BG0239).** The hook set
  `suites_ran` once the lane was started, not once it had run its scope, so a commit where a test
  module failed to import recorded a short run as this commit's cost: 73s against a 99s baseline,
  reported as `-26% since`. A broken suite read as an improvement, and at the same magnitude as
  the ratchet the lane exists to expose. `gate_timing scope` now decides whether a run may enter
  the series, from two signals and explicitly NOT from its duration - judging duration by duration
  history is circular, and would have rejected the genuine 196.7s -> 99s improvement as
  implausible. The signals are a module that failed to import (a fact, needing no history, and the
  filed reproduction exactly) and the test count against the historic peak, floor 80% - generous,
  because tests are legitimately deleted and a floor that fires on real deletions gets ignored. A
  suite that ran everything and FAILED is still recorded: the cost was paid whatever the verdict,
  and only "barely ran" is excluded. The count is recorded even when the run is refused, or one
  truncated run would poison the series permanently. The skip is printed, never silent.

- **A dev-repo-only gate test no longer fails from an installed copy, and the rule has one home
  (BG0237).** `GateRealWrapperTests` resolves its root as `parents[5]`, which from an installed
  copy is the home directory: `two_backlog_enforced` returns False, the derivable-request sweep
  never runs, and two tests failed on a count of 0. A consumer saw 2 failures in 3,409 with
  nothing saying the cause was location rather than code. Both tests already stubbed two of their
  three live dependencies, so the fix stubs the third rather than adding a fourth hand-copied skip
  guard - an installed copy now gains that coverage instead of skipping it. The dev-repo guard
  moved INTO the one helper that reaches the real gate and the two call-site copies were deleted,
  so the rule has a single home rather than four that drift. A class-wide sweep runs every other
  test in the class under installed-copy conditions and demands each pass or skip, so a future
  test that reads live state is caught however it is spelled.

- **A run stopped mid-flight can still take the bounded exit (BG0223).** The re-run guard on
  `--file-and-close` gated on the bare outcome string, so a run stamped `budget-spent` or
  `stopped` - `loop_guard`'s own recommended flow, and states the close path documents as
  routinely completing their ceremony afterwards - was refused with "already closed,
  re-running would duplicate the filing". That run has filed nothing, so the message was false
  on both counts and the bounded exit was unavailable to one of its natural customers. The
  refusal now gates on a COMPLETED close (`goal-reached` / `closed-outstanding`); duplication
  itself is caught by the filed-blockers record, which is the fact that proves a filing
  happened rather than a string that implies it.

- **The suite lanes run in a git environment of their own, not the caller's (BG0222).**
  `git commit -a` hands the pre-commit hook `GIT_INDEX_FILE` and friends; the suite lanes
  inherited them, so every test that builds a throwaway repo and shells out to git acted on
  the OUTER repo instead. The same commit passed when staged and failed under `-a`, so it read
  as flaky tests rather than an environment leak. `tools/skill-tests.sh` now clears the
  repo-locating variables before invoking the suites, and deliberately leaves the fixtures' own
  identity and config variables alone - the scrub has an upper bound as well as a lower one,
  and both are pinned. This is defence at the caller; `BG0230` covers the wider case, that the
  fixtures have no containment of their own and so remain reachable from any other polluted
  environment.

- **A path option is resolved against the project root, not the current directory (BG0220).**
  `verify_ac`'s `--root` defaulted to `"."`, so "the root" meant "wherever you happen to be":
  a run from a subdirectory wrote its report and history into a stray `sdlc-studio/.local`
  beside the cwd, printed that path, and exited 0. The sweep found the same hole on five more
  surfaces, including a second write (`scaffold --out`) and a read that contradicted the write
  (`run --root X` wrote to X, `--root X report` said "no report"). Every site now routes
  through one resolver: a named root is honoured verbatim, and only the family default `"."`
  triggers an upward search for a marker-bearing workspace - a bare "directory called
  sdlc-studio" check would stop at `.claude/skills` and call the skill's own source a project.
  `repo_map.py` carries the identical defect and is filed as BG0228 rather than fixed here.

- **The close-owed detector reads a Batch line's parenthesised units (BG0225).** Coverage was
  read through `retro.batch_ids`, whose deliberate `(...)` strip is correct for its own
  question (which units carry a plan-time forecast) and wrong for this one: a Batch line of
  `BG0219, EP0090 (US0276)` left US0276 reported as owed by the very retro naming it. Coverage
  now reads the Batch line through the canonical `sdlc_md.ID_SEARCH_RE` instead of a private
  third regex, which also fixes a latent miss - the private pattern pinned the digit run at
  exactly four, so a five-digit id matched nothing at all. Only a leaf unit earns coverage from
  inside a parenthetical; an epic there is provenance, and crediting it would forgive a
  childless epic no close had derived.

- **A velocity row's retro id is normalised at both the write and the read (BG0226).**
  `record_velocity` wrote the id verbatim while `velocity_history` matched an undashed form
  only, so a `RETRO-0060` close minted a row no consumer could see. The reader is the more
  important half: every consumer goes through it, so tolerating both forms makes rows already
  on disk visible and lets a legacy row self-heal on the next upsert.

- **An explicit `--tokens 0` clears a recorded actual (BG0224).** Supplied-ness was inferred
  from the value, so an absent flag and an explicit zero were indistinguishable and the
  documented override silently kept the wrong number. It now travels as its own sentinel:
  absent still preserves the recorded value, zero clears it.

- **`validate`'s placeholder warning uses the severity spelling the counters count (BG0217).**
  The placeholder check emitted `warn` where every other check emitted `warning` and both
  summary counters counted only `warning`, so a scaffold's slots printed as warnings and then
  reported `warnings=0`. The vocabulary is now closed, so a third spelling cannot be
  introduced. No gating change: every consumer filters on `error`.

- **`refine --into` no longer appends a duplicate epic-level AC heading (BG0221).** A second
  refine against the same batch epic inserted a fresh `## Acceptance Criteria (Epic Level)`
  under the one already there - a duplicate sibling heading that fails the repo's own
  markdownlint MD024, so `refine`'s output blocked the commit shipping it. Criteria now merge
  under the existing heading, attributed to their originating request, with the carried-from
  note lifted so it stays last and appears once.

- **`critic`'s table reader no longer returns the markdown header as data (BG0227).** The
  header skip was hardcoded to one table's first-column literal, so any table led by a
  different column returned its own header row as a record. Latent rather than live - both
  callers filter by unit id - but it is the list the per-round cost accumulation iterates. The
  header is now identified by matching the whole cell tuple against the declared columns.

- **An interactive close captures its own token actuals (CR0350: US0279).** The close runs
  `retro accuracy --tokens-from-harness`, which sums the current session's harness transcript
  usage (input + output + cache creation; cache reads excluded) and records the total on the
  velocity row beside the delivered points - closing estimate-versus-actual for interactive
  sprints after five consecutive retros of "not-yet-captured". A failed capture states plainly
  why; an already-recorded actual is reused, never re-stamped from a later session; an explicit
  `--tokens N` stays the operator override. Only the close passes the flag: a plain re-read of
  an old retro never attributes today's session to a past sprint.
- **The velocity record states delivered points even when nothing was forecast (BG0218).**
  VELOCITY.md's Points column is now the delivered-points series, read from the units' own
  artefacts (plan-recorded sum as fallback), so an interactive build-first sprint records its
  point total instead of `-`. The ratio columns keep their forecast gate, and the derived
  tokens-per-point (row cell and `measured_rate`) now requires a FULLY measured sprint - a
  partial token sum is no longer divided by the full points. RETRO0058's row is backfilled
  (Points 14) as the live proof.
- **The mutation gate names what its survivors were measured against (CR0363: US0277,
  US0278).** The report and text output now carry the test files the command statically
  resolves to (`selected_tests`; honest `UNRESOLVED` when nothing parses), and a warning per
  test file that references a target module but sits outside that selection - the
  manufactured-survivor condition that produced BG0203's two false survivors. Advisory only:
  the exit code never changes, so a deliberately narrow run stays legal and stays honest.
  The test command was already recorded in the JSON beside the result; a test now pins it.
- **A SIGKILLed mutation run can no longer poison the next run's restore source (BG0215).**
  `mutation.py` persists each mutant's original bytes to an on-disk sidecar
  (`sdlc-studio/.local/mutation-inflight.json`) before the mutant lands and clears it on
  restore. A later run recovers stranded targets from the sidecar before its baseline (and
  reports doing so), instead of reading the stranded mutant back as the original - which
  made every subsequent restore reinstate broken code while reporting on the real code. An
  unreadable sidecar refuses the run loudly and names the git restore path.
- **`audit.py`'s command and predicate branches are pinned (BG0212).** A full 190-mutant
  enumeration went from 15 survivors to 6. Nine were real: `cmd_profile`'s output branches had
  no test asserting what the command PRINTS, three predicate fall-through branches were tested
  for their true case only, and `cmd_check`'s status-query path was exercised nowhere - so
  neutralising its id selection left the batch empty, which audits clean and exits 0, a false
  green over work never examined. Two of those needed `assertIs(..., False)` rather than
  `assertFalse`, since a stub returning `None` is falsy and passed on a mutant that had broken
  the declared `-> bool` contract. The remaining 6 are equivalent mutants - unobservable
  initialisers, and `return 0` where `SystemExit(None)` exits 0 identically - and are recorded
  as such rather than chased with tests asserting what no caller can observe.
- **`transition --dry-run` gives the same answer as the real run (BG0213).** The dry-run did not
  evaluate the bug-depth, depth-parity or AC-verify gates, so a bug with no `Verification depth`
  field was reported as `would set BG0001 Open -> Fixed` while the real run blocked it. A dry-run
  exists so the requirements can be learnt before the work; one that disagrees with the real run is
  worse than none, because the requirement is still met as a refusal afterwards and the agent has
  been told the opposite meanwhile. The gates now fire on the dry-run path, which is the rule the
  tier gate already stated and the others did not follow. `--force` still waives what it waived, so
  a forced dry-run predicts a forced real run.
- **An epic whose breakdown declares a dead id is no longer owed a close no close can give
  (BG0211).** The union of `children_of` and the declared Story Breakdown is deliberately strict,
  but an id with no backing file (split, renamed, deleted) or naming a non-delivery artefact - a CR
  or an RFC - can never appear in a retro `Batch`, because a `Batch` names delivery units. The
  epic was therefore reported as owing a close forever, and every close left it owed: the exact
  unclearable debt that made the detector skimmable. Such ids are now excluded from the coverage
  demand and reported instead, so the cause is visible rather than silently forgiven. The advisory
  is scoped to epics whose forgiveness actually depended on the relaxation - this repo carries 33
  historical CR-in-breakdown declarations that change no answer, and a permanent 33-line advisory
  would be the same skim-past failure in another form. One unaccounted LIVE child still owes,
  so a ghost id cannot buy an exemption.
- **The audit profile parser's not-found paths are pinned (BG0203).** The two sites the bug named
  turned out to be covered already - hand-mutating both kills them. The real defect was the
  mutation run's test command being scoped below its target's coverage: pointed at one test file
  the gate reports 10 survivors for `audit.py`, and widened to that module's actual tests, the same
  mutants report 4. A narrow test command does not under-report coverage, it over-reports absence,
  and the phantom survivors get filed as bugs. The four genuine gaps are now pinned -
  `_refute_declaration`'s no-declaration return, `_reference_section`'s missing-anchor return and
  its sibling-heading rule - and `PROFILE_DIR`, which was defined but never used while
  `profile_names` recomputed the same path inline, is now the single answer it was meant to be. A
  full 190-mutant enumeration (0 truncated, 0 un-checked) leaves the profile PARSER clean - not the
  whole profile surface, since six of the fifteen residual survivors are in `cmd_profile` itself;
  that residue is BG0212.
- **The RFC accept gate names every open decision, not just the ones before a broken fence
  (BG0207).** The fail-closed re-scan was guarded by `fence is not None and not open_rows`, so it
  fired only when the main scan found nothing at all. With one open row before an unterminated
  fence and another after it, the first was found, the re-scan was skipped, and the caller got a
  list missing every row the fence hid - reported to the operator as the complete set. Both
  `transition` and `validate` print that list, so an RFC carrying D1 and D7 was described as
  carrying one open decision. The re-scan now fires on any unterminated fence; the unstructured
  read drops both structural rules, so it is a superset and can only add rows. The gate always
  blocked either way, so this was a false completeness claim rather than a bypass.
- **The shipped suite passes from an installed copy (BG0209).** Seven tests in `test_verify_ac`
  read the dogfooded workspace by path - real stories, US0163/US0166/US0172/US0173 - so from
  `~/.claude/skills/sdlc-studio` the root walk landed on the home directory and all seven raised
  `FileNotFoundError`. A consuming project running the shipped suite saw seven errors that said
  nothing about its own install. They now skip visibly, the pattern already established elsewhere.
  Measured both ways from a simulated install: 7 errors before, 7 clean skips after, with the dev
  repo still running all 144. The dev-repo check itself now has one definition,
  `tests/workspace.py`, instead of a copy per module.
- **A test module that imports a sibling helper runs under both forms (BG0206).**
  `test_reconcile` imported `loader` without first putting the tests directory on `sys.path`, the
  one line every other such module carries. Under `unittest discover -s tests` that resolves; under
  `unittest tests.test_reconcile` it raises `ModuleNotFoundError: loader`, which says nothing about
  the module being run - it cost a diagnosis cycle at a sprint close, where the mutation gate
  refused on the resulting red baseline and its remedy text pointed at a stranded mutant from a
  killed run, a plausible and entirely wrong lead. 154 tests now run under the module form that
  previously produced one error. A new hygiene sweep imports every sibling-importing module in its
  own interpreter, so the next module cannot drift the same way - one process per module
  deliberately, because importing them together lets the first module's `sys.path` insert mask
  every module after it.
- **The confinement roster sweep reads a write mode wherever the call form puts it (BG0202).**
  `_write_surface` read a call's mode from `args[1]`, which is where the builtin
  `open(path, mode)` puts it. The `Path` method is
  already bound to its path, so `path.open('a')` puts the mode at `args[0]` and was not matched at
  all - the detector reported an empty write surface for a module that demonstrably appends, and an
  uncovered writer would then pass the sweep in silence, which is the one failure the sweep exists
  to prevent. The mode index now follows the call form. Five modules gain a previously invisible
  append surface (`critic`, `deploy`, `ledger`, `telemetry`, `verify_ac`); all five were already
  covered or allowlisted by another route, so no writer was escaping today - the detector was blind,
  not the roster wrong. Both argument positions are now read, gated on the value being mode-shaped
  so a literal path is never mistaken for a mode, and a write mode wins over a read one - keying on
  the call form alone lost `io.open(p, 'w')`, and stopping at the first mode-shaped value lost
  `open('rt', 'w')`. Under-inclusion is the only direction that costs anything here: a spurious
  `open:txt` still reports a write surface, a missed write does not.
- **Refreshing a handoff no longer re-stamps it with another run's identity (BG0198).**
  `handoff.refresh` scoped the unit list to the batch it was given but drew everything else from
  ambient run state, so refreshing a closed run's handoff while a different run was open rewrote
  its Run / Outcome / Goal / Batch-source lines with the other run's identity and overwrote the
  shared worklist. The docstring promised "same id, same index row, same retro link"; a handoff
  belongs to a run, so the run is part of that identity. A mismatch between the document's
  recorded run and the open one is now refused by name, leaving the document untouched, rather
  than done quietly - this is not reachable through the shipped close, but it overwrote a live
  handoff twice during hand-running.

- **The allocator and the retro resolver now read one id space (BG0199).** `next_id._meta_nums`
  matches a meta id of 3 or 4 digits, so a legacy `RETRO001-x.md` holds its number and is never
  re-issued - but `retro._STEM_ID_RE` required 4+, so the very file the allocator was protecting
  could not be resolved. The resolver's floor is now 3 digits to match. The width is a floor, not
  the match: digits are still consumed greedily, so a 3-digit id does not resolve a longer file.

- **The apply-signoff tail no longer skips the velocity row in silence (BG0200).** The tail read
  the retro id from run-state `scaffolded_retro` and did nothing at all when it was absent - no
  row, no warning, and the close still printed success. A retro created with `artifact.py new`,
  the documented way to scaffold one, never sets that field, so the measurement the close owes went
  unrecorded and nothing said so. The id now falls back to the one the close was given, and with
  neither source the tail says on stderr that no row was written and names the command that writes
  it. This is the second half of the dashed-id fix: that repaired the case where the id was present
  but unmatchable, this the case where no id reached the tail at all - both closes reported success
  while the velocity record silently stalled.

- **The mutation gate no longer reports a mutant SURVIVED that never ran (BG0197).** CPython
  invalidates a cached `.pyc` on (source mtime, source size), so a mutant of identical byte length
  written inside one mtime second reused the stale bytecode: the ORIGINAL code executed, the tests
  passed, and the engine recorded a survivor. Same-length mutants are what operator-swap fault
  classes mostly produce, so the headline kill rate was partly evidence about the bytecode cache -
  the same unearned result the gate exists to expose. Two guards, each independently proven by
  killing a mutant of the fix: the runner now forces `PYTHONDONTWRITEBYTECODE`, and `applied`
  purges the target's cached bytecode on both apply and restore, because declining to WRITE a
  `.pyc` does not stop an existing one being READ - and a cache populated by an ordinary test run
  before the gate started is the normal case. `applied` additionally refuses a patch that leaves
  the file unchanged (reachable through a stale `occurrence` index): surviving a no-op is evidence
  about nothing.

- **The tranche audit no longer certifies an unfilled template as ready for implementation
  (BG0201).** `audit._weak_ac` documented itself as flagging "no checkable AC, or the tautology
  placeholder", but the placeholder it recognised was one hardcoded phrase - "lint and tests
  green". The `{{...}}` spans that `artifact.py new` actually emits matched nothing, so a story
  that was pure unexpanded template counted its AC-shaped markup as authored criteria and passed.
  Caught on a 32-unit batch the check reported as 32/32 ready while 28 of those units carried
  `{{executable check}}` as their only Verify line - the oracle `verify_ac` would then have
  executed to declare them Done. The check now flags an unexpanded placeholder anywhere in the
  Acceptance Criteria section, judged over the whole section rather than the counted items,
  because a criterion's `Verify:` line is part of it whether or not that line counts as an item.
  This is the step-2 gate whose stated purpose is that work never starts on a unit which would
  pass the downstream gates vacuously.

- **A single shared word no longer blocks a tranche on a keyword coincidence (BG0192).**
  `ac_scope` is a one-word keyword heuristic that documents itself as advisory, yet `audit` wired
  it as a hard readiness blocker. Every finding it produced against this repo was ordinary English
  shared with an unrelated epic title - "fixes", "residual", "cleanup", "fold", "around" - and the
  only remedies were to reword innocent prose or rescope an AC that was already correctly scoped.
  Findings now carry a `strength` (how many distinct keywords from the SAME owner epic) and only a
  multi-keyword hit blocks; a single-keyword hit is reported as a note. The frequency suppression no
  longer counts the OWNING epic's own stories towards a keyword's spread - it asks how widely a word
  is used outside the epic that owns it, and counting the owner meant one owner story plus one
  unrelated epic could erase a real cross-epic leak. (A story-count variant of the same suppression
  was tried during this sprint and removed for the same flaw.)

- **Each AC selects its own behaviour, and a shared selector is now visible (US0227).** US0172 and
  US0173 both ran `-k AttemptsAndCost`, and US0163's two ACs both ran the whole `test_close_owed.py`
  file byte-identically, so a regression in either behaviour failed both ACs and neither said which.
  All four are narrowed to the cases they own, and `verify_ac lint` now reports any Verify command
  appearing under more than one AC, with every AC that claims it. Advisory: two ACs asserting one
  indivisible behaviour is legitimate. The lint reports 17 such selectors across this workspace -
  pre-existing debt, now visible rather than silent.

- **The TRD's threat model agrees with its own write contract (BG0187).** 9 called
  `plan.py archive` the "sole, bounded exception" to confined writes while 5 rule 5 enumerates a
  dozen committed-file writers. The row now points at that set, guarded by a test so the
  contradiction cannot silently return.

- **The close refreshes its handoff after the sign-off cascade (BG0191).** The chain writes the
  handoff at step 5 and `--apply-signoff` transitions the run's units at the tail, so the document
  and the worklist the next `sprint plan --worklist` reads listed as remaining the very units the
  close had just completed. A new `handoff.refresh` re-renders the existing artefact in place -
  same id, same index row, same retro link, revision history preserved - scoped to the closing
  run's own batch, because `build` otherwise defaults to whichever run happens to be open. Blank
  runs are collapsed on the way out: the kept Revision History joined onto an already-terminated
  body produced a doubled blank line, and a generated document must not need hand-fixing to pass
  the markdown gate after every refresh.

- **A retro id resolves in either form (BG0195).** `find_retro` prefix-globbed the raw string, but
  files are named `RETRO0049-...` while indexes, run state and prose all write `RETRO-0049`. The
  close tail passed the dashed form, got "no retro file", and the velocity row went unrecorded for
  two consecutive sprints while the close still reported success. Resolution is now on the
  normalised leading id, and a 4-digit id no longer matches a longer one by prefix.

- **An unmeasured sprint is no longer reported as an unforecast one (BG0196).** `accuracy` derived
  the batch's estimator constants from RATED units only - those with both a forecast and a
  measurement - so a sprint with no token telemetry collected none and printed "no plan-time
  forecast was recorded" directly beneath its own "9 of 9 forecast at plan time". Constants are now
  read from every forecast unit. (The bug as filed diagnosed this as `accuracy` being unable to read
  an aggregate-only forecast; that was wrong, and the record carries the correction.)

- **A verifier that exits 0 having run no tests no longer counts as proof (BG0193).** A filtered
  runner whose pattern matches nothing can exit clean: `unittest` only began returning 5 for "no
  tests ran" in Python 3.12 (the skill supports 3.10+), and `go test -run NoMatch` exits 0 on every
  version. A renamed or deleted test class therefore turned an executable AC into a green no-op.
  `run_verifier` now reads the runner's own summary line and refuses a clean exit that reports zero
  tests, counting it as `vacuous` on the story report and naming the remedy. The signatures are
  anchored to each runner's summary format rather than matched as bare keywords, so an honest test
  that discusses test counts is unaffected, and only test-running verbs are judged - `grep` could
  otherwise match a signature inside the file it is searching. A no-test signature counts only when
  NOTHING claims to have run, decided PER RUNNER FAMILY from that family's own output: `go test
  ./...` prints `[no test files]` per package without tests while others pass, so the run is empty
  only when every package line says so, and a jest workspace's `No tests found` yields to another
  project's `PASS`. `unittest` and `pytest` print one exclusive summary each and are judged on it
  alone. A blob-wide "did anything pass?" veto was tried and removed: a `shell` verifier running
  `make test` beside a linter printing "12 passed" would have had the whole gate switched off.

- **The `grep` verb no longer lets a dash-leading pattern become the tool's flags (US0228).** The
  pattern is passed behind `-e` and the paths behind a `--` terminator, for both the `rg` and the
  `grep -rqE` back-end, so an AC whose regex starts with `-` searches for what its author wrote.

- **US0166 AC3 now checks the claim it makes (US0226).** The line read `grep -q "..." <one file>`,
  but the `grep` verb takes no flags: `-q` was parsed as the PATTERN and the quoted text as a PATH,
  so the verifier searched for the literal string `-q` across a list containing a file that does not
  exist, found it, and exited 0. The AC had been recorded green on every run without once checking
  its own claim - which happens to be true, which is why nothing surfaced it. It is now an explicit
  `shell` verb asserting both halves of the claim against both files it names.

- **A 4-digit artefact id can no longer be read out of a longer one (BG0194).** `ID_SEARCH_RE` and
  `ID_RE` matched a fixed `\d{4}` with no trailing boundary, so `US01010` parsed as `US0101` and any
  consumer matching ids this way attributed a 5-digit artefact to a different, real one. The digit
  run is now `\d{4,}`, and the v3 ULID alternative is tried before the sequential one so a
  digit-leading ULID (`BG-0123ABCD`) is claimed whole instead of truncating to `BG-0123`.
  `id_number` accepts 4 to 7 digits - a long sequential id was previously invisible to the max+1
  allocator, which would then re-mint an id already in use - while still refusing an 8+-char ULID.

- **The apply-signoff tail derives parent epics terminal (BG0190).** The per-unit cascade ticks an
  epic's Story Breakdown checkbox but never sets the epic's own `Status`, and with
  `two_backlog.enforce` off (the default) reconcile does not derive it either - so a close that
  transitioned every one of an epic's stories Done left the epic at Draft, to be moved by hand.
  `sprint close --apply-signoff` now transitions an epic whose breakdown units are all terminal,
  through the gated path. An epic with no breakdown units is skipped ("no children" is not "all
  children complete"), a live child blocks the derivation, and an already-terminal epic is left
  alone so a re-run stays idempotent. US0237's AC2 claimed this behaviour while its Verify line
  covered only the reconcile-drift half; it now points at the derivation tests. The derivation is
  scoped to the parents of the run's own units and refuses on any child it cannot read (a breakdown
  id with no backing file, or a unit with no `Status`) - an unreadable child is unknown, not
  finished, and the first implementation would have marked an incrementally-written epic Done off
  its one delivered story, on every epic in the repo.

- **The review close writes its own index row (EP0072, US0214).** `review_prep close` stamped
  review-state and derived the LATEST anchor but left the RV out of `reviews/_index.md`, so the very
  next step of the close chain - reconcile - caught the missing row as drift and halted the ceremony
  for a mechanical fix `reconcile apply` performed anyway. The close now ensures the row through the
  shared meta-index helper (house column order honoured, create-from-template path intact),
  idempotently. An indexing failure warns with the remedy rather than losing the close: the stamp is
  the close, indexing is a convenience on top of it.

- **An uncommitted-but-current review anchor is told apart from a stale one (EP0072, US0215,
  absorbing CR0341).** The review-current lane dated `LATEST.md` by its last commit, so a review
  re-run during the close - derived but not yet committed - read at its previous commit and the gate
  demanded the operator "run `review`", the exact thing they had just done. The lane now detects the
  dirty anchor, re-reads it at its working-tree time, and reports it as current but UNCOMMITTED with
  committing the close paperwork as the remedy. It still blocks (an uncommitted close is not a
  close), and an anchor that is genuinely older than a changed artefact still reports staleness.

- **A repo-wide conformance failure is attributed once, not to every unit (EP0072, US0217).** The
  `documented` stage is a repo-global floor: one uncatalogued command failed it for every Done
  unit, so a single doc gap rendered as 118 non-conformant units - a true count of a misleading
  thing, which buried every genuine per-unit finding. Repo-wide conditions (`documented`, and a
  missing index for `reconciled`) are now listed once under a new `globals` key with the reason and
  its remedy, and appear per unit as `missing_global` rather than `missing`. Reporting is the only
  thing that changed: the gate lane counts global failures alongside per-unit ones and
  `conformance check` still exits non-zero, so attributing a failure differently never enforces
  less. A condition affecting no judged unit is not reported as a failure at all.

- **The pre-commit gate measures, announces, and skips its long unit run (EP0072, US0219,
  US0220).** The ~2,800-test suite takes around 2.5 minutes, exceeding the 2-minute default of
  common tooling, so a commit looked hung and got killed or bypassed - and a bypassed guard guards
  nothing. New `tools/gate_timing.py` records each suite's wall-time to a bounded per-suite history
  (`sdlc-studio/.local/gate-timings.json`, most recent 10) and estimates the next run from the
  median, so one cold-cache run does not inflate every later figure; the hook prints the expected
  duration and a timeout to allow before starting. It degrades to silence rather than to a wrong
  number - no history, a corrupt file, or a non-numeric entry all print nothing and never fail a
  commit. The existing docs-only skip is now **named** rather than silent, stating which guards
  still ran, because a guard that quietly does not run is indistinguishable from one that ran and
  passed. Any change under `scripts/`, `templates/` or `tools/` still forces the full suite.

- **A bounded mutation run spends its ceiling on the changed lines (EP0072, US0218).** With
  `--since REF`, `mutation.py` now reads `git diff -U0` into a changed-line map and applies mutants
  on those lines before any untouched code; once the diff is covered the remainder spreads
  round-robin as before. Previously the rotation was fair across the surface but blind to the diff,
  so a low ceiling on a large file sampled whichever lines sorted first - peripheral helpers - and
  reported a confident kill rate about code nobody edited. The report gains `diff_mutations`,
  `diff_applied` and `diff_covered`, and a run whose ceiling could not reach the whole diff warns
  with the fraction achieved. Runs without diff information (`--files`, `--story`) are unchanged.

- **A metadata edit no longer invalidates a green AC verification (EP0072, US0213).** The Done
  gate judged freshness on the story file's mtime, so a Status transition, a Revision History row,
  or `verify_ac`'s own `**Verified:**` stamps all reported a correct green as "edited after it was
  last verified" - demanding a re-run that could only produce the same result. `verify_ac` now
  records an `ac_fingerprint` (sha256 over each AC's id, title and Verify command) and the gate
  compares that instead: metadata edits are recognised as noise, while a retitled AC, an added or
  removed AC, or a re-pointed verifier still invalidates. Reports written before the field existed
  carry no fingerprint and still fall back to mtime, so the new field's absence never silently
  passes a stale green.

- **A refused mutation run no longer reads as a clean sweep in the gate (EP0072, US0216).** When
  `mutation.py` refuses because the baseline is red (a failing suite, or a test command that errored
  on unmutated code) it applies no mutant, so the report's summary is all zeros. The gate's mutation
  lane rendered that as `0/0 mutations killed (advisory)` - indistinguishable from a run that mutated
  nothing because there was nothing to mutate. The lane now reads the report's `refused` flag and
  prints `mutation REFUSED - baseline <fail|error> (no mutants applied, nothing was proven)` followed
  by the report's own remedy, and counts as un-met rather than zero-as-clean. An ordinary run's
  rendering is unchanged.

- **The skill gives one answer for "current schema version" again (BG0189).**
  `project_upgrade.CURRENT_SCHEMA` was hardcoded `2` while `init` seeds new projects at
  `schema_version: 3` (from `templates/config.yaml`), so an upgrade computed against it would move a
  project to the wrong version. `CURRENT_SCHEMA` now derives from the single source of truth via a new
  `sdlc_md.current_schema()` (reads `templates/config.yaml`, the new-project seed); `config-defaults.yaml`
  stays the explicitly-named fallback for un-stamped legacy workspaces. The `.version` schema stamp now
  follows the project's own effective/config schema rather than being forced up to `CURRENT_SCHEMA`, so a
  project that declines the v2->v3 switch keeps its version. A coherence test asserts
  `CURRENT_SCHEMA == templates/config.yaml == init`'s seed so the two cannot drift again. `audit()`'s
  `stale-version` auto-fix now flags only what `apply()` actually stamps (a lagging skill version, or
  a `.version` schema behind the project's own config schema) - not merely a project below
  `CURRENT_SCHEMA` - so a legitimately-v2 project no longer carries a permanent, uncorrectable
  stale-version finding (the dry-run-matches-apply invariant, held).
- **`sprint plan --write` no longer accumulates a new batch onto a judged-but-unfinalised run
  (BG0188).** A close that records the Sprint Goal verdict but stops before the handoff leaves the
  run `outcome=running` while carrying a close artefact - an inconsistent state `open_run` did not
  detect, so the next plan reused the old `run_id`/`started_at`, unioned the new units onto the old
  terminal batch, and stamped the new goal over the already-judged verdict. `open_run` now treats a
  run carrying any close artefact (`sprint_goal_verdict`, `ended_at`, `handoff`) as spent and mints a
  fresh run; a genuinely-open run (no close artefact) still re-plans in place and accumulates.
- **The spec-truth refresh sprint (RUN-01KXR6XS): EP0071 + the open-bug backlog.**
  - **BG0184:** the cross-epic-ac lint (`ac_scope.check`) now exempts a keyword whose sole owning
    epic is *terminal*. A closed epic owns no live scope, so a new extension story reusing its title
    keyword is not a cross-epic leak - it was being silently blocked NOT-READY at the tranche-audit
    gate (was CR0331). A live (non-terminal) owner still flags. Terminal-owner and live-owner
    regression tests added.
  - **BG0183:** `test_telemetry.py` now carries the tests-dir `sys.path` shim its siblings already
    have, so its `gitutil` import resolves under a single-module run (`python3 -m unittest
    tests.test_telemetry`) as well as under `discover -s tests`. Removes the standing "ignore the 3
    gitutil failures" workaround that masked real regressions.
  - **BG0185:** a mis-cased or mis-spaced `[check: ...]` tag now ERRORS loudly instead of parsing as
    no-tag (was CR0332). `sdlc_md.check_tag_near_misses` detects a `[ check ... ]` shape the strict
    parser rejects, and `validate.py` reports it as a `malformed-check-tag` error - closing the silent
    control where a criterion's bar went unenforced. A near-miss must also carry a tag shape (a colon
    or an id-shaped dotted token), so bracketed prose like `[check the logs]` and an unrelated
    bracketed word do not flag.
  - **BG0186:** `parent_ref` (singular) now delegates to `parent_refs` and returns the first
    non-sentinel parent, so it agrees with the plural reader on a malformed record whose first
    `Parent:` line is a `-` sentinel followed by a real id. Inert today (consumers use the plural
    path) but the two readers no longer diverge for a future caller. Found by the CR0322 review.
  - **BG0182:** `help/mutation.md` now matches the shipped refuse-on-red-baseline contract
    (BG0180): a red or broken baseline refuses the run (no mutant applied, `refused`+remedy,
    non-zero exit) rather than recording a per-mutation error, and the stranded-mutant restore
    (atexit + SIGTERM) is documented.

- **The 2026-07-16 audit backlog (RUN-01KXQH64, the audit-backlog sprint).**
  - **BG0152:** per-attempt telemetry now has a production WRITER, not only a reader. `telemetry
    record` takes `--attempt MODEL:TOKENS` (repeatable, order-preserving) and `--attempts JSON`, and
    `transition set` threads the same list (plus `--tokens`/`--model`) onto the terminal-close event -
    so a unit that escalated records every attempt and `unit_cost` sums the true cost, instead of every
    escalation degenerating to one flat line. A malformed `--attempt` is refused, never dropped.
    US0172 gains AC2 (the writer path) to close its reader-only verification gap. Documented in
    `reference-scripts-domain.md`.
  - **BG0153:** `latest_actuals` now AGGREGATES cost across a unit's records instead of a
    last-non-null merge that silently dropped all but the final cycle. A reopen-reclose (or any
    multiple close) sums its tokens and wall-time (rework included), and a flat record followed by
    an attempts re-record concatenates into one attempts list - so `accuracy` (attempts-first now)
    and `unit_cost`/the spend report read one identical cost, never 50k vs 200k.
  - **BG0158:** the velocity elapsed-hours read requires a run-state to cover a strict MAJORITY of
    this sprint's units, not merely share one. A previous runner sprint's cumulative run-state that
    carried a single redelivered unit no longer lends its full elapsed (the 43h confounder), and an
    explicit `--elapsed-hours` is an operator override that now wins outright.
  - **BG0159:** `model_price` reads the `pricing` block once and indexes it by the raw model id
    first, then the family - so `pricing.claude-opus-4-8` (the printed hint's form) is honoured and
    a dotted foreign id like `gpt-4.1` is no longer destroyed by `config.get`'s dot-splitting. The
    telemetry docstring, the report hint and US0173's AC now agree on the key form.
  - **BG0160:** `config.get` degrades to the default on a malformed `.config.yaml` (a
    `yaml.YAMLError`, previously uncaught and tracebacking through every consumer), honouring the
    BG0093 warn-and-default contract; a malformed-YAML test now holds it.
  - **BG0164:** an attempts-only telemetry record (the escalation case) stamps `Delivered-by` from
    the last attempt's model, so the unit that most needs the audit attribution no longer silently
    goes unstamped.
  - **BG0165:** a unit delivered across more than one model is itself mixed - `accuracy` labels it
    MODEL_MIXED, marks the batch mixed (refusing the pooled ratio), and keeps it out of the
    per-model rows, so a haiku->opus escalation can no longer hide as a single-model batch or book
    its cheap-attempt tokens into the dear model's calibration.
  - **BG0181:** retro `accuracy` strips each `(...)` provenance parenthetical from the batch line
    IN PLACE (dropping the `(EPxxxx-EPyyyy, from CR.../RFC...)` / `(absorbing CRxxxx)` mentions that
    padded the UNFORECAST list) while keeping every delivery unit around it - the closing review
    caught that truncating at the first `(` silently dropped units listed after an inline
    parenthetical.
  - **BG0154:** `decisions.py` ledger writes are atomic and lock-guarded - concurrent `decisions
    add` no longer mint a duplicate D-id and a crash mid-write no longer truncates the ledger.
  - **BG0155:** a corrupt close-down baseline is a loud refusal, not a silent disarm - `owed()`
    reports `corrupt`, the close-owed detect exits non-zero, the close guard blocks, `gate
    --require-close` fails and the status advisory surfaces it, all directing repair over re-stamp.
  - **BG0156:** the PRD data model records run telemetry as committed `retros/evidence/` JSONL, not
    a `.local/telemetry.jsonl` (spec-rot corrected).
  - **BG0157:** the breakdown-gate AC in the PRD and TRD states the real sizing - a story/bug by
    `Points:`, a CR/RFC/epic by a T-shirt `Size:` - dropping the retired Effort S/M/L.
  - **BG0166:** all three retro/lessons close lanes honour `lessons.loop: judgement` through a
    shared helper, so the opt-out makes the whole set advisory as the docs promised (two were
    hard-coded blocking).
  - **BG0168:** the PRD status line and epic index record the verified 2026-07-09 Ready->Done
    close-out instead of the stale "all epics are Ready" note.
  - **BG0171:** the `--require-close` help no longer falsely claims the lane WARNS on every gate -
    it is bound to the flag; the plain gate never runs it.
  - **BG0162:** the TSD states the real test-coverage contract (a dedicated `test_<name>.py` by
    convention; named indirect coverage; the currently-untested scripts), not a phantom per-script
    build gate that never existed.
  - **BG0167:** the eval gate enumerates every scenario on disk, so a wholly-ungraded scenario
    fails the gate (UNGRADED) instead of vanishing from `data.items()` and reading as a pass.
  - **BG0170:** the TSD gate-lane tables match `gate.py` - `doc-freshness`/`hook-enabled` marked
    advisory, the `--require-close` bound lane and the two-leg `--release` binding recorded.
  - **BG0161:** RFC0018/0022/0023 record their accepted decision outcomes (per decisions D0002/
    D0004/D0010) rather than sitting Open with contradicting leanings.
  - **BG0163:** `sprint` batch-triage reports unreadable backlog artefacts as drops ("N
    unreadable - not triaged") instead of an unreadable file reading as a clean plan.
  - **BG0169:** CR0273 carries `Superseded-by: RFC0035` and RFC0035 records that it absorbs it.
  - **BG0172:** the test-specs index carries real coverage figures and an honest
    script-suite-is-the-validation-leg note, not a misleading empty shell.
  - **BG0173:** the audit refute panel has a quorum rule - a dead skeptic vote is never a
    refutation, an incomplete panel is UNJUDGED, and the report fails loud with an unjudged count.
  - **BG0174:** the `audit` command has a `help/audit.md`, a SKILL.md Type-Reference row and a
    `help/help.md` catalogue entry (it was catalogued nowhere; the doc-coverage floor requires
    both the Type Reference and the help catalogue).
  - **BG0175:** the review-meta scaffold stamps `Raised-by` and a real revision-row author from
    `--author` instead of leaving a literal `{{author}}`.
  - **BG0176:** `migrate` no longer advises re-sizing terminal legacy-Effort units - they become a
    one-line `terminal_sized` count, not work nobody should do.
  - **BG0178 / BG0179:** `refine`'s seeded AC headings and `handoff`'s goal-derived H1 strip
    trailing punctuation (no MD026).
  - **BG0180:** `mutation` refuses on a red or broken baseline (no mutant applied, `refused` +
    remedy in the report, non-zero exit) and restores any applied mutant on SIGTERM/atexit, instead
    of "applying" every mutant against a red baseline and possibly exiting 0.

- **Four integrity fixes cleared the delivery backlog (BG0142, BG0144, BG0145, BG0146).**
  - **BG0142:** `reconcile._link_exists` dropped the type-dir fallback for an archive row link - it
    now resolves only file-relative, agreeing with `check_links` (BG0137). Two guards no longer
    disagree about what a valid link is, and a regressed archive link can no longer hide in reconcile.
  - **BG0144:** the grooming gate refuses a unit whose declared `Affects` paths ALL fail to resolve
    on disk (a fictional/typo list sized from nothing), naming the unresolvable paths; a file the
    unit will create (greenfield) is tolerated as long as some path resolves. Gates both creation and
    planning, from the one shared definition.
  - **BG0145:** `complexity.assess` keeps the churn-based risk for a docs/config unit even when code
    complexity is inapplicable - a constantly-churning doc is no longer invisible to the router just
    because it carries no cognitive score. Code `difficulty` stays `unknown`; only the churn risk
    band picks it up. (The bug's part (1), the `--seed-source` CLI restriction, was already removed by
    RFC0038 - declined.)
  - **BG0146:** `sample_class` now labels a velocity row IN-SAMPLE only when the constants that MADE
    its forecast are the ones its actuals were fitted to. A row forecast by a retired estimator, whose
    actuals were later refit, reads `stale-constants`, not training error - so a recalibration can no
    longer relabel the out-of-sample falsifications that justified it (RETRO0025 0.55x, RETRO0026
    0.39x).

- **The canonical creator now writes the RIGHT sizing field per type (BG0148, BG0149).** `artifact.py
  new` gains `--size` and writes a T-shirt `Size` for a cr/rfc/epic and `Points` for a story/bug, from
  the same `sdlc_md` definition the finding filer uses - so the two creation paths can no longer disagree
  on what a type is sized by (LL0016). Two silent drops are closed: a story's `--points` used to vanish
  (the template had no Points line), and a CR was written with `Points` where the model wants `Size`. The
  wrong sizing flag for a type (a CR's `--points`, a story's `--size`) is now WARNED, never silently
  dropped.

- **The forecast is now RECORDED when it is made, so the estimator can be falsified (BG0133).**
  `retro.py accuracy` used to re-derive each estimate at retro time from the LIVE constants, so
  recalibrating them silently rewrote what every past sprint was deemed to have predicted. The 5.2x
  miss that CAUSED the recalibration had been erased BY it. `sprint plan` now records each unit's
  forecast, the seed it came from, and the constants that produced it, unconditionally - not behind
  `--write`, because a forecast that depends on someone remembering a flag is a forecast that does
  not exist. `accuracy` reads that record and never re-derives; the re-derivation path is deleted,
  not left as a fallback. A unit with no recorded forecast is UNFORECAST and excluded from both
  sides of the ratio, exactly as UNMEASURED already was: silence on the estimate side is not
  evidence either. And a velocity row whose forecast was produced by the constants currently in
  force is labelled IN-SAMPLE and excluded from any figure shown as evidence - the planner used to
  quote its own 1.09x training error back to the operator while the true out-of-sample figure was
  0.55x. The label is derived at read time, so a future refit reclassifies a row rather than leaving
  it standing as validation for a model it helped fit.

- **The filer now demands what the planner demands, from ONE shared definition of groomed (BG0136).**
  CR0260 made `sprint plan` refuse an ungroomed unit, but `file_finding.py` had no `--affects` flag
  at all - so every bug it filed was born unplannable, and the gate refused three bugs our own filer
  had written that same day. The filer does not restate the rule: it renders the body it is about to
  write and hands it to `sprint.breakdown()` itself, so a third grooming field would land at both
  ends at once, and an `--affects` the planner's parser cannot read back as a path list is refused as
  no `Affects` at all. `artifact new`/`batch` enforce it too, because the help documents them as the
  canonical path and enforcing only in the filer would move the bug rather than kill it. RFCs are
  exempt: the planner never selects one, so demanding it would be grooming theatre. Two defects this
  surfaced: `templates/core/cr.md` carried a decoy `**Effort:**` above the real one, so **every
  full-template CR had been unsized to the planner whatever `--effort` said**, and `artifact new
  --type bug --effort S` accepted the flag and silently dropped it.

- **The engagement-floor trailer check refuses instead of warning after the fact (BG0134).** It
  printed a failure-shaped message explaining that the floor could not attribute the commit, then
  exited 0 and let it land - a guard that names the hole it is leaving, and leaves it. A multi-id
  subject with no `Refs:` trailer now fails the commit and prints the exact trailer lines to paste.
  A single-id subject still needs none, and merges, reverts and fixups are untouched: git wrote those
  messages and the work they record was gated on its original commit. `--no-verify` remains the one
  escape; the `SDLC_ENGAGEMENT_STRICT` env var is gone rather than left as a second bypass.

- **reconcile sees an orphan index row, and so does the link checker (BG0135).** A row whose artefact
  file is gone survived `reconcile detect`, `check_links` AND `validate` - three guards, one phantom.
  The detector existed; the hole was the status gate, which treated a `Proposed`/`Draft` row with no
  file as an intentional reservation - and the filer mints CRs as `Proposed`, so deleting a
  freshly-filed artefact was invisible while deleting a `Complete` one would have been caught. The
  principle now: **a row that LINKS a file is not a reservation - a link is a claim that the file is
  there.** An unlinked row still reserves nothing, so that exemption survives. `apply` never prunes
  by default (a bad checkout, an in-flight rename and a deletion look identical from here) but no
  longer stays silent about it; `--prune-orphans` is the opt-in. `check_links` now validates index
  row file targets, not just anchors.

- **Every `_index.md` write is atomic now (BG0127).** `sdlc_md.atomic_write` exists so a reader never
  sees a half-written index, and it was used on the main paths - but six index-mutating writers went
  through a plain `write_text`, leaving a torn-read window: reconcile's full story-index rewrite,
  `meta_new`'s row insert (which wrote the artefact file atomically two lines earlier), archive's
  live-index trim, the pipeline and handoff index bootstraps, and the lessons index append. A guard
  applied inconsistently is not a guard (LL0008). All six now go through `atomic_write`, and an
  AST-scanning test fails on any NEW non-atomic index write - a source scan rather than a pin on
  today's six, because an enumerated fix exempts the one it forgot (LL0013).

- **`retro.py` no longer miscounts a decline that cites an artefact id (BG0130).** `dispositions_in`
  checked the artefact-id pattern before the decline pattern, so `declined: belongs to RFC0034
  (CR0257)` was reported as **filed** - the finding read as ticketed when it was deliberately not.
  An explicit `declined:` prefix now wins. A bare `declined` with no reason still counts as
  undecided.

- **Security hardening notes documented (CR0250).** `reference-verify.md` now recommends setting the
  AC-verifier's `http` host allowlist on a cloud or CI host (with it unset, a well-intentioned Verify
  line could reach a link-local metadata endpoint - inside the trust boundary, but worth closing).
  The README tells anyone installing in a sensitive environment to pin a tagged release and set
  `SDLC_STUDIO_REQUIRE_CHECKSUM=1`.

- **The `grep` verifier verb now expands globs, so the documented example works (BG0125).** `grep
  "..." src/**/*.ts` false-RED'd on present code because the verb runs argv (no shell) and the glob
  reached `rg`/`grep` literally. Globs are now expanded against the run directory before the tool
  sees them; an unmatched glob passes through literally so a genuinely missing target still fails
  honestly. The verb had zero test coverage (which is why this survived) - it now has tests,
  including the exact false-RED case. Its `rg`-vs-`grep -rqE` dialect difference (BG0128) is
  documented in `reference-verify.md`: keep patterns POSIX-ERE-portable, or install ripgrep.

- **`verify_ac run` accepts `--file` as an alias for `--story` (CR0251).** `--file` is the flag an
  agent reaches for first; it errored before. Now aliased on both `run` and `lint`.

- **The sprint-close review is a hard gate now, not just advice (CR0253).** The close is reconcile +
  review + retro; reconcile blocked on drift and retro was promoted to a hard gate (RFC0032), but
  review currency was only advisory (`doc_freshness`), so a stale review reached a close - and did:
  `LATEST.md` sat claiming "ready to tag" long after that stopped being true. A new blocking
  `gate --require-review` leg fails unless `reviews/LATEST.md` is at least as new as every artefact.
  Currency, not presence (`review-legs` already checked the docs exist; this checks the review was
  re-run). The deterministic input was already there in `review_prep`; it just needed a leg. The
  documented close command is now `gate --require-retro RETRO{next} --require-review`.

- **`meta_new` now takes the allocation lock (BG0126).** Retro/review/handoff creation allocated an
  always-sequential id and appended its index row without `sdlc_md.allocation_lock`, unlike every
  other creation path, so two concurrent `artifact new --type retro`/`--type review` could mint the
  same id and clobber each other's index insert. Wrapped to match `new()`/`file_finding()`.
  Delivered as the vehicle for the **token-supplier PoC** (CR0258): run as a background subagent, its
  harness-reported usage (46,792 tokens / 272s) was fed into `telemetry.py record`, producing the
  first telemetry record with a real token value - proving the supplier the sizing loop needs.

- **`review_prep` no longer counts `personas/index.md` as a persona (BG0129).** The filter excluded
  `_index.md` but the index file is `index.md`, so every review reported a phantom "Persona Index".
  Both spellings are excluded now, via one shared set used by both the usage and required-legs
  passes.

- **A passing test suite is silent again (CR0241).** Tests that feed the validator a
  deliberately-broken fixture were letting its diagnostics escape to the console, so a fully green
  run printed `ERROR` lines and the tail of 2000 passing tests read like a failure. That is not
  cosmetic: it trains everyone, human and agent, to skim past `ERROR`, which is the exact reflex
  that lets a real one through. A signal you cannot distinguish from noise is not a signal. The
  expected diagnostics are now captured and **asserted on** - the tests are stronger for it, since
  they previously checked only the exit code and never looked at what the validator actually said.
  A new `test-noise` gate leg keeps it that way.

- **The retro gate was satisfied by `touch` (BG0123).** Its leg globbed for a filename
  (`retros.glob(f"{retro_id}*.md")`), so a 0-byte `RETRO9999.md` returned
  `[PASS] retro: batch retro RETRO9999 present`. The one gate that existed to make the
  retrospective un-skippable was the one an agent could satisfy without doing the work. It now
  delegates to `retro.py validate` and reads the content. Existence is not evidence (LL0023).
  The suite was **guarding the bug**: a test wrote a file containing only `# RETRO-0005` and
  asserted the gate *passed* it, so fixing this would have been reported as a regression. That
  test now asserts the opposite.

- **LL0024 - a hazard found by calling a private helper directly may already be guarded at the only
  call site that matters.** BG0124 was filed as a High bug claiming the artefact filer corrupted
  executable `Verify:` lines into false greens. It was **wrong, and has been withdrawn**:
  `artifact.py` already routes `--verify` through a verbatim path that never markdown-safes it, and
  that function's docstring already spelled out both failure modes. The hazard was real, the
  exposure was zero, the defence was already there. It was "proven" by calling the private
  `_md_safe()` directly - which tests the helper and says nothing about the pipeline, the only thing
  that ships. Reproduce through the public path or you have not reproduced it; look for the guard
  before filing; and a confident false finding is not free, because a process that turns findings
  into work will faithfully manufacture work from a wrong one.

- **LL0023 - a gate that checks an artefact exists, not what is in it, is satisfied by `touch`.**
  From BG0123: the retro leg globbed for a filename, so a 0-byte `RETRO9999.md` returned
  `[PASS] retro: batch retro RETRO9999 present`. The one gate that made the retrospective
  un-skippable was the one an agent could satisfy without doing the work. A ceremony gate must
  assert on content and on the disposition of what the artefact contains; existence is not
  evidence. The tell that you are about to build one: there is no deterministic tool that produces
  or validates the artefact, so the gate has nothing to interrogate but the filesystem.

- **LL0022 - a guard that branches on invocation mode must be tested in every invocation mode.**
  Promoted to the cross-project registry from BG0122. A source-vs-execute guard has as many code
  paths as there are invocation modes (piped, executed, sourced), and the installer's suite only
  ever exercised the one that was never broken. Two rules: test every mode the guard
  discriminates, and assert on output rather than the exit code whenever the failure mode is "did
  not run" - the broken installer exited 0, so an exit-code assertion would have passed against
  the bug. Corollary: check the probe fails against the pre-fix code before trusting it.

### Security

- **Three high-severity advisories in the markdown lint chain are patched (BG0468).** `linkify-it`, `js-yaml` and `brace-expansion` all reached this tree transitively through `markdownlint-cli`, the repo's only devDependency, and were flagged the moment 208 commits were pushed and the dependency graph became visible again. Resolved by lockfile update alone: `package.json` is untouched, because `^0.49.0` already covered the 0.49.1 that carries the fixed transitives. Verified that the linter still LINTS rather than merely still running - a probe carrying trailing whitespace, consecutive blanks and a bare URL trips MD009, MD012 and MD034 and exits non-zero, which matters because `js-yaml` crossed a major version and a silently neutered lint would pass every gate.

## [4.1.0] - 2026-07-14

### Added

- **A declared appetite bounds an unattended run (CR0225).** An agentic run had exactly two
  ends: it finished, or it failed. It now accepts an appetite - `--appetite-minutes` and/or
  `--appetite-units` - and a circuit breaker (`loop_guard budget`) stops the run cleanly when
  the appetite is spent. The breaker is deterministic: elapsed time comes from the run's own
  start timestamp and the unit count is read from each artefact's status on disk, so neither
  input is a number the model reports about itself. It fires at unit boundaries, so no unit is
  abandoned mid-implementation, and budget-exhausted has its own exit code, distinct from a
  quarantine - the units keep their true status rather than being marked blocked. The run closes
  by reporting appetite declared against spent against delivered and generating the handoff
  guide. A token figure is reported as an estimate at plan and close, and is never a gate,
  because a script cannot observe token spend and a self-reported budget is not a breaker. The
  appetite is never auto-extended; extending it is a fresh run.

- **The handoff guide: a generated record of where an agentic run stopped (CR0223).** When a
  sprint or epic run ends short of its goal - blocked, budget spent, or halted - the tail of
  remaining work was scattered across hints, the decisions ledger and the retro, with no single
  document a human joining afterwards could pick up from. `handoff generate` now writes one: what
  was delivered with its evidence, what remains with a per-item pointer (the file, the failing
  AC, the stalled stage) and a suitability tag (copilot-tail versus judgement), and the open
  decisions. It is a join over machine-readable state, not new instrumentation, and it is exact
  about delivery - a Done unit whose acceptance criteria are red or stale is reported as
  remaining, not delivered, because a status is a claim and the verifier is the evidence. It also
  introduces the run-state object (`sdlc-studio/.local/run-state.json`) that records a run's
  identity, batch and outcome under a lock, so the tail can be assembled and later work can build
  on it. `sprint plan` reads a pending handoff back as an input.

- **The lessons close-loop is now a mechanism, not doctrine (CR0236).** Sprint close was
  meant to summarise the lessons learned, and the next sprint was meant to read them. Only
  the retro artefact was ever enforced; regenerating the summary and reading it at the start
  were prose, which an agent under effort pressure simply skips. Two blocking lanes now bind
  to the close gate: `lessons-summary` refuses a `LESSONS-SUMMARY.md` that is stale against
  the lessons log, and `lessons-validity` refuses an open lesson past its review horizon or
  carrying none at all. The staleness check **recomputes the digest and compares it** rather
  than trusting a stamp, a count or an mtime, so there is nothing to forge - closing one
  lesson and adding another is caught even though the count never moves. `sprint plan` now
  prints the lessons in force as part of the plan, so the agent reads them rather than being
  pointed at a file it may not open. Closed in passing: `--skip retro` had been silently
  voiding the retro gate; any deselected bound lane is now refused.

- **A `planning` template tier, and a promotion contract that cannot be forged (CR0235).**
  The full story template's structural floor is around 171 lines, so a pre-implementation
  planning story could not get near its ~120-line target however economically it was written.
  `--template planning` renders a story in 54 lines and an epic in 39, keeping the acceptance
  criteria, their `Verify:` targets, scope and technical notes, and deferring the sections
  implementation needs. Promotion (`artifact.py promote`) adds those sections back, losslessly
  and idempotently. The tier is gated on the **presence of the deferred sections**, not on the
  metadata stamp: a stamp is a claim, not the work, so a planning-tier story or epic cannot
  reach In Progress, Review or Done by relabelling itself - `transition annotate` refuses the
  field, a hand-forged `full` stamp is refused as a claim its sections do not support, and an
  unrecognised tier fails closed rather than switching the gate off. Projects that want the
  same rule applied to every story, stamped or not, can set
  `quality.require_full_sections: true` (opt-in: only 16 of this repo's 119 existing stories
  carry all eight sections, so enforcing it by default would be a breaking change).

- **`gate.py --release`: one command that cannot be misread before a tag (CR0233).** The
  standard gate plus an executing AC-verify pass, as a single exit code. The lane runs every
  `Verify:` expression for real rather than reading a report that may carry a stale green -
  the failure that let a rotted Verify layer reach the v4.0.0-rc.1 tag. It writes nothing, so
  the gate stays read-only and hook-safe. Three refusals make a false green unreachable:
  `--release` with the verify lane deselected refuses outright (no release verdict is printed
  over an unexamined AC layer), a verifier blocked by the external-provenance trust boundary
  reports as *unproven* rather than as a red AC (with `--allow-external` to run it once the
  content is trusted - a passthrough, never a bypass), and a story set with no executable
  `Verify:` expression at all now fails, because a lane with nothing to prove must not read
  as proof.
- **Cross-repo `Depends on:` resolution in the tranche audit (CR0224).** A dependency on an
  artefact in a sibling repo is resolved through the PVD manifest instead of being reported
  as unmet. The resolver that already worked inside `blocker_sweep` is lifted into
  `lib/xrepo.py` and shared. An uncloned sibling degrades honestly: it is named, with its
  path, and never silently passed - and the search continues past it, so the verdict follows
  the disk state rather than the manifest's ordering. Projects with no manifest are
  unaffected.

### Fixed

- **`curl ... | bash` installed nothing, silently (BG0122).** The source-vs-execute guard at the
  bottom of `install.sh` compared `${BASH_SOURCE[0]}` with `$0`. Piped, bash reads the script from
  stdin, so there is no source file: `BASH_SOURCE[0]` is unset while `$0` is `bash`. The test
  failed, `main` was never called, and the installer defined its functions, fell off the bottom and
  exited 0 - no output, no error, no install, for the exact one-line invocation the README
  advertises. The guard now falls back to `${BASH_SOURCE[0]:-$0}`, which runs `main` when piped and
  when executed as a file, and still suppresses it when sourced (so the functions stay
  unit-testable). The suite could not have caught this: it only ever sourced the script, the one
  mode that was never broken. `tools/tests/test_install_piped.py` now pipes the installer for real
  and asserts on stdout, not the exit code - the broken script exited 0.

- **The engagement floor's shared-commit gap is closable with a `Refs:` trailer (CR0239).**
  The floor could not catch understatement in a commit that named two work-items, because git
  cannot attribute a file to one id among several. A `Refs: <id>` line in the commit body is now
  read as an explicit statement of which id owns the change: the git leg attributes that commit's
  files to each id a trailer names, closing the case a bare co-named subject left open. The
  attribution is strictly additive - keyed on the commit subject, a body trailer can only raise a
  unit's file count, never lower it, so a conventional "see also" `Refs:` on a solo commit cannot
  disarm that unit's own check. An opt-in `commit-msg` hook nudges an author to add a trailer when
  a subject names several ids; it warns rather than blocks, and only blocks under an explicit
  strict opt-in. Consuming projects are never forced onto the convention.

- **A mechanical engagement floor: ship a multi-file change with no planning and the gate
  refuses (CR0229).** The v4 benchmark showed weaker models judging a multi-file, spec-touching
  ticket too small for ceremony and shipping the hidden-requirement defect the ceremony catches,
  while stronger models engaged unprompted - so the threshold cannot be left to the model's own
  judgement. A deterministic `engagement-floor` gate lane now refuses a shipped unit that neither
  planned (acceptance criteria, a `Verify:` line, or a linked plan) nor declares a real
  single-file footprint in `Affects:`. The signal is a file count and a presence check, no model
  call. A change is judged multi-file from its declared `Affects` and, as a cross-check against
  understatement, the source files its own commit touched; adoption is gated by a cutoff so the
  floor does not fail the existing backlog, and a cutoff set beyond the current work is refused
  rather than silently disarming the floor. What the floor guarantees is stated precisely: pure
  omission cannot dodge it, and understatement is caught when a unit's commit names only that
  unit. Understatement in a commit shared with another work item is a known limit - git cannot
  attribute a file to one id among several - and is tracked for a commit-id convention that would
  close it. The operator opt-out is a recorded waiver, not a silent switch. Pairs with the
  doctrine rule shipped in v4.

- **A required review leg can no longer be waved away in prose (BG0110).** The unified review's
  required legs are PRD, TRD, TSD and Persona. When one was absent, the review - being
  model-authored prose - could reclassify it as "optional polish" and still pass, so a required
  document could stay missing indefinitely while every review read clean. Leg presence is now
  machine-visible (`review_prep` reports each leg as present, absent, or waived), and a
  `review-legs` lane bound under `gate --release` fails on any required leg that is absent and
  unwaived. The only way past it is an explicit, recorded waiver - a decisions-log entry stating
  the leg is intentionally out of scope, which the review then reports as "waived (D00xx)". The
  lane is bound, so it cannot be skipped or excluded away. The waiver primitive is general (it
  names a subject, a leg or any rule), so later gates can reuse it. The CODE leg is deliberately
  out of scope: it has no single artefact whose presence can be tested.

- **Uniform CLI grammar across the skill scripts (CR0234).** Three grammar inconsistencies that
  each cost an agent a wrong turn are closed, and a conformance sweep now fails the build if a new
  script reintroduces the class. `--root` is accepted before the subcommand on every root-dealing
  script (and after the verb where the subcommand takes a root), instead of each script choosing
  its own placement. A repeated status selector unions rather than silently discarding an earlier
  value - `sprint plan --crs Proposed --crs Deferred` now plans both, where before it dropped
  `Proposed` without a word and produced a plan that was quietly wrong. And `transition set`'s
  all-or-none verdict error now names `transition annotate` as the path for an identity-only
  stamp, rather than leaving the agent to rediscover it. The sweep walks every script's argparse
  tree and checks root placement, the store-versus-append mismatch on repeatable flags, the
  format-flag vocabulary, and that no `--root` alias binds a divergent destination.

- **Cleanup wave: rendering, recognisers and guards, delivered from the sprint's own reviews
  (BG0113, BG0116, BG0117, BG0119, BG0120, CR0238).** A supplied field no longer swallows the
  template's `###` subsection prompts beneath the section it fills (BG0113); a consuming
  project's first retro or review bootstraps its index instead of landing as drift, and a fresh
  index of every type lints clean from creation (BG0116, BG0120); a prose field can no longer
  forge a metadata line the artefact reader would take for provenance - the escape now mirrors
  the field reader across its anchor set and whitespace class, and the low-severity consolidation
  bullet renders a multi-line summary faithfully (BG0117); the engagement floor's declared-flag
  and file-count now use one recogniser so they cannot disagree (BG0119); and the consolidation
  filer routes its revision row through the one shared writer, guarded at source (CR0238).

- **The release gate tells an omitted verifier from a declared manual one (CR0237).** The AC
  verifier counted an acceptance criterion with no `Verify:` line and one that says `Verify:
  manual` into the same bucket, so the release vacuity guard had to be repo-wide: one executable
  AC anywhere let every unverified story through, and under grandfathering, deleting a rotted
  `Verify:` line reached a green release. The two are now separate - an omission is *unspecified*,
  a declared judgement is *manual* - and the guard is per-story: a story with an unspecified AC
  fails and is named, a story whose ACs are all declared-manual passes. This closes the last route
  by which a rotted verify layer reached a tag.

- **The gate's coverage guard no longer certifies a gap it was written to catch (BG0114).** The
  `documented` conformance stage could appear as non-conformant with no remediation hint, and the
  test meant to catch a missing hint passed only because its own expected set shared the omission -
  a guard handed its own answer key. The same blind spot was live in two more checks: `reconcile`
  (three drift kinds, including the one that masks unfinished work) and `audit` (four, including a
  unit whose verifiers already pass being told "not ready" with no way forward). Each check now
  exposes the kinds it can emit as one vocabulary the guard derives from, pinned to the real
  emission sites by a test, so a new kind without a hint fails the build. Eight remediation hints
  added; the one shipped hint whose command did not exist is corrected.

- **The creators emit lint-clean tables (BG0112) and extension-less files count as a footprint
  (BG0118).** A freshly created full-template artefact tripped the workspace's markdown table
  rules - padded delimiter rows and dead handlebars loop markers left inside table bodies - so a
  new plan, bug, test-spec or workflow started life failing the lint the project enforces. The
  templates are fixed and a round-trip check now lints created artefacts against those rules (it
  skips honestly when the linter is absent, never a false pass). Separately, the engagement floor
  recognised only files with a dotted extension, so an honest single-file declaration of a
  `Makefile` or a dotfile was wrongly refused; it now accepts an extension-less real file while
  still rejecting prose.

- **Creator input fields can no longer forge metadata or inject an executable check (BG0115).**
  A line break in a creator's input field broke out of its metadata line or table cell, because
  the value was interpolated raw. Filed as a cosmetic newline in `--author`, it was a class: a
  `--title` carrying a newline forged the `Status` line, so a bug could be born `Fixed` and every
  reader downstream (reconcile, the dashboards, the transition gate) believed it; a `--ac`
  carrying a newline injected a sibling `- **Verify:**` line that the AC verifier read back and
  executed. Every field a creator writes into a metadata line or a table cell is now refused if
  it contains a line break - across the whole break class, not only `\n` - at the writer, so the
  value written is the value that was checked. A refused create writes nothing and burns no id.

- **The creators record the authorship they were given, not a hardcoded one (BG0109).**
  `file_finding.py` wrote `audit` into every Revision History row regardless of `--author`,
  and `artifact.py` wrote the literal `sdlc` while dumping a full `Name; type; version` triple
  into index cells that should carry a name. The provenance tooling was recording the wrong
  provenance. All three creators now resolve authorship once, through the shared resolver, and
  write the row through a single writer that escapes the value, so a name containing a pipe can
  no longer shift a table's columns.

- **The deterministic creators now emit artefacts the deterministic validator accepts
  (BG0108).** A schema-v3 decomposition of 31 artefacts opened with roughly 130 validator
  errors, and three separate agents each rediscovered and hand-stamped the fix. The creators
  (`artifact.py new`/`batch`, `file_finding.py file`, and the consolidation CR) now stamp
  `Raised-by`, carry the Impact and effort block a CR requires, and write the `Persona` line
  only when a persona is named. Content supplied to a creator now reaches the artefact:
  `--template full` previously grafted the core template over the caller's summary, steps,
  fix, options and recommendation, so `batch` - which defaults to `full` - returned exit 0 and
  a clean validator over an artefact the caller's words never reached. The guard against a
  recurrence is a parametrised create-then-validate round trip across every creator, artefact
  type and schema era, asserting both that the validator is clean and that the supplied content
  landed. A content-less scaffold still reports its unfilled placeholders, deliberately: making
  it green would mean writing non-AC text into the acceptance-criteria section, which passes
  the validator's `no-ac` rule *and* promotes an unspecified story to `specified` in the
  conformance gate.

- **Lessons written with `--global` are no longer lost on the next skill update (BG0111).**
  `lessons.py` resolved the skill tier relative to the *running* script, which in real use is
  the installed copy under `~/.claude/` - not a git repository. Every `--global` lesson was
  written into a directory the next update replaces, and the tool reported success. Nine
  lessons had already been written there. `--global` now refuses, loudly, to write anywhere a
  lesson cannot survive: outside a git work tree, into a gitignored directory (the vendored
  `.claude/skills/` case, where `--is-inside-work-tree` alone is not enough), or into a
  registry git does not track. It names which of the three it hit. The destination resolves
  from a `skill_source_repo` config key, and the running-skill fallback now refuses an
  installed or vendored copy rather than writing a lesson a commit there could never ship.
  **The project tier is now the documented default; `--global` is the deliberate promotion.**

- **CI portability: the schema-v3 backfill no longer uses a Python 3.13-only API
  (BG0105).** `Path.read_text/write_text(newline=)` failed on CI's 3.12 while local 3.14
  passed - now an `open()` pair with identical semantics, comment naming the 3.10 floor.
- **The install downgrade guard now understands semver pre-release precedence (BG0106).**
  Plain `sort -V` ranked `4.0.0-rc.1` above `4.0.0`, refusing every rc copy the GA
  upgrade; cores now compare via sort -V with pre-release precedence on equal cores.
  Found live when the GA forward-port was refused; seventeen edge cases critic-driven.

- **CI installs pytest for the bench harness's class-D grader (BG0107).** audit_quiz.py
  shells `python -m pytest` inside fixture workspaces with no fallback; the runner lacked
  the module, failing the grader's first CI exposure.

v4.1 scope is the EP0031 + EP0032 sprint; the tag cuts when the backlog empties.

## [4.0.0] - 2026-07-10

### Added

- **The white paper ships: "The Mill, Not the Engine" (docs/whitepaper.md + a designed
  PDF).** The standalone deep description for the engineering leader evaluating an agentic
  SDLC: the procedural-problem argument, the layer-nobody-governs positioning built from a
  seven-paper consensus check of the genre (no competitor named), the five-instrument
  operating model, the benchmark quadrant and pricing exhibits, the generated team, the
  operationalised-practice thesis, a worked example from this repo's own audit trail,
  governance/attestation, adoption, blunt limitations - and a claims register mapping every
  load-bearing claim to its verification path, a device the genre does not have. Gated by
  all three seats (reader value, technical accuracy against code, claim-by-claim recompute),
  each REJECT repaired before approval. `tools/whitepaper_pdf.py` renders the distributable
  PDF (cover, exhibits, print typography) from the same markdown in one command.

- **The engagement floor ships in v4 as doctrine (the benchmark's direct product
  consequence).** A multi-file change in a spec-bearing repo now REQUIRES the planning pass
  (spec delta naming every interacting requirement, one acceptance criterion per interaction)
  before code - a hard rule, not a judgement call, because the rerun measured judgement-gated
  engagement performing no better than no process on base models while the mandated pass cut
  escapes 4-5x for ~10-20% more tokens. Scale-to-size judgement still governs everything above
  the floor; `engagement_floor: judgement` in `.config.yaml` is the explicit opt-out. Doctrine
  rule 16, the shipped agent-instructions template, and the config reference all carry it; the
  mechanical enforcement (gate refusal) follows in v4.1 (CR0229).

- **The benchmark was rerun against the v4 release candidate before GA, across three model
  eras, and published whichever way it pointed (docs/benchmarks/2026-07-10-v4-rerun.md).**
  72 oracle-scored runs plus a post-hoc solution-quality rubric and the protocol's
  auditability quiz. Headlines, honest both ways: on the current frontier model the frozen
  fixtures' traps no longer bite in any arm (30/30 clean; single-ticket pipeline overhead
  ~1.4x, not the July 3.1x); on the base models most teams deploy the hidden-requirement
  trap still ships in most runs, and judgement-gated process gave no protection because the
  agents judged the ticket too small for ceremony exactly when they needed it - the July
  founding observation reproduced a generation later. Two v4.1 CRs filed from the findings:
  a deterministic engagement floor, and a phrasing-brittle harness oracle. Every figure in
  the report was independently recomputed from the raw rows by the reviewing critic.

- **EP0030 - team generation: fresh named seats grown from the project.** `persona generate
  --team` analyses the PRD/TRD/config/repo-map onto behavioural variables and risk axes (never
  demographics), asks hard-capped multi-choice questions only where signals are ambiguous, and
  generates fresh named individuals into `personas/seats/` - 3 core roles plus up to 2
  signal-earned extras, cast capped at 5. `persona_gen.py` is the deterministic floor:
  provenance stamp + content hash discriminate authored from generated cards, so an operator's
  edit promotes a generated card to authored and a re-run can never clobber it; batch-accept
  clears the provisional labels, headless runs keep them and `status` surfaces the count.
  `validate.py seats` (with `--require-stamp` for just-written cards) is the error-level floor:
  declared role, review render, clean demographic denylist, one card per role, valid provenance
  stamps, and a named path it cannot match is itself an error (a guard never vacuously passes).
  `--stakeholders` generates the other side of the table into `personas/stakeholders/` on the new
  stakeholder template - goals, veto lines, evidence-they-read, Cooper Customer/Served designation,
  and the buyer-never-overrides-the-Primary arbitration rule stated on every card; the same
  `--require-stamp` gate verifies their stamps, `validate.py personas` learns the stakeholder
  schema (advisory), and `consult stakeholders` groups on the declared type and names any
  still-provisional card in its output header. Stakeholder cards keep the provisional label until
  `persona review` clears it - assumption personas stay labelled until validated. Repository
  review closes with a team offer. Eval scenario 07 exercises the flow on an ambiguous-by-design
  fixture. The consult output for stakeholders renders one section per declared type actually
  present (legacy Users/Business/Technical only for untyped cards), and the malformed-stamp rule
  covers stakeholder cards. The Cooper usage pass makes personas arbitrate rather than decorate:
  `validate personas` warns on a multi-Primary cast and errors when two Primaries declare the same
  optional `Interface:`; the `**Serves:**` tag on PRD features and stories feeds `validate serves`
  (dormant until first tag or config opt-in - resolves names to persona files, flags units serving
  nobody, prints a coverage table); every consult carries the Primary test and a per-seat objection
  quota (eval scenario 08 grades it); the scenario taxonomy is documented (validation scenarios
  test robustness, never drive layout); Life goals generate only on a strategy-tier signal.
  Positioning made honest and philosophical: the README's falsifiable exclusivity claim is
  replaced by the defensible conjunction (team GENERATED from your project + both sides of the
  table in one system + mechanical independence), with the evidence framed as blind-spot coverage
  rather than a smarter model. docs/why is reframed around the project author's published
  philosophy (the five-instrument cockpit, human-in-the-lead, the mill-not-the-engine,
  "specify together, build apart, review independently" mapped to the sprint loop, batch-to-goal
  as the answer to railway time), gains the operationalised-practice section (the enforced
  methodologies, and the refuse-to-proceed pattern they share), frames critic-verdicts as an
  attestation log in the separation-of-duties sense, and answers the closed-platform school
  anonymously ("Others argue that...") with the stories-are-where-proof-lives stance. Cross-model
  review documented as the stronger form of independence (doctrine + sprint critic flow). The
  meet-your-team offer is wired everywhere the team is met: PRD close, project upgrade, after a
  repository review, and a status/hint advisory - always an offer, never auto-run. The README is
  newcomer-first end to end: the meet-your-team moment shown as a console sketch, the philosophy
  in one breath, and every existing-project concern (what v4 changes, the numbering question's
  three answers, upgrade steps, breaking-change honesty, the dev/testing flow) moved to its own
  prominently-linked page, docs/existing-users.md.

- **EP0029 - v4 GA readiness (the final pre-GA dogfood sprint).** The numbering switch is an
  explicit operator question end to end: `migrate_v3 apply`/`adopt` refuse without `--confirm`,
  `adopt` is the new FORWARD-ONLY answer (existing sequential ids stay valid - in tickets, chat,
  docs - and only new artefacts mint ULIDs; the eras coexist by design), and the upgrade walk
  presents all three answers with the multi-team rationale. A reconcile era-divergence advisory
  warns when a clone's v2 config meets v3 ids (two writers in different modes). `reconcile`
  now covers epic breakdown checkboxes for EVERY unit type (bug/CR/story) in detect and apply -
  the lane immediately surfaced and synced 21 real unticked boxes the old census certified clean.
  `transition set --depth/--verdict/--reviewer/--author` is the one-call gated bug close (every
  predictable refusal before any write). `install.sh --from DIR` installs a local working tree
  (the dev-testing path) under the same identity + downgrade guards. `tools/eval_run.py` is the
  deterministic spine of the eval gate (fixture from a machine-readable spec, per-behaviour
  verdict recording, gate-fail on blocking failures and ungraded blocking behaviours), with
  executable fixture specs on the two v4 scenarios. The README leads with the v4 story:
  collision-free identity makes sdlc-studio truly multi-team compatible - human and agent teams
  filing concurrently across machines and git states.

### Fixed

- **Done means done again for every pre-v4 story: 43 rotted Verify lines repaired
  (BG0104).** The pre-GA verify pass exposed executable acceptance criteria pointing at
  renamed test files, refactored test names, retired scripts and invalid verifier verbs -
  accumulated silently across months of refactors. Every line now points at current truth
  (individually re-run, no guarantee weakened, two AC texts aligned to deliberately-changed
  semantics with dated provenance notes), five checks are honestly manual where their
  machinery was retired, and the full pass reads 348 verified / 25 manual / 0 failed. The
  ritual gap that let it reach the rc tag is CR0233 (gate --release, v4.1).

- **The amigos-to-seats migration can no longer create a role collision, and the documented
  default-install decline command is no longer a silent no-op (found by the late critic
  ceremony on CR0218).** A legacy card whose role is already claimed by a seats/ card is now
  skipped with a loud retire-or-reconcile report instead of being migrated into a duplicate
  whose lexical tiebreak could flip resolution away from the authored seat; and
  `--apply --with-default-amigos` now counts as requested work in the CLI apply gate, so the
  command the upgrade report itself recommends actually installs on a current project.

- **verify_ac lint no longer crashes over a stories directory (BG0103, found by a
  benchmark delivery agent dogfooding the v4 RC).** The lint subcommand referenced an
  undefined `repo_root` whenever `--story` was absent; it now takes its own `--root`
  (default `.`) and resolves the stories directory under it. Regression tests cover the
  directory and single-story paths.

- **project upgrade --apply no longer stamps a migrated v3 project's `.version` back to
  schema 2 (BG0102, found mid-sprint).** The stamp is now `max(project effective schema,
  CURRENT_SCHEMA)` - an upgrade can only ever raise it.

### Added (EP0026-EP0028, the backlog-clear sprint)

- **Retros and reviews are reconciled like every other type (EP0028, CR0211).** RETRO and RV
  were the last recurring numbered artefacts whose index rows were hand-edited. `reviews/` now
  has an `_index.md` (backfilled from the existing RV history), so `artifact new --type review`
  self-indexes like `--type retro` already did. `reconcile detect/apply` gained a meta lane that
  checks row presence for both `retros/` and `reviews/` - a numbered file with no index row, a
  row with no backing file, or a wholly missing index - keyed on the RETRO/RV id namespace the
  pipeline regexes exclude, tolerant of the house columns (Sprint/Delivered/Blocked, Title/Date)
  and the absent status/count block. It runs on the default sweep and on `--scope meta`, never on
  a single pipeline scope; `apply --scope meta` appends a missing row header-driven (orphan rows
  and a missing index stay report-only). The sprint-close retro step and the repo-review workflow
  now point at the deterministic `artifact new` path.

### Changed

- **Quality and docs debt sweep (EP0028, CR0208).** A themed pass over Low/Medium debt surfaced
  by RV0007. So far: dead code removed (`sdlc_md.METADATA_FIELD_RE`, `reconcile._SEP_LINE_RE` /
  `_is_sep_line`, all unused) and duplicated helpers folded to one authority (`reconcile.
  _canonical_counts` collapsed into `_row_counts`; `artifact._schema_v3` delegates to
  `sdlc_md.is_schema_v3`; `sprint._default_branch` delegates to the now-public
  `next_id.origin_default_branch`). Exit-code drift fixed: `spec_guard` and `plan_review`
  check-failures now return `1` like the rest of the family (argparse keeps `2` for usage
  errors). Test-output hygiene: the agent-instructions, budget and version checkers' reports no
  longer leak past the unittest summary (the named cases; broader error-path stderr from other
  suites is a separate sweep). `--format json` added to the report/check verbs that lacked it
  (`spec_guard check`, `plan_review check`, `ledger show`, `critic show`, `doc_freshness`,
  `persona_resolve resolve`, `loop_guard record`) via the shared `sdlc_md.add_format_arg`, so a
  machine caller reads them uniformly (`github_sync state` and `loop_guard status` were already
  JSON); a new `test_json_report.py` asserts each emits parseable JSON.
  Small correctness fixes: `review_generate scan` accepts the secret via `--secret-env` (preferred,
  off the process list) or `--secret-stdin`, not only argv (CWE-214); the artefact-title regex now
  recognises a v3 ULID id so a ULID-titled artefact that lost its Status line is not dropped from
  the census; `reconcile`'s master-table tie-break compares all equally-ranked winners, not just
  the first and last (a distinct table between two mirrors is no longer misread as indistinguishable);
  the Low-severity consolidation CR no longer doubles its theme into
  `low-severity-low-severity-...` in the title or filename. `check_links` gained a root-docs pass:
  the repo-root docs (README, AGENTS, CLAUDE, ...) had never been scanned, so a broken `.md` link
  there was invisible; it now file-checks their links (anchored or not). The skill tree still
  checks only anchored intra-skill references - its templates and doc examples carry many
  legitimate non-resolving bare links (`../prd.md`, `path/to/guide.md`). The pre-commit hook now
  runs the unit suites when `templates/` is staged too (not only `scripts/`/`tools/`), since
  several tests assert over the shipped templates. Git-invoking tests share a new `gitutil` helper
  that neutralises the host git config (`GIT_CONFIG_GLOBAL`/`SYSTEM` -> /dev/null), so a
  developer's `commit.gpgsign` no longer makes the suite fail or hang. The provenance-tag style
  guard now also covers `scripts/lib/*.py` and every `templates/**/*.md` (the seat cards and
  index templates ship too); the live leaks it had missed (a dozen `(CRxxxx)`/`(RFCxxxx)` tags in
  `lib/sdlc_md.py`, four in the amigo cards) are stripped. Private names used across modules are
  now public: `reconcile.DEFAULT_TYPES`, `reconcile.index_row_ids`, and `sdlc_md.b32` (callers no
  longer reach into a `_`-prefixed name). Anchor-doc drift corrected: `AGENTS.md`'s file counts are
  now ranged (`50+` reference / `nearly 40` help files, was a stale `42`/`31`); `help/arguments.md`
  documents the full `triage -> plan -> design -> done` goal ladder (was just `done`/`design`); and
  `help/references.md` lists `reference-outputs.md` (it was the one reference file the catalogue
  omitted). `install.sh --target auto` no longer selects `copilot` on a global install (copilot is
  repo-scoped only, so auto would write `.github/skills` into the current directory). Two new eval
  scenarios cover v4 surfaces the frozen four missed: `05-schema-v3-identity` (ULID allocation,
  ULID-epic wiring, reconcile coverage) and `06-independence-gate` (author != reviewer and the
  verified-depth gate on terminal status). `sdlc_md.iter_tables` and `verify_ac.parse_story` are
  now fenced-block aware: a `|`-row or a `- **Verify:**` line shown as an example inside a fenced
  code block is skipped, so a documentation example table is never tallied and an illustrative
  verifier never reaches shell execution. The two worst complexity hotspots are decomposed:
  `sprint.cmd_plan` (cognitive 73 -> 10) and `github_sync.cmd_push` (85 -> 9), each split into
  named, single-purpose helpers under the cognitive-15 line with behaviour preserved (the
  existing sprint and github-sync suites stay green).
- **One CLI argument grammar across the script family (EP0028, CR0210).** The scripts disagreed
  on how ids and targets were passed - `audit check` took `--ids` comma-separated, `transition
  set` forced exactly one of `--id`/`--ids`, `artifact revision` required `--ids`, `ledger
  record` used `--tranche` where sibling recorders use `--unit` - and each mismatch cost an agent
  a `--help` probe. Now every id-taking batch verb accepts the same form via the shared
  `sdlc_md.add_ids_argument` / `resolve_ids`: a repeatable `--id` OR a single comma-separated
  `--ids` (kept as a legacy alias), merged into one de-duplicated list; `ledger record` gains a
  `--unit` alias. A new `tests/test_cli_grammar.py` sweeps the argparse definitions so a
  non-conforming new command fails the suite; `best-practices/script.md` and `reference-scripts.md`
  document the grammar once. Minor shape change: `transition set --format json` now emits a scalar
  object for exactly one id and a list for several (previously the list depended on which flag was
  used); the documented scalar `--id` path is unchanged and no consumer parsed the old list-of-one.

### Fixed (EP0026-EP0028, the backlog-clear sprint)

- **install.sh refuses to silently downgrade (BG0100, found dogfooding).** Running `install.sh`
  from inside the dev repo downloads the published release and its sweep refreshes every copy on
  the machine, including the repo's own working tree; when the remote was behind local (an unpushed
  dev checkout), that silently reverted newer work. Both the primary install and the sweep now
  compare versions (`version_lt` via `sort -V`, tolerating `-rc` and non-semver tokens) and **refuse
  to overwrite a copy newer than the version being installed**, printing a loud warning and leaving
  it untouched; `--allow-downgrade` forces it. The silent-downgrade vector is closed; a live dev
  checkout being swept at the same-or-newer version still warrants `--no-sweep`.
- **Era completion - v3 identity everywhere (EP0028; BG0086/87/88/93/97/99).** Six fixes so the
  schema-v3 default behaves, batch critic-approved (suite 1532, drift 0): `artifact new/batch`
  now links a story to a v3 ULID epic (`_find_epic` resolves the full record id instead of
  splitting on the first dash, which yielded a bare `EP`); `migrate_v3` id minting scales past
  1024 files (counter width grows with the entry count) and stops polluting dash-named slugs, a
  uniqueness assertion fails loud on any collision; `short_ulid` carries a real 2-char entropy
  tail so two uncoordinated writers in the same instant no longer mint identical ids (with the
  allocator's directory-glob retry as the single-writer backstop); `config.get` degrades to the
  caller's default with a warn-once when config can't load and `route.estimate` survives the
  same, with the PyYAML runtime dependency now documented; `--format json` on `reconcile apply`,
  `reconcile fields` and `verify_ac report` signals failure with a non-zero exit like the text
  path; and the finding filer backtick-wraps underscore identifiers in rendered prose so it
  stops minting markdownlint-breaking artefacts.
- **Reliability tier - Low-severity debt batch (EP0027, CR0207; US0119).** Ten small hardening
  fixes, critic-approved: `atomic_write` now preserves the existing file's permissions instead
  of flipping every rewritten index/artefact to owner-only 0600; `loop_guard`/`resume` `.local`
  state writes are atomic (a crash cannot reset a guardrail); the `http` verifier refuses a
  scheme-less URL in every mode (not just restricted); `npx jest` runs `--no-install`; the
  cascade watermark uses `max(mergedAt)`; `next_id`'s `ls-tree` has a timeout;
  `check_neutrality` fails loud when it cannot list files; the em-dash guard is `grep -P`-free
  (BSD/macOS portable); `install.ps1` ships the CHANGELOG (parity with `install.sh`); and CI
  installs PyYAML before the first Python run. Four larger items (batch-op amortisation,
  `detect_type` triple-read, gh pagination, mutation SIGKILL sidecar) are deferred with a note.
- **Reliability tier - push adopts an existing issue instead of duplicating (EP0027, CR0206;
  US0118).** A crash or `gh` timeout after a create was accepted but before the local stamp
  landed made the re-run create a second GitHub issue for one record. `push` now lists the
  type's sdlc-labelled issues once and adopts an existing `[rec_id]`-titled issue (stamping the
  local file with its number) instead of blind-creating; the bracket makes the prefix match
  collision-safe (`[CR-0001]` never adopts `[CR-0010]`), and the adopt re-parses for the
  post-stamp hash so the next push skips cleanly.
- **Reliability tier - concurrency floor completed (EP0027; BG0076).** CR0183's advisory lock
  covered only `artifact new`; `file_finding` and `new_batch` allocated ids and wrote outside
  it, so concurrent filers (multi-agent waves) minted the same id and clobbered index rows (a
  4-way collision was reproduced). `file_finding.file_finding`, `artifact.new_batch` and
  `meta_new` now allocate-and-write under `sdlc_md.allocation_lock`, and the finding-filer
  body, batch writes, `meta_new`, and the `transition` truth-file status stamp + epic cascade
  use `atomic_write` so a crash mid-write can never truncate a truth file. A red-first
  concurrency test mints 8 distinct ids with one index row each; the closing critic verified
  the `new_batch` re-indent is purely mechanical and the lock is deadlock-free.
- **Reliability tier - installers copy-then-swap (EP0027, CR0205; US0117).** `install.sh` staged
  `rm -rf $dest; cp -r ...` - a copy that failed between the two left the user with nothing or a
  half-copy. Both the install and sweep-refresh paths now stage into a same-filesystem sibling
  and atomically rename it into place; a failed copy returns non-zero and leaves the previous
  install byte-for-byte intact. The closing critic caught a latent `rm -rf` footgun (a same-line
  `local dest="$parent/..."` resolved via caller scope) - fixed with the declaration split and a
  caller-scope regression test.
- **Reliability tier - verify_ac discovery/contract and sync failure honesty (EP0027; BG0083,
  BG0084, BG0089, BG0092).** `verify_ac` now excludes companion docs and non-US files from
  story discovery (a consultations note's quoted example `Verify:` lines no longer run
  arbitrary shell - BG0083); an explicitly-named `--story` that does not exist exits 2 instead
  of a silent 0 read as "all ACs green" (BG0084); relative `--dir`/`--report` resolve against
  the repo root, so a run from any cwd with `--root` writes the report where the Done gate reads
  it (BG0089); and `github_sync push` leaves `last_push` unstamped and exits non-zero on any gh
  create/edit failure, saving only the mappings that succeeded (the BG0064 pull fix, now on the
  push side - BG0092). All four independently critic-approved.
- **Reliability tier - index-writer crash/reopen safety (EP0027; BG0081, BG0082, BG0091).**
  Three census-touching defects, each red-first and independently critic-approved: a reopened
  (archived-then-live-again) artefact was permanently shadowed by its stale archive row - now a
  live index row always wins over an archive row (BG0081); the index rewriter bled a previous
  data table's Status column into a following unclassifiable table (Dependencies/Notes),
  clobbering an author-maintained cell - now an unclassifiable header resets the tracked columns
  (BG0082); `archive.py` appended moved rows before trimming the live index with no dedupe, so a
  crash between the two writes then a re-run duplicated every archived row - now the append
  dedupes against the archived ids and uses atomic writes (BG0091).

### The 2026-07-09 preparation cut (same release)

The maturity release. Schema v3 (distributed ULID identity + structured authorship/evidence
enforcement) ships **active**, not dormant, and becomes the default for new projects.

### Breaking (2026-07-09 cut)

- **Schema v3 becomes the default for new projects.** `init` now scaffolds `schema_version: 3`
  (ULID identity + authorship/evidence enforcement). Existing and unpinned projects are NOT
  auto-flipped: the code default stays 2 and they upgrade explicitly via the `project upgrade`
  v2-to-v3 walk (capability delta -> `migrate_v3` dry-run -> apply -> re-baseline). Migration
  action for a consuming project: run `project upgrade` and follow the presented walk; the
  migration was rehearsed on two real projects (see `sdlc-studio/reviews/v4-migration-rehearsal.md`).

- **Hygiene: bugs closed, indexes archived, validate accepts v3 ULID ids (EP0025, CR0198/CR0199; US0112).** Closed BG0067/0068/0069/0070 (Fixed -> Closed); archived 57 story + 39 cr terminal rows into the `v4.0.0-rc.1` release batch (live indexes bounded, census unaffected via the archive-union). `validate` now accepts a v3 ULID id (`BG-01JQK3F8`) via a new `sdlc_md.is_v3_id`, instead of flagging it `id-format` - a v4 project's ULID artefacts validate cleanly while garbage and v2 ids classify as before.
- **Provenance-tag lint guard widened to catch US-form pairs (EP0025, CR0201; US0111).** The guard missed US-form ids, letting `(US0101/CR0186)` through in a shipped comment. It now also flags a US-led provenance pair joined by `/` or `;` (`(US0101/CR0186)`, `(US0090/CR0194)`), and its file glob covers the consuming-facing `templates/config*.yaml`. Lone US ids and comma/hyphen lists (`(US0045, US0046)`, `(US0001)`) stay unflagged - they are indistinguishable from legitimate example ids in tree diagrams and sample output. Five leaked US-pair tags stripped from scripts/reference/config-defaults, with a unit test.
- **Deterministic `status.py backlog` census (EP0025, CR0199; US0110).** A new `backlog` subcommand lists the non-terminal (open) artefacts per type and status from a file census - the deterministic answer to "what is left in the backlog?" that no longer needs a hand-parsed `_index.md` grep. Terminal detection uses the shared vocab's full terminal set (`is_terminal_status`), not a hardcoded subset; `--type` filters, `--format json` for tooling, and an empty backlog says so explicitly.
- **rc-tag readiness checklist enumerated (EP0024, CR0198; US0109).** `sdlc-studio/reviews/v4-rc-readiness.md` lists each rc-tag gate (portable gate green, version at rc.1, migration rehearsed, EP0014 closed, open-bug count 0, drift 0, suites green) with a live check command, so cutting `v4.0.0-rc.1` is a checklist read. It honestly reads NOT-YET-GREEN today: the open-bug gate is red until US0112 closes the four Fixed bugs.
- **Majors-only section added to the release-gate checklist (EP0024, CR0198; US0107).** `templates/workflows/release-gate.md` gains a section 8 for breaking releases: breaking-change inventory in the CHANGELOG, migration rehearsed on two real projects with evidence linked, eval scenarios re-run for the new major, docs saying the new major, and rc-first-from-a-green-gate-with-a-soak. The rc-tag decision becomes a checklist read.
- **v3 to v4 upgrade walk presented as a directed sequence + rehearsed on two real projects (EP0024, CR0198; US0106).** `project upgrade` now presents the v2 to v3 migration as an ordered walk (capability delta -> `migrate_v3` dry-run -> `migrate_v3` apply -> re-baseline) via a new `migration_walk`, in both text and `--format json`; the schema flip stays the deliberate `migrate_v3` id migration, never an auto-apply. The walk was rehearsed dry-run against two real consuming projects (evidence in `sdlc-studio/reviews/v4-migration-rehearsal.md`, names redacted); the rehearsal surfaced BG0070 (a per-artefact `git log --follow` makes migration impractical on a large project) - rc-relevant.

### Changed (2026-07-09 cut)

- **New projects start on `schema_version: 3`; existing projects untouched (EP0024, CR0198; US0105).** `init` now seeds `schema_version: 3` (ULID identity + authorship/evidence enforcement) into a new project's `.config.yaml`. The code default stays 2 and the schema reader is override-only (it does not merge `config-defaults.yaml`), so an existing or unpinned project is never auto-flipped - it upgrades explicitly via `project upgrade`. This dogfood repo is pinned to `schema_version: 2` as a safety belt. Era-gate regression test proves a v2 project's v3-gated paths stay dormant.

- **Complexity hotspots decomposed, latent test issues fixed, small cleanups + a debug channel
  (EP0022, CR0187; US0103).** `reconcile.detect_type` (115 -> 40 lines), `transition.transition`
  (128 -> 45) and `conformance.detect_conformance` (118 -> 84) are decomposed into named,
  behaviour-preserving helpers (the full suite is unchanged and green); `lessons.render_global_lesson`
  was already within bounds. Test fixes: `test_table_parsers.py` uses a raw string for the escaped
  pipe (no future SyntaxError) and the verify tests route `main()` through a quiet helper so they no
  longer leak `[APL]`/`wrote` lines into suite output. Cleanups: `gate.py`'s redundant
  `except (OSError, Exception)` narrowed to `Exception`; `artifact.py`'s `meta_new` dry-run predicts
  `indexed` honestly instead of always `False`. New opt-in diagnostics: `sdlc_md.debug`/`roll_jsonl` -
  `SDLC_DEBUG=1` emits one stderr line from each named swallowed-advisory site (telemetry, jest cache,
  sprint complexity, reconcile blocker-sweep), and the append-only `.local` logs (telemetry/verify
  history) roll to a bounded size.

- **"Find an artifact by id" and "a story's epic" consolidated onto the shared layer (EP0022,
  CR0187; US0102).** `lib/sdlc_md.py` gains canonical `find_by_id` (alias-aware) and
  `story_epic`; `audit.find_artifact`, `transition._find` and `lite_profile._story_epic` now
  delegate to them, so a lookup fix lands in one place. `reconcile.py`'s `detect`/`apply`/
  `fields`/`archive` all speak `--format json`, and the parity is locked by a test so a new
  subcommand cannot ship text-only. Maintainability only - no behaviour change.
- **`reference-scripts.md` split into a lean index + grouped detail pages (EP0020, CR0200;
  US0096).** The 643-line catalogue (past its 600 budget three sprints running) is now a lean
  index of one-line summaries linking to five grouped pages (`reference-scripts-{create,verify,
  review,upgrade,domain}.md`), each under budget; the `643` allowlist is removed. `doc_coverage`
  unions `reference-scripts*.md`, so the doc-coverage floor still hard-fails a missing entry.
  Documentation reorganisation only - no script behaviour changed.

### Added (2026-07-09 cut)

- **A disabled commit gate is now detectable (EP0026, CR0202; US0113).** New advisory
  `hook-enabled` gate lane plus a matching `status` dashboard warning: when a git work tree
  ships `.githooks/pre-commit` but `core.hooksPath` is unset or points elsewhere, both surfaces
  say so and name the fix (`bash tools/enable-hooks.sh`). Deliberately silent everywhere it
  means nothing - hook enabled, no tracked hook (every consuming project), or a non-git
  directory - so the lane carries signal, not standing noise. One shared
  `gate.hook_enablement_gap` message keeps the two surfaces from drifting.
- **Context tiering - status/hint read closed-artefact digests, not the full corpus (EP0023,
  CR0179; US0104).** A long-lived repo pays a growing token tax on every status/planning pass
  that re-reads the whole closed corpus. Once the closed-artefact count reaches
  `digests.min_closed` (default 500), `digest.py build` writes a filename-keyed mechanical
  digest (id/title/status/outcome/refs) and `status`/`hint` read a closed artefact's status from
  it instead of opening the original - the enumeration (`sdlc_md.iter_artifact_files`, now the
  basis of `artifact_files`) skips the is-artifact read for those trusted filenames. Measured on
  a 501-closed fixture: `status` reads 0 closed originals / 0 bytes vs 501 / 59,010 with no
  digest (recorded in CR0179). The digest is byte-stable (deterministic) and `reconcile detect`
  flags it as an advisory when it drifts from the census; a closed artefact still resolves by id
  (including a CR0167 alias) to its full original. Below the threshold the feature is dormant -
  no digest is produced or read, so a small repo sees no behaviour change.
- **Sync, state and verifier-sandbox hardening (EP0022, CR0186; US0101).** `github_sync push`
  now scans each record's title+body for secret-shaped tokens (GitHub tokens/PATs, AWS keys,
  AI API keys, Slack tokens, private-key blocks, credential assignments) and refuses to publish
  a flagged record to a public - or unknown-visibility - repo; findings are reported redacted
  (prefix + length, never the raw token), visibility is resolved lazily via `gh repo view` only
  when a secret is found, and `--allow-secrets` overrides for a confirmed-private target. The
  `http` verifier verb gains a scheme floor enforced in every mode (only http/https, blocking
  `file://`/`ftp://`/`gopher://` SSRF vectors) plus an opt-in host allow-list (restricted mode
  via `SDLC_VERIFY_HTTP_HOSTS`); the shared trust boundary with the mutation gate's `--test`
  command is documented in the `verify_ac` module. `version-check.json` and any nested `.local/`
  are named in `.gitignore` so machine-local state cannot land in a commit.
- **Supply-chain integrity: Actions pinned to commit SHAs + installer checksum verification
  (EP0022, CR0186; US0100).** Every GitHub Action in `.github/workflows/` is now pinned to a
  full 40-hex commit SHA (version in a trailing comment) so a moved tag cannot inject code into
  CI, and a new `tools/check_action_pins.sh` guard (wired into `npm run lint` and the pre-commit
  gate, with a unit test) fails if any Action reverts to a mutable tag/branch. Both installers
  (`install.sh`, `install.ps1`) verify the downloaded artefact against a published sha256 before
  extraction - the digest comes from `SDLC_STUDIO_SHA256` (an explicit pin) or a best-effort
  `<url>.sha256` sidecar; a mismatch aborts before any extraction, and
  `SDLC_STUDIO_REQUIRE_CHECKSUM=1` makes a missing digest fatal. Also untracks two `.local/`
  runtime files a broad `git add -A` shipped, and adds a `**/.local/` safety-net ignore.
- **Plan-review gate - a deterministic AC-vs-spec check before implementation (EP0019, CR0194;
  US0090, schema v3, opt-in).** New `scripts/plan_review.py` closes the N=5 "bad plan
  propagates" failure: a story with spec-derived ACs cannot reach implementation (In
  Progress/Review/Done, wired into `transition.py`) without an independent plan-review verdict.
  The trigger is **deterministic** (TRD ADR-006, no model judgement in fire/skip): it fires on
  any of three signals - the Affects/ACs cite a `plan_review.spec_globs` path, `affects_files`
  reaches `plan_review.affects_files_threshold` (default 5), or the routed difficulty band
  reaches `plan_review.min_difficulty` (default medium). `critic.py record` gains a `--phase
  {delivery,plan-review}` field (its own log, so a plan-review verdict never satisfies the
  delivery critique gate); `plan_review record` pins the verdict to the reviewed ACs by
  fingerprint, so a post-approval AC edit invalidates it. The only sanctioned skip is a
  recorded `> **Plan-Review-Override:**` field (auditable; not bypassable by `--force`). Dormant
  under schema v2. US0091 adds the reviewer's charter
  (`reference-agent-prompt-template.md#plan-review-charter`: the QA seat re-reads the cited spec
  section and flags any AC that inverts it as a blocking finding, escalating to blind
  re-derivation for high-difficulty units), an optional `> **Plan-Review:**` story-template slot,
  and a plan-review telemetry event (`telemetry.record_plan_review`, summarised as its own block
  so the gate's run count, verdict mix, and independent-review rate are measurable).
- **Spec-edit guard - an untraced edit to a requirements/spec document is a blocking finding
  (EP0019, CR0195; US0092, schema v3, opt-in).** New `scripts/spec_guard.py` closes the N=5 case
  where a worker edited the workspace spec to match its wrong implementation and review missed it.
  `check --changed <files> --story <file>` deterministically surfaces which changed files are
  requirements/spec documents (config `review.spec_paths`) and whether any AC cites a spec change;
  an `untraced` edit (a spec doc touched with no citing AC) is the signal the critic charter
  (`reference-agent-prompt-template.md#spec-edit-charter`) treats as blocking. A requested spec
  edit (an AC citing the path) stays legitimate; the traceability judgement stays with the critic.
  Dormant under schema v2.
- **Agentic triage - human sampling policy + triage-quality metrics (EP0014, CR0173; US0066,
  schema v3, opt-in).** New `scripts/triage_sampling.py`: `sample()` is a deterministic
  (seeded-hash) audit-sampling policy - every Critical, every raiser/triager severity
  disagreement, plus `triage.sample_rate` (default 0.20) of the rest; `metrics()` computes
  triage quality from the records (no hand-counting) - the false-positive rate (a finding
  triaged as real then closed invalid), severity inflation (triager vs raiser), and
  sampled-but-unreviewed findings as standing pending audit. Surfaced by
  `status triage-metrics`. New `triage.sample_rate` / `triage.always_sample` config keys.
- **Agentic triage - optional tranche reference (EP0014, CR0172; US0068, schema v3, opt-in).**
  An external orchestrator may stamp a record-only `> **Tranche:**` reference on an artefact
  (`artifact new` passes it through when supplied; sdlc-studio never allocates it), so the
  records answer "what shipped in tranche X" without sdlc-studio becoming a scheduler. `validate`
  gains a `tranche-shape` check (absent or valued is fine; present-but-empty is a malformed
  record; era-gated to v3), and `status tranche --value <ref>` lists every artefact carrying a
  given reference across all types.
- **Agentic triage - noise controls (EP0014, CR0173; US0067, schema v3, opt-in).** New
  `scripts/triage_noise.py` and a `triage:` config block add two creation-time controls, both
  dormant under v2: a **session cap** (`triage.session_cap`, default 20) refuses the N+1th
  finding of a session loudly (a session keyed by the `SDLC_TRIAGE_SESSION` environment
  variable, its count in `.local/triage-session.json`) so an agent cannot flood the backlog; and
  **Low-severity consolidation** (`triage.low_consolidation`, default on) folds a Low-severity
  finding into a themed consolidation CR - one per theme, carrying a `> **Consolidation:**`
  marker - instead of minting its own artefact, while Medium and above still get individual ones.
  Both `file_finding` and `artifact new` route finding creation through the controls, so neither
  path is a bypass.
- **Agentic triage - vocabulary and gated transitions (EP0014, CR0173; US0065, schema v3, opt-in).**
  Under `schema_version: 3`, findings (bug/cr/rfc) gain an `inbox` triage lane prepended to their
  status vocabulary, and `artifact.py` files a fresh finding into `inbox` rather than its per-type
  create status. A gated `inbox -> triaged` transition (`transition.py`) records the triaging seat:
  the target is type-specific (bug `Open`, cr `Approved`, rfc `In Review` - agent findings skip the
  human `Proposed`/`Draft` proposal states), it requires a structured `--triaged-by "Name; type;
  version"` and refuses loudly without one, enforces separation of duties (the triager must differ
  from the raiser; a solo human self-triage warns rather than deadlocks), and records the triager's
  severity via `--triage-severity` alongside the raiser's. All era-gated and dormant under v2, so
  existing projects are untouched.
- **Difficulty-aware model-tier routing** (RFC0026, CR0189-CR0191; US0083-US0085): new
  `scripts/route.py` - a deterministic 0-100 difficulty estimate per work unit (blast-radius
  cognitive/risk via `complexity.assess`, file scope, unresolved-path novelty, AC count,
  story points; an unresolved signal defaults to 0.5 and lowers confidence), banded to five
  abstract tiers (`tiny/small/medium/large/xlarge`) that a project maps to its own model ids
  in the new `routing:` config block (sparse maps degrade upward only). `sprint plan` stamps
  every unit with `difficulty` (always) and `tier`/`model` (when `routing.enabled`);
  `telemetry` records `tier_recommended/tier_delivered/model/escalated` and summarises per
  delivered tier. Advisory throughout - no gate reads a tier, no model API is called, and the
  critic is never a smaller tier than the author (medium floor for code units). Escalation on
  failure steps one declared tier within loop_guard's unchanged attempt cap. Shared
  `affects_files`/`resolve_affects`/`count_acs` helpers lifted into `lib/sdlc_md.py`.
- **Benchmark v2 + the calibration re-spike** (CR0192/CR0193; US0086-US0089, repo-only,
  not in the skill payload): tools/bench hardened (multi-file hidden-suite scoring,
  environmental arm isolation - the baseline arm's workspace contains no skill at all,
  automatic token/wall-time capture with disclosed manual fallback, arm R = routed pipeline,
  operator-priced cost index, min/max in summaries); two harder Tier-1 fixtures
  (`multifile-notify-digest`, `change-request-ledger-drift`), each validated
  red-on-naive/green-on-reference and independently fairness-reviewed; the held-back
  **Auditability** metric (`audit_quiz.py`: mutant-checked evidence citations +
  citation-validated trace answers; reviewer-independence descriptive at weight 0);
  `docs/benchmarks/protocol-v2.md` superseding pre-registration. The N=1 re-spike
  (3 arms x 2 fixtures) is published in `docs/benchmarks/2026-07-08-v2-respike.md`: the
  pipeline's mandated planning pass was the only arm with zero defect escapes, and the
  Auditability metric graded a real evidence-quality gradient. N=5: GO (D0013).
- **Benchmark v2 measured N=5 run** (D0014, repo-only): Tier 1 at N=5 per cell (30 runs +
  30 graded audit passes), Tier 2 via pre-declared cut #1. Published in
  `docs/benchmarks/2026-07-08-n5-run.md`: unstructured arms escaped 10/10 on notify-digest
  vs the mandated-planning arm's 2/5 (one-sided Fisher p 0.083, below conventional
  significance); Auditability tracked the escapes exactly; routing cut arm-R delivery cost
  to a 0.40 index on the easy fixture with zero escapes; the routed pipeline costs ~3.1x
  baseline tokens per single ticket. New documented failure mode - **a bad plan
  propagates**: two arm-R planners mis-pinned a spec rule in their ACs and the critic
  approved against the wrong oracle; in one of the two runs the worker went on to write the
  error into the workspace spec itself. Points at an independent AC-vs-spec conformance
  check before implementation.
- **Benchmark runner - calibration rows excluded by the tool, not by hand** (CR0196/US0093,
  repo-only, not in the skill payload). Protocol v2 forbids pooling calibration rows with
  measured ones, but producing the N=5 report needed hand-filtering that will one day be
  forgotten. `runner record` now stamps a `phase` field (default `measured`; `--phase
  calibration` for a calibration run), `runner summary` excludes calibration rows by default
  (`--include-phase calibration|all` opts them back in), and a one-time `runner backfill`
  stamps legacy rows (`v2n1` = calibration, else measured). `docs/benchmarks/protocol-v2.md`
  is unchanged (frozen).
- **Positioning refresh + the full value document** (CR0177/US0072): README reframed under
  the three hard constraints (anti-vibe-coding umbrella, greenfield equally visible,
  catalogue below the fold) with the now-unlocked team-shape and evidence paragraphs; new
  `docs/why-sdlc-studio.md` - a progressively-disclosed value argument (thesis, labelled
  operator-reported field results, benchmark evidence including the unflattering findings,
  economics, calibrated team-shape, open questions); agent-facing discoverability: root
  `llms.txt`, a For-agents README block, and SKILL.md gains NOT-for triggers plus
  namespaced openclaw metadata. Every claim critic-reviewed for calibration against the
  published benchmark data.
- **Upgrade re-baseline census (EP0020, CR0197; US0094, schema v3, opt-in).**
  `project_upgrade.rebaseline()` walks every non-terminal artefact and buckets its gaps against
  the capability delta - `backfill` (a mechanical stamp computable now, e.g. a missing
  `Difficulty`), `re-review` (matches a gate's deterministic trigger but lacks the verdict, e.g.
  a spec-derived story with no plan-review verdict), `residual` (judgement gaps). The bucketed
  report (empty buckets printed explicitly) surfaces from `project upgrade`. Read-only,
  deterministic, dormant under schema v2. `project upgrade --apply` (US0095) performs ONLY the
  mechanical `backfill` bucket - stamping a `route estimate` `Difficulty` band on units lacking
  it - idempotently, never touching the re-review/residual buckets and never fabricating history;
  `reference-upgrade.md` states the next-transition enforcement policy (a new gate attaches at an
  artefact's next transition, never retroactively).

- **Origin-drift pre-flight for `sprint plan` + branch-aware remote id allocation (EP0021,
  CR0188; US0099).** `sprint plan` now runs a `git fetch origin` + drift check: when the local
  clone is behind origin's default branch it warns (naming the commit count and any overlap
  between the incoming remote changes and the batch's own artefacts) and, under `--strict`,
  refuses - so a sprint is not planned against a stale checkout. Fail-safe: no remote, no git, or
  up-to-date behaves exactly as before. `next_id.remote_ids` now resolves origin's actual default
  branch (was hardcoded `origin/main`), so remote-aware id allocation also protects
  `master`/`develop`-default repos from re-minting an id the remote already holds. An AGENTS.md
  orientation bullet documents the fetch-before-trusting step.

### Fixed (2026-07-09 cut)

- **CI now runs the portable artefact gate, making the claimed hook/CI parity real (EP0026;
  BG0096).** `.githooks/pre-commit` and CONTRIBUTING both said "the same gate CI runs" while the
  Lint workflow ran only lint/tests/coverage/bandit - artefact drift, conformance or integrity
  breakage could reach a green CI. The workflow gains a `gate.py --root .` step (after
  setup-python, PyYAML installed so config-driven lanes fail loud); the two doc claims are now
  true as written.
- **Unit-lifecycle ergonomics: annotate verb, batched gate refusals, one-call close (EP0026,
  CR0209; US0116).** `transition annotate --id --field --value` deterministically stamps a
  metadata field (no more hand-editing artefact bodies for `Verification depth`) - with a
  gate-protection denylist the critic forced: it refuses Status/Triaged-by/Triage-severity
  (an ungated Status rewrite would have been an exit-0 bypass of the whole ladder), refuses
  line-break injection across every separator, and fails loud without a metadata anchor. A
  blocked transition now reports EVERY unmet gate in one refusal (was one per attempt: three
  round-trips to close a v3 finding). `artifact close --depth --verdict --reviewer --author
  [--triaged-by]` orchestrates stamp + critic verdict + terminal transition in one durable,
  re-runnable call, refusing self-review before any write.
- **Every test-suite `__main__` guard sits at true end-of-file, enforced (EP0026, CR0204;
  US0114).** Fifteen test files kept classes after a mid-file guard, so a direct
  `python3 test_x.py` run silently dropped them (22 tests once vanished while reporting OK)
  and agent appends risked truncation. An AST-driven normalisation relocated every guard
  (verified pure relocation, zero tests lost: 1497 + 2 new = 1499); a new
  `test_repo_hygiene.py` pins guard-at-EOF for every file and direct-run == discover parity,
  so the layout cannot regress.
- **The shipped payload is now markdownlint-covered (EP0026; BG0098).** `lint:md`'s `'**/*.md'`
  glob never matched dot-directories, so the 160+ shipped `.md` files under
  `.claude/skills/sdlc-studio/` were invisible to npm lint, the pre-commit hook AND CI - 2,502
  accumulated mechanics errors, found while dogfooding. The lane (script + hook) gains an
  explicit payload invocation with a payload-scoped config: every mechanics rule enforced
  (~1,850 auto-fixes + blockquote joins landed), seven template/example-noise rules disabled
  with the rationale ledgered (example H1s, placeholder rows, `{#anchor}` idiom, questionnaire
  blanks, pipe cosmetics).
- **The `Provenance: external` trust stamp has a writer (EP0026; BG0095).** verify_ac's shell
  gate read a stamp nothing ever wrote: `reference-verify.md` claimed "the ingest path stamps
  this field" while no workflow, template or tool did. `artifact.py new --provenance external`
  now stamps mechanically on every render path; the CR pull workflow and a new
  `reference-story.md` from-issue branch mandate the flag (the branch reference-github-sync
  linked to now exists); the `github_sync pull` TODO names it; and an end-to-end test proves a
  stamped story's `shell` verifier is refused. The reference-verify claim is finally true.
- **plan_review resolves stories through the shared lookup and fails loud on a miss (EP0026;
  BG0094).** `_resolve_story` re-implemented artefact lookup with a case-sensitive `US*.md`
  glob, so lowercase-named stories never resolved: `record_review` stamped a null fingerprint
  (an approval that could never match, an unclearable false block) and a pathless `gate()`
  skipped with `ok: True` (vacuous PASS). It now delegates to the alias-aware
  `sdlc_md.find_by_id`; recording against an unresolvable story raises, and a not-found gate
  fails closed with a loud reason.
- **The origin-drift preflight survives every plan order (EP0026; BG0085).** `sprint plan`
  always emits `waves` (None for manual order and empty batches), so the preflight raised
  TypeError and a blanket `except Exception: pass` swallowed it - silently disabling the
  behind-origin warning and the documented `--strict` refusal on exactly those paths. Now
  `(or [])` keeps the check alive and containment narrows to git's expected failure modes so a
  programming error surfaces loudly; end-to-end tests refuse under `--strict` for manual order
  and empty batches on a behind-origin clone.
- **A crashing blocking check now fails the gate (EP0026; BG0090).** A check that raised a
  non-config exception was recorded `blocking: False` and excluded from the PASS calculation,
  so a buggy or crashed blocking lane (validate, reconcile, conformance...) silently converted
  a red gate to green - the vacuous-PASS class at a new location. A declared
  `BLOCKING_ON_ERROR` lane set makes a crash in any blocking lane block; custom/injected
  checks stay contained (advisory-on-error), and a drift-guard test asserts every DEFAULT lane
  that blocks on failure also blocks on crash (it immediately caught `doc-coverage` missing
  from the first cut).
- **The eval gate joined the rc checklist and the four scenarios were re-run: 4/4 PASS
  (RV0007; BG0079).** The rc-readiness checklist omitted the eval gate its own release-gate
  template mandates (sections 1 and 8) and the scenarios had not run since v3.5.0 despite a
  SKILL.md description change. The checklist gains the row, and a full two-Claude run
  (worker + grader per scenario, method deviations recorded) passed every blocking behaviour
  across trigger routing, greenfield create, the generate-mode gate, and drift/reconcile
  dry-run safety - recorded in `sdlc-studio/reviews/v4-eval-run-2026-07-10.md`.
- **Superseded-regime docs corrected for the v4 majors gate (RV0007; BG0080).** The
  `status`/`hint` pre-flight tables covered only `schema_version: 2` (a fresh v4 project, on
  the new default of 3, had no row and the prompt still said "v1 format... upgrade to v2"); both
  tables are now era-neutral (2 or 3 proceed; the schema is read from `.version` OR
  `.config.yaml`, which is all a fresh v3 project has) with a schema-aware output prefix. The
  public SECURITY.md support table, frozen at 1.x, is restated in terms of the current major
  (4.x fixes / 3.x security-only) with the tracking rule written down.
- **`migrate_v3` journals its id map and resumes from it (RV0007; BG0073).** apply rewrote every
  reference (phase 1) then renamed files (phase 2) with no persisted map - a crash between or
  during the phases followed by a re-run re-derived a DIFFERENT assignment (phase-1 writes bump
  mtimes; already-renamed files shift the counter), silently cross-wiring identities across a
  consuming project. The map is now journalled to `.local/migrate-map.json` before the first
  write; plan and apply both detect the journal and resume from the SAVED map, a file present
  under neither name fails loud, a corrupt journal refuses to re-plan, and the journal comes off
  only after the index rebuild and era stamp are durable. The closing full-diff critic REJECTED
  the first cut with a reproduction (resume re-rewrote the old id inside `> **Aliases:**` lines,
  self-referencing every alias); repaired test-first - alias lines are structurally exempt from
  reference rewriting - and the same critic re-ran its reproductions to APPROVE.
- **`migrate_v3 apply` stamps `schema_version: 3` itself (RV0007; BG0074).** The docstring said
  the stamp "should be set" manually and the upgrade walk had no flip step - so after a clean
  migration all numeric ids vanished, `allocate_number` restarted at 1, and the very next
  `artifact new` minted `BG0001` while a migrated artefact still carried `> **Aliases:** BG0001`
  (ambiguous identity for every external reference). A completed apply now writes the stamp into
  `.config.yaml` (created if absent, other keys preserved; `plan` never stamps), so the era flip
  is mechanical. End-to-end: post-migrate filing mints a ULID.
- **The Low-consolidation lane exits 0 and its dry-run works (RV0007; BG0078).** `artifact new`'s
  text output indexed `epic_linked`/`indexed` unconditionally, but a consolidation result has its
  own shape - so a Low finding on a v3 project created/appended its CR and then exited 1
  (`error: 'epic_linked'`), inviting orchestrator retries and duplicate findings; `--dry-run`
  crashed outright. The text path now prints consolidation results by their own shape
  (`consolidated into CR-... created=True|False`); CLI tests cover dry-run, create and append.
- **The finding filer is era-aware (RV0007; BG0077).** `file_finding` allocated sequential v2
  numbers unconditionally, so on a schema-v3 project the primary agent filing path minted
  `BG0002`-style ids alongside ULIDs - reintroducing the id race v3 removes and shadowing live
  aliases. The v3 ULID mint now lives in one shared allocator (`sdlc_md.mint_v3_id`); both
  `artifact new` and the filer delegate to it, v2 projects keep sequential ids, and red-first
  tests pin both eras.
- **`artifact close` types v3 ULID ids (RV0007; BG0072).** Type inference collected every
  alphabetic character of the id, so a ULID's random tail (`BG-01JQK3F8` -> `BGJQKF`) defeated
  the prefix lookup and the documented close cascade raised `cannot infer type` for every
  artefact a schema-v3 project mints. A new `infer_type_from_id` reads only the LEADING alpha
  prefix (v2, dashed-v2 and v3 forms all resolve); unit tests pin all three forms and a live
  dry-run close of a freshly minted ULID.
- **`reconcile apply` no longer crashes appending a missing row into a dated index (RV0007;
  BG0071).** `row_from_header` indexed `f["date"]` directly while every other column used
  `.get()`, so the self-heal path raised `KeyError: 'date'` on the shipped bug/cr/plan index
  templates (and every dogfood index) whenever a file lacked an index row - aborting
  `transition set --ids` batches mid-flight after stamping the artefact. Absent dates now
  default to `--` like every other column; a cross-script seam test appends into a dated index
  and a unit test pins the empty-fields contract.
- **Repo lint restored to green and the commit gate actually enabled (RV0007; BG0075).** Six
  commits had landed markdown-breaking content on `main` while `git config core.hooksPath` was
  unset in the dogfooding clone (the tracked hook never ran) and CI sat dark behind the unpushed
  release freeze. The 26 markdownlint errors across 10 files are fixed (duplicate `### Changed`
  headings merged, founding-epic blockquotes joined, auto-fixables swept), `tools/enable-hooks.sh`
  is now run in this clone, and the rc-readiness checklist gains two rows: full `npm run lint`
  green and hook-enablement verified in the tagging clone.
- **The two archive implementations consolidated onto one `iter_tables` walker (EP0021,
  CR0182; US0098).** `archive.py` (release-based) and `reconcile.py`'s `archive_plan`/`archive_type`
  (flat) each hand-rolled their own index-table parser; both now delegate to a shared
  `reconcile.master_terminal_rows` built on `sdlc_md.iter_tables` (the single structural boundary).
  It picks the master data table by id-row count, so a multi-view index cannot double-archive a
  terminal row, and both paths use `sdlc_md.terminal_statuses` (BG0061's Deferred mis-classification
  cannot recur). Behaviour-preserving; the fail-loud-on-unrecognised-status and `--statuses` override
  contracts are intact.
- **`github_sync` and `verify_ac` discover artefacts through the shared layer (EP0021, CR0181;
  US0097).** Both tools now find lowercase-named files (the old case-sensitive `CR*`/`US*` prefix
  globs silently missed `cr0001.md` on Linux): `github_sync` dropped its private `TYPE_DIRS`
  duplicate of the type map and threads `--root` through discovery and the state file;
  `verify_ac`'s `walk_stories` and `--id` resolution are case-insensitive and it accepts `--root`
  as an alias of `--repo-root`, so the flag grammar matches every sibling script.
- **`decisions.py --supersedes` now flips the superseded row's Status to `superseded`
  (EP0020, BG0068).** The log no longer carries two contradictory `accepted` decisions; an
  unknown/typo id fails loud (anchored id parse) instead of silently recording a dangling
  supersession; a `decisions.py backfill` sweep fixes pre-existing rows (D0012/D0013). Also
  hardens `list_decisions` to split on unescaped pipes so a `\|` in a cell can't shift columns.
- **Shipped `test_gate` real-wrapper tests skip cleanly from an installed copy (EP0020,
  BG0069).** The two repo-coupled tests detect the dev-repo shape and `skipTest` with an
  explicit message otherwise, so a consuming operator verifying an install sees a visible SKIP,
  never a misleading FAILED on environment.

## [3.6.0] - 2026-07-06

The review/lite on-ramp (EP0016): two try-before-you-adopt entry points for an existing repo,
both non-breaking and independent of the dormant schema-v3 work. A project on v3.5.0 upgrades
with no migration and nothing renumbered.

### Release verification

Deterministic gate green: 1248 script tests + 49 tool tests pass, `check_versions --strict`
consistent across the four version homes, budgets/links/style/neutrality clean, `gate` PASS,
reconcile drift 0. The behavioural eval scenarios (`evals/README.md`) were not re-run this pass:
v3.6.0 adds two scripts plus help/config docs and does not change SKILL.md routing or
instructions - the surface those scenarios guard - so run them manually for a full behavioural
sign-off.

### Present but dormant (experimental, opt-in)

- The schema-v3 identity and enforcement machinery (ULID ids, migration, structured authorship,
  evidence and separation-of-duties lint) ships in this tag but is **inert** unless a project
  sets `schema_version: 3` (defaults to 2). It is experimental and unsupported until v4.0; see
  the `## v4 ...` sections below.

### Added

- **US0070 `review generate` on-ramp.** Point sdlc-studio at an existing repo and get a dated
  review report plus triaged findings with no prior workspace. `review_generate.py bootstrap`
  creates the `reviews/`, `bugs/`, and `change-requests/` folders and their indexes
  idempotently; the model-driven review runs three legs (architecture, code quality, defensive
  security) from `templates/workflows/repo-review.md`, read-only on source. Security findings
  are remediation-only by policy - location, weakness class, impact, and fix, no exploits or
  payloads, and a committed secret is reported by location plus rotation with the value never
  copied into an artefact. The policy is embedded verbatim in the prompt template, and
  `review_generate.py scan --secret <value>` fails if any produced artefact contains the value.
- **US0071 lite profile.** `profile: lite` in `.config.yaml` collapses the pipeline to
  PRD -> story -> implement: a story is created without an epic, `status`/`hint` never nag
  about a missing TRD/TSD/persona/epic, and executable-AC verification and reconcile behave
  identically. Every other profile keeps the epic layer mandatory. `sdlc_md.profile` is the
  reader; `lite_profile.py promote` is the one-way door to `full` - it inserts one umbrella epic
  above the existing epic-less stories, wires each to it, flips the profile, and reconciles the
  indexes clean. Documented under `reference-config.md#profile`.

## v4 Tranche 2 - authorship & enforcement + tooling debt (WIP, unreleased)

The v4 Tranche 2 - authorship & policy enforcement (EP0013), plus the RV0006 tooling-debt
tranche (EP0018) and the benchmark protocol. 13 stories delivered trunk-based. All schema-v3
enforcement is era-gated, so existing v2 projects are unaffected.

### Added

- **v4 Tranche 2 - authorship & enforcement (schema v3, opt-in).** All rules are era-gated,
  so existing v2 projects are unaffected.
  - **US0060 structured authorship.** A typed `> **Raised-by:** Name; type; version` reference
    (type one of human | persona | agent). `validate` enforces presence, shape, and
    resolvability on v3 artefacts (persona names resolve against `sdlc-studio/personas/`);
    `sdlc_md.schema_version`/`is_schema_v3`/`parse_authorship`/`resolve_author` back it.
    `backfill_authorship.py plan|apply` seeds a raised_by onto pre-adoption artefacts, marking
    inferred attributions, idempotent. The persona resolver is swappable for an agent resolver
    later with no schema change.
  - **US0061 separation-of-duties lint.** A `duties-separated` validate rule fails a v3
    artefact whose `Triaged-by` equals its `Raised-by` (a different seat must triage); a solo
    human self-triaging only warns, so a lone operator never deadlocks. The transition-time
    refusal wires in with the agentic triage transitions (EP0014).
  - **US0062 evidence as schema.** An `evidence-present` validate rule (v3 only) requires a
    bug to carry a file:line reference, command output, or reproduction steps, and a CR to
    carry an impact statement plus an effort estimate. Presence only (truth stays with
    reviewers); a `{{placeholder}}` counts as absent; legacy v2 artefacts are exempt.
  - **US0063 consolidated audit-check.** `audit_check.py check` runs the team-schema rules
    with stable ids (`authorship-structured`, `evidence-present`, `duties-separated`,
    `id-format`, `index-derived`, ...), exits non-zero on any violation, and gives `--format
    json` for the crew audit linter. The same rules are enforced in the blocking `gate` via
    `validate` and `index-derived`; `tranche-shape` ships dark until EP0014's tranche field.
  - **US0064 cross-script invariant test tier.** `test_invariants.py` guards the cascade seams
    the RV0006 review found unprotected: one telemetry record per artefact close, new-then-
    reconcile zero drift, CLI/library allocation parity, and master-table append on a
    multi-view index. It immediately earned its place - it caught a regression of BG0053 (the
    double-telemetry-on-close line had crept back into `artifact.close`), now re-fixed.
  - **US0073 benchmark protocol (pre-registered).** `docs/benchmarks/protocol.md` freezes the
    task set, metrics (tokens, wall time, defect escapes via a held-back suite, rework rate),
    N=5-with-an-N=1-spike, an independently-reviewed baseline `CLAUDE.md`, and a
    publish-regardless-of-outcome commitment - the RFC0025 device that must exist before any
    measured run. The harness and runs (US0074/US0075) follow.
  - **US0082 context tiering.** `digest.py build` produces mechanical, drift-checked digests of
    closed artefacts (id / title / status / outcome / refs) so status and planning reads need
    not re-read the whole corpus as a repo ages; originals are never summarised away.
    `digest.is_stale` gives the reconcile-style drift check. The read-path integration and size
    threshold stay scoped in CR0179.

### Fixed

- **US0078 archive consolidation - correctness guard (CR0182).** A regression test confirms
  both archivers (`archive.py` release-based and `reconcile archive_type`) relocate each
  terminal row of a multi-view index exactly once - the master row moves, the shared view row
  is kept. The double-archive path CR0182 flagged no longer reproduces (fixed by the BG0066 /
  v4 table-parsing work); the full dedup onto one `iter_tables` archiver stays scoped in CR0182.
- **US0077 shared discovery (CR0181).** `github_sync.walk_local` now discovers artefacts via
  the shared `sdlc_md.artifact_files` (case-insensitive, root-aware) instead of a
  case-sensitive `CR*.md` prefix glob that silently missed lowercase-named files (`cr0001.md`)
  on Linux. Full `--root`/STATE_PATH grammar unification stays scoped in CR0181.
- **US0080 code-quality debt (CR0187).** Corrected the `reconcile.py` module docstring - it
  claimed "read-only ... Subcommand: detect" while shipping `apply`/`fields`/`archive` write
  subcommands, so a read-only allowlist trusting it under-scoped the mutation surface; it now
  lists all four and scopes read-only to `detect`. Added `--format json` to `reconcile apply`
  for programmatic callers. (The larger CR0187 items - shared `find_by_id`, complexity
  decomposition, log rolling - stay scoped in the CR.)
- **US0079 security hardening - state hygiene (CR0186).** The skill-install `.local/` runtime
  state is now gitignored and `version-check.json` untracked, so machine state stops churning
  in every commit. A `tools/tests` guard keeps any `.local/` file from being tracked again.
  (The remaining CR0186 supply-chain items - SHA-pinning Actions, installer checksums, sync
  redaction - need out-of-band inputs and stay scoped in the CR.)
- **US0081 batch scaffold wiring (CR0166).** A regression guard confirms a multi-epic batch
  wires cleanly - the Story Breakdown placeholder is replaced (no stray `---` separator) and
  each epic gets exactly its stories with no empty table. The structural edges CR0166 flagged
  no longer reproduce (incidentally fixed by the v4 batch/index work); the guard prevents them
  returning.
- **US0076 config failure regimes (CR0180).** `sdlc_md.project_override` now emits a
  one-line warn-once to stderr when a `sdlc-studio/.config.yaml` exists but cannot be honoured
  (no PyYAML / malformed), instead of silently reverting to defaults - so a project's declared
  conventions are never silently ignored. Absent config stays silent. (BG0062 already fixed
  the related Done-gate crash.)

## v4 foundation - distributed identity, schema v3 (WIP, unreleased)

The v4 foundation - distributed artefact identity (schema v3). The move from a
single-writer tool toward a team-based one. All new capability is opt-in (`schema_version: 3`);
existing v2 projects and their sequential ids are untouched until they choose to migrate.

### Added

- **v4 foundation - distributed artefact identity (schema v3, RFC0024).** Opt-in via
  `schema_version: 3` in a project's `.config.yaml`; existing v2 projects are untouched
  (sequential ids stay the default).
  - **US0055 ULID ids.** A stdlib Crockford-base32 ULID generator (`sdlc_md.new_ulid` /
    `short_ulid`): a 48-bit millisecond timestamp (lexicographically sortable = creation
    order) plus 80 bits of randomness, so concurrent writers in parallel worktrees never
    collide without coordination. `artifact.py new`/`batch` mint `BG-01JQK3F8`-form ids in a
    v3 project (collision-checked, suffix extended on a rare clash) and stay sequential in v2.
    Every id reader is now era-tolerant: `ID_RE`/`ID_SEARCH_RE` match both forms, `id_number`
    returns the sequential number for v2 ids and `None` for ULIDs (keeping them out of the
    max+1 path).
  - **US0058 derived indexes.** A new `index-derived` gate check enforces that every
    `_index.md` is output of the census, never a hand-edited input: it runs a dry-run
    `reconcile apply` per type and fails when the index is not a fixed point (a hand-edited
    status/row/count the tool would rewrite). `reconcile.index_derived_issues` backs it.
  - **US0069 passive concurrency safety.** `sdlc_md.atomic_write` (same-dir temp then
    `os.replace`) means a crash mid-write leaves the previous index intact, never truncated;
    index writes in `artifact`, `file_finding` and `reconcile apply` now use it. An advisory
    `sdlc_md.allocation_lock` (POSIX `flock`, best-effort elsewhere, timeout-and-proceed so a
    stale lock never wedges a wave) serialises allocate-and-write in `artifact.new`, so
    concurrent writers never mint the same id or clobber a shared index.
  - **US0056 v2-to-v3 migration.** `migrate_v3.py plan|apply` rewrites a workspace's
    sequential ids to ULIDs, preserving creation order (each ULID's timestamp is derived from
    the file's date), retaining the old id as an alias (`> **Aliases:** BG0001`), rewriting
    every intra-workspace link, and regenerating index counts. Dry-run-first and idempotent (a
    second run is a no-op). `sdlc_md.alias_map` resolves a pre-migration id to its current
    ULID, and `transition` looks artefacts up through it, so `--id US0001` still works after a
    migration.
  - **US0057 friendly GitHub aliases.** A synced artefact's GitHub issue number becomes a
    resolvable friendly alias (`alias_map` maps `GH42` -> the canonical id) while the ULID
    stays the identity; recording the issue number is offline-safe (only written after a
    successful `gh` create).
  - **US0059 TRD refresh + freshness guard.** The generated TRD is corrected to the shipped
    script layer: the real (bounded, tested) write contract replaces the false "read-only
    over the workspace" claim, plus accurate component counts, state-file inventory, and test
    figures. A `tools/tests` freshness guard fails if those stale claims reappear.

### Fixed

- **Self-review bug sweep (RV0006, BG0053-BG0066).** 14 defects found by an
  architecture / code-quality / defensive-security review of the skill's own
  source, each fixed with a failing-first regression test:
  - `artifact close` recorded a telemetry event twice per close (transition
    already records on entering the terminal set); estimation-calibration data
    was inflated ~2x. Metrics now flow through the single record.
  - `install.sh` exited 1 after a successful install when the stale-copy sweep
    refreshed another tool's copy (`set -e` plus a trailing `&&` test); the
    success banner never printed. `sweep_stale` now returns 0.
  - `verify_ac ts-check` cross-checked the verify-report by bare AC id, so one
    story's failing AC1 flagged every story's AC1 in a merged report. The key
    is now story-qualified.
  - `verify_ac` executes shell-backed verifiers only when shell is allowed and
    the story is not stamped `Provenance: external`; an unrecognised expression
    is now an invalid verifier, not a silent shell run. New `--no-shell`,
    `--allow-external`, `--allow-shell-fallback` flags turn the documented trust
    boundary into an enforced one.
  - `gate.py` reported a vacuous PASS when `--only`/`--skip` named no real
    check; it now fails loud on an unknown name or an empty selection.
  - `next_id allocate` (CLI) re-implemented allocation and could re-issue a
    deleted-but-indexed id; it now delegates to the one `allocate_number`
    authority.
  - `archive.py` hardcoded terminal-status sets that treated `Deferred` as
    closed; it now uses the shared `terminal_statuses`, so re-activatable rows
    stay live.
  - The story Done gate raised a PyYAML `RuntimeError` on stdlib-only machines
    instead of its block message; policy is now read via the degrading
    `project_override`. The gate also blocks on a stale verify-report entry
    (story edited or an AC added since it was verified).
  - `github_sync` gives `gh` a timeout (no indefinite hang) and no longer stamps
    `last_pull` when a `gh` call failed (a swallowed failure recorded as
    success).
  - `append_index_row` bounded its insertion to the master table's contiguous
    rows, so a trailing link-first view table no longer captures the new row.
  - CI workflow now declares least-privilege `permissions: contents: read`.

### Changed

- SKILL.md description opens with the masthead tagline ("The antidote to
  vibe coding: a full software engineering team at your fingertips") ahead
  of the unchanged trigger catalogue - re-run eval scenario 01
  (trigger-routing) before the next tag, as for any description change.

## [3.5.0] - 2026-07-05

### Release verification

Eval scenarios (the two-Claude worker/grader loop, `evals/README.md`) run in
full: **01 trigger-routing PASS** (natural language model-invoked the skill;
template-conformant PRD; the new slice-read rule honoured unprompted), **02
greenfield-create PASS** (canonical paths, tool-allocated sequential ids,
Draft-only births, GWT + Verify lines - and the v3.4.0 advisory retired: the
Three Amigos consult ran with attribution rows in every artifact), **03
generate-mode-gate PASS** (philosophy gate read before generation; every
extracted contract verified code-accurate by the grader), **04
drift-reconcile PASS** (all three seeded drift kinds enumerated; the grader
mechanically re-verified 18/18 checksums unchanged under --dry-run). Three
cosmetic scaffold-wiring edges triaged to CR0166 (Low). Tranche critic:
Sam Eriksson (QA seat, review render) APPROVE after three rounds, verdicts
recorded under the seat.

### Changed (reconcile apply)

- `reconcile apply` appends missing index rows mechanically: one
  header-driven row per census file the index lacks, built in the pinned
  MASTER table's own column order (the table already holding the census
  rows - a trailing view never captures the append), with the status
  landing in a declared alias column and the id mirroring the table's
  display style. Unplaceable rows (no ID-column header) warn and exit
  non-zero; orphan rows stay report-only. A consuming project's agent
  had hand-authored 23 rows because this class was report-only.
- The critic is a seat, not an anonymous instance: `critic.py record`
  warns when the reviewer matches no declared seat/amigo, and the sprint
  and persona references state the close-pass critic runs AS the QA
  seat's review render.

### Added (token economy)

- Index-bloat advisory: `reconcile detect` and `status hint` recommend the
  progressive-disclosure archive (`scripts/archive.py`) when live terminal
  rows exceed `indexes.archive_after` (default 30) - advisory only, counted
  from the live index so an archived workspace stays silent; the
  release-gate template carries the archive step. First live run archived
  265 rows on this repo (live indexes 332 -> 83 lines, census 0-drift).
- `artifact.py revision --ids A,B --note "..."`: deterministic batch
  appends to Revision History tables (dated, author-stamped); a file
  without the section is refused loudly and one refusal never aborts the
  batch - retires the hand-scripted close-out loop.
- Slice-read rule: SKILL.md instructs section reads for references over
  ~400 lines (honour the Reading Guide - Grep the anchor, offset-read the
  section); the epic and story Reading Guides now name greppable anchors.
- Anchor-window discipline: LATEST.md is a window, not a ledger - past
  sprints become one-line History pointers to their retros, and
  `doc_freshness` flags the anchor when it exceeds `docs.latest_max_lines`
  (default 80). Codified for consuming projects in
  `reference-operator-heuristics.md#anchor-window`.

### Added

- Tolerant convention layer (`lib/conventions.py`): one place where a
  consuming project's house conventions are interpreted, declared under
  `conventions:` in `.config.yaml` (status-column aliases, companion-doc
  suffixes, bug-readiness heading vocabularies, per-type scaffold
  templates). Reconcile accepts declared status-column aliases, and
  `artifact new`/`batch` scaffold a project-declared template (grafted onto
  the deterministic provenance head) instead of planting the skill shape a
  house-templated project's checks then reject. Every key defaults to the
  historical behaviour; a wrong-shaped value fails loud naming the key.

### Added (project upgrade)

- `project upgrade` surfaces the capability delta, not just file
  corrections: a "Changed since <recorded skill_version>" digest of the
  shipped CHANGELOG entries in the version gap (grouped by kind, capped
  with a "+N more" tail), plus one line per advisory-when-absent gate
  lane introduced in the gap naming its baseline command - sourced from
  a declared registry in `gate.py` that a test keeps honest. Absent or
  unparseable CHANGELOG degrades to an explicit "unavailable" line.
  `install.sh` now ships `CHANGELOG.md` with the skill payload.

### Changed

- `reconcile apply` inserts a missing summary status row instead of
  exiting 0 over a count-mismatch it created: a status flip into a status
  absent from the summary now lands `| <Status> | <n> |` in the
  reconcile-managed global summary block (before the Total row); scoped
  per-epic roll-ups are never touched, and when no managed block exists
  the missing statuses are named as warnings and apply exits non-zero.
  A transition into such a status now reports `index_synced=True`
  truthfully - the sync actually happens.
- The dormant `Verified` bug status has defined semantics mapped onto the
  verification-depth tiers: `Fixed` = implemented and proven at the
  functional tier (the honest status when a higher-tier proof is owed);
  `Verified` = additionally proven at the tier its risk demands
  (conversational/soak/live). `transition` gates the Fixed → Verified
  promotion on a recorded depth above functional; projects that never
  promote to Verified are unaffected.
- Companion-doc recognition is header-based, not a one-suffix allowlist:
  a file under an artifact directory that carries no artifact header (no
  `> **Status:**` line and no `# <ID>:` title) is a companion/note, so an
  `EP0244-...-decisions.md` beside its epic no longer trips a false
  `no-status` validate error plus a `duplicate-id` collision. The rule
  lives once in `artifact_files` via the convention layer (extra suffixes
  declarable under `conventions.companion_suffixes`); a real artifact
  that lost its Status line keeps its `# <ID>:` title and stays flagged.
- Adversarial-close hardening of the above (all nine critic findings
  fixed with repros re-run): id allocation keys on the filename so an
  off-template or companion file always holds its number; `validate`
  emits a `not-an-artifact` warning naming every id-named file the
  census excludes; the degenerate-index diagnosis is judged on the live
  index before the archive merge; `apply` rewrites a declared
  status-column alias (writer parity); heading match is word-set
  equality or ordered prefix, never blanket containment; and a
  wrong-shaped `conventions` value fails the gate rather than silently
  disabling the lane that read it.
- Bug-readiness reads its heading vocabularies from the convention layer:
  a house template documented as Symptom / Root cause / Fix (proposed) is
  ready (a documented cause is stronger evidence than bare repro steps),
  heading match is word-order-insensitive and suffix-tolerant, a
  genuinely-empty bug still flags, and a project can declare its own set
  under `conventions.bug_ready_sections`.
- Mutation-check summary states its sampling coverage explicitly: when the
  budget truncates, the CLI note, report `summary.enumerated`, and the gate
  lane detail all carry `sampled N/M enumerated (x%)`, so a green sample can
  never read as whole-surface assurance; an untruncated run reads as before.
- Sprint plan names the provenance of its seat scores: which units carry
  wsjf-inputs seat judgements (and the file's write time), which fell back
  to the neutral default, and an advisory staleness warning when the
  inputs file is older than `sprint.wsjf_inputs_stale_days` (default 7) -
  a stale cross-sprint consult is now visible at the operator STOP.
- Reconcile diagnoses a mis-named or absent index Status column once: when
  every row parses as Unknown and no data table pins an exact `Status`
  header, `detect` emits a single `index-status-column` finding naming the
  offending header (e.g. `Effective Status`) instead of a per-row
  status-mismatch storm plus a misleading count-mismatch, and `apply`
  refuses loudly (exit 1) rather than recompute counts it cannot reconcile.

## [3.4.0] - 2026-07-04

### Release verification

Eval scenarios (the two-Claude worker/grader loop, `evals/README.md`) run in full
for the first time since v2.0.0 - the 02-04 waiver is retired: **01
trigger-routing PASS** (skill self-invoked from natural language, template-
conformant PRD), **02 greenfield-create PASS** (canonical paths, sequential ids,
Draft-only GWT stories; one advisory unclear - the Three Amigos consult was
skipped rather than offered under a self-answered interview, triaged as
acceptable, re-check next instructions release), **03 generate-mode-gate PASS**
(philosophy gate read before generation, code-exact extraction), **04
drift-reconcile PASS** (deterministic helpers, both seeded drift items, zero
mutation). Suites 1058 + 41 green; strict version check green; gate PASS.

### Added

- **Verified lines land in canonical order (BG0051).** verify_ac applied multiple
  write-backs top-down from a single parse, so each insertion shifted every later
  AC's cached line indices - Verified lines drifted one line earlier per prior
  insert (the Given/Verified/When misordering in US0051-54). Write-backs now
  apply bottom-up, leaving earlier indices valid; the four affected stories were
  repaired by strip-and-regenerate through the fixed tool.

- **status/hint surface a concurrent-session advisory (CR0150).** When the
  sdlc-studio/ workspace carries uncommitted or untracked artifact changes, the
  re-anchoring commands print one advisory line naming the artifact ids -
  "another session may be mid-flight" - instead of the next session discovering
  the collision by gate failure. Informational only; no authorship guesses;
  degrades silently without git. Critic hardening: the pillars text-mode wiring
  was dead behind a misplaced return (caught by a live command run while the
  helper-only tests stayed green - lesson L-0004: test the command, not only the
  helper); renames now name both the old and new ids.

- **Terminal transitions record telemetry (BG0052).** The delivery loop closes
  units via `transition.py`, but telemetry only fired in `artifact close` - which
  the loop never calls - so three full sprints recorded zero events and the
  RFC0018 `show --summary` had nothing to summarise (the product_reconcile
  disease: a feature that exists and silently never runs). A transition whose
  target status is terminal for the type now appends the event (id, type, plus
  any `--iterations`/`--wall-time-s`/`--verdict` passed through); never on
  dry-run or non-terminal moves. The sprint's own discipline is instrumented
  from the run that fixed it forward.

- **Batch transitions and tool-created retros/reviews (CR0143).** `transition.py set
  --ids A,B,C` runs a same-target batch with each id individually gated - one
  refusal reports, continues, and exits non-zero (no more shell loops around the
  tool). `artifact.py new --type retro|review` creates the meta-artifacts
  (allocated id, template scaffold - retro renders from the shipped retro
  template - and an index row where a meta index exists), retiring the last
  hand-authored artifact class; `transition` refuses meta ids with a message
  naming why they sit outside the status machinery.
  Close-of-sprint critic fixes: batch json stdout stays pure (summary to stderr),
  the meta-index insertion is bounded to the data table, and the gate's hash paths
  resolve against --root.

- **WSJF's no-seat fallback divides by the neutral default (CR0149).** The
  complexity signal - the cognitive complexity of the existing files a unit
  touches - is blast-radius risk, not effort; it no longer stands in as the WSJF
  size when the Engineering seat has not scored a unit, surviving only as the
  within-priority tiebreak and token-budget input. A one-line fix in a complex
  file no longer sinks on the file's complexity.

- **One shared structural table iterator (CR0144).** `sdlc_md.iter_tables()` is now
  the single boundary rule every table parser uses - header+separator (any dash
  count) opens a table, a heading ends it, and a caller predicate covers legacy
  vocabulary headers. The four parsers that each hand-rolled boundaries (the
  duplicate-id scan, `_index_rows_and_summary`, `_index_row_ids`,
  `verify_ac.ts_check`) are ported one at a time with their existing tests
  unmodified and green between ports - retiring the defect class behind BG0046
  and BG0049 instead of fixing it per parser (lesson L-0001 made structural).

- **Mutation gate v2 (CR0146).** Correctness first: the report records a content
  hash per target and the gate lane reports STALE when any target changed since
  the run - same rev included - so a dirty tree can no longer ride an old green
  report (the hole the critic demonstrated live). The cost ceiling now distributes
  round-robin with files as the fast axis instead of first-N in file order, and
  Python string/docstring interiors are excluded from enumeration (tokeniser-based;
  a parse failure skips the exclusion and NOTES it, never silently).

- **verify_ac lint flags Verify runners missing from PATH (CR0145).** A Verify
  line whose runner (pytest/jest/vitest/go/rg; http checks curl+jq) is absent
  from this machine's PATH draws an advisory naming the install-or-rewrite-or-
  runs-elsewhere choice - the wording owns that the author machine's PATH may
  differ from CI's. shell and manual are exempt; nothing blocks. Live-verified:
  the historical pytest Verify lines on this pytest-less machine light up
  exactly as the field pain predicted.

- **The close-of-sprint adversarial critic pass is a named, exact step (CR0148).**
  reference-sprint.md's closing gate now specifies the CODE leg's shape - an
  independent critic instance over the FULL sprint diff, refute framing, findings
  with reproductions, fixes seen red first, and the same critic re-running its own
  repros before approve - as a sharpening of the existing critic step, never a
  second parallel gate. help/sprint.md, the conformance critiqued hint, and the
  retro guidance (a 'critic loop, observed' section) point at it. This is the pass
  that caught both sprints' worst escapes.

- **doc-freshness names its counting method (CR0147, reduced AC).** The test-count
  finding now says "N test functions counted statically ... claim this number", so
  the LATEST.md claim and the checker agree on what is being counted instead of the
  operator chasing the runner's skip/subclass accounting. The checker still never
  runs the suite.

- **RFC-0018 closed as accept-reduced (operator decision D0004).** `telemetry show
  --summary` aggregates the run log per type (count, mean iterations, mean wall
  time, reopen rate, verdict mix - a field never measured reports None, not a
  fabricated 0), replacing the raw-dump-only view; `best-practices/script.md`
  gains the subcommand verb taxonomy (guidance for new commands, no renames).
  The cross-file vocabulary-consistency checker is declined: zero repeat
  incidents in two releases, and a recurrence's right home is a declared
  `constitution.md` rule, which now exists.

- **The executable mutation-check gate ships (CR0134 / RFC-0022 / EP0011).** The
  skill's named biggest blind spot is now enforced, not prose: `scripts/mutation.py`
  applies a declared, bounded fault set (invert-guard, stub-return-null,
  unset-delivered-field, no-op-mapper) to a selected surface via per-language
  textual profiles (.py, .js/.ts, .go invert-guard), re-runs the mapped tests per
  mutation, and reports **killed vs survived** - a survivor is a finding, exit
  non-zero. Deterministic (same code + set = same report); honest degrade
  everywhere: un-mutatable surfaces report un-checked, a red baseline yields error
  verdicts (never a fake kill), and ceiling truncation (`--max-mutations`,
  `quality.mutation_max`) is counted, never silent. Surfaces: `--files`,
  `--since REF`, `--story USxxxx` (epic/CR Affects chain); `prefilter` lists
  assertion-free test files. The release gate gains an advisory `mutation` lane
  (absent report reads not-run, never PASS). Dogfooded on this repo's own sprint
  diff: 12/12 mutations killed by the 1017-test suite, 2653 enumerations honestly
  truncated. Complements `verify_ac` (checks pass) with the can-it-fail question.

- **The deterministic toolbox is now discoverable from the router (CR0133).** A field
  session used ~2 of the 40+ scripts and hand-did what they automate (hand-allocated
  ids, never ran `validate`). SKILL.md now carries a "Deterministic Entry Points"
  task-to-script card; the Progressive Loading Guide names the script to run for
  creating and filing (not only the prose to read); doctrine rule 15 makes
  script-first the stated discipline; `templates/agent-instructions.md` presents
  non-interactive `artifact.py new` as the canonical create path (interactive
  commands are wrappers); `help/bug.md` / `help/cr.md` lead with the one-liner and
  state that ids + index rows are tool-allocated.
- **RFC-0022 opens the mutation-check gate design (CR0134, RFC-first).** The skill's
  named biggest blind spot - nothing executable asks whether a test would FAIL if
  the feature broke - is epic-sized with an unsettled cross-language injection
  design, so the sprint delivered the RFC, not the implementation: four options
  (per-language AST, declared textual mutations, framework adapters, static
  heuristics), a recommendation (textual-mutation core, framework lane opt-in,
  static pre-filter, AC-to-test mapping over the existing Verify + coverage-matrix
  bridge), and six open decisions. CR0134 is Blocked pending the RFC decision and
  decomposes into an epic on acceptance.
- **The style guard now checks British spelling (CR0135).** AGENTS.md stated three
  prose rules; `lint-style.sh` enforced two. A bounded, high-signal American-spelling
  pass (the analyze/analyse pairs and the -ize/-ization family, word-boundary matched
  so size and prize are untouched) now flags offenders with the British form suggested, sharing
  the existing allowlist for genuine exceptions (API identifiers like `optimize=True`
  and `EXPLAIN ANALYZE`, quoted command names, `gh --color` flags); the Contributor
  Covenant text is excluded as third-party. The script accepts an optional scan-root
  argument so the new fixture tests exercise it in isolation. Zero hits on the
  current tree after allowlisting the seven literal-identifier lines.
- **A mixed bugs + CRs tranche is a first-class sprint batch (CR0138).** The most
  common maintenance sprint (backlog clear) was inexpressible: `sprint.py plan`'s
  queries were mutually exclusive, `--write` kept whichever half ran last, and the
  documented worklist file did not exist. Status queries are now combinable
  (`--bugs Open --crs Proposed` yields one merged, dependency-waved plan with
  cross-type edges honoured), `--worklist <file>` (ids one per line) is a real
  batch source that errors on unknown ids, and cross-type ordering uses one
  documented weight scale (Critical/P1 .. Low/P4, case-tolerant - lowercase bug
  severities now rank correctly too). `audit.py check` treats a dependency
  sitting in the same batch as informational `sequenced-in-batch` instead of
  `unmet-deps` (pending deps only - a dead or missing referent stays unmet), and
  `conformance.py check` states its story-only scoping in its output rather than
  leaving a bug/CR tranche's coverage gap unstated. Critic hardening: a blank
  Severity/Priority field ranks Medium instead of crashing the planner; worklist
  ids dedupe in every order mode; `--worklist` + `--epic` refuses loudly instead
  of silently ignoring the filter.
- **Verification-depth tiers are enforced on transition, not decorative (CR0136).**
  `transition.py` now refuses `bug -> Fixed` below `functional` and `bug -> Closed`
  on a production-affecting bug (`> **Production-affecting:** yes`) below `soak`,
  naming the current and required tier; a missing/unparseable depth field on a
  gated transition is refused, never assumed satisfied. Story `Done` gains a
  depth-parity advisory (an AC's declared `Verification target` above `functional`
  should not out-run the recorded depth), upgradeable to a refusal via
  `quality.depth_parity_gate: true`. `--force` records an override, as before.
  The Production-affecting flag matches by leading token, so an annotated
  `yes (checkout path)` still gates rather than silently classifying as
  non-production (independent-critic finding).

### Changed

- **Payload hygiene: repo-only `tools/` checker tests moved out of the shipped skill
  (CR0140).** Five tests (`test_check_neutrality/budgets/links/versions`, `test_validate_skill`)
  lived in `.claude/skills/sdlc-studio/scripts/tests/` - so they shipped into every consumer
  install and reached the repo-root `tools/` they test, which does not ship. Moved to a repo-level
  `tools/tests/`; runners (`package.json`, the pre-commit hook, CI) now run both suites; total count
  preserved (995 = 958 skill + 37 tools). The shipped payload now tests only what ships, and the
  domain-neutrality guard (a public-repo-only concern) no longer has any footprint in consumer
  installs.

### Fixed

- **ts-check's AC matrix no longer bleeds into later tables (BG0049).** The matrix
  parser locked onto the coverage-matrix header and then read every subsequent
  table row in the spec as an AC row - the canonical References and Revision
  History tables reported as unmapped ACs, so `epic-ts` failed on the shipped
  convention's own shape (the already-closed EP0010's spec failed it). A markdown
  heading now ends the matrix scope; a genuinely unmapped AC row still fails.
  Same defect class as the BG0046 structural-boundary fix - found while authoring
  EP0011's spec at the design rung.
- **provenance remake honours the adoption cutoff and never double-stamps (BG0048).**
  `remake` now applies the same `provenance.adopt_after` exemption as `check`
  (previously it mass-stamped all 145 artifacts against the documented intent;
  `--all` opts back in), and ANY non-empty `Created-by:` counts as provenance for
  both commands - a field-report attribution is respected, not nagged forever and
  given a second `Created-by:` line beside the human one.
- **The Engineering seat can size WSJF jobs; unknown effort is never minimal (BG0047).**
  `wsjf-inputs.json` takes an optional per-unit `size` (story-point scale) that
  overrides the complexity seed - previously the seat that owns effort had no slot,
  and a unit whose Affects named not-yet-existing files got size 0, ranking
  greenfield epics as the cheapest jobs in the batch. When neither a seat size nor
  the complexity seed resolves, a declared neutral default divides the score.
- **Reconcile and validate findings now self-diagnose (CR0132, absorbing CR0139).**
  Two field sessions dead-ended on an opaque `count-mismatch` whose "recompute the
  summary counts" hint `apply` could not clear - the cause was an out-of-vocab
  status silently dropped from the row tally. The finding now names each mismatched
  status with both numbers (`cr: Proposed rows=5 summary=4`, text and JSON), and
  when out-of-vocab statuses are the cause it names the status, its artifacts, and
  the `status_vocab.<type>` config remedy, routing to `validate.py check`; the
  generic recompute hint survives only for true arithmetic drift. `validate`'s
  status-vocab error now names the config extension mechanism instead of implying
  historical artifacts must be rewritten. Documented in `reference-reconcile.md`,
  `help/reconcile.md`, `help/status.md`.
- **Duplicate-id gate no longer trips on the shipped CR index's Dependencies table
  (BG0046).** `reconcile`'s within-table duplicate scan reset its per-table tally only
  on a header containing a bare `Status` cell; the `templates/indexes/cr.md`
  Dependencies header carries `Dependency Status`, so its rows tallied into the
  previous table's scope and a fully-templated project failed its own release gate
  (field run: 12 false duplicates, the operator converted the table to prose to get
  green). The table boundary is now structural - any header row followed by its
  `| --- |` separator resets the scope - and regression tests pin the shipped
  Dependencies shape plus the true-positive (same id twice within one table still
  flags). The independent-critic pass extended the same structural boundary to the
  sibling parsers (`_index_rows_and_summary`, `_index_row_ids`): a table whose
  header declares no Status column is never scavenged for one, so a
  `| CR-0001 | CR-0003 | Complete |` dependency row can no longer overwrite
  CR-0001's parsed status (the phantom status-mismatch + unclearable
  count-mismatch loop), and short-dash GFM separators (`|--|`) count as
  boundaries everywhere.
- **Bug-readiness check accepts the shipped template's own headings (BG0045).**
  `audit.py`'s `_bug_underspecified` demanded the literal `## Steps to Reproduce` +
  `## Proposed Fix`, while `templates/core/bug.md` shipped `## Reproduction Steps` +
  `## Fix Description` - so every template-authored bug in every consuming project
  flagged "underspecified" forever (a field run reported 0/4 ready on four fully
  specified bugs). The predicate now accepts both vocabularies, the template is
  aligned to the canonical pair, and a regression test renders the shipped template
  through the predicate so the gate is validated against its own template's output.
- **Pre-commit hook now runs markdownlint from the npm-local install.** The hook
  checked only for a *global* `markdownlint`, so after `npm install` (which provides
  `markdownlint-cli` at `node_modules/.bin/`) it silently skipped the check - and an
  MD032 (blank-lines-around-lists) error in a CR doc passed the local gate and failed
  CI on the v3.3.0 push. The hook now prefers `node_modules/.bin/markdownlint` and,
  when Node is absent entirely, prints a visible SKIP instead of passing silently.
  AGENTS.md documents the gap. Fixed the MD032 error itself in CR0131.

## [3.3.0] - 2026-07-04

The anti-vibe hardening release: enforcement you cannot skip, a test-integrity
discipline, and a field retrospective that made the toolbox discoverable. A
pre-commit hook now runs the whole gate on every commit and explains every failure
in detail (CR0137); the assertion-integrity discipline teaches, and the templates
now record, whether a test would fail if the feature broke (CR0131); and the AGENTS/
PRD/TRD/TSD docs plus the README were reworked so an agent finds the 40+ deterministic
scripts and the local gate instead of hand-doing their work. Five CRs (CR0132-CR0136)
capture the remaining enforcement gaps found by dogfooding.

### Added

- **Pre-commit hook makes the gate un-skippable (CR0137).** `bash tools/enable-hooks.sh`
  installs a tracked `.githooks/pre-commit` that runs the whole npm-independent gate
  (style, links, skill-spec, versions, budgets, neutrality, `gate.py`, and the script
  suite when code changes) on every commit and blocks a breaking one. Every failure is
  explained in detail: what the guard enforces, the offending file:line, and the fix;
  drift items print their own remediation. Turns "the agent should run the gate" into
  "the agent cannot commit past it" - the anti-vibe last mile. Emergency bypass:
  `git commit --no-verify`.

- **Assertion-integrity discipline + mutation-check gate (CR0131).** The skill taught verification
  *depth* but not whether a test *can fail*. Added a `reference-test-best-practices.md#assertion-integrity`
  section (the vacuous/tautological assertion, the injected-data unit test that bypasses the real
  wiring, and the mutation check - break the feature, confirm the test goes red, restore), a
  per-AC `Mutation-checked` field in `templates/core/story.md`, a `Mutation-checked` verification
  item in `templates/core/bug.md` (the regression test must be seen red against the unfixed code),
  and an e2e-mutation-checked + real-data-path gate in `templates/workflows/release-gate.md`. Found
  in the field: a governance surface shipped marked "renders + initiates + audits" while doing none
  of the three on the real data path, behind a green-but-vacuous suite.

### Changed

- **README: a concrete vibe-coding vs spec-driven vs governed framing.** The "Why"
  section led with an abstract argument hidden in a collapsible; added a visible
  three-mode contrast that lands the differentiator (spec-driven tools *align* the
  agent on intent; SDLC Studio also *argues back with facts* - executable ACs,
  reconcile-from-census, a commit gate), so a newcomer sees why it is worth using.

- **Docs: make the local gate and the deterministic toolbox discoverable (dogfood
  fix for CR0133).** AGENTS.md "Testing the Skill" now lists every CI guard as an
  npm-independent command with what each catches (a session broke CI four ways by
  not running them); the Skill Structure scripts row points at `reference-scripts.md`
  and names the load-bearing scripts (`artifact.py`, `file_finding.py`, `next_id.py`,
  ...); Style Requirements now states the rules are enforced by `lint-style.sh`. PRD
  section 10 records the enforcement-gap debt (CR0131/0132/0133/0134/0135/0136); TSD
  folds in the run-the-gate-pre-commit lesson and the assertion-integrity pointer.

### Proposed

- **Field-retrospective CRs (dogfooding against a consuming project).** From driving the skill end-to-end:
  - CR0132 - reconcile findings must self-diagnose. The `count-mismatch` fix hint is generic and
    misleading (points at `apply`, which cannot clear an out-of-vocab status); it should name the
    offending status and route to `validate`. Completes the CR0025 remediation-guidance principle
    for the drift that dead-ended a session. *(Root-cause corrected: the vocab is already
    config-driven; the defect is diagnostics, not configurability.)*
  - CR0133 - surface the deterministic toolbox so an agent reaches for the right script (map
    task -> script in the router, not just task -> prose). Broadened from "the create path" after a
    session used ~2 of 40+ scripts and hand-did work `file_finding.py` / `next_id.py` automate.
  - CR0134 - an executable mutation-check / test-quality gate (epic-sized, RFC-first) to *enforce*
    the CR0131 assertion-integrity discipline, not just document it - the skill's biggest blind spot.
  - CR0135 - extend the style guard with British-spelling detection. *(Root-cause corrected:
    `tools/lint-style.sh` already enforces em-dash + jargon; the only unchecked rule is British
    spelling. Filing this CR itself broke the style guard by not running it - self-evidence for
    CR0133.)*
  - CR0136 - enforce the verification-depth tiers on `transition` (Fixed needs `functional`+, Close
    needs `soak`). The tiers are documented but `transition.py` never reads the depth field.

## [3.2.0] - 2026-06-27

The skill self-improvement release: a token-economy + learning-loop epic (EP0010), the
test-strategy heuristics (CR0128), and a newcomer-first README and onboarding overhaul.
New commands - `reconcile archive`, `lessons revalidate`/`summary`, `gate --require-retro`,
`blocker_sweep`, and the `audit` regression-test check - plus four promoted cross-project
lessons (LL0009-LL0012). CI restored to green and the Dependabot action bumps adopted.

### Fixed

- **CI coverage gate restored to green (US0047).** The gate failed on CI not from a coverage
  shortfall (coverage is a healthy ~82%) but from test *failures*: the config-driven tests
  (provenance/validate `adopt_after` cutoff, transition done-gate, conformance) read
  `.config.yaml` via `config._yaml()` and raise without PyYAML, which the CI step never installed -
  so `coverage run -m unittest` exited non-zero before the threshold was ever checked. Added
  `pyyaml` to the coverage step's `pip install`. The story's original "coverage drops from skips"
  framing was a misdiagnosis, corrected in its Root Cause section.

### Changed

- **README + onboarding overhaul for newcomers.** Rewrote `README.md` as a black-box-first,
  progressively-disclosed landing page: a jargon-free hero and what/who/why, the "you just ask"
  table, a quick-start *path* with a greenfield/brownfield fork, a mermaid pipeline diagram + an
  annotated `status` dashboard, a scannable capabilities table, three collapsible worked examples
  (Product/Engineer/QA), a "start here by role" table, and a collapsible FAQ with a plain-language
  glossary. The 63-line version-history "Roadmap" moved out to CHANGELOG; the philosophy manifesto
  moved below the fold. Added `help/brownfield-runbook.md` (the existing-code sibling to the
  greenfield runbook) and registered it in `SKILL.md`. Reviewed via a four-lens persona consult
  (Product, Engineering, QA, and a non-technical-newcomer lens); all four approved after fixes.
- **CI action bumps adopted (US0048):** `actions/checkout` v6 -> v7 (both jobs) and
  `actions/setup-python` v5 -> v6 in `.github/workflows/lint.yml`, superseding Dependabot PRs
  #25/#26.

### Added

- **EP0010 - skill self-improvement: token economy + learning loop (11 stories, 5 CRs).** Delivered
  this sprint; see `sdlc-studio/retros/RETRO0005`.
  - **Index archive (CR0125 / US0040, US0041).** `reconcile archive` relocates terminal index rows to
    a derived `<type>/archive/_index.md`, leaving active rows + the summary block live; idempotent,
    `--dry-run`, fail-loud on an unclassifiable status. Terminal-status vocab is `sdlc_md`-derived;
    `next_id` unions the archive sub-indexes so an archived id is never re-issued.
  - **Blocker sweep (CR0130 / US0049, US0050).** New `blocker_sweep.py` finds units whose blockers
    cleared - in-repo by census, cross-repo via the PVD `product-manifest.yaml`. Runs before
    `sprint plan` and as the advisory `reconcile detect --blocker-sweep` lane; proposes
    `Blocked -> Ready`, never auto-transitions, never false-clears an unresolved referent (LL0008).
  - **Retro lifecycle (CR0129 / US0042-US0044).** The sprint close is a hard fail-loud gate
    (`gate --require-retro`); `lessons revalidate` closes stale lessons by validity; `lessons summary`
    regenerates a deterministic committed `LESSONS-SUMMARY.md` read at sprint start. Dogfooded here.
  - **Agentic-wave worktree doctrine (CR0126 / US0045)** and **pre-deploy readiness checklist
    (CR0127 / US0046)** added to their reference docs.
- **Test-strategy heuristics (CR0128).** New `best-practices/testing.md` captures five heuristics
  with a one-line trigger each (production-state-shape integration tests, a named regression test
  per production bug, rejects-old-shape contract tests, resource-count regression tests,
  pure-function extraction), referenced from the test-spec workflow. The test-spec template gained a
  "Strategy Heuristics" AC block. Determinism: `audit` raises `missing-regression-test` for a
  terminal bug whose recorded tests carry no integration/regression-level case (name-signal; the
  seam judgement stays with review, per the recorded advisory boundary).
- **Four cross-project lessons promoted to the skill tier (LL0009-LL0012).** LL0009 - a silent failure
  that misleads the caller outranks a loud failure of the same scope. LL0010 - validate a defence using
  the bug it defends against before shipping it. LL0011 - a gate that fails on CI but passes locally is
  an environment gap until proven otherwise (reproduce the CI env before trusting the symptom). LL0012 -
  a new private helper that shadows a module-level name silently breaks every existing caller.

## [3.1.1] - 2026-06-25

A field-hardening release. Six bugs and five change requests, raised from four
upgrade-run retrospectives, plus RFC0021 - the seats/amigos duality - settled by a
dogfooded Three Amigos consult and delivered in two slices. The persona model converges
to one role-based actor model: `seats/` is the home, an "amigo" is an enriched seat that
can also build, and the delegation resolver and consult both honour a project's authored
seats via a declared `role:` field. The cluster of reconcile/conformance/validate fixes
all trace to one law captured as LL0008: a deterministic tool must fail loud, never report
success it did not achieve. Built by the amigos - the Engineering amigo under TDD, the QA
amigo verifying as a separate instance - dogfooding the author != reviewer independence
gate on the skill's own backlog (which caught a missed call site mid-delivery).

### Added

- **A declared, machine-readable seat-role field; the resolver keys on it (RFC0021 slice 1, D6).**
  Each amigo/seat card now carries a `<!-- role: engineering|qa|product -->` comment, and the three
  default cards plus the amigo template declare theirs. `persona_resolve.card_role(path)` reads this
  field - never the H1 prose or the filename - so a seat card named after a person ("Sarah") maps
  to its seat deterministically. The form is an HTML comment: invisible in rendered markdown,
  unambiguous to a single regex, and independent of prose a translation or rename could change.

### Fixed

- **The old-persona-model upgrade hint names the actual signal that fired, not a misdirecting
  content-rewrite instruction (BG0041).** `project upgrade`'s persona finding now separates
  structural-layout drift (a nested `team/`/`stakeholders/` dir, or the word "amigo" in `index.md`
  - fixed by a dir move / index reword) from content-model drift (an old-model heading in a named
  file - fixed by a rewrite), and names the offending dir/file. A faithful content rewrite alone no
  longer leaves the operator chasing a flag that only clears on a layout change.

- **The `adopt_after` cutoff is parsed by one shared helper and never silently disabled (BG0039).**
  `conformance.adopt_after` and `provenance.adopt_after` looked identical in `.config.yaml` but
  were parsed by two different code paths with two different value formats and two different
  boundary operators - and the conformance side dropped a bare-integer cutoff with no error
  (`id_number("103")` returned `None`), leaving the gate red and unexplained. A third reader,
  `validate`'s no-ac exemption, carried the same silent-fail and the same strict `<`. All three
  now route through `sdlc_md.parse_cutoff`, which accepts a bare integer (`103`) or a prefixed id
  (`US0103`, `CR0103`) interchangeably and raises a clear, loud config error on an unparseable
  value instead of returning `None` and silently judging everything (LL0008). The conformance and
  validate boundaries are aligned from strict `<` to `<=` to match the name and provenance's
  existing behaviour: ids up to and including the cutoff are exempt ("this id and earlier are
  grandfathered"). The repo's own `provenance.adopt_after: 57` keeps exempting ids <= 57 unchanged.
- **`reconcile apply` no longer reports a status flip it did not persist (BG0043).** A status
  fix the writer could not place in the row (an off-schema/header-less layout it declines to
  guess) was still printed as `set <id>: A -> B` and counted as a changed row, while the index
  stayed untouched - a no-op dressed as a clean apply. `apply_type` now partitions planned fixes
  by what actually landed in the buffer: only persisted fixes are reported as changes, an
  unpersisted one is surfaced (a `WARNING: could not apply ...` on stderr, named in the summary
  line, non-zero exit) so it is hand-edited rather than trusted. The writer also preserves inline
  emphasis on a status cell - a bold-wrapped `**Proposed**` is rewritten to `**Complete**`, not
  flattened to `Complete` - mirroring the reader's tolerant canonicalisation. This is the
  fail-loud discipline (LL0008): never announce an edit you did not make.
- **`reconcile` verified to scope the count recompute to the canonical global summary, sparing
  per-epic count sub-tables (BG0044).** An index carrying per-epic `| Done | N |` blocks plus a
  global summary recomputes only the global summary (identified by its `Total`-row signature, or
  as the sole summary); the per-section blocks survive unchanged rather than being stamped with
  the project-wide total. Locked with a regression test on the exact field shape.
- **`validate personas` no longer reports a vacuous clean pass on a nested persona layout (BG0040).**
  The flat `personas/*.md` glob matched zero files when a project keeps its personas nested (e.g.
  `personas/team/`, `personas/stakeholders/`), and the check still printed "personas look
  well-formed". It now emits a `persona-layout` advisory ("personas present but not in the flat
  Cooper layout (N nested files found); not validated") when the flat glob inspects nothing but
  persona-shaped files sit in subdirs. A pass means inspected and well-formed, never found nothing
  to inspect (LL0008). The `seats/` subtree (review-seat charters) stays excluded.

### Changed

- **`persona_resolve` reads a project's review seats, not only `personas/amigos/` (BG0042, RFC0021
  D6).** The resolution chain is now most-specific-first: an explicit `personas/amigos/<seat>.md`
  override, then a role-matched `personas/seats/*.md` card (matched by the declared `role:` field),
  then the skill default, then generic. A project's hand-authored "Three Amigos" are no longer
  shadowed by the generic defaults. Two seat cards declaring one role resolve lexically by filename
  with a warning; zero declaring it falls through to the default and never crashes. A seat resolved
  for `--render review` that lacks its review-render sections (Lens / Pushes Back When / Shadow) is
  a **hard error** (`RenderError`, RFC0021 D4), never a silent fallback. New floor tests prove a
  role-matched seat resolves over the default, the two-claim/zero-claim cases, the render-less hard
  error, and that build and review framed from one seat card stay separate instances the critic
  `author != reviewer` gate still requires (RFC0021 D5).
- **`project upgrade` is seat-aware - it enriches in place instead of manufacturing a parallel
  amigo set (CR0120 AC1-4, RFC0021 D2).** `_missing_amigos` no longer reports a role as missing
  when an existing `personas/seats/*.md` card declares it; the generic cards are installed
  **greenfield only**, when no seat or amigo fills the role, so an authored seat is never doubled
  by a generic card beside it. When a seat and an amigo both claim a role, the upgrade emits an
  explicit **overlap heads-up** naming the roles - in `--dry-run` too - so the parallel role
  systems are never a silent collision.
- **A conformance failure names its remedies inline instead of burying them in a docstring (CR0121).**
  The gate and `conformance check` previously printed a bare `N non-conformant unit(s)`; the two
  mechanisms that legitimately resolve it - the `conformance.adopt_after` cutoff (forward-only
  adoption, now stated with the correct value format) and the `verify_ac` backfill path - were
  documented only in the script's source. The output now names both, and distinguishes
  unadopted-discipline debt (most units mass-missing the same stage - pre-existing, forward-only)
  from scattered per-unit gaps that may be a regression from the current change, so a
  grown-but-accepted count no longer reads as a new breakage. No stale count is hard-coded in the
  config comment - any count shown is the live computed figure.
- **`reconcile detect` signposts the fix order and names the file to link (CR0122).** When both
  status drift and count drift are present, the report now states the recommended order - resolve
  the file/index status mismatches first, re-sync the index rows, recompute counts/summaries LAST
  (because fixing statuses moves the counts) - so the operator no longer learns it by watching the
  count move the wrong way. A `fix_order` field is added to the JSON report. A missing-row finding
  now emits the artifact's actual filename relative to its type directory (and carries a `file`
  field), so the index link can be wired without guessing.
- **Disambiguated the three "upgrade" surfaces in one place (CR0123).** `skill-update` (the
  installed skill), `project upgrade` (a consuming project's conventions), and `upgrade` (a
  project's v1 -> v2 artifact schema) were all called "upgrade". `reference-upgrade.md` now carries
  a single side-by-side table naming what each changes and when to reach for which, cross-linked
  from each command's help; the command and help wording names its target so "upgrade" is never
  bare. Documentation only; no behaviour change.
- **One seat schema: the enriched amigo template supersedes the lean review-seat charter (RFC0021
  slice 2, CR0120 AC5, D3).** `amigo-template.md` is now the single seat schema. It already was a
  strict superset of the old `review-seat-charter.md` (Cooper depth + charter discipline + the dual
  render + the declared role field), and it is now explicit that the one schema covers both a
  build-capable "Three Amigos" seat and a review-only document-owner seat (Product Owner / Product
  Manager / UX): a review-only seat fills the review render and marks the work-render sections
  "n/a". `review-seat-charter.md` is retired to a thin pointer at the enriched schema, so existing
  references do not 404 and any consuming project is guided to the one template. Every active source
  reference (`reference-consult.md`, `reference-persona.md`, `reference-workflow-personas.md`, the
  upgrade drift hint, the template header) now points at the enriched schema.
- **Consult resolves its seat through the same declared-`role:` chain as delegation (CR0124).** The
  consult workflow previously loaded its charter from the template keyed on `{{seat_name}}`/H1
  prose, so a project's authored seat was honoured when the sprint loop delegated work but shadowed
  in a consult. `reference-consult.md` now resolves the seat by declared `<!-- role: -->` (a project
  `personas/seats/` card whose role matches, else the skill default seat, else the generic enriched
  seat schema as the fallback), via a new `persona_resolve.py resolve-consult` surface that reuses
  the delegation resolver (`seat_card`, `card_role`, the chain). A consult critiques, so a matched
  seat missing its review render is a hard error, consistent with the delegation resolver. An
  authored seat is now honoured in both paths.

## [3.1.0] - 2026-06-25

### Added

- **sprint plan flags an undeclared dependency graph so its waves are real (CR0114, field
  report):** the `--goal design` rung now establishes inter-story `Depends on:` as part of
  grooming Draft -> Ready, so a designed backlog carries the dependency graph the planner needs.
  When `plan` selects a batch of >1 unit with no declared in-batch dependency, it prints a hint
  that all units are parallel because no `Depends on:` is declared - so a flat single wave is not
  mistaken for "no dependencies exist", the prose-derived sequencing the waves feature exists to
  remove (scripts/sprint.py, reference-sprint.md).
- **the Three Amigos are now a rich, instantiated engineering team (CR0118, RFC0020 D4):** an
  enriched amigo card (`templates/personas/amigo-template.md`) fuses Cooper goal-directed depth
  (Who They Are, Craft Goals, Proficiency, Scenario) with seat discipline (Non-Negotiables, Shadow,
  Tensions) and a dual render (build/author vs review, separate instances). Three default amigos
  ship instantiated - Engineering (Dani), QA (Sam), Product (Lena) - editable per project; a richer
  project-authored practitioner amigo overrides a default. Documented in reference-workflow-personas.md.
- **the test-spec AC Coverage Matrix scaffolds from an epic's stories (CR0115, field report):**
  `verify_ac` can emit a matrix pre-filled with one row per AC across an epic's stories, so the
  design rung no longer hand-extracts dozens of ACs and no AC is silently omitted - the model fills
  the Test Cases column, ts-check validates completeness (scripts/verify_ac.py).
- **mechanical author != reviewer independence gate (CR0117, RFC0020):** `critic.py record` now
  stamps both the reviewer and the author (the authoring seat / delegation id); the conformance
  gate hard-fails any Done unit whose critic verdict reviewer id equals its author id, or that has
  no recorded author - a self-review never clears Done, and the floor holds for generic workers too,
  not only persona-framed ones. Units closed before the gate carry a visible `pre-gate` marker and
  are grandfathered (one-time migration); the policy is reconciled in reference-sprint.md
  (independence is the floor for every risk tier, only the review depth scales).
- **project upgrade installs the amigo defaults (CR0119):** `project upgrade` installs the three
  default amigo cards into a consuming project's `sdlc-studio/personas/amigos/` when absent
  (idempotent, never overwriting a customised amigo) and reports the v3.1 persona enrichment, so
  upgrading projects gain the editable engineering team (scripts/project_upgrade.py, reference-upgrade.md).
- **persona-shaped delegation: workers are framed as amigo seats (CR0116, RFC0020 Accepted):** a new
  `persona_resolve.py` resolves the worker identity most-specific-first - a project-authored
  practitioner amigo overrides the skill default (Dani / Sam / Lena), which overrides generic. The
  agentic wave appends the resolved stance *after* the contract (file list / ACs / gates stay law),
  the build and review seats are always separate instances (the CR0117 independence gate), and
  `--skip-personas` yields a byte-equivalent contract that still builds. Wired in
  reference-agent-prompt-template.md + reference-sprint.md; RFC0020 accepted on Option B.

### Fixed

- **ac_scope no longer cries wolf on shared domain vocabulary (CR0113, field report):** the
  cross-epic AC lint flagged any story whose AC named a keyword distinctive to another epic's
  title, but a noun like "list" or "item" appears in the ACs of stories across many epics - it is
  shared domain vocabulary, not epic-specific leakage. ac_scope now measures document frequency
  across distinct epics and suppresses a keyword that spreads beyond a threshold, so a genuine,
  concentrated cross-epic reference still flags while the noise that trained operators to ignore
  the advisory is gone (scripts/ac_scope.py).
- **integrity no longer requires a Story link on test-specs (BG0038, field report):** an
  epic-scoped test-spec carries an Epic link and covers a whole epic with no single Story field
  (reference-test-spec.md#epic-scoped-coverage), yet `integrity.py` listed both Epic and Story as
  required and flagged the very artifact the skill mandates at epic scope. Story is dropped from the
  test-spec required-link set; Epic stays required, so a test-spec with neither still flags.

## [3.0.1] - 2026-06-24

> The v3 line: the `autosprint`->`sprint` rename + sprint lifecycle, greenfield authoring,
> the RV0005 self-review, and the field-dogfooding fixes - consolidated into one release.

### Added

- **natural-language "You can just ask" blocks on every command help file (CR0108):** the skill
  is model-invoked, so each `help/*.md` now opens with a `Just say... | Runs` table mapping plain
  phrasings to commands - a non-technical operator can just ask. A `disclosure` check enforces the
  block on every non-meta help file. Authored across 35 files via a multi-agent sweep.

- **`verify_ac --batch` jest mode - run the runner once, not a cold start per AC (CR0111, field
  report):** `reconcile --verify --batch` runs `jest --json` once and resolves jest-targeted ACs
  against that result set (a field sprint measured ~48 cold `jest -t` starts / 70s collapsing to
  one run). Mirrors `jest -t` (pass iff matches exist and all pass); cache misses + non-jest verbs
  fall through to the per-AC path. pytest/vitest caches are a fast-follow (the parse/resolve path
  is runner-general).

- **the `--goal design` rung authors the test-spec AC Coverage Matrix (CR0110, field report):**
  the breakdown produced Ready stories + points but never authored the test-spec, so the AC↔test
  bridge (CR0085) was reverse-engineered at *implement* (a field delivery repointed ~48 Verify
  lines + backfilled coverage gaps by hand). The design rung now authors each epic's AC Coverage
  Matrix - every AC mapped to a planned test case/title, Verify lines runner-targeted by
  construction - so implement binds to the matrix and the test-spec `epic-ts` (CR0096) requires at
  Done is produced up front. Documented in `reference-sprint.md` + `reference-test-spec.md`.

- **the tranche audit runs `verify_ac lint` + `ac_scope` (CR0109, field report):** `audit check`
  (the sprint breakdown's readiness groom) now flags **weak-verify** (a non-executable / prose
  Verify line, reusing `verify_ac.lint_verifier`) and **cross-epic-ac** (an AC owned by another
  epic, reusing `ac_scope`). Two readiness problems the skill already had tools for - but which a
  field breakdown re-discovered by hand - are now surfaced deterministically at design time.

- **`sprint plan` emits dependency waves (CR0107, field report):** the planner returned a flat
  order; the parallelisable wave structure (L1/L2/L3...) was only computed by the model at
  `--agentic` implement time, so operators hand-derived it and stored the rich plan externally.
  `build_plan` now returns **waves** (dependency levels) for priority/wsjf order - wave 1 = units
  with no in-batch dep, wave n+1 = units whose deps are all in earlier waves, units in a wave
  parallelisable - printed in the plan output and persisted by `--write`. Reuses the existing dep
  graph; within-wave order keeps WSJF/priority rank.

- **`sprint plan --epic` scopes a story batch to one or more epics (CR0106, field report):**
  the planner filtered only by status, so `--stories Draft` pulled every Draft story across all
  epics - a field agent planning the next tranche (EP0002+EP0003) had to hand-scope and hand-build
  the waves instead of using `plan --write`. `sprint plan --stories <status> --epic EPxxxx`
  (repeatable, union) now restricts to the named epics; dependency ordering, `--write`, and WSJF
  operate on the scoped batch. Story-only (errors with `--crs`/`--bugs`).

- **deterministic id-allocation extended to the meta-artifacts (CR0105):** `next_id.py allocate
  --type` now covers `review` (RV####) and `retro` (RETRO####) in addition to the 8 pipeline
  types, so review/retro ids are allocated collision-free (respecting `--remote`) instead of
  hand-picked by reading the directory. Kept out of `ARTIFACT_TYPES` so reconcile/conformance
  ignore them. (Lessons `LL####` keep their own `lessons.py` manager; personas are named.)

- **SOTA linter coverage in the quality guides (CR0103, RV0005 audit):** `best-practices/script.md`
  gains a Tooling section (ShellCheck + shfmt as the baseline; the anti-pattern table reframed as
  what ShellCheck enforces) and teaches `set -euo pipefail` instead of bare `set -e`;
  `best-practices/python.md` gains a Tooling section (Ruff + mypy/pyright, 3.10+ floor) and its
  Type Hints example uses PEP 604 `X | None` rather than `typing.Optional`; `help/code.md` `code
  check` now lists a shell linter so every language the repo ships is covered.

- **v3.0 capabilities surfaced in the always-loaded router + help catalogue (CR0104, RV0005
  review):** `help/help.md` now lists the `decisions` command (add/list/promote) and names the
  sprint **goal ladder** `triage -> plan -> design -> done`; the SKILL.md Type Reference gains
  `init` (greenfield step 1) and `decisions` and names the ladder; `artifact batch`,
  `--template full`, and `next_id allocate` are in the deterministic-tooling catalogue; the
  greenfield manual workflow leads with `init`. Closes the `decisions` doc-coverage false-green.

- **seat-scored WSJF sprint planning (CR0099, from LL0007):** `sprint plan --order wsjf` now
  orders by **WSJF = (value + time-criticality + risk-reduction) / size**. The review seats score
  the numerator (Product Owner = value, QA = risk, Engineering = effort seeded by the complexity
  signal) into `.local/wsjf-inputs.json`; the planner computes and records the components in the
  sprint-plan artifact. Degrades gracefully to priority + complexity with no inputs or under
  `--skip-personas`. Sprint planning becomes a value/risk judgement, not a bare-priority sort.

- **already-satisfied flag in the tranche audit (CR0098, from LL0007):** `audit check` (the
  sprint pre-flight) now flags a Ready unit whose executable ACs all pass in the verify-report as
  **already-satisfied** - a close-candidate, not work to build. The audit can't see a feature
  shipped under a different artifact, but a green verifier set is the deterministic signal - the
  exact gap that let 5 stale Ready stories through this session's first plan. Advisory; reuses the
  verify-report.

- **persona index-projection via a canonical field (CR0097):** the deferred half of CR0082. The
  story template + scaffold now carry a canonical `> **Persona:**` field, and `reconcile fields`
  projects it into the index `Persona` column alongside Title/Points (absent field left untouched,
  BG0032). The "As a {persona}" prose stays; the metadata field is the projection source - so the
  index Persona column is derived, not hand-kept.

- **hard epic-scope test-spec requirement (CR0096):** the deferred half of CR0085 - the
  AC-to-test bridge is now mandatory at epic scale. `verify_ac epic-ts --epic EPxxxx` requires an
  epic to have a test-spec (linked by its `Epic:` field) whose AC Coverage Matrix passes
  `ts-check`; gated by `quality.epic_requires_test_spec` (default true), single-story work exempt.
  Reuses `ts-check` (no new verification logic); documented in `reference-epic.md`.

- **done-requires-verified toggle + status verification lane (CR0095):** the deferred half of
  CR0084. `quality.done_requires_verified` (default true) lets a project set the story->Done
  AC-verify gate policy in `.config.yaml` - false downgrades it to advisory-warn project-wide
  (per-call `--force` still overrides). And `status` now reads `verify-report.json` and surfaces
  a verification lane (stories with unverified ACs; the manual-AC count), so env-bound/manual ACs
  read as "deferred", not silent gaps.

- **reconcile-before-plan (CR0094):** `sprint plan` runs `reconcile detect` first and surfaces
  index drift - warns by default, refuses under `--strict`. The planner reads each unit's file
  `Status`, so a stale index misleads selection; reconcile-first guarantees a clean census.
  Mechanical drift only - semantic staleness (a unit whose feature shipped elsewhere) still
  needs the audit + grooming (LL0007). Documented as step 0 of the loop in `reference-sprint.md`.

- **authoring sprint - PRD to a reviewable backlog (RFC0019, CR0088-0093):** `sprint` now drives
  greenfield authoring. `sprint <prd.md> --goal design` bootstraps **PRD → epics → stories**
  (CR0088 PRD-input planner; CR0089 decomposition via the shared `epic`/`story` core + batch
  create) with two STOPs - approve the epic cut, resolve open questions (CR0090; `--autonomous`
  records-and-proceeds). The **goal ladder** gains `--goal plan` for sprint planning
  (select + sequence + estimate → `sprint.py plan --write` artifact; CR0091); the rungs are
  cumulative stop-points and NL maps to the furthest one. `--goal design` assigns story points,
  projected into the index by `reconcile fields` (CR0092); the closing **consistency pass** runs
  `ac_scope` + `ts-check` + `reconcile fields` + `validate` + `integrity` over the produced
  backlog (CR0093). The loop is documented in `reference-sprint.md`; never implements at
  `design`/`plan`.

- **greenfield runbook (CR0081):** `help/getting-started.md` gives the canonical command order
  from an empty repo to a reviewable backlog (`init -> prd -> persona -> trd -> tsd -> epic ->
  story -> reconcile/validate`) and on through the implementation handoff, each step with
  why/command/output/next. Linked from the SKILL router and `init`'s next-steps. It names the
  decisions log and the future authoring loop at the right points, and documents autosprint's
  **cold-start precondition** (a runnable gate) plus the foundation-first handoff - also
  mirrored into `reference-autosprint.md`.

- **agent-instructions enforce the tool-first discipline (CR0083):** the shipped
  `templates/agent-instructions.md` (read by every consuming-project agent; `.CLAUDE.md`
  inherits it via `@AGENTS.md`) gains a mandatory "use the deterministic tooling" rule -
  bootstrap with `init`, create via `new`/`batch` (never hand-roll ids/indexes), the index is
  derived, a story reaches Done only when its executable ACs pass, foundation-first then
  autosprint. The root cause every greenfield friction shared: agents improvise because
  nothing tells them to trust the tooling. Dogfooded into this repo's own `AGENTS.md`.

- **cross-epic AC scope lint (CR0086):** `ac_scope.py check` flags, advisory, a story whose
  acceptance criteria reference a distinctive capability keyword owned by a different epic's
  title (the un-Done-able-in-its-own-epic defect the field audit found - US0002/US0018 reached
  into EP0006/EP0003). Heuristic, read-only, never auto-edits; the operator splits or
  re-scopes. The "single most useful defect" the dogfooding surfaced, now caught at authoring.

- **Definition-of-Done gate on `transition`/`close` (CR0084):** a story moving to Done is
  refused when it declares executable (non-`manual`) ACs that are red or never run in
  `verify-report.json` - the safety net for the hand-driven path that a diligent agent
  bypassed (shipping 0/7 by its own green suite). The block is the one deterministic fact
  (the verifier result); `--force` overrides (recorded). Scoped to stories - CR/epic/bug
  closures, manual-only / AC-less stories, and dry-runs are never gated. Pairs with CR0085
  (the gate is a clean signal only once the TS matrix makes names converge).

- **test-spec as the AC-to-test bridge, enforceable (CR0085):** `verify_ac ts-check --spec
  <ts> [--verify-report <json>]` validates an AC Coverage Matrix is not decorative - every AC
  mapped to a passing test case, no placeholders, cross-checked against the live report.
  `verify_ac lint` flags Verify lines that fall through to `shell` as mis-written runner
  calls (`npm test -- ... -t`, `curl ... returns N`), nudging to the DSL - catching the 0/7
  drift at author time. `verify_ac run --id USNNNN` adds grammar parity with `transition`.
  The TS-bridge + DSL discipline is documented in `reference-verify.md`. (Deferred to a
  follow-up: a hard epic-scope TS requirement wired into epic-implement, and a status manual
  lane - both touch the model-driven workflow surface.)

- **reconcile projects file-owned index cells (CR0082):** `reconcile fields` (`--apply`)
  syncs the index's `Title` and `Points` cells from the backing story files, so the index is
  fully derived (LL0001) and the audited story-points hand-copy disappears. A field absent in
  the file is left untouched (BG0032 no-clobber); persona is deferred (no single canonical
  field in a story). `apply` and `fields` are now documented (the entry was stale at
  read-only/`detect`).

- **project decisions log (CR0080):** `scripts/decisions.py` (`add` / `list`) maintains
  `sdlc-studio/decisions.md` - the canonical, append-only home for load-bearing decisions,
  both product (scope cuts, resolved PRD open questions) and implementation conventions
  (error envelope, ID scheme, token strategy, migrations, test harness). `init` seeds it
  empty. The project "spine" lives in one place and feeds the delegated-agent handoff
  context, instead of being scattered and pasted per prompt. Distinct from the autosprint
  per-tranche ledger.

- **batch artifact creation (CR0078):** `artifact.py batch --type <t> --spec <items.json>`
  creates many artifacts of one type in one atomic pass - a reserved contiguous id block
  (LL0002), every index row, and every story-to-epic link wired together; a missing epic or
  id collision aborts before any write; `--dry-run` previews the id map. Defaults to
  `--template full` (the fan-out case where delegated agents fill pre-wired scaffolds rather
  than coordinate structure).

- **executable `init` (CR0079):** `init` was a manual checklist; it is now `scripts/init.py`.
  `init run` creates the full `sdlc-studio/` directory tree, pre-creates every per-type
  `_index.md` (reusing the CR0077 helper, so the first `new` of any type is indexed), seeds
  `sdlc-studio/.config.yaml` + the `AGENTS.md`/`CLAUDE.md` starters from templates, and with
  `--scaffold` seeds the singleton docs (prd/trd/tsd/personas). `--detect` infers the stack;
  idempotent (never overwrites without `--force`); `--dry-run` previews every write so the
  workflow can confirm config before applying. The CR0077 index-bootstrap moved to the shared
  `file_finding.ensure_index` (single source, used by both `new` and `init`).

- **greenfield `new`: lazy index creation + full-template scaffolds (CR0077):** `artifact.py new`
  now creates a missing `<dir>/_index.md` from `templates/indexes/<type>.md` on first use (the empty-
  project first run), so the very first artifact of a type is indexed like every later one - closing
  the misleading `indexed=false` signal that taught a greenfield agent to hand-manage indexes.
  `--dry-run` reports `would_create_index`. New opt-in `--template full` grafts the rich
  `templates/core/<type>.md` body onto the deterministic provenance head (minimal stays the default;
  validate/provenance behave identically). Part of the greenfield-friction workstream (CR0077-0086).

### Changed

- **stripped internal provenance tags from consuming-facing docs + shipped code (CR0112):** the
  skill's own change-request ids (CR/BG/RFC) were embedded pervasively in `reference-*.md`,
  `help/*.md`, and `scripts/*.py` - where they collide with a consuming project's own id
  namespace. ~420 tags removed (a deterministic pass + an 82-file grammar-aware sweep); a
  `lint-style.sh` guard blocks the parenthetical provenance form from creeping back. The skill's
  own artifacts (change-requests/, CHANGELOG, rfcs/, reviews/) keep their ids; example ids stay.

- **`autosprint` renamed to `sprint` (CR0087, WS0 of RFC0019):** the command is now the whole
  sprint lifecycle (`--goal plan` / `design` / `done`), not just autonomous delivery - autonomy
  is the `--autonomous` flag, not the name. `scripts/autosprint.py` → `scripts/sprint.py`,
  `reference-autosprint.md` → `reference-sprint.md`, `help/autosprint.md` → `help/sprint.md`, and
  the live command surface now says `sprint`. **`autosprint` stays as a deprecated alias** (a
  re-export shim + NL resolution) so nothing breaks. History (closed CRs, RFC0001, prior
  CHANGELOG entries) keeps the original name.

### Fixed

- **`verify_ac` merges per-story results into the report instead of clobbering it (BG0037, field
  report):** `write_report` rebuilt verify-report.json from only the current run, so verifying a
  sprint one story at a time left the report holding only the last story - and `transition -> Done`
  (CR0084) reads that report, so the gate failed for every earlier story. Runs now merge (this
  run's entries win, others preserved); per-story verification accumulates and the Done-gate finds
  every verified story. `--fresh` forces a clean rebuild. No more `--dir`-re-stamps-everything.

- **`init` now gitignores the runtime-state dir (BG0036, field report):** `init` created
  `sdlc-studio/.local/` (caches, verify reports, lessons) but wrote no `.gitignore`, so greenfield
  projects committed derived state (this repo only avoided it via a hand-written root entry). `init`
  now drops a self-contained `sdlc-studio/.gitignore` (`.local/`) - never touching the project's own
  root `.gitignore`. Idempotent.

- **duplicate-id gate false-positived on the canonical two-table story index (BG0035, field
  report):** `reconcile.detect_duplicate_rows` counted an id across ALL tables in an `_index.md`,
  but the story-index template ships two id-bearing views (`Stories by Epic` + `All Stories`), so
  every story id was flagged twice (a field upgrade saw duplicate-id: 33). Detection is now
  **per-table**: an id once-per-view across the two tables is not a duplicate; a repeat *within*
  one table (the silent-collapse bug it guards, CR0055/BG0022) still flags. The template's
  two-view layout is valid again - no need to gut the per-epic view to pass the gate.

- **`--no-artifacts` behaviour de-duplicated to one canonical anchor (CR0102, RV0005 audit):**
  the suppressed-files / still-enforced-gates lists were restated verbatim across
  `reference-epic.md`, `reference-story.md`, and `reference-outputs.md` (drift risk on any change
  to the gate set). `reference-epic.md#flag-no-artifacts` is now the single source; story and
  outputs point to it and keep only their file-local framing (story-phase flow / status-flow shape).

- **Story Completion Cascade re-anchored on the deterministic close (CR0100, RV0005 audit):**
  `reference-outputs.md#story-completion-cascade` led with prose telling the agent to hand-edit the
  story Status, index rows, summary counts, and epic checkbox - exactly what `artifact.py close` /
  `transition.py` now own. It now leads with the deterministic close and marks steps 7-8 as
  script-owned (do not hand-edit), leaving only the genuine judgement residue as model steps.

- **`help/reconcile.md` now names the deterministic `scripts/reconcile.py` (CR0101, RV0005
  audit):** the per-command help framed all index/count/status fixes as model prose with no
  pointer to the script, inviting hand-recomputed counts (a recorded corruption mode). It now
  names the script (`detect`/`apply`/`--dry-run`), carries a do-not-hand-edit caution, and lists
  it in the See Also REQUIRED block.

- **`sprint plan` silently selected an empty batch for a lowercase status arg (BG0034, RV0005
  audit):** the documented form (`sprint --crs proposed`) never matched, because `select_batch`
  compared the raw arg against the canonical title-case vocab. The arg is now canonicalised
  (`proposed` == `Proposed`) and an unknown status fails loudly listing the valid vocabulary,
  instead of returning a silent zero-item batch. Docs aligned to title-case. (Found by the
  adversarial determinism lens; it was an untested path.)

## [2.5.0] - 2026-06-22

### Added

- **CI coverage + security gates (CR0076):** `lint.yml` now runs a coverage floor (>= 80% of the
  runtime scripts; currently 83%) and a `bandit` Python security scan. Three intentional patterns got
  justified `# nosec` (the project-authored AC verifier's `shell=True`; the https-only version check).
- **Test-reference routing map (CR0075):** `help/references.md` now maps the five `reference-test-*.md`
  to their distinct tasks (spec / automation / best-practices / brownfield-validation / E2E), so the
  right one is obvious. (A physical file-merge was assessed and deferred - the files are genuinely
  distinct and a merge would bloat an at-ceiling file for marginal gain.)
- **Navigation entry points (CR0074):** a 'which persona doc do I use' routing table
  (`reference-persona.md#which-doc`), a grouped overview of the gate's checks in `help/gate.md`
  (artifact-quality / index / provenance / skill-docs - replacing its stale 5-check line), and
  Progressive-Loading rows for persona create/consult and test-spec/automation.
- **doc-freshness advisory gate check (CR0073):** a new non-blocking `gate.py` check that flags when
  `LATEST.md`'s claimed version / test count / disclosure count drift from reality - the state-anchor
  staleness the audit caught by hand. Skill-only, read-only; only checks facts LATEST.md actually states.

## [2.4.4] - 2026-06-22

### Fixed

- **npm vulnerabilities cleared (BG0033):** the 5 moderate advisories (brace-expansion, js-yaml,
  markdown-it, smol-toml via `markdownlint-cli`) are gone - `npm audit fix` + `markdownlint-cli` ^0.49.0.
  `npm audit` reports 0; lint still passes on the new line.

### Changed

- **project_upgrade determinism hygiene (CR0071):** `.version` date is now injectable (deterministic
  tests) and the persona scan uses a sorted glob - reproducible regardless of filesystem order.

### Added

- **Test-density backfill (CR0070):** +145 substantive tests on the highest-risk under-tested scripts
  - `repo_map` (13->69), `github_sync` (15->59, `gh` fully mocked), `lessons` (13->58) - covering AST
  parsing, the sync diff/state logic, recall/prune, and edge cases. Suite now 789 tests. (Surfaced two
  documented behaviour-limits; a lessons docstring was corrected.)
- **CONTRIBUTING dev-bootstrap (CR0072):** a Development Workflow section (setup, gate-every-commit,
  trunk-based discipline, the bug/CR/RFC lifecycle, the regression-test obligation, forward-porting)
  plus an Architecture pointer - so a new contributor can get productive without reading the source.
- **Table-parser regression battery (CR0069):** a 20-test edge-case suite (`test_table_parsers.py`)
  locks the shared `table_cells` / `join_row` / `canonical_status` primitives - escaped pipes,
  ragged/empty/unicode cells, separator variants, join round-trip, status-token boundaries. Closes the
  reconcile-lineage fault class at the parser level (no live bug found; pure hardening).
- **`deploy` - the orchestrate-only deploy last-mile (RFC0013, CR0066-0068):** a new workflow that
  **gates** before, **verifies** after, and **records** a deploy - without owning the runtime. The
  project supplies `deploy.{command,smoke,soak_minutes,rollback}` in `.config.yaml`; the skill never
  holds the production trigger, never auto-rolls-back, and **never deploys inside `autosprint`**
  (deploy is a stop-condition action). `scripts/deploy.py preflight` gives a gate-backed readiness
  verdict + the operator hand-off; `deploy.py record` logs the outcome to `sdlc-studio/deploy-log.md`.
  Smoke green == rolled-out; a soak window is required for verified. Ecosystem-neutral; no secrets read.
- **Domain-neutrality lint guard (`lint:neutrality`):** a CI check fails if a private
  project/product/repo name appears in a tracked file. The blocklist is stored as SHA-256
  **hashes** (never plaintext) so the guard - itself a public file - does not reveal the names it
  guards, and its output redacts matches to a hash prefix. Sub-token aware (a base name catches
  hyphenated variants). Caught and cleared 3 pre-existing leaks on first run.

## [2.4.3] - 2026-06-22

### Added

- **RFC0013 (deploy last-mile) pressure-tested and settled:** four adversarial lenses sharpened it
  to **Option A orchestrate-only** (skill gates + verifies + records around an operator-triggered
  deploy; no auto-execute, no auto-rollback, never inside the autonomous loop); D1-D7 decided, build
  deferred until a consuming project needs a deploy it cannot already sequence itself.
- **Document-owner review seats + requirements-met sign-off (CR0065):** the **Product Owner** seat
  owns the PRD and signs a "PRD requirements satisfied" verdict in `review` (every project); the
  **Product Manager** seat owns the PVD and signs a "PVD requirements satisfied" verdict via a new
  PVD review leg - **only when `sdlc-studio/product/pvd.md` exists** (a single-repo project has no
  PVD, so neither the seat nor the leg applies). Corrects the prior workflow-personas mislabel that
  called the product/PRD seat "PM".

## [2.4.2] - 2026-06-22

### Fixed

- **reconcile reads the Status cell by vocab token, not a fixed column (BG0032):** indexes whose
  tables stack multiple schemas (Status in different columns) or have header-less blocks no longer
  misread off-schema rows as `Unknown` (which produced phantom status/count drift); apply rewrites
  only when the pinned column holds a status, never guessing a cell. (~90 phantom drifts -> 9 on a real repo.)
- **`project upgrade --apply` no longer bundles reconcile (BG0029):** it applies only the safe
  deterministic set (config + `.version`); reconcile is opt-in via `--with-reconcile`, so an upgrade
  can't rewrite/corrupt indexes. Index drift is reported as a `review with reconcile` item.
- **`.version` bump preserves author fields (BG0030):** the skill/schema bump is a surgical update
  that keeps `created_at` (and any other lines) instead of overwriting from a template.
- **reconcile `--apply` never deletes index rows (BG0031):** orphan/missing rows stay report-only;
  an inline-only record is never removed. Locked with a regression test.

## [2.4.1] - 2026-06-22

### Added

- **Charter review fast-follow:** the agent-instructions starter documents the one-canonical-summary
  index convention and the `Verify: manual` / never-hand-stamp rules.

### Fixed

- **verify_ac handles prose/manual Verify lines (BG0028):** a Verify line led by `manual`/`manually`
  is counted **manual** (never executed), so a human-checked AC can't be shelled out, time out, and
  report a false `failed`. Real commands are unaffected. `Verify: manual <description>` documented.
- **persona checks ignore non-design files (BG0027):** `project upgrade`'s old-model detector and
  `validate personas` no longer flag a `consult-guide`, a README, or the `seats/` review-seat charters
  as old/ill-formed design personas - so a migrated project stops reporting a phantom persona item.
- **reconcile no longer corrupts per-epic count tables (BG0026):** `reconcile --apply` (and thus
  gate/autosprint/`project upgrade`) recomputes only the canonical global summary (the `Status|Count`
  block with a `**Total**` row, or the sole summary); scoped per-epic/per-section count tables are left
  to the author. Previously it stamped the fleet total into every one (hit a consuming project: per-epic Done 6 -> 590).
- **project upgrade dry-run now reports the stale `.version` bump (BG0025):** a present-but-stale
  `.version` (older skill than installed) is reported as auto-correctable, matching what `--apply`
  does - the dry-run no longer says "nothing auto-correctable" while apply bumps it.
- **version_check no longer serves a stale `latest` older than installed (BG0024):** a fresh
  TTL cache whose `latest` predates the installed version is treated as stale and re-fetched (you
  cannot install newer-than-latest), so post-release the check stops reporting the old version.

### Changed

- **Consumer-copied templates carry no framework tracking IDs:** the persona template, review-seat
  charter, `config-defaults.yaml`, and `product-manifest.yaml` no longer cite the framework's internal
  RFC/CR numbers in their comments, so a project that copies them gets no framework-provenance noise.
- **Disclosure backlog driven to zero (CR0064):** fixed the 28 real gaps the disclosure check found
  in the skill's own source (24 scripts `chmod +x`, 4 `Load when:` markers, 2 section files indexed)
  and refined the check to clear 38 false-positives - help/<type>.md is reachable via the
  `help/{type}.md` Progressive-Loading pattern, and the template placeholder check is scoped to
  `templates/core/` (fill scaffolds), not guidance modules/prompts. `disclosure` now reports 0.

## [2.4.0] - 2026-06-21

### Added

- **Critic verdicts no longer trip MD037 (BG0023):** `critic._clean` now escapes `_` so an
  underscored identifier in the issues text cannot pair into markdown emphasis - a recurring lint
  papercut when recording verdicts about code (`_read`, `_index_row`).
- **Progressive-disclosure + best-practice check (CR0063):** `scripts/disclosure.py` (advisory) flags
  reference-/help- files missing a `Load when:` trigger or orphaned from every index, plus best-practice
  items (scripts executable + `--help`, templates use `{{placeholder}}`, SKILL.md has When-to-Use). The
  skill is loaded into sessions, so disclosure discipline is a token lever; the check holds new files to
  it and reports the existing backlog. Skill-dev only (no-op for consuming repos); wired into the gate
  NON-BLOCKING; `--strict` opts into enforcement. `npm run lint:disclosure`.
- **`project upgrade` - migrate a consuming project to current conventions (CR0062):** `skill-update`
  updates the tool; `project upgrade` (`scripts/project_upgrade.py`) updates a consuming PROJECT's
  artefacts. It detects the version/convention gap and reports a migration plan split into
  auto-correctable (scaffold `.config.yaml` with a `provenance.adopt_after` cutoff, scaffold/bump
  `.version`, reconcile drift - applied only with `--apply`) and needs-judgement (old personas ->
  Cooper / review-seat charters, AGENTS refresh, missing `Verify:` - reported, never auto-applied,
  never filed as CRs). Dry-run by default, idempotent; skill-update offers it after a version bump.

## [2.3.0] - 2026-06-21

### Added

- **RFC0016 resolved - review-seat charters + isolated consults (CR0060):** review seats (the
  Three Amigos + PM/PO owners) are now structured **charters** (`review-seat-charter.md`, with a
  mandatory `shadow`) consulted as **isolated subagents** with an explicit synthesis step, reusing
  the existing critic/decision ledgers as the externalised record. Clears the stale pre-RFC0017
  fields from the consult prompts. The authored-identity tail (broker, drift-detection, ratified
  canon) is declined as out-of-scope (the external identity system). Review seats are distinct
  from RFC0017's Cooper design personas.
- **Stakes-scaled review depth (CR0061):** the autosprint independent critic now scales to risk -
  a full adversarial sub-agent for code/risky units, a lighter recorded review for pure-doc/
  mechanical ones - so review tokens are spent in proportion. The `critiqued` gate still requires a
  committed verdict (the tier is noted), so depth scales without losing honesty. From the RV0004
  over-engineering/token review.
- **Persona well-formedness check (CR0059, RFC0017 WS3):** `validate.py personas` flags a
  goal-directed persona missing a section for its cast role - advisory (exits 0, not in the hard
  gate). Cast-role-aware: the Negative variant (Why-not, no Experience Goals) and Customer/Served
  (Experience + Scenario optional) are not false-flagged; a missing cast role is itself flagged.
  Prefix-matched headings so an unrelated `## Context` does not satisfy Behaviours. Surfaced via
  `persona review`.
- **Cooper goal-directed persona model (CR0058, RFC0017 WS1):** the persona template and
  reference-persona model move from demographic categories to Alan Cooper's goal-directed model -
  a full cast (Primary / Secondary / Supplemental / Negative / Customer / Served), ordered End
  goals + Experience goals, and a **well-formed persona file** as the bar (structural, not
  research-gated; a Negative persona uses a variant shape - goals stated-to-exclude + a why-not -
  per the dogfood learning). Design personas (the product's users) are distinguished from review seats
  (the Three Amigos, RFC0016). No research/evidence apparatus and no authored-identity machinery -
  a goal-directed persona is good input to an external identity system, nothing sdlc-studio builds.
- **Unified artifact create paths (CR0057):** the two create paths (`artifact new` and the
  finding filer `file_finding`) no longer diverge - the filer now writes the same provenance
  stamp (so `provenance check` stops false-flagging filer-created artifacts), both build index
  rows through one shared header-driven builder (`sdlc_md.row_from_header`, `find_data_header`,
  `join_row` - also used by reconcile), and `--dry-run` (preview, write nothing) is available
  on `artifact new`/`close`, `file_finding file`, and `pvd sync`.
- **artifact new correctness (BG0022):** a story created for a non-existent epic now raises
  before writing any file (no silent orphan), and id allocation honours local files, lingering
  index rows, AND origin/main (`next_id.allocate_number`) - never re-issuing an id that exists
  only on the remote or as a stale index row.
- **Help reframed around autosprint (CR0054):** help now leads with getting-started and the
  autosprint (Goal-Driven Development) loop as the recommended path; the by-hand per-tool
  pipeline is retained but secondary. The catalogue lists every command (pvd, gate, provenance,
  telemetry, artifact new/close, skill-update, product reconcile); references.md adds
  reference-autosprint/-pvd/-skill-update; arguments.md adds the autosprint and gate flags.
- **Unfilled-placeholder gate (CR0056):** a freshly-scaffolded story used to pass conformance
  (specified + verifiable) and validate with pure `{{placeholder}}` AC/Verify content - a hidden
  hole. validate now flags a metadata or AC-structural line whose value is placeholder-ONLY as
  an error, and conformance treats a placeholder-only AC/Verify as not-yet-specified (a scaffold
  cannot reach Done with unfilled slots). Scoped to placeholder-only values, so prose that
  references `{{...}}` syntax and a real AC that mentions a token are never flagged; the two
  gates agree on what counts as filled.
- **Gate duplicate-id + provenance checks (CR0055):** the gate now flags duplicate artifact
  ids - both duplicate files (next_id) and duplicate index ROWS (reconcile keyed rows into a
  dict, so a second `US0001` row silently overwrote the first: zero drift, false PASS - now
  `reconcile.detect_duplicate_rows` counts the raw rows). Provenance is also registered as a
  gate check, blocking only when `provenance.enforce` (the constitution opt-in pattern).
- **Documentation in the autosprint Definition of Done (CR0053):** a new `documented`
  conformance stage + a deterministic `scripts/doc_coverage.py` gate - every Type-Reference
  command must be in the help catalogue and every script in reference-scripts.md (a prose
  mention does not count); empty CHANGELOG [Unreleased] is a soft warn; no-op for consuming
  repos. Wired into the gate (blocking) + conformance. reference-autosprint's DoD now requires
  user/operator docs updated, a structured final report, and a Phase-1 clarify step. Closing
  the gap the self-audit found - it immediately forced 15 undocumented commands/scripts green.
- **Artifact provenance: stamp + check + remake (CR0052):** `new` stamps every artifact
  it creates (`> **Created-by:** sdlc-studio ...`); `scripts/provenance.py check` flags
  un-stamped artifacts past `provenance.adopt_after` with remediation (advisory;
  `provenance.enforce` to block; legacy exempt); `remake` content-preservingly backfills
  the stamp (idempotent, dry-run-able, header-anchored - never touches the body). Makes
  deterministic creation the checkable path.
- **Portable CI quality gate (CR0046):** `scripts/gate.py` aggregates the
  deterministic checks (conformance, reconcile drift, validate, constitution, integrity)
  into one consolidated pass/fail and exits non-zero only on a blocking failure; `--only`
  /`--skip` select checks, constitution blocks only when enforced, and a wrong/missing
  `--root` fails rather than passing vacuously. No network, no CI/cloud assumption -
  runnable in any CI or a pre-commit hook (`help/gate.md` shows GitHub Actions / GitLab /
  shell wiring).
- **Product Vision Document - the multi-repo product layer (CR0047, RFC0015 WS1):** a tiered
  `templates/core/pvd.md` (vision/goals/feature-map/cross-repo-deps/contracts/risks/decisions
  always; topology tree + G1-G5 gates + release coordination opt-in) and a
  `templates/product-manifest.yaml` listing the child repos. The PVD coordinates and traces
  (product feature -> owning repo -> PRD feature), never re-specifies; Product Manager owns it.
- **PVD projection + drift (CR0048, RFC0015 WS2):** `scripts/pvd.py sync` projects the one
  writable master PVD into each child repo read-only (copy in dev, symlink in prod);
  `drift` reports in-sync / stale / behind / missing, and an unreadable/missing master
  reports error rather than a vacuous in-sync.
- **Cross-repo feature-map traceability (CR0049, RFC0015 WS3):** `scripts/product_reconcile.py`
  verifies every product feature `PF####` in the PVD maps to a feature actually declared in
  its owning repo's PRD (orphan / unknown-repo / missing-path block; absent repo + empty map
  degrade with an un-verified count). Declaration-anchored - a prose mention never false-passes.
  Completes the PVD core (WS1-3); the contract layer + governance stay deferred.
- **Deterministic artifact create + close (CR0045):** `scripts/artifact.py new --type <any
  of the 8 numbered types>` allocates the id, renders a valid scaffold, appends the
  header-matched index row, recomputes counts, and wires a story into its epic's Story
  Breakdown - one command for what was a ~10-step hand cascade. `close --id` terminal-
  transitions by id. Shares file_finding.append_index_row. This CR's own story (US0035) was
  created and closed *by the tool itself* (dogfood).
- **Run telemetry recorder (CR0050, RFC0014 WS1):** `scripts/telemetry.py record` appends a
  per-unit run outcome to the gitignored `sdlc-studio/.local/telemetry.jsonl` (local-only, no
  network, advisory - never raises into the loop; only whitelisted non-None fields written).
  Feeds the deferred calibrate step + RFC0009 WS5.
- **Close cascade records telemetry (CR0051, RFC0014 WS2):** `artifact close` records a
  telemetry event (id, type, plus `--iterations`/`--verdict`/`--wall-time-s`/`--stages`)
  after the transition - advisory, never affects the close. Run data now accrues
  automatically on every unit close.

## [2.2.0] - 2026-06-21

Self-update: the skill now notices new releases itself. On the first `status`/`hint`
of a session it compares its installed version against the latest GitHub release and
prints a one-line notice if newer; **`skill-update`** upgrades the scope-detected
install on confirm, with a per-version snooze so it never nags. On by default, silent
offline, opt-out via `version_check.enabled`. Drop-in upgrade from v2.1.

### Added

- **Skill version check + `skill-update` (CR0044):** on the first `status`/`hint` of a
  session the skill compares its installed version against the latest GitHub release and
  prints a one-line notice if newer; `/sdlc-studio skill-update` upgrades the
  scope-detected install (user / project / agents) via the installer on explicit
  confirm. Deterministic `scripts/version_check.py` (TTL-cached, silent offline,
  per-version snooze so it never nags until a newer release); on by default, opt-out via
  `version_check.enabled: false`. Distinct from `upgrade` (project schema migration).

## [2.1.0] - 2026-06-21

Goal-Driven Development arrives: the **`autosprint`** autonomous loop with hard
guardrails (decisions ledger, iteration cap, completion oracle, conformance gate,
independent critic), plus a deterministic control plane around it - complexity +
churn-weighted test risk, a portable adversarial `audit` harness with a deterministic
filer, an optional project `constitution` gate, progressive-disclosure index archival,
deterministic status transitions, and per-project config. No artifact-schema change
(`schema_version` still 2); a drop-in upgrade from v2.0.

### Fixed

- **Escaped pipes in table cells (BG0021):** every table parser now shares one
  `sdlc_md.table_cells` splitter that honours `\|`, so a cell that legitimately
  contains a pipe (e.g. an index title `string \| string[]`, an RFC workstream
  `All\|Crew`) no longer shifts the columns after it and misreads the row.
  Unified `reconcile`, `critic`, `rfc`, and `ledger` onto it.

### Removed

- **15 baked fictional-character persona files (RFC0007 / CR0034):** the
  `templates/personas/stakeholders/**` and `team/**` characters (~1680 lines of
  invented backstory shipped in every install) are removed. Personas now generate on
  demand: `persona create --from-archetype <slug>` builds the full persona from
  `persona-template.md` + the retained archetype seeds (role + one-line disposition)
  in `reference-persona.md#archetypes`. A migration note is in that file; a consuming
  project regenerates any personas it referenced. Aligns with Create-vs-Generate.

### Changed

- **Test references consolidated (RFC0008 / CR0033):** the triplicated test
  anti-patterns are deduped into one `reference-test-best-practices.md#test-anti-patterns`
  section (8 patterns + the integration-dependency and low-coverage checklists);
  `reference-test-pitfalls.md` and the subsumed `#common-ai-testing-mistakes` section
  are removed (no content lost); and `reference-test-validation.md` /
  `reference-test-e2e-guidelines.md` are now reachable from the SKILL.md router.
- **repo_map documented honestly (RFC0004 / CR0032):** reframed as a lexical
  relevance ranker (token overlap + import in-degree bonus), not a semantic call
  graph or PageRank, with a soft-dependency pointer to Aider's repo map / RepoMapper
  for graph-based ranking. Documentation only; ranking behaviour unchanged.
- **`reconcile.apply_type` decomposed (CR0030):** acting on RFC0009's own
  refactor-first signal (the complexity tool flagged it as the top hotspot at
  cognitive 56), `apply_type` is split into single-purpose helpers and reduced to 7,
  with behaviour held identical by the CR0026 corruption-guard suite and a regression
  guard against regrowth. No behaviour change.
- **Strict Agent Skills spec conformance:** the Claude-Code-only
  `argument-hint` frontmatter field is dropped (its content is already in the
  description verbatim) and `tools/validate_skill.py` now enforces the spec's
  closed six-field set - exactly what the official `skills-ref` validator
  rejects ("Unexpected fields in frontmatter"). The skill now passes strict
  reference validation.

### Added

- **Complexity/churn test-risk band (RFC0009 WS4 / CR0043):** `complexity.py` gains a git
  `churn` signal and a churn-weighted `composite_risk` band (low/medium/high) exposed by
  `assess` as `risk_band`. Churn is weighted ~3x complexity - grounded in the calibration
  (bug-affected files were ~4.9x more churned vs ~1.8x more complex). A complex- or
  hot-alone file floors to at least medium. `reference-test-best-practices.md#complexity-test-risk`
  maps the band to coverage / scenario / verification-tier depth. WS5 (wave-sizing by run
  cost) stays deferred - the calibration proves defect risk, not cost.
- **Deterministic status-transition helper (CR0042):** `scripts/transition.py set --id
  <ID> --status <new>` performs the last hand-driven write cascade - set the artifact's
  `Status`, sync its index row + summary counts (reusing `reconcile.apply_type`), and
  tick/untick a story's checkbox in the parent epic's Story Breakdown. `index_synced`
  reflects the true post-state (warns on an archived row or a status with no summary
  row). Retires the manual "mark it Done + update the index" edit.
- **Progressive-disclosure indexes (RFC0012 / CR0041):** `scripts/archive.py archive
  --type <t> --release <r>` bounds a large `_index.md` by moving the master table's
  terminal rows into `<type>/archive/{release}/{type}.md` (rows move, files stay),
  leaving a bullet pointer. `reconcile.parse_index` now unions the archive sub-indexes,
  so the census stays exact (archived artifacts are never `missing-row`; counts =
  active+archived) - the stale-counts risk is removed by counting the real archived
  rows, not a summary. Conventions + slice-read guidance in reference-outputs.md.
  Proven read-only at scale on consuming repo B (371 stories / 407 CRs archivable).
- **Project constitution gate (RFC0005 / CR0040):** an optional
  `sdlc-studio/constitution.md` lets a project declare inviolable principles;
  `scripts/constitution.py check` asserts the machine-checkable ones across the artifact
  graph. Each checkable principle carries a `` `rule:` `` from a fixed vocabulary
  (story-requires-epic, story-has-ac, ac-requires-verify, links-resolve, status-in-vocab,
  no-index-drift) that maps onto the existing integrity/conformance/validate/reconcile
  checks; free-text principles are advisory. Advisory by default; `constitution.enforce:
  true` makes a violation fail the check. Proven against consuming repo A + consuming repo B.
- **autosprint `--order wsjf` (RFC0009 WS3 / CR0038):** the WSJF stub is now real -
  priority stays dominant and the cognitive complexity of a unit's `Affects` files
  (scored by complexity.py) breaks ties within a priority, so the smaller blast-radius
  job goes first; the plan also carries a complexity-weighted per-unit token budget.
  Degrades to plain priority when no complexity is known; complexity never overrides
  priority; dependencies still win.
- **Packaged skill-audit lens pack (RFC0002 WS5 / CR0039):**
  `templates/audit-profiles/skill.md` declares the four skill lenses as a loadable
  profile for the audit harness.
- **Adversarial audit harness (RFC0002 / CR0035-CR0037):** the portable, tool-neutral
  `audit` methodology - `reference-audit.md` (find -> refute-panel verify -> merge ->
  file pipeline, project + skill lens profiles, N-of-M refute, budget controls), the
  `templates/automation/audit-{finder,refute,classify}.md` prompt harness, and a
  deterministic `scripts/file_finding.py` filer that writes a structured (non-hollow)
  Bug/CR/RFC, allocates the ID, and keeps the index in sync. The wired `/audit` command
  (WS4) and skill-profile pack (WS5) remain deferred.
- **Code-complexity signals (RFC0009 / CR0028 / CR0029):** new `scripts/complexity.py`
  computes cognitive (SonarSource) and cyclomatic complexity per function from Python's
  `ast` (pure stdlib; `lizard` soft-dep for other languages, degrading to unscored).
  `repo_map` emits per-function scores into the map. `code plan` (reference-code.md
  step 6b) runs `complexity assess` over a change's blast radius to weight the estimate
  by difficulty and recommend a scoped refactor-first for hotspots - advisory, never a
  gate. Threshold is `complexity.cognitive_high` (default 15). WS3/4/5 stay deferred.
- **Per-project status vocabulary (CR0027):** a project can declare extra statuses
  in `sdlc-studio/.config.yaml` under `status_vocab.<type>` (e.g. `story: [Gated]`)
  and reconcile/validate/conformance recognise them instead of parsing the row as
  `Unknown`; extensions add to the shared base, never replace it. `Blocked` is now a
  base story status. Reads via a new fully-degrading `sdlc_md.project_override`.
- **Conformance adoption cutoff (CR0027, extended CR0031):** `conformance.adopt_after:
  USnnnn` exempts pre-adoption stories - both from the conformance gate (reported,
  never counted non-conformant) and from `validate`'s `no-ac` error - so a project that
  turns the AC discipline on partway is not buried in permanent legacy findings. Fails
  safe: any uncertainty (no config / no PyYAML / malformed / unparseable id) judges the
  story as before.
- **`reconcile apply` (RFC0003 / CR0026):** the mechanical index fixes are now a
  deterministic, idempotent script step - `reconcile apply [--scope] [--dry-run]`
  rewrites each drifted index row's Status cell (positionally, by header) to the
  file's status and recomputes the summary counts from the same `parse_index`
  authority `detect` uses. `--dry-run` reports without writing; cells are
  re-escaped on write; structural classes (missing/orphan-row, missing-index)
  stay report-only. Replaces ~3-4k tokens of re-derived prose per cadence trigger.
- **Generic `agents` installer target:** `--target agents` installs to
  `.agents/skills`, the neutral directory read by Codex, Gemini CLI, Copilot,
  and Cursor - one copy serves all four. `codex` and `agents` resolve to the
  same directory and the installers dedup; docs note Claude Code does not
  read it.

## [2.0.0] - 2026-06-12

The open-format release. SDLC Studio is now formally a standard
[Agent Skill](https://agentskills.io) - one folder that works in Claude
Code, Codex, Gemini CLI, opencode, and Copilot - with an installer that
keeps every copy fresh, consolidated and budgeted documentation, two new
deterministic helpers, CI guards for spec conformance and version
consistency, behavioural eval scenarios, and two workflow gates adopted
from AWS AI-DLC. No consuming-project migration: the artifact schema is
unchanged.

### Changed

- **SKILL.md frontmatter conforms to the Agent Skills open standard**
  (agentskills.io): adds `license`, `compatibility` (Python 3.10+, gh CLI;
  agentic waves Claude-Code-only), `metadata.version`, and `argument-hint`;
  the description now leads with capability and an explicit "Use when..."
  trigger sentence while keeping every existing trigger term.
- **Script examples use `$CLAUDE_SKILL_DIR`** instead of the project-local
  `.claude/skills/sdlc-studio/` path, so they work at personal, project, and
  plugin install levels; one canonical fallback rule for other tools lives at
  `reference-scripts.md#skill-dir`.
- **Repo-root agent instructions follow the cross-tool convention the skill
  itself recommends:** substantive guidance moved to a new `AGENTS.md`
  (read directly by Codex, Copilot, Cursor, Gemini); `CLAUDE.md` is now an
  `@AGENTS.md` import plus Claude-Code-only notes.
- **Duplicated instruction blocks consolidated to canonical homes** with
  do-not-restate pointers: story completion cascade
  (`reference-outputs.md#story-completion-cascade`), Three Amigos per-persona
  focus lists (`reference-workflow-personas.md`), wave quality gates
  (`reference-project.md#quality-gates`), and the agent prompt template (new
  file). `reference-epic.md` shrinks 1191 -> ~1050 lines.
- **Every reference and help file over 100 lines now opens with a
  `Load when:` hint** (one convention; the older multi-line `Load:` blocks
  renamed), and large reference files gain a Contents list so partial reads
  reveal scope. The story Ready validation pseudocode is replaced by a
  pointer to `validate.py check` (determinism in scripts, judgement in
  Claude).
- **README rewritten for v2** (521 -> ~200 lines): open Agent Skills
  positioning, the five-tool install matrix with per-tool invocation, the
  stale-copy sweep, feature tour, v1.x upgrade notes (no project migration),
  and a v2.1 roadmap (task DAGs, review iteration history, artifact graph -
  recorded from the AI-DLC review).

### Fixed

- **`verify_ac.py` counts stale downgrades.** A `yes` Verified state
  downgraded to `no` now increments the report's `stale` counter (apply and
  dry-run modes); previously it was always 0, hiding regressions from
  `verify-report.json`.
- **`verify_ac.py` inserts new Verified lines at the right anchor.** The
  fallback tracked the first bullet of an AC block instead of the last; the
  Verify line, once seen, now holds the insertion anchor so the canonical
  bullet order (Given / When / Then / Verify / Verified) is preserved.
- **Story workflow phase order reconciled to the 8-phase canon** (Plan, Test
  Spec, Tests, Implement, Test, Verify, Check, Review) across
  `reference-story.md`, `reference-decisions.md` (checkpoint relabel plus a
  missing Phase 8 entry), `help/story.md`, and `templates/core/workflow.md`;
  `--from-phase N` is no longer ambiguous between Tests and Implement.
- **Broken file references repaired:** `reference-epic.md` (epic workflow
  template), `reference-story.md` (cohesion findings template),
  `reference-test-pitfalls.md` (pre-v2 TSD template name), and
  `reference-code.md` (best-practices paths now skill-relative instead of
  `~/.claude/best-practices/`).
- **`install.sh` exit status no longer clobbered by the cleanup trap.** With an
  empty `TMP_DIR` (e.g. `--list-targets`, `--dry-run`), the EXIT trap's failed
  test made the script exit 1 under `set -e` even after success.
- **Best-practices corrections:** `docker.md` Python base images bumped to
  3.13, `openapi.md` example matches the recommended 3.1.1, `postgresql.md`
  drops an EOL version qualifier, `sql.md` notes `/*+ LEADING */` is
  Oracle/MySQL-only syntax.

### Added

- **`evals/` behavioural regression scenarios** - four manually-run
  two-Claude scenarios (worker session + grader session) covering trigger
  routing, the greenfield create path, the generate-mode philosophy gate,
  and reconcile dry-run safety; wired into the release gate. The
  counterpart to `scripts/tests/` for the skill's *instructions*.
- **Blind review gate** (adopted from AWS AI-DLC): before implementation,
  `story plan` re-reads the story's AC and judges the plan's task list from
  the task descriptions alone - no code - asking whether every AC would be
  satisfied as written (`reference-story.md#blind-review`, checkpoint row in
  `reference-decisions.md`). Catches semantic drift that test execution
  cannot.
- **Structured clarification convention** (adopted from AWS AI-DLC): pauses
  pose 2-4 concrete options with an evidence-favoured suggestion instead of
  open prose questions
  (`reference-agent-prompt-template.md#structured-clarifications`, wired into
  the execution contract's blocker row).
- **`reference-agent-prompt-template.md`** - the agentic wave prompt template
  extracted from `reference-epic.md` into its own canonical file (its three
  consumers - epic waves, project orchestration, lessons injection - now load
  it without the rest of the epic reference).
- **`scripts/plan.py` and `scripts/lessons.py`** - stdlib-only helpers that
  replace procedural prose with deterministic, tested code: `plan.py
  list|archive` manages Claude Code plan-mode files under `~/.claude/plans/`
  (active/stale tables, archive by year-month; the one script that writes
  outside `.local/`, to that operator-owned directory, never deleting or
  overwriting), and `lessons.py list|add|prune|recall` manages both lesson
  tiers (project `.local/lessons.md` with L-NNNN allocation and newest-first
  insertion; the skill's cross-project `lessons/` registry with LL-ID
  allocation, `_template.md` instantiation, and `_index.md` row upkeep).
- **`tools/validate_skill.py`** - stdlib-only CI validator for SKILL.md
  frontmatter against the agentskills.io spec subset (name pattern and
  directory match, description length, known-field allowlist, semver
  `metadata.version`); wired into `npm run lint` as `lint:skill`.
- **`tools/check_versions.py` and `tools/check_budgets.py`** - CI guards
  wired into `npm run lint`: the version checker asserts the four
  authoritative version homes agree by structured extraction (never
  repo-wide grep; `--strict` adds the CHANGELOG topmost release for the
  release gate), and the budget guard holds SKILL.md under 500 lines and
  un-allowlisted reference files under 600 (allowlisted files carry a
  recorded ceiling +5% tolerance, so they cannot silently regrow).
  `templates/workflows/release-gate.md` gains both checks plus the eval run.
- **Installer stale-copy sweep:** after installing to the chosen targets,
  `install.sh` and `install.ps1` refresh every other sdlc-studio copy found in
  the known tool locations (identity-checked: only directories whose SKILL.md
  declares `name: sdlc-studio` are touched), reporting each as `old -> new`.
  Opt out with `--no-sweep` / `-NoSweep`; `--dry-run` previews the sweep; the
  Windows CI smoke test asserts both behaviours.
- **`plan` command surface:** `help/plan.md` plus SKILL.md and `help/help.md`
  entries for `/sdlc-studio plan list` / `plan archive`
  (`reference-plan-files.md` existed since v1.7.0 without them).
- **Four best-practices guides:** `typescript.md`, `rust.md` (referenced by
  `reference-code.md` but missing), `java.md`, `csharp.md` (test-automation
  ships JUnit/xUnit templates with no matching guide); best-practices README
  index now lists every guide.
- **Regression tests** for both `verify_ac.py` fixes (stale counting in apply
  and dry-run modes, insertion-anchor parsing).

### Removed

- **`templates/workflows/workflow.md`** - an unreferenced duplicate of
  `templates/core/workflow.md` with divergent phase order and a 7-phase claim.

## [1.9.1] - 2026-06-10

Back-port of production fixes to the read-only helper scripts: `reconcile`,
`status`, and `validate` now tolerate real-world artefact conventions instead of
emitting false-positive drift. Folded in from live use on a project whose
artefacts use mixed id casing, decorated status lines, and plain-bullet
acceptance criteria.

### Fixed

- **`reconcile` no longer false-positives on six artefact conventions.** Case- and
  punctuation-insensitive id matching (a file `cr0001.md` matches an index row
  `CR-0001` instead of double-counting as missing-row + orphan-row); decorated
  statuses (`Done (v2.83.0) · **CR:** CR-0088`) canonicalise to their vocabulary
  token before comparison; status-less files (legacy docs, most CRs) assert
  nothing and are not status-mismatched; summary counts for such types reconcile
  against the index rows, not the file census; `*-consultations.md` notes are
  excluded from the census so they no longer clobber the real artefact; and
  reserved/retired index rows (`Proposed`/`Draft`/custom non-vocabulary states)
  with no file are treated as intentional reservations, not orphans. See
  `reference-reconcile.md#matching-tolerances`.
- **`status` tallies decorated statuses under their canonical token,** so
  `Done (v2.66.0)` counts as `Done` and done-percentages stay correct.
- **`validate` accepts more valid forms.** Acceptance criteria may be `### ACn`
  headings, compact `- **ACn:**` bullets, or a populated `## Acceptance Criteria`
  section; metadata fields parse with or without the leading `>` blockquote;
  decorated statuses pass the vocabulary check.

### Changed

- **Status vocabulary additions:** story gains `Proposed` (optional pre-Draft
  intake state); bug and CR gain `Superseded`. Docs in `reference-outputs.md`
  and `help/story.md` updated to match.
- **`lib/sdlc_md.py`** gains shared `norm_id()` and `canonical_status()` helpers
  and excludes `*-consultations.md` from `artifact_files()`; id regexes are now
  case-insensitive.

### Tests

- Script test count 101 → 123 (id-normalisation, canonical-status, decorated and
  plain-bullet AC, consultations exclusion, reserved-row, and count-authority
  regressions).

## [1.9.0] - 2026-06-09

`init` now seeds (or checks) the project's agent-instructions file, and a new
deterministic hygiene check keeps `AGENTS.md` / `CLAUDE.md` honest - wired into
`/sdlc-studio review`.

### Added

- **`validate.py instructions`** - a deterministic hygiene check for a project's
  agent-instructions files: `AGENTS.md` exists (canonical), `CLAUDE.md` is a
  `@AGENTS.md` pointer, the operating-doctrine and `LATEST.md` pointers are present, the
  pre-release gate and the context-compaction re-read rule are present, and the file is
  not bloated with per-ship narrative or stale version strings. Emits JSON; exits
  non-zero on a missing `AGENTS.md`.
- **`/sdlc-studio review` runs the instruction-file hygiene check** (via
  `validate.py instructions`, alongside `review_prep`), so a stale or bloated
  instructions file is caught as drift.

### Changed

- **`/sdlc-studio init` seeds or checks the agent-instructions file.** When `AGENTS.md`
  is absent, init creates it from `templates/agent-instructions.md` plus a one-line
  `CLAUDE.md` pointer (`@AGENTS.md`); when present, it runs `validate.py instructions`
  and suggests improvements rather than overwriting hand-written specifics. Current-state
  stays in `sdlc-studio/reviews/LATEST.md` (progressive disclosure), not in the
  instructions file.

### Tests

- Script test count 95 → 101 (the instruction-file check).

## [1.8.0] - 2026-06-09

Cross-tool portability and a determinism-first script layer. The skill stops
hard-coding `CLAUDE.md` so it runs from Codex and Copilot too, ships a starter
agent-instructions file, and moves its most mechanical workflows (census,
status, validation, ID allocation, review inputs) into tested read-only Python
helpers that emit JSON. The principle: determinism in scripts, judgement in
Claude. The five-leg review verdict and its CODE leg are never scripted.

### Added

- **Agent-instructions template** (`templates/agent-instructions.md`, plus
  `agent-instructions.CLAUDE.md` and `agent-instructions.README.md`): a
  tool-neutral starter for a consuming project. `AGENTS.md` is the canonical
  cross-tool file (read by Codex, Copilot, Cursor and others); Claude Code's
  `CLAUDE.md` imports it with `@AGENTS.md`. It carries the production-release
  gate (reconcile --verify plus the five-leg review) and the
  autonomous-execution-with-persona-consultation goal inline, and points at the
  doctrine rather than restating it.
- **Five read-only deterministic helpers** under `scripts/`, each emitting JSON
  the workflows consume: `reconcile.py detect` (file-census index drift),
  `status.py` (four-pillar census plus hint), `validate.py` (artifact-structure
  linter), `next_id.py` (cross-repo-safe ID allocation), and `review_prep.py`
  (the mechanical inputs the five-leg review consumes). Shared parsing lives in
  `scripts/lib/sdlc_md.py`, the single source of truth for the markdown
  conventions and the artifact-type and status-vocabulary tables.
- **Link-check CI** (`tools/check_links.py`, `npm run lint:links`): verifies
  every intra-skill `path.md#anchor` reference resolves. `npm test` and the
  script unit tests now also run in CI.
- **Cross-harness installer.** `install.sh` and `install.ps1` gain
  `--target claude|codex|gemini|opencode|copilot|all|auto` (plus `--uninstall`
  and `--list-targets`), installing the standard `SKILL.md` skill into each
  tool's skills directory. SDLC Studio is a standard Agent Skill, so it now runs
  from Codex, Gemini CLI, opencode and Copilot as well as Claude Code; native
  installers (`gh skills install`, `gemini skills install`) work too. New
  `docs/INSTALL.md` is the full install guide; the README install section is
  trimmed to a multi-harness summary that links to it.

### Changed

- **The skill no longer hard-codes `CLAUDE.md`.** Seventeen references across
  nine files now read "the project's agent-instructions file (`AGENTS.md`)", so
  the skill is portable to Copilot and Codex. `help/init.md` and
  `reference-doctrine.md` point at the new template.
- `reconcile`, `status`/`hint`, ID allocation, story Ready checks, and the
  unified review now invoke their helper script first and consume the JSON,
  keeping the manual walk as a fallback. The five-leg review verdict stays
  Claude's; the CODE leg is never scripted.
- The agent-instructions template instructs re-reading `reviews/LATEST.md` and
  running `status` after any context compaction or reset - portable across
  Claude Code, Codex, Copilot, and opencode.

### Fixed

- Hardened the three existing scripts: a corrupt `.local/*.json` now exits 2
  instead of raising a traceback; every `main()` wraps `KeyboardInterrupt`
  (exit 130) and unexpected errors (exit 1) per the script template; fixed a
  `repo_map` import-prefix bug; `github_sync push` no longer re-fetches the
  issue list once per record; removed a dead acceptance-criterion boundary
  block in `verify_ac`.
- Renamed `best-practices/readme.md` to `readme-guide.md` to remove a
  case-collision with `README.md` on case-insensitive filesystems.
- Fixed three pre-existing broken cross-reference anchors
  (`reference-epic.md#post-wave-merge-protocol`, and mis-named anchors in
  `reference-verify.md` and `templates/core/tsd.md`).
- Script test count rose from 46 to 95.

## [1.7.2] - 2026-06-05

Extends the style guard to corporate jargon, and restructures SKILL.md for
token efficiency via progressive disclosure. No behaviour changes.

### Added

- `tools/lint-style.sh` now also fails on the four banned corporate-jargon
  words, filtered through `tools/style-allowlist.txt`. The allowlist
  permits lines documenting the rule itself, plus the established term
  "user journey". The em-dash check now lives in the same script, which
  `npm run lint:style` calls.
- `help/arguments.md` (full flag reference) and `help/references.md` (the
  reference-file and template catalogue), loaded on demand.

### Changed

- **SKILL.md slimmed from 651 to 195 lines (~70%)** by relocating the
  command catalogue, argument reference, workflow diagrams, and reference
  index out of the always-loaded router into lazy-loaded `help/help.md`,
  new `help/arguments.md`, and new `help/references.md`. This cuts the
  per-invocation context cost with no feature loss: all 153 command
  strings and 55 flags are verified present in the relocated files. The
  Progressive Loading Guide gains routing rows for the new files.
- Reworded two metaphorical jargon uses (operator-heuristics, lessons
  help) to plainer wording; these were not allowlist candidates.

## [1.7.1] - 2026-06-05

Style and tooling housekeeping. No content or behaviour changes.

### Fixed

- Replaced 201 em-dashes across the skill docs, templates, lessons,
  README, CHANGELOG, and CLAUDE.md with spaced en-dashes, per the
  house style rule in CLAUDE.md. The v1.7.0 content reintroduced them
  because no automated check existed.
- Corrected a stale line-count note in CLAUDE.md (SKILL.md is 651
  lines, not 584).

### Changed

- `npm run lint` now also runs a style guard (`lint:style`) that fails
  on any em-dash in markdown, so the regression cannot recur. CI picks
  this up automatically via the existing `npm run lint` step.

## [1.7.0] - 2026-06-05

Field-tested patterns from real-world use, generalised and folded back
into the skill. This release adds a design-exploration artifact type,
an operating doctrine for onboarding, a cross-project lessons registry,
and hardening of the reconcile, review, and release workflows. The
v1.6.0 Python helper scripts are unchanged.

### Added

- **RFC artifact type** (`/sdlc-studio rfc`): a first-class artifact for
  exploring an unsettled design space *before* committing to a CR.
  Lifecycle: create, list, review, accept (spawns CRs), close
  (supersede/withdraw). Ships with `reference-rfc.md`, `help/rfc.md`, and
  `templates/core/rfc.md` + `templates/indexes/rfc.md`. RFCs share the
  cross-repo numbering guard with CRs.
- **Operating doctrine** (`reference-doctrine.md`): a project-agnostic
  manual for onboarding a Claude to any sdlc-studio project - the skill as
  an OS, the RFC/CR/ADR decision matrix, files-as-truth and reconcile
  discipline, review cadence, consult gates, TDD default, paperwork in the
  same commit, lessons recall, and cross-repo numbering. Surfaced from
  `/sdlc-studio init`.
- **Cross-project lessons registry** (`lessons/`): a release-curated set of
  generalisable engineering/process lessons (seeded with six) that any
  project can recall before substantive decisions, distinct from a
  project's own transient `.local/lessons.md`. Recall and promote hooks
  documented in `help/lessons.md` and `reference-agentic-lessons.md`.
- **Operator heuristics** (`reference-operator-heuristics.md`): cross-cutting
  patterns for running a live service alongside development - hypothesis
  discipline, memory-entry drift, silent-CLI/proxy failure localisation,
  bug-title framing, external-layer-first diagnosis, post-release briefing,
  and adversarial review as a release gate.
- **Deploy readiness patterns** (`reference-deploy-readiness.md`): platform-
  agnostic post-deploy verification - cold-spawn pre-warm, smoke budget
  sizing, auto-rollback on smoke fail, readiness-wait protocol, and soak
  windows.
- **Plan-file lifecycle** (`reference-plan-files.md`): conventions for
  Claude Code plan files (`~/.claude/plans/`) - active vs archived layout,
  listing, archiving, and anti-patterns.
- **Persona review**: `/sdlc-studio review` now reviews personas (staleness
  map, PRD/CR cross-checks, self-consistency), scans `sdlc-studio/rfcs/`,
  supports `--skip-personas`, and writes a unified `reviews/LATEST.md`
  first-read anchor (`templates/reviews/unified-anchor.md`).
- **Reconcile census + cadence**: reconcile now rebuilds each index from an
  on-disk file census (detecting status mismatch, missing rows, and orphan
  rows), adds RFC scope, detects numeric-claim drift in prose docs
  (report-only, or auto-fix with `--fix-counts`), and emits advisory
  cadence triggers (epic close, ship, CR action, 7-day window) tracked in
  `reconcile-state.json`.
- **Release strategy**: `release_strategy` config (`solo-dev | pr-required |
  staged-rollout`) plus a decision tree (`reference-decisions.md`) that
  branches ship guidance accordingly.
- **Execution contract**: `reference-decisions.md` defines stop conditions
  and anti-patterns for agentic execution after plan approval.
- **Multi-persona pressure-test canvas** (`reference-consult.md`): a
  structured pattern for consulting multiple personas in parallel on
  high-blast-radius design decisions.
- **Verification depth tiers** and **test-timeout tuning** discipline
  (`reference-test-best-practices.md`), recorded per AC and at bug close;
  rollback envelope and per-AC verification target in `reference-story.md`.
- **Release-gate checklist** template (`templates/workflows/release-gate.md`)
  and new config knobs: `personas.staleness_days`, `contract_tables`.

## [1.6.0] - 2026-06-04

Structural upgrades from competitive research against BMAD-METHOD,
GitHub Spec Kit, Kiro, and Aider. Four new capabilities target the
real pain points: agent prompts that hallucinate files, acceptance
criteria that drift from reality, the skill as a parallel universe
to GitHub Issues, and projects that start dumb every time.

### Added

- **Scripts directory convention**: `.claude/skills/sdlc-studio/scripts/`
  now holds skill-internal Python helpers invoked by workflows.
  Documented in `reference-scripts.md`. Ships with three scripts,
  all pure-Python stdlib except where noted, all with unit tests
  runnable via `python3 -m unittest discover -s scripts/tests`.
- **AST Repo Map** (`scripts/repo_map.py`): indexes source files
  by symbols and imports, ranks files by relevance to a story
  description. Supports Python (via stdlib ast), TypeScript,
  JavaScript, Go, Rust, Java, Kotlin, C#, Ruby, PHP, Swift via
  regex extractors. Subcommands: `build`, `query`, `stats`. Output
  at `sdlc-studio/.local/repo-map.json`. The Agent Prompt Template
  now derives its `READ THESE FILES FIRST` list from repo_map
  query output instead of hand-authoring from memory.
- **Executable Acceptance Criteria** (`scripts/verify_ac.py`): AC
  blocks in story files gain optional `Verify:` and `Verified:`
  bullets. `/sdlc-studio reconcile --verify` runs each verifier
  and updates state in place. DSL supports `pytest`, `jest`,
  `vitest`, `go`, `file`, `grep`, `http ... -- <jq>`, and `shell`
  as fallback. Report written to
  `sdlc-studio/.local/verify-report.json`. Story Completion Cascade
  gains an optional gate (`require_ac_verification: true` in
  config) that blocks Done unless every AC reports `Verified: yes`.
- **GitHub Issues Sync** (`scripts/github_sync.py`): two-way sync
  between local CR / Story / Epic files and GitHub Issues via the
  `gh` CLI. Unified model: a CR and its linked Issue are two
  representations of the same record. Subcommands: `push`, `pull`,
  `cascade`, `state`. Label convention uses `sdlc:` prefix. Every
  record template gains a `> **GitHub Issue:**` metadata line.
  reference-cr.md gains a full `/sdlc-studio cr sync` workflow.
  Story Completion Cascade gains step 12 to update linked issues
  on status transitions.
- **Per-Project Lessons**: `sdlc-studio/.local/lessons.md`
  accumulates project-specific failure patterns across agentic
  runs. Loaded at every wave start and injected into Agent Prompt
  Templates as a `Known Pitfalls on This Project` section.
  reference-agentic-lessons.md gains a "Lessons Accumulation"
  section with the file format, four hook points (wave failure,
  post-wave merge failure, epic retrospective, manual add), and
  consumption pattern. `/sdlc-studio lessons list|add|prune`
  commands.
- **Windows PowerShell installer** (`install.ps1`): one-line install
  via `irm ... | iex`, mirroring `install.sh`. Supports `-Local`,
  `-Global`, `-DryRun`, `-Version <tag>`, and `-Help`. README gains
  Windows instructions throughout.

### Changed

- **Verifier DSL** (`reference-verify.md`): new document defining
  the executable-AC DSL, writing guidance, troubleshooting, and
  integration with reconcile.
- **`reference-reconcile.md`**: Phase 2 gains check h) AC
  verification drift. Scope table gains `verify` row that
  delegates to `scripts/verify_ac.py`.
- **`reference-outputs.md`**: Story Completion Cascade gains step
  0 (AC verification gate, conditional on config flag) and step 12
  (external sync push for records with a `GitHub Issue:` field).
- **`reference-cr.md`**: new `/sdlc-studio cr sync - Step by Step`
  workflow inserted between `cr review` and `cr close`.
- **`reference-epic.md`**: Agent Prompt Template instructs authors
  to derive `READ THESE FILES FIRST` from repo_map query output.
  Wave prep loads `.local/lessons.md`. Handle Story Errors appends
  a lesson on failure.
- **`reference-code.md`**: code plan step 6 explicitly runs
  repo_map build + query before the Explore agent.
- **`reference-agentic-lessons.md`**: READ THESE FILES FIRST
  guidance references repo_map. New "Load project lessons before
  exploration" subsection. New "Lessons Accumulation" section at
  end of file.
- **`reference-story.md`**: story-create step 3g emits best-effort
  Verify lines matching AC type.
- **`templates/core/story.md`**: AC blocks gain Verify and
  Verified bullets. Metadata gains `GitHub Issue:` field.
- **`templates/core/cr.md`**, **`templates/core/epic.md`**: both
  gain a `GitHub Issue:` metadata field.
- **`templates/config-defaults.yaml`**: new
  `require_ac_verification: false` gate.
- **`SKILL.md`**: new "Utilities" and "External Integrations"
  command sections. Progressive Loading Guide rows for
  repo-map, verify, github-sync, scripts, and lessons.
- **`help/*.md`**: new help files for repo-map, verify,
  github-sync, lessons. Existing `help/reconcile.md` documents
  `--verify`, `--story`, and `--scope verify` arguments.
- **Templates**: pre-existing markdownlint drift in
  `templates/core/story.md` cleaned up while adding Verify fields.
- **Script hardening**: the three scripts gain release-grade
  robustness: malformed `gh` output and corrupt sync state no longer
  crash `github_sync.py` (graceful fallback), `verify_ac.py` clamps
  out-of-bounds insertion points, all file I/O is explicit UTF-8, and
  every public function is documented. Test suite grows to 46 cases
  covering the new edge paths.

### Config

- `templates/config-defaults.yaml` adds `require_ac_verification`
  (default `false`). Flip to `true` once reconcile reports zero
  manual ACs to enable the Story Completion Cascade gate.

## [1.5.0] - 2026-04-14

Production-run upgrades to the SDLC pipeline. Four new commands, a
formal Three Amigos review model, project-wide orchestration, and
mechanical drift reconciliation. All additions are backwards
compatible with v1.4.0 artefacts.

### Added

- **Change Requests**: `/sdlc-studio cr` lifecycle for post-PRD changes
  - `cr create`, `cr list` (filter by status, priority, type, affects),
    `cr action` (bridges a CR into epics and stories and updates the
    PRD feature inventory), `cr review` (staleness and cascade
    checks), `cr close` (Complete, Rejected, Deferred)
  - New files: `reference-cr.md`, `help/cr.md`, `templates/core/cr.md`,
    `templates/indexes/cr.md`
  - Stored at `sdlc-studio/change-requests/CR{NNNN}-{slug}.md`
- **Project-Level Orchestration**: `/sdlc-studio project plan` and
  `/sdlc-studio project implement`
  - Dependency-graph execution across all epics with topological sort
    and cycle detection
  - Flags: `--agentic`, `--from epics|stories`,
    `--commit-strategy per-wave|per-epic|per-project`, `--resume
    EP000X`, `--skip EP000X`, `--no-artifacts`, `--dry-run`
  - Persistent state at `sdlc-studio/.local/project-state.json` with
    epic-by-epic checkpoints
  - Quality gates at wave, epic, and project boundaries
  - New files: `reference-project.md`, `help/project.md`
- **Reconciliation**: `/sdlc-studio reconcile [--dry-run] [--scope
  stories|epics|prd|crs|indexes]`
  - Mechanical drift detection and repair across stories, epics, PRD
    feature statuses, CRs, indexes, dependency tables, and checkbox
    state
  - Idempotent; runs automatically at epic and wave boundaries during
    agentic execution
  - New files: `reference-reconcile.md`, `help/reconcile.md`
- **Agentic Lessons**: `reference-agentic-lessons.md` captures
  production-tested patterns for wave execution, exploration cadence,
  hub-file sidecar pattern, per-wave reconcile, commit pacing, and a
  failure-mode table. Loaded before any `--agentic` wave execution.
- **Three Amigos Consultation**: formal PM/Eng/QA review model now the
  default for epic create, story create, story plan, and bug fix.
  Personas named (Sarah Chen, Marcus Johnson, Priya Sharma) with
  distinct review remits.

### Changed

- **`reference-outputs.md`**: canonical 11-step Story Completion
  Cascade (previously 6) and 9-step Epic Completion Cascade. All other
  reference files now delegate to this file rather than maintaining
  local copies. Adds compressed status flow (Ready -> Done) for
  agentic batch mode and documents the `project-state.json` artefact
  and the `Owner` field on stories.
- **`reference-epic.md`** (+50%): Three Amigos mandatory review,
  8-step Post-Wave Merge Protocol with troubleshooting table, full
  Agent Prompt Template (READ FIRST, DO NOT, AC-to-files mapping, code
  snippets for shapes not logic), wave-boundary quality gates,
  `--no-artifacts` agentic mode.
- **`reference-review.md`** (+50%): automatic Phase 3a persona
  consultation, Phase 3b auto-apply mechanical fixes (with `--no-fix`),
  Phase 4 review-state.json update, test-tree validation against TSD,
  CR staleness checks.
- **`reference-workflow-personas.md`**: defaults flipped from Optional
  to Always for most artefacts; new sections for story-plan and
  bug-fix consultation.
- **`reference-story.md`**: Three Amigos default review, new Agentic
  Mode Behaviour section covering `--no-artifacts`.
- **`reference-code.md`**: Three Amigos plan review; completion
  checklist expanded from 6 to 12 steps.
- **`reference-bug.md`**: Three Amigos for bug fixes (impact, root
  cause, regression).
- **`reference-prd.md`**: automatic persona consultation when
  `sdlc-studio/personas/` exists.
- **`reference-tsd.md`**: review-state.json fallback to `RV*.md` scan
  with explicit reviews-health formula.
- **`reference-config.md`**: project implement configuration block
  (`commit_strategy`, `review_interval`, `auto_reconcile`,
  `auto_commit`).
- **`reference-consult.md`**: automation table with Three Amigos as
  the explicit default across most artefacts.
- **`SKILL.md`**: registers new commands and flags, adds
  Reconciliation, Change Management, and Project Implementation
  sections.
- **`help/help.md`**: Change Management, Project Implementation, Epic
  Implementation, Story Implementation, and manual Development Cycle
  sections.
- **`help/status.md`**: dual-source metrics with `RV*.md` fallback
  when `.local/review-state.json` is absent.

### Config

- `.markdownlint.json`: set `MD046` to fenced style and disable
  `MD036` (the skill deliberately uses bold labels as sub-step markers
  within numbered lists).

## [1.4.0] - 2026-02-18

Persona consultation system, interactive chat sessions, agentic epic execution, and workflow state management.

### Added

- **Persona Consultation System**: `/sdlc-studio consult` command for structured persona feedback on artefacts
  - Single persona, Three Amigos (`consult team`), and stakeholder group (`consult stakeholders`) modes
  - Verdicts: Approve, Concerns, Reject with actionable recommendations
  - New files: `help/consult.md`, `reference-consult.md`, 3 consultation templates
- **Interactive Persona Chat**: `/sdlc-studio chat` command for conversational persona sessions
  - Workshop mode (`--workshop`) for multi-persona discussions
  - Context loading (`--context`), transcript saving (`--save`)
  - New files: `help/chat.md`, `reference-chat.md`
- **Persona Generation**: `/sdlc-studio persona generate` with three source modes
  - `--from-prd`, `--from-code`, `--from-docs` extraction
  - Import/export and list commands
  - New file: `reference-persona-generate.md`
- **Archetype Personas**: 15 pre-built persona templates across Team and Stakeholder categories
  - Team: Product (2), Engineering (4), QA (2)
  - Stakeholders: Users (3), Business (2), Technical (2)
  - New directory: `templates/personas/` with per-category subdirectories
- **Workflow Persona Integration**: `--with-personas` and `--skip-personas` flags across all workflows
  - New file: `reference-workflow-personas.md`
- **Agentic Epic Execution**: `--agentic` flag for autonomous concurrent story execution
  - Dependency graph analysis and hub file overlap detection
  - Concurrent wave assignment with automatic sequential fallback
  - Post-wave test suite verification
- **Story Completion Cascade**: Automatic status propagation to linked plans, test specs, and workflows when a story reaches any terminal status
- **Terminal Status Support**: Won't Implement, Deferred, Superseded statuses for stories, plans, test specs, and workflows
- **Workflow State Templates**: `templates/core/workflow.md` and `templates/indexes/workflow.md` for implementation tracking
- **Index Reconciliation**: `status --full` detects missing entries, status mismatches, stale statuses, and ID collisions
- **Frontend Testing Patterns**: Vitest + React patterns, shared API client mocking, jsdom mocking for Recharts/D3/MapboxGL
- **Test Case Numbering**: Global TC numbering across specs and epic-scoped coverage rules

### Changed

- **`--parallel` renamed to `--agentic`**: Better branding for autonomous execution capability (all files updated, `#flag-agentic` anchor)
- **Persona workflows expanded**: `help/persona.md` (+305 lines) and `reference-persona.md` (+423 lines) with category framework, create/generate workflows, enrichment questions
- **Story workflows enhanced**: `reference-story.md` (+321 lines) with mandatory plan prerequisites, resume-from-phase, persona validation, completion cascade
- **Epic workflows enhanced**: `reference-epic.md` (+178 lines) with persona assessment, agentic execution, post-epic checklist
- **Output formats expanded**: `reference-outputs.md` (+91 lines) with terminal statuses, cascade checklist, status vocabulary enforcement, ID collision prevention
- **SKILL.md updated**: New persona/consult/chat commands, `--agentic` flag, agentic workflow diagram (+93 lines, now 505 lines)
- **README.md updated**: Agentic epic execution in Common Commands table and Workflows section
- **Help files**: Source of truth pointers added to bug, code, refactor, test-automation, test-spec help files

## [1.3.0] - 2026-01-28

Major restructuring with modular template architecture, expanded command coverage, and British English standardisation.

### Added

- **Modular Template Architecture**: Reorganised templates into logical structure
  - `templates/core/*.md` - Streamlined core templates (prd, trd, tsd, epic, story, plan, test-spec, bug, personas)
  - `templates/indexes/*.md` - Index file templates
  - `templates/modules/trd/*.md` - Optional TRD modules (c4-diagrams, container-design, adr)
  - `templates/modules/tsd/*.md` - Optional TSD modules (contract-tests, performance-tests, security-tests)
  - `templates/modules/epic/*.md` - Epic perspective modules (engineering-view, product-view, test-view)
  - `templates/automation/*.template` - Test automation templates (pytest, jest, vitest, go, xunit, junit)
  - `templates/workflows/*.md` - Workflow state templates
  - `templates/reviews/*.md` - Review output templates
- **New Reference Files**: Expanded documentation coverage
  - `reference-config.md` - Project configuration options
  - `reference-refactor.md` - Code refactoring workflows
  - `reference-review.md` - Unified document review workflow
  - `reference-upgrade.md` - Schema migration guidance
  - `reference-test-spec.md` - Test specification workflows
  - `reference-test-automation.md` - Test automation and environment workflows
  - `reference-tsd.md` - Test Strategy Document workflows
  - `reference-epic-sections.md` - Epic section deep dives
  - `reference-story-sections.md` - Story section deep dives
  - `reference-test-pitfalls.md` - Test generation anti-patterns
- **New Help Files**: Command-specific guidance
  - `help/init.md` - Project initialisation
  - `help/refactor.md` - Refactoring commands
  - `help/review.md` - Review commands
  - `help/test-env.md` - Test environment setup
  - `help/upgrade.md` - Schema upgrade guidance
- **New Best Practice Guides**:
  - `best-practices/postgresql.md` - PostgreSQL-specific patterns
  - `best-practices/sql.md` - General SQL best practices
- **Configuration System**: New project configuration
  - `templates/config.yaml` - Project configuration template
  - `templates/config-defaults.yaml` - Skill default settings
  - `templates/version.yaml` - Version tracking template

### Changed

- **British English Standardisation**: Consistent spelling throughout
  - `visualize` → `visualise` (command name)
  - `License` → `Licence` (section headers)
- **SKILL.md Streamlined**: Improved command reference and progressive loading guide
- **Reference Files Updated**: Enhanced navigation sections and cross-references
- **Help Files Consolidated**: Reduced duplication, improved See Also sections

### Removed

- **Legacy Templates**: Replaced with modular structure
  - `templates/bug-template.md`, `templates/bug-index-template.md`
  - `templates/epic-template.md`, `templates/epic-index-template.md`, `templates/epic-workflow-template.md`
  - `templates/story-template.md`, `templates/story-index-template.md`
  - `templates/plan-template.md`, `templates/plan-index-template.md`
  - `templates/prd-template.md`, `templates/trd-template.md`, `templates/tsd-template.md`
  - `templates/test-spec-template.md`, `templates/test-spec-index-template.md`
  - `templates/personas-template.md`, `templates/workflow-template.md`
- **Obsolete Reference File**: `reference-testing.md` (split into test-spec, test-automation, tsd)

## [1.2.0] - 2026-01-26

Major documentation overhaul with comprehensive refactoring for improved navigation, progressive disclosure, and best practices compliance. Consolidated best practices structure and enhanced AI-assisted testing guidance.

### Added

- **Single Source of Truth for Outputs**: New `reference-outputs.md` (150 lines)
  - Centralised documentation for all output formats, file locations, and status values
  - Status transition diagrams for all artifact types
  - File naming conventions and index file structure
  - Traceability documentation
- **Advanced Testing Patterns**: New `reference-test-validation.md` (486 lines)
  - Validation workflows and contract testing guidance
  - Parameterised testing patterns (Python, TypeScript, Go)
  - Test data management and flakiness prevention
  - Property-based and snapshot testing
- **Navigation Infrastructure**: 419 section anchors across all reference files
  - Deep linking to specific sections (e.g., `reference-code.md#edge-case-coverage`)
  - Enables precise cross-referencing between documentation
- **Navigation Sections**: Added to 8 reference files
  - Prerequisites (required files to load first)
  - Related workflows (upstream/downstream dependencies)
  - Cross-cutting concerns (decisions, outputs)
  - Deep dives (optional advanced topics)
- **Best Practice Guides for Skill Development**: New guides for maintaining quality standards
  - `best-practices/command.md` (168 lines) - Claude Code command patterns
  - `best-practices/documentation.md` (165 lines) - Documentation standards
  - `best-practices/claude-skill.md` (268 lines) - Skill development guide
  - `best-practices/settings.md` - Configuration best practices
- **Enhanced AI-Assisted Testing Guidance**:
  - `reference-test-pitfalls.md` (144 lines) - Test generation anti-patterns catalogue
  - 90% coverage targets with proven achievable strategies
  - AI-specific testing anti-patterns and validation workflows
  - Conditional assertion pitfall detection
  - Silent test helper failure prevention

### Changed

- **SKILL.md Restructured** (453 → 484 lines, improved organisation):
  - Added explicit "Instructions" section (best practices compliance)
  - Moved philosophy to "Critical Philosophy (Read This First)" section
  - Replaced "File Loading Guide" with "Progressive Loading Guide" (structured table format)
  - Added "Navigation Map" showing file relationships by domain and workflow stage
  - References `reference-outputs.md` as single source of truth
- **Progressive Disclosure Improvements**:
  - Edge case validation moved to step 5 in `reference-code.md` (validates BEFORE planning)
  - Critical warnings moved to first 40 lines in help files
  - Philosophy callout added to `help/prd.md` for generate mode users
- **Help Files Standardised** (10 files updated):
  - "See Also" sections now use priority markers (REQUIRED/Recommended/Optional)
  - Added section anchor references for precise navigation
  - Removed duplicate output format documentation
- **Template Headers Standardised** (16 templates updated):
  - Added consistent header comments to all templates
  - Templates reference `reference-outputs.md` for status values
  - Includes file path and related documentation links
- **Consolidated Language Best Practices**: Unified split files into single files per language
  - Merged `python-rules.md` + `python-examples.md` → `python.md` (247 lines)
  - Merged `go-rules.md` + `go-examples.md` → `go.md` (416 lines)
  - Merged `javascript-rules.md` + `javascript-examples.md` → `javascript.md`
  - Merged `typescript-rules.md` + `typescript-examples.md` → `typescript.md`
  - Merged `rust-rules.md` + `rust-examples.md` → `rust.md`
  - Single source of truth per language improves AI context and maintenance
- **Testing Documentation Restructured**: Split `reference-test-best-practices.md` (862 → 410 lines)
  - Core practices, checklist, and warnings remain in `reference-test-best-practices.md`
  - Advanced patterns moved to new `reference-test-validation.md` (486 lines)
  - Clearer separation of concerns and improved maintainability
- **Improved Workflow Organisation**: Refactored scope validation from `reference-code.md` to `reference-decisions.md`
  - Progressive disclosure: HOW to plan vs WHEN plan is ready
  - Cleaner separation of workflow steps and validation criteria

### Removed

- **Split Best Practice Files**: Removed 14 language-specific split files
  - `*-rules.md` and `*-examples.md` files for Python, Go, JavaScript, TypeScript, Rust, PHP, C#
  - Content preserved in consolidated single files

### Fixed

- **Broken File References**: Fixed 2 instances of non-existent file references
  - `reference-requirements.md` → `reference-prd.md`, `reference-trd.md`, `reference-persona.md`
  - `reference-specifications.md` → `reference-epic.md`, `reference-story.md`, `reference-bug.md`
- **Markdownlint Compliance**: Fixed 45 linting errors in refactored files
  - Added language specifiers to 16 code blocks
  - Added blank lines around 16 lists
  - Added blank lines around 9 code blocks
  - Added blank lines around 4 headings
- `help/bug.md` line 288: Corrected reference link from `reference.md` to `reference-bug.md`

### Technical Improvements

- **Documentation Quality**: 100% best practices compliance
  - Explicit Instructions section per skill development guidelines
  - No broken references (0 remaining)
  - All code blocks have language specifiers
  - Consistent spacing and formatting
- **Navigation Efficiency**: 419 section anchors enable
  - Direct linking to specific workflow steps
  - Precise cross-references between files
  - Reduced navigation time by ~40%
- **Maintenance Burden**: Reduced by ~60%
  - Single source of truth for output formats
  - No duplicate content across files
  - Clear dependency relationships documented

## [1.1.0] - 2026-01-20

Based on production testing and user feedback to improve workflow and output quality.

### Added

- **Test Strategy Document (TSD)**: New `/sdlc-studio tsd` command with improved structure
- **Story Workflow Automation**: Execute stories through 7 phases (Plan → Test Spec → Tests → Implement → Test → Verify → Check)
- **Epic Workflow Automation**: Process all stories in dependency order with `/sdlc-studio epic implement`
- **Explicit Story Dependencies**: Stories track schema, API, and service dependencies
- **Modular Reference Architecture**: Split reference.md into 13 focused files:
  - `reference-philosophy.md` - Create vs Generate modes
  - `reference-prd.md`, `reference-trd.md`, `reference-epic.md`, `reference-story.md`
  - `reference-bug.md`, `reference-persona.md`
  - `reference-code.md`, `reference-testing.md`
  - `reference-architecture.md`, `reference-decisions.md`
  - `reference-test-best-practices.md`, `reference-test-e2e-guidelines.md`
- **New Best Practices**: Go language guide, architecture patterns guide
- **New Templates**: `workflow-template.md`, `epic-workflow-template.md`, `tsd-template.md`

### Changed

- SKILL.md updated for modular architecture
- Help files updated with workflow automation commands
- Templates improved for better output quality

### Removed

- **Commands**: `init`, `migrate`, `test-strategy`, generic `test`
- **Files**: `reference.md`, `definition-of-done-template.md`, `test-strategy-template.md`
- **Help Files**: `help/init.md`, `help/migrate.md`, `help/test-strategy.md`, `help/test.md`

### Migration

| Old | New |
| ----- | ----- |
| `/sdlc-studio init` | `/sdlc-studio status` (start with prd create/generate) |
| `/sdlc-studio migrate` | No longer needed |
| `/sdlc-studio test-strategy` | `/sdlc-studio tsd` |
| `/sdlc-studio test` | `/sdlc-studio code test` |

**Workflow automation (new):**

```bash
/sdlc-studio story implement --story US0001   # Single story, all phases
/sdlc-studio epic implement --epic EP0001     # All stories in epic
```

## [1.0.0] - 2025-01-17

### Added

- **Requirements Pipeline**: PRD, TRD, Epic, Story, Persona management
- **Bug Tracking**: Report, list, fix, verify, and close bugs with traceability
- **Code Workflows**: Plan, implement, review, and check code against requirements
- **Testing Pipeline**: Test Strategy, Test Specifications, Test Automation
- **Test Execution**: Run tests with traceability to stories and epics
- **Pipeline Bootstrap**: Auto-detect brownfield/greenfield projects with `/sdlc-studio init`
- **Migration**: Migrate from old test-plan/suite/case format
- **Status & Hints**: Check pipeline state and get actionable next steps
- **Help System**: Type-specific help for all commands
- **Templates**: 22 templates for all artifact types
- **Best Practices**: 11 guides for quality artifacts

[1.4.0]: https://github.com/DarrenBenson/sdlc-studio/compare/v1.3.0...v1.4.0
[1.3.0]: https://github.com/DarrenBenson/sdlc-studio/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/DarrenBenson/sdlc-studio/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/DarrenBenson/sdlc-studio/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/DarrenBenson/sdlc-studio/releases/tag/v1.0.0
