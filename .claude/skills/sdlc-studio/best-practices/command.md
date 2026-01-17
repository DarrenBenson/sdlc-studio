# Best Practices: Commands

## Template

Start from the template to ensure compliance:

```bash
cp .claude/templates/command/command.md .claude/commands/[name].md
```

Then replace all `{{placeholders}}` with actual values.

## Checklist

Before considering a command complete:

- [ ] File exists at `.claude/commands/[name].md`
- [ ] First line is `/command-name [args] - Brief description`
- [ ] Usage section with syntax
- [ ] Clear instructions for AI execution
- [ ] Examples showing common use cases
- [ ] "See Also" links to related commands/skills
- [ ] Added to `/engram-help` command list

## Structure

```markdown
/command-name [args] - One-line description

## Usage

```
/command-name [required] [optional]
```

Brief explanation of what happens.

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `arg1` | What it does | - |
| `--flag` | Optional flag | false |

## Instructions

When this command is invoked:

1. First action
2. Second action
3. Third action

## Examples

```
/command-name foo           # Basic usage
/command-name bar --verbose # With flag
```

## See Also

- `/related-command` - Description
- `related-skill` - Description
```

## Examples

### Good

```markdown
/foundry-cleanup [archive|delete] - Clean up foundry/output/ folder

## Usage

```
/foundry-cleanup           # Asks which action
/foundry-cleanup archive   # Zip to foundry/archive/ then delete
/foundry-cleanup delete    # Delete without archiving
```
```

### Bad

```markdown
# Cleanup Command

This command cleans things up.
```

(Missing `/command` format, vague description)

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| No `/command` first line | Hard to scan | Start with `/name [args] - description` |
| Missing usage syntax | Unclear how to invoke | Add `## Usage` with exact syntax |
| Instructions as prose | Hard to follow | Numbered steps with clear actions |
| No examples | User guesses at usage | Add 2-3 concrete examples |
| Missing from help | Undiscoverable | Update `/engram-help` |
| Duplicates skill docs | Maintenance burden | Reference skill, don't duplicate |

## Commands vs Skills

| Aspect | Command | Skill |
|--------|---------|-------|
| Location | `.claude/commands/` | `.claude/skills/[area]/` |
| Invoked by | User typing `/name` | AI deciding to use it |
| Complexity | Thin wrapper | Full implementation |
| Documentation | Brief instructions | Comprehensive SKILL.md |

**Principle:** Commands invoke skills. Keep commands thin.

## Help Index Commands

Help commands (like `/engram-help`) are special - they're reference indexes, not actions.

**Template:** `.claude/templates/command/help-index.md`

**Structure:**

```markdown
/help-name - Show available commands and usage

## Quick Start

[3 commands for new users to try first]

## Commands

### Category 1
| Command | Description |
...

## Common Flags
[Shared flags across commands]

## Documentation
[Links to guides]

## Version
**Project:** X.Y.Z | **Commands:** N
```

**Checklist for help indexes:**

- [ ] Quick Start section for new users (3 commands max)
- [ ] Commands grouped by category
- [ ] Tables for scannability
- [ ] Common flags section (avoid repetition)
- [ ] Links to full documentation
- [ ] Version info at bottom
- [ ] No trailing questions or prompts

## Naming Convention

- Use kebab-case: `foundry-cleanup`, `framework-test`
- Group related commands with prefix: `foundry-*`, `chat-*`
- Be specific: `/foundry-regrade` not `/regrade`

## Registration

After creating a command:

1. Test it works: `/command-name --help` or similar
2. Add to `.claude/commands/engram-help.md`
3. Update `CLAUDE.md` commands table if significant
