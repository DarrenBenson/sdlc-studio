# Best Practices: Scripts

> **See also:** [python.md](python.md) for Python-specific library guidance (YAML, requests, Pillow).

## Checklist

Before considering a script complete:

- [ ] Shebang line (`#!/bin/bash` or `#!/usr/bin/env python3`)
- [ ] Executable permissions (`chmod +x`)
- [ ] Supports `--help` with usage information
- [ ] Handles errors gracefully (non-zero exit on failure)
- [ ] Uses configuration from config file where applicable
- [ ] Documented in project README or scripts/README.md
- [ ] No hardcoded paths (use relative or config)
- [ ] Clear output messages

## Structure: Bash

```bash
#!/bin/bash
# Brief description of what this script does
# Usage: ./scripts/name.sh [args]

set -e  # Exit on error

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Help text
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    echo "Usage: $0 [options]"
    echo ""
    echo "Description of what this does."
    echo ""
    echo "Options:"
    echo "  --help, -h    Show this help"
    echo "  --dry-run     Preview without changes"
    exit 0
fi

# Main logic
main() {
    echo "Doing the thing..."
    # Implementation
}

main "$@"
```

## Structure: Python

```python
#!/usr/bin/env python3
"""Brief description of what this script does.

Usage:
    python3 scripts/name.py [options]
"""

import argparse
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# from lib.config import get_config  # If project has shared config


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true',
                        help='Preview without changes')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')
    args = parser.parse_args()

    # Implementation
    print("Doing the thing...")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
```

## Examples

### Good

```bash
#!/bin/bash
set -e

if [[ -z "${1:-}" ]]; then
    echo "Usage: $0 <name>" >&2
    exit 1
fi

SLUG="$1"
echo "Processing $SLUG..."
```

### Bad

```bash
cd /home/user/projects/my-project
python test.py
```

(No shebang, hardcoded path, no error handling)

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| No `set -e` | Continues after errors | Add `set -e` at top |
| Hardcoded paths | Breaks on other machines | Use `$SCRIPT_DIR` or config |
| No `--help` | Undiscoverable | Add help flag handling |
| Silent failures | Hard to debug | Echo status, exit non-zero |
| Bare `except:` | Hides errors | Catch specific exceptions |
| Print to stdout for errors | Mixed output | Use `>&2` or `stderr` |

## Configuration

Use a shared config module for project-wide settings. For bash, read from config files or use environment variables.

## Output Conventions

| Output Type | Format | Destination |
|-------------|--------|-------------|
| Progress messages | Plain text | stdout |
| Errors | Prefixed with "Error:" | stderr |
| Data for parsing | JSON | stdout |
| Reports | Markdown | file |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 130 | Interrupted (Ctrl+C) |

## File Locations

```
scripts/
├── README.md              # Document all scripts
├── lib/                   # Shared Python modules
│   ├── __init__.py
│   └── config.py          # Configuration loader
├── script-name.py         # Python scripts
└── script-name.sh         # Bash scripts
```

## Documentation

Every script must be documented in `scripts/README.md`:

```markdown
### script-name.sh

Brief description.

```bash
./scripts/script-name.sh [options]
```

**Options:**
- `--dry-run` - Preview only
- `--verbose` - More output
```

## Testing

Before committing:

1. Run with `--help` to verify
2. Test with valid input
3. Test with invalid input (should fail gracefully)
4. Test with `--dry-run` if applicable
5. Verify exit codes
