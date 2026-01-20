# SDLC Studio Philosophy

## Create vs Generate: Two Fundamentally Different Modes

SDLC Studio operates in two distinct modes. Understanding the difference is critical.

---

## Create Mode (Greenfield)

**Purpose:** Plan something new that doesn't exist yet.

**Flow:**
```
User requirements → PRD → Epics → Stories → Implementation → Tests
```

**Characteristics:**
- Interactive - asks user questions
- Forward-looking - describes what WILL be built
- Aspirational - captures intent before reality exists
- Tests come AFTER implementation

---

## Generate Mode (Specification Extraction)

**Purpose:** Extract a complete, testable specification from existing code.

**Flow:**
```
Existing code → PRD → Epics → Stories → Test Specs → Tests → VALIDATION
```

**This is NOT documentation. This is a migration blueprint.**

### Why This Matters

A properly extracted specification enables:

1. **Technology Migration** - Hand the spec to a team using Go, Rust, or any stack. They can rebuild with confidence because the spec is complete and the tests validate correctness.

2. **Complete Refactoring** - Change internals freely. As long as tests pass, behaviour is preserved.

3. **Legacy Modernisation** - Extract specs from a 15-year-old codebase, then rebuild it piece by piece with modern practices.

4. **Vendor Independence** - Your specification, not your code, becomes the source of truth. Swap implementations without losing functionality.

### The Validation Requirement

**A generated specification is worthless until validated.**

The cycle must be:
```
Extract spec → Write tests from spec → Run tests against existing code → PASS
```

If tests fail, either:
- The specification is wrong (fix the spec)
- The code has bugs (document as known issues)

Only when tests pass against the existing implementation do you have a valid specification.

---

## Generate Mode Requirements

### Acceptance Criteria Must Be Implementation-Ready

**Bad (documentation-style):**
```
### AC1: Search works
- Given a user searches
- When they enter a query
- Then results are returned
```

**Good (specification-style):**
```
### AC1: Search returns ranked results by relevance
- Given the index contains engrams with slugs "alice-smith", "bob-jones", and "alice-wong"
- When I GET /search?q=alice
- Then I receive results with alice-smith and alice-wong
- And alice-smith has match_score >= 0.9 (exact slug match)
- And results are sorted by match_score descending
- And each result includes slug, name, role, category, match_score, matched_field
```

The second version can be implemented by someone who has never seen the original code.

### Edge Cases Must Be Exhaustive

Don't just note "handles errors". Document every edge case:

| Scenario | Input | Expected Output |
|----------|-------|-----------------|
| Query too short | `q=a` | 422, "min length 2" |
| No matches | `q=zzzznotfound` | 200, empty array |
| Special characters | `q=o'brien` | 200, matches o'brien |
| Case insensitive | `q=ALICE` | 200, matches alice |
| Limit exceeded | `limit=500` | Capped at 100 |

### API Contracts Must Be Precise

Not "returns engram data" but:

```
GET /engrams/{slug}

Response 200:
{
  "slug": "string",           // URL-safe identifier
  "name": "string",           // Display name
  "role": "string",           // Job title or role
  "category": "fictional|real",
  "el_rating": "string|null", // EL-1 through EL-5, or null
  "engram_content": "string", // Full .engram file content (JSON)
  "psychometrics": object|null,
  "user_manual": "string|null",
  "headshot_path": "string|null",
  "labels": ["string"]
}

Response 404:
{
  "detail": "Engram not found: {slug}"
}
```

### Tests Must Validate Reality

Generated test specs aren't complete until:

1. Executable tests are generated from them
2. Those tests PASS against the existing implementation
3. Any failures are investigated and resolved (fix spec or document bug)

---

## Story Generate vs Story (from Epics)

### `/sdlc-studio story` (Default)

Generates stories from Epic acceptance criteria.
- Input: Epics (which came from PRD)
- Best for: Forward-looking planning

### `/sdlc-studio story generate` (Extraction)

Reverse-engineers stories from actual code behaviour.
- Input: The codebase itself
- Best for: Brownfield specification extraction

**When to use `story generate`:**
- Existing functionality with no documentation
- Legacy code that needs to be understood
- Preparing for migration or major refactor

**What it does differently:**
1. Analyses actual code paths, not just Epic descriptions
2. Extracts real validation rules, error messages, edge cases
3. Documents actual API contracts from code
4. Identifies implicit behaviour that might not be in any docs
5. Produces specs detailed enough to reimplement

---

## The Complete Extraction Pipeline

For a brownfield project, the full pipeline is:

```
1. /sdlc-studio prd generate        # Extract requirements from code
2. /sdlc-studio trd generate        # Extract technical architecture
3. /sdlc-studio persona generate    # Infer user types from code
4. /sdlc-studio epic                # Group into epics (from PRD)
5. /sdlc-studio story generate      # Extract detailed specs from CODE
6. /sdlc-studio test-spec           # Generate test specifications
7. /sdlc-studio test-automation     # Generate executable tests
8. /sdlc-studio code test           # RUN TESTS - validate spec
```

**Step 8 is not optional.** Until tests pass, you have documentation, not a specification.

---

## Status: Ready vs Done

For extracted specifications:

- **Ready** = Specification extracted, awaiting validation
- **Done** = Specification validated (tests pass against implementation)

Never mark as "Done" until tests confirm the spec matches reality.

---

## Quality Checklist for Generated Specs

Before considering a story "Ready":

- [ ] AC detailed enough for someone to implement without seeing original code
- [ ] All edge cases documented with specific inputs and outputs
- [ ] API contracts include exact request/response shapes
- [ ] Error scenarios documented with actual error messages
- [ ] Test scenarios cover happy path AND all edge cases
- [ ] No ambiguous language ("handles errors", "returns data", "works correctly")

Before marking "Done":

- [ ] Test spec generated from story
- [ ] Executable tests generated from test spec
- [ ] All tests pass against existing implementation
- [ ] Any failures investigated and resolved
