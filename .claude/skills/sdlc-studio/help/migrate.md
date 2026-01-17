# /sdlc-studio migrate

Migrates existing test-plan, test-suite, and test-case files to the new consolidated test-spec format.

## Usage

```bash
# Preview migration (dry run)
/sdlc-studio migrate

# Execute migration
/sdlc-studio migrate --execute

# Create backup before migrating
/sdlc-studio migrate --backup --execute
```

## What Gets Migrated

The migrate command consolidates:

| Old Format | New Format |
|------------|------------|
| `sdlc-studio/testing/plans/TP*.md` | Merged into TSP |
| `sdlc-studio/testing/suites/TS*.md` | Merged into TSP |
| `sdlc-studio/testing/cases/TC*.md` | Merged into TSP |
| `sdlc-studio/testing/features/*.feature` | Removed (Gherkin deprecated) |
| `sdlc-studio/testing/data/fixtures.yaml` | Embedded in TSP |

## Migration Process

1. **Scan** existing test artifacts
2. **Group** test cases by their parent suite
3. **Group** suites by their parent plan/epic
4. **Create** TSP files consolidating all related content
5. **Preserve** all test case details and fixtures
6. **Archive** old files to `sdlc-studio/testing/.archive/`
7. **Update** cross-references in other specs

## Example

```bash
/sdlc-studio migrate

Scanning existing test artifacts...

Found:
- 4 test plans (TP0001-TP0004)
- 27 test suites (TS0001-TS0027)
- 135 test cases (TC0001-TC0344)

Migration plan:
- Create 4 test-spec files (one per plan/epic)
- Consolidate 135 test cases into specs
- Archive old files to sdlc-studio/testing/.archive/

Run `/sdlc-studio migrate --execute` to proceed.
```

## File Mapping

```
Old                              New
sdlc-studio/testing/plans/             sdlc-studio/testing/.archive/plans/
sdlc-studio/testing/suites/            sdlc-studio/testing/.archive/suites/
sdlc-studio/testing/cases/             sdlc-studio/testing/.archive/cases/
sdlc-studio/testing/features/          sdlc-studio/testing/.archive/features/
sdlc-studio/testing/data/              sdlc-studio/testing/.archive/data/

TP0001 + TS0001-TS0005 + TC*     sdlc-studio/testing/specs/TSP0001-*.md
TP0002 + TS0006-TS0010 + TC*     sdlc-studio/testing/specs/TSP0002-*.md
```

## Options

| Option | Description |
|--------|-------------|
| (none) | Preview only, show what would be migrated |
| `--execute` | Perform the migration |
| `--backup` | Create backup before migration |
| `--no-archive` | Delete old files instead of archiving |

## Rollback

If you need to rollback:

```bash
# Restore from archive
mv sdlc-studio/testing/.archive/* sdlc-studio/testing/
rm -rf sdlc-studio/testing/specs/

# Or restore from backup if --backup was used
```

## Post-Migration

After migration:

1. Verify TSP files contain all test cases
2. Run `/sdlc-studio status` to confirm counts
3. Update any external references to old file paths
4. Remove `.archive/` directory when satisfied

## When to Use

- Upgrading from old spec skill version
- Projects with existing test-plan/suite/case files
- One-time migration to streamlined format

## See Also

- `/sdlc-studio test-spec` - New consolidated format
- `/sdlc-studio status` - Verify migration results
- `/sdlc-studio test-automation` - Generate tests from new format
