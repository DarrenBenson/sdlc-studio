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
import critic  # noqa: E402
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
NEW_KEYS = ("personas.standard", "ci.wait_timeout_minutes", "ci.rerun_limit",
            "review.rendered_paths")

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


if __name__ == "__main__":
    unittest.main()
