<!--
Load: On /sdlc-studio chat or /sdlc-studio chat help
Dependencies: SKILL.md (always loaded first)
Related: reference-chat.md, reference-persona.md, reference-consult.md
-->

# /sdlc-studio chat - Interactive Persona Sessions

> **Source of truth:** `reference-chat.md` - Detailed workflow steps

Have conversations with personas for requirements discovery, design validation, and decision-making.

## Quick Reference

```bash
/sdlc-studio chat [persona]                    # Chat with one persona
/sdlc-studio chat --workshop [topic]           # Multi-persona discussion
/sdlc-studio chat --workshop [topic] --amigos  # Three Amigos meeting
/sdlc-studio chat --workshop [topic] --team    # All team personas
```

## How It Works

1. Claude loads the persona's full profile
2. Responds "in character" throughout the session
3. You can ask questions, explore scenarios, seek opinions
4. Session continues until you end it

**Key Difference from `/sdlc-studio consult`:**
- `consult` = Automated review, structured output
- `chat` = Interactive conversation, back-and-forth

---

## Modes

### Single Persona Chat

```bash
/sdlc-studio chat marcus-johnson
```

Talk to one persona. Good for:
- Deep-diving into their perspective
- Exploring technical approaches (with engineers)
- Understanding user needs (with user personas)
- Getting mentorship on best practices

**Example:**
```
User: /sdlc-studio chat marcus-johnson

Marcus: "Hey, I'm Marcus. Senior dev, 18 years in the game.
What's on your mind?"

User: We're debating between REST and GraphQL for our new API.

Marcus: "What's driving the decision? If you've got a lot of
different clients needing different data shapes, GraphQL can
help. But if your API is straightforward CRUD, REST is simpler
and your team probably knows it better..."
```

### Workshop Mode

```bash
/sdlc-studio chat --workshop "Should we adopt microservices?"
```

Multi-persona discussion. Good for:
- Getting diverse perspectives on decisions
- Simulating stakeholder meetings
- Surfacing conflicts early
- Building consensus

**Participant flags:**

| Flag | Who Participates |
|------|------------------|
| `--amigos` | One from each: Product, Engineering, QA |
| `--team` | All team personas |
| `--stakeholders` | All stakeholder personas |
| `--personas [list]` | Specific personas (comma-separated) |

**Example:**
```bash
/sdlc-studio chat --workshop "MVP scope" --amigos

# Workshop with specific people
/sdlc-studio chat --workshop "Onboarding UX" --personas emma-wilson,tom-bradley,sarah-chen
```

---

## Options

### Context Loading

Load an artefact for the discussion:

```bash
# Discuss a PRD
/sdlc-studio chat sarah-chen --context sdlc-studio/prd.md

# Workshop on an epic
/sdlc-studio chat --workshop "Epic sizing" --context sdlc-studio/epics/EP0001.md --team
```

### Saving Transcripts

```bash
# Save automatically
/sdlc-studio chat marcus-johnson --save transcripts/caching-chat.md

# Save during session
User: [save transcripts/my-session.md]
```

---

## Session Commands

During a chat session, special commands:

| Command | Effect |
|---------|--------|
| `[end]` or `[exit]` | End the session |
| `[summary]` | Get summary of discussion so far |
| `[save filename]` | Save transcript to file |
| `[add persona-name]` | Bring another persona into discussion |

---

## Examples

### Requirements Discovery

```bash
# Explore what a power user needs
/sdlc-studio chat emma-wilson --context sdlc-studio/prd.md
```

"Emma, looking at this PRD, what features would make your daily work significantly easier?"

### Design Validation

```bash
# Team review of API design
/sdlc-studio chat --workshop "API design" --team --context specs/api-design.md
```

### Conflict Resolution

```bash
# When consult showed disagreement
/sdlc-studio chat --workshop "Timeline vs quality trade-off" --personas sarah-chen,marcus-johnson
```

### Learning/Mentoring

```bash
# Learn from the architect
/sdlc-studio chat nadia-okonkwo
```

"Nadia, when should we consider event-driven architecture over request-response?"

### User Research Simulation

```bash
# Walk through a feature as a novice
/sdlc-studio chat tom-bradley --context sdlc-studio/stories/US0001.md
```

"Tom, can you walk me through how you'd use this feature step by step?"

---

## When to Use Chat vs Consult

| Need | Use |
|------|-----|
| Structured feedback on artefact | `consult` |
| Exploring options or ideas | `chat` |
| Quick approval/rejection | `consult --quick` |
| Deep discussion | `chat` |
| Multiple perspectives on decision | `chat --workshop` |
| Validating requirements | `consult`, then `chat` if questions arise |

---

## Best Practices

1. **Have a goal** - Know what you want to learn
2. **Provide context** - Use `--context` with relevant artefacts
3. **Ask open questions** - Let personas elaborate
4. **Challenge assumptions** - Personas can handle pushback
5. **Save important sessions** - Use `--save` for reference

### For Workshops

1. **Right participants** - Match personas to topic
2. **Clear topic** - Specific enough to be actionable
3. **Let conflict emerge** - Don't seek false consensus
4. **Conclude with actions** - What decisions or next steps?

---

## Prerequisites

Personas must exist in `sdlc-studio/personas/`. If not:

```bash
/sdlc-studio persona create    # Create interactively
/sdlc-studio persona generate  # Generate from PRD/code
```

---

## See Also

**Workflows:**
- `reference-chat.md` - Detailed chat workflows
- `reference-consult.md` - Automated consultation

**Related commands:**
- `/sdlc-studio consult help` - Structured feedback
- `/sdlc-studio persona help` - Persona management
