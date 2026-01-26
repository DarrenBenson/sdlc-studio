<!--
Template: Product Requirements Document
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

### Maturity Assessment
{{maturity_level}}

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

### Error Handling
{{error_handling_approach}}

---

## 6. AI/ML Specifications

> Skip this section if not applicable.

### Models and Providers
{{models_used}}

### Prompt Patterns
{{prompt_patterns}}

### Context Management
{{context_management}}

### Parameters and Settings
{{model_parameters}}

### Retry and Fallback Logic
{{fallback_logic}}

---

## 7. Data Architecture

### Data Models
{{data_models}}

### Relationships and Constraints
{{data_relationships}}

### Storage Mechanisms
{{storage_mechanisms}}

### Data Flow
{{data_flow_description}}

---

## 8. Integration Map

### External Services
{{external_services}}

### Authentication Methods
{{auth_methods}}

### Webhooks and Events
{{webhook_patterns}}

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

### Deployment Requirements
{{deployment_requirements}}

---

## 10. Test Coverage Analysis

### Tested Functionality
{{tested_features}}

### Untested Areas
{{untested_areas}}

### Test Patterns Used
{{test_patterns}}

### Quality Assessment
{{quality_assessment}}

---

## 11. Technical Debt Register

### TODO/FIXME Items Found
{{todo_items}}

### Inconsistent Patterns
{{inconsistent_patterns}}

### Deprecated Dependencies
{{deprecated_deps}}

### Security Concerns
{{security_concerns}}

---

## 12. Documentation Gaps

### Undocumented Features
{{undocumented_features}}

### Missing Inline Comments
{{missing_comments}}

### Unclear Code Sections
{{unclear_sections}}

---

## 13. Recommendations

### Critical Gaps
{{critical_gaps}}

### Suggested Improvements
{{improvements}}

### Security Hardening
{{security_hardening}}

---

## 14. Open Questions

{{open_questions}}

---

## Appendix

### A. File Tree Summary
```
{{file_tree}}
```

### B. Dependency List
{{dependency_list}}

### C. Environment Variable Reference
{{env_reference}}

### D. API Endpoint Catalogue

| Method | Endpoint | Description |
|--------|----------|-------------|
| {{method}} | {{endpoint}} | {{description}} |

### E. Changelog

| Date | Version | Changes |
|------|---------|---------|
| {{date}} | {{version}} | {{changes}} |

---

## Confidence Markers Legend

- **[HIGH]** - Clear from code, tests, or documentation
- **[MEDIUM]** - Reasonable inference from patterns
- **[LOW]** - Speculative, needs verification
- **[UNKNOWN]** - Cannot determine

## Status Legend

- **Complete** - Fully implemented and tested
- **Partial** - Partially implemented, some functionality missing
- **Stubbed** - Interface exists but implementation incomplete
- **Broken** - Was working, now failing
- **Not Started** - Planned but not yet implemented
