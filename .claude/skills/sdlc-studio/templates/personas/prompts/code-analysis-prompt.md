<!--
Template: Codebase Analysis Prompt for Persona Generation
Usage: Prompt for Task tool with Explore agent
-->

# Codebase Analysis for Persona Discovery

Analyse this codebase to identify user types and roles. Search systematically for:

---

## 1. Authentication & Authorisation

**Search for:**
- User model/schema definitions
- Role enums, constants, or type definitions
- Permission definitions or capability lists
- RBAC (Role-Based Access Control) configurations
- Auth middleware, guards, or decorators
- JWT claims or session data structures

**Report:**
- Role names found
- Permissions per role
- File locations (file:line)

---

## 2. User Interface Patterns

**Search for:**
- Route definitions with role guards or access control
- Conditional rendering based on user type/role
- Different dashboard or landing page components
- Navigation items filtered by role
- Feature flags tied to user types
- Admin panels or privileged UI sections

**Report:**
- UI routes per role
- Conditional features found
- Estimated UI complexity per role (simple/moderate/complex)

---

## 3. API Patterns

**Search for:**
- Endpoints with role-based access decorators
- Different response shapes by role
- Rate limits or quotas by user type
- Audit logging mentioning user types
- Webhook or integration endpoints (often admin-only)

**Report:**
- API capabilities per role
- Access restrictions found

---

## 4. Database & Data Model

**Search for:**
- User table/collection schema
- Role or type fields on user records
- Audit tables with actor types
- Multi-tenancy patterns (org, team, individual)

**Report:**
- User data structure
- Role storage approach

---

## 5. Documentation & Tests

**Search for:**
- README sections about user types
- Test fixtures with user personas
- Comments describing user scenarios
- Seed data with different user types
- E2E tests that login as different roles

**Report:**
- User types mentioned in docs
- Test scenarios per role

---

## Output Format

For each user type discovered, report:

```
USER TYPE: [name/identifier]
Source: [primary file:line where defined]
Category: [from_auth | from_ui | from_api | from_docs | inferred]

Permissions/Capabilities:
- [capability 1]
- [capability 2]

UI Access:
- [route 1]
- [route 2]

Evidence:
- [file:line]: [brief description]
- [file:line]: [brief description]

Estimated Profile:
- Technical Level: [novice/intermediate/advanced/expert]
- Likely Role: [suggested job title]
- Confidence: [high/medium/low]
```

---

## Summary

After analysis, provide:

1. **Definite user types** - Explicitly defined in code
2. **Probable user types** - Strong evidence but not explicit
3. **Possible user types** - Inferred from patterns
4. **Gaps** - Roles that might exist but have no code evidence
