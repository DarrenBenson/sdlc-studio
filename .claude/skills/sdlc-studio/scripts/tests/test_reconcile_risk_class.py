"""US1314. Reconcile reports an open story whose stamped `Risk-class` ranks below the class its
Affects now get from the component map, and `apply` raises the stamp, never lowering one.

A stamped class wins over the map (`critic.unit_risk_class`), so a map declared or widened after
refine leaves every earlier story at its old class. A stamp above the map may be an operator's
raise, so it is left alone, and a closed story is history.
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import reconcile  # noqa: E402

KIND = "risk-class"
_MAP = "risk:\n  components:\n    src/pay: high\n"
REFERENCE = SCRIPTS.parent / "reference-reconcile.md"


def _story(root: Path, num: int, status: str, affects: str, cls: str | None,
           inline: bool = False) -> Path:
    """A story file; `inline` carries the stamp on the Status line's `·` run."""
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    if inline:
        head = f"> **Status:** {status} · **Risk-class:** {cls}\n"
    else:
        head = f"> **Status:** {status}\n" + (f"> **Risk-class:** {cls}\n" if cls else "")
    path = d / f"US{num:04d}-s.md"
    path.write_text(f"# US{num:04d}: s\n\n{head}> **Affects:** {affects}\n> **Points:** 2\n\n"
                    f"## Acceptance Criteria\n\nNone yet.\n", encoding="utf-8")
    return path


def _tree(root: Path, config: str | None) -> None:
    (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
    if config is not None:
        (root / "sdlc-studio" / ".config.yaml").write_text(config, encoding="utf-8")


def _run(*argv: str) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = reconcile.main(list(argv))
    return rc, out.getvalue()


def _risk_items(root: Path) -> list[dict]:
    _, out = _run("detect", "--root", str(root), "--format", "json")
    return [d for d in json.loads(out)["drift"] if d["kind"] == KIND]


def _stamp(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    return (reconcile.sdlc_md.extract_field(text, "Risk-class") or "").strip()


class RiskClassDriftTests(unittest.TestCase):
    def test_a_stamp_below_the_map_is_reported(self) -> None:
        """AC1. MUTANTS: read the stamp as authoritative (nothing reported); report a Done story
        or a stamp level with the map; report an unstamped story; leave the detector out of the
        sweep; drop the stamped or the mapped class from the item. With no map declared every
        path classes standard, so the no-map case is a positive control, not a mutant."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _tree(root, _MAP)
            _story(root, 1, "Ready", "src/pay/charge.py", "standard")
            _story(root, 2, "Ready", "src/pay/refund.py", "high")      # level with the map
            _story(root, 3, "Done", "src/pay/charge.py", "standard")   # closed: history
            _story(root, 4, "Draft", "src/pay/charge.py", None)        # unstamped: map rules
            _story(root, 5, "Draft", "src/payroll.py", "standard")     # not under src/pay
            items = _risk_items(root)
            self.assertEqual(["US0001"], [i["id"] for i in items])
            item = items[0]
            self.assertEqual(("story", "standard", "high"),
                             (item["type"], item["stamped"], item["mapped"]))
            for word in ("US0001", "standard", "high", "src/pay"):
                self.assertIn(word, item["fix"])
            self.assertIn(KIND, reconcile.DRIFT_KINDS)
            rc, text = _run("detect", "--root", str(root))
            self.assertEqual(1, rc)
            self.assertTrue(any(ln.startswith(KIND) and "US0001" in ln
                                for ln in text.splitlines()), text)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _tree(root, None)   # no map declared: every story is the default, nothing drifts
            _story(root, 1, "Ready", "src/pay/charge.py", "standard")
            self.assertEqual([], _risk_items(root))

    def test_apply_raises_open_stamps_and_never_lowers_one(self) -> None:
        """AC2. MUTANTS: lower a stamp above the map; rewrite a Done story; miss the inline
        `·` run; write on a dry run; an apply that is not idempotent."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _tree(root, _MAP)
            raised = _story(root, 1, "Ready", "src/pay/charge.py", "standard")
            kept = _story(root, 2, "Ready", "src/other/thing.py", "high")
            closed = _story(root, 3, "Done", "src/pay/charge.py", "standard")
            inline = _story(root, 4, "In Progress", "src/pay/charge.py", "elevated", inline=True)
            before = {p: p.read_text(encoding="utf-8") for p in (kept, closed)}
            _, dry = _run("apply", "--root", str(root), "--dry-run")
            self.assertIn("WOULD raise US0001 Risk-class: standard -> high", dry)
            self.assertEqual("standard", _stamp(raised), "a dry run wrote the stamp")
            rc, out = _run("apply", "--root", str(root))
            self.assertIn("raised US0001 Risk-class: standard -> high", out)
            self.assertEqual("high", _stamp(raised))
            self.assertEqual("high", _stamp(inline))
            self.assertEqual("high", _stamp(kept), "a stamp above the map was lowered")
            self.assertIn("> **Status:** In Progress · **Risk-class:** high\n",
                          inline.read_text(encoding="utf-8"))
            for p, text in before.items():
                self.assertEqual(text, p.read_text(encoding="utf-8"), p.name)
            self.assertEqual([], _risk_items(root))
            settled = {p: p.read_text(encoding="utf-8") for p in (raised, kept, closed, inline)}
            _run("apply", "--root", str(root))
            for p, text in settled.items():
                self.assertEqual(text, p.read_text(encoding="utf-8"), f"second apply: {p.name}")
            _, js = _run("apply", "--root", str(root), "--format", "json")
            self.assertEqual([], json.loads(js)["by_type"]["risk_class"]["synced"])
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _tree(root, None)
            story = _story(root, 1, "Ready", "src/pay/charge.py", "standard")
            _run("apply", "--root", str(root))
            self.assertEqual("standard", _stamp(story))

    def test_the_reference_names_the_risk_class_kind(self) -> None:
        """AC3. MUTANTS: drop the section; name a kind the code does not emit; drop that apply
        only raises, or the reason a stamp is never lowered."""
        text = REFERENCE.read_text(encoding="utf-8")
        # The section's heading, not the generated reading guide's row that names its anchor.
        heading = re.search(r"^#+ [^\n]*\{#risk-class\}", text, re.M)
        self.assertIsNotNone(heading, "reference-reconcile.md has no {#risk-class} section")
        start = heading.start()
        end = text.find("\n## ", start)
        section = text[start:end if end != -1 else len(text)]
        self.assertIn(f"`{KIND}`", section)
        self.assertIn(KIND, reconcile.DRIFT_KINDS)
        self.assertIn("raises", section)
        self.assertIn("never lowers", section)
        self.assertIn("operator", section)   # why: a stamp above the map is an operator's raise


if __name__ == "__main__":
    unittest.main()
