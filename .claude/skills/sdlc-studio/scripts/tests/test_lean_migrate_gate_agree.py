"""BG0854: migrate's report and the gate agree, on one tree, run end to end.

The v6 upgrade rehearsal found migrate disagreeing with `gate.py` on three lanes of a v4.1 project,
each seen only by a human reading the two outputs side by side. Here both shipped entry points run
as subprocesses on one COMMITTED git fixture shaped like that project: `migrate.py --apply`, the
apply committed, then `gate.py`. The commit matters - on a dirty tree the gate scopes conformance
and validate to the diff and they pass, which is how the rehearsal missed them. The lanes to compare
are taken from the gate's own output, so no hand-kept kind-to-lane map can fall behind it.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS))
sys.path.insert(0, str(_SCRIPTS / "tests"))
import gitutil  # noqa: E402 - confined, hermetic git for the fixture and both subprocesses

#: The lanes the rehearsal's v4.1 project failed; the fixture must fail every one.
REHEARSAL_LANES = {"reconcile", "conformance", "validate", "engagement-floor"}


def _w(root: Path, rel: str, text: str) -> None:
    p = root / "sdlc-studio" / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def _story(n: int, status: str = "Done", verified: bool = True) -> str:
    stamp = f"  - **Verified:** yes (2026-01-0{n})\n" if verified else ""
    return (f"# US000{n}: s{n}\n\n> **Status:** {status}\n> **Epic:** EP0001\n\n"
            f"## Acceptance Criteria\n\n- [x] **AC1** given x, when y, then z\n"
            f"  - **Verify:** shell true\n{stamp}")


def _v41(root: Path) -> None:
    """A v4.1-shaped project, committed: schema 2, `conformance.adopt_after` below its failing
    stories, the five-column verdict ledger, shipped bugs with no plan, a status outside the
    vocabulary, a breakdown box ticked over a live story, and no sdlc-studio/.gitignore."""
    env = gitutil.git_env()
    subprocess.run([sys.executable, str(_SCRIPTS / "init.py"), "--root", str(root), "run"],
                   check=True, capture_output=True, text=True, env=env)
    sd = root / "sdlc-studio"
    (sd / ".gitignore").unlink()                     # a v4.1 project never got one
    (sd / ".version").write_text('schema_version: 2\nskill_version: "4.1.0"\n', encoding="utf-8")
    cfg = sd / ".config.yaml"
    cfg.write_text(cfg.read_text(encoding="utf-8").replace("schema_version: 3", "schema_version: 2")
                   + "\nconformance:\n  adopt_after: US0002\n", encoding="utf-8")
    for n in (1, 2, 3, 4):                           # conformance: US0003, US0004 unreviewed
        _w(root, f"stories/US000{n}-s.md", _story(n))
    _w(root, "reviews/critic-verdicts.md",
       "# Critic verdicts\n\n| Unit | Verdict | Reviewer | Date | Issues |\n"
       "| --- | --- | --- | --- | --- |\n| US0003 | APPROVE | qa-seat | 2026-01-03 | - |\n")
    for n in (5, 6):                                 # engagement floor: shipped, no plan
        _w(root, f"bugs/BG000{n}-b.md", f"# BG000{n}: b\n\n> **Status:** Fixed\n> **Severity:** Low\n")
    _w(root, "stories/US0007-s.md",                  # validate: a status outside the vocabulary
       "# US0007: s7\n\n> **Status:** Shipped\n> **Epic:** EP0001\n")
    _w(root, "stories/US0008-s.md", _story(8, status="In Progress", verified=False))
    _w(root, "epics/EP0001-e.md",                    # reconcile: a box ticked over a live story
       "# EP0001: e\n\n> **Status:** In Progress\n\n## Story Breakdown\n\n- [x] US0008: s8\n")
    import reconcile  # noqa: PLC0415 - index rows for the files, so the drift is the sweep's
    for type_ in ("story", "epic", "bug"):
        reconcile.apply_type(type_, root)
    gitutil.git(["init", "-q"], root)
    gitutil.git(["add", "-A"], root)
    gitutil.git(["commit", "-q", "-m", "a v4.1 project"], root)


def _cli(script: str, root: Path, *args: str) -> dict:
    proc = subprocess.run([sys.executable, str(_SCRIPTS / script), "--root", str(root), *args,
                           "--format", "json"], capture_output=True, text=True, timeout=600,
                          env=gitutil.git_env())
    return json.loads(proc.stdout)


class MigrateGateAgreeTests(unittest.TestCase):
    """One fixture, one migrate-then-gate run, shared by both criteria."""

    @classmethod
    def setUpClass(cls) -> None:
        cls._tmp = tempfile.TemporaryDirectory()
        root = cls.root = Path(cls._tmp.name)
        _v41(root)
        cls.had_gitignore = (root / "sdlc-studio" / ".gitignore").exists()
        cls.migrate = _cli("migrate.py", root, "--apply")
        gitutil.git(["add", "-A"], root)
        gitutil.git(["commit", "-q", "-m", "migrate --apply"], root)
        cls.gate = _cli("gate.py", root)
        cls.status = gitutil.git(["status", "--porcelain"], root, text=True).stdout.splitlines()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def test_migrate_names_every_lane_the_gate_fails(self) -> None:
        # Mutants: no `lane` on an item (today's reconcile and validate items), a count that
        # disagrees with the gate's, and a lane migrate does not name at all.
        failing = {c["check"]: c["count"] for c in self.gate["checks"]
                   if c["blocking"] and c["status"] == "fail"}
        self.assertTrue(REHEARSAL_LANES <= set(failing),
                        f"the fixture must fail the rehearsal's four lanes: {failing}")
        for lane, count in failing.items():
            items = [h for h in self.migrate["needs_human"] if h.get("lane") == lane]
            self.assertEqual(1, len(items),
                             f"the gate fails `{lane}` and migrate names it {len(items)} time(s): "
                             f"{[(h['kind'], h.get('lane')) for h in self.migrate['needs_human']]}")
            self.assertEqual(count, items[0].get("count"),
                             f"`{lane}`: the gate counts {count}, migrate {items[0].get('count')}")

    def test_migrate_then_gate_leaves_no_runtime_state_in_git_status(self) -> None:
        self.assertFalse(self.had_gitignore, "the fixture must start with no ignore file")
        self.assertTrue(any((self.root / "sdlc-studio" / ".local").iterdir()),
                        "the gate wrote no runtime state, so there was nothing to leak")
        leaked = [ln for ln in self.status if "sdlc-studio/.local" in ln]
        self.assertEqual([], leaked, "runtime state left in `git status`")


if __name__ == "__main__":
    unittest.main()
