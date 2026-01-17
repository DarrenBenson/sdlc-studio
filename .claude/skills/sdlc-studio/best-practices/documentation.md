# Best Practices: Documentation

## Checklist

Before considering documentation complete:

- [ ] Clear title describing the topic
- [ ] Audience stated or obvious (user, developer, AI)
- [ ] Logical structure (overview → details → reference)
- [ ] Examples for complex concepts
- [ ] No outdated or contradictory information
- [ ] Cross-references to related docs
- [ ] Consistent terminology throughout

## Document Types

| Type | Location | Purpose |
|------|----------|---------|
| Guide | `docs/guides/` | How to do something (tutorial) |
| Reference | `docs/reference/` | Complete specification |
| Schema | `framework/agent/` | Data structure definitions |
| Workflow | Various | Step-by-step processes |

## Structure: Guide

```markdown
# Topic Name

Brief intro explaining what this guide covers.

## Overview

High-level explanation.

## Prerequisites

What you need before starting.

## Steps

### Step 1: First Thing

Details...

### Step 2: Second Thing

Details...

## Examples

Worked examples.

## Troubleshooting

Common issues and fixes.

## Next Steps

- [Related Guide 1](path/to/guide.md)
- [Related Guide 2](path/to/guide.md)
```

## Structure: Reference

```markdown
# Component Reference

Brief description.

## Syntax

```
format or schema
```

## Fields/Options

| Name | Type | Required | Description |
|------|------|----------|-------------|
| field1 | string | Yes | What it does |
| field2 | number | No | What it does |

## Examples

Example 1...

Example 2...

## Related

- [Other Reference](path/to/ref.md)
```

## Examples

### Good

```markdown
## Creating an Engram

Engrams are created through the foundry pipeline. This guide walks through
the three creation modes.

### Mode 1: Interactive Creation

Use when you have a general concept but no source material.

1. Run `/foundry-create "description"`
2. Answer the calibration questions
3. Review the generated engram
```

### Bad

```markdown
## Engrams

Engrams are JSON files. They have many fields. You can create them
in different ways. See the schema for details.
```

(Vague, no actionable steps, no examples)

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Passive voice | Unclear who does what | Use active voice, direct instructions |
| Undefined jargon | Confuses new readers | Define terms or link to glossary |
| Orphan pages | Hard to discover | Link from related docs |
| Duplicate content | Maintenance burden | Single source of truth, link to it |
| No examples | Abstract and unclear | Add concrete examples |
| Outdated screenshots | Misleading | Update or remove |

## Writing Style

- **Active voice**: "Run the command" not "The command should be run"
- **Second person**: "You can..." not "Users can..."
- **Present tense**: "This creates..." not "This will create..."
- **Concrete**: Specific examples, not abstract descriptions
- **Scannable**: Headers, bullets, tables for quick navigation

## Linking

- Use relative paths: `../other-folder/doc.md`
- Link to specific sections: `doc.md#section-name`
- Verify links work after moving files
- Prefer linking over duplicating content

## Versioning

For versioned content:

- Include version in document or folder name
- Note which version docs apply to
- Archive old versions, don't delete
- Update version references when framework changes

## Maintenance

- Review docs when related code changes
- Remove or update outdated information
- Check links periodically
- Consolidate scattered information
