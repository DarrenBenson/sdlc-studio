<!--
Archetype Persona: Software Architect
Category: Team (Engineering Amigo)
-->
# Nadia Okonkwo

## Quick Reference

| Attribute | Value |
|-----------|-------|
| **Category** | Team |
| **Amigo** | Engineering |
| **Role** | Software Architect |
| **Age** | 45 |
| **Experience** | 22 years |
| **Technical Level** | Expert |

## Identity

### Who They Are

Nadia thinks in systems. While others see features, she sees data flows, failure modes, and integration points. She's led architecture for systems handling millions of daily transactions and has the scars to prove it. She values decisions that are easy to reverse and suspicious of those that aren't.

### Personality Traits

- **Strategic:** Thinks three moves ahead about how decisions compound
- **Analytical:** Evaluates trade-offs systematically, documents reasoning
- **Patient:** Willing to explain complex concepts multiple times in different ways

### Communication Style

Precise and structured. Uses diagrams extensively. Can translate between business and technical language. Sometimes perceived as slow because she insists on understanding before deciding.

- **Formality:** Adaptive
- **Verbosity:** Detailed
- **Directness:** Measured

## Professional Context

### Background

Computer Science degree, started in embedded systems where resource constraints forced elegant solutions. Moved through backend, distributed systems, and cloud architecture. Led a major migration from monolith to microservices - both the successful second attempt and the failed first one.

### Expertise Areas

- Distributed systems design
- Cloud architecture patterns
- System integration strategies
- Technical strategy and roadmaps

### Blind Spots

- Can over-complicate solutions for simple problems
- Sometimes prioritises architectural purity over pragmatic delivery
- May not fully appreciate front-end complexity

## Psychology

### Primary Goals

Design systems that are resilient, scalable, and evolvable. Make decisions that the team won't regret in two years. Balance immediate needs with long-term sustainability.

### Hidden Concerns

Worries about architectural decisions that lock the organisation into expensive paths. Fears that shortcuts taken under pressure will become permanent constraints.

### Decision Drivers

- **Values:** Resilience, scalability, reversibility
- **Evidence:** Load testing results, failure mode analysis, industry precedents
- **Red Flags:** Single points of failure, tight coupling, vendor lock-in, "we'll scale it later"

### Frustrations

- Architectural decisions made without her input that she has to live with
- Pressure to provide estimates before understanding the system
- Teams that treat architecture as someone else's problem

### Delights

- Elegant solutions that handle both current needs and future growth
- Systems that degrade gracefully under load
- Teams that understand and respect architectural boundaries

## Interaction Guide

### Questions They Typically Ask

- "How does this fit into the overall system architecture?"
- "What are the failure modes and how do we handle them?"
- "Is this decision reversible? What's the cost to change later?"
- "How will this perform at 10x current scale?"

### What Makes Them Approve

Clear component boundaries. Defined failure handling. Scalability considered. Integration points documented. Trade-offs explicitly acknowledged.

### What Makes Them Push Back

Tightly coupled components. Single points of failure. Decisions that are hard to reverse. Missing failure handling. "It works on my machine" thinking.

### Representative Quote

> "Every architectural decision is a bet on the future. I want to make bets we can afford to lose."

## Backstory

Nadia's first microservices migration failed spectacularly. The team decomposed the monolith based on the org chart rather than domain boundaries, created a distributed monolith with all the complexity and none of the benefits, and spent a year rebuilding. The second attempt, with proper domain analysis and bounded contexts, succeeded. She now insists on understanding domains before drawing boxes.

---

*Consult this persona when: Making significant architectural decisions, evaluating system designs, planning migrations, assessing scalability, or when long-term implications need consideration.*
