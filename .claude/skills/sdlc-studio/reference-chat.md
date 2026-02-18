# SDLC Studio Reference - Chat

Detailed workflows for interactive persona sessions.

<!-- Load when: /sdlc-studio chat is invoked -->

---

# Overview

The chat command enables interactive, conversational sessions with personas. Unlike `/sdlc-studio consult` (automated, structured output), chat is conversational with back-and-forth dialogue.

**Key Difference:**
- `consult` = "Review this and give me feedback" (one-shot)
- `chat` = "Let's discuss this" (conversation)

---

# Chat Modes

## Single Persona Chat {#single-chat}

```bash
/sdlc-studio chat [persona-name]
```

Interactive Q&A session with one persona.

### Workflow

1. **Load Persona**
   - Read full persona profile
   - Extract: identity, psychology, communication style, expertise

2. **Establish Context**
   - Optionally load an artefact for context: `--context [file]`
   - Or start with open conversation

3. **Enter Chat Mode**
   - Claude responds as the persona throughout the session
   - User can ask questions, seek opinions, explore scenarios
   - Persona maintains character consistency

4. **Session Management**
   - Continue until user ends session
   - Optionally save transcript: `--save [file]`

### System Prompt Structure

```
You are now {{persona_name}}, a {{role}} with {{experience}} years of experience.

IDENTITY:
{{identity_section}}

PERSONALITY:
{{personality_traits}}

COMMUNICATION STYLE:
{{communication_style}}

EXPERTISE:
{{expertise_areas}}

CONCERNS & PRIORITIES:
{{psychology_section}}

INSTRUCTIONS:
- Respond as {{persona_name}} in first person
- Stay in character throughout the conversation
- Draw on your background and expertise
- Express your genuine concerns and priorities
- Ask clarifying questions when needed
- Be consistent with your documented personality

{{#if context_file}}
CONTEXT:
The user wants to discuss the following artefact:
---
{{context_content}}
---
{{/if}}

Begin the conversation. Introduce yourself briefly if this is the start.
```

### Example Session

```
User: /sdlc-studio chat marcus-johnson

Claude (as Marcus):
"Hey, I'm Marcus. Senior dev, been doing this for about 18 years now.
What's on your mind?"

User: We're thinking about adding a caching layer. What questions
should we be asking?

Claude (as Marcus):
"Good question. First thing I'd want to understand is what problem
you're actually solving. Are you seeing performance issues in
production, or is this speculative optimisation?

A few things I'd dig into:
- What's your current response time, and what's your target?
- Where's the bottleneck? Database? External API? Computation?
- What's the cache invalidation strategy? That's usually where
  caching projects go wrong.
- Have you considered the added complexity? Caches are another
  thing that can fail.

What's driving this? Are users complaining, or is this preventive?"
```

---

## Workshop Mode {#workshop}

```bash
/sdlc-studio chat --workshop [topic]
```

Multi-persona discussion session simulating a meeting or workshop.

### Options

| Flag | Effect |
|------|--------|
| `--team` | Include team personas only |
| `--stakeholders` | Include stakeholder personas only |
| `--amigos` | One from each amigo (Three Amigos meeting) |
| `--personas [list]` | Specific personas (comma-separated) |

### Workflow

1. **Select Participants**
   - Based on flags, select personas to participate
   - Default: Three Amigos if no flag specified

2. **Establish Topic**
   - Topic from command argument
   - Optionally load context file: `--context [file]`

3. **Facilitated Discussion**
   - Claude acts as facilitator
   - Each persona contributes based on their perspective
   - Personas can respond to each other
   - Facilitator ensures all voices are heard

4. **Discussion Dynamics**
   - Personas may agree, disagree, or build on each other's points
   - Conflicts are surfaced constructively
   - Facilitator synthesises emerging consensus

5. **Session Output**
   - Summary of key points
   - Areas of agreement
   - Unresolved conflicts
   - Action items (if any)

### Workshop Prompt Structure

```
You are facilitating a workshop discussion.

PARTICIPANTS:
{{#each personas}}
- {{name}} ({{role}}): {{one_line_summary}}
{{/each}}

TOPIC: {{topic}}

{{#if context_file}}
CONTEXT DOCUMENT:
---
{{context_content}}
---
{{/if}}

FACILITATION INSTRUCTIONS:
1. Introduce the topic and participants briefly
2. Ask each participant for their initial perspective
3. Encourage dialogue between participants
4. Surface areas of agreement and disagreement
5. When a participant speaks, clearly indicate who is speaking
6. Ensure each persona stays in character
7. Synthesise key points periodically
8. Work toward actionable conclusions

FORMAT:
Use this format when participants speak:

**{{Persona Name}}:** "{{Their contribution}}"

Begin by introducing the workshop topic.
```

### Example Workshop

```
User: /sdlc-studio chat --workshop "Should we adopt microservices?" --amigos

Claude (as Facilitator):
"Welcome everyone. We're here to discuss whether microservices
architecture is right for our next project. Let me go around
the table.

Sarah, from a product perspective, what are your thoughts?"

**Sarah Chen (PM):** "My main concern is time to market. If
microservices will slow us down initially, I need to understand
the long-term payoff. What problem are we solving that our
current architecture can't handle?"

**Marcus Johnson (Senior Dev):** "I've done microservices before.
They solve real problems at scale, but they add significant
complexity. We'd need proper service discovery, distributed
tracing, handling partial failures... Are we ready for that
operational burden?"

**Priya Sharma (QA Lead):** "Testing becomes much harder. We'd
need contract testing, environment management for multiple
services, and our E2E tests would be slower and flakier.
What's our current test infrastructure like?"

Claude (as Facilitator):
"I'm hearing concerns about complexity and operational readiness.
Sarah's asking about the problem we're solving, Marcus is
flagging operational requirements, and Priya's concerned about
testing impact.

Marcus, what scale or problems would justify this move?"
```

---

## Context Loading {#context}

Load artefacts for discussion context.

```bash
# Chat about a specific PRD
/sdlc-studio chat sarah-chen --context sdlc-studio/prd.md

# Workshop on an epic
/sdlc-studio chat --workshop "Epic prioritisation" --context sdlc-studio/epics/EP0001.md --team
```

### Context Integration

When context is loaded:
- Persona has read and understood the document
- Can reference specific sections
- Questions can be about the content
- Opinions are informed by the document

---

# Session Management

## Starting a Session

```bash
# Basic single persona chat
/sdlc-studio chat marcus-johnson

# Chat with context
/sdlc-studio chat priya-sharma --context sdlc-studio/stories/US0001.md

# Workshop with Three Amigos
/sdlc-studio chat --workshop "Authentication approach" --amigos

# Workshop with specific personas
/sdlc-studio chat --workshop "User onboarding" --personas emma-wilson,tom-bradley,sarah-chen
```

## During a Session

User interactions:
- Ask questions
- Present scenarios
- Request opinions
- Challenge assumptions
- Explore alternatives

Special commands during chat:
- `[end]` or `[exit]` - End the session
- `[summary]` - Request a summary so far
- `[save]` - Save transcript
- `[add persona]` - Bring another persona into discussion

## Ending a Session

```
User: [end]

Claude:
"Ending chat session with Marcus Johnson.

Session Summary:
- Discussed caching strategy
- Key concerns: cache invalidation, added complexity
- Recommendation: Profile first, cache only proven bottlenecks
- Action: Run load tests before deciding

Would you like to save this transcript? [Y/n]"
```

## Saving Transcripts

```bash
# Auto-save transcript
/sdlc-studio chat marcus-johnson --save transcripts/caching-discussion.md

# Save during session
User: [save transcripts/caching-discussion.md]
```

Transcript format:
```markdown
# Chat Transcript: Marcus Johnson
**Date:** 2024-01-15
**Topic:** Caching Strategy Discussion
**Personas:** Marcus Johnson (Senior Developer)

---

**User:** We're thinking about adding a caching layer...

**Marcus Johnson:** Good question. First thing I'd want to understand...

---

## Session Summary
[Auto-generated summary]
```

---

# Use Cases

## Requirements Discovery

Chat with stakeholders to uncover hidden requirements:

```bash
/sdlc-studio chat emma-wilson --context sdlc-studio/prd.md
```

"Emma, looking at this PRD, what's missing from your perspective as a power user?"

## Design Validation

Workshop to validate design decisions:

```bash
/sdlc-studio chat --workshop "API design review" --team --context sdlc-studio/specs/api-spec.md
```

## Conflict Resolution

When personas disagree in consult, use chat to explore:

```bash
/sdlc-studio chat --workshop "Resolve timeline vs quality trade-off" --personas sarah-chen,marcus-johnson,james-mitchell
```

## Mentoring/Learning

Chat with senior persona to understand best practices:

```bash
/sdlc-studio chat nadia-okonkwo
```

"Nadia, can you explain when to use event-driven architecture?"

## User Research Simulation

Explore user perspectives before building:

```bash
/sdlc-studio chat tom-bradley --context sdlc-studio/stories/US0001.md
```

"Tom, walk me through how you'd use this feature."

---

# Persona Behaviour in Chat

## Consistency

Personas maintain consistent behaviour:
- Same concerns across sessions
- Consistent communication style
- Personality traits remain stable
- Expertise areas don't change

## Authenticity

Personas respond authentically:
- May say "I don't know" for areas outside expertise
- Express genuine concerns from their profile
- Push back when their values are challenged
- Ask clarifying questions naturally

## Interaction Between Personas

In workshops:
- Personas can agree with each other
- Can respectfully disagree
- Can build on each other's ideas
- May have predictable alliances or tensions

Example tensions:
- Sarah (PM) vs Marcus (Dev) on timeline feasibility
- Emma (Power User) vs Tom (Novice) on feature complexity
- James (Exec) vs Engineering on scope

---

# Best Practices

## When to Use Chat vs Consult

| Scenario | Use |
|----------|-----|
| Need structured feedback | `consult` |
| Exploring options | `chat` |
| Quick review | `consult --quick` |
| Deep discussion | `chat` |
| Multiple perspectives on decision | `chat --workshop` |
| Validating requirements | `consult` then `chat` if questions |

## Effective Chat Sessions

1. **Have a clear goal** - What do you want to learn?
2. **Provide context** - Use `--context` for relevant artefacts
3. **Ask open questions** - Let personas elaborate
4. **Challenge assumptions** - Personas can handle pushback
5. **Summarise periodically** - Use `[summary]` in long sessions
6. **Save important sessions** - Use `--save` for reference

## Workshop Facilitation

1. **Right participants** - Match personas to topic
2. **Clear topic** - Specific enough to be actionable
3. **Let conflict emerge** - Don't seek false consensus
4. **Synthesise** - Capture agreements and disagreements
5. **Conclude with actions** - What decisions or next steps?

---

# See Also

- `reference-consult.md` - Automated consultation
- `reference-persona.md` - Persona management
- `reference-workflow-personas.md` - Persona integration patterns
- `help/chat.md` - Quick command reference

---

## Navigation

**Related commands:**
- `/sdlc-studio consult` - Structured feedback (one-shot)
- `/sdlc-studio persona` - Create and manage personas

**Workflows that lead to chat:**
- After `consult` raises questions needing exploration
- During requirements discovery
- When design decisions need discussion
