---
id: LL0007
title: Plan from value, not bare priority; a Ready story whose verifiers pass is already done
tags: [sprint, planning, wsjf, personas, conformance]
added: 2026-06-24
origin: dogfooded sprint-planning run, 2026-06-24
---

**Lesson.** **Lesson.** Two planning disciplines. (1) Before selecting a sprint, flag any Ready unit whose executable ACs already pass - it is already delivered (often under a different artifact); close it, do not queue it to build. The tranche audit only checks mechanical readiness (weak-AC, unmet-deps, terminal, links), not 'already satisfied' - but a green verifier set is a deterministic signal of it. (2) Sprint planning is a value/effort/risk judgement, not a bare-priority sort: consult the Product Owner seat for value (+ time-criticality, risk-reduction), the Engineering seat for effort (seeded by the complexity signal), the QA seat for risk - the WSJF inputs. Order by WSJF, not the Priority field alone.\n\n**Why / what it cost.** A dogfooded plan queued five Ready stories the audit passed as ready; their verifiers all passed - the features had shipped under CRs and the records were never transitioned. Estimates/priorities set solo by one agent miss the value/risk perspective the review seats exist to provide.\n\n**How to apply.** Reconcile before plan; run the verifiers and treat all-green Ready units as close-candidates; at the plan rung consult the PO/Eng/QA seats and order by WSJF.\n\n**Generalises to.** Any backlog-driven project with executable ACs and a review-seat/persona model.

**Why / what it cost.** {{the failure or friction that taught it}}

**How to apply.** {{the concrete check or habit that prevents recurrence}}

**Generalises to.** {{the class of situations this covers – when to recall it}}
