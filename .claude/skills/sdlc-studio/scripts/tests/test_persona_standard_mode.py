"""`personas.standard` sets how the persona standard holds a project's own cards: `block` (the
default) refuses a card that breaks a blocking rule, and `report` frames it and names it on one
stderr line. `project_upgrade.py --apply` sets `report` for a project holding its own cards, so
an upgrade names them rather than refusing them, and an unknown value is read as `block`.

Driven through the shipped entry points as the operator runs them (`persona_resolve.py`,
`critic.py`, `project_upgrade.py`), in throwaway projects built on the persona-block fixture: a
qa seat card carrying a demographic token, which `seat-demographic-fluff` blocks.
"""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_persona_review_block as pb  # noqa: E402 - the fixture, the confined CLI runner

SKILL = pb.SCRIPTS.parent
REPORT = "persona card blocked (report mode):"
TOKEN_CARD = pb._seat("qa", "Ivy Cole", extra=" She is 42 years old.")
CONFIG = "two_backlog:\n  enforce: true\n"


def _project(root: Path, standard: str | None) -> None:
    pb._fixture(root, TOKEN_CARD)
    pb._write(root, "sdlc-studio/.config.yaml",
              CONFIG + (f"personas:\n  standard: {standard}\n" if standard else ""))


def _runs(root: Path) -> dict[str, tuple[int, str, str]]:
    return {"resolve": pb._resolve(root, "--render", "review"),
            "critic brief": pb._cli(root, "critic.py", "brief", "--unit", "US0001", "--seat",
                                    "qa", "--root", str(root))}


#: What each run prints when it frames the card: resolve prints the card, the brief its path.
FRAMED = {"resolve": "Ivy Cole reviews the work.", "critic brief": f"/{pb.QA} (the review render)"}


def _lines(err: str, prefix: str) -> list[str]:
    return [ln for ln in err.splitlines() if ln.startswith(prefix)]


def _upgradable(root: Path, cards: str = "", standard: str = "") -> None:
    """A project an older skill set up: a `.version` naming skill 1.0.0, a config setting
    `personas.standard` only when `standard` names a value, and its own cards: `seat` a qa seat
    card, `persona` a persona card, both or neither."""
    pb._write(root, "sdlc-studio/.config.yaml",
              "# this project's own settings\npersonas:\n  staleness_days: 30\n"
              + (f"  standard: {standard}\n" if standard else ""))
    pb._write(root, "sdlc-studio/.version",
              "schema_version: 3\nupgraded_from: null\nupgraded_at: 2026-01-01\n"
              'skill_version: "1.0.0"\n')
    pb._write(root, "sdlc-studio/stories/US0001-a-story-on-disk.md", pb.STORY)
    if "seat" in cards:
        pb._write(root, pb.QA, pb._seat("qa", "Ivy Cole"))
    if "persona" in cards:
        pb._write(root, "sdlc-studio/personas/ada-lane.md", "# Ada Lane\n\nSomebody.\n")


class PersonaStandardModeTests(unittest.TestCase):

    def test_report_mode_names_a_blocked_card_and_frames_it(self) -> None:
        """AC1. Mutants: report mode refusing as block; report mode printing no line, or the
        line once per resolution; block mode, or no key, framing the card."""
        results = {}
        for standard in ("report", "block", None):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d) / "proj"
                root.mkdir()
                _project(root, standard)
                results[standard] = _runs(root)
        for name, (rc, out, err) in results["report"].items():
            with self.subTest(mode="report", run=name):
                self.assertEqual(0, rc, err)
                self.assertIn(FRAMED[name], out)
                lines = _lines(err, REPORT)
                self.assertEqual(1, len(lines), err)
                self.assertIn(f" {pb.QA} ", lines[0])
                self.assertIn("seat-demographic-fluff", lines[0])
                remedy = pb.REMEDY_RE.search(lines[0])
                self.assertIsNotNone(remedy, lines[0])
                self.assertEqual(pb.QA, remedy.group(1))
                self.assertNotEqual("qa", remedy.group(2))
        for standard in ("block", None):
            for name, want in (("resolve", 1), ("critic brief", 2)):
                rc, out, err = results[standard][name]
                with self.subTest(mode=standard, run=name):
                    self.assertEqual(want, rc, err)
                    self.assertIn("seat-demographic-fluff", err)
                    self.assertIn(pb.QA, err)
                    self.assertEqual([], _lines(err, REPORT))
                    self.assertNotIn(FRAMED[name], out)

    def test_an_upgrade_sets_report_mode_only_for_a_project_with_its_own_cards(self) -> None:
        """AC2. Mutants: the upgrade leaving a carded project without the key, or counting only
        one kind of card; writing it for a project with no cards of its own, or over a value
        the project set; the report not naming the setting that turns the standard on; the
        rest of the config lost."""
        projects = {"seat": ("seat", ""), "persona": ("persona", ""), "bare": ("", ""),
                    "set": ("seat persona", "block")}
        runs, configs, before = {}, {}, {}
        with tempfile.TemporaryDirectory() as d:
            for name, (cards, standard) in projects.items():
                root = Path(d) / name
                root.mkdir()
                _upgradable(root, cards, standard)
                cfg = root / "sdlc-studio" / ".config.yaml"
                before[name] = cfg.read_bytes()
                runs[name] = pb._cli(root, "project_upgrade.py", "--apply", "--root", str(root))
                configs[name] = cfg.read_text(encoding="utf-8")
        for name, (rc, out, err) in runs.items():
            self.assertEqual(0, rc, f"{name}: {err}")
        for name in ("seat", "persona"):
            with self.subTest(project=name):
                text, out = configs[name], runs[name][1]
                self.assertEqual({"personas": {"staleness_days": 30, "standard": "report"}},
                                 yaml.safe_load(text))
                self.assertTrue(text.startswith("# this project's own settings\n"), text)
                applied = [ln for ln in out.splitlines() if "personas.standard" in ln
                           and ln.lstrip().startswith("+ ")]
                self.assertEqual(1, len(applied), out)
                self.assertTrue(applied[0].lstrip().startswith("+ set personas.standard: report"),
                                applied[0])
                self.assertIn("personas.standard: block", applied[0])
        for name in ("bare", "set"):
            with self.subTest(project=name):
                self.assertEqual(before[name], configs[name].encode("utf-8"))
                self.assertNotIn("personas.standard", runs[name][1])

    def test_the_key_is_documented_and_an_unknown_value_fails_safe(self) -> None:
        """AC3. Mutants: an unknown value read as report, or read as block with no line naming
        the key; the key undocumented in either file."""
        defaults_text = (SKILL / "templates" / "config-defaults.yaml").read_text(encoding="utf-8")
        self.assertEqual("block", yaml.safe_load(defaults_text)["personas"]["standard"])
        block = defaults_text.split("\npersonas:\n", 1)[1].split("\n\n", 1)[0]
        for word in ("block", "report", "project_upgrade"):
            self.assertIn(word, block)
        rows = [ln for ln in (SKILL / "reference-config.md").read_text(encoding="utf-8")
                .splitlines() if ln.startswith("| `personas.standard` |")]
        self.assertEqual(1, len(rows))
        cells = [c.strip() for c in rows[0].strip("|").split("|")]
        self.assertEqual("`block`", cells[1])
        for word in ("`block`", "`report`", "project_upgrade"):
            self.assertIn(word, cells[2])
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "proj"
            root.mkdir()
            _project(root, "warn")
            rc, out, err = pb._resolve(root)
        self.assertEqual(1, rc, err)
        self.assertIn("seat-demographic-fluff", err)
        self.assertEqual([], _lines(err, REPORT))
        named = [ln for ln in err.splitlines() if "personas.standard" in ln]
        self.assertEqual(1, len(named), err)
        for word in ("'warn'", "block", "report"):
            self.assertIn(word, named[0])
        self.assertNotIn(FRAMED["resolve"], out)

    def test_the_dry_run_lists_the_config_write_apply_performs(self) -> None:
        """Mutants: the dry run's auto-correctable list leaving out the write `--apply` makes;
        listing it for a project with no cards of its own or a value set; the dry run writing."""
        projects = {"seat": ("seat", ""), "bare": ("", ""), "set": ("seat persona", "block")}
        dry, applied = {}, {}
        with tempfile.TemporaryDirectory() as d:
            for name, (cards, standard) in projects.items():
                root = Path(d) / name
                root.mkdir()
                _upgradable(root, cards, standard)
                cfg = root / "sdlc-studio" / ".config.yaml"
                before = cfg.read_bytes()
                dry[name] = pb._cli(root, "project_upgrade.py", "--root", str(root))
                self.assertEqual(before, cfg.read_bytes(), f"{name}: the dry run wrote")
                applied[name] = pb._cli(root, "project_upgrade.py", "--apply", "--root",
                                        str(root))
        rc, out, err = dry["seat"]
        self.assertEqual(0, rc, err)
        auto = [ln.strip() for ln in out.splitlines() if ln.strip().startswith("[auto]")]
        write = [ln for ln in auto if "personas.standard" in ln]
        self.assertEqual(1, len(write), out)
        self.assertTrue(write[0].startswith("[auto]   set personas.standard: report in "
                                            "sdlc-studio/.config.yaml"), write[0])
        # The preview and the change `--apply` reports are the same words.
        done = [ln.strip() for ln in applied["seat"][1].splitlines()
                if ln.strip().startswith("+ ") and "personas.standard" in ln]
        self.assertEqual([write[0].removeprefix("[auto]").strip()],
                         [ln.removeprefix("+").strip() for ln in done])
        for name in ("bare", "set"):
            with self.subTest(project=name):
                self.assertNotIn("personas.standard", dry[name][1])

    def test_the_config_write_keeps_the_project_s_own_layout(self) -> None:
        """Mutants: the key always indented two spaces, breaking a four-space block; a one-line
        `personas:` read as no block, so a second block is appended and PyYAML keeps only it,
        losing `staleness_days`; a one-line block listed under Applied as though written; a
        second `--apply` adding the key again."""
        configs = {"four": "personas:\n    staleness_days: 30\n",
                   "one-line": "personas: {staleness_days: 30}\n"}
        runs, texts = {}, {}
        with tempfile.TemporaryDirectory() as d:
            for name, config in configs.items():
                root = Path(d) / name
                root.mkdir()
                _upgradable(root, "seat")
                cfg = root / "sdlc-studio" / ".config.yaml"
                cfg.write_text(config, encoding="utf-8")
                runs[name] = [pb._cli(root, "project_upgrade.py", *extra, "--root", str(root))
                              for extra in ((), ("--apply",), ("--apply",))]
                texts[name] = cfg.read_text(encoding="utf-8")
        self.assertEqual({"personas": {"staleness_days": 30, "standard": "report"}},
                         yaml.safe_load(texts["four"]))
        self.assertIn("\n    standard: report\n", texts["four"])
        self.assertEqual(1, texts["four"].count("standard: report"))
        self.assertNotIn("personas.standard", runs["four"][2][1])
        # A one-line block is never rewritten: it is reported for a person, never as applied.
        self.assertEqual(configs["one-line"], texts["one-line"])
        for rc, out, err in runs["one-line"]:
            self.assertEqual(0, rc, err)
            self.assertEqual([], [ln for ln in out.splitlines() if "personas.standard" in ln
                                  and not ln.strip().startswith("[manual]")])
            manual = [ln for ln in out.splitlines() if ln.strip().startswith("[manual]")
                      and "personas.standard" in ln]
            self.assertEqual(1, len(manual), out)
            self.assertIn("standard: report", manual[0])

    def test_a_sibling_seat_card_that_is_not_utf8_leaves_both_modes_working(self) -> None:
        """Mutants: a seat card's declared role read as strict UTF-8 again, so the resolver's
        walk over every seat card tracebacks on the engineering card; that card's hold ignored,
        so the remedy names the engineering seat, first in the roster, rather than product.
        (`critic.py brief` reads every seat card itself and refuses such a tree cleanly,
        BG1667's ground, so only the resolver runs.)"""
        results = {}
        for standard in ("report", "block"):
            with tempfile.TemporaryDirectory() as d:
                root = Path(d) / "proj"
                root.mkdir()
                _project(root, standard)
                card = root / pb.ENGINEERING
                card.write_bytes(card.read_bytes().replace(b"reviews the work.",
                                                           b"reviews S\xe3o's work."))
                results[standard] = pb._resolve(root, "--render", "review")
        rc, out, err = results["report"]
        self.assertEqual(0, rc, err)
        self.assertNotIn("Traceback", err)
        self.assertIn(FRAMED["resolve"], out)
        lines = _lines(err, REPORT)
        self.assertEqual(1, len(lines), err)
        self.assertIn(f" {pb.QA} ", lines[0])
        remedy = pb.REMEDY_RE.search(lines[0])
        self.assertIsNotNone(remedy, lines[0])
        self.assertEqual("product", remedy.group(2))
        rc, out, err = results["block"]
        self.assertEqual(1, rc, err)
        self.assertNotIn("Traceback", err)
        self.assertIn("seat-demographic-fluff", err)
        self.assertNotIn(FRAMED["resolve"], out)

if __name__ == "__main__":
    unittest.main()
