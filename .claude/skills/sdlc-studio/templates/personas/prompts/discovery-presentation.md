<!--
Template: Persona Discovery Presentation
Usage: Present discovered personas to user for confirmation
Variables: {{source_type}}, {{explicit_personas}}, {{inferred_personas}}
-->

# Persona Discovery Results

I've analysed the {{source_type}} and found these potential personas:

---

## Explicit Personas (named in source)

{{#each explicit_personas}}
### {{index}}. {{name}}

**Mentioned:** {{mention_count}} times

**Evidence:**
{{#each evidence}}
- {{location}}: "{{quote}}"
{{/each}}

**Inferred profile:**
- Likely role: {{inferred_role}}
- Technical level: {{inferred_tech_level}}
- Key capabilities: {{capabilities}}

---
{{/each}}

## Inferred Personas (implied but not named)

{{#each inferred_personas}}
### {{index}}. {{suggested_name}}

**Inferred from:** {{inference_source}}

**Evidence:**
{{#each evidence}}
- {{location}}: {{description}}
{{/each}}

**Suggested profile:**
- Likely role: {{inferred_role}}
- Reason: {{inference_reason}}

---
{{/each}}

## Confirmation

Should I proceed with these personas?

| Option | Description |
|--------|-------------|
| **Yes** | Continue with enrichment for all listed personas |
| **Add more** | I'll suggest additional personas to consider |
| **Remove some** | Tell me which to skip |
| **Start over** | Re-analyse with different parameters |
