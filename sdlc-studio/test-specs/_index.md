# Test Specification Index

## Summary by Epic

| Spec                                                               | Epic   | Cases | Automated | Status |
| ------------------------------------------------------------------ | ------ | ----- | --------- | ------ |
| [TS0001](TS0001-ep0010-ac-coverage-token-economy-learning-loop.md) | EP0010 | 28    | 0         | Ready  |
| [TS0002](TS0002-mutation-check-gate-test-spec.md)                  | EP0011 | 14    | 0         | Ready  |

## Coverage Summary

| Metric           | Value    |
| ---------------- | -------- |
| Epics with specs | 2/70     |
| Total test cases | 42       |
| Automated        | 0 (0%)   |
| Pending          | 42       |

## Next Steps

**Epics without specs:** most epics in this workspace carry no standalone test-spec by
design. The validation leg here is the shipped **script suite** (`scripts/tests/`, run by
`npm test` and the pre-commit gate), not a per-epic TS document. TS0001 and TS0002 are the
two exceptions that warranted a written spec, so the absence of the other epics is
deliberate, not a coverage gap to close one spec at a time.

**Specs with pending automation:** TS0001 and TS0002 both read Automated 0. Their acceptance
criteria are exercised by the script suite rather than by generated `test-automation` code,
so the Automated column stays 0 by design and the specs sit Ready, not dormant-and-forgotten.
