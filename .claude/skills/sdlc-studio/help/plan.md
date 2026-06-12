<!-- Load when: user runs /sdlc-studio plan or asks about plan-file lifecycle -->
<!-- Dependencies: reference-plan-files.md -->

# /sdlc-studio plan - Help

> **Source of truth:** `reference-plan-files.md` - File layout, states, pickup behaviour, anti-patterns

Manage Claude Code plan-mode files (`~/.claude/plans/`). One file per task,
kebab-case slug. Active plans live at the top level; retired plans move to
`archive/{yyyy-mm}/`. The skill suggests archival but never moves files
unprompted.

Both commands are backed by `python3 "$CLAUDE_SKILL_DIR/scripts/plan.py"`
(`list` / `archive`).

## Quick Reference

```bash
/sdlc-studio plan list                # Show active plans only
/sdlc-studio plan list --all          # Include archive
/sdlc-studio plan list --stale        # Plans untouched > 30 days
/sdlc-studio plan archive {slug}      # Move plan to archive/{yyyy-mm}/
```

## Actions

### list

Print active plans: slug, last-modified, first heading. `--stale` flags
plans older than 30 days whose slug matches no current branch, CR, or
story - candidates for archival, advisory only.

### archive {slug}

Move an active plan into `archive/{yyyy-mm}/`. Errors clearly if the slug
does not exist or is already archived.

## When to Archive

Archive on ship, on abandonment, or when superseded. If an old plan
represents paused work in flight, archive it explicitly before starting
an unrelated plan - overwriting is silent loss.

## See Also

- `reference-plan-files.md` - Full lifecycle, pickup behaviour, anti-patterns
- `reference-decisions.md#execution-contract` - What happens once a plan is approved
