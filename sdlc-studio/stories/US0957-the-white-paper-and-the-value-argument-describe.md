# US0957: The white paper and the value argument describe the v6 operating model

> **Status:** Draft
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** docs/whitepaper.md, docs/whitepaper.pdf, docs/why-sdlc-studio.md, tools/tests/test_lean_public_docs_retired.py, changelog.d/US0957.md
> **Epic:** EP0266
> **Points:** 5
> **Persona:** Jonah Reyes

## User Story

**As a** team lead evaluating whether to adopt an agentic lifecycle
**I want** the white paper, its PDF and the value argument to describe the process v6 runs, including what it deleted and why
**So that** the case I take to my team matches the tool they will install

## Acceptance Criteria

- **AC1:** Given docs/whitepaper.md and docs/why-sdlc-studio.md, then neither names a retired surface from U3's derived union or the retired phrases (depth tiers, attestation ledger of sign-offs, the plan's independent review gate) except in a passage saying it was removed and why. Fails on: HEAD (whitepaper 145, 147, 224, 310, 356-359, 394, 475; why 70, 72, 79, 124)
  - **Verify:** pytest tools/tests/test_lean_public_docs_retired.py::PublicDocsTests::test_the_value_docs_teach_no_retired_surface
- **AC2:** Given the white paper, then its version line names v6, it carries a section on the ratchet citing its sources (82% of the last 116 units served the machinery; plan review 60% REJECT, 255 of 428; what was deleted), and its claims register has no row for a deleted gate. Fails on: a version bump with the claims register still citing `transition.py` for depth-gated closes
  - **Verify:** pytest tools/tests/test_lean_public_docs_retired.py::PublicDocsTests::test_the_whitepaper_is_v6_and_carries_the_ratchet
- **AC3:** Given docs/whitepaper.pdf, when its text is extracted, then it carries the markdown's v6 version line. Fails on: shipping the 2026-07-10 v4 PDF under a v6 README
  - **Verify:** shell pdftotext docs/whitepaper.pdf - | grep -q 'v6'

## Notes

- Depends on: US0954
- Operator ruling: regenerate the PDF with `tools/whitepaper_pdf.py` from a scratch venv (`python3 -m venv`, `pip install markdown weasyprint`); weasyprint is not installed on this machine (measured). The venv lives in scratch, never in the repo. pdftotext is at /usr/bin/pdftotext.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (D1) |
