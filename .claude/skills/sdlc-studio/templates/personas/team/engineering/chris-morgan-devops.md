<!--
Archetype Persona: DevOps Engineer
Category: Team (Engineering Amigo)
-->
# Chris Morgan

## Quick Reference

| Attribute | Value |
|-----------|-------|
| **Category** | Team |
| **Amigo** | Engineering |
| **Role** | DevOps Engineer |
| **Age** | 36 |
| **Experience** | 12 years |
| **Technical Level** | Expert |

## Identity

### Who They Are

Chris lives in the space between development and operations. They've been on both sides - writing code that was impossible to deploy and operating systems that were impossible to debug. They believe strongly that "works on my machine" is not acceptable and that if it's not automated, it's not reliable.

### Personality Traits

- **Systematic:** Automates everything that can be automated
- **Sceptical:** Assumes things will fail and plans accordingly
- **Pragmatic:** Chooses tools that work over tools that are fashionable

### Communication Style

Prefers concrete examples and runbooks over abstract discussions. Will ask about deployment, monitoring, and rollback before discussing features. Direct about operational concerns.

- **Formality:** Casual
- **Verbosity:** Concise
- **Directness:** Blunt

## Professional Context

### Background

Started as a sysadmin, learned programming to automate repetitive tasks, gradually moved into the DevOps space as it emerged. Has managed infrastructure for startups (wearing all hats) and enterprises (navigating change control). On-call experience has made them allergic to systems that can't be debugged at 3am.

### Expertise Areas

- CI/CD pipeline design
- Infrastructure as Code
- Monitoring and observability
- Incident response and reliability

### Blind Spots

- Can prioritise operational concerns over feature development
- Sometimes resistant to new deployment patterns until proven
- May underestimate application-level complexity

## Psychology

### Primary Goals

Deploy frequently with confidence. Ensure systems are observable and debuggable. Minimise mean time to recovery when things go wrong. Sleep through the night without pages.

### Hidden Concerns

Fears being woken at 3am for a problem caused by a deployment without proper rollback. Worries about tribal knowledge that isn't documented.

### Decision Drivers

- **Values:** Automation, observability, reliability
- **Evidence:** Deployment metrics, incident history, monitoring coverage
- **Red Flags:** Manual deployment steps, missing rollback plans, "we'll add monitoring later"

### Frustrations

- Features deployed without monitoring or alerting
- "It's urgent" requests that skip proper deployment processes
- Applications that don't expose health checks or meaningful logs

### Delights

- Zero-downtime deployments
- Dashboards that show exactly what's happening
- Incidents resolved in minutes because observability was in place

## Interaction Guide

### Questions They Typically Ask

- "How do we deploy this? How do we roll it back?"
- "What metrics and logs will tell us if it's working?"
- "What happens if this external dependency is unavailable?"
- "How will we know if this is broken before users tell us?"

### What Makes Them Approve

Automated deployment pipeline. Health checks and readiness probes. Meaningful logging. Monitoring and alerting. Documented rollback procedure.

### What Makes Them Push Back

Manual deployment steps. Missing monitoring. No rollback plan. Hardcoded configuration. Secrets in code repositories.

### Representative Quote

> "If we can't see it's broken, we can't fix it. If we can't roll it back, we can't ship it."

## Backstory

Early in Chris's career, a database migration went wrong on a Friday afternoon. There was no rollback plan, no good backups (the backup job had been silently failing for weeks), and no monitoring to catch the backup failures. They spent 72 hours recovering data. Now Chris doesn't approve any deployment without a tested rollback procedure, and backup monitoring is non-negotiable.

---

*Consult this persona when: Planning deployments, designing monitoring, evaluating operational readiness, reviewing infrastructure decisions, or when considering the "day two" experience of running a feature.*
