# Critic Verdicts

> Append-only. The independent non-author critic's verdict per unit (RFC0001 D3).
> APPROVE = ready; REJECT = repair before Done. Latest row per unit wins.

| Unit | Verdict | Reviewer | Date | Issues |
| --- | --- | --- | --- | --- |
| US0009 | APPROVE | independent-critic | 2026-06-20 | - |
| US0010 | APPROVE | independent-critic | 2026-06-20 | - |
| US0011 | APPROVE | independent-critic | 2026-06-20 | - |
| US0012 | APPROVE | independent-critic | 2026-06-20 | - |
| US0013 | APPROVE | independent-critic | 2026-06-20 | - |
| US0014 | APPROVE | independent-critic | 2026-06-20 | - |
| US0015 | APPROVE | independent-critic | 2026-06-20 | - |
| US0016 | APPROVE | independent-critic | 2026-06-20 | - |
| US0006 | APPROVE | backfill-closing-gate | 2026-06-20 | - |
| US0007 | APPROVE | backfill-closing-gate | 2026-06-20 | - |
| US0008 | APPROVE | backfill-closing-gate | 2026-06-20 | - |
| US0017 | APPROVE | independent-critic | 2026-06-20 | approved after broadening reconciled to missing-row + no-index |
| US0018 | APPROVE | independent-critic | 2026-06-20 | approved after fixing prose-id phantom edges |
| US0019 | APPROVE | independent-critic | 2026-06-20 | - |
| US0020 | APPROVE | independent-critic | 2026-06-20 | approved after guarding non-numeric threshold + boundary test |
| US0021 | APPROVE | independent-critic | 2026-06-20 | approved; verified against real RFCs; added first-table-only + exact-Open guard tests |
| US0022 | APPROVE | independent-critic | 2026-06-20 | approved; added registry-completeness contract test + bulk-note floor per critic |
| US0023 | APPROVE | independent-critic | 2026-06-20 | REJECT->fixed: escaped-pipe re-escape on write, counts from parse_index authority, summary anchoring; +4 corruption-guard tests |
| US0024 | APPROVE | independent-critic | 2026-06-20 | CR0027 reviewed: degradation contract holds all inputs; 13 sites correct; cutoff exclusive-boundary correct. LOW followups applied (id_number reuse + type-confusion/all-exempt tests) |
| US0025 | APPROVE | independent-critic | 2026-06-20 | CR0027 reviewed: degradation contract holds all inputs; 13 sites correct; cutoff exclusive-boundary correct. LOW followups applied (id_number reuse + type-confusion/all-exempt tests) |
| US0026 | APPROVE | independent-critic | 2026-06-20 | RFC0009 complexity reviewed: REJECT->fixed 4 cognitive spec deviations (comprehension filter, else-vs-elif via col_offset, nested-ternary nesting, match guard); cyclomatic/lizard/assess correct; +5 spec-edge tests |
| US0027 | APPROVE | independent-critic | 2026-06-20 | RFC0009 complexity reviewed: REJECT->fixed 4 cognitive spec deviations (comprehension filter, else-vs-elif via col_offset, nested-ternary nesting, match guard); cyclomatic/lizard/assess correct; +5 spec-edge tests |
| US0028 | APPROVE | independent-critic | 2026-06-20 | apply_type refactor 56->7: behaviourally identical (14-case differential probe, 0 divergence); +ragged-row regression test |
| US0029 | APPROVE | independent-critic | 2026-06-20 | validate no-ac adoption cutoff (consuming repo A contribution): APPROVE - story-scoped, fail-safe in every direction (no config/PyYAML/malformed/unparseable id -> judges), mirrors CR0027; added degradation + at-cutoff regression tests |
| US0030 | APPROVE | independent-critic | 2026-06-21 | version_check + skill-update: APPROVE - safety contract holds (offline/disabled/raising-fetch all silent); fixed self-degrading check() + guarded cache write + 5 gap tests (raising-fetch, offline-no-poison, semver 2.10>2.9, corrupt cache, scope-under-home) |
| US0031 | APPROVE | independent-critic | 2026-06-21 | gate.py: REJECT->fixed. Exit contract + all 5 wrappers correct (incl. the reconcile dict-vs-drift fix). HIGH fixed: vacuous PASS on wrong/missing root now guarded (scope check fails -> exit 1); added missing-root, exit-code, and constitution-enforce tests |
| US0032 | APPROVE | independent-critic | 2026-06-21 | PVD template+manifest: REJECT->fixed. Complete (7 lean sections + 3 opt-in fenced), consistent across template/manifest/reference/help, proportional, domain-neutral, no re-spec. Medium fixed: removed the dead reference-outputs.md See-Also pointer (that edit was dropped to respect its maxed budget; intent already stated in reference-pvd intro + SKILL) |
| US0033 | APPROVE | independent-critic | 2026-06-21 | pvd.py: REJECT->fixed. Idempotent read-only sync + symlink mechanics solid. HIGH fixed: drift no longer reports vacuous in-sync when master unreadable/missing (returns error). MEDIUM fixed: read_manifest strips inline comments from values. Added unreadable-master, symlink-mode, and inline-comment tests |
| US0034 | APPROVE | independent-critic | 2026-06-21 | product_reconcile.py: REJECT->fixed. Parser solid (placeholders/escaped-pipes/multi-colon rejected). 2 HIGH fixed: (1) missing manifest path no longer silently reads the manifest dir's PRD (missing-path blocks); (2) feature match anchored to a declaration site (table cell/heading) so prose/changelog/removed mentions no longer false-pass. MEDIUM: empty-feature-map + un-verified count surfaced. Added prose, F7/F70, missing-path, empty, placeholder, exit-code tests |
