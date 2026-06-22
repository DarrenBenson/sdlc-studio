# Help: gate

<!-- Load when: /sdlc-studio gate - running the ecosystem-neutral quality gate -->

A single, **ecosystem-neutral** quality gate over the deterministic checks. Run it in
any CI (or a pre-commit hook) to enforce the discipline on a consuming project's changes.

## Command

```bash
python3 "$CLAUDE_SKILL_DIR/scripts/gate.py" --root .          # run all checks, exit 1 on a blocking failure
python3 "$CLAUDE_SKILL_DIR/scripts/gate.py" --only conformance,reconcile
python3 "$CLAUDE_SKILL_DIR/scripts/gate.py" --skip constitution --format json
```

Prints a consolidated report and exits non-zero only when a **blocking** check fails; a non-blocking
failure is reported (`warn`) but does not fail the gate. No network, no CI/cloud assumption.

### The checks

| Group | Checks | Blocks? |
| --- | --- | --- |
| **Artifact quality** | `conformance` (lifecycle stages), `validate` (structure/vocab), `integrity` (required links/refs), `constitution` (project principles) | yes (constitution only when `constitution.enforce`) |
| **Index consistency** | `reconcile` (file-census drift), `duplicate-id` | yes |
| **Provenance** | `provenance` (tool-created stamps) | only when `provenance.enforce` |
| **Skill docs (skill repo only)** | `doc-coverage` (every command/script documented), `disclosure` (progressive-disclosure hygiene), `doc-freshness` (LATEST.md vs reality) | doc-coverage yes; disclosure + doc-freshness advisory |

The four **artifact-quality** checks are the ones that police every artifact; the rest guard the
index, provenance, and the skill's own docs. `--only` / `--skip` select a subset.

## CI wiring (the gate is the mechanism; these are just examples)

### GitHub Actions

```yaml
- name: SDLC gate
  run: python3 .claude/skills/sdlc-studio/scripts/gate.py --root .
```

### GitLab CI

```yaml
sdlc-gate:
  script:
    - python3 .claude/skills/sdlc-studio/scripts/gate.py --root .
```

### Generic shell / pre-commit hook

```bash
# .git/hooks/pre-commit  (or any Jenkins/Buildkite/CircleCI step)
python3 .claude/skills/sdlc-studio/scripts/gate.py --root . || {
  echo "SDLC gate failed - fix drift/conformance before committing"; exit 1; }
```

Any runner that can execute a shell command can run the gate; nothing here is
GitHub-specific.

## See also

- `reference-scripts.md` - the script catalogue
- `reference-doctrine.md` - where the gate fits the operating discipline
