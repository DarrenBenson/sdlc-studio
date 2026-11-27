"""US1328: the help, upgrade and public pages describe what 6.5 ships.

Each test names its mutant first: the page as it stood when EP0379 was groomed, which must fail
it. What a page claims is read against the code rather than a hand list wherever the code holds
it: the gate's and the config loader's PyYAML refusals from real runs with a `yaml` module that
will not import; the report-mode line and the block from real `persona_resolve.py` runs; the
duplicate refusal and the `Distinct-from` line from real `file_finding.py file` runs; the
`risk-class` drift and its raise from real `reconcile.py` runs; the runner's verdict lines, the
kept list and its replay from real `mutation.py`, `critic.py self-check record` and
`critic.py brief` runs; the Signed by cell and the Accountable line from the functions that
write them; and what a 6.4 project owes `migrate` from real `migrate.py` runs on a 6.4-shaped
fixture. Every section is found by its heading, never by its position, so a later release's
section above it leaves these true.
"""
# test-census-subject: docs/existing-users.md
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
SCRIPTS = SKILL / "scripts"
HELP = SKILL / "help"
README = REPO / "README.md"
LLMS = REPO / "llms.txt"
LEADERS = REPO / "docs" / "engineering-leaders.md"
UPGRADE = REPO / "docs" / "existing-users.md"
BG1613 = REPO / "sdlc-studio" / "bugs"

sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS / "tests"))
sys.path.insert(0, str(REPO / "tools"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import critic  # noqa: E402
import escape  # noqa: E402
import loop_guard  # noqa: E402
import release_cut  # noqa: E402
import retro  # noqa: E402
import yaml  # noqa: E402
from lib import cost_anatomy, risk_class  # noqa: E402
import test_cache_read_fall as crf  # noqa: E402
import test_delegation_disclosure as dd  # noqa: E402
import test_effort_by_kind as ebk  # noqa: E402
import test_engineering_leaders_page as elp  # noqa: E402
import test_enterprise_doc as ent  # noqa: E402
import test_loop_guard_spend as lgs  # noqa: E402
import test_readme_front_door as rfd  # noqa: E402
import test_release_record as rr  # noqa: E402
import evidence_pack  # noqa: E402
import gate  # noqa: E402
import persona_review  # noqa: E402
import sprint  # noqa: E402
import sprint_report  # noqa: E402
import test_lean_docs_v64 as v64  # noqa: E402
import test_lean_sign_principal as sp  # noqa: E402
import test_persona_review_block as pb  # noqa: E402

_read, _flat = v64._read, v64._flat
_config_ref_default, _shipped_default = v64._config_ref_default, v64._shipped_default

#: The configuration keys 6.5 adds, each with the dotted path its shipped default sits at.
#: The two keys that turn the solution review on, in `NEW_KEYS` with the rest.
SOLUTION_KEYS = ("review.solution_review.min_points", "review.solution_review.risk_classes")
NEW_KEYS = ("personas.standard", "ci.wait_timeout_minutes", "ci.rerun_limit",
            "review.rendered_paths", *SOLUTION_KEYS)
#: The spend and per-kind effort keys the widened 6.5 adds, each shown with its default.
SPEND_EFFORT_KEYS = ("appetite.spend", "capacity.spend", "routing.effort.docs",
                     "routing.effort.bug", "routing.effort.code")
ENTERPRISE = REPO / "docs" / "enterprise.md"
SEATS_REF = SKILL / "reference-workflow-personas.md"
SEATS_ANCHOR = "seats-for-the-requirements-documents"
LANES_LINK = "](../.claude/skills/sdlc-studio/help/sprint.md#lanes-dispatching-work-and-accepting-it-back)"
NUMBER_WORDS = {5: "five", 10: "ten"}

#: What a page says of PyYAML's system package: the distribution's own, named per distribution.
DISTRO_PACKAGE = ("your distribution's PyYAML package", "`python3-yaml` on Debian and Ubuntu",
                  "`python-yaml` on Arch")
#: The wording that gave Debian's name as every system's package.
ONE_PACKAGE = "package manager's `python3-yaml`"
#: A gate lane's result line, as the gate prints one for each lane it runs.
LANE_LINE = r"(?m)^\s*\[(?:PASS|FAIL|WARN|SKIP)\] "

#: A qa seat card that breaks a blocking rule: a demographic token in its identity.
TOKEN_CARD = pb._seat("qa", "Ivy Cole", extra=" She is 42 years old.")
REPORT_LINE = "persona card blocked (report mode):"


def _section(text: str, heading: str) -> str:
    """The body under the heading line `heading`, up to the next heading of its level or
    higher outside a code fence, so a `# comment` in a shell block does not end it."""
    lines = text.splitlines(keepends=True)
    level = len(heading) - len(heading.lstrip("#"))
    start = next((i for i, ln in enumerate(lines) if ln.rstrip() == heading), None)
    if start is None:
        return ""
    fenced, body = False, []
    for line in lines[start + 1:]:
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and re.match(rf"^#{{1,{level}}} ", line):
            break
        body.append(line)
    return "".join(body)


def _stated_default(key: str) -> str:
    """The default `reference-config.md` states for `key`, as `_config_ref_default` reads it,
    else, for a per-kind entry such as `routing.effort.docs`, the last cell of the row whose
    first cell names the parent key "per kind" and the kind: never a role row's `inherit`."""
    if stated := _config_ref_default(key):
        return stated
    parent, _, kind = key.rpartition(".")
    for line in _read(v64.CONFIG_REF).splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        if line.startswith("| `") and cells[0].startswith(f"`{parent}` per kind") \
                and f"`{kind}`" in cells[0]:
            return cells[-1].strip("`")
    return ""


def _verbs(parser: argparse.ArgumentParser, at: tuple = ()) -> set[tuple]:
    """Every sub-verb path a parser takes, as its subparsers hold them: `("approach", "brief")`."""
    out: set[tuple] = set()
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            for name, sub in action.choices.items():
                out |= {at + (name,)} | _verbs(sub, at + (name,))
    return out


def _block(text: str, start: str) -> str:
    """The paragraph or list item of `text` that starts with `start`, flattened; "" if none."""
    return _flat(next((b for b in re.split(r"\n(?=- |\d+\. )|\n\s*\n", text)
                       if b.lstrip().startswith(start)), ""))


def _helper(case_class: type) -> unittest.TestCase:
    """A feature story's own fixture case, set up for reuse; the caller cleans it up."""
    case = case_class()
    case.setUp()
    return case


def _links_resolve(case: unittest.TestCase, text: str, page: Path) -> None:
    v64._assert_links_resolve(case, text, page)


def _write(root: Path, rel: str, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def _anchors_above(path: Path, needle: str) -> set[str]:
    """The anchors of the heading nearest above the first line of `path` that starts with
    `needle`, so a link to that heading lands on the line; empty when no line does."""
    heading = ""
    for line in _read(path).splitlines():
        if re.match(r"^#{1,6}\s", line):
            heading = line
        elif line.startswith(needle):
            title = heading.lstrip("#").strip()
            return set(re.findall(r"\{#([\w-]+)\}", title)) | {v64.check_links.slug(title)}
    return set()


def _skill_version() -> tuple[int, ...]:
    """The skill version this tree ships, from `templates/version.yaml`, as a tuple of ints."""
    m = re.search(r'(?m)^skill_version:\s*"?(\d+)\.(\d+)\.(\d+)',
                  _read(SKILL / "templates" / "version.yaml"))
    assert m, "templates/version.yaml names no skill_version"
    return tuple(int(g) for g in m.groups())


def _bug_status(bug: str) -> str:
    """The `Status` a bug's own file holds, or "" when no file holds the bug."""
    for path in sorted(BG1613.glob(f"{bug}-*.md")):
        if m := re.search(r"(?m)^> \*\*Status:\*\* (\S+)", _read(path)):
            return m.group(1)
    return ""


def _fixture_64(tmp: Path, *, cards: bool = True,
                retired: bool = True) -> tuple[v64._Fixture, Path]:
    """A project as 6.4 left it: initialised, stamped 6.4.0, its own seat card when `cards`,
    `require_ac_verification` set when `retired`, and no `personas.standard`."""
    fx = v64._Fixture(tmp)
    made = fx.run("init.py", "--root", str(fx.root), "run")
    assert made.returncode == 0, made.stdout + made.stderr
    fx.write("sdlc-studio/.version", 'schema_version: 3\nupgraded_from: 6.3.0\n'
                                     'upgraded_at: 2026-11-16\nskill_version: "6.4.0"\n')
    config = fx.root / "sdlc-studio" / ".config.yaml"
    body = _read(config) if config.is_file() else ""
    if retired:
        body += "\nrequire_ac_verification: true\n"
    config.write_text(body, encoding="utf-8")
    if cards:
        fx.write(pb.QA, pb._seat("qa", "Ivy Cole"))
    return fx, config


def _owed(fx: v64._Fixture) -> list[str]:
    proc = fx.run("migrate.py", "--root", str(fx.root), "--format", "json")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return [str(item.get("detail", "")) for item in json.loads(proc.stdout)["deterministic"]]


class DocsV65Tests(unittest.TestCase):

    def test_the_help_pages_name_the_refusals_65_adds(self):
        """Mutant: the four help pages as EP0379's grooming found them, help/upgrade.md's
        Prerequisites naming no PyYAML, help/persona.md no `personas.standard`, help/bug.md no
        `--distinct-from` and help/reconcile.md's fixes table no `risk-class`. AC1."""
        # help/upgrade.md: the PyYAML prerequisite, against the gate's and the loader's refusals.
        page = HELP / "upgrade.md"
        pre = _flat(_section(_read(page), "## Prerequisites"))
        self.assertTrue(pre, "help/upgrade.md has no Prerequisites section")
        for needle in ("Python 3.10+", "PyYAML", f"`{gate.PYYAML_INSTALL}`", "installers",
                       "`gate.py`", "`.config.yaml`", "refuse", *DISTRO_PACKAGE):
            self.assertIn(needle, pre, f"the Prerequisites section does not say {needle!r}")
        self.assertNotIn(ONE_PACKAGE, pre, "the page gives Debian's package name for every system")
        _links_resolve(self, pre, page)
        self.assertEqual(gate.PYYAML_INSTALL, "python3 -m pip install pyyaml")
        for installer in ("install.sh", "install.ps1"):
            source = _read(REPO / installer)
            self.assertTrue("-m pip install pyyaml" in source and "PyYAML" in source,
                            f"{installer} names no PyYAML refusal and install command")
        with tempfile.TemporaryDirectory() as tmp:
            fx = v64._Fixture(Path(tmp))
            shim = _write(Path(tmp), "noyaml/yaml.py", "raise ImportError('no yaml here')\n")
            fx.env["PYTHONPATH"] = str(shim.parent)
            fx.write("sdlc-studio/.config.yaml", "review:\n  author_self_check: report\n")
            refused = fx.run("gate.py", "--root", str(fx.root))
            self.assertEqual(refused.returncode, 2, refused.stdout + refused.stderr)
            self.assertIn("PyYAML is required", refused.stdout + refused.stderr)
            self.assertIn(gate.PYYAML_INSTALL, refused.stdout + refused.stderr)
            self.assertIn(f"`gate.py` refuses with exit {refused.returncode} before any lane runs",
                          pre, "the page states another exit, or another order, than the gate's")
            self.assertNotRegex(refused.stdout + refused.stderr, LANE_LINE,
                                "the refused gate ran a lane")
            read = fx.run("config.py", "--root", str(fx.root), "show")
            self.assertEqual(read.returncode, 1, read.stdout + read.stderr)
            self.assertIn("PyYAML", read.stderr)
            self.assertIn(gate.PYYAML_INSTALL, read.stderr)
            fx.env.pop("PYTHONPATH")
            read = fx.run("config.py", "--root", str(fx.root), "show")
            self.assertEqual(read.returncode, 0, "the positive control: with PyYAML it reads")
            ran = fx.run("gate.py", "--root", str(fx.root))
            self.assertRegex(ran.stdout + ran.stderr, LANE_LINE,
                             "the positive control: with PyYAML the gate prints its lanes")

        # help/persona.md: the standard's two modes, against real resolutions.
        page = HELP / "persona.md"
        review = _flat(_section(_read(page), "### review"))
        self.assertTrue(review, "help/persona.md has no review section")
        for needle in ("`personas.standard`", "`block`, the default", "`report` frames the card",
                       f"`{REPORT_LINE}`", "`migrate --apply`", "its own cards",
                       "no value set", "](../reference-persona.md#persona-rules)"):
            self.assertIn(needle, review, f"the persona review section does not say {needle!r}")
        _links_resolve(self, review, page)
        config_link = re.search(r"\]\(\.\./reference-config\.md#([\w-]+)\)", review)
        self.assertIsNotNone(config_link, "the persona review section does not link "
                                          "reference-config.md")
        self.assertIn(config_link.group(1), _anchors_above(v64.CONFIG_REF, "| `personas.standard` |"),
                      "the reference-config.md link does not land on the personas.standard row")
        self.assertEqual(persona_review.STANDARD_KEY, "personas.standard")
        self.assertEqual(_config_ref_default("personas.standard"), "block")
        runs = {}
        for standard in ("report", "block", None):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp) / "proj"
                root.mkdir()
                pb._fixture(root, TOKEN_CARD)
                _write(root, "sdlc-studio/.config.yaml", "two_backlog:\n  enforce: true\n"
                       + (f"personas:\n  standard: {standard}\n" if standard else ""))
                runs[standard] = pb._resolve(root, "--render", "review")
        rc, out, err = runs["report"]
        self.assertEqual(rc, 0, err)
        self.assertIn("Ivy Cole reviews the work.", out)
        self.assertEqual(len([ln for ln in err.splitlines() if ln.startswith(REPORT_LINE)]), 1)
        for standard in ("block", None):
            rc, out, err = runs[standard]
            self.assertEqual(rc, 1, f"standard {standard!r} framed a card that breaks a rule")
            self.assertIn("seat-demographic-fluff", err)
            self.assertNotIn(REPORT_LINE, err)
        with tempfile.TemporaryDirectory() as tmp:
            fx, config = _fixture_64(Path(tmp), retired=False)
            done = fx.run("migrate.py", "--root", str(fx.root), "--apply")
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertRegex(_read(config), r"(?m)^personas:\n(?:  .*\n)*?  standard: report$")

        # help/bug.md: the duplicate refusal and `--distinct-from`, against real filings.
        page = HELP / "bug.md"
        filing = _flat(_section(_read(page), "## File a bug non-interactively (the canonical "
                                             "path)"))
        self.assertTrue(filing, "help/bug.md has no filing section")
        for needle in ("`file_finding.py file`", "every declared `Affects` path",
                       "of its type", "duplicate bar", "exits 1 and writes nothing",
                       "`--distinct-from <id>`", "`Distinct-from` line"):
            self.assertIn(needle, filing, f"the filing section does not say {needle!r}")
        with tempfile.TemporaryDirectory() as tmp:
            fx = v64._Fixture(Path(tmp))
            fx.write("src/thing.py", "")
            fx.write("sdlc-studio/bugs/_index.md",
                     "# Index\n\n## Summary\n\n| Status | Count |\n| --- | --- |\n| Open | 0 |\n"
                     "| **Total** | **0** |\n\n## All\n\n"
                     "| ID | Title | Status | Severity | Created | Updated |\n"
                     "| --- | --- | --- | --- | --- | --- |\n")
            fx.write("sdlc-studio/bugs/BG0001-x.md",
                     "# BG0001: check_links misses a broken anchor link defect in nested lists"
                     "\n\n> **Status:** Open\n> **Severity:** High\n> **Points:** 2\n"
                     "> **Affects:** src/thing.py\n\n## Summary\n\nx\n")

            def file(*extra: str) -> subprocess.CompletedProcess:
                return fx.run("file_finding.py", "file", "--root", str(fx.root), "--type",
                              "bug", "--title", "a broken anchor link defect is not caught by "
                              "check_links", "--severity", "high", "--affects", "src/thing.py",
                              "--points", "3", "--summary", "s", "--steps", "r", "--fix", "f",
                              *extra)

            bugs = fx.root / "sdlc-studio" / "bugs"
            before = sorted(p.name for p in bugs.iterdir())
            refused = file()
            self.assertEqual(refused.returncode, 1, refused.stdout + refused.stderr)
            self.assertIn("--distinct-from BG0001", refused.stderr)
            self.assertEqual(sorted(p.name for p in bugs.iterdir()), before, "the refusal wrote")
            filed = file("--distinct-from", "BG0001")
            self.assertEqual(filed.returncode, 0, filed.stdout + filed.stderr)
            new = [p for p in bugs.glob("BG0002-*.md")]
            self.assertEqual(len(new), 1, filed.stdout)
            self.assertIn("> **Distinct-from:** BG0001", _read(new[0]))

        # help/reconcile.md: `risk-class` drift, raised and never lowered, against real runs.
        page = HELP / "reconcile.md"
        fixes = _flat(_section(_read(page), "### What It Fixes (mechanical bookkeeping)"))
        self.assertTrue(fixes, "help/reconcile.md has no What It Fixes section")
        for needle in ("`risk-class`", "`Risk-class`", "raises", "never lowers",
                       "](../reference-reconcile.md#risk-class)"):
            self.assertIn(needle, fixes, f"the What It Fixes table does not say {needle!r}")
        _links_resolve(self, fixes, page)
        with tempfile.TemporaryDirectory() as tmp:
            fx = v64._Fixture(Path(tmp))
            fx.write("sdlc-studio/.config.yaml", "risk:\n  components:\n    src/pay: high\n")
            story = "# {id}: s\n\n> **Status:** Ready\n> **Risk-class:** {cls}\n" \
                    "> **Affects:** {path}\n> **Points:** 2\n\n## Acceptance Criteria\n\nx\n"
            low = fx.write("sdlc-studio/stories/US0001-s.md",
                           story.format(id="US0001", cls="standard", path="src/pay/a.py"))
            high = fx.write("sdlc-studio/stories/US0002-s.md",
                            story.format(id="US0002", cls="high", path="src/web/b.py"))
            seen = fx.run("reconcile.py", "detect", "--root", str(fx.root), "--format", "json")
            self.assertEqual(seen.returncode, 1, "detect found no drift: " + seen.stderr)
            drift = [d for d in json.loads(seen.stdout)["drift"] if d["kind"] == "risk-class"]
            self.assertEqual(len(drift), 1, drift)
            self.assertEqual((drift[0]["id"], drift[0]["stamped"], drift[0]["mapped"]),
                             ("US0001", "standard", "high"))
            applied = fx.run("reconcile.py", "apply", "--root", str(fx.root))
            self.assertEqual(applied.returncode, 0, applied.stdout + applied.stderr)
            self.assertIn("> **Risk-class:** high", _read(low), "apply did not raise the stamp")
            self.assertIn("> **Risk-class:** high", _read(high), "apply lowered a stamp")

    def test_the_review_help_names_the_authors_replayed_mutants(self):
        """Mutant: help/review.md's self-check section as EP0379's grooming found it, showing
        only `--claims claims.json --mutants mutants.json`, with no runner, no kept list and no
        replay in the brief. AC2."""
        page = HELP / "review.md"
        check = _flat(_section(_read(page), "## Before a unit review: the author's self-check"))
        self.assertTrue(check, "help/review.md has no author self-check section")
        for needle in ("`mutation.py run --edits <list.json> --scope <id>`", "scratch copy",
                       "one verdict line each", "killed", "survived", "`not-applied`", "`error`",
                       "`critic.py self-check record`", "`--mutants-from <report>`",
                       "`sdlc-studio/reviews/author-mutants/<id>.json`", "`critic.py brief`",
                       "replays that list against the tree",
                       "verdict differs from its recorded one", "the author's",
                       "not the reviewer's own mutation pass",
                       "](../reference-review.md#author-self-check)"):
            self.assertIn(needle, check, f"the self-check section does not say {needle!r}")
        _links_resolve(self, check, page)

        with tempfile.TemporaryDirectory() as tmp:
            fx = v64._Fixture(Path(tmp))
            fx.write("src/widget.py", "def w():\n    return 1\n")
            test = fx.write("tests/test_widget.py",
                            "from src.widget import w\n\n\ndef test_w():\n    assert w() == 1\n")
            fx.write("src/__init__.py", "")
            fx.write("sdlc-studio/personas/seats/qa.md",
                     "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n\n## Lens\n\nx\n\n"
                     "## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")
            fx.write("sdlc-studio/stories/US0101-widget.md",
                     "# US0101: widget\n\n> **Status:** Review\n> **Points:** 2\n"
                     "> **Epic:** EP0001\n> **Affects:** src/widget.py, tests/test_widget.py, "
                     "changelog.d/US0101.md\n\n## Acceptance Criteria\n\n### AC1: works\n"
                     "- **Verify:** shell true\n")
            fx.write("changelog.d/US0101.md", "w returns 1\n")
            git = v64.gitutil.git
            git(["init", "-q", "-b", "main"], fx.root)
            git(["add", "-A"], fx.root)
            git(["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m",
                 "US0101: widget"], fx.root)
            edits = fx.write("edits.json", json.dumps([
                {"mutant": "w returns 2", "file": "src/widget.py", "old": "return 1",
                 "new": "return 2", "test": "tests/test_widget.py::test_w"},
                {"mutant": "absent text", "file": "src/widget.py", "old": "return 9",
                 "new": "return 8", "test": "tests/test_widget.py::test_w"}]))
            report = fx.root / "sdlc-studio" / ".local" / "lane" / "US0101-report.json"
            ran = subprocess.run([sys.executable, "-B", str(SCRIPTS / "mutation.py"), "run",
                                  "--edits", str(edits), "--scope", "US0101", "--report",
                                  str(report)], cwd=fx.root, capture_output=True, text=True,
                                 check=False, timeout=300, env=fx.env)
            lines = ran.stdout.splitlines()
            self.assertTrue(any(ln.startswith("w returns 2 killed:") for ln in lines),
                            ran.stdout + ran.stderr)
            self.assertTrue(any(ln.startswith("absent text not-applied:") for ln in lines),
                            ran.stdout)
            claims = fx.write("claims.json", json.dumps([
                {"surface": "commit message", "claim": "w returns 1", "ruling": "TRUE"},
                {"surface": "changelog.d/US0101.md", "claim": "w is new", "ruling": "TRUE"}]))

            def record() -> subprocess.CompletedProcess:
                return fx.run("critic.py", "self-check", "record", "--unit", "US0101",
                              "--author", "Ade (engineering)", "--claims", str(claims),
                              "--mutants-from", str(report), "--root", str(fx.root))

            listed = fx.root / "sdlc-studio" / "reviews" / "author-mutants" / "US0101.json"
            refused = record()
            self.assertNotEqual(refused.returncode, 0, "a row the runner did not apply was kept")
            self.assertIn("absent text", refused.stdout + refused.stderr)
            self.assertFalse(listed.exists(), "the refused record kept a mutant list")
            kept = json.loads(_read(report))
            kept["mutants"] = [m for m in kept["mutants"] if m["result"] == "killed"]
            report.write_text(json.dumps(kept), encoding="utf-8")
            recorded = record()
            self.assertEqual(recorded.returncode, 0, recorded.stdout + recorded.stderr)
            self.assertEqual(critic.author_mutants_path(fx.root, "US0101"), listed)
            self.assertTrue(listed.is_file(), "the record kept no mutant list")

            test.write_text("def test_w():\n    assert True\n", encoding="utf-8")
            brief = fx.run("critic.py", "brief", "--unit", "US0101", "--seat", "qa", "--root",
                           str(fx.root))
            self.assertEqual(brief.returncode, 0, brief.stderr)
            self.assertIn(critic.AUTHOR_MUTANTS_HEADING, brief.stdout)
            self.assertIn("not the reviewer's mutation pass", critic.AUTHOR_MUTANTS_HEADING)
            line = next((ln for ln in brief.stdout.splitlines() if "w returns 2" in ln), "")
            self.assertIn(critic.REPLAY_DISAGREES, line, brief.stdout)

    def test_the_public_pages_name_what_65_adds(self):
        """Mutant: README whose newest 'New in' line is 6.4's, llms.txt linking no
        docs/known-issues.md, and a Signer bullet in docs/engineering-leaders.md that names no
        delegation. AC3."""
        readme = _read(README)
        new = [b for b in re.split(r"\n(?=- )|\n\s*\n", readme) if b.startswith("- **New in 6.5")]
        self.assertEqual(len(new), 1, "README has no single 'New in 6.5' line")
        new = _flat(new[0])
        for needle in ("fewer than 50 open defects", "None is at Medium or above",
                       "](docs/known-issues.md)", "persona and seat card",
                       "written standard", "delegated signature",
                       "names the decision authorising it"):
            self.assertIn(needle, new, f"README's 6.5 line does not say {needle!r}")
        _links_resolve(self, new, README)
        lines = [ln for ln in readme.splitlines() if ln.startswith("- **New in ")]
        at = {v: next(i for i, ln in enumerate(lines) if ln.startswith(f"- **New in {v}"))
              for v in ("6.5", "6.4")}
        self.assertLess(at["6.5"], at["6.4"], "README's 6.5 line is not above its 6.4 line")

        llms = _read(LLMS)
        self.assertIn("](docs/known-issues.md)", llms, "llms.txt does not link the known issues")
        self.assertTrue((REPO / "docs" / "known-issues.md").is_file())

        signer = _flat(next((b for b in re.split(r"\n(?=- )|\n\s*\n", _read(LEADERS))
                             if b.startswith("- **Signer.**")), ""))
        self.assertTrue(signer, "engineering-leaders.md has no Signer bullet")
        for needle in ("under delegation", "only with `--delegated` and `--decision`",
                       "accepted decision",
                       "`sdlc-studio/decisions.md`", "Signed by", "Accountable",
                       "evidence pack", "the delegation and the decision"):
            self.assertIn(needle, signer, f"the Signer bullet does not say {needle!r}")
        _links_resolve(self, signer, LEADERS)

        # The statement against the code: the refusal without `--decision`, and what the
        # report's cell and the pack's line say for a delegated signature and for one entered.
        root = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(root, ignore_errors=True))
        bare = argparse.Namespace(delegated=True, decision=None)
        did, why = sprint._delegation(root, bare)
        self.assertIsNone(did)
        self.assertIn("--decision", why)
        self.assertIn("accepted decision in sdlc-studio/decisions.md", why)
        did, why = sprint._delegation(root, argparse.Namespace(delegated=False, decision="D0001"))
        self.assertIn("not marked --delegated", why)
        # Through `sprint.py sign` on a closed run: only `--delegated` with an accepted
        # `--decision` seals a delegated signature; an entered one needs neither.
        cases = (("entered", lambda a, s: [], True),
                 ("a decision with no --delegated", lambda a, s: ["--decision", a], False),
                 ("--delegated with no decision", lambda a, s: ["--delegated"], False),
                 ("--delegated with a superseded decision",
                  lambda a, s: ["--delegated", "--decision", s], False),
                 ("--delegated with the accepted decision",
                  lambda a, s: ["--delegated", "--decision", a], True))
        for label, argv_of, seals in cases:
            with self.subTest(label), tempfile.TemporaryDirectory() as tmp:
                fx = v64._Fixture(Path(tmp))
                sp._closed_run(fx.root)
                accepted, superseded = sp._decisions(fx.root)
                argv = argv_of(accepted, superseded)
                done = fx.run("sprint.py", "sign", "--report", "RPT0001", "--principal",
                              "Ada Lane", *argv, "--root", str(fx.root))
                signature = sp._read(fx.root).get("signature")
                if not seals:
                    self.assertNotEqual(done.returncode, 0, f"{argv} sealed a signature")
                    self.assertIsNone(signature, f"{argv} wrote a signature")
                    continue
                self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
                want = ("Ada Lane" if "--delegated" not in argv else
                        f"Ada Lane (entered under delegation, authorised by decision {accepted})")
                self.assertEqual(sprint_report.signed_by(signature), want)
        signed = {"principal": "Ada Lane", "signed_at": "2026-11-25T10:00:00Z",
                  "fingerprint": "abc", "delegated": True, "decision": "D0001"}
        self.assertEqual(sprint_report.signed_by(signed),
                         "Ada Lane (entered under delegation, authorised by decision D0001)")
        own = {k: v for k, v in signed.items() if k not in ("delegated", "decision")}
        self.assertEqual(sprint_report.signed_by(own), "Ada Lane")
        pack = "\n".join(evidence_pack._entry("US0001", "RPT0001", {}, None, [], [], signed))
        self.assertIn("- Accountable: Ada Lane, whose signature on its report was entered under "
                      "delegation, authorised by decision D0001", pack)
        pack = "\n".join(evidence_pack._entry("US0001", "RPT0001", {}, None, [], [], own))
        self.assertNotIn("delegation", pack)

    def test_existing_users_has_the_64_to_65_upgrade_path(self):
        """Mutant: the upgrade page whose newest section is still 'From 6.3 to 6.4'. AC4."""
        page = _read(UPGRADE)
        froms = re.findall(r"(?m)^### (From \S+ to \S+)\s*$", page)
        self.assertIn("From 6.4 to 6.5", froms, "the upgrade page has no 6.5 section")
        at = froms.index("From 6.4 to 6.5")
        self.assertEqual(froms[at:at + 2], ["From 6.4 to 6.5", "From 6.3 to 6.4"],
                         "the 6.5 section is not directly above the 6.4 one")
        six_five = _flat(_section(page, "### From 6.4 to 6.5"))
        for needle in ("PyYAML", f"`{gate.PYYAML_INSTALL}`", "Reinstall", "`migrate`",
                       "`migrate --apply`", "`sdlc-studio/.version`",
                       "`personas.standard: report`", "its own cards", "`require_ac_verification`",
                       "`persona_review.py check`", "`personas.standard: block`",
                       "holds no card", "optional", *DISTRO_PACKAGE):
            self.assertIn(needle, six_five, f"the 6.5 section does not say {needle!r}")
        self.assertNotIn(ONE_PACKAGE, six_five, "the page gives Debian's name for every system")
        self.assertLess(six_five.index("PyYAML"), six_five.index("Reinstall"),
                        "the 6.5 section does not put PyYAML before the reinstall")
        for key in NEW_KEYS:
            stated = _config_ref_default(key)
            self.assertTrue(stated, f"reference-config.md states no default for {key}")
            self.assertEqual(stated, _shipped_default(key).strip("`"),
                             f"reference-config.md and the shipped default disagree on {key}")
            shown = re.escape(f"`{key}`") + r" \(" + re.escape(
                stated if re.fullmatch(r"\d+", stated) else f"`{stated}`") + r"[,)]"
            self.assertRegex(six_five, shown, f"the 6.5 section does not give {key} its default "
                                              f"{stated}")
        if _bug_status("BG1613") == "Open":
            # No script reads the CI wait key while that bug is open: the page must say so.
            self.assertIn("which no shipped script reads yet", six_five)
            self.assertNotRegex(six_five, r"`ci\.wait_timeout_minutes`[^.]*\bbounds\b")
        _links_resolve(self, six_five, UPGRADE)

        with tempfile.TemporaryDirectory() as tmp:
            fx, config = _fixture_64(Path(tmp))
            owed = _owed(fx)
            # Until the cut stamps the skill 6.5.0 a 6.4.0 stamp is current; from then it is owed.
            stamp_owed = _skill_version() >= (6, 5, 0)
            self.assertEqual(any(".version" in d for d in owed), stamp_owed, owed)
            self.assertTrue(any("personas.standard: report" in d for d in owed), owed)
            self.assertTrue(any("require_ac_verification" in d for d in owed), owed)
            self.assertEqual(len(owed), 2 + stamp_owed, f"migrate owes a 6.4 project more: {owed}")
            done = fx.run("migrate.py", "--root", str(fx.root), "--apply")
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertNotIn("require_ac_verification", _read(config))
            self.assertRegex(_read(config), r"(?m)^  standard: report$")
            self.assertEqual('"6.4.0"' in _read(fx.root / "sdlc-studio" / ".version"),
                             not stamp_owed, "the version stamp was not restamped as owed")
            clean = fx.run("persona_review.py", "check", "--root", str(fx.root))
            self.assertEqual(clean.returncode, 0, clean.stdout + clean.stderr)
            fx.write(pb.QA, TOKEN_CARD)
            held = fx.run("persona_review.py", "check", "--root", str(fx.root))
            self.assertEqual(held.returncode, 1, "check named no card the standard holds")
            self.assertIn("seat-demographic-fluff", held.stdout + held.stderr)
        with tempfile.TemporaryDirectory() as tmp:
            fx, config = _fixture_64(Path(tmp), cards=False, retired=False)
            owed = _owed(fx)
            self.assertFalse(any("personas.standard" in d for d in owed),
                             f"migrate set the standard for a project with no cards: {owed}")
            self.assertFalse(any("require_ac_verification" in d for d in owed), owed)

    def test_the_sprint_help_names_the_spend_ceiling_and_effort_by_kind(self):
        """Mutant: help/sprint.md whose Appetite section names no spend key, warning or stop,
        and whose Reasoning effort paragraph stamps both roles on every unit. AC1."""
        page = _read(HELP / "sprint.md")
        appetite = _flat(_section(page, "### Appetite: the circuit breaker"))
        for needle in ("`--appetite-spend`", "`appetite.spend`", "`capacity.spend`",
                       "priced input-equivalent tokens", "both ship at 0, no spend ceiling",
                       "75 and 95 per cent", f"exits {loop_guard.BUDGET_EXIT}",
                       "units already dispatched finish and no further unit starts",
                       "leaves spend unjudged at that boundary and says so",
                       "`spend: NOT JUDGED at this boundary`",
                       "minutes and units still stop the run", "appetite resize --spend",
                       "`--decision` must name a row of `sdlc-studio/decisions.md`"):
            self.assertIn(needle, appetite, f"the Appetite section does not say {needle!r}")
        self.assertEqual(loop_guard.SPEND_WARNINGS, (95, 75))
        effort = _block(page, "**Reasoning effort:**")
        for needle in ("The `docs`, `bug` and `code` entries under `routing.effort`",
                       "they ship empty", "a bug by its id, else code when an Affects path is "
                       "a code file, else docs", "refuses an unknown kind, role or effort, "
                       "naming the key", "within a kind", "`sprint lane brief` names the "
                       "unit's own effort", "`routing.effort.reviewer_below_builder`"):
            self.assertIn(needle, effort, f"the effort paragraph does not say {needle!r}")
        self.assertNotIn("stamps both on every unit", effort)

        # The stop and the unread meter, through `loop_guard.py budget` on its own fixture.
        fx = _helper(lgs.LoopGuardSpendTests)
        self.addCleanup(fx.doCleanups)
        fx._open({"minutes": 0, "units": 0, "spend": 7000})
        fx._use(1000, output=1000, cache_read=10000)  # 1,000 + 5,000 + 1,000 priced
        rc, text = fx._budget(fmt="text")
        self.assertEqual(rc, loop_guard.BUDGET_EXIT, text)
        self.assertIn("units already dispatched finish and no further unit starts", text)
        unread = _helper(lgs.LoopGuardSpendTests)
        self.addCleanup(unread.doCleanups)
        unread._open({"minutes": 60, "units": 0, "spend": 1000}, opening=None)
        rc, text = unread._budget(fmt="text")
        self.assertEqual((rc, True), (0, "spend: NOT JUDGED at this boundary" in text), text)
        lgs.run_state.update(str(unread.root), started_at="2026-01-01T00:00:00Z")
        rc, text = unread._budget(fmt="text")
        self.assertEqual(rc, loop_guard.BUDGET_EXIT, text)
        self.assertIn("reason=minutes", text)
        self.assertIn("spend: NOT JUDGED at this boundary", text)

        # The kinds and the refusals, through `sprint plan` and `sprint lane brief`.
        for entry, key in (("doc: {builder: low}", r"routing\.effort\.doc\b(?!\.)"),
                           ("docs: {author: low}", r"routing\.effort\.docs\.author\b"),
                           ("docs: {builder: fast}", r"routing\.effort\.docs\.builder\b")):
            with self.subTest(entry=entry), tempfile.TemporaryDirectory() as d:
                rc, out, err = ebk._plan(ebk._project(d, f"routing:\n  effort:\n    {entry}\n"))
                self.assertEqual(rc, 2, f"{entry} planned:\n{out}{err}")
                self.assertRegex(err, key)
        with tempfile.TemporaryDirectory() as d:
            root = ebk._project(d, ebk.AC1)
            rc, out, err = ebk._plan(root, "--bugs", "Open")
            self.assertEqual(rc, 0, err)
            kinds = {uid: (e or {}).get("kind") for uid, e in ebk._efforts(out).items()}
            self.assertEqual(kinds, {ebk.DOCS: "docs", ebk.CODE: "code", ebk.BUG: "bug"})
            ebk.run_state.open_run(root, batch=[ebk.DOCS], goal="g")
            line = ebk._brief_line(root, ebk.DOCS)
            self.assertIn("the docs kind", line)
            self.assertRegex(line, r"builder at low effort\b")
        self.assertEqual(_shipped_default("routing.effort.docs"), "{}")

    def test_the_help_names_the_cache_measures_and_the_retro_they_demand(self):
        """Mutant: help/sprint.md naming no cache-write split, and help/retro.md's validate row
        naming no `## Cost` demand. AC2."""
        anatomy = _block(_read(HELP / "sprint.md"), "`cost --anatomy` reads")
        for needle in ("splits each role's cache writes into growth and re-writes after "
                       "5-minute and 1-hour expiry", "a write's lifetime from its kind",
                       "a role with an untimed usage record reads not available for its split"):
            self.assertIn(needle, anatomy, f"the anatomy paragraph does not say {needle!r}")
        self.assertEqual(cost_anatomy.CACHE_LIFETIMES, {"cache_write_5m": (300, "rewrite_5m"),
                                                        "cache_write_1h": (3_600, "rewrite_1h")})
        self.assertEqual((cost_anatomy.GROWTH, cost_anatomy.NOT_AVAILABLE),
                         ("growth", "not available"))
        row = next((ln for ln in _read(HELP / "retro.md").splitlines()
                    if ln.startswith("| `/sdlc-studio retro validate`")), "")
        for needle in (f"`## {retro.COST_SECTION}`", f"`{retro.COST_ISSUE}` one",
                       f"`{retro.CACHE_READ_ISSUE}` one", "names the cause",
                       f"more than {NUMBER_WORDS[retro.CACHE_READ_FALL_POINTS]} points below",
                       f"up to the last {NUMBER_WORDS[sprint_report.CACHE_TREND_RUNS]} signed "
                       "runs", "names each such role", "A rolling boundary stops on a fall its "
                       "retro does not name", "](../reference-sprint.md#cost-regression)"):
            self.assertIn(needle, row, f"the validate row does not say {needle!r}")
        _links_resolve(self, row, HELP / "retro.md")
        # The refusal, through `retro.py validate` on the cache-read fall's own fixture.
        fx = _helper(crf.CacheReadFallTests)
        self.addCleanup(fx.doCleanups)
        root = fx.issue_tree()
        fx.write_retro(root, crf.THREE_LINE)
        rc, out = fx.validate(root)
        self.assertNotEqual(rc, 0, out)
        self.assertIn("missing cache-read cause", out)
        fx.write_retro(root, crf.THREE_LINE + "\n## Cost\n\n- the builder's prompt changed\n")
        rc, out = fx.validate(root)
        self.assertEqual(rc, 0, out)

    def test_the_help_names_the_release_record_failure_rate_and_disclosure(self):
        """Mutant: help/gate.md naming no release record, help/retro.md's scorecard naming no
        `escape.py failure-rate` figure, and the `sign` paragraph silent on what a refused or
        repeated disclosure writes. AC3."""
        gate_page = _flat(_section(_read(HELP / "gate.md"),
                                   "## `--release`: the one command before a tag"))
        for needle in ("`release_cut.py changelog-cut --version X.Y.Z`",
                       "one committed release record per version", f"`{release_cut.RELEASES_REL}`",
                       "the date of the cut", "the signed reports since the previous release",
                       "A second cut of the same version leaves the record unchanged"):
            self.assertIn(needle, gate_page, f"help/gate.md does not say {needle!r}")
        self.assertIn(("changelog-cut",), _verbs(release_cut.build_parser()))
        root = rr._project(self)
        rr._sign(root, "RPT0001", "2026-11-20T10:00:00Z")
        changelog = _read(root / "CHANGELOG.md")
        done = rr._cli(root, "changelog-cut", "--version", "1.0.0")
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        [record] = rr._lines(root)
        self.assertEqual((record["version"], record["reports"]), ("1.0.0", ["RPT0001"]))
        self.assertRegex(record["date"], r"^\d{4}-\d{2}-\d{2}$")
        cut = (root / release_cut.RELEASES_REL).read_bytes()
        again = rr._cli(root, "changelog-cut", "--version", "1.0.0")
        self.assertNotEqual(again.returncode, 0, "a second cut of 1.0.0 was not refused")
        self.assertEqual(cut, (root / release_cut.RELEASES_REL).read_bytes())
        (root / "CHANGELOG.md").write_text(changelog, encoding="utf-8")  # an interrupted cut
        rerun = rr._cli(root, "changelog-cut", "--version", "1.0.0")
        self.assertEqual(rerun.returncode, 0, rerun.stdout + rerun.stderr)
        self.assertEqual(cut, (root / release_cut.RELEASES_REL).read_bytes())

        seats = _section(_read(HELP / "retro.md"), "## Each seat's own record")
        for needle in ("the figure `escape.py failure-rate` prints for the same window",
                       "A release inside the settling period is pending", "never 0%",
                       "](deploy.md#commands)"):
            self.assertIn(needle, _flat(seats), f"help/retro.md's scorecard does not say "
                                                f"{needle!r}")
        _links_resolve(self, seats, HELP / "retro.md")
        self.assertIn(("failure-rate",), _verbs(escape.build_parser()))
        with tempfile.TemporaryDirectory() as tmp:
            rate = escape.failure_rate(tmp, "2026-01-01", "2026-03-31")
        self.assertIsNone(rate.get("rate"), rate)
        self.assertTrue(rate.get("not_measured"), rate)

        sign = _block(_read(HELP / "sprint.md"), "**`sign --report RPTxxxx")
        for needle in ("`sprint_report.py disclose --report RPTxxxx --decision Dnnnn`",
                       "the fingerprint", "still reads VALID", "An unsigned report, a decision "
                       "it does not hold as accepted", "are refused, writing nothing",
                       "one line however often it runs"):
            self.assertIn(needle, sign, f"the sign paragraph does not say {needle!r}")
        self.assertIn(("disclose",), _verbs(sprint_report.build_parser()))
        for label, opts, decision in (("unsigned", {"sign": False}, "D0001"),
                                      ("a decision the log does not hold", {}, "D0002"),
                                      ("the accepted decision", {}, "D0001")):
            with self.subTest(label), tempfile.TemporaryDirectory() as tmp:
                [rid] = dd._project(Path(tmp), (dd.RUN_A, opts), rulings=dd.ACCEPTED)
                before = dd._bytes(Path(tmp), rid)
                first = dd._disclose(Path(tmp), rid, decision)
                if label != "the accepted decision":
                    self.assertNotEqual(first.returncode, 0, first.stdout)
                    self.assertEqual(before, dd._bytes(Path(tmp), rid), "a refusal wrote")
                    continue
                self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
                once = dd._bytes(Path(tmp), rid)
                self.assertEqual(dd._disclose(Path(tmp), rid, decision).returncode, 0)
                self.assertEqual(once, dd._bytes(Path(tmp), rid), "a repeat rewrote the report")
                twin = dd._files(Path(tmp), rid)["twin"].read_text(encoding="utf-8")
                self.assertEqual(twin.count("entered under delegation"), 1)
                check = dd._cli(Path(tmp), "check", "--report", rid)
                self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
                self.assertIn("VALID", check.stdout)

    def test_the_public_pages_name_what_the_widened_65_adds(self):
        """Mutant: README's 6.5 line naming no spend, the upgrade page naming none of the five
        keys, the leaders page capping a run by minutes and units alone with no owner and no
        change failure rate, and the enterprise page bounding a run without spend. AC4."""
        readme = _read(README)
        line = _flat(next(b for b in re.split(r"\n(?=- )|\n\s*\n", readme)
                          if b.startswith("- **New in 6.5")))
        self.assertIn("A run can also stop on spend", line)
        self.assertLessEqual(rfd.words(readme), rfd.CR0742_WORDS)

        raw = _section(_read(UPGRADE), "### From 6.4 to 6.5")
        for key in SPEND_EFFORT_KEYS:
            stated = _stated_default(key)
            self.assertEqual(stated, _shipped_default(key).strip("`"), key)
            if key.startswith("routing.effort."):
                self.assertEqual(stated, "{}", f"{key} read a row other than the per-kind one")
            shown = re.escape(f"`{key}`") + r" \(" + re.escape(
                stated if re.fullmatch(r"\d+", stated) else f"`{stated}`") + r"[,)]"
            self.assertRegex(_flat(raw), shown, f"the 6.5 section does not give {key} {stated}")
        fall = _block(raw, "6. **Name each cache-read fall in the retro.**")
        for needle in ("`retro validate` refuses the retro", "`## Cost`", "each such role"):
            self.assertIn(needle, fall, f"the cache-read item does not say {needle!r}")

        page = _read(LEADERS)
        cost = elp.section_body(page, "cost in dollars a point")
        for body, needles in (
                (cost, ("There is no dollar budget setting.", "`capacity.spend` or "
                        "`appetite.spend`, in priced input-equivalent tokens, both 0 and "
                        "unbounded by default", "a lower bound, so a stop can come late but "
                        "never early", "](../.claude/skills/sdlc-studio/scripts/loop_guard.py)")),
                (elp.section_body(page, "separation of duties"), (
                    "The person owns the PRD and the PVD.", "under authority the person "
                    "delegates: it corrects a fact itself, proposes any change to a requirement "
                    "as a change request the person decides, and asks when unsure",
                    f"reference-workflow-personas.md#{SEATS_ANCHOR})")),
                (elp.section_body(page, "change approval"), (
                    "`escape.py failure-rate` states the release change failure rate",
                    "release records", "never 0%",
                    "](../.claude/skills/sdlc-studio/scripts/escape.py)"))):
            for needle in needles:
                self.assertIn(needle, _flat(body), f"engineering-leaders.md does not say "
                                                   f"{needle!r}")
            self.assertEqual(elp.claim_problems(body), [])
        self.assertNotIn("capped by wall-clock minutes and a number of units.", _flat(cost))
        self.assertIn(SEATS_ANCHOR, elp.anchors(SEATS_REF))
        self.assertIn("LOWER BOUND", loop_guard.__doc__)
        self.assertIn("late but never early", loop_guard.__doc__)
        self.assertLessEqual(elp.word_count(page), elp.WORD_LIMIT)
        approved = elp.SIGNER_SENTENCES[elp.PAGE]
        self.assertEqual(elp.signer_sentence_problems(page, approved), [])
        self.assertTrue(elp.signer_sentence_problems(page + "\n\nAn agent signs for you.\n",
                                                     approved), "the closed world is open")

        text = _read(ENTERPRISE)
        for body, needles in (
                (_section(text, "## Cost"), ("`capacity.minutes`, `capacity.units` and "
                                             "`capacity.spend`", "`appetite.spend`",
                                             "`--appetite-units` and `--appetite-spend`")),
                (_section(text, "## Harness and models"), (
                    "`routing.effort.docs`, `routing.effort.bug` and `routing.effort.code` set "
                    "it per kind of unit",))):
            for needle in needles:
                self.assertIn(needle, _flat(body), f"enterprise.md does not say {needle!r}")
            self.assertEqual(ent.command_problems(body), [])

    def test_the_upgrade_page_says_how_to_turn_on_the_solution_review(self):
        """Mutant: the upgrade page naming no solution review and no `solution_review` key.
        AC5."""
        self.assertTrue(set(SOLUTION_KEYS) <= set(NEW_KEYS), "NEW_KEYS lacks the two keys")
        raw = _section(_read(UPGRADE), "### From 6.4 to 6.5")
        for key in SOLUTION_KEYS:
            stated = _stated_default(key)
            self.assertEqual(stated, _shipped_default(key).strip("`"), key)
            shown = re.escape(f"`{key}`") + r" \(" + re.escape(
                stated if re.fullmatch(r"\d+", stated) else f"`{stated}`") + r"[,)]"
            self.assertRegex(_flat(raw), shown, f"the 6.5 section does not give {key} {stated}")
        start = raw.find("7. **Turn on the solution review when you want it.**")
        self.assertNotEqual(start, -1, "the 6.5 section has no solution review item")
        item = _flat(re.split(r"\n(?=\d+\. )", raw[start:])[0])  # its fence and paragraphs
        for needle in ("It is off at the shipped defaults", "this repository's own values rather "
                       "than a recommended default", "`risk.components`", "`sprint lane land` refuses "
                       "a unit the settings name until a seat's GO stands on its approach note",
                       "`critic.py approach brief`", "`critic.py approach record`", LANES_LINK):
            self.assertIn(needle, item, f"the solution review item does not say {needle!r}")
        self.assertNotRegex(item, r"\b(?:US|BG|CR|RFC|EP|D)\d{4}\b", "the item names an id")
        _links_resolve(self, item, UPGRADE)
        self.assertEqual(risk_class.CONFIG_KEY, "risk.components")
        verbs = _verbs(critic.build_parser())
        self.assertTrue({("approach", "brief"), ("approach", "record")} <= verbs, verbs)
        fence = re.search(r"```yaml\n(.*?)\n\s*```", raw, re.S)
        self.assertTrue(fence, "the 6.5 section gives no YAML lines to turn the review on")
        lines = textwrap.dedent(fence.group(1)) + "\n"
        self.assertIn("solution_review", yaml.safe_load(lines).get("review", {}))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write(root, "sdlc-studio/stories/US0001-a-story.md",
                   "# US0001: a story\n\n> **Status:** Ready\n> **Points:** 3\n")
            self.assertIsNone(critic.solution_review_reason(root, "US0001"),
                              "the shipped defaults name a 3-point story")
            _write(root, "sdlc-studio/.config.yaml", lines)
            reason = critic.solution_review_reason(root, "US0001")
            self.assertTrue(reason, "the page's lines leave a 3-point story without the review")
            self.assertIn("3 points", reason)


if __name__ == "__main__":
    unittest.main()
