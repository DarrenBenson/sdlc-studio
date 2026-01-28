# Epic Section Reference

Detailed guidance for completing each section of the Epic template.

<!-- Load when: filling out epic template sections in detail -->

---

## Summary {#summary}

### What to Include {#summary-what-to-include}
- 2-3 sentences describing what this Epic delivers
- Written for someone unfamiliar with the project
- Focus on user value, not technical implementation

### What to Avoid {#summary-what-to-avoid}
- Technical jargon without explanation
- Implementation details (save for stories)
- Vague statements like "improve the system"

---

## Business Context {#business-context}

### Problem Statement {#problem-statement}
- Extract from PRD's Problem Statement
- Focus on the specific aspect this Epic addresses
- Reference PRD section for traceability

### Value Proposition {#value-proposition}
- What happens if we DO this?
- What happens if we DON'T?
- Quantify where possible

### Success Metrics {#success-metrics}
- Must be measurable
- Include baseline (current state) even if "N/A"
- Specify how measurement will occur
- Examples: completion rate, time reduction, error rate

---

## Scope {#scope}

### In Scope {#in-scope}
- Be specific about what's included
- List features, not implementation details
- Helps prevent scope creep

### Out of Scope {#out-of-scope}
- Explicitly state exclusions
- Include brief rationale (helps prevent arguments later)
- Can reference "future Epic" if planned

### Affected Personas {#affected-personas}
- Link to personas.md
- Describe HOW this Epic affects each persona
- Helps prioritise and validate stories

---

## Acceptance Criteria (Epic Level) {#acceptance-criteria}

### Format {#ac-format}
- High-level, observable outcomes
- Use checkboxes for tracking
- NOT detailed Given/When/Then (save for stories)

### Good Examples {#ac-good-examples}
- [ ] Users can complete registration without assistance
- [ ] Dashboard loads within 2 seconds
- [ ] All data is encrypted at rest

### Bad Examples {#ac-bad-examples}
- [ ] Code is written (too vague)
- [ ] Tests pass (that's DoD, not AC)
- [ ] Given user clicks button, When... (too detailed for Epic)

---

## Dependencies {#dependencies}

### Blocked By {#blocked-by}
- Other Epics that must complete first
- External systems or APIs
- Data migrations or infrastructure
- Include impact notes (what happens if delayed)

### Blocking {#blocking}
- What's waiting on this Epic
- Helps prioritise and communicate urgency
- Include consequence of delay

---

## Risks & Assumptions {#risks-and-assumptions}

### Assumptions {#assumptions}
- What are we taking for granted?
- Each should be validateable
- If assumption proves wrong, impact should be assessed

### Risks {#risks}
- Technical risks (new technology, integration)
- Business risks (user adoption, market timing)
- Resource risks (availability, skills)
- Include likelihood/impact for prioritisation
- Must have mitigation strategy

---

## Technical Considerations {#technical-considerations}

### Architecture Impact {#architecture-impact}
- Does this require new services?
- Significant refactoring needed?
- Infrastructure changes?
- Keep high-level (details in stories)

### Integration Points {#integration-points}
- External APIs and services
- Internal system boundaries
- Authentication/authorisation touchpoints

### Data Considerations {#data-considerations}
- New data models
- Migrations required
- Data dependencies from other systems

---

## Sizing & Effort {#sizing-and-effort}

### Story Points {#story-points}
- Relative sizing (1, 2, 3, 5, 8, 13, 21)
- Based on complexity, not time
- Compare to reference Epics

### Story Count {#story-count}
- Estimate range (e.g., "8-12 stories")
- Helps sprint planning
- Refine after story generation

### Complexity Factors {#complexity-factors}
- What makes this harder than it looks?
- New technology, integrations, unknowns
- Helps justify sizing

---

## Story Breakdown {#story-breakdown}

### Before Story Generation {#before-story-generation}
- Provisional titles only
- Use `- [ ] US{{TBD}}: {Title}`

### After Story Generation {#after-story-generation}
- Updated automatically by `/sdlc-studio story`
- Links to actual story files
- Status tracked via story files

---

## See Also

- `reference-epic.md` - Epic workflows (parent document)
- `templates/core/epic.md` - Epic template
- `reference-prd.md` - PRD workflows (upstream)
