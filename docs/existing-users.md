# SDLC Studio v4 for existing projects

You already run SDLC Studio on a project and want to know what v4 changes, what it
asks you, and what it will never do without asking. This page is the whole answer;
the [README](../README.md) stays focused on newcomers.

**The one-line summary: nothing about your running project changes until you say so.**
v4 is a drop-in skill update - existing `sdlc-studio/` directories keep working,
sequential ids stay valid, and every new behaviour that affects your artifacts arrives
as an explicit question, never a silent switch.

## What v4 changes

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

```bash
# 1. Update the skill itself (drop-in; no project migration happens here)
/sdlc-studio skill-update          # or re-run the installer

# 2. Walk your project through the upgrade (asks the numbering question,
#    offers the generated team, reports every change before applying)
/sdlc-studio project upgrade       # add --apply when you accept the plan

# 3. Reconcile, so the census confirms the state
/sdlc-studio reconcile
```

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
