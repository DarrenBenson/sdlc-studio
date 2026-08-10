# SDLC Studio v5 for existing projects

You already run SDLC Studio on a project and want to know what v5 changes, what it
asks you, and what it will refuse until you act. This page is the whole answer; the
[README](../README.md) stays focused on newcomers.

**The one-line summary: your artifacts are safe, but two gates will refuse work on
day one until you clear them.** Nothing rewrites your files without asking, sequential
ids stay valid, and every change to your *artifacts* still arrives as an explicit
question. What is NOT a drop-in is the gate: `sprint plan` refuses a backlog that
predates the sizing fields, and `gate.py` fails on a history that predates the
conformance rule. Both have a one-line remedy, both are below, and the upgrade steps in
this page are executed against a fixture on every boundary gate run - so if they stop
working, this page reddens a build rather than misleading you.

## What v5 refuses on day one, and how to clear it

| Gate | What it does on an upgraded project | Remedy |
| --- | --- | --- |
| `sprint.breakdown` (default `enforce`) | `sprint plan` refuses any batch holding a unit with no `Affects` or `Points`. Your existing backlog predates both fields, so this fires on the first plan. | Groom the units you are about to plan (`sprint breakdown --stories Ready --bugs Open` lists them), or record `sprint.breakdown: judgement` in `sdlc-studio/.config.yaml` as a deliberate decision. Omission is not an escape - an absent config blocks. |
| `conformance.adopt_after` (default unset) | Unset judges EVERY story you have ever written, so `gate.py` fails on history written before the rule existed. | Set `conformance: { adopt_after: US0123 }` to the last id of your pre-v5 era. Ids at or below it are reported `exempt (pre-adoption)` and the gate judges forward only. |
| `plan_review.enabled` (unset; schema v3) | An independent review of a story's acceptance criteria before it is implemented. Fires on most units. | Nothing to do on an upgrade: it already applied in v4. A project that has never closed a sprint gets a report instead of a refusal for its first run only. |
| `review.two_role_after` (unset) | Dormant. Set it to a date to require adversarial evidence plus an independent sign-off before Done. | Opt in when you want it; an unset value changes nothing. |
| `review.test_plan_after` (unset) | Dormant, same shape. | Opt in when you want it. |

The last three are listed because operators ask; only the first two change what your
project is held to the moment you upgrade.

## What v5 inherits from v4

| Area | What is new | Affects you when |
| --- | --- | --- |
| Artifact identity | New projects mint collision-free ULID ids (`US-01JQK3F8`) instead of sequential (`US0001`), so concurrent humans and agents never clash | Only if you opt in via `project upgrade` |
| The team | `persona generate --team` grows fresh named working seats from your project; the shipped Dani/Sam/Lena become the zero-setup fallback | Offered at `project upgrade` and after a PRD; never auto-run |
| Default amigos | The upgrade no longer auto-installs the default amigo cards; they are opt-in (`--with-default-amigos`), and legacy `personas/amigos/` cards migrate to `personas/seats/` | On your next `project upgrade` |
| Quality floor | Independence gate (author can never be reviewer), verification-depth tiers, portable CI gate (`gate.py`), provenance-stamped generated personas | Immediately, but only on new work - nothing retro-fails |
| Reviews | Repository audit (`audit --profile repo`), stakeholder panels with declared types, consult objection quota | As you use them |
| Renames | `autosprint` is now `sprint` (old name kept as an alias) | Muscle memory only |

## The numbering question - three answers, all supported

When you run `project upgrade` on a v3-or-earlier project, it asks you explicitly how
to handle identity. There is no default that rewrites anything:

1. **Migrate everything** (`migrate_v3 apply --confirm`) - every artifact gets a ULID;
   old sequential ids are kept as aliases, so links and tickets keep resolving.
2. **Adopt forward-only** (`migrate_v3 adopt --confirm`) - the recommended path for a
   living project. Existing ids stay exactly as they are (still valid in tickets, chat,
   and docs); only NEW artifacts mint ULIDs. The two eras coexist by design and nothing
   is renamed.
3. **Stay sequential** - decline, and the project keeps sequential numbering entirely.
   You can revisit at any later upgrade.

Both migration commands refuse to run without `--confirm`, and refuse to touch a
directory that is not an sdlc-studio workspace. If your clones disagree (one machine
upgraded, another not), `reconcile` raises an era-divergence advisory rather than
letting two writers mint in different modes silently.

## Upgrade steps

These are the steps the release rehearsal executes against a v4-era fixture on every
boundary gate run. They are parsed out of this block, so a step that stops working here
fails a build rather than misleading a reader.

```bash
migrate.py --apply
gate.py
```

`migrate` is the orchestrator: it runs `project upgrade` (conventions and version),
`migrate_v3 sizing` (a container's legacy `Effort` to a T-shirt `Size`) and the
artefact-review sweep, then reports what it upgraded deterministically and what needs a
human. It auto-applies only the reversible set and never guesses a judgement - a
request's breakdown, an Issue's triage and a unit's re-size are REPORTED with the exact
command, never done for you.

Then `gate.py`. Expect it to FAIL the first time, on `conformance`, `reconcile` and
`index-derived`. That is the honest state of the upgrade path today and it is recorded
in `tools/release-rehearsal-baseline.txt` with the artefact that will close it. Set
`conformance.adopt_after` and run `reconcile apply`, and it goes green.

`project upgrade` without `--apply` is a report: it lists what would change (including
a `team-offer` entry and any legacy amigo cards that would migrate to `seats/`) and
applies nothing. The installer also refuses to downgrade a newer installed copy unless
you pass `--allow-downgrade`.

## Meeting the generated team on an existing project

`persona generate --team` is offered, never run for you. On a brownfield project it
works from the repo map alone (no PRD needed), asks at most four multi-choice
questions, and **never overwrites a card you authored or edited** - authored and
generated cards are discriminated by a provenance stamp plus a content hash, so your
edit promotes a card to authored and re-runs propose diffs instead of clobbering.
Generated cards stay labelled provisional-unverified until you review and accept them
(`persona review`); `status` counts the unreviewed ones so the label cannot silently
linger.

## Developing or testing the skill itself

- **Try a local working tree** without touching your global install:
  `./install.sh --from <dir> --target claude` installs from a directory instead of the
  frozen release, under the same identity and downgrade guards.
- **Check what changed since your version:** `project upgrade` reports the capability
  delta; [CHANGELOG.md](../CHANGELOG.md) carries the full history.
- **Run the repo's own gate** before contributing: `npm run lint` and `npm test`, or
  the plain Python/bash equivalents listed in [AGENTS.md](../AGENTS.md) - the
  pre-commit hook (`bash tools/enable-hooks.sh`) runs all of it on every commit.

## Breaking-change honesty

- `autosprint` -> `sprint` (alias kept).
- Default amigo cards are no longer auto-installed at upgrade; they are opt-in, and
  the generated team is offered first. Existing cards are never deleted; legacy
  `personas/amigos/` cards are migrated to `personas/seats/` with their role declared,
  never overwriting a seat that already exists.
- New projects default to `schema_version: 3` (ULIDs). Existing projects are never
  auto-switched - see the numbering question above.
- Nothing else in v4 removes or renames a command; if you find a behaviour this page
  does not prepare you for, that is a bug - please file it.
