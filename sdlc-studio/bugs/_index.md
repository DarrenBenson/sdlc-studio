# Bug Index

**Last Updated:** 2026-10-18

## Summary

| Status | Count |
| --- | --- |
| Open | 99 |
| In Progress | 0 |
| Fixed | 804 |
| Verified | 0 |
| Closed | 87 |
| Won't Fix | 40 |
| Superseded | 32 |
| **Total** | **1062** |

## All Bugs

| ID | Title | Status | Severity | Created | Updated |
| --- | --- | --- | --- | --- | --- |
| [BG0944](BG0944-three-behaviours-bg0940-and-bg0943-shipped-have-no.md) | Three behaviours BG0940 and BG0943 shipped have no test that fails when they break | Fixed | Low | 2026-10-05 | 2026-10-05 |
| [BG0945](BG0945-bg0940-s-changelog-entry-says-a-page-with.md) | BG0940's changelog entry says a page with a late ruling is signed, though sign refuses until the run is re-closed | Fixed | Low | 2026-10-05 | 2026-10-05 |
| [BG0946](BG0946-reports-index-md-last-updated-is-not-restamped.md) | reports/_index.md Last Updated is not restamped when a report is filed | Open | Low | 2026-10-05 | 2026-10-05 |
| [BG0947](BG0947-reference-outputs-md-terminal-status-table-contradicts-sdlc.md) | reference-outputs.md terminal-status table contradicts sdlc_md.TERMINAL_STATUS | Open | Medium | 2026-10-05 | 2026-10-05 |
| [BG0948](BG0948-a-migrating-project-cannot-baseline-pre-existing-placeholder.md) | A migrating project cannot baseline pre-existing placeholder findings, and v3 ids can never be baselined | Open | Medium | 2026-10-05 | 2026-10-05 |
| [BG0949](BG0949-an-inline-ruled-or-decided-ruling-is-never.md) | An inline `ruled:` or `decided:` ruling is never recognised - `_RULING_RE` puts a word boundary after the colon | Open | Medium | 2026-10-06 | 2026-10-06 |
| [BG0950](BG0950-a-verdict-that-follows-critic-py-brief-s.md) | A verdict that follows `critic.py brief`'s return contract to the letter is refused by `critic.py record --from-verdict` | Fixed | Medium | 2026-10-06 | 2026-10-06 |
| [BG0951](BG0951-critic-tier-for-reads-the-raw-difficulty-band.md) | `critic.tier_for` reads the raw difficulty band and skips every critic-role policy `route.pick` applies, so code units get a light review the routing policy says should be medium | Won't Fix | High | 2026-10-06 | 2026-10-06 |
| [BG0952](BG0952-an-open-questions-item-declaring-none-after-a.md) | An Open Questions item declaring None after a dash is read as unanswered - `_DECLARES_NONE_RE` does not allow a leading dash | Open | Low | 2026-10-06 | 2026-10-06 |
| [BG0953](BG0953-full-template-story-and-tsd-ship-unrendered-config.md) | Full-template story and TSD ship unrendered {{config.story_quality.*}} placeholders | Open | Low | 2026-10-06 | 2026-10-06 |
| [BG0954](BG0954-a-draft-story-transitions-straight-to-done-the.md) | A Draft story transitions straight to Done - the Definition of Ready is never required | Open | Medium | 2026-10-06 | 2026-10-06 |
| [BG0955](BG0955-test-lean-backlog-sweep-reads-only-the-live.md) | `test_lean_backlog_sweep` reads only the live `_index.md`, so the v6.1 row archive turned main red with 25 false disagreements | Fixed | Medium | 2026-10-06 | 2026-10-06 |
| [BG0956](BG0956-transition-set-reports-index-synced-but-leaves-archived.md) | transition set reports index synced but leaves archived index rows stale, and reconcile apply refuses them | Open | Medium | 2026-10-06 | 2026-10-06 |
| [BG0957](BG0957-test-epic-index-derived-s-negative-control-needs.md) | `test_epic_index_derived`'s negative control needs a live epic row with a count, so an archive that empties the live epic index turns it red | Open | Medium | 2026-10-06 | 2026-10-06 |
| [BG0958](BG0958-mutation-py-finds-no-changed-lines-when-git.md) | `mutation.py` finds no changed lines when git's `diff.mnemonicPrefix` is set, so a mutation probe scoped to a unit's changes has nothing to mutate | Open | Medium | 2026-10-06 | 2026-10-06 |
| [BG0959](BG0959-the-engagement-floor-rejects-a-ulid-adopt-after.md) | The engagement floor rejects a ULID adopt_after cutoff and tells you to set a sequential one | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0960](BG0960-a-plan-refused-for-a-missing-verify-line.md) | A plan refused for a missing Verify line tells you to add Affects and Points | Open | Low | 2026-10-07 | 2026-10-07 |
| [BG0961](BG0961-a-verify-line-cannot-name-the-skill-skill.md) | A Verify line cannot name the skill: <skill> is a shell redirect, not a path | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0962](BG0962-closing-review-reads-a-unit-s-latest-verdict.md) | closing-review reads a unit's latest verdict only from the frozen sprint-review ledger, so a frozen batch REJECT outlives a later per-unit APPROVE and blocks the close as a hard correctness gate | Open | High | 2026-10-07 | 2026-10-07 |
| [BG0963](BG0963-wall-clock-assertions-in-the-parallel-suite-fail.md) | Wall-clock assertions in the parallel suite fail under load, so a busy machine refuses commits and pushes on timing alone | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0964](BG0964-help-refine-md-never-mentions-into-so-a.md) | help/refine.md never mentions `--into`, so a story added to an already-refined epic is made with `artifact.py new` and carries no Delivers link | Open | Low | 2026-10-07 | 2026-10-07 |
| [BG0965](BG0965-retro-py-validate-ignores-actions-raised-in-a.md) | retro.py validate ignores '## Actions raised' in a Keep/Stop/Try retro, so it reports '0 findings, all dispositioned' over rows it never read | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0966](BG0966-review-prep-persona-usage-calls-a-persona-unused.md) | review_prep persona_usage calls a persona unused unless its file's H1 appears verbatim in prd.md - stories, CRs and consult logs are never read | Open | Low | 2026-10-07 | 2026-10-07 |
| [BG0967](BG0967-the-finding-filer-backtick-wraps-identifiers-inside-steps.md) | The finding filer backtick-wraps identifiers inside Steps to Reproduce, corrupting the shell commands a repro depends on | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0968](BG0968-ci-runs-tools-tests-in-the-same-step.md) | CI runs tools/tests in the same step as the skill suite, so a red skill suite hides every tools/tests failure | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0969](BG0969-sprint-close-file-and-close-silently-drops-a.md) | sprint close --file-and-close silently drops a supplied --goal-verdict, then refuses because the goal is unjudged - a hard blocker it cannot file | Open | Low | 2026-10-07 | 2026-10-07 |
| [BG0970](BG0970-critic-py-brief-says-nothing-when-the-unit.md) | `critic.py brief` says nothing when the unit's Affects carry uncommitted changes, though it sends the reviewer to an isolated worktree that cannot see them | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0971](BG0971-sprint-close-dry-run-reports-later-chain-steps.md) | sprint close --dry-run reports later chain steps in the past tense ('lessons lifted', 'summary regenerated', 'anchor refreshed') although nothing was written | Open | Low | 2026-10-07 | 2026-10-07 |
| [BG0972](BG0972-artifact-py-retitle-quotes-the-old-title-verbatim.md) | `artifact.py retitle` quotes the old title verbatim in its revision row, so a retitle made to remove an em dash or a bare identifier puts it straight back | Open | Low | 2026-10-07 | 2026-10-07 |
| [BG0973](BG0973-artifact-py-new-type-review-warns-its-acceptance.md) | artifact.py new --type review warns 'its acceptance criteria are still the scaffold placeholder' although the review scaffold has no Acceptance Criteria section | Open | Low | 2026-10-07 | 2026-10-07 |
| [BG0974](BG0974-the-filing-tools-do-not-markdown-safe-the.md) | The filing tools do not markdown-safe the title or the Evidence line, so a bare snake_case identifier fails MD037 at commit or in CI | Open | Low | 2026-10-07 | 2026-10-07 |
| [BG0975](BG0975-critic-py-brief-rejoinder-derives-a-light-tier.md) | critic.py brief --rejoinder derives a light tier from the risk band even when the round it answers was taken at an explicit full tier | Open | Low | 2026-10-07 | 2026-10-07 |
| [BG0976](BG0976-the-pre-push-hook-prints-its-ssh-keepalive.md) | The pre-push hook prints its ssh keepalive warning on every push, even when the clone already carries a keepalive | Fixed | Low | 2026-10-07 | 2026-10-07 |
| [BG0977](BG0977-help-status-md-documents-sdlc-studio-status-brief.md) | help/status.md documents '/sdlc-studio status --brief' but status.py has no --brief, so the documented one-line summary errors | Open | Low | 2026-10-07 | 2026-10-07 |
| [BG0978](BG0978-test-pre-push-hook-s-stub-path-symlinks.md) | `test_pre_push_hook`'s stub PATH symlinks python3, which drops a virtualenv's packages, so the push gate cannot pass where pytest lives in a venv | Fixed | Low | 2026-10-07 | 2026-10-07 |
| [BG0979](BG0979-file-finding-py-misdirects-a-cr-s-author.md) | `file_finding.py` misdirects a CR's author: `--recommendation` is documented as RFC-only though a CR carries it, and the no-verifier warning cites a `sprint plan` refusal that never applies to a CR | Open | Low | 2026-10-07 | 2026-10-07 |
| [BG0980](BG0980-filing-refuses-a-verify-selector-for-a-test.md) | Filing refuses a Verify selector for a test the fix will add to an existing module, accepts the same selector into a new file, and judges neither without pytest | Open | Low | 2026-10-07 | 2026-10-07 |
| [BG0981](BG0981-breakdown-and-plan-call-a-unit-groomed-when.md) | breakdown and plan call a unit groomed when a Verify line is one verify_ac cannot parse | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0982](BG0982-critic-brief-s-diff-scope-is-the-unit.md) | critic brief's diff scope is the unit's Affects only - files the unit changed but did not declare are invisible to the reviewer | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0983](BG0983-review-coverage-and-verdict-for-read-a-unit.md) | `review_coverage` and `verdict_for` read a unit's whole per-unit ledger, so an APPROVE from an earlier delivery covers a re-delivered unit that nobody reviewed in this run | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0984](BG0984-changing-a-criterion-s-verify-expression-keeps-the.md) | Changing a criterion's Verify expression keeps the old Verified date and evidence when the new one passes | Open | Low | 2026-10-07 | 2026-10-07 |
| [BG0985](BG0985-sprint-close-dry-run-reports-a-non-blocking.md) | sprint close --dry-run reports a non-blocking pre-flight row as a STOP refusal and exits 1, so a close that would proceed previews as refused | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0986](BG0986-tools-forward-port-sh-deletes-the-changelog-md.md) | `tools/forward-port.sh` deletes the CHANGELOG.md the installer ships into the skill, so `project upgrade` loses its changelog digest after every forward-port | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0987](BG0987-the-close-s-goal-judgement-reaches-only-the.md) | The close's goal judgement reaches only the terminal, not the sprint report the signer is told to read, and says 'blocks the close' of defects that did not block it | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0988](BG0988-sprint-plan-s-one-run-slot-refusal-tells.md) | sprint plan's one-run-slot refusal tells the operator to finish a close that already finished, when only the signature is owed | Open | Low | 2026-10-07 | 2026-10-07 |
| [BG0989](BG0989-a-sprint-close-on-a-second-machine-wipes.md) | A sprint close on a second machine wipes the committed LESSONS-SUMMARY.md: the project lessons log it regenerates from is gitignored, so it exists only on the machine that wrote it | Fixed | High | 2026-10-07 | 2026-10-07 |
| [BG0990](BG0990-reconcile-s-field-sync-reads-a-joined-metadata.md) | reconcile's field sync reads a '·'-joined metadata run to end of line, writing 'P2 · **Type:** ...' into index cells and dropping the later fields | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0991](BG0991-verify-ac-attaches-a-verify-line-from-a.md) | verify_ac attaches a **Verify:** line from a LATER section (history, update notes) to the last criterion and executes it, because a criterion block never closes at a ## heading | Open | Medium | 2026-10-07 | 2026-10-07 |
| [BG0992](BG0992-bg0989-s-approved-repair-leaves-three-branches-unpinned.md) | BG0989's approved repair leaves three branches unpinned, and its docs over-claim which commands move the legacy lessons log | Open | Low | 2026-10-08 | 2026-10-08 |
| [BG0993](BG0993-the-open-sprint-run-lives-in-one-machine.md) | The open sprint run lives in one machine's gitignored .local/run-state.json: another checkout can open a second run beside it, and cannot sign it | Fixed | High | 2026-10-08 | 2026-10-08 |
| [BG0994](BG0994-bg0989-left-test-lessons-py-s-fixtures-on.md) | BG0989 left test_lessons.py's fixtures on the legacy lessons path, so seven tests print the migration line and CI's noise gate is red on main | Fixed | High | 2026-10-08 | 2026-10-08 |
| [BG0995](BG0995-refine-leaves-the-bold-acn-label-in-seeded.md) | refine leaves the bold **ACn** label in seeded AC headings, so a request written by the skill's own filer seeds '### AC1: **AC1** ...' (BG0291 incomplete) | Open | Medium | 2026-10-08 | 2026-10-08 |
| [BG0996](BG0996-the-finding-filer-s-identifier-wrapper-pulls-trailing.md) | The finding filer's identifier wrapper pulls trailing punctuation into the code span: (`API_KEY_2`, `TOKEN_V2)` and `keep_alive.` | Open | Low | 2026-10-08 | 2026-10-08 |
| [BG0997](BG0997-a-per-unit-engagement-floor-waiver-pasted-with.md) | A per-unit engagement-floor waiver pasted with the dashed v3 id does not waive the unit | Open | Medium | 2026-10-08 | 2026-10-08 |
| [BG0998](BG0998-the-story-template-ships-verified-no-which-verify.md) | The story template ships Verified no, which verify_ac treats as an authored miss | Open | Medium | 2026-10-08 | 2026-10-08 |
| [BG0999](BG0999-caller-check-cannot-resolve-a-skill-script-named.md) | Caller-check cannot resolve a skill script named as the consumer | Open | Medium | 2026-10-08 | 2026-10-08 |
| [BG1000](BG1000-the-commit-s-test-selection-does-not-recognise.md) | The commit's test selection does not recognise loader.load_script, so 71 of 77 loader edges are never selected and a commit touching sprint.py skips 22 modules that drive it | Open | High | 2026-10-08 | 2026-10-08 |
| [BG1001](BG1001-a-clone-that-never-held-a-run-awaiting.md) | A clone that never held a run awaiting its signature can end it only by signing it: stop there says there is nothing to stop | Open | Low | 2026-10-08 | 2026-10-08 |
| [BG1002](BG1002-goal-review-brief-ignores-the-plan-s-serves.md) | goal-review brief ignores the plan's --serves and the batch changes made after plan --write | Open | Medium | 2026-10-08 | 2026-10-08 |
| [BG1003](BG1003-critic-record-refuses-a-review-round-the-operator.md) | critic record refuses a review round the operator authorised past the cap, so the ledger's last word on the unit is a superseded REJECT | Fixed | Medium | 2026-10-08 | 2026-10-08 |
| [BG1004](BG1004-bg0993-s-tracked-run-record-tells-a-newer.md) | BG0993's tracked run record tells a newer copy by reopen count alone, so two reopens made at once overwrite each other; and the close preview's no-write guard is unpinned | Open | Low | 2026-10-09 | 2026-10-09 |
| [BG1005](BG1005-a-pytest-verify-that-partly-skips-is-stamped.md) | A pytest Verify that PARTLY skips is stamped green - BG0317 closed only the all-skipped case | Open | Medium | 2026-10-09 | 2026-10-09 |
| [BG1006](BG1006-sprint-batch-add-prints-a-refusal-for-an.md) | sprint batch add prints a refusal for an unresolvable Affects path but adds the unit anyway | Open | Low | 2026-10-09 | 2026-10-09 |
| [BG1007](BG1007-a-signed-report-s-figure-sources-are-outside.md) | A signed report's figure sources are outside its fingerprint, so every source can be rewritten and the page still checks VALID | Open | Low | 2026-10-09 | 2026-10-09 |
| [BG1008](BG1008-a-waiver-recorded-before-the-run-can-answer.md) | A waiver recorded before the run can answer a checklist row while the page's Waivers in force section says no gate stood down | Open | Low | 2026-10-09 | 2026-10-09 |
| [BG1009](BG1009-revert-check-reads-a-timed-out-verifier-as.md) | revert-check reads a timed-out verifier as red and an empty revert as green, so it passes a unit it never measured and refuses one it never reverted | Open | Medium | 2026-10-09 | 2026-10-09 |
| [BG1010](BG1010-sprint-report-py-build-run-resolves-the-named.md) | sprint_report.py build --run resolves the named run and then builds the page from the default run | Open | Low | 2026-10-09 | 2026-10-09 |
| [BG1011](BG1011-ll0056-ships-with-its-label-doubled-and-the.md) | LL0056 ships with its label doubled and the template's placeholder sections left in, and nothing refuses a lesson with an unfilled placeholder | Open | Low | 2026-10-09 | 2026-10-09 |
| [BG1012](BG1012-the-sprint-checklist-reads-a-run-only-from.md) | The sprint checklist reads a run only from .local, so in any other clone a signed run's rows read 'no run record could be read' | Open | Medium | 2026-10-09 | 2026-10-09 |
| [BG1013](BG1013-the-waiver-remedy-the-close-and-the-checklist.md) | The waiver remedy the close and the checklist print omits --authorised-by, so the command as printed is refused | Open | Low | 2026-10-09 | 2026-10-09 |
| [BG1014](BG1014-revert-check-rewrites-production-files-in-place-without.md) | revert-check rewrites production files in place without declaring a rewrite window, so a commit made while it runs can stage a reverted file | Open | Low | 2026-10-09 | 2026-10-09 |
| [BG1015](BG1015-persona-resolve-py-resolve-refuses-a-seat-role.md) | persona_resolve.py resolve refuses a seat role the project declares (sre), though validate seats and critic.py brief accept it | Open | Medium | 2026-10-09 | 2026-10-09 |
| [BG1016](BG1016-lessons-add-global-defaults-a-promoted-lesson-s.md) | lessons add --global defaults a promoted lesson's origin to the working directory's name, so a consuming project's directory name is written into a shipped lesson | Open | Low | 2026-10-09 | 2026-10-09 |
| [BG1017](BG1017-validate-warns-pseudo-verify-on-the-verify-line.md) | validate warns pseudo-verify on the Verify line a request's own writers put beneath each criterion | Open | Low | 2026-10-09 | 2026-10-09 |
| [BG1018](BG1018-refine-apply-question-leaves-the-request-ending-on.md) | refine apply --question leaves the request ending on a blank line, which markdownlint refuses (MD012) | Open | Low | 2026-10-09 | 2026-10-09 |
| [BG1019](BG1019-artifact-py-retitle-refuses-in-every-consuming-project.md) | artifact.py retitle refuses in every consuming project: it loads tools/check_links.py from the operated repo or the skill's own source checkout, and an installed skill has neither | Open | Medium | 2026-10-09 | 2026-10-09 |
| [BG1020](BG1020-transition-py-refuses-an-rfc-s-accepted-until.md) | transition.py refuses an RFC's Accepted until its spawned CRs are resolved, contradicting reference-rfc.md's accept step | Open | Low | 2026-10-09 | 2026-10-09 |
| [BG1021](BG1021-a-cr-declared-size-l-is-not-flagged.md) | A CR declared Size L is not flagged for decomposition | Open | Medium | 2026-10-09 | 2026-10-09 |
| [BG1022](BG1022-a-stale-tsd-still-says-the-batch-does.md) | A stale TSD still says the batch does not deliver Unit Testing | Open | Medium | 2026-10-09 | 2026-10-09 |
| [BG1023](BG1023-verify-ac-s-vitest-and-jest-verbs-fold.md) | verify_ac's vitest and jest verbs fold the whole tail into the -t pattern and call a bare binary, so `vitest <file> -t "name"` can never select its test | Open | Medium | 2026-10-11 | 2026-10-11 |
| [BG1024](BG1024-verify-ac-s-grep-verb-takes-a-leading.md) | verify_ac's grep verb takes a leading flag as the pattern, so `grep -q -e X file` and `grep -E ... file` Verify lines fail | Open | Low | 2026-10-11 | 2026-10-11 |
| [BG1025](BG1025-sprint-sign-moves-every-batch-unit-to-its.md) | sprint sign moves every batch unit to its terminal status, overriding a unit an operator ruling deliberately left open (Watching), and the seal then blocks transition from restoring it | Fixed | Medium | 2026-10-12 | 2026-10-12 |
| [BG1026](BG1026-an-ac-heading-with-a-suffix-after-its.md) | An AC heading with a suffix after its id (`### AC3 (DEFERRED)`) is not parsed as a criterion, so its Verify line is folded into the criterion above | Open | Low | 2026-10-12 | 2026-10-12 |
| [BG1027](BG1027-the-commit-time-links-lane-resolves-a-link.md) | The commit-time links lane resolves a link against the working tree, so a staged index row linking to an untracked file passes the commit and turns CI red | Open | Medium | 2026-10-12 | 2026-10-12 |
| [BG1028](BG1028-there-is-no-supported-way-to-run-only.md) | There is no supported way to run only the release verify lane: `gate.py --release --only verify` is refused for deselecting the bound lanes, and the refusal's advice (drop --release) leads to `unknown check name(s): verify` | Open | Low | 2026-10-12 | 2026-10-12 |
| [BG1029](BG1029-critic-record-splits-a-verdict-s-findings-on.md) | critic record splits a verdict's findings on every ';', so reviewer prose with a semicolon is refused as an untagged finding | Superseded | Low | 2026-10-12 | 2026-10-12 |
| [BG1030](BG1030-prose-after-blocking-none-or-a-trailing-rulings.md) | Prose after `BLOCKING: none`, or a trailing `RULINGS:` line, is folded into BLOCKING and refused, so an APPROVE carrying rulings cannot be recorded unedited | Open | Low | 2026-10-13 | 2026-10-13 |
| [BG1031](BG1031-modulealonelanetests-asserts-the-lane-finishes-in-under-3.md) | ModuleAloneLaneTests asserts the lane finishes in under 3.0 seconds of wall clock, so it fails whenever the full parallel suite or another workload shares the cores | Fixed | Medium | 2026-10-13 | 2026-10-13 |
| [BG1032](BG1032-bg0950-did-not-converge-in-review-round-2.md) | BG0950 did not converge in review: round 2 REJECT findings | Fixed | Medium | 2026-10-13 | 2026-10-13 |
| [BG1033](BG1033-when-sign-cannot-read-the-close-s-carried.md) | When sign cannot read the close's carried rows it moves every unit, and the warning it prints has no test | Open | Low | 2026-10-13 | 2026-10-13 |
| [BG1034](BG1034-sign-s-predates-exemption-has-no-pin-and.md) | Sign's predates exemption has no pin, and BG0944's reopen pin and module selection are weaker than they look | Open | Low | 2026-10-13 | 2026-10-13 |
| [BG1035](BG1035-bg0945-s-test-holds-the-old-claim-off.md) | BG0945's test holds the old claim off by one literal phrase, and the untracked first-ruling branch is unstated and unpinned | Open | Low | 2026-10-13 | 2026-10-13 |
| [BG1036](BG1036-bg0978-s-stub-interpreter-test-cannot-tell-sys.md) | BG0978's stub-interpreter test cannot tell sys.executable from the PATH's python3, and checks only an exit code | Open | Low | 2026-10-13 | 2026-10-13 |
| [BG1037](BG1037-a-bracket-of-another-type-opened-inside-a.md) | A bracket of another type opened inside a pair is not literal, so a ';' the pair encloses is still split, and BG1032's note over-claims inside code spans | Open | Low | 2026-10-13 | 2026-10-13 |
| [BG1038](BG1038-the-pre-push-keepalive-check-reads-git-ssh.md) | The pre-push keepalive check reads GIT_SSH above core.sshCommand, the reverse of git's order, and asks ssh -G without the configured command's own options | Open | Low | 2026-10-13 | 2026-10-13 |
| [BG1039](BG1039-us1004-s-one-list-test-no-longer-requires.md) | US1004's one-list test no longer requires `-r` on the suite step, and still checks hand installs against its own list of four packages | Open | Low | 2026-10-13 | 2026-10-13 |
| [BG1040](BG1040-gate-prereqs-prints-the-sdlc-coverage-python-route.md) | gate_prereqs prints the SDLC_COVERAGE_PYTHON route without reading that interpreter, reads markers without evaluating them, and skips -r lines silently | Open | Low | 2026-10-13 | 2026-10-13 |
| [BG1041](BG1041-the-module-alone-lane-test-can-never-pass.md) | The module-alone lane test can never pass on a host with fewer than four cores, and blames the pool for it | Open | Low | 2026-10-13 | 2026-10-13 |
| [BG1042](BG1042-the-push-preflight-s-tests-leak-sdlc-coverage.md) | The push preflight's tests leak SDLC_COVERAGE_PYTHON and leave its REFUSES mark and pytest's class unpinned | Open | Low | 2026-10-13 | 2026-10-13 |
| [BG1043](BG1043-the-prerequisite-check-and-the-gate-read-pytest.md) | The prerequisite check and the gate read pytest-xdist two different ways | Open | Low | 2026-10-13 | 2026-10-13 |
| [BG1044](BG1044-a-ruling-record-s-note-is-decided-by.md) | A ruling record's note is decided by the whole ledger, and a tab in a reviewer id still forges a field | Fixed | Low | 2026-10-13 | 2026-10-13 |
| [BG1045](BG1045-us1006-did-not-converge-in-review-round-2.md) | US1006 did not converge in review: round 2 REJECT findings | Fixed | Medium | 2026-10-14 | 2026-10-14 |
| [BG1046](BG1046-a-carry-turns-a-pre-existing-finding-into.md) | A carry turns a pre-existing finding into a criterion the carried bug can never meet | Open | Low | 2026-10-14 | 2026-10-14 |
| [BG1047](BG1047-test-status-s-backlog-advisory-fixture-dates-its.md) | test_status's backlog advisory fixture dates its bugs 2026-07-16, so it went stale on 2026-10-14 and main is red | Fixed | High | 2026-10-14 | 2026-10-14 |
| [BG1048](BG1048-forward-port-deletes-the-changelog-md-install-sh.md) | forward-port deletes the CHANGELOG.md install.sh ships into the installed copy | Open | Low | 2026-10-14 | 2026-10-14 |
| [BG1049](BG1049-bg1044-s-ruling-record-tests-leave-the-date.md) | BG1044's ruling-record tests leave the date, the note's once-only rule, the heading anchor and the case boundary unpinned | Open | Low | 2026-10-14 | 2026-10-14 |
| [BG1050](BG1050-a-reviewer-id-carrying-a-carriage-return-or.md) | A reviewer id carrying a carriage return or line separator tears its own verdict row | Open | Medium | 2026-10-14 | 2026-10-14 |
| [BG1051](BG1051-the-close-s-chain-report-cuts-every-refusal.md) | The close's chain report cuts every refusal line at 160 characters, hiding which unit is blocked and why | Open | Medium | 2026-10-14 | 2026-10-14 |
| [BG1052](BG1052-a-unit-whose-risk-band-rises-after-its.md) | A unit whose risk band rises after its review is found under-reviewed only at the close | Open | Medium | 2026-10-14 | 2026-10-14 |
| [BG1053](BG1053-us1004-did-not-converge-in-review-round-3.md) | US1004 did not converge in review: round 3 REJECT findings | Fixed | Medium | 2026-10-14 | 2026-10-14 |
| [BG1054](BG1054-the-scheduled-corpus-verify-lane-reads-us0892-ac1.md) | The scheduled corpus-verify lane reads US0892 AC1 red because its job installs no pytest-xdist | Open | Medium | 2026-10-14 | 2026-10-14 |
| [BG1055](BG1055-a-retro-scaffolded-by-the-close-and-committed.md) | A retro scaffolded by the close and committed before the close re-runs turns the release-verify lane red | Open | Low | 2026-10-15 | 2026-10-15 |
| [BG1056](BG1056-bg1053-did-not-converge-in-review-round-2.md) | BG1053 did not converge in review: round 2 REJECT findings | Fixed | Medium | 2026-10-15 | 2026-10-15 |
| [BG1057](BG1057-the-one-list-test-s-check-that-ci.md) | The one-list test's check that ci installs from requirements-dev.txt sits outside its self-tested rules | Open | Low | 2026-10-15 | 2026-10-15 |
| [BG1058](BG1058-the-close-s-dry-run-names-a-unit.md) | The close's dry run names a unit the run cannot end over that the real tree answers | Open | Medium | 2026-10-15 | 2026-10-15 |
| [BG1059](BG1059-a-retro-s-batch-field-is-never-compared.md) | A retro's Batch field is never compared with the run's batch, so a unit added after the retro was scaffolded is left out of the run's measurement and its close accounting | Open | Medium | 2026-10-16 | 2026-10-16 |
| [BG1060](BG1060-retro-extract-starts-a-new-project-lessons-log.md) | retro extract starts a new project lessons log when the committed one is missing, though the committed digest lists the lessons that log holds | Open | Medium | 2026-10-16 | 2026-10-16 |
| [BG1061](BG1061-the-committed-project-lessons-log-cannot-be-committed.md) | The committed project lessons log cannot be committed where markdownlint's defaults apply: every lesson heading ends in its sentence's punctuation, which MD026 refuses | Open | Medium | 2026-10-16 | 2026-10-16 |
| [BG1062](BG1062-sprint-sign-names-no-commit-trailers-for-the.md) | sprint sign names no commit trailers for the paperwork it writes, so its commit draws one engagement-floor attribution advisory per unit it moved | Open | Low | 2026-10-18 | 2026-10-18 |

## Archived Releases

- **v6.1** (BG0659-BG0943, 283 archived) -> sdlc-studio/bugs/archive/v6.1/bug.md
- **v5.1.0** (BG0350-BG0663, 181 archived) -> sdlc-studio/bugs/archive/v5.1.0/bug.md
- **v5.0.0** (BG0302-BG0498, 178 archived) -> sdlc-studio/bugs/archive/v5.0.0/bug.md
- **v3.4.0** (BG0001-BG0052, 52 archived) -> sdlc-studio/bugs/archive/v3.4.0/bug.md
