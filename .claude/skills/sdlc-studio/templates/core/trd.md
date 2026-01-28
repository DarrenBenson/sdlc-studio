<!--
Template: Technical Requirements Document (Streamlined)
File: sdlc-studio/trd.md
Status values: See reference-outputs.md
Modules: trd/c4-diagrams.md, trd/container-design.md, trd/adr.md
Related: help/trd.md, reference-trd.md
-->
# Technical Requirements Document

**Project:** {{project_name}}
**Version:** {{version}}
**Status:** Draft | Approved
**Last Updated:** {{date}}
**PRD Reference:** [PRD](../prd.md)

---

## 1. Executive Summary

### Purpose
{{brief description of what this technical design achieves}}

### Scope
{{what is covered and not covered by this TRD}}

### Key Decisions
- {{decision 1}}
- {{decision 2}}
- {{decision 3}}

---

## 2. Project Classification

**Project Type:** {{web_application | api_backend | mobile_backend | desktop_application | sdk_library | monorepo}}

**Classification Rationale:** {{why this type was chosen}}

**Architecture Implications:**
- **Default Pattern:** {{recommended pattern from reference-architecture.md}}
- **Pattern Used:** {{actual choice}}
- **Deviation Rationale:** {{if different, explain why}}

---

## 3. Architecture Overview

### System Context
{{high-level description of how the system fits into its environment}}

### Architecture Pattern
{{monolith | microservices | serverless | hybrid}}

**Rationale:** {{why this pattern was chosen}}

### Component Overview

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| {{component}} | {{what it does}} | {{stack}} |

> **C4 Diagrams:** Use `trd create --with-diagrams` or see `modules/trd/c4-diagrams.md`

---

## 4. Technology Stack

### Core Technologies

| Category | Technology | Version | Rationale |
|----------|-----------|---------|-----------|
| Language | {{language}} | {{version}} | {{why chosen}} |
| Framework | {{framework}} | {{version}} | {{why chosen}} |
| Database | {{database}} | {{version}} | {{why chosen}} |

### Build & Development

| Tool | Purpose |
|------|---------|
| {{tool}} | {{purpose}} |

### Infrastructure Services

| Service | Provider | Purpose |
|---------|----------|---------|
| {{service}} | {{provider}} | {{purpose}} |

---

## 5. API Contracts

### API Style
{{REST | GraphQL | gRPC | WebSocket}}

### Authentication
{{JWT | OAuth2 | API Key | Session}}

### Endpoints Overview

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| {{method}} | {{path}} | {{description}} | {{required?}} |

### Error Response Format
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": {}
  }
}
```

---

## 6. Data Architecture

### Data Models

#### {{Model Name}}

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| {{field}} | {{type}} | {{constraints}} | {{description}} |

### Storage Strategy

| Data Type | Storage | Rationale |
|-----------|---------|-----------|
| {{type}} | {{where stored}} | {{why}} |

### Migrations
{{approach to schema migrations}}

---

## 7. Integration Patterns

### External Services

| Service | Purpose | Protocol | Auth |
|---------|---------|----------|------|
| {{service}} | {{purpose}} | {{REST/gRPC/etc}} | {{auth method}} |

### Event Architecture
{{if applicable - event-driven patterns, message queues}}

---

## 8. Infrastructure

### Deployment Topology
{{description of how the system is deployed}}

### Environment Strategy

| Environment | Purpose | Characteristics |
|-------------|---------|-----------------|
| Development | Local development | {{characteristics}} |
| Staging | Pre-production testing | {{characteristics}} |
| Production | Live system | {{characteristics}} |

### Scaling Strategy
{{horizontal/vertical scaling approach}}

> **Container Design:** Use `trd create --with-containers` or see `modules/trd/container-design.md`

---

## 9. Security Considerations

### Threat Model

| Threat | Likelihood | Impact | Mitigation |
|--------|-----------|--------|------------|
| {{threat}} | {{L/M/H}} | {{L/M/H}} | {{mitigation}} |

### Security Controls

| Control | Implementation |
|---------|----------------|
| Authentication | {{approach}} |
| Authorisation | {{approach}} |
| Encryption at rest | {{approach}} |
| Encryption in transit | {{approach}} |

---

## 10. Performance Requirements

### Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response time (p50) | {{target}} | {{how measured}} |
| Response time (p95) | {{target}} | {{how measured}} |
| Throughput | {{target}} | {{how measured}} |
| Availability | {{target}} | {{how measured}} |

---

## 11. Architecture Decision Records

> See `modules/trd/adr.md` for ADR template

### ADR-001: {{Decision Title}}

**Status:** Proposed | Accepted | Deprecated | Superseded

**Context:** {{what is the issue we're seeing}}

**Decision:** {{what is the change we're proposing}}

**Consequences:**
- Positive: {{benefits}}
- Negative: {{drawbacks}}

---

## 12. Open Technical Questions

- [ ] **Q:** {{question}}
  **Context:** {{why this matters}}

---

## 13. Implementation Constraints

### Must Have
- {{constraint}}

### Won't Have (This Version)
- {{constraint}}

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| {{date}} | {{version}} | Initial draft |
