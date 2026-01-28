# User Story Section Reference

Detailed guidance for completing each section of the User Story template.

<!-- Load when: filling out story template sections in detail -->

---

## User Story Statement {#user-story-statement}

### Format {#story-format}
**As a** {persona name from personas.md}
**I want** {specific capability or action}
**So that** {concrete benefit or outcome}

### Good Examples {#story-good-examples}
- As a **new user**, I want **to reset my password via email** so that **I can regain access without contacting support**.
- As a **team lead**, I want **to see my team's activity summary** so that **I can identify blockers in our standup**.

### Bad Examples {#story-bad-examples}
- As a user, I want a button... (which user? button for what?)
- As a developer, I want clean code... (not user-facing value)
- As a user, I want the system to be fast... (not specific action)

---

## Context {#context}

### Persona Reference {#persona-reference}
- Link to full persona in personas.md
- Include relevant summary (goals, pain points)
- Helps developers understand who they're building for

### Background {#story-background}
- Why does this story exist?
- What led to this need?
- Business context not obvious from Epic

---

## Acceptance Criteria {#acceptance-criteria-guide}

### Given/When/Then Format {#given-when-then-format}
- **Given**: precondition or context
- **When**: action taken
- **Then**: observable outcome

### Guidelines {#ac-guidelines}
- 3-5 criteria per story
- Each criterion independently testable
- Cover happy path AND key edge cases
- Avoid implementation details

### Good Example {#ac-good-example}
```
### AC1: Successful password reset
- **Given** user has a registered email address
- **When** they submit the password reset form
- **Then** they receive a reset link within 5 minutes
```

### Bad Example {#ac-bad-example}
```
### AC1: Works correctly
- **Given** user is logged in
- **When** they use the feature
- **Then** it works
```

---

## Scope {#story-scope}

### In Scope {#story-in-scope}
- What this specific story delivers
- Boundaries prevent scope creep
- Be precise (e.g., "Email reset only, not SMS")

### Out of Scope {#story-out-of-scope}
- Related functionality NOT in this story
- Explicitly state to prevent misunderstandings
- Reference other stories if covered elsewhere

---

## UI/UX Requirements {#ui-ux-requirements}

### When to Include {#when-to-include}
- User-facing functionality
- Visual or interaction requirements
- Accessibility considerations

### What to Include {#what-to-include}
- Wireframe or design references
- Design system components to use
- Behavioural specifications (animations, transitions)
- Responsive requirements

---

## Technical Notes {#technical-notes}

### Purpose {#purpose}
- Guide developers without prescribing solution
- Share relevant context
- Prevent known pitfalls

### API Contracts {#api-contracts}
- Expected request/response shapes
- Error codes and messages
- Authentication requirements

### Data Requirements {#data-requirements}
- Schema changes needed
- Data sources
- Validation rules

---

## Edge Cases & Error Handling {#edge-cases-and-error-handling}

### What to Include {#edge-cases-what-to-include}
- Unusual but valid scenarios
- Error conditions
- Recovery behaviours

### Format {#edge-cases-format}
| Scenario | Expected Behaviour |
|----------|-------------------|
| User submits expired reset link | Show "Link expired" with option to request new |
| Network timeout during submit | Show retry option, preserve form data |

---

## Test Scenarios {#test-scenarios}

### Purpose {#test-scenarios-purpose}
- Key scenarios for QA
- NOT exhaustive test cases
- Helps estimate test effort

### Guidelines {#test-scenarios-guidelines}
- Focus on user journeys
- Include happy path and key edge cases
- Checkbox format for tracking

---

## Definition of Done {#definition-of-done}

### Standard Reference {#standard-reference}
- Link to project-level DoD
- Don't repeat standard items

### Story-Specific Additions {#story-specific-additions}
- Additional criteria for THIS story
- Security review needed?
- Performance benchmark required?
- Specific documentation?

---

## Estimation {#estimation}

### Story Points {#story-points-guide}
- Filled in during team refinement
- Initially `{{TBD}}` from generation
- Fibonacci sequence (1, 2, 3, 5, 8, 13)

### Complexity {#complexity}
- Low: familiar patterns, no unknowns
- Medium: some new elements, manageable risk
- High: significant unknowns, new technology

---

## See Also

- `reference-story.md` - Story workflows (parent document)
- `templates/core/story.md` - Story template
- `reference-philosophy.md#ac-implementation-ready` - AC quality standards
