# BG0614 ledger fixture

A committed mutation ledger carrying the duplicate-key shapes this repository's own ledger held on 2026-09-07: ten keys with two rows naming one test, one key with four rows naming one test, five keys with three rows naming two tests, three keys in an entry whose target bytes no longer match its hash (`stale_target.py`), one criterion carrying two distinct rows (no duplicate), and one key whose second row is withdrawn (no duplicate). The tests copy `targets/` into a temporary root beside the ledger so `entry_staleness` can hash them.
