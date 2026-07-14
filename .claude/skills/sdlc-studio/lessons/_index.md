# Cross-Project Lessons-Learned Registry

Generalisable engineering/process lessons that improve decisions on **any**
sdlc-studio project. Lives **in the skill** (shared across projects), distinct
from a project's own `.local/lessons.md` (transient agentic-wave failure memory)
and from per-project memory (project-specific facts).

> **Recall** relevant lessons before substantive decisions (`/sdlc-studio lessons recall`).
> **Promote** a lesson here (`/sdlc-studio lessons add --global`) only once it clearly
> generalises beyond the project that surfaced it. Keep entries tight.

## All Lessons

| ID | Title | Tags |
| --- | --- | --- |
| [LL0001](LL0001-reconcile-from-file-census.md) | Reconcile from a file census, not from the existing counts | reconcile, indexes, drift |
| [LL0002](LL0002-cross-repo-artifact-number-collisions.md) | Cross-repo artifact-number collisions (shared CR/RFC namespace) | cross-repo, numbering |
| [LL0003](LL0003-config-schema-vs-type-alignment.md) | Config-schema vs type alignment – strict validators strip unknown fields | schema, validation, bug-class |
| [LL0004](LL0004-ship-paperwork-in-the-same-commit.md) | Ship the paperwork in the same commit as the code | process, docs, release |
| [LL0005](LL0005-full-review-set-includes-a-code-leg.md) | The between-releases review set must include a CODE leg | review, release, quality |
| [LL0006](LL0006-deploy-meta-files-gap-class.md) | Deploy meta-files gap – new boot-read file → every deploy path | deploy, packaging, gap-class |
| [LL0007](LL0007-plan-from-value-not-bare-priority-a-ready-story-whose-verifiers-pass-is-already-done.md) | Plan from value, not bare priority; a Ready story whose verifiers pass is already done | sprint, planning, wsjf, personas, conformance |
| [LL0008](LL0008-a-deterministic-tool-must-fail-loud-never-report-success-it-did-not-achieve.md) | A deterministic tool must fail loud, never report success it did not achieve | tooling, determinism, false-green, mis-report, bug-class |
| [LL0009](LL0009-silent-misleading-failure-outranks-loud-failure-of-the-same-scope.md) | Silent misleading failure outranks loud failure of the same scope | severity, triage, silent-failure, review, bug-class |
| [LL0010](LL0010-validate-a-defence-using-the-bug-it-defends-against-before-shipping-it.md) | Validate a defence using the bug it defends against, before shipping it | quality-gate, defence, testing, process, bug-class |
| [LL0011](LL0011-a-gate-that-fails-on-ci-but-passes-locally-is-an-environment-gap-until-proven-otherwise.md) | A gate that fails on CI but passes locally is an environment gap until proven otherwise | ci, debugging, environment, fail-loud |
| [LL0012](LL0012-a-new-private-helper-that-shadows-a-module-level-name-silently-breaks-every-existing-caller.md) | A new private helper that shadows a module-level name silently breaks every existing caller | python, refactoring, naming, testing |
| [LL0013](LL0013-an-ac-that-enumerates-the-paths-it-checks-silently-exempts-the-path-it-forgot.md) | An AC that enumerates the paths it checks silently exempts the path it forgot | acceptance-criteria, testing, false-green, bug-class |
| [LL0014](LL0014-a-mocked-boundary-tests-the-code-on-your-side-of-it-and-nothing-else.md) | A mocked boundary tests the code on your side of it, and nothing else | testing, mocking, coverage, false-green |
| [LL0015](LL0015-a-guard-that-only-catches-the-total-case-is-not-a-guard.md) | A guard that only catches the total case is not a guard | defence, data-loss, bug-class, review |
| [LL0016](LL0016-when-two-code-paths-build-the-same-artefact-they-must-agree-on-what-it-means.md) | When two code paths build the same artefact, they must agree on what it MEANS | consistency, data-loss, bug-class, architecture |
| [LL0017](LL0017-a-function-that-only-ever-appears-inside-patch-is-untested-however-many-tests-cover-it.md) | A function that only ever appears inside patch() is untested, however many tests cover it | testing, mocking, coverage, false-green, bug-class |
| [LL0018](LL0018-it-failed-and-it-did-not-run-are-different-questions-a-retry-loop-that-conflates-them-never-converges.md) | 'It failed' and 'it did not run' are different questions; a retry loop that conflates them never converges | retry, idempotence, status, bug-class, convergence |
| [LL0019](LL0019-except-exception-does-not-catch-a-cancellation-a-lock-released-only-there-leaks-on-every-shutdown.md) | except Exception does not catch a cancellation - a lock released only there leaks on every shutdown | asyncio, python, shutdown, locks, bug-class |
| [LL0020](LL0020-a-test-fixture-that-supplies-the-thing-under-test-proves-nothing-about-production.md) | A test fixture that supplies the thing under test proves nothing about production | testing, fixtures, observability, false-green, bug-class |
| [LL0021](LL0021-verify-a-deploy-by-looking-at-the-running-system-not-by-re-reading-the-green-build.md) | Verify a deploy by looking at the running system, not by re-reading the green build | deploy, verification, observability, process |
| [LL0022](LL0022-a-guard-that-branches-on-invocation-mode-must-be-tested-in-every-invocation-mode.md) | A guard that branches on invocation mode must be tested in every invocation mode | testing, false-green, shell, bug-class, silent-failure |
| [LL0023](LL0023-a-gate-that-checks-an-artefact-exists-not-what-is-in-it-is-satisfied-by-touch.md) | A gate that checks an artefact exists, not what is in it, is satisfied by touch | gate, false-green, ceremony, bug-class, silent-failure, process |
| [LL0024](LL0024-a-tool-that-silently-rewrites-its-caller-s-input-is-indistinguishable-from-one-that-corrupts-it.md) | A hazard found by calling a private helper directly may already be guarded at the only call site that matters | testing, false-positive, review, tooling, bug-class, humility |

## Notes

- IDs are global and zero-padded: `LL{NNNN}`. Files: `LL{NNNN}-{slug}.md`.
- A lesson = **generalisable** wisdom (what to do differently next time, anywhere). A project fact (a config path, an incident, a box name) is **memory**, not a lesson.
- This folder ships with the skill, so the seed set is release-curatable. An addition reaches the next release exactly one way: `lessons add --global` writes it into the skill **source checkout** (`skill_source_repo` in the project's `.config.yaml`), and someone commits it there. There is no other blessing path - and a write into an installed copy is refused, not silently lost, because a skill update replaces that folder wholesale.
- Format: see `_template.md`. Mechanism + recall/promote hooks: `help/lessons.md` + `reference-agentic-lessons.md`.
