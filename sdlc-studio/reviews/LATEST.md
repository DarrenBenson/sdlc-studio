# Reviews - LATEST (anchor)

> Derived from the sprint-close review of **RUN-01KXRMQT** (the artefact-schema
> contract sprint, 2026-07-17, RETRO0047). Supersedes the RETRO0046 picture.

## Where the pipeline is (2026-07-17)

The **artefact-schema contract sprint** (RUN-01KXRMQT) is delivered: **EP0084 (US0258-US0260,
3 stories, 11 points) Done and every AC verified**, Sprint Goal judged ACHIEVED (RETRO0047).
This delivers **RFC0047 option B**: the `sdlc-studio/` artefact tree is now a versioned,
drift-guarded public contract rather than an undeclared de facto interface. `reference-schema.md`
documents the six on-disk surfaces (id grammar, directory layout, per-type header fields, status
vocabulary and transition gates, the Verify-line DSL, the derived index format); `schema_version`
is the contract stamp (current version **3** - new projects ship v3 via `init` ->
`templates/config.yaml`; v2 is the legacy era; `config-defaults.yaml`'s 2 is the fallback for
un-stamped projects); and `scripts/tests/test_schema_contract.py` (11 tests) fails the suite when
the documented vocabularies or version stamp diverge from the code constants.

## CODE leg

Closing full-diff adversarial pass (independent instance, refute framing, a repro per claim), run
twice. **Round 1 REJECT (BLOCKING):** the contract asserted new projects are/stay schema v2 until
migration, but shipped `init.py` stamps `schema_version: 3` into every new project (proven by
running it); decision D0033's mechanism was factually false. **Round 2 APPROVE:** the fix declares
the contract at schema v3 (current; v2 legacy), anchors the guard to the new-project seed
(`templates/config.yaml`), and adds a fallback-never-leads test; the reviewer re-ran the mutation
checks (status / masthead / v3-inbox drift all go red, revert green), confirmed all three verifiers
and lint clean, and both MINORs were closed (the v3 `inbox` lane is now a guarded table;
`CURRENT_SCHEMA=2` is BG0189). Reviewer-of-record sign-off recorded. Full suite 2828 green, drift 0.

## Document legs

`reference-schema.md` (new), `reference-config.md`, `help/references.md`, `config-defaults.yaml`
and `templates/config.yaml` are the surfaces this sprint touched; each is consistent with the
shipped code, enforced by the drift guard. Decision D0034 (supersedes D0033) records the
current-version resolution.

## Next steps

- Follow-ups filed this sprint: **BG0188** (`sprint plan --write` accumulates a new batch into a
  prior run left `outcome=running`, reusing its id and clobbering its verdict) and **BG0189**
  (`project_upgrade.CURRENT_SCHEMA=2` contradicts `init` seeding new projects at schema_version 3).
- Standing: **CR0278** (interactive-sprint token capture) - per-unit token actuals were not
  captured this run, so est/actual is uncomputable.
- Residual audit CRs (CR0280-CR0306) and BG0187 remain for a future scheduled batch.
- Release freeze holds until ~2026-07-21; everything lands unreleased on `main`.
