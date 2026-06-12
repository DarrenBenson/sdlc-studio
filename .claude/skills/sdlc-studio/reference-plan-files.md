# Plan-File Lifecycle Reference

<!-- Load when: entering plan mode and an existing plan file is offered, when an old plan file slug is unfamiliar, or when the operator asks "what plans are open" -->

Claude Code's plan-mode persists each plan as a single file in `~/.claude/plans/`. Files are kebab-case-slugged (auto-generated from the plan content) and there is **one file per task**. Plan mode does not introduce a directory of plans for the operator to navigate; it always points at the most-recently-edited slug.

This file documents the discipline for managing those plan files so a follow-up plan-mode session can:

1. Tell at a glance whether the existing plan is the same task or a different one.
2. Decide cleanly between "continue the existing plan" vs "overwrite with a fresh plan".
3. Find prior plans without searching.

---

## File layout

```
~/.claude/plans/
├── <active-slug>.md            ← whichever plan was edited most recently
├── <other-active-slug>.md      ← any plan still relevant
└── archive/
    └── <yyyy-mm>/
        └── <archived-slug>.md  ← retired plans, grouped by month
```

There is no central index. The slugs themselves carry the topic (kebab-case, generated from the plan's first heading).

## States

| State | Where it lives | When |
| --- | --- | --- |
| Active | `~/.claude/plans/<slug>.md` | The plan is for ongoing work. Either currently being executed, or paused awaiting a decision. |
| Archived | `~/.claude/plans/archive/<yyyy-mm>/<slug>.md` | Work shipped, was abandoned, or has been superseded by a newer plan. The file is kept for historical reference but not surfaced in plan-mode pickup. |

Plans do not have an explicit "completed" state in the filesystem; once shipped, they are archived. The decision to archive vs keep active is the operator's; the skill suggests archival via `/sdlc-studio plan list` when stale, but does not move files unprompted.

---

## Plan-mode pickup behaviour

When the operator re-enters plan mode and an existing plan file is present, the prompt asks Claude to:

1. **Read the existing file.** Understand what it covered.
2. **Compare against the user's current request.** Topic match? Same task continuing? Or a fresh task?
3. **Choose a path:**
   - **Same task continuing** – modify the existing plan, removing outdated sections.
   - **Different task** – overwrite the existing plan with a fresh one (the previous plan should already have been archived; if not, this plan-file's purpose was satisfied and overwriting is correct).

The skill does not silently merge plans. If the existing file has substance worth preserving and the new task is unrelated, the operator should archive the existing file first – `/sdlc-studio plan archive <slug>` – before re-entering plan mode.

---

## /sdlc-studio plan list

Backed by `scripts/plan.py`. Claude runs
`python3 "$CLAUDE_SKILL_DIR/scripts/plan.py" list` (`--all` includes the
archive, `--format json` for machine-readable output):

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/plan.py" list
```

```text
PLANS
  add-user-authentication  (2026-04-30, 0d)
                           Plan - implement OAuth login across the API and web client
1 active plan(s)
```

---

## /sdlc-studio plan archive {slug}

Backed by `scripts/plan.py`. Claude runs
`python3 "$CLAUDE_SKILL_DIR/scripts/plan.py" archive <slug>`, which moves the
plan into the archive subfolder by current year-month. The script errors
(non-zero exit) if the slug does not exist, is already archived, or would
overwrite an existing archive file:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/plan.py" archive add-user-authentication
```

```text
Archived add-user-authentication -> ~/.claude/plans/archive/2026-04/add-user-authentication.md
```

---

## /sdlc-studio plan list --stale

Backed by `scripts/plan.py`. Claude runs
`python3 "$CLAUDE_SKILL_DIR/scripts/plan.py" list --stale` (threshold
`--days N`, default 30) to surface candidates for archival:

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/plan.py" list --stale
```

```text
STALE PLANS
  some-old-task-slug  (2026-03-12, 49d)
                      Plan - that thing we never finished
1 active plan(s)
```

The script flags by age only; whether a stale slug still matches the current
branch, task, or open CR is Claude's judgement. The skill does not
auto-archive; the suggestion is advisory. A plan whose work was deferred but
is genuinely still valid stays active until the operator says otherwise.

---

## When to write a new plan vs continue an existing one

| Signal | Action |
| --- | --- |
| Same artefact, refining the approach | Continue (edit) |
| Same artefact, but the approach has been completely re-thought | Continue, but rewrite content fresh |
| Different artefact, same ongoing project | Archive the old plan, write a new one |
| New project entirely | Archive the old plan, write a new one |
| Old plan is for a task that shipped but never got archived | Archive it as part of the current pickup, then write fresh |

The plan-mode prompt's "different task" → overwrite path is correct **when the old plan no longer represents active work**. If the old plan represents work in flight that the operator has paused, archive it explicitly rather than overwriting; an overwrite is silent loss.

---

## Anti-patterns

- **Editing the active plan file with content for an unrelated task.** Plans are atomic – one file, one task. Mixing erodes both.
- **Letting old plans accumulate as "active".** A plans directory full of dead plans is a search problem on every plan-mode entry. Archive on ship.
- **Overwriting without checking.** The plan-mode prompt asks Claude to read the existing file first for a reason; skipping the check loses information. If the existing plan is genuinely stale, archive it explicitly rather than overwrite it.
- **Treating the slug as semantic.** Slugs are auto-generated and can drift from the actual topic over edits. Read the first heading, not the slug, to identify the plan.

---

## See Also

- `reference-decisions.md#execution-contract` – what happens once a plan is approved (no mid-flight check-ins; gates are SDLC-internal)
- `help/plan.md` – `/sdlc-studio plan list` / `archive` quick reference
- The plan-mode system prompt itself documents the in-prompt overwrite-vs-continue choice; this file documents the *between-sessions* lifecycle
