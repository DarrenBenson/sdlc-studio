# Known issues

The defects SDLC Studio knows about and has chosen to ship. This page is the disclosure
half of the release bar: a project that hides its open findings is asking to be trusted
rather than read.

## The bar v6.2 is held to

**Zero open Critical or High finding at the tag, and every open Medium ruled by one triage
decision.** A finding either reaches a terminal status with its own verifiers passing, or it
stays open under the triage target below, which one recorded decision rules for the whole list
rather than a waiver per finding.

**Medium and Low findings ship open, listed here by id, triaged to v6.3.** Each is a real
defect with a reproduction and, in most cases, a proposed fix. None of them stops the
lifecycle running. They are listed rather than closed, because closing a bug to make a
release look clean is the practice this tool exists to prevent.

Each id below is a file in `sdlc-studio/bugs/` in the source repository, carrying the
evidence, the reproduction and the proposed fix in full.

## The bar v5.1 was held to, kept as history

**Zero open High-severity bugs at the tag, and every Medium disposed of or ruled.** A
finding either reaches a terminal status with its own verifiers passing, or it stays open
carrying a dated ruling that says why it ships.

## The bar v5.0.0 was held to, kept as history

**Zero open High-severity bugs at the tag.** Every High finding raised against v5 was
fixed and closed before the tag was cut. The bar was originally zero open bugs of any
severity; it moved on 2026-08-11, because holding a release for findings that are real
but not release-blocking had cost a month and was buying nothing a disclosure could not
buy honestly.

## Triaged to v6.3

| Id | Severity | Finding |
| --- | --- | --- |
| `BG0946` | Low | reports/_index.md Last Updated is not restamped when a report is filed |
| `BG0952` | Low | An Open Questions item declaring None after a dash is read as unanswered - `_DECLARES_NONE_RE` does not allow a leading dash |
| `BG0953` | Low | Full-template story and TSD ship unrendered {{config.story_quality.*}} placeholders |
| `BG0960` | Low | A plan refused for a missing Verify line tells you to add Affects and Points |
| `BG0964` | Low | help/refine.md never mentions `--into`, so a story added to an already-refined epic is made with `artifact.py new` and carries no Delivers link |
| `BG0966` | Low | review_prep persona_usage calls a persona unused unless its file's H1 appears verbatim in prd.md - stories, CRs and consult logs are never read |
| `BG0969` | Low | sprint close --file-and-close silently drops a supplied --goal-verdict, then refuses because the goal is unjudged - a hard blocker it cannot file |
| `BG0971` | Low | sprint close --dry-run reports later chain steps in the past tense ('lessons lifted', 'summary regenerated', 'anchor refreshed') although nothing w... |
| `BG0972` | Low | `artifact.py retitle` quotes the old title verbatim in its revision row, so a retitle made to remove an em dash or a bare identifier puts it straig... |
| `BG0973` | Low | artifact.py new --type review warns 'its acceptance criteria are still the scaffold placeholder' although the review scaffold has no Acceptance Cri... |
| `BG0974` | Low | The filing tools do not markdown-safe the title or the Evidence line, so a bare snake_case identifier fails MD037 at commit or in CI |
| `BG0975` | Low | critic.py brief --rejoinder derives a light tier from the risk band even when the round it answers was taken at an explicit full tier |
| `BG0977` | Low | help/status.md documents '/sdlc-studio status --brief' but status.py has no --brief, so the documented one-line summary errors |
| `BG0979` | Low | `file_finding.py` misdirects a CR's author: `--recommendation` is documented as RFC-only though a CR carries it, and the no-verifier warning cites... |
| `BG0980` | Low | Filing refuses a `-k` selector for a test the fix will add to an existing module without naming the node-id form it would accept, so authors scatte... |
| `BG0984` | Low | Changing a criterion's Verify expression keeps the old Verified date and evidence when the new one passes |
| `BG0988` | Low | sprint plan's one-run-slot refusal tells the operator to finish a close that already finished, when only the signature is owed |
| `BG0992` | Low | BG0989's approved repair leaves three branches unpinned, and its docs over-claim which commands move the legacy lessons log |
| `BG0996` | Low | The finding filer's identifier wrapper pulls trailing punctuation into the code span: (`API_KEY_2`, `TOKEN_V2)` and `keep_alive.` |
| `BG1001` | Low | A clone that never held a run awaiting its signature can end it only by signing it: stop there says there is nothing to stop |
| `BG1004` | Low | BG0993's tracked run record tells a newer copy by reopen count alone, so two reopens made at once overwrite each other; and the close preview's no-... |
| `BG1006` | Low | sprint batch add prints a refusal for an unresolvable Affects path but adds the unit anyway |
| `BG1008` | Low | A waiver recorded before the run can answer a checklist row while the page's Waivers in force section says no gate stood down |
| `BG1010` | Low | sprint_report.py build --run resolves the named run and then builds the page from the default run |
| `BG1011` | Low | LL0056 ships with its label doubled and the template's placeholder sections left in, and nothing refuses a lesson with an unfilled placeholder |
| `BG1013` | Low | The waiver remedy the close and the checklist print omits --authorised-by, so the command as printed is refused |
| `BG1014` | Low | revert-check rewrites production files in place without declaring a rewrite window, so a commit made while it runs can stage a reverted file |
| `BG1016` | Low | lessons add --global defaults a promoted lesson's origin to the working directory's name, so a consuming project's directory name is written into a... |
| `BG1017` | Low | validate warns pseudo-verify on the Verify line a request's own writers put beneath each criterion |
| `BG1018` | Low | refine apply --question leaves the request ending on a blank line, which markdownlint refuses (MD012) |
| `BG1020` | Low | transition.py refuses an RFC's Accepted until its spawned CRs are resolved, contradicting reference-rfc.md's accept step |
| `BG1022` | Low | A stale TSD still says the batch does not deliver Unit Testing |
| `BG1024` | Low | verify_ac's grep verb takes a leading flag as the pattern, so `grep -q -e X file` and `grep -E ... file` Verify lines fail |
| `BG1026` | Low | An AC heading with a suffix after its id (`### AC3 (DEFERRED)`) is not parsed as a criterion, so its Verify line is folded into the criterion above |
| `BG1028` | Low | There is no supported way to run only the release verify lane: `gate.py --release --only verify` is refused for deselecting the bound lanes, and th... |
| `BG1030` | Low | Prose after `BLOCKING: none`, or a trailing `RULINGS:` line, is folded into BLOCKING and refused, so an APPROVE carrying rulings cannot be recorded... |
| `BG1033` | Low | When sign cannot read the close's carried rows it moves every unit, and the warning it prints has no test |
| `BG1034` | Low | Sign's predates exemption has no pin, and BG0944's reopen pin and module selection are weaker than they look |
| `BG1035` | Low | BG0945's test holds the old claim off by one literal phrase, and the untracked first-ruling branch is unstated and unpinned |
| `BG1037` | Low | A bracket of another type opened inside a pair is not literal, so a ';' the pair encloses is still split, and BG1032's note over-claims inside code... |
| `BG1038` | Low | The pre-push keepalive check reads GIT_SSH above core.sshCommand, the reverse of git's order, and asks ssh -G without the configured command's own... |
| `BG1040` | Low | gate_prereqs prints the SDLC_COVERAGE_PYTHON route without reading that interpreter, reads markers without evaluating them, and skips -r lines sile... |
| `BG1041` | Low | The module-alone lane test can never pass on a host with fewer than four cores, and blames the pool for it |
| `BG1042` | Low | The push preflight's tests leak SDLC_COVERAGE_PYTHON and leave its REFUSES mark and pytest's class unpinned |
| `BG1043` | Low | The prerequisite check and the gate read pytest-xdist two different ways |
| `BG1049` | Low | BG1044's ruling-record tests leave the date, the note's once-only rule, the heading anchor and the case boundary unpinned |
| `BG1055` | Low | A retro scaffolded by the close and committed before the close re-runs turns the release-verify lane red |
| `BG1062` | Low | sprint sign names no commit trailers for the paperwork it writes, so its commit draws one engagement-floor attribution advisory per unit it moved |
| `BG1064` | Low | 15 of 69 shipped scripts are tracked without the executable bit the TRD's script contract requires, a regression of CR0064's fix |
| `BG1067` | Low | The triage session cap keys on the run state's id whether or not the run is sealed, so a signed run's counter keeps charging every later session's... |
| `BG1068` | Low | artifact.py retitle rewrites an inbound link's target but leaves its link text naming the old title, so an epic's story breakdown reads the retired... |
| `BG1069` | Low | critic escalation reads verdicts across a reopen: a reopened unit's first new-round REJECT is reported as a panel split against the previous delive... |
| `BG1070` | Low | conformance reads US0357 and US0358 as missing their verified stage wherever markdownlint is not installed, because their test modules raise at col... |
| `BG1071` | Low | The project seat card's design-persona check stops at a full stop, so a name followed by a file path before 'design persona' passes |
| `BG1072` | Low | test_persona_coherence's id check reads a fixed list of id prefixes, so a card citing a handoff or test-spec id that resolves to nothing passes |
| `BG1073` | Low | critic.py record writes a reviewer's findings verbatim into a ledger the repository's markdownlint refuses, so a finding quoting an email-shaped na... |
| `BG1074` | Low | No test pins that a red gate-host run records its duration, so the hook can stop recording exit 1 with the suite green |
| `BG1075` | Low | tools/remote-gate.sh's local side needs bash 4, so a pusher on stock macOS bash 3.2 has every gate-host push refused |
| `BG1079` | Low | A unit carried at the review cap gets a criterion for every ISSUES item, including info rulings and pre-existing findings already filed |
| `BG1080` | Low | remote-gate doctor calls a host ready without checking flock and setsid, which every push run on it needs |
| `BG1081` | Low | remote-gate doctor sources gate-env.sh from its temporary directory, where the gate sources it from the host's home |
| `BG1082` | Low | Four of remote-gate doctor's stated behaviours have no test that fails without them |
| `BG1083` | Low | enable-hooks.sh's tolerance of an unready or unreachable gate host has no test |
| `BG1084` | Low | remote-gate doctor's exit codes are documented as 0, 1 and 3, and a missing transport is reported as an unready host |
| `BG1085` | Low | remote-gate doctor prints the local clone's Python install route for a gap on the gate host |
| `BG1086` | Low | run-suite.sh's passed count needs bc, which is not a declared prerequisite, and is null with a broken-pipe error where bc is absent |
| `BG1092` | Low | The TSD says the commit-msg hook falls back to skill-tests.sh only without pytest; it also does when the handover carries no selectors |
| `BG1093` | Low | BG1061's heading checks read a heading's trailing space as its last character, so a mark left behind a space passes |
| `BG1094` | Low | A lesson that is only punctuation gets an empty heading title since BG1061 |
| `BG1096` | Low | The TRD says verify_ac run --coverage refuses under block and reports under report when coverage is absent; the split is the Done gate's |
| `BG1097` | Low | US1085's toolchain-doc tests leave coverage unpinned, still pass three counted phrasings, and fail at collection without PyYAML |
| `BG1098` | Low | AGENTS.md gives the local boundary-push series as the push's cost on a clone that names a gate host |
| `BG1100` | Low | gate.py's verify ceiling still calls 300 s CI's figure, though corpus-verify now runs every criterion under 450 s |
| `BG1103` | Low | The close binds the untracked files it leaves into the signature without naming them, so tidying one refuses the sign |
| `BG1104` | Low | A message-only amend runs the whole-workspace gate at commit, because the hook's gate lane reads an empty staged diff as no diff to scope to |
| `BG1106` | Low | package-lock.json resolves smol-toml 1.7.1 and katex 0.16.47 through markdownlint-cli 0.49.1, inside Dependabot alerts 25 and 24 |
| `BG1110` | Low | backlog_triage's duplicate lens has no way to record a pair confirmed distinct, so a triaged pair is re-reported on every run |
| `BG1115` | Low | A commit that adds a subcommand never selects test_cli_grammar.py, which reaches every script through surface.enumerate_scripts, so a grammar defec... |
| `BG1118` | Low | Six behaviours the self-check record, its brief gate and the author section state are pinned by no test (US1087, US1088, US1089 reviews) |
| `BG1119` | Low | Two behaviours BG1000's repair states for per-commit selection are pinned loosely or not at all: the census header's 40-line window, and the rewrit... |
| `BG1121` | Low | An author self-check record still reads stale in landing orders the per-file own-change view cannot see through: work recorded before its own commi... |
| `BG1123` | Low | A review brief now carries two different diffs of the unit: the scope line's `git diff <base> -- <Affects>` (the working tree) and US1094's UNIT DI... |
| `BG1126` | Low | A seat-requested amendment of an open run's goal leaves the run state on the old goal, so the close's goal read reports 'a different goal' |
| `BG1128` | Low | The close's goal panel and the next amendment's carry read only the latest goal-review round, while the plan reads every round on the latest wordin... |
| `BG1129` | Low | test_lean_gate_host_docs.py's table test says a hook honouring a value other than 1 fails it, but an edit outside the lines `_hook_code` cuts passe... |
| `BG1130` | Low | The builder brief's commit step quotes each Affects path with shlex.quote, but no test has a path with a space, so dropping the quoting stages the... |
| `BG1131` | Low | The close checklist's cost row never reads a run holding only its legacy baseline, and its main-thread-only re-derivation note has no test |
| `BG1132` | Low | BG0962's AC7 test proves only the REJECT half of 'the frozen verdict decides' when the per-unit ledger cannot be read |
| `BG1133` | Low | Three VELOCITY Priced/pt behaviours US1092 states are pinned by no test: the Source guard, an earlier row keeping its recorded figure, and rows wit... |
| `BG1134` | Low | US1095's cost check is pinned only on the older retro shape, cost-baseline add reports a row the median never uses, and its latest-five window has... |
| `BG1141` | Low | The gate-host docs test's docstrings claim more than it samples: values of SDLC_GATE_LOCAL other than 1, and keys read as `git -C <dir> config` |
| `BG1142` | Low | doc-freshness is described as a LATEST.md check everywhere, though it now censuses the TRD, PRD and TSD; one hook comment lists it as a per-commit... |
| `BG1143` | Low | doc_freshness's baseline leg has no pin for checking every Coverage line, nor for skipping the revision history |
| `BG1144` | Low | The commit hook's unittest fallback ignores pytest's serial_only and boundary_only marks, so a push-only test still runs on a commit there |
| `BG1145` | Low | readiness's carry note names a re-review that critic.py record refuses for a unit at the cap with no filed carry bug; only a --ruling discharges it |
| `BG1146` | Low | lessons.py revalidate --close appends its Status bullet straight after a paragraph, so the lessons log fails markdownlint MD032 |
| `BG1148` | Low | revalidate's real-date guard has no test, its refusal prefix names --extend for any bad fields file, and the gate hint and four docs show --extend... |
| `BG1149` | Low | RFC0048's resolved D6 still states a 120s per-commit gate budget against a 99s baseline, while the config has declared 480s against 400s since 2026... |
| `BG1150` | Low | sprint.py still says the planner reads the series 'the budget lane reads', though that lane was deleted in 315ec358 |
| `BG1151` | Low | The interface-path persona router reads a template placeholder as a declared interface, cuts a row at an escaped pipe, leaves ./ unpinned, and disa... |
| `BG1152` | Low | artifact.py batch writes a list-valued affects as a Python repr, so the Affects line reads ['hooks/pre-push'] |
| `BG1153` | Low | EXECUTES_VERIFIERS's docstring says verify_ac reads it, but verify_ac keeps its own VERIFIABLE_PREFIXES, and the TRD says an un-decomposed CR 'reac... |
| `BG1154` | Low | Trevor's card says a sign-off on each unit is declined, though sprint.py sign writes a per-unit sign-off row under the one signature |
| `BG1155` | Low | decisions.read_once's change detection is pinned only by a growing file: dropping inode, mtime or ctime from its identity stays green |
| `BG1156` | Low | test_persona_coherence's span recogniser skips some `script.py verb` shapes, and its mixed-unit probe cannot tell first-listed Primary from first-p... |
| `BG1157` | Low | No test pins that a --host prerequisite check still names a missing markdownlint, so widening PUSHER_ONLY to it stays green |
| `BG1158` | Low | The TRD verifier-authority scan misses some story-only rewordings and fails true sentences about a story-only run |
| `BG1159` | Low | supersede's reference omits --brief and row-brief, two of its new guarantees are unpinned, and a no-match refusal contradicts itself |
| `BG1161` | Low | A clean-checkout gate.py run judges conformance over the whole workspace and reads OVER the standard budget every time |
| `BG1162` | Low | PrdRulesTests' protections are thinner than its claims: four PRD facts can drift past it |
| `BG1164` | Low | ADR-009 omits the generic persona rung, the TRD gh-caller scan reads only a literal argv, and sprint's fetch-failure reason is garbled |
| `BG1165` | Low | The TSD's Security Testing section says the script contract forbids network calls except the gh wrapper, but a version-check GET and git fetch orig... |
| `BG1168` | Low | The PRD test's unreleased-marker check strips code spans from the whole row, and PRD edits land with no Revision History row |
| `BG1169` | Low | mutation.py's _drop_ignored ignores git check-ignore's exit code, so one path git refuses leaves the rest partly filtered |
| `BG1170` | Low | The TSD and TRD refresh tests leave low residual gaps their round-2 and BG1166 reviews named |
| `BG1171` | Low | reconcile settle closes an epic in the pre-commit hook but leaves the requests that close made derivable, so the same commit's gate refuses on that... |
| `BG1172` | Low | Four open Dependabot alerts on main sit in development dependencies: markdown-it (High and Low), smol-toml (Medium) and katex (Low) |
| `BG1173` | Low | A close that reuses a pinned token actual writes 'Priced cost: not stated' into the retro with a lower-case reason, though its report states the ru... |
| `BG1174` | Low | The v6.2 notes test exempts the whole no-Breaking paragraph, so a changed-default sentence added inside it passes with no Instead clause |
| `BG1175` | Low | docs/existing-users.md has a From 6.0 to 6.1 section but none for 6.1 to 6.2, so the upgrade page stops one release short |
| `BG0947` | Medium | reference-outputs.md terminal-status table contradicts sdlc_md.TERMINAL_STATUS |
| `BG0948` | Medium | A migrating project cannot baseline pre-existing placeholder findings, and v3 ids can never be baselined |
| `BG0949` | Medium | An inline `ruled:` or `decided:` ruling is never recognised - `_RULING_RE` puts a word boundary after the colon |
| `BG0954` | Medium | A Draft story transitions straight to Done - the Definition of Ready is never required |
| `BG0956` | Medium | transition set reports index synced but leaves archived index rows stale, and reconcile apply refuses them |
| `BG0957` | Medium | `test_epic_index_derived`'s negative control needs a live epic row with a count, so an archive that empties the live epic index turns it red |
| `BG0958` | Medium | `mutation.py` finds no changed lines when git's `diff.mnemonicPrefix` is set, so a mutation probe scoped to a unit's changes has nothing to mutate |
| `BG0959` | Medium | The engagement floor rejects a ULID adopt_after cutoff and tells you to set a sequential one |
| `BG0961` | Medium | A Verify line cannot name the skill: <skill> is a shell redirect, not a path |
| `BG0965` | Medium | retro.py validate ignores '## Actions raised' in a Keep/Stop/Try retro, so it reports '0 findings, all dispositioned' over rows it never read |
| `BG0967` | Medium | The finding filer backtick-wraps identifiers inside Steps to Reproduce, corrupting the shell commands a repro depends on |
| `BG0968` | Medium | CI runs tools/tests in the same step as the skill suite, so a red skill suite hides every tools/tests failure |
| `BG0970` | Medium | `critic.py brief` says nothing when the unit's Affects carry uncommitted changes, though it sends the reviewer to an isolated worktree that cannot... |
| `BG0981` | Medium | breakdown and plan call a unit groomed when a Verify line is one verify_ac cannot parse |
| `BG0982` | Medium | critic brief's diff scope is the unit's Affects only - files the unit changed but did not declare are invisible to the reviewer |
| `BG0983` | Medium | `review_coverage` and `verdict_for` read a unit's whole per-unit ledger, so an APPROVE from an earlier delivery covers a re-delivered unit that nob... |
| `BG0985` | Medium | sprint close --dry-run reports a non-blocking pre-flight row as a STOP refusal and exits 1, so a close that would proceed previews as refused |
| `BG0986` | Medium | `tools/forward-port.sh` deletes the CHANGELOG.md the installer ships into the skill, so `project upgrade` loses its changelog digest after every fo... |
| `BG0987` | Medium | The close's goal judgement reaches only the terminal, not the sprint report the signer is told to read, and says 'blocks the close' of defects that... |
| `BG0990` | Medium | reconcile's field sync reads a '·'-joined metadata run to end of line, writing 'P2 · **Type:** ...' into index cells and dropping the later fields |
| `BG0991` | Medium | verify_ac attaches a **Verify:** line from a LATER section (history, update notes) to the last criterion and executes it, because a criterion block... |
| `BG0995` | Medium | refine leaves the bold **ACn** label in seeded AC headings, so a request written by the skill's own filer seeds '### AC1: **AC1** ...' (BG0291 inco... |
| `BG0997` | Medium | A per-unit engagement-floor waiver pasted with the dashed v3 id does not waive the unit |
| `BG0998` | Medium | The story template ships Verified no, which verify_ac treats as an authored miss |
| `BG0999` | Medium | Caller-check cannot resolve a skill script named as the consumer |
| `BG1002` | Medium | goal-review brief ignores the plan's --serves and the batch changes made after plan --write |
| `BG1005` | Medium | A pytest Verify that PARTLY skips is stamped green - BG0317 closed only the all-skipped case |
| `BG1009` | Medium | revert-check reads a timed-out verifier as red and an empty revert as green, so it passes a unit it never measured and refuses one it never reverted |
| `BG1012` | Medium | The sprint checklist reads a run only from .local, so in any other clone a signed run's rows read 'no run record could be read' |
| `BG1015` | Medium | persona_resolve.py resolve refuses a seat role the project declares (sre), though validate seats and critic.py brief accept it |
| `BG1019` | Medium | artifact.py retitle refuses in every consuming project: it loads tools/check_links.py from the operated repo or the skill's own source checkout, an... |
| `BG1021` | Medium | A CR declared Size L is not flagged for decomposition |
| `BG1023` | Medium | verify_ac's vitest and jest verbs fold the whole tail into the -t pattern and call a bare binary, so `vitest <file> -t "name"` can never select its... |
| `BG1027` | Medium | The commit-time links lane resolves a link against the working tree, so a staged index row linking to an untracked file passes the commit and turns... |
| `BG1050` | Medium | A reviewer id carrying a carriage return or line separator tears its own verdict row |
| `BG1051` | Medium | The close's chain report cuts every refusal line at 160 characters, hiding which unit is blocked and why |
| `BG1052` | Medium | A unit whose risk band rises after its review is found under-reviewed only at the close |
| `BG1058` | Medium | The close's dry run names a unit the run cannot end over that the real tree answers |
| `BG1059` | Medium | A retro's Batch field is never compared with the run's batch, so a unit added after the retro was scaffolded is left out of the run's measurement a... |
| `BG1060` | Medium | retro extract starts a new project lessons log when the committed one is missing, though the committed digest lists the lessons that log holds |
| `BG1063` | Medium | `require_ac_verification` is documented as a gate that aborts the completion cascade on a failed verification, but no code reads it |
| `BG1090` | Medium | test_output_prints_in_declared_order_whatever_finishes_first failed one subtest under heavy load, and passes alone; not yet diagnosed |
| `BG1101` | Medium | test_repo_hygiene writes probe fixtures into the real scripts/tests directory, so a parallel test copying that tree can fail |
| `BG1107` | Medium | sprint._end_goals keeps only the first line of a wrapped End goal, so the goal-review brief and the goal trace show Rowan's goals cut off mid-sentence |
| `BG1108` | Medium | A carried unit whose repair landed before the new run's base has an empty review diff, so its redelivery review cannot block |
| `BG1112` | Medium | verify_ac's timeout kills only the shell it started, so a timed-out shell or eval verifier leaves its real test runner (npx, vitest, pytest) runnin... |
| `BG1114` | Medium | critic.py brief spends 19 of its 20 seconds walking the artefact corpus, because it reads the files' history without the corpus cache that lane bri... |
| `BG1116` | Medium | Shipped guidance tells a consuming project's agent to run the full suite before every commit, which the shipped gate's per-commit selection and pus... |
| `BG1120` | Medium | A self-check record reads an author's own edit made in a merge commit as another unit's, so the brief gate admits a changed diff in a project that... |
| `BG1122` | Medium | Each meter reading now re-reads every subagent transcript from the start, so a lane, transition or report command takes about 36 s on a long sessio... |
| `BG1124` | Medium | critic.py brief's practice and claim-inventory refusals read the whole brief, so the unit diff US1094 embeds can satisfy them, and a unit whose own... |
| `BG1125` | Medium | The review brief's unit diff is the whole run's diff over the unit's files, not the unit's own change, so on a shared file the 400-line cap is spen... |
| `BG1147` | Medium | The pre-commit markdown lane skips in a linked worktree, because it looks for markdownlint only in that worktree's node_modules |
| `BG1160` | Medium | gate.py --run-tests prints 'no tests ran' and exits 0 when one of its modules is missing, even if a real module beside it fails |
| `BG1163` | Medium | The TRD's lifecycle table states a tracked record is filed on every close, which --file-and-close does not do, and the .local writer pin accepts an... |
| `BG1167` | Medium | Conformance re-derives a closed unit's risk band from today's tree, so a later unit's edit to a shared file fails a light APPROVE that was right wh... |

176 findings: 56 Medium, 120 Low.

## Not carried

5 findings at a barred severity were ruled `Won't Fix` on their own merits: `BG0124`,
`BG0139`, `BG0583`, `BG0713`, `BG0951`.

They are not in the list above because they are not open, and a disclosure that pads
its count is as misleading as one that trims it.

## How this list is kept

It is derived from the bug corpus by `tools/known_issues.py` when a release is cut, not
maintained by hand, and the pre-push hook refuses a tag whose page disagrees with the corpus.
Any open bug whose severity is Medium or Low appears here; a bug that reaches a terminal
status leaves at the next cut. Cut it with
`python3 tools/known_issues.py write --release <version>`.
