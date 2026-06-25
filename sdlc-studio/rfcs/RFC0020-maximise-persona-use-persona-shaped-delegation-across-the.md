# RFC-0020: Maximise persona use - persona-shaped delegation across the SDLC lifecycle

> **Status:** Accepted - Option B, delivered v3.1.0 (consulted Three Amigos 2026-06-25)
> **Date:** 2026-06-25
> **Created-by:** sdlc-studio file

## Summary

The skill has rich persona machinery (RFC0016 review seats - Product/Engineering/QA Three Amigos + document owners; RFC0017 Cooper design personas) but uses it ONLY for review/consult: the independent critic, spec review, and WSJF seat scoring. The WORKERS that author specs/stories, build code, and write tests are generic and unframed - the main loop, or a blank general-purpose subagent (a field agent built the whole EP0005 SPA with a generic general-purpose agent). Operator direction: MAXIMISE persona use - each lifecycle role should be performed by a subagent framed as the relevant persona/seat. Proposed role->seat mapping for the WORKERS: Product Owner/Manager authors PRD + stories (create-mode authoring + story decomposition); Engineering implements (the agentic wave / build sub-agent); QA authors test-specs + tests + runs verification. The review seats keep reviewing - but the LOAD-BEARING invariant is that the reviewing seat is ALWAYS a separate instance from the authoring seat (never self-review; author/critic separation). Open decisions: (D1) which stages get framing; (D2) main-loop-adopts-the-seat vs only-delegated-subagents-are-framed; (D3) how independence is enforced; (D4) charter source - extend the review-seat charters with build/author/test variants, or reuse; (D5) degradation without personas (--skip-personas -> generic); (D6) interplay of review-seats (RFC0016) and design-personas (RFC0017). Implementing the full vision is feature-sized (a later minor release), not the v3.0.2 patch.

## Terminology - two distinct concepts (do not conflate)

The skill deliberately separates two things, and this RFC must use them precisely:

- **Design personas (RFC0017)** - **Alan Cooper goal-directed** archetypes: *who the product is
  for*, defined by End/Experience/Life goals (e.g. Priya). They describe **users**. They never
  author, build, test, or review - they are the **target** the work serves and is judged against.
- **Review seats (RFC0016)** - structured **charters** (Product / Engineering / QA Three Amigos +
  document owners): *who does/reviews the work*. They are the **actors**.

So this RFC is about the **seats** acting as workers (build/test/author), NOT about Cooper personas
doing work. "Persona-shaped" in the title is the operator's banner phrase; read it as **seat-shaped
delegation**. The two levers of "maximise persona use" are therefore: **(1)** the *seats* do the
work (this RFC's core), and **(2)** the Cooper *design personas* are the **lens/target** threaded
through every stage - the Engineering seat builds **to serve the Primary persona's goals**, the QA
seat tests **as that persona would use it** (her End/Experience goals as test lenses), the Product
seat authors **against** that persona. That second lever is the deeper win and was under-stated in
the first draft (see revised D6).

## Design Options

- **A (recommended): persona-shape all three worker roles (Product authors, Engineering builds, QA tests) at the subagent-delegation layer, reusing/extending the review-seat charters, independence invariant preserved (reviewer always a separate seat instance), degrade to generic without personas. Slice into CRs: CR0116 (Engineering build) + QA-test + Product-author**
- **B: persona-shape only the highest-value delegations (Engineering build + QA test); leave PRD/story authoring to the main loop**
- **C: status quo - personas review only; workers stay generic**

## Recommendation (revised after consultation)

**Option B** for the *generic* case, plus **D7** (the operator's point): a project-authored,
specifically-skilled **practitioner persona** overrides the generic seat as the worker - and that is
where persona-shaping earns its keep. The Three Amigos seats - consulted independently (dogfooding
`reference-consult.md`) - all three flipped the recommendation from A to B for *generic* framing: a
charter's value is **independence**, not flavour, and a thin **stance** delivers it. But the Eng
seat's "thin value" critique is scoped to the *generic* identity; a richly-skilled persona the
operator invested in carries real expertise, so the worker identity is **pluggable, most-specific-
first** (practitioner persona > generic seat > generic). Net: persona-shape Engineering build + QA
test; resolve the worker identity by specificity; **defer Product-author** (reject PRD-authoring);
keep the mechanical independence gate (CR0117) as the floor under all of it.

## Consultation Outcome - Three Amigos (2026-06-25)

Each seat was consulted as an independent subagent; verdicts converged strongly.

- **Overall:** unanimous **B**. Engineering-build + QA-test are the high-value, independence-bearing slices; Product-author earns its place later on evidence, not symmetry.
- **The load-bearing requirement (all three INSISTED, the RFC only asserted it in prose): make author != reviewer a MECHANICAL gate, not an honour-system convention.** `critic.py` records a `reviewer` but does not prove `reviewer != author`. Required: stamp an **author identity** (seat/delegation instance id) on the unit when the diff/tests are produced; the conformance gate **hard-fails** any unit whose critic verdict `reviewer` id equals its `author` id. *"Independence you cannot verify is independence you do not have."* This is the prerequisite for everything else (filed as its own CR).
- **The persona is a thin STANCE PREAMBLE appended to the existing prompt, NOT a charter rewrite (Engineering).** `reference-agent-prompt-template.md` already carries the load-bearing contract (READ THESE FILES FIRST, verbatim AC, Files to Create/Modify/DO NOT Modify, quality gates) - that, not a persona, is 80% of build quality. The persona adds ~10 lines of standing disposition (tests must be able to fail; red gate is a stop; never weaken an AC to go green). Persona text goes *after* the contract, never woven through it.
- **QA runs the oracle, it does not judge green.** The QA seat authors the test-spec/matrix + tests, but pass/fail stays the deterministic `verify_ac` oracle + the conformance gate. Tests must trace to the **canonical AC `Verify:` line**, not the seat's paraphrase (else self-fulfilling green / parallel descriptions).
- **Product: defer.** Reject PRD-authoring by the Product seat - it is *accountable that the PRD is satisfied*, so authoring it collapses accountability (it would review its own work). Story-authoring framing is optional/weak and earns its place only with measured value over the generic main loop.

## Decisions (resolved by the consultation)

| # | Decision | Resolution |
| --- | --- | --- |
| D1 | Which stages get persona framing | Engineering build + QA test now; Product story-author later (optional); PRD-author **rejected** |
| D2 | Main loop adopts the seat vs only delegated subagents framed | **Only delegated subagents** are framed; the main loop stays the neutral orchestrator/critic-router (else the later review is self-review) |
| D3 | Enforce author != reviewer | **Mechanical, gate-enforced** - author id stamped on the unit; conformance hard-fails if `reviewer == author`. Prerequisite slice |
| D4 | Charter source | Extend the existing review-seat charter with a thin **stance/render-mode** (build / test), not a forked heavyweight charter taxonomy |
| D5 | Degradation without personas | `--skip-personas` -> generic workers, but the **independence gate + the verify oracle survive the fallback** (independence is the floor; persona is the optional layer) |
| D6 | Review-seats (RFC0016) vs design-personas (RFC0017) | Design (Cooper) personas are the **input/target/lens** threaded through every stage (build to serve the Primary, test as that persona) - never the author; review/worker seats are the actors; the independent critic stays terminal + separate |
| D7 | Generic seat vs **operator-authored project-specific skilled persona** | The worker identity is **resolved most-specific-first**: a project-authored skilled **practitioner persona** (e.g. "staff frontend engineer, our design system + React 19 + a11y") **overrides** the generic seat; absent one, the generic Three Amigos seat; absent personas (`--skip-personas`), generic worker. This is where persona-shaping's value lives - the Eng seat's "thin stance" critique holds for the *generic* case, but a specifically-skilled persona the operator invested in carries real expertise. Support the full spectrum |

## Worker-identity resolution (the spectrum, D7)

Persona-shaping is worth more the more specific the identity. The delegation resolves the worker
identity in priority order:

1. **Project-authored practitioner persona** (highest value) - a richly-skilled, project-specific
   expert the operator crafted (`templates/personas/` extended with a *practitioner* kind, distinct
   from Cooper *design* personas and from generic seats). Carries real domain/codebase expertise and
   conventions. If the operator spent the time to design it, the delegation **uses it**.
2. **Generic review-seat charter** (Engineering / QA / Product) - the thin-stance default; modest
   value over a well-specified generic prompt, but a sane fallback.
3. **Generic worker** (`--skip-personas` or no personas) - the contract prompt alone.

All three keep the load-bearing invariants unchanged: the worker is still a **separate instance**
from the reviewer (CR0117), the persona/stance sits **after** the concrete contract (never rewrites
the file-list / AC / gates), and green stays the deterministic oracle. The persona adds *who* and
*what good looks like*; it never becomes *the arbiter of done*.

## Slices (on acceptance of B)

1. **CR (prerequisite): mechanical author != reviewer independence gate** - the floor all three seats insisted on; valuable standalone (hardens the existing critic). Candidate for v3.0.2.
2. **CR0116: Engineering build stance** - reframed as a thin stance preamble over the existing contract; `--skip-personas` yields a byte-equivalent contract that still builds + passes the same gated ACs.
3. **CR: QA test stance** - QA seat authors test-spec + tests as a separate instance; green stays the oracle; tests trace to the canonical `Verify:` line.
4. **Product-author: deferred** - revisit only with measured value; PRD-author rejected.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | audit | Filed |
| 2026-06-25 | Three Amigos consult | Consulted Product/Engineering/QA seats independently; all three recommend **B**; recorded the mechanical author!=reviewer gate as the load-bearing prerequisite; resolved D1-D6 |
