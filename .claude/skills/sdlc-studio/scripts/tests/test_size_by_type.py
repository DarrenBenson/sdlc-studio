"""Size by what a thing IS: T-shirt on containers/requests, points on delivery units (RFC0038).

Points belong on the thing that is DELIVERED and MEASURED - a story or a bug. A T-shirt Size
belongs on the CONTAINER/REQUEST that must be decomposed first - a CR or an RFC. A CR is not a
unit of work until someone breaks it down, and pointing it is guessing at a shape that does not
exist yet.

The contract, driven through the PUBLIC paths (the finding filer's CLI, the planner's grooming
predicate, the token forecast) and read back with the shared parsers - never a source grep:

- Filing a CR with a T-shirt `--size M` and NO points is ACCEPTED and grooms.
- A story with `Points: 5` grooms; the gate demands POINTS of it, never a Size.
- A CR carrying `Points` and no `Size` still READS and still validates - the absorbed legacy
  shape (CRs filed under the earlier gate that forced points onto a request). New CRs get Size.
- A CR's T-shirt Size is NEVER summed into a velocity/forecast figure - it is not a measurement.
- A value off the T-shirt scale is refused, never coerced.

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


ff = _load("file_finding")
sprint = _load("sprint")
validate = _load("validate")
sdlc_md = ff.sdlc_md


def _seed_index(root: Path, type_: str) -> Path:
    dirs = {"bug": ("bugs", "| ID | Title | Status | Severity | Created | Updated |",
                    "| Open | 0 |\n| Fixed | 0 |"),
            "cr": ("change-requests",
                   "| ID | Title | Status | Priority | Type | Date | Linked Epics |",
                   "| Proposed | 0 |\n| Complete | 0 |")}
    rel, header, summary = dirs[type_]
    d = root / "sdlc-studio" / rel
    d.mkdir(parents=True, exist_ok=True)
    sep = "|" + " --- |" * (header.count("|") - 1)
    (d / "_index.md").write_text(
        f"# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n{summary}\n"
        f"| **Total** | **0** |\n\n## All\n\n{header}\n{sep}\n", encoding="utf-8")
    return d / "_index.md"


def _artifacts(root: Path, type_: str) -> list[Path]:
    rel = {"bug": "bugs", "cr": "change-requests"}[type_]
    return [p for p in (root / "sdlc-studio" / rel).glob("*.md") if p.name != "_index.md"]


def _run(main, argv: list[str]) -> tuple[int, str]:
    err = io.StringIO()
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(err):
            rc = main(argv)
    except ValueError as exc:
        return 1, str(exc)
    return rc, err.getvalue()


def _file_cr(root: Path, *extra: str) -> tuple[int, str]:
    return _run(ff.main, ["file", "--type", "cr", "--title", "tighten the gate",
                          "--priority", "High", "--ctype", "Improvement", "--summary", "s",
                          "--impact", "the gate lets bad units through", "--ac", "a criterion",
                          "--affects", "scripts/sprint.py", "--root", str(root), *extra])


def _file_bug(root: Path, *extra: str) -> tuple[int, str]:
    return _run(ff.main, ["file", "--type", "bug", "--title", "a defect",
                          "--severity", "High", "--summary", "s", "--steps", "x", "--fix", "y",
                          "--affects", "src/thing.py", "--root", str(root), *extra])


def _write_story(root: Path, points_line: str) -> Path:
    """A minimal groomed story on disk: it names its files and (usually) its points."""
    d = root / "sdlc-studio" / "stories"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "US0001-a-delivery-unit.md"
    p.write_text(
        "# US0001: a delivery unit\n\n"
        "> **Status:** Ready\n"
        f"{points_line}"
        "> **Affects:** src/x.py\n\n"
        "## Acceptance Criteria\n\n- [ ] it works\n", encoding="utf-8")
    return p


def _write_legacy_cr(root: Path) -> Path:
    """A CR in the ABSORBED legacy shape: `Points` and no `Size`, exactly as CRs filed under the
    earlier gate carry it. It must still read and still validate - the transition may not
    invalidate the backlog already on disk."""
    d = root / "sdlc-studio" / "change-requests"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "CR0001-a-legacy-request.md"
    p.write_text(
        "# CR-0001: a legacy request\n\n"
        "> **Status:** Proposed\n> **Priority:** High\n> **Type:** Improvement\n"
        "> **Affects:** scripts/sprint.py\n\n"
        "## Summary\n\nfiled before the vocabulary changed.\n\n"
        "## Impact\n\nevery sprint plan reads it.\n\n"
        "**Points:** 5\n\n"
        "## Acceptance Criteria\n\n- [ ] it holds\n", encoding="utf-8")
    return p


def _bd(root: Path, path: Path, type_: str) -> dict:
    uid = sdlc_md.extract_record_id(path.stem) or path.stem.split("-")[0]
    return sprint.breakdown(root, [{"id": uid, "type": type_, "path": str(path)}],
                            skip_personas=True)


class ACrIsSizedByATshirt(unittest.TestCase):
    """A CR is a REQUEST: it carries a T-shirt Size, sized before it is decomposed."""

    def test_a_cr_filed_with_size_and_no_points_is_accepted_and_grooms(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "cr")
            rc, _ = _file_cr(root, "--size", "M")
            self.assertEqual(rc, 0)
            filed = _artifacts(root, "cr")[0]
            text = filed.read_text(encoding="utf-8")
            self.assertEqual(sdlc_md.read_size(text), "M")
            self.assertIsNone(sdlc_md.read_points(text),
                              "a request is not pointed - the container carries no story points")
            bd = _bd(root, filed, "cr")
            self.assertEqual(bd["ungroomed"], [])
            self.assertTrue(bd["ok"])

    def test_a_cr_with_no_size_and_no_points_is_refused_naming_the_size_flag(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "cr")
            rc, msg = _file_cr(root)               # neither --size nor --points
            self.assertEqual(rc, 1)
            self.assertEqual(_artifacts(root, "cr"), [])
            self.assertIn("--size", msg)           # the refusal names the flag that fills it

    def test_a_value_off_the_tshirt_scale_is_refused(self) -> None:
        for bad in ("XXL", "5", "medium", "S/M/L", ""):
            with self.subTest(size=bad), tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _seed_index(root, "cr")
                rc, _ = _file_cr(root, "--size", bad)
                self.assertEqual(rc, 1, f"{bad!r} was accepted as a T-shirt size")
                self.assertEqual(_artifacts(root, "cr"), [])

    def test_the_scale_is_S_M_L_XL_and_nothing_else(self) -> None:
        self.assertEqual(sdlc_md.SIZE_SCALE, ("S", "M", "L", "XL"))


class ADeliveryUnitIsPointed(unittest.TestCase):
    """A story/bug is MEASURED: the gate demands POINTS of it, never a T-shirt Size."""

    def test_a_story_with_points_grooms(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            story = _write_story(root, "> **Points:** 5\n")
            bd = _bd(root, story, "story")
            self.assertEqual(bd["ungroomed"], [])
            self.assertTrue(bd["ok"])

    def test_a_story_with_no_points_is_ungroomed_for_points_not_size(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            story = _write_story(root, "")           # no size at all
            bd = _bd(root, story, "story")
            self.assertEqual(len(bd["ungroomed"]), 1)
            self.assertIn("Points", bd["ungroomed"][0]["missing"])
            self.assertNotIn("Size", bd["ungroomed"][0]["missing"])

    def test_a_bug_is_pointed_a_size_does_not_groom_it(self) -> None:
        # --size is not a bug's field: a delivery unit is measured in points, and a Size on it
        # leaves it ungroomed for Points. (Argparse still accepts the flag; the gate does not.)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "bug")
            rc, msg = _file_bug(root, "--size", "M")   # a Size, but no --points
            self.assertEqual(rc, 1)
            self.assertEqual(_artifacts(root, "bug"), [])
            self.assertIn("--points", msg)


class LegacyPointsOnACrAreTolerated(unittest.TestCase):
    """The transition may not invalidate the backlog. A CR filed with Points and no Size - the
    shape the earlier gate forced - still reads, still grooms, and still validates."""

    def test_a_legacy_points_cr_still_reads_and_grooms(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cr = _write_legacy_cr(root)
            text = cr.read_text(encoding="utf-8")
            self.assertEqual(sdlc_md.read_points(text), 5)   # legacy Points still READ
            self.assertIsNone(sdlc_md.read_size(text))       # it declares no T-shirt Size
            bd = _bd(root, cr, "cr")
            self.assertEqual(bd["ungroomed"], [],
                             "a legacy points-shaped CR must still count as sized")
            self.assertTrue(bd["ok"])

    def test_a_legacy_points_cr_still_validates(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cr = _write_legacy_cr(root)
            errs = [v for v in validate.validate_file(cr, "cr", root)
                    if v["severity"] == "error"]
            self.assertEqual(errs, [], f"legacy points CR failed validation: {errs}")


class ATshirtSizeIsNeverAMeasurement(unittest.TestCase):
    """Velocity and the forecast count STORY POINTS ONLY. A T-shirt Size is never summed."""

    def test_a_cr_tshirt_size_is_not_summed_into_the_forecast(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _seed_index(root, "cr")
            rc, _ = _file_cr(root, "--size", "L")   # an L would be 'big' if it were a number
            self.assertEqual(rc, 0)
            cr = _artifacts(root, "cr")[0]
            uid = sdlc_md.extract_record_id(cr.stem)
            fc = sprint._token_forecast(root, [{"id": uid, "type": "cr", "path": str(cr)}])
            self.assertEqual(fc["points"], 0, "a T-shirt Size leaked into the points total")
            self.assertIn(sdlc_md.norm_id(uid), [sdlc_md.norm_id(u) for u in fc["unpriced"]])

    def test_read_points_never_reads_a_size_as_a_number(self) -> None:
        # The one reader every velocity/forecast path shares must not see `Size: L` as points.
        cr_body = ("# CR-0002: sized L\n\n> **Status:** Proposed\n> **Size:** L\n\n"
                   "## Impact\n\ni\n")
        self.assertIsNone(sdlc_md.read_points(cr_body))
        self.assertEqual(sdlc_md.read_size(cr_body), "L")


if __name__ == "__main__":
    unittest.main()
