"""US0882 (BG0747): re-registration keeps the anchored rows it did not move.

The re-registration is driven through `mutation.py register`, the surface an agent meets, in
throwaway git workspaces. Nothing reads this repository's own config or ledger. US0882's
evidence-drift tests went with the lane (US0920).
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - confined git for the fixture repos
import mutation  # noqa: E402

BUG = ("# BG0001: fixture\n\n> **Status:** Fixed\n> **Severity:** Medium\n> **Points:** 1\n"
       "> **Affects:** src/x.py\n\n## Acceptance Criteria\n\n- [ ] **AC1** Given a, when b, then c\n"
       "  - **Verify:** pytest tests/test_x.py::T::test_c\n")


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True,
                   env=gitutil.git_env(), check=True, timeout=120)


def _workspace() -> Path:
    """A repo whose delivered BG0001 holds a registered row on `src/x.py` at HEAD's bytes."""
    root = Path(tempfile.mkdtemp(prefix="lean_mut_off_"))
    _git(root, "init", "-q", "-b", "main", str(root))
    (root / "src").mkdir()
    (root / "src" / "x.py").write_text("alpha = 1\n", encoding="utf-8")
    bugs = root / "sdlc-studio" / "bugs"
    bugs.mkdir(parents=True)
    (bugs / "BG0001-fixture.md").write_text(BUG, encoding="utf-8")
    (root / "sdlc-studio" / ".local").mkdir()
    (root / ".gitignore").write_text("sdlc-studio/.local/\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "seed")
    mutation.register_mutant(root, root / "src" / "x.py", "flip alpha", "pytest t", "killed",
                             unit="BG0001", criterion="AC1", line=1, anchor="alpha = 1", row=0)
    # the commit moves the row's own site, so its evidence drifts
    (root / "src" / "x.py").write_text("alpha = 2\n", encoding="utf-8")
    _git(root, "add", "src/x.py")
    return root


def _register(root: Path, *argv: str) -> tuple[int, str]:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        rc = mutation.main(["register", "--root", str(root), *argv])
    return rc, out.getvalue()


class RegisterKeepsUnmovedRowsTests(unittest.TestCase):
    def _root(self) -> Path:
        root = _workspace()
        self.addCleanup(shutil.rmtree, root, True)
        return root

    def test_register_keeps_anchored_rows_that_did_not_move(self) -> None:
        """US0882 AC3. MUTANTS: drop every earlier row on changed bytes (the old rule); keep a row whose
        anchor is gone; keep a row whose anchor now occurs twice; keep an unanchored row; drop
        or stale another unit's unmoved row."""
        root = self._root()
        fp = root / "src" / "x.py"
        fp.write_text("alpha = 1\nbeta = 1\ngamma = 1\ndelta = 1\nplain = 1\n", encoding="utf-8")

        def reg(unit, row, anchor, mutant):
            mutation.register_mutant(root, fp, mutant, "pytest t", "killed", unit=unit,
                                     criterion="AC1", line=1, anchor=anchor, row=row)
        reg("BG0001", 0, "alpha = 1", "flip alpha")     # site untouched: kept
        reg("BG0001", 1, "beta = 1", "flip beta")       # the row being re-registered
        reg("BG0001", 2, "gamma = 1", "flip gamma")     # site now occurs twice: dropped
        reg("BG0001", 3, None, "flip plain")            # no anchor: dropped
        reg("BG0002", 0, "delta = 1", "other delta")    # another unit, site untouched: live
        fp.write_text("alpha = 1\nbeta = 2\ngamma = 1\ngamma = 1\ndelta = 1\nplain = 1\n",
                      encoding="utf-8")
        rc, out = _register(root, "--target", "src/x.py", "--mutant", "flip beta again",
                            "--test", "pytest t", "--verdict", "killed", "--unit", "BG0001",
                            "--criterion", "AC1", "--line", "2", "--row", "1",
                            "--anchor", "beta = 2")
        self.assertEqual(0, rc, out)
        self.assertIn("DROPPED 3 earlier registration(s)", out,
                      "the old beta row, the doubled anchor and the unanchored row are the "
                      "three to go:\n" + out)
        self.assertNotIn("STALE:", out, "the other unit's unmoved row was named stale:\n" + out)
        live = _current(root, fp)
        rows = {(m["unit"], m["row"]): m for m in live["mutants"]}
        self.assertEqual({("BG0001", 0), ("BG0001", 1)}, set(rows),
                         "the current entry is not exactly the unit's unmoved row plus the new one")
        self.assertEqual("flip beta again", rows[("BG0001", 1)]["mutant"])
        self.assertEqual(2, live["summary"]["applied"], live["summary"])
        self.assertEqual(2, live["summary"]["killed"], live["summary"])
        self.assertEqual({("BG0001", 0): "live", ("BG0001", 1): "live", ("BG0002", 0): "live"},
                         _live(root), "a row whose site did not move does not read live")
        # the row being re-registered is replaced, never carried - even when its own anchor did
        # not move - so a later edit elsewhere lets it be re-measured as it always could
        fp.write_text(fp.read_text(encoding="utf-8") + "omega = 1\n", encoding="utf-8")
        rc, out = _register(root, "--target", "src/x.py", "--mutant", "flip alpha again",
                            "--test", "pytest t", "--verdict", "survived", "--unit", "BG0001",
                            "--criterion", "AC1", "--line", "1", "--row", "0",
                            "--anchor", "alpha = 1")
        self.assertEqual(0, rc, "re-registering an unmoved row was refused:\n" + out)
        rows = {(m["unit"], m["row"]): m["verdict"] for m in _current(root, fp)["mutants"]}
        self.assertEqual({("BG0001", 0): "survived", ("BG0001", 1): "killed"}, rows)
        self.assertEqual({("BG0001", 0): "live", ("BG0001", 1): "live", ("BG0002", 0): "live"},
                         _live(root))


def _current(root: Path, fp: Path) -> dict:
    """The one registered entry on the target's current bytes."""
    state, _ = mutation._load_ledger(mutation.ledger_path(root))
    digest = hashlib.sha256(fp.read_bytes()).hexdigest()
    live = [e for e in state["entries"] if e.get("hash") == digest]
    assert len(live) == 1, state
    return live[0]


def _live(root: Path) -> dict:
    """Every non-withdrawn row as the ledger's readers judge it, keyed by (unit, row)."""
    state, _ = mutation._load_ledger(mutation.ledger_path(root))
    return {(m["unit"], m["row"]): mutation.row_staleness(root, e, m)
            for e in state["entries"] for m in e["mutants"] if not m.get("withdrawn")}


class CarryTests(unittest.TestCase):
    """What the carry claims beyond AC3: it never evicts a live row, and it moves only one
    live, newest copy of each of the registering unit's rows."""

    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="lean_mut_carry_"))
        self.addCleanup(shutil.rmtree, self.root, True)
        _git(self.root, "init", "-q", "-b", "main", str(self.root))
        (self.root / "sdlc-studio" / ".local").mkdir(parents=True)
        self.fp = self.root / "x.py"
        self.fp.write_text("".join(f"v{i} = {i}\n" for i in range(200)), encoding="utf-8")

    def reg(self, unit: str, row: int, anchor: str | None = None, mutant: str | None = None):
        return mutation.register_mutant(self.root, self.fp, mutant or f"m{row}", "t", "killed",
                                         unit=unit, criterion="AC1", line=row + 1,
                                         anchor=anchor or f"v{row} = {row}\n", row=row)

    def edit(self, tail: str) -> None:
        self.fp.write_text(self.fp.read_text(encoding="utf-8") + tail + "\n", encoding="utf-8")

    def test_other_units_rows_are_not_evicted_by_the_cap(self) -> None:
        """MUTANT: carry every unit's unmoved rows onto the current entry, which runs it past
        MUTANT_LIMIT and evicts the oldest live rows."""
        for i in range(99):
            self.reg("BG0002", i)
        self.edit("tail = 1")                  # no BG0002 site moved
        self.reg("BG0001", 100)
        self.reg("BG0001", 101)
        self.edit("tail2 = 1")
        self.reg("BG0003", 102)
        live = _live(self.root)
        self.assertEqual(102, len(live))
        self.assertEqual({"live"}, set(live.values()), "a live row was lost or read stale")

    def test_a_carry_past_the_cap_leaves_the_rest_in_place(self) -> None:
        """MUTANT: carry every own row and let the cap evict the oldest - here the other unit's
        rows already registered on the current bytes."""
        for i in range(99):
            self.reg("BG0002", i)
        self.edit("tail = 1")
        for i in range(100, 150):
            self.reg("BG0003", i)
        res = self.reg("BG0002", 150)
        self.assertEqual(0, res["dropped_stale"], res)
        current = _current(self.root, self.fp)
        self.assertEqual(mutation.MUTANT_LIMIT, len(current["mutants"]))
        self.assertNotIn("dropped_mutants", current, "the carry evicted rows through the cap")
        live = _live(self.root)
        self.assertEqual(150, len(live), "a row was lost")
        self.assertEqual({"live"}, set(live.values()), "a row was read stale")

    def _seed(self, rows_by_entry: list[tuple[str, list[dict]]]) -> None:
        """Replace the ledger with registered entries on the given hashes ("now" = current)."""
        now = hashlib.sha256(self.fp.read_bytes()).hexdigest()
        entries = [{"target": "x.py", "hash": now if h == "now" else h, "provenance": "registered",
                    "summary": {"applied": len(rows)}, "mutants": rows}
                   for h, rows in rows_by_entry]
        path = mutation.ledger_path(self.root)
        mutation._store_ledger(path, mutation._load_ledger(path)[0], entries, False)

    @staticmethod
    def row(r: int, mutant: str, **extra) -> dict:
        return {"mutant": mutant, "test": "t", "verdict": "killed", "unit": "BG0001",
                "criterion": "AC1", "row": r, "line": r + 1, "anchor": f"v{r} = {r}\n", **extra}

    def _own_rows(self) -> list[tuple[int, str]]:
        return sorted((m["row"], m["mutant"]) for m in _current(self.root, self.fp)["mutants"])

    def test_a_withdrawn_row_is_not_carried(self) -> None:
        """MUTANT: carry withdrawn rows, so a corrected verdict reads live again."""
        self._seed([("old", [self.row(0, "gone", withdrawn={"reason": "wrong"})])])
        res = self.reg("BG0001", 5)
        self.assertEqual([(5, "m5")], self._own_rows())
        self.assertEqual(1, res["dropped_stale"], res)

    def test_a_row_the_current_bytes_already_hold_is_not_carried_twice(self) -> None:
        """MUTANT: no check against the rows the current entry already holds."""
        self._seed([("old", [self.row(0, "stale copy")]), ("now", [self.row(0, "held copy")])])
        res = self.reg("BG0001", 5)
        self.assertEqual([(0, "held copy"), (5, "m5")], self._own_rows())
        self.assertEqual(1, res["dropped_stale"], res)

    def test_the_newest_copy_of_a_row_wins(self) -> None:
        """MUTANT: walk the stale entries oldest first, so the older copy is carried."""
        self._seed([("older", [self.row(0, "older copy")]), ("newer", [self.row(0, "newer copy")])])
        res = self.reg("BG0001", 5)
        self.assertEqual([(0, "newer copy"), (5, "m5")], self._own_rows())
        self.assertEqual(1, res["dropped_stale"], res)


if __name__ == "__main__":
    unittest.main()
