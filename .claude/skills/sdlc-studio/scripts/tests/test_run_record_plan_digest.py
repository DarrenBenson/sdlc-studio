"""US0998: the committed run record names its sprint plan by a content digest, never by a path.

Each run is opened by the real `sprint plan --write` (a rolling run's next cycle by the real
`sprint boundary`) and closed by the real `sprint close`, its chain steps stubbed green, in a
throwaway workspace; the tracked record that close files is then read back. The close stubs are
the lean close fixture's, which resolve `sprint` at call time. The rolling suite's are not
imported: loading that module a second time replaces the instance its own stubs patch.

Run from the repo root:
    python3 -m pytest .claude/skills/sdlc-studio/scripts/tests/test_run_record_plan_digest.py -q
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import hashlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_lean_close as lean  # noqa: E402 - call-time module resolution and close stubs, shared

DIGEST = r"^sha256:[0-9a-f]{64}$"
INDEXES = (("bugs", "Bugs"), ("stories", "Stories"), ("epics", "Epics"),
           ("change-requests", "Change Requests"), ("retros", "Retros"),
           ("handoffs", "Handoffs"), ("reviews", "Reviews"), ("rfcs", "RFCs"))
RETRO = "RETRO0001"


def _main(*argv: str, stubbed: bool = False) -> tuple[int, str]:
    """`sprint.main(argv)` on the instance `sys.modules` holds now; with `stubbed`, the close
    chain and the report holds stubbed green."""
    mod = lean._live("sprint")
    buf = io.StringIO()
    with (lean._green_steps(mod) if stubbed else contextlib.nullcontext()), \
            contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        rc = mod.main(list(argv))
    return rc, buf.getvalue()


def _run_state():
    return lean._live("sprint").run_state


def _ws(root: Path) -> None:
    """Every artefact folder with its index table, and one retro to close on."""
    sd = root / "sdlc-studio"
    for sub, head in INDEXES:
        (sd / sub).mkdir(parents=True, exist_ok=True)
        (sd / sub / "_index.md").write_text(
            f"# {head}\n\n| ID | Title | Status |\n| --- | --- | --- |\n", encoding="utf-8")
    (sd / "retros" / f"{RETRO}-x.md").write_text(
        f"# {RETRO}: r\n\n> **Status:** Complete\n\n## Lessons\n\n- A lesson worth keeping. "
        "It carries a second sentence.\n", encoding="utf-8")
    with (sd / "retros" / "_index.md").open("a", encoding="utf-8") as f:
        f.write(f"| [{RETRO}]({RETRO}-x.md) | r | Complete |\n")


def _bug(root: Path, num: int, status: str = "Open") -> None:
    """A groomed bug (Affects, Points, a criterion), which `sprint plan` accepts."""
    src = root / f"src/bg{num:04d}.py"
    src.parent.mkdir(parents=True, exist_ok=True)
    src.write_text("", encoding="utf-8")
    d = root / "sdlc-studio" / "bugs"
    (d / f"BG{num:04d}-x.md").write_text(
        f"# BG{num:04d}: b{num}\n\n> **Status:** {status}\n> **Severity:** Medium\n"
        f"> **Affects:** src/bg{num:04d}.py\n> **Points:** 2\n\n## Acceptance Criteria\n\n"
        "### AC1: it behaves as recorded\n\n- **Given** the recorded state\n"
        "- **Verify:** shell true\n", encoding="utf-8")
    idx = d / "_index.md"
    rows = [ln for ln in idx.read_text(encoding="utf-8").splitlines()
            if not ln.startswith(f"| [BG{num:04d}]")]
    idx.write_text("\n".join(rows + [f"| [BG{num:04d}](BG{num:04d}-x.md) | b{num} | {status} |"])
                   + "\n", encoding="utf-8")


def _judged(root: Path) -> None:
    _run_state().update(root, sprint_goal_verdict={"verdict": "achieved", "note": "fixture"})


def _sha(path: Path) -> str:
    """`sha256:` and the full hex digest of the bytes at `path`, computed here, not by the code."""
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _strings(value):
    if isinstance(value, dict):
        for v in value.values():
            yield from _strings(v)
    elif isinstance(value, list):
        for v in value:
            yield from _strings(v)
    elif isinstance(value, str):
        yield value


class PlanDigestTests(unittest.TestCase):

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        _ws(self.root)
        self.plan_file = self.root / "sdlc-studio" / ".local" / "sprint-plan.json"

    def _plan(self, *extra: str) -> str:
        """Plan the open bugs with `--write`; the digest of the plan file that write left."""
        rc, out = _main("plan", "--bugs", "Open", "--write", "--no-fetch", "--root",
                        str(self.root), "--sprint-goal", "ship the fixture batch", *extra)
        self.assertEqual(rc, 0, out)
        return _sha(self.plan_file)

    def _close(self) -> dict:
        """Judge and close the open run through `sprint close`; the tracked record it filed."""
        rid = _run_state().read(self.root)["run_id"]
        _judged(self.root)
        rc, out = _main("close", "--retro", RETRO, "--root", str(self.root), stubbed=True)
        self.assertEqual(rc, 0, out)
        record = _run_state().read_tracked(self.root, rid)
        self.assertEqual(record.get("run_id"), rid, "the close filed no tracked record")
        return record

    def _assert_names_no_local_path(self, record: dict) -> None:
        self.assertIn("plan", record, "the record dropped the legacy `plan` key")
        self.assertIsNone(record["plan"], "the record still names the plan by its path")
        local = [s for s in _strings(record) if ".local/" in s]
        self.assertEqual([], local, "a committed record names a path under .local/")

    def test_plan_write_records_a_content_digest(self) -> None:
        """AC1. Mutants: `open_run(plan=str(out))` left in cmd_plan, which the tracked record
        projects to sdlc-studio/.local/sprint-plan.json; the digest written into `plan`; the
        digest cut to portable's 12 hex."""
        _bug(self.root, 1)
        written = self._plan()
        record = self._close()
        self.assertRegex(record.get("plan_digest") or "", DIGEST)
        self.assertEqual(written, record["plan_digest"])
        self._assert_names_no_local_path(record)

    def test_a_replan_moves_the_digest_to_the_last_write(self) -> None:
        """AC2. Mutant: the digest recorded only when `open_run` opens a fresh run, so a re-plan
        that rewrites the plan leaves the record naming a plan that no longer exists."""
        _bug(self.root, 1)
        first = self._plan()
        self.assertEqual(first, _run_state().read(self.root).get("plan_digest"))
        _bug(self.root, 2)
        second = self._plan()
        self.assertNotEqual(first, second, "the re-plan wrote the same plan, so proves nothing")
        self.assertEqual(["BG0001", "BG0002"], sorted(_run_state().read(self.root)["batch"]),
                         "the re-plan did not grow the open run's batch")
        record = self._close()
        self.assertEqual(second, record.get("plan_digest"))
        self._assert_names_no_local_path(record)

    def test_the_next_cycle_records_its_own_plan_digest(self) -> None:
        """AC3. Mutants: `_open_next_cycle` left passing `plan=str(out)`; its cycle given no
        digest, or the previous cycle's."""
        _bug(self.root, 1)
        _bug(self.root, 2)
        first = self._plan("--cycles", "2")
        first_run = _run_state().read(self.root)["run_id"]
        _judged(self.root)
        # the cycle delivered BG0001 and raised BG0003, so the next cycle's plan is its own
        _bug(self.root, 1, status="Fixed")
        _bug(self.root, 3)
        rc, out = _main("boundary", "--root", str(self.root), "--retro", RETRO, "--no-fetch",
                        stubbed=True)
        self.assertEqual(rc, 0, out)
        state = _run_state().read(self.root)
        self.assertNotEqual(first_run, state["run_id"], "the boundary opened no fresh run")
        self.assertEqual(2, state["cycle"]["index"])
        own = _sha(self.plan_file)
        self.assertNotEqual(first, own, "the next cycle wrote the same plan, so proves nothing")
        record = self._close()
        self.assertRegex(record.get("plan_digest") or "", DIGEST)
        self.assertEqual(own, record["plan_digest"])
        self._assert_names_no_local_path(record)


if __name__ == "__main__":
    unittest.main()
