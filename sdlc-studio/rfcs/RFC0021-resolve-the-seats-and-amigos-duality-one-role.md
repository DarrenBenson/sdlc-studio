# RFC-0021: resolve the seats and amigos duality - one role-based actor model

> **Status:** Accepted - Option B (sliced), settled by Three Amigos consult
> **Created:** 2026-06-25
> **Created-by:** sdlc-studio new

## Summary

A field upgrade of a consuming project surfaced that SDLC Studio now ships **two parallel,
role-based persona-review systems** that overlap on the same three roles (engineering / qa /
product):

- **Review seats** (RFC0016, `personas/seats/`, template `review-seat-charter.md`): role charters
  (mandate, lens, non-negotiables, shadow) consulted as isolated subagents. The established model
  the consuming project's AGENTS.md discipline and `consult-guide.md` are built on
  (Sarah / Marcus / Priya / Maya / Claude-Code).
- **Amigos** (RFC0020, `personas/amigos/`, template `amigo-template.md`): a strictly **richer**
  card that fuses Cooper depth (craft / experience goals, proficiency, scenario) with the seat
  charter and adds a **dual render** - a build render and a review render - so one identity both
  does and critiques (always as separate instances). Ships Dani / Sam / Lena.

The defect: `project upgrade --apply` installs the generic amigos into `personas/amigos/` even when
the project already has rich seats filling those roles, with no heads-up - manufacturing two systems
([[CR0120]]). And `persona_resolve` only reads `personas/amigos/`, so the project's authored seats
are **shadowed** by generic defaults - the "most-specific-first" promise breaks exactly where the
project is most specific ([[BG0042]]). An amigo is, in substance, an enriched seat that can also
build. The question this RFC settles: **are seats and amigos one system or two, and if one, how do
they converge without breaking the RFC0016 model consuming projects already depend on?**

Out of scope: **Cooper design personas** (flat `personas/*.md`, RFC0017) are a distinct third
concept - the *users* a product targets (the lens), not the *actors* that build and review. They
stay separate. This RFC is only about the seats-vs-amigos actor duality.

## Design Options

- **Option A - Two systems, resolver precedence.** Keep `seats/` and `amigos/` as separate homes and
  two templates. `persona_resolve` reads `amigos/` then falls back to `seats/` then the default;
  `project upgrade` keeps installing both. Smallest code change, but the duality persists: two homes,
  two templates, the operator still reconciles overlap by hand. Treats the symptom, not the cause.

- **Option B - Converge on the enriched seat; keep the `seats/` home and name.** One role-based actor
  model. The amigo template becomes the **enriched schema** for a review seat (it already is a
  superset: it adds the build render and Cooper depth to the charter). Existing seats are **enriched
  in place** to that schema; the separate `personas/amigos/` project directory is retired as a
  runtime home - `templates/personas/amigos/` survives only as the *defaults source* installed INTO
  `seats/` when a role is unfilled (greenfield). `persona_resolve` and `consult` both read the one
  home (`seats/`), so RFC0016 references, `consult-guide.md`, and the consuming AGENTS.md keep
  working. "Amigo" becomes the friendly name for "an enriched seat that can also build." Resolves the
  duality and honours enrich-in-place; the cost is a one-time schema-merge of the two templates and a
  migration path.

- **Option C - Converge on `amigos/` as the home; deprecate `seats/`.** Same convergence as B but the
  amigo directory/name wins and `seats/` is migrated away. Cleanest conceptual slate, but it breaks
  every existing reference to `seats/` (AGENTS.md, consult-guide, RFC0016 wiring) in every consuming
  project and forces a rename migration with no functional gain over B.

The operator's stated instinct is **enrich in place** (do not manufacture a parallel set), which
points at B. This RFC dogfoods the Three Amigos consult to pressure-test that before committing.

## Consult (dogfooded - three independent seats)

Each seat was consulted in its **review render** as an isolated instance (fresh context, its own
charter), exactly as `reference-consult.md` prescribes. None saw the others' verdicts. **All three
independently chose Option B**, each surfacing a distinct refinement that the prose-only RFC had not.

**Engineering (Dani Okafor) - B, with a determinism fix.** The defect (BG0042) is a determinism
bug: the resolver keys on a filename, but authored seat cards are named after people and declare
their role only in free-text H1 prose. Any role->card mapping that scrapes `# X - Engineering seat`
from prose is non-deterministic at the boundary (two seats claiming one role, a renamed/translated
heading). The load-bearing change is therefore **add one declared `role:` field and resolve on it** -
small, testable, additive. One template beats two; the amigo card is already a strict superset of the
charter, so a build-less seat just leaves the work-render sections thin. Would block: a resolver that
keys on parsed prose; no deterministic tiebreak for two-claim/zero-claim roles; a migration that can
clobber an authored section; a silent install (heads-up must fire in `--dry-run` too); any merge that
drops the "separate instance / never sign off your own work" line.

**QA (Sam Eriksson) - B, with testability gates.** B is the only option testable as a single oracle:
"is the authored seat actually used?" becomes one assertion against one resolution path. The
independence gate is structurally orthogonal and holds (it lives in `critic.py`/conformance, not in
the persona home), but the input is where the risk moves: a converged build-and-review card tempts
resolving both renders to the *same* instance. The test that matters is **build-id != review-id for
one seat** (and `critic` recording those two ids passes `is_independent`; one id fails). Migration is
where silent green hides: a half-enriched seat (charter present, review render absent) must be a
**hard error**, not a fallback; ambiguous/zero-role mappings need negative coverage or the resolver
returns a plausible-but-wrong instance and the suite stays green. Would block: no failing-first test
that the authored seat resolves over the default (BG0042's own AC); a render-less seat resolving to
anything but an error; build and review sharing one instance id; the enrich migration without an
idempotency test and the overlap heads-up test.

**Product (Lena Marsh) - B, sliced.** The operator's goal is ratified and concrete: "I spent time
designing a specifically skilled persona - why shouldn't it be used?" plus "enrich the existing ones
in place." B is the only option where the authored seat is read AND no parallel home is manufactured
AND every existing `seats/` reference keeps working (zero migration surprise). A restates the bug; C
charges every consuming project a rename for conceptual tidiness "with no functional gain" - cut it.
Crucially: **ship B in two slices** - the resolver fix + the silent-collision heads-up first (the
operator's actual pain, BG0042 + CR0120 AC1-4), then the two-template schema-merge as a follow-up, so
the goal-bearing fix is not gated on the merge. Would block: any second runtime persona home the
operator reconciles by hand; non-idempotent enrichment that clobbers authored work; a dropped
heads-up; any AC phrased as "feels unified" rather than executable.

## Recommendation

**Adopt Option B (converge on the enriched seat; keep the `seats/` home and name), with the three
consult refinements, delivered in two slices.** One role-based actor model. "Amigo" is the friendly
name for an enriched seat that can also build; there is no runtime `personas/amigos/` project
directory - `templates/personas/amigos/` survives only as the greenfield defaults source. The
duality dies; RFC0016 references, `consult-guide.md`, and consuming AGENTS.md keep working.

**Slice 1 (goal-bearing, ship first):** the resolver reads existing seats and the upgrade stops
manufacturing a parallel set - i.e. [[BG0042]] and [[CR0120]] AC1-4, plus the **declared `role:`
field** (Dani) the resolver keys on, and the **build-id != review-id** + **role-less seat = hard
error** + **ambiguous/zero-role negative** tests (Sam).
**Slice 2 (follow-up):** merge `amigo-template.md` and `review-seat-charter.md` into one enriched
seat schema and enrich existing seats in place to it ([[CR0120]] AC5) - an improvement, not a gate on
slice 1.

## Open Decisions

| # | Decision | Resolution | Status |
| --- | --- | --- | --- |
| D1 | One system or two? | **One** (Option B). Two role systems over the same three roles is the bug, not a feature. Unanimous. | Accepted |
| D2 | Which home and name survive? | **`seats/`** stays the runtime home and name; `amigos/` reduces to `templates/personas/amigos/` defaults source. Unanimous (C rejected as cost-without-gain). | Accepted |
| D3 | One template or two? | **One** - `amigo-template.md` becomes the enriched seat schema, superseding `review-seat-charter.md`. Sequenced as **slice 2** (Lena), not a gate on the resolver fix. | Accepted |
| D4 | Migration for existing seats? | **Enrich in place**, idempotent, never clobbering customisation; generic cards scaffold **greenfield only**; explicit overlap heads-up incl. `--dry-run`. A seat missing the review render is a **hard error** (Sam), not a silent fallback. | Accepted |
| D5 | Independence gate under the converged model? | **Holds unchanged** - it lives in `critic.py`/conformance, orthogonal to the persona home. New floor test: **build instance id != review instance id resolved from one seat card** (Sam). | Accepted |
| D6 | Resolver mapping key? | Resolve on a **declared `role:` field** on the seat card, never parsed H1 prose or filename (Dani). Deterministic tiebreak required for two-claim and zero-claim roles. | Accepted |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | field | Created via `new` (deterministic) |
| 2026-06-25 | consult | Three Amigos consulted as independent instances; all three chose B. Accepted Option B (sliced), D1-D6 resolved. Refinements: declared `role:` field (Eng), build-id != review-id + role-less-seat hard error (QA), two-slice delivery (Product). |
