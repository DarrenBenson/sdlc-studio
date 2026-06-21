# CR-0047: PVD template + product manifest (RFC0015 WS1)

> **Status:** Proposed
> **Priority:** High
> **Type:** Feature
> **Requester:** Darren Benson (RFC decision session)
> **Date:** 2026-06-21
> **Affects:** templates/core/pvd.md (new), reference-config.md, reference-outputs.md
> **Depends on:** RFC0015
> **GitHub Issue:** --

## Summary

Add the Product Vision Document artifact (tiered: lean v1 sections always, tree/gates opt-in) and a product manifest that lists the child repos (path + git URL).

## Proposed Changes

- `templates/core/pvd.md` - tiered PVD template (vision, strategic goals, feature->repo->PRD-feature map, cross-repo deps, API-contract commitments; tree + G1-G5 opt-in).
- Product manifest schema in `reference-config.md` (child repos: path + URL).
- `pvd` type rows in SKILL.md + help/pvd.md; the PVD sits above the PRD in reference-outputs.md.

## Acceptance Criteria

- [ ] A `pvd create` renders the tiered template; the lean sections are present, the tree/gates are opt-in.
- [ ] The product manifest lists child repos by path + URL and is read by the tooling.
- [ ] Unit-tested where code; independent critic APPROVE.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Darren Benson | Raised - RFC decision session |
