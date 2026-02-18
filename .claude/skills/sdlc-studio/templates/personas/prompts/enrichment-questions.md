<!--
Template: Persona Enrichment Questions
Usage: Interactive questions to enrich discovered personas
Modes: quick, standard, thorough
-->

# Persona Enrichment: {{persona_name}}

Let's add depth to this persona.

---

## Quick Mode Questions

### 1. Category

Is this a **Team** persona or **Stakeholder**?

| Option | Description |
|--------|-------------|
| **Team** | Internal team member - will be assigned to an amigo (Product/Engineering/QA) |
| **Stakeholder** | External user or business stakeholder |

### 2. Human Name

What name should we use for this persona?

- Current identifier: `{{code_identifier}}`
- Suggestion: {{suggested_name}}
- Or enter custom name: ___

### 3. One-Line Summary

In one sentence, what does this persona need to accomplish?

### 4. Primary Goal

What does success look like for this persona?

---

## Standard Mode Questions (adds to Quick)

### 5. Type/Amigo

{{#if is_team}}
Which amigo does this persona belong to?

| Amigo | Focus | Choose if... |
|-------|-------|--------------|
| **Product** | What & Why | Makes product decisions, defines requirements |
| **Engineering** | How | Builds solutions, technical decisions |
| **QA** | What If | Tests, validates, finds edge cases |
{{else}}
What type of stakeholder is this?

| Type | Choose if... |
|------|--------------|
| **User** | Uses the product directly |
| **Business** | Business stakeholder (exec, operations, finance) |
| **Technical** | Technical stakeholder (security, compliance, infrastructure) |
{{/if}}

### 6. Experience Level

| Level | Years | Choose if... |
|-------|-------|--------------|
| Junior/Entry | 1-3 | New to role, learning |
| Mid-level | 4-7 | Competent, independent |
| Senior | 8-15 | Experienced, mentors others |
| Executive | 15+ | Strategic, organisational scope |

### 7. Technical Proficiency

| Level | Description |
|-------|-------------|
| Novice | Needs guidance, follows instructions |
| Intermediate | Comfortable with standard features |
| Advanced | Uses advanced features, some customisation |
| Expert | Power user, automation, deep knowledge |

### 8. Top 3 Frustrations

What frustrates this persona most? (from the source analysis or your knowledge)

1. ___
2. ___
3. ___

### 9. Decision Style

How does this persona make decisions?

| Style | Description |
|-------|-------------|
| Data-driven | Needs metrics, evidence, analysis |
| Intuition | Trusts experience and gut feel |
| Consensus | Seeks input from others before deciding |
| Authority | Defers to higher authority or policy |

### 10. Representative Quote

What would this persona say that captures their mindset?

> "___"

---

## Thorough Mode Questions (adds to Standard)

### 11. Full Background

In 2-3 sentences, describe this persona's career path and what shaped their current perspective.

### 12. Personality Traits

List 3 personality traits and how each manifests in their work:

| Trait | How it shows up |
|-------|-----------------|
| ___ | ___ |
| ___ | ___ |
| ___ | ___ |

### 13. Communication Style

| Aspect | Options |
|--------|---------|
| Formality | Formal / Casual / Adaptive |
| Verbosity | Concise / Moderate / Detailed |
| Directness | Blunt / Diplomatic / Measured |

### 14. Expertise Areas

What are this persona's areas of deep knowledge? (3-5 items)

### 15. Blind Spots

What might this persona miss or undervalue? (2-3 items)

### 16. Hidden Concerns

What worries this persona that they might not voice openly?

### 17. Decision Drivers

| Driver | Description |
|--------|-------------|
| Values | What matters most to them |
| Evidence | What type of evidence convinces them |
| Red Flags | What makes them nervous or sceptical |

### 18. Delights

What makes this persona enthusiastic? (2-3 items)

### 19. Typical Questions

What questions does this persona typically ask? (3-5)

- "___?"
- "___?"
- "___?"

### 20. Approval Criteria

What makes this persona approve something?

### 21. Rejection Triggers

What makes this persona push back or reject?

### 22. Backstory Incident

Describe a specific past experience that shaped this persona's viewpoint. (This humanises them and explains why they hold certain positions.)

---

## Archetype Match Check

{{#if archetype_match}}
This persona seems similar to an existing archetype:

**{{archetype_name}}**
- Role: {{archetype_role}}
- Focus: {{archetype_focus}}
- Match confidence: {{match_confidence}}%

Would you like to:

| Option | Description |
|--------|-------------|
| **Use archetype** | Start from {{archetype_name}}, customise for this project |
| **Create new** | Build a distinct persona (you've provided enough unique detail) |
| **Compare** | Show me the archetype details to decide |
{{/if}}
