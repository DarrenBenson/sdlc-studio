"""`sprint.py plan` names, per unit, the registry files a change implies that its Affects omits.

A new skill script, a new verb or flag, and a reference page near a size threshold each owe
files beyond the ones the change edits, and a lane that does not declare them is refused at the
land after its whole hook run. The plan is the cheap place to say so: ADVISORY, per unit, and
only for registries the tree actually holds.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import types
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "sprint.py"
SKILL = ".claude/skills/sdlc-studio"
SCRIPTS = f"{SKILL}/scripts"

ROOT_CENSUS = "sdlc-studio/reviews/root-census.md"
COMMAND_AUDIT = "sdlc-studio/reviews/command-audit.md"
SCRIPTS_PAGE = f"{SKILL}/reference-scripts.md"
SURFACE_PAGE = f"{SKILL}/reference-scripts-surface.md"
SURFACE_LIB = f"{SCRIPTS}/lib/surface.py"
SPRINT_REPORT = f"{SCRIPTS}/sprint_report.py"
PROSE_SWEEP = f"{SCRIPTS}/tests/test_artifact.py"
BUDGETS = "tools/check_budgets.py"
GUIDE_TOOL = f"{SCRIPTS}/docgen.py"

HEADER = "Registry files the units' changes imply"


def _load():
    spec = importlib.util.spec_from_file_location("sprint", SCRIPT)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["sprint"] = mod
    spec.loader.exec_module(mod)
    return mod


def _write(root: Path, rel: str, text: str = "x\n") -> str:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return rel


#: A script with verbs, a nested sub-verb and flags: what a criterion's invocation is judged on.
WIDGET = '''import argparse


def build_parser():
    p = argparse.ArgumentParser(prog="widget.py")
    p.add_argument("--root")
    sub = p.add_subparsers(dest="cmd")
    spin = sub.add_parser("spin")
    spin.add_argument("--speed")
    lane = sub.add_parser("lane")
    lane.add_subparsers(dest="lcmd").add_parser("land")
    return p
'''

#: A free-prose writer: its parser takes a flag whose value is prose an author writes.
SCRIBE = '''import argparse


def build_parser():
    p = argparse.ArgumentParser(prog="scribe.py")
    sub = p.add_subparsers(dest="cmd")
    sub.add_parser("add").add_argument("--note")
    return p
'''


#: A parser with no verbs at all: a word after it is a positional argument, never a new verb.
PLAIN = '''import argparse


def build_parser():
    p = argparse.ArgumentParser(prog="plain.py")
    p.add_argument("--quiet")
    return p
'''

#: A script the installed skill and the consuming project both hold, under one name.
DEPLOY = '''import argparse


def build_parser():
    p = argparse.ArgumentParser(prog="deploy.py")
    p.add_subparsers(dest="cmd").add_parser("{verb}")
    return p
'''


def _scripts(root: Path) -> None:
    """The scripts a criterion can name: present in a consuming project's tree too."""
    _write(root, f"{SCRIPTS}/widget.py", WIDGET)
    _write(root, f"{SCRIPTS}/scribe.py", SCRIBE)
    _write(root, f"{SCRIPTS}/plain.py", PLAIN)


def _registries(root: Path) -> None:
    """Every registry the skill repository holds, as files on disk."""
    for rel in (ROOT_CENSUS, COMMAND_AUDIT, SCRIPTS_PAGE, SURFACE_PAGE, SURFACE_LIB,
                SPRINT_REPORT, GUIDE_TOOL):
        _write(root, rel)
    _write(root, PROSE_SWEEP, '_PROSE_FLAGS = ("--note", "--body")\n')
    _write(root, BUDGETS, 'REFERENCE_BUDGET = 600\nCEILING_TOLERANCE = 1.05\nALLOWLIST = {\n'
                          '    # a comment inside the literal, as the real one carries\n'
                          '    "reference-config.md": 695,\n    "reference-roomy.md": 800,\n'
                          '    "reference-close.md": 700,\n    "reference-c724.md": 700,\n'
                          '    "reference-c725.md": 700,\n}\n')


def _page(root: Path, name: str, lines: int, guide: bool = False) -> str:
    body = [f"# {name}"]
    if guide:
        body += ["<!-- BEGIN GENERATED reading-guide -->", "guide",
                 "<!-- END GENERATED reading-guide -->"]
    body += [f"line {i}" for i in range(lines - len(body))]
    return _write(root, f"{SKILL}/{name}", "\n".join(body) + "\n")


def _story(root: Path, num: int, affects: list[str], criteria: list[str]) -> None:
    body = "".join(f"\n### AC{i}: a\n\n- **Given** {c}\n- **Verify:** shell true\n"
                   for i, c in enumerate(criteria, 1))
    _write(root, f"sdlc-studio/stories/US{num:04d}-x.md",
           f"# US{num:04d}: s\n\n> **Status:** Ready\n> **Priority:** Medium\n"
           f"> **Affects:** {', '.join(affects)}\n> **Points:** 2\n\n"
           f"## Acceptance Criteria\n{body}")


def _plan(root: Path) -> tuple[int, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = _load().main(["plan", "--stories", "Ready", "--root", str(root),
                           "--no-fetch", "--skip-personas"])
    return rc, out.getvalue() + err.getvalue()


def _advice(out: str) -> dict[str, list[str]]:
    """`{unit id: [line, ...]}` from the registry block, and only from it."""
    lines = out.splitlines()
    starts = [i for i, ln in enumerate(lines) if HEADER in ln]
    found: dict[str, list[str]] = {}
    for i in starts:
        for ln in lines[i + 1:]:
            if not ln.startswith("    "):
                break
            uid, _, rest = ln.strip().partition(": ")
            found.setdefault(uid, []).append(rest)
    return found


def _line(lines: list[str], what: str) -> str:
    hits = [ln for ln in lines if ln.startswith(what + " -> ")]
    assert len(hits) == 1, f"expected one line for {what!r}, got {lines}"
    return hits[0].split(" -> ", 1)[1]


class PlanRegistryAdvisoryTests(unittest.TestCase):

    def test_a_new_script_names_its_registries(self) -> None:
        """AC1. A unit adding a script with only the script and its test in Affects is NOT clean:
        the census, a reference-scripts heading, the surface page and the command audit are owed,
        and lib/surface.py too when no criterion's code span names the script."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _registries(root)
            _scripts(root)
            _story(root, 1, [f"{SCRIPTS}/newlib.py", f"{SCRIPTS}/tests/test_newlib.py"],
                   ["a helper other scripts import"])
            _story(root, 2, [f"{SCRIPTS}/newcli.py", f"{SCRIPTS}/tests/test_newcli.py"],
                   ["`newcli.py run --fast` runs"])
            rc, out = _plan(root)
            self.assertEqual(rc, 0, out)
            adv = _advice(out)
            lib = _line(adv.get("US0001", []), "new script newlib.py")
            for owed in (ROOT_CENSUS, "reference-scripts", "### newlib.py", SURFACE_PAGE,
                         COMMAND_AUDIT, SURFACE_LIB):
                self.assertIn(owed, lib)
            cli = _line(adv.get("US0002", []), "new script newcli.py")
            for owed in (ROOT_CENSUS, "### newcli.py", SURFACE_PAGE, COMMAND_AUDIT):
                self.assertIn(owed, cli)
            self.assertNotIn(SURFACE_LIB, cli, "a script its criteria run has a parser")
            self.assertNotIn("test_newlib.py", "".join(adv["US0001"]),
                             "a new test module is not a new script")

    def test_a_new_verb_or_flag_names_its_registries(self) -> None:
        """AC2. A verb the parser lacks owes the surface page and NON_CEREMONY_VERBS, a flag owes
        the command audit (never the unjudged-flags baseline, which only shrinks), and the prose
        sweep is owed for --fields-file or a free-prose writer. What the parser has is silent, and
        so is a word after a leaf verb or after a parser with no verbs: a positional argument."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _registries(root)
            _scripts(root)
            _story(root, 1, [f"{SCRIPTS}/widget.py", f"{SCRIPTS}/scribe.py",
                             f"{SCRIPTS}/plain.py"], [
                "`widget.py frob` frobs",
                "`widget.py spin fast` and `plain.py go` take a positional argument, not a verb",
                "`python3 .claude/skills/sdlc-studio/scripts/widget.py lane dock --root .` docks",
                "`widget.py spin --torque 3` spins",
                "`widget.py --fields-file f.json` reads",
                "`scribe.py add --tag x` tags",
                "`widget.py spin --speed 2` and `widget.py lane land` and `scribe.py add --note n`",
            ])
            rc, out = _plan(root)
            self.assertEqual(rc, 0, out)
            lines = _advice(out).get("US0001", [])
            for verb in ("widget.py frob", "widget.py lane dock"):
                owed = _line(lines, f"new verb {verb}")
                self.assertIn(SURFACE_PAGE, owed)
                self.assertIn(SPRINT_REPORT, owed)
                self.assertIn("NON_CEREMONY_VERBS", owed)
            self.assertEqual(_line(lines, "new flag widget.py --torque"), COMMAND_AUDIT)
            for flag in ("widget.py --fields-file", "scribe.py --tag"):
                owed = _line(lines, f"new flag {flag}")
                self.assertIn(COMMAND_AUDIT, owed)
                self.assertIn(PROSE_SWEEP, owed)
            text = "\n".join(lines)
            for known in ("spin ->", "--speed", "lane land", "--note", "--root", "widget.py lane ->",
                          "spin fast", "plain.py"):
                self.assertNotIn(known, text, f"{known!r} is already on the parser")
            self.assertNotIn("unjudged-flags-baseline", out)
            self.assertEqual(len(lines), 5, lines)

    def test_a_page_near_a_threshold_names_the_guide_or_ceiling(self) -> None:
        """AC3. A 395-line page nears the 400-line guide threshold; reference-config.md at 729
        lines sits at 695 plus 5% and a 726-line page 9 below 700 plus 5% (735); a 610-line page
        has no ALLOWLIST entry. Each names the threshold, the size and what to add. A page one
        line outside either window (379 lines; 829 against 800 plus 5%, 840) is silent, and
        each window's edges are pinned on both sides."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _registries(root)
            pages = [_page(root, "reference-near.md", 395), _page(root, "reference-config.md", 729),
                     _page(root, "reference-wild.md", 610), _page(root, "reference-under.md", 379),
                     _page(root, "reference-roomy.md", 829), _page(root, "reference-close.md", 726)]
            _story(root, 1, pages, ["the pages grow"])
            # Each window's edges: the guide's 380-399, the budget's 601 on, the ceiling's 725 on.
            edges = {n: _page(root, f"reference-{k}{n}.md", n)
                     for k, n in (("g", 380), ("g", 399), ("g", 400), ("b", 600), ("b", 601),
                                  ("c", 724), ("c", 725))}
            _story(root, 2, list(edges.values()), ["the pages grow to the edges"])
            rc, out = _plan(root)
            self.assertEqual(rc, 0, out)
            edge = _advice(out).get("US0002", [])
            for n, why in ((380, "400-line reading-guide"), (399, "400-line reading-guide"),
                           (601, "600-line budget"), (725, "700 +5% allows 735")):
                self.assertIn(why, _line(edge, f"{Path(edges[n]).name}: {n} lines"))
            self.assertEqual(len(edge), 4, f"400, 600 and 724 lines are outside: {edge}")
            lines = _advice(out).get("US0001", [])
            near = _line(lines, "reference-near.md: 395 lines")
            self.assertIn("400-line reading-guide threshold", near)
            self.assertIn("docgen.py reading-guides", near)
            config = _line(lines, "reference-config.md: 729 lines")
            self.assertIn("695", config)
            self.assertIn("729", config)
            self.assertIn(BUDGETS, config)
            close = _line(lines, "reference-close.md: 726 lines")
            self.assertIn("700 +5% allows 735", close)
            self.assertIn(BUDGETS, close)
            wild = _line(lines, "reference-wild.md: 610 lines")
            self.assertIn("600", wild)
            self.assertIn("ALLOWLIST", wild)
            self.assertIn(BUDGETS, wild)
            text = "\n".join(lines)
            self.assertNotIn("reference-under.md", text)
            self.assertNotIn("reference-roomy.md", text)
            self.assertEqual(len(lines), 4, lines)

    def test_a_unit_naming_its_registries_or_a_consuming_project_is_clean(self) -> None:
        """AC4. The same units with the implied files declared report nothing, the same units in
        a tree holding none of the registries report nothing, a local install's project script
        that shares a skill script's name draws none of the skill's registries, and the advisory
        never refuses a plan, not even under `sprint.affects_check: block`."""
        def units(root: Path, declared: bool) -> None:
            extra = [ROOT_CENSUS, SCRIPTS_PAGE, SURFACE_PAGE, COMMAND_AUDIT, SURFACE_LIB,
                     SPRINT_REPORT, PROSE_SWEEP, BUDGETS] if declared else []
            _story(root, 1, [f"{SCRIPTS}/newlib.py", *extra], ["a helper"])
            _story(root, 2, [f"{SCRIPTS}/widget.py", f"{SCRIPTS}/scribe.py", *extra],
                   ["`widget.py frob --fields-file f` and `scribe.py add --tag x`"])
            near = _page(root, "reference-near.md", 395, guide=declared)
            _story(root, 3, [near, _page(root, "reference-config.md", 729), *extra],
                   ["the pages grow"])

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _registries(root)
            _scripts(root)
            units(root, declared=True)
            rc, out = _plan(root)
            self.assertEqual(rc, 0, out)
            self.assertEqual(_advice(out), {}, out)
            self.assertNotIn(HEADER, out)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _scripts(root)
            units(root, declared=False)
            rc, out = _plan(root)
            self.assertEqual(rc, 0, out)
            self.assertNotIn(HEADER, out, "a consuming project holds none of these registries")

        with tempfile.TemporaryDirectory() as d:
            # A local install: the skill's scripts AND the registries its payload ships, beside
            # the project's own scripts/deploy.py. Only the skill's own copy is judged.
            root = Path(d)
            for rel in (SCRIPTS_PAGE, SURFACE_PAGE, SURFACE_LIB, SPRINT_REPORT):
                _write(root, rel)
            _write(root, f"{SCRIPTS}/deploy.py", DEPLOY.format(verb="status"))
            own = _write(root, "scripts/deploy.py", DEPLOY.format(verb="rollback"))
            _story(root, 1, [own], ["`python3 scripts/deploy.py rollback --to v2` rolls back",
                                    "`deploy.py rollback` rolls back"])
            _story(root, 2, [own], [f"`python3 {SCRIPTS}/deploy.py rollback` rolls back"])
            _story(root, 3, [f"{SCRIPTS}/deploy.py"], ["`deploy.py rollback` rolls back"])
            _story(root, 4, [f"{SCRIPTS}/deploy.py"], ["`vendor/scripts/deploy.py rollback` too"])
            rc, out = _plan(root)
            self.assertEqual(rc, 0, out)
            adv = _advice(out)
            for uid in ("US0001", "US0004"):
                self.assertNotIn(uid, adv, "another directory's script is not the skill's")
            for uid in ("US0002", "US0003"):
                owed = _line(adv.get(uid, []), "new verb deploy.py rollback")
                self.assertIn(SURFACE_PAGE, owed, "the skill's own path, or one its Affects names")
                self.assertIn(SPRINT_REPORT, owed)

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _registries(root)
            _scripts(root)
            _write(root, "sdlc-studio/.config.yaml", "sprint:\n  affects_check: block\n")
            _story(root, 2, [f"{SCRIPTS}/widget.py"], ["`widget.py frob` frobs"])
            rc, out = _plan(root)
            self.assertIn(HEADER, out, "the precondition: the advisory IS raised")
            self.assertEqual(rc, 0, out)

    def test_reading_a_scripts_parser_leaves_the_running_modules_in_place(self) -> None:
        """The tree's copy of a script is loaded under its own name to read its parser. A module
        of that name the plan was already running is put back, and a name nothing held is
        released, so a tree's copy never replaces the running plan's `config` or the like."""
        running = types.ModuleType("widget")
        running.__file__ = "/elsewhere/widget.py"
        sys.modules["widget"] = running
        sys.modules.pop("scribe", None)
        try:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _registries(root)
                _scripts(root)
                _story(root, 1, [f"{SCRIPTS}/widget.py", f"{SCRIPTS}/scribe.py"],
                       ["`widget.py frob` frobs", "`scribe.py jot` jots"])
                rc, out = _plan(root)
            self.assertEqual(rc, 0, out)
            lines = _advice(out).get("US0001", [])
            for what in ("new verb widget.py frob", "new verb scribe.py jot"):
                _line(lines, what)                      # the precondition: both were read
            self.assertIs(sys.modules.get("widget"), running)
            self.assertNotIn("scribe", sys.modules)
        finally:
            sys.modules.pop("widget", None)


if __name__ == "__main__":
    unittest.main()
