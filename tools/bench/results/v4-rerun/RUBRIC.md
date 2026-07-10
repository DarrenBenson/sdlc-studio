# Solution-quality rubric (post-hoc, exploratory - NOT pre-registered)

Score each workspace 1-5 per dimension. Anchor: 3 = professionally acceptable; 5 =
exemplary; 1 = defective. Judge the FINAL STATE of the workspace only.

1. SPEC FIDELITY - behaviour honours every rule in the workspace's docs/SPEC.md
   INCLUDING interactions between rules (a missed interaction caps this at 2).
2. TEST QUALITY - tests pin the requirements (not the implementation), cover
   boundaries and interactions, and would fail on plausible regressions.
3. DESIGN FIT - minimal cohesive change following the codebase's existing patterns;
   no needless abstraction, no copy-paste drift.
4. SPEC/DOC MAINTENANCE - spec text updated faithfully where behaviour changed;
   docstrings honest; requirement cross-references correct.
5. SCOPE DISCIPLINE - everything the ticket asked, nothing it did not; judgement
   calls on silent points are reasonable AND recorded somewhere in the workspace.

Return strict JSON: {"scores": [{"workspace": "<dirname>", "spec_fidelity": n,
"test_quality": n, "design_fit": n, "doc_maintenance": n, "scope_discipline": n,
"one_line_justification": "..."}]}
