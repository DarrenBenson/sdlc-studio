<!--
Template: Persona Index
File: sdlc-studio/personas/index.md
Purpose: Lists all personas active for this project
Related: reference-persona.md, help/persona.md
-->
# Project Personas

Personas for {{project_name}}. This index lists all active personas organised by category.

**Last updated:** {{date}}

---

## Team Personas

Internal team members who create and review artefacts. Organised by Three Amigos perspective.

### Product Amigo

| Persona | Role | Summary | File |
|---------|------|---------|------|
| {{name}} | {{role}} | {{one_line_summary}} | [Details]({{filename}}) |

### Engineering Amigo

| Persona | Role | Summary | File |
|---------|------|---------|------|
| {{name}} | {{role}} | {{one_line_summary}} | [Details]({{filename}}) |

### QA Amigo

| Persona | Role | Summary | File |
|---------|------|---------|------|
| {{name}} | {{role}} | {{one_line_summary}} | [Details]({{filename}}) |

---

## Stakeholder Personas

External stakeholders who use the product or influence requirements.

### End Users

| Persona | Role | Summary | File |
|---------|------|---------|------|
| {{name}} | {{role}} | {{one_line_summary}} | [Details]({{filename}}) |

### Business Stakeholders

| Persona | Role | Summary | File |
|---------|------|---------|------|
| {{name}} | {{role}} | {{one_line_summary}} | [Details]({{filename}}) |

### Technical Stakeholders

| Persona | Role | Summary | File |
|---------|------|---------|------|
| {{name}} | {{role}} | {{one_line_summary}} | [Details]({{filename}}) |

---

## Consultation Defaults

Default personas consulted for each artefact type.

| Artefact | Team | Stakeholders |
|----------|------|--------------|
| PRD | Product (all) | End Users, Business |
| Epic | Product, Engineering Lead | Affected users |
| User Story | Product | Primary persona |
| Technical Spec | Engineering (all) | Security, Compliance (if relevant) |
| Test Strategy | QA (all) | Operations |

Override defaults with `--persona` flag or `--skip-personas` to bypass.

---

## Custom Personas

Project-specific personas not from archetypes.

| Persona | Category | Role | File |
|---------|----------|------|------|
| {{name}} | {{team/stakeholder}} | {{role}} | [Details]({{filename}}) |

---

## Usage

```bash
# Consult specific persona
/sdlc-studio consult sarah-chen prd.md

# Three Amigos review
/sdlc-studio consult team epic.md

# All stakeholders
/sdlc-studio consult stakeholders prd.md

# Interactive chat
/sdlc-studio chat marcus-johnson

# Multi-persona workshop
/sdlc-studio chat --workshop "API design approach" --amigos
```

---

## Persona Sources

| Source | Count | Notes |
|--------|-------|-------|
| Archetypes | {{n}} | From SDLC Studio templates |
| Generated | {{n}} | Inferred from PRD/codebase |
| Imported | {{n}} | From external files |
| Custom | {{n}} | Created for this project |

---

*See [reference-persona.md](../../reference-persona.md) for detailed persona workflows.*
