<!--
Template: Product Requirements Document (Streamlined)
File: sdlc-studio/prd.md
Status values: See reference-outputs.md
Related: help/prd.md, reference-prd.md
-->
# Product Requirements Document

**Project:** {{project_name}}
**Version:** {{version}}
**Last Updated:** {{last_updated}}
**Status:** {{status}}

---

## 1. Project Overview

### Product Name
{{product_name}}

### Purpose
{{purpose_description}}

### Tech Stack
{{tech_stack_summary}}

### Architecture Pattern
{{architecture_pattern}}

---

## 2. Problem Statement

### Problem Being Solved
{{problem_description}}

### Target Users
{{target_users}}

### Context
{{context_notes}}

---

## 3. Feature Inventory

| Feature | Description | Status | Priority | Location |
|---------|-------------|--------|----------|----------|
| {{feature_name}} | {{feature_description}} | {{status}} | {{priority}} | {{location}} |

### Feature Details

#### {{feature_name}}

**User Story:** As a {{user_type}}, I want to {{action}} so that {{benefit}}.

**Acceptance Criteria:**
- [ ] {{criterion_1}}
- [ ] {{criterion_2}}
- [ ] {{criterion_3}}

**Dependencies:** {{dependencies}}
**Status:** {{feature_status}}
**Confidence:** {{confidence_marker}}

---

## 4. Functional Requirements

### Core Behaviours
{{functional_requirements}}

### Input/Output Specifications
{{io_specifications}}

### Business Logic Rules
{{business_rules}}

---

## 5. Non-Functional Requirements

### Performance
{{performance_requirements}}

### Security
{{security_requirements}}

### Scalability
{{scalability_requirements}}

### Availability
{{availability_requirements}}

---

## 6. AI/ML Specifications

> Skip if not applicable.

### Models and Providers
{{models_used}}

### Prompt Patterns
{{prompt_patterns}}

### Context Management
{{context_management}}

---

## 7. Data Architecture

### Data Models
{{data_models}}

### Relationships and Constraints
{{data_relationships}}

### Storage Mechanisms
{{storage_mechanisms}}

---

## 8. Integration Map

### External Services
{{external_services}}

### Authentication Methods
{{auth_methods}}

### Third-Party Dependencies
{{third_party_deps}}

---

## 9. Configuration Reference

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| {{env_var}} | {{env_description}} | {{required}} | {{default}} |

### Feature Flags
{{feature_flags}}

---

## 10. Quality Assessment

### Tested Functionality
{{tested_features}}

### Untested Areas
{{untested_areas}}

### Technical Debt
{{todo_items}}

---

## 11. Open Questions

{{open_questions}}

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| {{date}} | {{version}} | {{changes}} |

---

> **Confidence Markers:** [HIGH] clear from code | [MEDIUM] inferred from patterns | [LOW] speculative
>
> **Status Values:** Complete | Partial | Stubbed | Broken | Not Started
