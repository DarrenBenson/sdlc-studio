# Best Practices: README Files

## Template

Start from the template for folder READMEs:

```bash
cp .claude/templates/readme/README.md [folder]/README.md
```

Then replace all `{{placeholders}}` with actual values.

## Checklist

Before considering a README complete:

- [ ] Title clearly states what this is
- [ ] One-paragraph description of purpose
- [ ] Quick start (setup in <10 minutes)
- [ ] Structure/contents overview if it's a folder
- [ ] Links to related documentation
- [ ] No outdated information
- [ ] Scannable (headers, bullets, tables)

## Types of README

| Type | Location | Purpose |
|------|----------|---------|
| Project | `/README.md` | First impression, installation, quick start |
| Folder | `[folder]/README.md` | Explain folder contents and purpose |
| Skill | `.claude/skills/[name]/SKILL.md` | AI-facing documentation |

## Structure: Project README

```markdown
# Project Name

Brief description (1-2 sentences).

## Features

- Feature one
- Feature two
- Feature three

## Quick Start

```bash
# Installation steps
git clone ...
cd ...
./setup.sh
```

## Usage

Common commands or examples.

## Documentation

- [Guide 1](docs/guide1.md)
- [Guide 2](docs/guide2.md)

## Contributing

How to contribute.

## Licence

Licence type.
```

## Structure: Folder README

```markdown
# Folder Name

What this folder contains and why.

## Contents

| File/Folder | Purpose |
|-------------|---------|
| `thing1/` | Description |
| `thing2.py` | Description |

## Usage

How to work with contents.

## Related

- [Related doc](../path/to/doc.md)
```

## Examples

### Good

```markdown
# Engram Foundry

Multi-agent pipeline for creating and validating engram identity files.

## Quick Start

1. Place input in `foundry/input/`
2. Run `/foundry-backlog`
3. Review output in `foundry/output/`
```

### Bad

```markdown
# README

This folder contains various files for the project.

See the documentation for more information.
```

(Generic title, vague description, no actionable content)

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| Generic title | Doesn't describe content | Use descriptive name |
| Wall of text | Hard to scan | Break into sections, use bullets |
| Outdated info | Causes confusion | Review and update regularly |
| No quick start | User can't get going | Add minimal setup steps |
| Links to nowhere | Broken experience | Verify all links work |
| Too long | Overwhelming | Move details to separate docs |

## Formatting

- **Headers**: Use `##` for main sections, `###` for subsections
- **Lists**: Bullets for unordered, numbers for sequences
- **Tables**: For structured data (arguments, options, mappings)
- **Code blocks**: With language hints (```bash, ```python)
- **Links**: Relative paths for internal docs

## Project README Extras

For the main project README, consider:

- **Badges**: Version, license, build status (shields.io)
- **Screenshot/GIF**: Visual hook at the top
- **Table of contents**: For longer READMEs
- **Acknowledgments**: Credits and thanks

## Length Guidelines

| Type | Target Length |
|------|---------------|
| Project README | 100-300 lines |
| Folder README | 30-100 lines |
| Minimal README | 10-30 lines |

If longer, consider splitting into separate docs and linking.
