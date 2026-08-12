# The sprint toolchain, by step

`reference-scripts.md` is the catalogue: it is ordered by script and answers "what does X do".
Nobody planning a sprint has that question. The question at each step is **"what is the next
thing, and which command performs it"** - and answering that from memory is where hand-rolling
comes from. Every entry below therefore names the step, the one command, and **the hand-rolled
shape it replaces**, so the entry is findable from the wrong instinct as well as the right one.

Read this at plan time. `sprint plan` prints it.

## 1. Orient

| Do | Command | Instead of |
| --- | --- | --- |
| Read what the last run left owed | `cat sdlc-studio/reviews/LATEST.md` | guessing from git log |
| Pipeline state and next step | `status.py` | counting artefacts by hand |
| How much is left, in points | `status.py points` | writing a census script on the spot |
| Cross-project lessons | `lessons.py summary` | recalling them after the decision |

## 2. Groom and plan

| Do | Command | Instead of |
| --- | --- | --- |
| Turn a CR/RFC into deliverable units | `refine.py apply --request <id> --breakdown <file>` | hand-creating epics and stories |
| Check a batch is plannable | `sprint.py breakdown --stories Ready --bugs Open` | reading each file for `Affects` and `Points` |
| Review the sprint goal with the seats | `sprint.py goal-review record --goal ... --seat ...` | asserting the goal is achievable |
| Open the run | `sprint.py plan --worklist <file> --write --sprint-goal ...` | picking units by eye |

## 3. Deliver a unit

| Do | Command | Instead of |
| --- | --- | --- |
| Allocate an id | `next_id.py allocate --type <type>` | reading `_index.md` for the highest |
| Create an artefact | `artifact.py new --type <t> --fields-file <doc>` | writing the markdown by hand |
| Run the criteria | `verify_ac.py run --id <id>` | claiming they pass |
| Run a suite | `tools/run-suite.sh all` | `npm test \| tail`, which reports tail's exit code |
| Confirm the suite verdict | `tools/run-suite.sh --check` | trusting a remembered green |
| Mutation-check a guard | `mutation.py run --story <id> --test <cmd>` | a hand-rolled mutate/restore loop |
| Change status | `transition.py set <id> <status>` | editing the Status line |

## 4. Review a unit

| Do | Command | Instead of |
| --- | --- | --- |
| Brief a seat | `critic.py brief --unit <id> --seat engineering\|product\|qa` | writing the review prompt yourself |
| Resolve who reviews and who signs | `persona_resolve.py panel` | choosing seats by judgement |
| Record the adversarial pass | `critic.py evidence --unit <id> --findings ...` | leaving the pass in a transcript |
| Record the verdict | `critic.py record --unit <id> --verdict ... --brief <fingerprint>` | a verdict with no provenance |
| Record a batch pass | `sprint.py review-batch --units ... --fields-file <doc>` | findings mangled by the shell |
| Answer a REJECT once its findings are repaired | `critic.py repair --unit <id> --author <who> --closed-file <doc>` | a repaired batch that still reads as unreviewed |
| Find library-only verifiers | `verify_ac.py lane-check` | discovering it in review |

## 5. Close

| Do | Command | Instead of |
| --- | --- | --- |
| See every refusal at once | `sprint.py close --dry-run` | fixing one blocker per attempt |
| Scaffold the retro | `artifact.py new --type retro` | hand-mirroring the template |
| Check the retro is complete | `retro.py validate --id <id>` | reading it over |
| Record estimate versus actual | `retro.py accuracy --id <id> --write` | leaving the cost unmeasured |
| Lift the retro's lessons | `retro.py extract --id <id>` | letting a lesson die in one document |
| Refresh what the next sprint reads | `lessons.py summary` | a digest that no longer matches the log |
| Record the adversarial pass | `critic.py evidence --unit <id> --reviewer <seat>` | a review that exists only in a transcript |
| Record the reviewer of record | `critic.py signoff --units <ids> --principal <who>` | claiming a unit is signed |
| Say where a closed unit's work went | `transition.py annotate --id <id> --field "Closed with findings in"` | leaving the reader to hunt the retro |
| Close | `sprint.py close --retro <id> --apply-signoff --principal <who>` | transitioning units by hand |
| End a run that will not reach its goal | `sprint.py stop --reason <why>` | abandoning it and opening a fresh one |
| Write the handoff | `handoff.py generate --title <t>` | prose about what is left |
| Discharge the close-owed ledger | `gate.py --require-retro <id>` | an advisory nobody clears |
| Re-baseline what a retro accounts for | `close_owed.py baseline --note <why>` | a ledger that never returns to zero |
| Take the backlog census | `status.py points` | counting artefacts by hand |
| Mirror to the installed copy | `bash tools/forward-port.sh --yes` | `install.sh`, which clobbers the tree |

## 6. Release

| Do | Command | Instead of |
| --- | --- | --- |
| Compose the changelog section | `release_cut.py changelog-cut --version <v>` | hand-merging fragments |
| Stamp the commit the gate passed on | `release_cut.py record-green --commit <sha>` | tagging on a green nobody recorded |
| Refuse a tag the gate never covered | `release_cut.py tag-check --version <v>` | tagging on memory |
| Publish the release and its artefacts | your project's release automation, triggered by the tag | a hand-uploaded artefact, which is the step that gets skipped |

Make the publish step something the tag triggers, not a line somebody runs. Where a project offers
a verified install, the checksum a user verifies against is published by that step, so a release
that skips it leaves the documented verification broken while everything else looks fine. Two
releases shipped that way here before it was automated - one with no artefacts attached, one with
no release entry at all - and both were somebody meaning to and not doing it. The second case is
the quieter one: `skill-update` asks the forge for the LATEST RELEASE, so until the release entry
exists, every installed copy still reports the previous version and prompts nobody to upgrade. A
tag without a release is, to the update mechanism, unreleased.

## In-flight: changing a run that is already open

| Do | Command | Instead of |
| --- | --- | --- |
| Trade units | `sprint.py batch swap --out <ids> --in <ids> --reason <why>` | a drop that happens to sit beside an add |
| Pull a unit from the batch | `sprint.py batch drop <id> --reason <why>` | `Deferred`, which leaves it gated |
| Add an epic's stories as one priced set | `sprint.py batch add-epic --epic <id> --status Ready` | adding them one at a time |
| Raise the ceiling on the record | `sprint.py appetite resize --units <n> --reason <why>` | overrunning silently |
| Review at the batch boundary | `sprint.py review-batch --open <ids>` | queueing every review to the close |

Review at the BOUNDARY, not at the close. A batch reviewed where it was built makes a finding
delivery work in the batch that caused it; the same finding found at the close is close
overhead, and by then the repair means reopening work believed finished.

## When a command is missing

If a step here has no command, that is a finding, not an invitation to hand-roll it. File it
(`file_finding.py file --type cr --fields-file <doc>`) and say what you had to do instead.
