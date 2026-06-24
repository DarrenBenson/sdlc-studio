#!/usr/bin/env python3
"""Deprecated alias for `sprint.py` (CR0087). `autosprint` was renamed to `sprint` when the
command became the whole sprint lifecycle (plan/design/done); autonomy is the `--autonomous`
flag, not the name. This shim re-exports `sprint` so `import autosprint` and the
`autosprint.py` CLI keep working (incl. `--help`, via the re-exported argparse parser).
Prefer `sprint`."""
from __future__ import annotations
import sys
from sprint import *  # noqa: F401,F403 - back-compat re-export
from sprint import main, select_batch, build_plan, build_parser  # noqa: F401 - explicit for importers

if __name__ == "__main__":
    print("note: `autosprint` is a deprecated alias - use `sprint` (see `sprint --help`).", file=sys.stderr)
    sys.exit(main())
