# US1339: The skill says the person owns the PRD and the PVD, and the seat checks the work under delegated authority

> **Status:** Done
> **Risk-class:** standard
> **Delivers:** CR0755
> **Created:** 2026-11-26
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-prd.md, .claude/skills/sdlc-studio/reference-pvd.md, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/reference-workflow-personas.md, .claude/skills/sdlc-studio/reference-persona.md, .claude/skills/sdlc-studio/help/pvd.md, .claude/skills/sdlc-studio/templates/personas/amigo-template.md, .claude/skills/sdlc-studio/templates/personas/review-seat-charter.md, tools/tests/test_lean_ownership_wording.py, changelog.d/US1339.md
> **Epic:** EP0384
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** head of engineering who answers for every release at the change board (Abena)
**I want** the skill to say that a person owns the PRD and the PVD, and that the seat checks the
work against each under authority that person delegates
**So that** every specification names an accountable person, not 'the agent', and the skill, its
explainer and its website give one owner for each document

The skill says a seat owns the PRD and the PVD, while the explainer and the website say the
person in each role owns each document and the seat reviews work against it, so a reader finds
two owners for one document. Every shipped page and seat-card template that says a seat owns a
requirements document, or calls a seat a document owner, is reworded so the person owns every
document (the PRD, the PVD, the TRD, the TSD and the personas). The Product Owner or Product
Manager seat is accountable, with authority the person delegates, for checking the work
satisfies its document; it signs that document's review leg and asks the person when unsure.
The seats section and its anchor are renamed, the three links into it updated, and the reading
guides regenerated. The PVD page also stops calling the Product Manager a persona: it is a seat.

## Acceptance Criteria

### AC1: No page says a seat owns the PRD or the PVD

- **Given** the PRD page (reference-prd.md), the PVD page (reference-pvd.md) and `pvd help`
  (help/pvd.md)
- **When** each is read with blockquote marks and bold markup stripped and its lines joined
- **Then** none says a seat or a persona owns the PRD or the PVD, and the PRD and PVD pages each
  say the person owns the document. Fails on: "The PRD is owned by the Product Owner seat"
  (reference-prd.md:201); "owned by" then "the **Product Manager** persona (the PRD stays owned
  by the Product Owner)" (reference-pvd.md:18-19, split across a line break and bold);
  "(Product Manager owns it)" (help/pvd.md:28).
- **Verify:** pytest tools/tests/test_lean_ownership_wording.py::OwnershipWordingTests::test_no_page_says_a_seat_owns_the_prd_or_the_pvd
- **Verified:** yes (2026-11-26)

### AC2: The review legs say the seat signs under delegated authority

- **Given** the unified review's PVD and PRD legs (reference-review.md)
- **When** each leg's "requirements satisfied" verdict is read
- **Then** each says its seat signs the verdict under authority the person delegates, and
  neither says a seat owns it. Fails on: "The Product Manager seat owns this"
  (reference-review.md:137); "The Product Owner seat owns this" (reference-review.md:153); no
  "delegat" anywhere in lines 124-157.
- **Verify:** pytest tools/tests/test_lean_ownership_wording.py::OwnershipWordingTests::test_the_review_legs_say_the_seat_signs_under_delegated_authority
- **Verified:** yes (2026-11-26)

### AC3: The seats section names the person as owner and the seat as delegate

- **Given** the section of reference-workflow-personas.md that defines the Product Owner and
  Product Manager seats
- **When** it is read
- **Then** it says the person owns every document the skill keeps (the PRD, the PVD, the TRD,
  the TSD and the personas), that each seat is accountable, with authority the person
  delegates, for checking the work satisfies its document and signs that document's review leg,
  and that the seat asks the person when unsure; no column of its table is headed Owns. Fails
  on: the heading "### Document-owner seats" (line 117); the header row
  "| Seat | Owns | Accountable for | Applies |" (line 122); a section (lines 117-132) with no
  "delegat", no "unsure" and no sentence naming the person as owner.
- **Verify:** pytest tools/tests/test_lean_ownership_wording.py::OwnershipWordingTests::test_the_seats_section_names_the_person_as_owner_and_the_seat_as_delegate
- **Verified:** yes (2026-11-26)

### AC4: No shipped page or template calls a seat a document owner

- **Given** every markdown page and template under .claude/skills/sdlc-studio/
- **When** each is searched for a seat named as a document's owner, and every link into
  reference-workflow-personas.md is resolved
- **Then** no seat is called a document owner, and every link into
  reference-workflow-personas.md names an anchor that page defines. Fails on: "document-owner"
  or "document owner" at reference-workflow-personas.md:10 (the reading guide), :78 and :117,
  reference-prd.md:204, reference-pvd.md:21, reference-persona.md:44, amigo-template.md:6, :27
  and :62, and review-seat-charter.md:5 and :18; "PO/PM owners" at reference-persona.md:39.
- **Verify:** pytest tools/tests/test_lean_ownership_wording.py::OwnershipWordingTests::test_no_shipped_page_calls_a_seat_a_document_owner
- **Verified:** yes (2026-11-26)

### AC5: The wording test proves it can fail

- **Given** the wording test module
- **When** its forbidden patterns are run against a planted sentence carrying the old wording
  and against a compliant one ("The person owns the PRD; the Product Owner seat signs its review
  leg")
- **Then** each pattern matches the planted sentence, none matches the compliant one, and the
  corpus the module reads is not empty. Fails on: no such module at HEAD
  (`ls tools/tests | grep -E "^test_lean_(ownership|document|seat_change)"` prints nothing), so
  nothing guards against a pattern that has stopped matching.
- **Verify:** pytest tools/tests/test_lean_ownership_wording.py::OwnershipWordingTests::test_the_patterns_fail_on_a_planted_owner_sentence
- **Verified:** yes (2026-11-26)

## Notes

- Serves: Abena Osei, End goal 2, verbatim from her card: "Every specification and every change
  names an accountable person, not 'the agent'". Graham Doyle's End goal 1 (approve from one
  document showing who reviewed independently and who is accountable) is served beside it.
- Suggested wording, for the builder to improve; the tests pin meaning, not exact prose:
  - reference-prd.md:201: "**The person owns the PRD.** The Product Owner seat checks the work
    satisfies it, under authority the person delegates: a review of the PRD (here, and the PRD
    leg of the unified `review`) ends with the seat's "PRD requirements satisfied: yes / no
    (gaps: ...)" sign-off, and the seat asks the person when unsure."
  - reference-pvd.md:18-21: "... in a product/anchor repo. The person owns it, as they own each
    PRD. The **Product Manager** seat checks the work against it, under authority the person
    delegates, and signs the **PVD review leg** ..."
  - help/pvd.md:28: "(the person owns it; the Product Manager seat checks the work against it)".
  - reference-review.md:137 and :153: "The Product Manager (Product Owner) seat signs this, under
    authority the person delegates; ..."
  - reference-workflow-personas.md:117-129: a heading such as "Seats for the requirements
    documents" with its own anchor, opening: "The person owns every document the skill keeps:
    the PRD, the PVD, the TRD, the TSD and the personas. On a team that is whoever holds the
    role; on a solo project, the operator. Two seats hold authority the person delegates for a
    top-level requirements document. Each checks the work satisfies it, signs its review leg,
    and asks the person when unsure." The table's Owns column becomes something like "Checks the
    work against".
  - reference-persona.md:39: "(Three Amigos, the Product Owner and Product Manager seats)".
  - amigo-template.md:6, :27, :62 and review-seat-charter.md:5, :18: "a review-only seat (one
    that checks work against a document, such as Product Owner / Product Manager / UX, and does
    not build)".
- Test design: normalise each page before matching (strip `>` blockquote marks and `**`, join
  lines). A line-by-line grep passes the PVD page's split sentence, which is how CR0755's own
  Verify misses it. Scope the owner and document-owner patterns to every `.md` under
  .claude/skills/sdlc-studio/; at HEAD they hit only the files in Affects. The criteria must stay
  true after later releases, because `gate.py --release` runs every story's Verify at each cut.
- Leave each page's first descriptive line alone: `docgen.py references` derives
  help/references.md from it, and that file is not in Affects. The reading guides at the top of
  the edited reference pages regenerate (`docgen.py reading-guides`); the pre-commit budgets lane
  refuses drift. `tools/check_links.py --staged` refuses a dangling anchor, so the heading rename
  and the three link updates land in one commit. Run `bash tools/forward-port.sh --check` after.
- How a seat changes a document it reviews against is US1340's, which depends on this story and
  edits the same section; this story does not state that rule.
- Out of scope: the shipped product seat card (it already says the seat never authors the PRD),
  the "Which Personas for Which Artefacts" table (who is consulted, not who owns), and
  CHANGELOG.md history. A file outside Affects that needs a change is a finding to report, not
  an edit.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-26 | product seat | Groomed for run twenty-eight under D0636 |
