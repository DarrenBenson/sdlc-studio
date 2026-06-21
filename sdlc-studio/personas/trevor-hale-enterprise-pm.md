# Trevor Hale

> The anti-persona - stated so we know who we are deliberately *not* designing for.

## Quick Reference

| Attribute | Value |
| --- | --- |
| **Cast role** | Negative |
| **Role** | Delivery manager in a large enterprise programme |
| **Context** | Runs a multi-team programme through a GUI work-tracker and a governance board |

## Who They Are

Trevor coordinates several teams through a corporate work-tracker. He does not write code and does
not use a terminal; he lives in boards, dashboards, and steering meetings. He needs heavyweight
governance - approval chains, RACI, portfolio roll-ups, audit trails for compliance - and he is
not willing to let an autonomous agent make changes without a human gate at every step.

## End Goals (stated to exclude)

*Trevor's goals are real, but serving them would pull the product away from its Primary. We say no on purpose.*

1. Drive delivery from a rich GUI with boards, swimlanes, and portfolio dashboards
2. Enforce multi-stage human approval and sign-off gates on every change
3. Integrate with the corporate stack (SSO, the enterprise tracker, compliance reporting)
4. Govern many teams centrally, with non-technical staff operating the tool

## Why We Are Not Designing For Him

sdlc-studio is files + an agent + a CLI, built for one operator or a small team who trust a
disciplined autonomous loop. Trevor needs a GUI, central governance, and a human gate on every
action - the opposite of the value here. Chasing his needs would add boards, role hierarchies,
and approval ceremony that would ruin the product for Maya. His requirements are a **clear signal
to decline**, not a backlog.

## Behaviours & Context

- **Environment:** a browser, an enterprise work-tracker, recurring governance meetings
- **Frequency:** continuous oversight across teams; never hands-on in a repo
- **Proficiency:** strong in process and reporting; will not use a CLI or trust an unattended agent

## Frustrations

*What he would (legitimately) dislike about sdlc-studio - and why that is fine.*

- No GUI, boards, or portfolio view - intentional; sdlc-studio is file-and-agent driven
- An autonomous loop that commits without a human gate at each step - intentional; the loop is the point
- No central multi-team governance layer - out of scope by design

## Scenario

*How a request from Trevor should be handled.*

Trevor asks for an approval-board view and per-change sign-off gates wired to the corporate
tracker. The right response is to recognise this as the Negative persona and decline: it serves a
user the product is not for, and building it would degrade the experience for the Primary. Note
the request, point him at an enterprise tool that fits, and keep sdlc-studio lean.

---

- This persona exists to **bound** the design. When a feature only serves Trevor, that is a reason to say no.
