# Known issues

The defects SDLC Studio knows about and has chosen to ship. This page is the disclosure
half of the release bar: a project that hides its open findings is asking to be trusted
rather than read.

## The bar v6.4 is held to

**Zero open Critical or High finding at the tag, and every open Medium ruled by one triage
decision.** A finding either reaches a terminal status with its own verifiers passing, or it
stays open under the triage target below, which one recorded decision rules for the whole list
rather than a waiver per finding.

**Medium and Low findings ship open, listed here by id, triaged to v6.5.** Each is a real
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

## Triaged to v6.5

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
| `BG1006` | Low | sprint batch add prints a refusal for an unresolvable Affects path but adds the unit anyway |
| `BG1008` | Low | A waiver recorded before the run can answer a checklist row while the page's Waivers in force section says no gate stood down |
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
| `BG1110` | Low | backlog_triage's duplicate lens has no way to record a pair confirmed distinct, so a triaged pair is re-reported on every run |
| `BG1115` | Low | A commit that adds a subcommand never selects test_cli_grammar.py, which reaches every script through surface.enumerate_scripts, so a grammar defec... |
| `BG1118` | Low | Six behaviours the self-check record, its brief gate and the author section state are pinned by no test (US1087, US1088, US1089 reviews) |
| `BG1119` | Low | Two behaviours BG1000's repair states for per-commit selection are pinned loosely or not at all: the census header's 40-line window, and the rewrit... |
| `BG1121` | Low | An author self-check record still reads stale in landing orders the per-file own-change view cannot see through: work recorded before its own commi... |
| `BG1123` | Low | A review brief now carries two different diffs of the unit: the scope line's `git diff <base> -- <Affects>` (the working tree) and US1094's UNIT DI... |
| `BG1126` | Low | A seat-requested amendment of an open run's goal leaves the run state on the old goal, so the close's goal read reports 'a different goal' |
| `BG1128` | Low | The close's goal panel and the next amendment's carry read only the latest goal-review round, while the plan reads every round on the latest wordin... |
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
| `BG1168` | Low | The PRD test's unreleased-marker check strips code spans from the whole row, and PRD edits land with no Revision History row |
| `BG1169` | Low | mutation.py's _drop_ignored ignores git check-ignore's exit code, so one path git refuses leaves the rest partly filtered |
| `BG1170` | Low | The TSD and TRD refresh tests leave low residual gaps their round-2 and BG1166 reviews named |
| `BG1171` | Low | reconcile settle closes an epic in the pre-commit hook but leaves the requests that close made derivable, so the same commit's gate refuses on that... |
| `BG1173` | Low | A close that reuses a pinned token actual writes 'Priced cost: not stated' into the retro with a lower-case reason, though its report states the ru... |
| `BG1174` | Low | The v6.2 notes test exempts the whole no-Breaking paragraph, so a changed-default sentence added inside it passes with no Instead clause |
| `BG1178` | Low | known_issues.py check compares the page with the corpus but never reads the release notes' count sentence, so a hand edit of that line goes uncheck... |
| `BG1179` | Low | The TRD refresh test pins vocabulary rather than US1101's corrected claims: the ADR-012 row, the ADR sentences and an aliased urlopen all slip past it |
| `BG1180` | Low | The PRD's section 8 says git fetch origin serves remote-aware id allocation, which section 5 and next_id.py contradict: id allocation never fetches |
| `BG1181` | Low | gate_prereqs.py check reports every prerequisite present on a machine with no Python 3.10, which the release gate's US0908 lane needs |
| `BG1182` | Low | `test_agents_md_full_suite_rule`'s `_problems` docstring says it lists every way the text falls short of AC1, but it checks more than AC1 and stops... |
| `BG1184` | Low | BG1176's re-pointed criteria leave three sub-claims unpinned, and two manual Verify lines still send a reviewer to a folded fragment |
| `BG1185` | Low | BG1167's rule reads a light APPROVE's scope from git history, so three narrow orderings still count a unit whose own Affects widened as covered |
| `BG1186` | Low | The release verify lane's declared budget is 600 s against a measured 3,340 s, so every release run prints OVER and the pin keeps it there |
| `BG1188` | Low | One lane-cap test took 695 s on a worker, re-running its whole class once per hook lane |
| `BG1189` | Low | reference-verify.md#batch says only jest batches, but verify_ac has a pytest batch cache that the release lane uses |
| `BG1191` | Low | The batch's phase plugin reads serial_only before a conftest's own trylast hook, so a mark that hook applies runs on an xdist worker |
| `BG1192` | Low | US1113 AC3's one-at-a-time pin lets a concurrent serial pool through under load, because its three 0.5 s probes must start within 0.5 s of each other |
| `BG1193` | Low | sdlc_md.corpus_cache hands later callers the path spelling of the first walk, so a relative root then an absolute one raises ValueError in reconcile |
| `BG1194` | Low | remote-gate.sh's release route does not send SDLC_GATE_BOUNDARY, so a value set in the shell changes the local release gate but not the host's |
| `BG1195` | Low | Four test modules of tools/remote-gate.sh name no test-census-subject, so a commit to the script runs only one of the five |
| `BG1196` | Low | No test pins the host's SDLC_STUDIO_BOUNDARY_SUITE=1 export for remote-gate.sh's push and suite jobs |
| `BG1198` | Low | reference-config.md says the commit-msg hook refuses a commit without a Refs: trailer per owning id, and does not name the Mentions: trailer US1115... |
| `BG1199` | Low | US1115's reference and fragment say a commit whose every id is a mention is attributed no files, but a one-id subject whose only id is a Mentions:... |
| `BG1200` | Low | mutation.changed_lines reports no lines when git's color.ui or color.diff is always, because the +++ b/ header arrives wrapped in ANSI codes |
| `BG1201` | Low | US0989's Cursor usage reader takes its variable names and response shape from documentation, not from a real Cursor cloud run |
| `BG1202` | Low | US0989's Cursor reader leaves two guards unpinned and names an empty usage for a malformed answer |
| `BG1203` | Low | US0991 AC3's Verify line cannot fail on the close's main-thread prose, which only a sibling test pins |
| `BG1204` | Low | A run metered by two harnesses adds the supplied delegated totals in full, even over a reading that already holds delegated spend |
| `BG1206` | Low | BG1116's pins key on literal wording: the boundary-habit test refuses only gate.py, and the per-commit and AGENTS.md checks pass reworded regressions |
| `BG1207` | Low | BG1197's harness scrub lives in the root conftest, so unittest runs (skill-tests.sh, the hook's unittest fallback) still read the harness from the... |
| `BG1208` | Low | BG1122's meter memo leaves the unfinished-line size refresh unpinned, and its changelog's equals-a-whole-read claim holds only for append-only growth |
| `BG1209` | Low | The pre-commit hook's payload markdown lane quotes its markdownlint path untested, because the BG1147 fixture tracks no markdown under .claude/ |
| `BG1211` | Low | The shell-hazard check flags unittest's own assertion separator (the spaced colon after an assertion's operands) when a reviewer's finding quoting... |
| `BG1214` | Low | BG1212's AC2 docstring says only a clock can see the no-timeout join mutant, but the clock-free AC2 test also fails on it |
| `BG1215` | Low | verify_ac's fallback for a queued collection that raised is untested, so dropping it would read a live stamp as stale |
| `BG1218` | Low | A critic brief spends most of its 5 to 13 s in the per-unit affect-key parse, and a refused brief still renders before the self-check gate |
| `BG1219` | Low | migrate's dry run leaves its private bytecode directory behind when verify_ac's ceiling kills it, and BG1183 AC1 cannot pass verify_ac at its 120 s... |
| `BG1222` | Low | The hand-copied-list census runs only at the push gate and matches any three quoted .py names, fixture names included |
| `BG1225` | Low | An http loopback Cursor API base still goes through an http_proxy in cleartext with the key on it |
| `BG1230` | Low | lane return --agent: one agent priced onto two units, stale --tokens wording, and undocumented help |
| `BG1231` | Low | lane land: exit 1 documented too narrowly, two test gaps, a false --units help line, and an unscrubbed git environment |
| `BG1232` | Low | The lane brief's budget and hand-in: no-Points untested, one shared hand-in for a multi-unit lane, and US1093's stale story text |
| `BG1233` | Low | The Cursor hook ledger: mid-run creation or deletion misreads the run, deep nesting is fatal, and the text cut is untested |
| `BG1234` | Low | Small follow-ups from run six's approved bug fixes: BG1217, BG1220, BG1223, BG1224 and BG1227 |
| `BG1235` | Low | Run six's round-2 and lane accept follow-ups: an unfailing help pin, unpinned counts, and accept's late refusals |
| `BG1237` | Low | Orchestration frictions: batch add takes an id with no file, and a re-review's prior-finding notes parse as a blocking item |
| `BG1239` | Low | US0987's Copilot meter leaves its git-root-over-cwd preference unpinned and counts `includes_subagents: False` on trust |
| `BG1241` | Low | US1122's price table leaves ten defensive branches unpinned, promises a date format its parser does not hold to, and prices a bare `cost()` call wi... |
| `BG1243` | Low | US1124's cost anatomy leaves four rules unpinned: the per-component maximum, the CLI harness fallback and two role assignments |
| `BG1250` | Low | Fourteen `tools/tests` modules strip every `GIT_*` variable from a child's environment, dropping the conftest's `maintenance.auto` pin and reopenin... |
| `BG1251` | Low | Three lane frictions each cost a hand-fix: an in-flight warning per sibling lane on every brief, a hand-in fragment not linted before the commit, a... |
| `BG1253` | Low | lib/lanes.py clears only 7 of the 11 repo-locating git variables before it runs a lane |
| `BG1266` | Low | The dollar report and price table leave the run's end date, a signed table edit, the premium-request override and four price slots unpinned, and wo... |
| `BG1267` | Low | `sprint.py lane return` prints a two-model session's `lane run cost` at the largest model's rate, and BG1244's fragment misstates what the parser d... |
| `BG1269` | Low | `sprint plan` puts every unit in one shared-file cluster when they share a reference doc, so a collision in one code file is hidden and nothing kee... |
| `BG1270` | Low | The always-loaded instruction cuts leave their restored rules and their budget gate unpinned, and a keep-indicator description escapes the 600-char... |
| `BG1271` | Low | `sprint cost --anatomy` counts a call from the second the run opened that the opening reading already holds, reads a zero, negative or quoted start... |
| `BG1275` | Low | Two statements from run eight's last repairs claim more than the code or its tests show |
| `BG1276` | Low | The footprint counter splits Affects on every comma, so a path inside a bracketed note is dropped from the unit's file count |
| `BG1277` | Low | The close's closing-review row does not credit a unit carried at the review cap whose carrying bug was fixed and approved in the same run |
| `BG1282` | Low | `COPILOT_HOME` and `OPENCODE_DB`, user configuration variables, count as harness signals, so a Claude Code user who exports either gets no token re... |
| `BG1283` | Low | One old Codex thread whose rollout file is gone makes every later Codex reading in that workspace unmetered, permanently |
| `BG1284` | Low | Dollars per point omits the coverage its dollar figure has, and the Priced cost row's reach sentence uses Claude-transcript wording for every harness |
| `BG1285` | Low | A non-UTF-8 legacy OpenCode message file is refused as 'raised UnicodeDecodeError', and a Cursor cloud reading's stamps are given the wrong unprice... |
| `BG1286` | Low | `sprint lane land` leaves a timed-out commit's hook running while saying it was stopped, and reports a dirty worktree's rebase refusal as a conflict |
| `BG1287` | Low | Every lane brief's standing obligation hard-codes `main` and tells the builder to fast-forward, contradicting the same brief's 'do not commit' |
| `BG1292` | Low | `sprint lane brief` run in a builder worktree that is behind the root's branch prints the worktree's stale copy of the unit without a warning |
| `BG1293` | Low | A Codex lane that times out or prints no usage leaves no delegated record, and since BG1288 its worktree thread is left out of the reading, so its... |
| `BG1294` | Low | `sprint lane accept`'s stale-self-check refusal tells the operator to land the unit again, which `lane land` refuses after an out-of-band repair, a... |
| `BG1295` | Low | No test pins `lane accept`'s `off` and unrecognised `review.author_self_check` branches, so asking for the self-check gap under `off`, or reading a... |
| `BG1296` | Low | `sprint lane land` names a unit's brief and no-brief note by the unit id as typed, so `--units us0101` writes `us0101-qa.none` beside `US0101-qa.tx... |
| `BG1297` | Low | The 6.3.0 release-notes test checks the CLI against expectations typed into the test, not against the notes, so a notes sentence naming a wrong fla... |
| `BG1298` | Low | The TRD's path-row pin checks its depth rule in one direction only, so loosening `_matches` to accept the directory itself or a deeper file leaves... |
| `BG1299` | Low | A commit that changes sdlc-studio/trd.md selects 2 of the test modules that read it, so a broken spec sentence is first seen by the full suite at push |
| `BG1301` | Low | The release cut leaves this repository's own sdlc-studio/.version on the previous release, so `gate.py --release` refuses US0926::AC1 at every cut... |
| `BG1304` | Low | `artifact.py new` wraps a file name inside a path in backticks, so tools/tests/x.py in a CR's Impact or criteria is written as tools/tests/`x.py` |
| `BG1306` | Low | `critic.py brief` never tells a reviewer probing confinement or environment-isolation code to run its mutants with HOME set to a temporary director... |
| `BG1307` | Low | The shipped persona registry reader parses only the Primary, Secondary and Negative headings of `personas/index.md`, so a Served persona such as RF... |
| `BG1308` | Low | The product seat card's worked example names Maya Okafor as the shipped skill's Primary, which RFC0063 makes false once Abena Osei's card lands |
| `BG1309` | Low | A Cursor Composer or Grok session in Fast mode is priced at the standard rate, because the model id a reading carries cannot tell Fast from standard |
| `BG1311` | Low | `sprint.py lane land` removes the builder's worktree, so the builder cannot be resumed for a repair after a REJECT and a fresh builder must re-read... |
| `BG1313` | Low | The resume brief has three edges its tests do not pin: a batch listed out of plan order, a `-qa.none` landing marker read as in flight, and a Sprin... |
| `BG1314` | Low | Two US1146 persona checks cannot catch a swapped Primary, and `validate.py personas` compares the whole Interface cell, so a card reverted to Prima... |
| `BG1315` | Low | `help/sprint.md` still names a lane hand-in `<unit>-claims.json` under the id as typed, which BG1303's landing now keys by the normalised id, and `... |
| `BG1316` | Low | `sprint.py handoff` silently drops an `--agent` naming a unit outside the batch, both new verbs crash on an unreadable run state, and the next-step... |
| `BG1317` | Low | A Copilot `credit_usd` of 0 is accepted and prices every Copilot reading at $0, and reference-sprint.md's list of price sources omits the newer ones |
| `BG1319` | Low | Five Copilot model ids priced from the shared OpenAI entries stay token-priced under `pricing.copilot_billing: requests`, so a request-billed Copil... |
| `BG1321` | Low | Trevor Hale's Scenario check misses a capitalised offer and a negation outside its word list, so changelog.d/US1147.md claims more than the AC7 tes... |
| `BG1322` | Low | The commit-msg trailer check still refuses commit 089008d5's `Refs: US1090`, whose only record is a waiver row in decisions.md |
| `BG1323` | Low | The commit-msg hook misses git's scissors line under a non-default `core.commentChar`, the multi-id rule still reads trailers below it, and `_ledge... |
| `BG1324` | Low | No test replays a page filed before the Copilot billing basis existed, a mixed run's page drops the 'plan bills by request' reason, and US1145's la... |
| `BG1325` | Low | A hand-run mutation pass can leave a stale `.pyc` that Python reuses after the source is restored, so a later test run, the commit hook's among the... |
| `BG1326` | Low | `sprint.py handoff` writes a resume brief while a lane is still in flight, so the wave boundary reference-sprint.md defines is stated but not enfor... |
| `BG1327` | Low | A verdict file's `\;` escape, which the review brief prescribes for a semicolon inside a finding, still splits the finding when `critic.py record -... |
| `BG1328` | Low | `artifact.py new --type story --epic <a Done epic>` leaves the epic Done, so its parent request derives Complete although the new story is Draft, a... |
| `BG1335` | Low | sprint.py decision defer --block cannot mark a bug Blocked, so an autonomous run's blocked bug reads as an ordinary open unit |
| `BG1338` | Low | The lane brief does not tell a builder to fast-forward its worktree, and harness worktrees start at origin's commit, so builders build on a base mi... |
| `BG1342` | Low | sprint.py plan --write --format json prints its run-opening lines on stdout before the JSON |
| `BG1346` | Low | The first verdict recorded after the ledger gained its Source column pads every row, and the commit-msg hook credits that change to every unit the... |
| `BG1347` | Low | A second RULINGS: line in a verdict block is silently dropped |
| `BG1348` | Low | critic.py's 'none blocking' guard has no test |
| `BG1349` | Low | No test pins that a verdict file stays under --root inside a larger git repository |
| `BG1350` | Low | sprint_report._cited_record's run-archive branch has no test |
| `BG1351` | Low | US1149's tests have no fixture with two synthetic records in a row |
| `BG1352` | Low | US1013's in-order comparison of a verdict and its issued file has no pinning test |
| `BG1353` | Low | Two branches of US1016's rejoinder selection have no test |
| `BG1354` | Low | The close's re-close window_end wiring has no test |
| `BG1355` | Low | Four branches US1014's claims name have no test |
| `BG1356` | Low | US1000's AC2 test holds one read record per model, so replacing components across records survives |
| `BG1357` | Low | The report's Prices NOT MEASURED reasons and _run_usd's no-split guard are unpinned |
| `BG1358` | Low | US0997's changelog and reference-scripts.md say the close commits the run record, but it files it |
| `BG1359` | Low | help/sprint.md says the run record never names the plan by its .local path, but a run opened before 509850a1 still does |
| `BG1361` | Low | US1001's note says 'this clone's refusal log', which misleads in a fresh clone |
| `BG1363` | Low | The US1000 report's price rows cite the config while their values come from the page's own price table |
| `BG1364` | Low | fresh_session: no or false reads as off, though the help and US1149's AC2 say any other value reads as warn |
| `BG1365` | Low | sprint_report.py build of a signed run ignores the time window saved on its signed page |
| `BG1366` | Low | The verdict-file header check misses a byte order mark, a lower-case header or a leading prose line |
| `BG1367` | Low | The replay refusal tells a lane accept retry to re-brief when only the verify and the move are owed |
| `BG1368` | Low | After the rejecting reviewer's round-2 APPROVE, rebrief_notice names a bare --rejoinder that exits 2 |
| `BG1369` | Low | verify_ac's markdown-evidence lint matches the verdicts path as written, so reviews/../reviews/ and a symlink get through |
| `BG1370` | Low | A later rewrite of a verdict file is attributed to the reviewer when its last write was an Edit |
| `BG1375` | Low | US1015's run-state floor and its Write, MultiEdit, NotebookEdit, Read and Bash evidence cases have no tests |
| `BG1376` | Low | US1015's brief bound counts any round's issued path, not the round being recorded |
| `BG1377` | Low | The hooks' replay of a refusal's stderr is not pinned |
| `BG1378` | Low | US1134's AC3 skips markdownlint without saying so when the binary is missing |
| `BG1379` | Low | The report's Markdown twin still prints a `www.` or upper-case-scheme price source bare |
| `BG1380` | Low | BG1374's exclusion of a trailing comma or full stop from a linked address has no test |
| `BG1381` | Low | A price source URL whose path ends in a closing bracket loses that bracket from its link target |
| `BG1382` | Low | A nested run_verifier caller's own verifier can outlive it, because both levels wait the same one second grace and Ctrl-C leaks the inner verifier |
| `BG1383` | Low | Two more group-kill helpers duplicate verify_ac's, one closure in mutation.py and one in verify_ac._run_phase |
| `BG1384` | Low | The changelog's 6.3.0 text and the BG1112 fragment still over-state what the group kill does |
| `BG1385` | Low | This repo's own AGENTS.md lacks the template's 'Integrate continuously' line, so validate.py check warns here |
| `BG1386` | Low | Timing tests fail under parallel load: test_status GatherPerformanceTests read 4.9 s against a 3 s limit and a verify_ac criterion failed once at l... |
| `BG1387` | Low | test_cli_grammar RealTreeMarkerTests copies the whole tree into /tmp and fails with EDQUOT on a small tmpfs |
| `BG1388` | Low | An sdlc_md root-discovery test fails when TMPDIR is inside a repository, because it assumes its temporary directory lies outside any project |
| `BG1389` | Low | sdlc_md.extract_field reads an empty field on into the next line and returns '>', and two is_swallowed_run branches are unpinned |
| `BG1390` | Low | test_lean_tracked_run_record test_this_repos_signed_reports_check_in_a_clean_clone fails in a harness worktree |
| `BG1392` | Low | prices and token_meters have untested edges: `_rates()` falls back to an empty table, `_list`'s long-context pop, a true threshold read as 1, and `... |
| `BG1398` | Low | The tool-call budget in a multi-unit lane brief is printed once per unit and nothing states the lane's total |
| `BG1401` | Low | BG1190's unpinned reap and BG1262/BG1261's watchdog SIGKILL after its grace are covered by no test |
| `BG1402` | Low | The BG1333 integration rule counts as present if 'Integrate continuously' appears anywhere in AGENTS.md, so a sentence negating it passes |
| `BG1403` | Low | retro's new `supplied` guard and its `declined` list have no tests |
| `BG1404` | Low | critic.py record splits a verdict's ISSUES at every semicolon, so a semicolon inside one finding becomes an untagged finding and the record is refused |
| `BG1405` | Low | Nothing pins critic's 'live rows' filter, the carried-refusal wording or the stacked-criterion naming, and the BG1339 rejoinder path guards are unt... |
| `BG1408` | Low | sprint lane land's hook-refusal text and module docstring say the worktree and main are as they were, which is untrue after the replay, and _discar... |
| `BG1410` | Low | BG1330's re-pointed clean-run test lost its known-issues assertion, unpriced_units' filter is untested, and lane land with no run open names lane r... |
| `BG1411` | Low | The unpriced-gap remedy 'lane return --units <id> --agent A' cannot work after the close |
| `BG1412` | Low | templates/agents/sdlc-builder.md and its pinned .claude/agents copy still tell a builder to run verify_ac without --dry-run |
| `BG1414` | Low | The BG1262/BG1261 changelog headline is too broad, the help line reads as SIGTERM-first for every death of sprint.py, and lanes._reaping sends SIGK... |
| `BG1415` | Low | No test pins the line number verify_ac's lint prints |
| `BG1416` | Low | help/verify.md's exit-3 row in the revert-check table leaves out git failing to read the base blob |
| `BG1421` | Low | verify_ac's revert check reads a missing runner binary as red rather than as no verdict |
| `BG1422` | Low | No test pins verify_ac's class and module skip-mark check on the decorator's name |
| `BG1424` | Low | A bare sprint close runs its whole pre-flight report before scaffolding the retro, so the scaffold takes many minutes |
| `BG1427` | Low | file_finding.py --parent writes the parent's Decomposed-into but not its index row's spawned-work cell, so the next commit is refused for reconcile... |
| `BG1428` | Low | The per-unit dollars cell prices a unit's Grok agent read from a session total with no lower-bound label, and BG1391's changelog says the label hol... |
| `BG1429` | Low | A project Grok price entry with a lower long-context threshold is still booked at the shipped 200,000 threshold, so a long prompt is priced at the... |
| `BG1430` | Low | verify_ac's signal relay raises its running count outside the try, so a raise in that window leaves every later returning handler refused, and no t... |
| `BG1431` | Low | Two release-notes tests take 120 s to over 300 s under load, past verify_ac's default per-verifier timeout, so BG1420's and BG1425's recorded runs... |
| `BG1432` | Low | Three lane-pricing and re-close behaviours are pinned by no test: each split share's per-model split, the minutes split, and the lane-yield re-free... |
| `BG1433` | Low | The report templates still say the wall-clock span has no ratio, which is wrong on a page filed under the cost-forecast mark |
| `BG1434` | Low | The risk-class map reader drops an empty-prefix entry and a scalar risk value silently, and four refine stamping paths are pinned by no test |
| `BG1435` | Low | retitle leaves a reference-style link definition and a link in the project-root README dangling, while its changelog says it finds every link to th... |
| `BG1438` | Low | The evidence annex says fingerprint strings escape all control characters while the reference implementation escapes only U+0000 to U+001F, and it... |
| `BG1440` | Low | lane return --model with no total is dropped without a word, the model trim is untested, and help/sprint.md omits that a several-unit total is not... |
| `BG1443` | Low | Four cost-forecast behaviours are correct but unpinned, the Minutes row's reason reads 'not forecast: not measured', and US1151's criteria name a c... |
| `BG1444` | Low | sprint plan reports a malformed risk map as 'no component map is declared', says nothing when a unit's risk tag is outside the vocabulary, and no t... |
| `BG1446` | Low | Three second-seat behaviours are correct but unpinned: a story's risk tag read over its Affects, the brief's no-map default, and the first seat's l... |
| `BG1447` | Low | tools/check_budgets.py reports every file within budget while the pre-commit budgets lane fails the same tree on docgen drift |
| `BG1449` | Low | lane accept refuses to record a REJECT when the unit's self-check is stale, though a REJECT moves nothing |
| `BG1450` | Low | A reviewer's verdict file is refused by critic.py record over one code span with a leading space, and the review brief does not warn |
| `BG1451` | Low | The commit-msg hook refuses git commit --amend on a lane commit because it attributes only the newly staged files |
| `BG1453` | Low | file_finding keeps a placeholder id such as changelog.d/BGXXXX.md in Affects verbatim instead of substituting the minted id or refusing it |
| `BG1454` | Low | sprint lane return --agent agent-<id> leaves the unit unpriced, while lane land prints the builder as agent-<id> |
| `BG1456` | Low | The escaped-bug Fixed gate's scaffold stripping is untested and matches the scaffold by exact string, and test_file_finding's selector reader test... |
| `BG1457` | Low | The seat record reads any bracketed word as a seat, lane brief --seat accepts any value, and retro seats counts rounds across deliveries |
| `BG1458` | Low | escape.py to-class records a class with no files for a hand-edited bug with no Affects, collapses whitespace inside Affects paths, and the catalogu... |
| `BG1461` | Low | lane brief warns a landed unit under review never returned, and that the tree may already carry its work |
| `BG1462` | Low | lane accept records under the self-check's agent author and critic.py record then warns that author lacks the holder (role) form |
| `BG1464` | Low | retro.py's own-finding check matches a review word anywhere in Evidence and two of its guards have no test |
| `BG1466` | Low | A signed report's signoff principal and signed_at figures still read not yet signed, though the evidence schema says they hold who signed and when |
| `BG1467` | Low | A review-cap carry bug copies the carried unit's Affects verbatim, so it declares the unit's changelog fragment, not its own |
| `BG1473` | Low | A damaged tracked run record reads on the brief as awaits its run's signature, not as damaged |
| `BG1476` | Low | file_finding stamps Raised-in-batch as none open for a finding filed while a run is open |
| `BG1481` | Low | test_support_page lets four planted SUPPORT.md defects through: a gh skills install line, an install command in prose, and Stack Overflow or IRC na... |
| `BG1485` | Low | A shell Verify line run with -s still reads all-skipped and no-tests shapes from its whole output, and a partial-skip test's docstring still says t... |
| `BG1486` | Low | US1157's AC1 names a file_finding.py bug verb that does not exist, so the plan's registry advice reads it as a new verb |
| `BG1488` | Low | reference-outputs.md still calls Deferred a story terminal status at lines 134, 745 and 755, against its own Story row and sdlc_md.TERMINAL_STATUS |
| `BG1490` | Low | test_critic_rejoinder_from_ledger and test_critic_verdict_file_binding fail when run inside an agent session, because the harness session id reache... |
| `BG1495` | Low | sprint plan warns a wave is not safely parallel when its units share no file, because the cluster joins them through a unit in a later wave |
| `BG1496` | Low | BG1487's README-opening guard lets a reworded approval claim through, though its docstring says it never would |
| `BG1497` | Low | Two config keys the code reads are undocumented: sprint.fresh_session is missing from reference-config.md and pricing.copilot_billing from config-d... |
| `BG1499` | Low | US1058 still reads Status Ready though run thirteen carried it at the review cap and BG1460 delivered it, and the PRD row naming it says Complete |
| `BG1500` | Low | help/retro.md says an escaped defect is charged to the seat whose latest verdict approved, in any run, leaving out the code's limit to verdicts on... |
| `BG1502` | Low | critic.py self-check record refuses a unit until it claims its changelog.d fragment, though the release cut has already merged that fragment into C... |
| `BG1504` | Low | The sdlc-builder agent card does not confine a builder's clean-up to paths it created, so a builder deleted every tmp.* directory in the shared tes... |
| `BG1505` | Low | 6.4.0's CHANGELOG says a fragment that opens with a list item folds byte for byte, but compose bullets an ordered item, and no test pins a later li... |
| `BG0948` | Medium | A migrating project cannot baseline pre-existing placeholder findings, and v3 ids can never be baselined |
| `BG0949` | Medium | An inline `ruled:` or `decided:` ruling is never recognised - `_RULING_RE` puts a word boundary after the colon |
| `BG0954` | Medium | A Draft story transitions straight to Done - the Definition of Ready is never required |
| `BG0956` | Medium | transition set reports index synced but leaves archived index rows stale, and reconcile apply refuses them |
| `BG0957` | Medium | `test_epic_index_derived`'s negative control needs a live epic row with a count, so an archive that empties the live epic index turns it red |
| `BG0959` | Medium | The engagement floor rejects a ULID adopt_after cutoff and tells you to set a sequential one |
| `BG0961` | Medium | A Verify line cannot name the skill: <skill> is a shell redirect, not a path |
| `BG0967` | Medium | The finding filer backtick-wraps identifiers inside Steps to Reproduce, corrupting the shell commands a repro depends on |
| `BG0968` | Medium | CI runs tools/tests in the same step as the skill suite, so a red skill suite hides every tools/tests failure |
| `BG0970` | Medium | `critic.py brief` says nothing when the unit's Affects carry uncommitted changes, though it sends the reviewer to an isolated worktree that cannot... |
| `BG0981` | Medium | breakdown and plan call a unit groomed when a Verify line is one verify_ac cannot parse |
| `BG0982` | Medium | critic brief's diff scope is the unit's Affects only - files the unit changed but did not declare are invisible to the reviewer |
| `BG0983` | Medium | `review_coverage` and `verdict_for` read a unit's whole per-unit ledger, so an APPROVE from an earlier delivery covers a re-delivered unit that nob... |
| `BG0985` | Medium | sprint close --dry-run reports a non-blocking pre-flight row as a STOP refusal and exits 1, so a close that would proceed previews as refused |
| `BG0986` | Medium | `tools/forward-port.sh` deletes the CHANGELOG.md the installer ships into the skill, so `project upgrade` loses its changelog digest after every fo... |
| `BG0987` | Medium | The close's goal judgement reaches only the terminal, not the sprint report the signer is told to read, and says 'blocks the close' of defects that... |
| `BG0995` | Medium | refine leaves the bold **ACn** label in seeded AC headings, so a request written by the skill's own filer seeds '### AC1: **AC1** ...' (BG0291 inco... |
| `BG0997` | Medium | A per-unit engagement-floor waiver pasted with the dashed v3 id does not waive the unit |
| `BG0999` | Medium | Caller-check cannot resolve a skill script named as the consumer |
| `BG1002` | Medium | goal-review brief ignores the plan's --serves and the batch changes made after plan --write |
| `BG1012` | Medium | The sprint checklist reads a run only from .local, so in any other clone a signed run's rows read 'no run record could be read' |
| `BG1015` | Medium | persona_resolve.py resolve refuses a seat role the project declares (sre), though validate seats and critic.py brief accept it |
| `BG1021` | Medium | A CR declared Size L is not flagged for decomposition |
| `BG1023` | Medium | verify_ac's vitest and jest verbs fold the whole tail into the -t pattern and call a bare binary, so `vitest <file> -t "name"` can never select its... |
| `BG1027` | Medium | The commit-time links lane resolves a link against the working tree, so a staged index row linking to an untracked file passes the commit and turns... |
| `BG1050` | Medium | A reviewer id carrying a carriage return or line separator tears its own verdict row |
| `BG1051` | Medium | The close's chain report cuts every refusal line at 160 characters, hiding which unit is blocked and why |
| `BG1058` | Medium | The close's dry run names a unit the run cannot end over that the real tree answers |
| `BG1059` | Medium | A retro's Batch field is never compared with the run's batch, so a unit added after the retro was scaffolded is left out of the run's measurement a... |
| `BG1060` | Medium | retro extract starts a new project lessons log when the committed one is missing, though the committed digest lists the lessons that log holds |
| `BG1063` | Medium | `require_ac_verification` is documented as a gate that aborts the completion cascade on a failed verification, but no code reads it |
| `BG1101` | Medium | test_repo_hygiene writes probe fixtures into the real scripts/tests directory, so a parallel test copying that tree can fail |
| `BG1107` | Medium | sprint._end_goals keeps only the first line of a wrapped End goal, so the goal-review brief and the goal trace show Rowan's goals cut off mid-sentence |
| `BG1108` | Medium | A carried unit whose repair landed before the new run's base has an empty review diff, so its redelivery review cannot block |
| `BG1120` | Medium | A self-check record reads an author's own edit made in a merge commit as another unit's, so the brief gate admits a changed diff in a project that... |
| `BG1124` | Medium | critic.py brief's practice and claim-inventory refusals read the whole brief, so the unit diff US1094 embeds can satisfy them, and a unit whose own... |
| `BG1125` | Medium | The review brief's unit diff is the whole run's diff over the unit's files, not the unit's own change, so on a shared file the 400-line cap is spen... |
| `BG1229` | Medium | critic.py's self-check and verdict records refuse shapes authors and reviewers write naturally, and record has no dry run |
| `BG1256` | Medium | test_lane_run.py runs git unconfined through a local name and inside its fake CLI script, where the unconfined-git sweep cannot see it |
| `BG1265` | Medium | Reviewers' throwaway copies of the repository are never removed and carry no history, so they fill the temp quota and fail history-dependent tests... |
| `BG1272` | Medium | The pre-push check reads only the latest Lint run, so a push made while the previous run is still in progress never sees it fail |
| `BG1310` | Medium | `tools/skill-tests.sh`, the unittest runner `npm test` uses, loads no conftest, so the harness-variable scrub BG1197 added never runs there and the... |
| `BG1332` | Medium | No command writes a retro's 'Known issues carried' rows, so the orchestrator types them by hand and run nine's two late rows landed outside the table |
| `BG1373` | Medium | A NUL byte in a transcript's file path makes critic.py record refuse the unit |
| `BG1399` | Medium | lane land commits and lands the code, then refuses a self-check missing a required surface, when the builder can no longer be resumed |
| `BG1400` | Medium | lane accept takes --reviewer as free text, so a carried unit's re-review under the wrong id strands an APPROVE that only an operator supersession r... |
| `BG1406` | Medium | lane run accepts a home-isolated unit and hands its worktree builder the main-checkout brief, and 'Isolation: no home' reads as home |
| `BG1407` | Medium | A builder's mutation probe in a scratch copy of the tests runs without the repo-root conftest.py, so without HOME confinement |
| `BG1409` | Medium | lane land's rebase uses --empty=keep --reapply-cherry-picks, so a commit a builder made that main already holds becomes an empty commit |
| `BG1413` | Medium | A Ctrl-C during lane run's 2 s kill grace drops the SIGKILL that follows, so a SIGTERM-ignoring child stages after the run, and nothing pins that S... |
| `BG1417` | Medium | CI's lint.yml sets up Node 20 while markdownlint-cli and markdownlint declare node >=22, so the gap is invisible until a dependency uses a Node 22 API |
| `BG1436` | Medium | A lesson class recorded with no run open retires at the next close in a clone with more than the quiet-run count of archived runs, from class-add a... |
| `BG1448` | Medium | lane land spends its full hook run before a rebase conflict, and a replayed generated page merges into drift |
| `BG1452` | Medium | reconcile derives a request Complete when every child of a partial refine resolves, though its unrefined criteria are undelivered |
| `BG1455` | Medium | escape.py trace counts a Mentions: trailer id as a unit the release shipped, so a commit that only names a unit puts it among the suspects |
| `BG1463` | Medium | retro.py seats drops an Escaped-via bug silently when its unit's approval names no seat, has only a REJECT, or post-dates the bug |
| `BG1465` | Medium | retro.py seat_misses reads each cited unit's file uncached, so an unbounded window does not finish in ten minutes |
| `BG1470` | Medium | lane land runs the full commit hooks, then refuses the rebase over an unstaged author-self-checks.md the builder's self-check left in the worktree |
| `BG1472` | Medium | Five branches of the close's learning review and the sign's strike are right by execution but no test fails without them |
| `BG1475` | Medium | sprint close --dry-run takes about half an hour and prints nothing until it ends, mostly one git log per artefact in the review-current check |
| `BG1477` | Medium | lane accept --agent on a multi-unit lane charges the builder's whole transcript to each unit, overriding the land's split by points |
| `BG1482` | Medium | A build-injected lesson class can no longer retire, so once more than INJECT_MAX build classes are live the digest cap drops the oldest builder traps |
| `BG1483` | Medium | A run's repeat of a lesson class is counted only from a cited REJECT or retro Try item, so a repeat caught by the land or the push gate goes unreco... |
| `BG1491` | Medium | lane accept on an APPROVE prints that the unit moved to Fixed and then that its return is blocked, when one criterion has no Verify line |
| `BG1492` | Medium | Nothing stops the orchestrator committing a reviewer's half-written verdict: git add of the records sweeps in a verdict file still being written |

369 findings: 65 Medium, 304 Low.

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
