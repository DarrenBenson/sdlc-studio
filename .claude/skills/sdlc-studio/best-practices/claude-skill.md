# Best Practices: Skills

Based on [official Claude Code documentation](https://code.claude.com/docs/en/skills) and [Anthropic engineering guidance](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills).

## Template

Start from the template to ensure compliance:

```bash
cp .claude/templates/skill/SKILL.md .claude/skills/[name]/SKILL.md
```

Then replace all `{{placeholders}}` with actual values.

## Checklist

Before considering a skill complete:

- [ ] `SKILL.md` exists with frontmatter (`name`, `description`)
- [ ] `name` is lowercase with hyphens, max 64 chars, matches folder name
- [ ] `description` explains what it does and includes trigger keywords (max 1024 chars)
- [ ] `description` is double-quoted if it contains `: `, `[]`, `{}`, or `#`
- [ ] Clear "When to Use" section with trigger phrases
- [ ] Step-by-step instructions the AI can follow
- [ ] Examples with expected inputs/outputs
- [ ] SKILL.md is under 500 lines (use progressive disclosure for larger content)
- [ ] Scripts (if any) have `--help` and are executable
- [ ] Templates (if any) use `{{placeholder}}` syntax
- [ ] Related skills/commands listed in "See Also"

## Frontmatter

### Required Fields

| Field | Description | Constraints |
|-------|-------------|-------------|
| `name` | Skill identifier | Lowercase, hyphens, max 64 chars, match folder name |
| `description` | What it does and when to use | Max 1024 chars, include trigger keywords |

### Optional Fields

| Field | Description | Example |
|-------|-------------|---------|
| `allowed-tools` | Restrict available tools | `Read, Grep, Glob` |
| `model` | Specify Claude model | `sonnet`, `opus`, `haiku`, or full model ID |
| `argument-hint` | Hint text for arguments | `[issue-number]`, `[filename] [format]` |
| `user-invocable` | Whether users can invoke directly | `true` or `false` |
| `disable-model-invocation` | Prevent AI auto-triggering | `true` or `false` |
| `context` | Execution context | `fork` (run in subagent) |
| `agent` | Subagent type | `Explore`, `Plan`, `general-purpose` |

### YAML Quoting Rules

Values containing special YAML characters must be quoted. Unquoted values with colons cause `malformed YAML frontmatter` errors on claude.ai.

| Character | Example problem | Fix |
|-----------|----------------|-----|
| `: ` (colon-space) | `SDLC pipeline: requirements` | Wrap value in double quotes |
| `#` | `Run # of tests` | Wrap value in double quotes |
| `[` or `]` | `[type] [action]` | Wrap value in double quotes |
| `{` or `}` | `{name}` | Wrap value in double quotes |

```yaml
# Bad - colons and brackets cause YAML parse errors
description: /skill [type] - Pipeline: requirements, specs, code.

# Good - double quotes protect special characters
description: "/skill [type] - Pipeline: requirements, specs, code."
```

## Structure

### Required: SKILL.md

```markdown
---
name: example
description: Brief description of what this does. Use when user asks about X or wants to do Y.
---

# Example Skill

One-line summary.

## When to Use

- "Trigger phrase one"
- "Trigger phrase two"
- When user asks about X

## Instructions

Step-by-step what the AI should do:

1. First step
2. Second step
3. Third step

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `arg1` | What it does | value |

## Examples

```
/example foo        # Does X
/example bar --flag # Does Y
```

## See Also

- `related-skill` - Brief description
```

### Optional: scripts/

```
my-skill/
├── SKILL.md
└── scripts/
    ├── main.py
    └── lib/
```

### Optional: references/ (Progressive Disclosure)

For skills with extensive documentation, split into separate files:

```
my-skill/
├── SKILL.md           # Overview and navigation (under 500 lines)
├── reference.md       # Detailed docs - loaded when needed
├── examples.md        # Usage examples - loaded when needed
└── scripts/
    └── helper.py
```

Link from SKILL.md: "For detailed API reference, see `reference.md`."

**Progressive disclosure levels:**
1. **Startup**: Only `name` and `description` loaded into system prompt
2. **Triggered**: Full `SKILL.md` loads when skill is relevant
3. **On-demand**: Bundled files load selectively as needed

### Optional: templates/

For skills that generate reports, artifacts, or structured output:

```
my-skill/
├── SKILL.md
├── scripts/
└── templates/
    ├── report-template.md
    └── summary-template.md
```

**When to use templates:**

- Skill generates markdown reports or summaries
- Output format needs to be consistent and maintainable
- Non-developers may need to update output structure
- Validation or quality checks depend on output format

**Template conventions:**

| Convention | Example |
|------------|---------|
| Use `{{placeholder}}` syntax | `{{engram_name}}`, `{{test_date}}` |
| Include comments for complex sections | `<!-- Repeat for each test -->` |
| Keep templates self-documenting | Add section headers even if brief |

## Description Best Practices

A good description answers:
1. **What does this skill do?** (list specific capabilities)
2. **When should Claude use it?** (include trigger keywords)

### Standard Pattern

```yaml
description: "Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction."
```

### Command-Wrapper Pattern

When a skill is invoked via a command wrapper (`.claude/commands/*.md`), you can prefix the description with the command syntax for documentation clarity:

```yaml
description: "/search [query] - Search engrams by name, slug, nationality, MBTI, or role. Use when looking up or finding engrams."
```

This pattern:
- Shows users which command invokes the skill
- Still includes trigger keywords for semantic matching
- Links documentation between commands and skills

**Command file** (`.claude/commands/search.md`):
```markdown
/search [query] - Search engrams by name, slug, or filters

## Instructions
Follow the skill instructions in `.claude/skills/library-search/SKILL.md`.
```

**Skill file** (`.claude/skills/library-search/SKILL.md`):
```yaml
---
name: library-search
description: "/search [query] - Search engrams by name, slug, nationality, MBTI, or role. Use when looking up or finding engrams."
---
```

### Bad

```yaml
description: Helps with documents
```

(Too vague, no trigger keywords)

## Examples

### Good: When to Use

```markdown
## When to Use

- "Run tests on this engram"
- "Check if the engram passes validation"
- When user wants to verify engram quality before deployment
```

### Bad: When to Use

```markdown
## When to Use

This skill is used for testing.
```

(Too vague, no trigger phrases)

### Good: Read-only Skill

```yaml
---
name: safe-reader
description: Read files without making changes. Use when you need read-only file access.
allowed-tools: Read, Grep, Glob
---
```

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| No frontmatter | Won't be discovered | Add `---` block with name/description |
| Vague description | AI won't know when to invoke | Include specific capabilities and trigger keywords |
| SKILL.md over 500 lines | Context bloat | Use progressive disclosure with reference files |
| Wall of text instructions | Hard to follow | Numbered steps, clear actions |
| Missing examples | Unclear usage | Add 2-3 concrete examples |
| Hardcoded paths | Breaks portability | Use relative paths or config |
| No error handling docs | AI doesn't know failure modes | Document what can go wrong |
| Inline report formats | Hard to maintain output structure | Use `templates/` folder with `.md` files |
| Deeply nested references | Hard to navigate | Keep one level deep from SKILL.md |

## Naming Convention

- Folder name should match the `name` field
- Use kebab-case (lowercase with hyphens)
- Examples: `pdf-processor`, `code-reviewer`, `deploy`

## Scripts

If the skill includes scripts:

- Must be executable (`chmod +x`)
- Must support `--help`
- Handle errors gracefully with clear messages
- Output should be parseable (JSON for data, Markdown for reports)
- Scripts execute without loading contents into context (only output consumes tokens)

## Troubleshooting

- Skills must be in correct directory with exact filename `SKILL.md`
- Use `claude --debug` to see skill loading errors
- Scripts need execute permissions: `chmod +x scripts/*.py`
- YAML frontmatter must start on line 1 (no blank lines before `---`)
- Use spaces for indentation in YAML (not tabs)
- Quote `description` values containing `: `, `[]`, `{}`, or `#` to avoid YAML parse errors
- The claude.ai web uploader has stricter YAML parsing than the CLI; always quote descriptions with special characters
