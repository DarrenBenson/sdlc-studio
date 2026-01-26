<!--
Template: Technical Requirements Document
File: sdlc-studio/trd.md
Status values: See reference-outputs.md
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

## 1.5 Project Classification

**Project Type:** {{web_application | api_backend | mobile_backend | desktop_application | sdk_library | monorepo}}

**Classification Rationale:**
{{Why this type was chosen - e.g., "Serves web frontend with React SPA"}}

**Architecture Implications:**
Based on this project type:
- **Default Pattern:** {{recommended pattern from reference-architecture.md}}
- **Pattern Used:** {{actual choice}}
- **Deviation Rationale:** {{if different from default, explain why - document as ADR}}

---

## 2. Architecture Overview

### System Context
{{high-level description of how the system fits into its environment}}

### Architecture Pattern
{{monolith | microservices | serverless | hybrid}}

**Rationale:** {{why this pattern was chosen}}

### Component Overview

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| {{component}} | {{what it does}} | {{stack}} |

### Component Diagram
```
{{ASCII or mermaid diagram showing component relationships}}
```

---

## 3. Technology Stack

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

## 4. API Contracts

### API Style
{{REST | GraphQL | gRPC | WebSocket}}

### Authentication
{{JWT | OAuth2 | API Key | Session}}

**Flow:**
```
{{authentication flow diagram or description}}
```

### Endpoints Overview

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| {{method}} | {{path}} | {{description}} | {{required?}} |

### Request/Response Schemas

#### {{Endpoint Name}}

**Request:**
```json
{
  "field": "type - description"
}
```

**Response:**
```json
{
  "field": "type - description"
}
```

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

## 5. Data Architecture

### Data Models

#### {{Model Name}}

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| {{field}} | {{type}} | {{constraints}} | {{description}} |

### Relationships
```
{{ERD or relationship description}}
```

### Storage Strategy

| Data Type | Storage | Rationale |
|-----------|---------|-----------|
| {{type}} | {{where stored}} | {{why}} |

### Migrations
{{approach to schema migrations}}

---

## 6. Integration Patterns

### External Services

| Service | Purpose | Protocol | Auth |
|---------|---------|----------|------|
| {{service}} | {{purpose}} | {{REST/gRPC/etc}} | {{auth method}} |

### Event Architecture
{{if applicable - event-driven patterns, message queues}}

### Auth/Authz Model
{{how authentication and authorisation work across components}}

---

## 7. Infrastructure Approach

### Deployment Topology
{{description of how the system is deployed}}

```
{{deployment diagram}}
```

### Environment Strategy

| Environment | Purpose | Characteristics |
|-------------|---------|-----------------|
| Development | Local development | {{characteristics}} |
| Staging | Pre-production testing | {{characteristics}} |
| Production | Live system | {{characteristics}} |

### Scaling Strategy
{{horizontal/vertical scaling approach, auto-scaling rules}}

### Disaster Recovery
{{backup strategy, RTO, RPO}}

---

## 8. Security Considerations

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
| Input validation | {{approach}} |
| Logging & monitoring | {{approach}} |

### Data Classification

| Category | Examples | Handling |
|----------|----------|----------|
| Public | {{examples}} | {{handling}} |
| Internal | {{examples}} | {{handling}} |
| Confidential | {{examples}} | {{handling}} |
| Restricted (PII) | {{examples}} | {{handling}} |

---

## 9. Performance Requirements

### Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Response time (p50) | {{target}} | {{how measured}} |
| Response time (p95) | {{target}} | {{how measured}} |
| Throughput | {{target}} | {{how measured}} |
| Availability | {{target}} | {{how measured}} |

### Capacity Planning
{{expected load, growth projections}}

---

## 9.5 Architecture Checklist

### Pattern Selection
- [ ] Project type identified and documented
- [ ] Default pattern evaluated against project needs
- [ ] Deviation from default documented as ADR (if applicable)

### Technology Decisions
- [ ] Language selection justified (not just "familiarity")
- [ ] Framework selection justified
- [ ] Database selection justified
- [ ] API style selection justified

### Standards Compliance
- [ ] OpenAPI documented (if REST)
- [ ] Error responses standardised
- [ ] Authentication approach documented
- [ ] Pagination approach documented (if applicable)

### Infrastructure
- [ ] Deployment target identified
- [ ] Scaling strategy documented
- [ ] Disaster recovery documented

---

## 10. Architecture Decision Records

### ADR-001: {{Decision Title}}

**Status:** Proposed | Accepted | Deprecated | Superseded

**Context:** {{what is the issue we're seeing that motivates this decision}}

**Decision:** {{what is the change we're proposing}}

**Consequences:**
- Positive: {{benefits}}
- Negative: {{drawbacks}}
- Neutral: {{other effects}}

---

## 11. Open Technical Questions

- [ ] **Q:** {{question}}
  **Context:** {{why this matters}}
  **Options:** {{if applicable}}

---

## 12. Implementation Constraints

### Must Have
- {{constraint}}

### Should Have
- {{constraint}}

### Won't Have (This Version)
- {{constraint}}

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| {{date}} | {{version}} | Initial draft |
