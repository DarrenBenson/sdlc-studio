"""BG0873: reconcile reads a meta artefact keyed by a v3 id, not only a numeric one.

The meta lane (`meta_census`, `_meta_index_row_ids`) read only `PREFIX<digits>` keys, so a
handoff filed as `HO-<ulid>-slug.md` was absent from the census, and its index row - whose
ULID opens on digits - was read as the truncated number `HO-0001` and reported an orphan.

Every test drives `reconcile.py detect` in a throwaway project that cleans itself up; none
reads this repository.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/reconcile.py
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402

_SCRIPTS = Path(__file__).resolve().parent.parent
_V3 = "HO-01J2ABCDEFGHJKMNPQRSTVWXYZ"
_V3_FILE = f"{_V3}-x.md"
_NUM_FILE = "HO0002-y.md"


def _project(root: Path, *, v3_file: bool) -> None:
    """A schema v3 workspace whose handoff index holds a row for the v3 handoff and one for a
    numeric `HO0002`; the numeric file always exists, the v3 file only when `v3_file`."""
    ws = root / "sdlc-studio"
    (ws / "handoffs").mkdir(parents=True)
    (ws / ".config.yaml").write_text("schema_version: 3\n", encoding="utf-8")
    (ws / "handoffs" / _NUM_FILE).write_text("# HO-0002: numeric\n", encoding="utf-8")
    if v3_file:
        (ws / "handoffs" / _V3_FILE).write_text(f"# {_V3}: v3 keyed\n", encoding="utf-8")
    (ws / "handoffs" / "_index.md").write_text(
        "# Handoff Index\n\n"
        "| ID | Title | Date |\n"
        "| --- | --- | --- |\n"
        f"| [{_V3}]({_V3_FILE}) | v3 keyed | 2026-10-01 |\n"
        f"| [HO-0002]({_NUM_FILE}) | numeric | 2026-10-01 |\n",
        encoding="utf-8")


def _handoff_drift(root: Path) -> list[dict]:
    proc = subprocess.run(
        [sys.executable, "-B", str(_SCRIPTS / "reconcile.py"), "detect", "--root", str(root),
         "--format", "json"],
        cwd=root, env=gitutil.git_env(), capture_output=True, text=True, timeout=300)
    if proc.returncode not in (0, 1):
        raise AssertionError(f"detect exited {proc.returncode}:\n{proc.stdout}\n{proc.stderr}")
    report = json.loads(proc.stdout)
    return [d for d in report["drift"] if d.get("type") == "handoff"]


class MetaV3KeyTests(unittest.TestCase):
    def test_a_v3_handoff_is_not_an_orphan(self) -> None:
        """AC1. MUTANT: HEAD's census pattern `^HO0*(\\d+)-` skips the v3 file and the row reader
        `HO-?0*(\\d+)` reads its ULID as `HO-0001`, so detect reports `orphan-row HO-0001`."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, v3_file=True)
            self.assertEqual(_handoff_drift(root), [])

    def test_a_missing_v3_handoff_is_still_named(self) -> None:
        """AC2. MUTANTS: a fix that silences every meta row reports nothing; one that keys the v3
        row by a truncated number names `HO-0001`. The numeric HO0002 is the positive control:
        its file exists, so it must report nothing."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _project(root, v3_file=False)
            drift = _handoff_drift(root)
            self.assertEqual([(x["kind"], x["id"]) for x in drift], [("orphan-row", _V3)], drift)


if __name__ == "__main__":
    unittest.main()
