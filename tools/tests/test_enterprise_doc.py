"""docs/enterprise.md: the page an enterprise reviewer reads to decide whether SDLC Studio fits.

It has six sections (harness and models, data, adopting without forking, fitting existing
controls, cost, and verification for less experienced engineers) and links the engineering
leaders page, which links it back. Its data section names every file in the installers and the
installed skill that makes a network call, scanned from the tree here, so a file with a call
added later, or a new kind of call in a named file, fails without a page update. Its controls map names real evidence for each gate and claims no
certification, and its cost section names commands that parse and dollar figures that a signed
report's committed JSON carries. Each check runs on the live page and on a planted failure
beside it, so a check that has stopped looking cannot pass.
"""
# test-census-subject: docs/enterprise.md
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PAGE = REPO / "docs" / "enterprise.md"
LEADERS = REPO / "docs" / "engineering-leaders.md"
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
SCRIPTS = SKILL / "scripts"
REPORTS = REPO / "sdlc-studio" / "reports"
CONFIG_REF = SKILL / "reference-config.md"

#: Each required section, found by its level-two heading.
SECTIONS = {
    "harness and models": re.compile(r"\bharness\b.*\bmodels\b", re.I),
    "data": re.compile(r"\bdata\b", re.I),
    "adopting without forking": re.compile(r"\bwithout forking\b", re.I),
    "fitting existing controls": re.compile(r"\bexisting controls\b", re.I),
    "cost": re.compile(r"^cost\b", re.I),
    "verification for less experienced engineers":
        re.compile(r"\bless experienced engineers\b", re.I),
}
#: The control gates the controls map must give evidence for.
GATES = ("requirements approved", "design reviewed", "tests evidenced", "independent review",
         "approval before release")
#: Commands the cost section must name, so a reformatted page cannot pass by naming none.
COST_COMMANDS = ("sprint plan", "sprint report", "sprint cost")

_H2 = re.compile(r"^##\s+(.*?)\s*$")
_HEADING = re.compile(r"^#{1,6}\s+(.*?)\s*$")
_EXPLICIT_ID = re.compile(r"\{#([\w-]+)\}")
_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
_CODE = re.compile(r"`([^`]+)`")
_ITEM = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
_DOLLARS = re.compile(r"\$\d[\d,]*(?:\.\d+)?")
_REPORT_ID = re.compile(r"\bRPT\d{4}\b")
_CONFIG_KEY = re.compile(r"^[a-z_]+(?:\.[a-z_0-9]+)+$")
_FILE_SUFFIXES = (".md", ".py", ".json", ".yaml", ".yml", ".sh", ".ps1", ".jsonl", ".txt")
#: A word that, used as a claim, asserts certification or compliance.
_CERT_WORD = re.compile(r"\b(?:certif\w*|complian\w*|accredit\w*|conform\w*|SOC\s*2|"
                        r"ISO(?:/IEC)?\s*\d{4,5}|HIPAA|FedRAMP|PCI[\s-]DSS|GDPR|"
                        r"Sarbanes\w*)\b", re.I)
_NEGATION = re.compile(r"\b(?:no|not|never|nor|neither|none|without)\b|n't\b", re.I)
_SENTENCE = re.compile(r"(?<=[.!?])\s+")

#: Network calls in Python, each a kind: an HTTP library, a `gh` subprocess, a git remote verb.
_PY_HTTP = re.compile(r"urllib\.request|urlopen\(|http\.client|^\s*import\s+socket\b|"
                      r"\bsocket\.(?:socket|create_connection)\(|"
                      r"^\s*(?:import|from)\s+(?:requests|httpx|aiohttp|urllib3)\b|"
                      r"[\"'(\[]\s*(?:curl|wget)[\s\"']", re.M)
_PY_GH = re.compile(r"[\[(]\s*[\"']gh[\"']\s*[,\])]")
_PY_GIT = re.compile(r"(?:\b_?git\s*\(|[\"']git[\"']\s*,)[^\n]*"
                     r"[\"'](fetch|clone|push|pull|ls-remote)[\"']")
#: The same in a shell or PowerShell line that is not a comment.
_SH_HTTP = re.compile(r"\b(?:curl|wget)\s+-|Invoke-WebRequest|Invoke-RestMethod|Net\.WebClient")
_SH_GH = re.compile(r"\bgh\s+(?:api|issue|pr|repo|release|run|workflow|auth)\b")
_SH_GIT = re.compile(r"\bgit\s+(fetch|clone|push|pull|ls-remote)\b")
#: What a data-section row must say for each kind of call it covers.
_MARKERS = {"http": re.compile(r"https?://"), "gh": re.compile(r"`gh\b")}


def sections(text: str) -> list[tuple[str, str]]:
    """Each level-two section as (heading, body), in page order."""
    out: list[tuple[str, list[str]]] = []
    for line in text.splitlines():
        m = _H2.match(line)
        if m:
            out.append((m.group(1), []))
        elif line.startswith("# "):
            out.append(("", []))
        elif out:
            out[-1][1].append(line)
    return [(h, "\n".join(body)) for h, body in out if h]


def section_body(text: str, key: str) -> str:
    """The body of the one section whose heading matches `key`, or empty."""
    return "\n".join(b for h, b in sections(text) if SECTIONS[key].search(h))


def claims(body: str) -> list[str]:
    """Each paragraph, list item and table row of a section body; headings are not claims."""
    out: list[str] = []
    for block in re.split(r"\n\s*\n", body):
        lines = [ln for ln in block.splitlines() if ln.strip() and not _HEADING.match(ln)]
        current: list[str] = []
        for line in lines:
            if (_ITEM.match(line) or line.lstrip().startswith("|")) and current:
                out.append(" ".join(current))
                current = []
            current.append(line.strip())
        if current:
            out.append(" ".join(current))
    return out


def table_rows(body: str) -> list[list[str]]:
    """The cells of each table row in `body`, header and separator rows left out."""
    rows = []
    for line in body.splitlines():
        s = line.strip()
        if not s.startswith("|") or re.fullmatch(r"\|[\s:|-]+\|?", s):
            continue
        rows.append([c.strip() for c in s.strip("|").split("|")])
    return rows[1:] if rows else []


def anchors(path: Path) -> set[str]:
    """The anchors a markdown file's headings render: explicit ids and GitHub slugs."""
    seen: dict[str, int] = {}
    out: set[str] = set()
    fenced = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        m = None if fenced else _HEADING.match(line)
        if not m:
            continue
        out.update(_EXPLICIT_ID.findall(m.group(1)))
        base = re.sub(r"\s+", "-", re.sub(r"[^\w\s-]", "",
                                          _EXPLICIT_ID.sub("", m.group(1)).strip().lower()))
        n = seen.get(base, 0)
        seen[base] = n + 1
        out.add(base if n == 0 else f"{base}-{n}")
    return out


def link_problem(target: str, page: Path = PAGE) -> str:
    """Why a link `target` written on `page` resolves to no file or heading, or empty."""
    if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
        return f"{target} is not a file in this repository"
    path_part, _, anchor = target.partition("#")
    resolved = (page.parent / path_part).resolve() if path_part else page.resolve()
    if REPO.resolve() not in resolved.parents:
        return f"{target} resolves outside the repository"
    if not resolved.exists():
        return f"{target} names no file"
    if anchor and (not resolved.is_file() or anchor not in anchors(resolved)):
        return f"{target} names no heading in {resolved.name}"
    return ""


def links_to(text: str, name: str) -> bool:
    """Whether `text` holds a markdown link to the docs page `name`, an anchor allowed."""
    return any(t.partition("#")[0].removeprefix("./") == name for t in _LINK.findall(text))


def structure_problems(page_text: str, leaders_text: str) -> list[str]:
    """Each required section missing or repeated, and each missing link between the pages."""
    problems = []
    headings = [h for h, _ in sections(page_text)]
    for key, rx in SECTIONS.items():
        hits = [h for h in headings if rx.search(h)]
        if len(hits) != 1:
            problems.append(f"section {key!r}: {len(hits)} headings match, want 1")
    if not links_to(page_text, "engineering-leaders.md"):
        problems.append("docs/enterprise.md does not link engineering-leaders.md")
    if not links_to(leaders_text, "enterprise.md"):
        problems.append("docs/engineering-leaders.md does not link enterprise.md")
    return problems


def scanned_files(root: Path) -> list[Path]:
    """The installers and every executable file of the installed skill, its tests left out."""
    files = [p for p in (root / "install.sh", root / "install.ps1") if p.is_file()]
    skill = root / ".claude" / "skills" / "sdlc-studio"
    for p in sorted(skill.rglob("*")) if skill.is_dir() else []:
        parts = p.relative_to(skill).parts
        if (p.is_file() and p.suffix in (".py", ".sh", ".ps1", ".js", ".mjs")
                and "tests" not in parts and "__pycache__" not in parts):
            files.append(p)
    return files


def scan(root: Path = REPO) -> dict[str, set[str]]:
    """Each scanned file that makes a network call, repo-relative, to the kinds it makes:
    `http`, `gh`, or `git <verb>` for a git remote operation."""
    found: dict[str, set[str]] = {}
    for path in scanned_files(root):
        text = path.read_text(encoding="utf-8", errors="replace")
        kinds: set[str] = set()
        if path.suffix == ".py":
            if _PY_HTTP.search(text):
                kinds.add("http")
            if _PY_GH.search(text):
                kinds.add("gh")
            kinds.update(f"git {v}" for v in _PY_GIT.findall(text))
        else:
            code = "\n".join(ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
            if _SH_HTTP.search(code) or path.suffix == ".js" and "fetch(" in code:
                kinds.add("http")
            if _SH_GH.search(code):
                kinds.add("gh")
            kinds.update(f"git {v}" for v in _SH_GIT.findall(code))
        if kinds:
            found[path.relative_to(root).as_posix()] = kinds
    return found


def unnamed(found: dict[str, set[str]], body: str) -> list[str]:
    """Each scanned file the data section's table does not name, or names without saying what
    each kind of call it makes contacts."""
    rows = table_rows(body)
    problems = []
    for rel, kinds in sorted(found.items()):
        base = rel.rsplit("/", 1)[-1]
        row = next((r for r in rows if r and any(
            c.rsplit("/", 1)[-1] == base and rel.endswith(c) for c in _CODE.findall(r[0]))), None)
        if row is None:
            problems.append(f"{rel}: makes a network call the data section does not name")
            continue
        said = " | ".join(row[1:])
        for kind in sorted(kinds):
            marker = _MARKERS.get(kind) or re.compile(re.escape(kind))
            if not marker.search(said):
                problems.append(f"{rel}: its {kind} call is not said in its row")
    return problems


def controls_problems(body: str, page: Path = PAGE) -> list[str]:
    """Each gate with no row or no evidence link, and each link or path that does not exist."""
    problems = []
    rows = table_rows(body)
    for gate in GATES:
        row = next((r for r in rows if r and r[0].strip("* ").lower().startswith(gate)), None)
        if row is None:
            problems.append(f"gate {gate!r} has no row")
        elif not _LINK.findall(" ".join(row[1:])):
            problems.append(f"gate {gate!r} names no evidence")
    for target in _LINK.findall(body):
        if problem := link_problem(target, page):
            problems.append(problem)
    for span in _CODE.findall(body):
        if " " in span or "<" in span or span.startswith("-"):
            continue
        if "/" in span:
            if not (REPO / span).exists():
                problems.append(f"`{span}` names no path")
        elif span.endswith(".py") and not (SCRIPTS / span).is_file():
            problems.append(f"`{span}` names no script")
    return problems


def certification_claims(text: str) -> list[str]:
    """Each sentence that uses a certification or compliance word with no negation."""
    out = []
    for claim in claims(text):
        for sentence in _SENTENCE.split(claim):
            if _CERT_WORD.search(sentence) and not _NEGATION.search(sentence):
                out.append(sentence[:90])
    return out


def commands(body: str) -> list[list[str]]:
    """Each command a code span names: `sprint <verb>...` or `<script>.py <verb>...`, as the
    script and the words before its first option or placeholder."""
    out = []
    for span in _CODE.findall(body):
        words = span.split()
        if not words or not (words[0] == "sprint" or words[0].endswith(".py")):
            continue
        script = "sprint.py" if words[0] == "sprint" else words[0].rsplit("/", 1)[-1]
        sub = []
        for w in words[1:]:
            if w.startswith(("-", "<")):
                break
            sub.append(w)
        if [script, *sub] not in out:
            out.append([script, *sub])
    return out


def _isolated_env(home: str) -> dict:
    env = dict(os.environ)
    for var in ("HOME", "XDG_CONFIG_HOME", "XDG_DATA_HOME", "COPILOT_HOME", "CODEX_HOME",
                "CLAUDE_CONFIG_DIR"):
        env[var] = home
    env["OPENCODE_DB"] = str(Path(home) / "opencode.db")
    return env


def command_problems(body: str) -> list[str]:
    """Each named command whose `--help` does not parse, and each config key the config
    reference does not document."""
    problems = []
    with tempfile.TemporaryDirectory() as home:
        for script, *sub in commands(body):
            path = SCRIPTS / script
            if not path.is_file():
                problems.append(f"{script} is not a skill script")
                continue
            proc = subprocess.run([sys.executable, str(path), *sub, "--help"], cwd=home,
                                  env=_isolated_env(home), capture_output=True, text=True,
                                  timeout=120)
            if proc.returncode != 0:
                problems.append(f"{' '.join([script, *sub])} --help exits {proc.returncode}")
    reference = CONFIG_REF.read_text(encoding="utf-8")
    for span in _CODE.findall(body):
        if _CONFIG_KEY.match(span) and not span.endswith(_FILE_SUFFIXES) \
                and f"`{span}`" not in reference:
            problems.append(f"`{span}` is not a key the config reference documents")
    return problems


#: The report rows a cost figure is looked up in, and the cell of each row that only explains it.
HEADLINE = ("Dollar cost", "Dollars per point")
_BASIS = "est_basis"


def _headline(node) -> list[dict]:
    """Each estimate row of a report JSON whose measure is a headline cost row."""
    if isinstance(node, list):
        return [r for v in node for r in _headline(v)]
    if not isinstance(node, dict):
        return []
    measure = node.get("est_measure")
    if isinstance(measure, dict) and measure.get("value") in HEADLINE:
        return [node]
    return [r for v in node.values() for r in _headline(v)]


def _strings(node) -> list[str]:
    if isinstance(node, dict):
        return [s for v in node.values() for s in _strings(v)]
    if isinstance(node, list):
        return [s for v in node for s in _strings(v)]
    return [node] if isinstance(node, str) else []


def signed_report(report_id: str, reports: Path = REPORTS) -> tuple[list[str], str]:
    """(the values of the report JSON's Dollar cost and Dollars per point rows, why it cannot be
    cited) for a report id. A unit's or a model's dollars are not a headline figure."""
    path = reports / f"{report_id}.json"
    if not path.is_file():
        return [], f"{report_id} has no committed JSON"
    doc = json.loads(path.read_text(encoding="utf-8"))
    sig = doc.get("signature")
    if not (isinstance(sig, dict) and sig.get("report") == report_id
            and sig.get("fingerprint") and sig.get("signed_at")):
        return [], f"{report_id} is not signed"
    return [s for row in _headline(doc) for k, v in row.items() if k != _BASIS
            for s in _strings(v)], ""


def figure_problems(body: str, reports: Path = REPORTS) -> list[str]:
    """Each dollar figure whose claim names no signed report whose JSON carries it."""
    problems = []
    for claim in claims(body):
        figures = _DOLLARS.findall(claim)
        if not figures:
            continue
        values: list[str] = []
        ids = sorted(set(_REPORT_ID.findall(claim)))
        for report_id in ids:
            strings, why = signed_report(report_id, reports)
            if why:
                problems.append(why)
            values.extend(strings)
        for figure in figures:
            if not ids:
                problems.append(f"{figure} names no report")
                continue
            rx = re.compile(rf"{re.escape(figure)}(?!\d)")
            if not any(rx.search(v) for v in values):
                problems.append(f"{figure} is carried by no signed report its claim names")
    return problems


class EnterpriseDocTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = PAGE.read_text(encoding="utf-8")
        cls.leaders = LEADERS.read_text(encoding="utf-8")

    def test_the_page_has_the_six_sections_and_links_the_leaders_page(self) -> None:
        """US1317 AC1. MUTANTS: a section heading dropped; a heading repeated; the link to the
        leaders page dropped; the link back from it dropped."""
        self.assertEqual(structure_problems(self.text, self.leaders), [])
        for key, rx in SECTIONS.items():
            heading = next(h for h, _ in sections(self.text) if rx.search(h))
            dropped = self.text.replace(f"## {heading}\n", "")
            self.assertIn(f"section {key!r}: 0 headings match, want 1",
                          structure_problems(dropped, self.leaders), key)
            doubled = f"{self.text}\n## {heading}\n\nAgain.\n"
            self.assertIn(f"section {key!r}: 2 headings match, want 1",
                          structure_problems(doubled, self.leaders), key)
        unlinked = re.sub(r"\]\((?:\./)?engineering-leaders\.md[^)]*\)", "]", self.text)
        self.assertIn("docs/enterprise.md does not link engineering-leaders.md",
                      structure_problems(unlinked, self.leaders))
        unlinked_back = re.sub(r"\]\((?:\./)?enterprise\.md[^)]*\)", "]", self.leaders)
        self.assertIn("docs/engineering-leaders.md does not link enterprise.md",
                      structure_problems(self.text, unlinked_back))

    def test_every_network_call_is_named_in_the_data_section(self) -> None:
        """US1317 AC2. MUTANTS: a planted script with an HTTP call, a `gh` call or a git fetch the
        page does not name; a named file whose row omits a kind of call it makes; a comment
        counted as a call; the no-telemetry statement dropped."""
        body = section_body(self.text, "data")
        found = scan()
        self.assertIn(".claude/skills/sdlc-studio/scripts/version_check.py", found,
                      "the scan no longer finds the version check's call: it has stopped looking")
        self.assertEqual(found["install.sh"], {"http"})
        self.assertEqual(unnamed(found, body), [])
        self.assertRegex(body, r"\bno telemetry\b")
        self.assertNotIn(".claude/skills/sdlc-studio/scripts/telemetry.py", found,
                         "telemetry.py makes a network call the no-telemetry statement denies")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            scripts = root / ".claude" / "skills" / "sdlc-studio" / "scripts"
            (scripts / "lib").mkdir(parents=True)
            (root / "install.sh").write_text("# curl -fsSL https://example.invalid\necho hi\n")
            (scripts / "lib" / "planted_http.py").write_text(
                "import urllib.request\nurllib.request.urlopen('https://example.invalid')\n")
            (scripts / "planted_gh.py").write_text("run(['gh', 'issue', 'list'])\n")
            (scripts / "planted_git.py").write_text("_git(root, 'fetch', 'origin')\n")
            (scripts / "planted.js").write_text("await fetch('https://example.invalid');\n")
            (scripts / "version_check.py").write_text("subprocess.run(['gh', 'api', 'x'])\n")
            (scripts / "tests").mkdir()
            (scripts / "tests" / "test_x.py").write_text("import urllib.request\n")
            planted = scan(root)
            self.assertNotIn("install.sh", planted, "a commented curl was counted as a call")
            self.assertEqual(planted[".claude/skills/sdlc-studio/scripts/planted_git.py"],
                             {"git fetch"})
            problems = unnamed(planted, body)
            for name in ("lib/planted_http.py", "planted_gh.py", "planted_git.py", "planted.js"):
                self.assertIn(f".claude/skills/sdlc-studio/scripts/{name}: makes a network call "
                              "the data section does not name", problems)
            self.assertIn(".claude/skills/sdlc-studio/scripts/version_check.py: its gh call is "
                          "not said in its row", problems)
            self.assertEqual(len(problems), 5, problems)

    def test_the_controls_map_names_evidence_and_claims_no_certification(self) -> None:
        """US1317 AC3. MUTANTS: a gate's evidence emptied; a gate row dropped; a link to a file
        that does not exist; a backticked path that does not exist; certified or compliant used
        as a claim."""
        body = section_body(self.text, "fitting existing controls")
        self.assertEqual(controls_problems(body), [])
        self.assertEqual(certification_claims(self.text), [])
        rows = {r[0].strip("* ").lower(): r for r in table_rows(body)}
        for gate in GATES:
            row = next(r for k, r in rows.items() if k.startswith(gate))
            line = next(ln for ln in body.splitlines() if ln.strip().startswith(f"| {row[0]} "))
            emptied = body.replace(line, f"| {row[0]} | nothing | |")
            self.assertIn(f"gate {gate!r} names no evidence", controls_problems(emptied), gate)
            self.assertIn(f"gate {gate!r} has no row",
                          controls_problems(body.replace(line, "")), gate)
        broken = body + "\n[gone](../sdlc-studio/no-such-record.md)\n"
        self.assertIn("../sdlc-studio/no-such-record.md names no file", controls_problems(broken))
        self.assertIn("../sdlc-studio/prd.md#no-such-heading names no heading in prd.md",
                      controls_problems(body + "\n[gone](../sdlc-studio/prd.md#no-such-heading)\n"))
        self.assertIn("`sdlc-studio/no-such-dir/` names no path",
                      controls_problems(body + "\n`sdlc-studio/no-such-dir/`\n"))
        for planted in ("SDLC Studio makes a team SOC 2 ready.",
                        "The evidence pack is certified for audit.",
                        "The process is compliant with audit rules."):
            self.assertEqual(certification_claims(f"{self.text}\n\n{planted}\n"), [planted])
        self.assertEqual(certification_claims("It holds no certification of any kind.\n"), [])

    def test_cost_commands_exist_and_figures_cite_signed_reports(self) -> None:
        """US1317 AC4. MUTANTS: a command that does not exist; a config key the reference does
        not document; a figure changed; a figure whose report is dropped from its claim; a
        report cited that is not signed."""
        body = section_body(self.text, "cost")
        named = [" ".join(c).replace("sprint.py", "sprint") for c in commands(body)]
        for command in COST_COMMANDS:
            self.assertIn(command, named)
        self.assertEqual(command_problems(body), [])
        self.assertRegex(body, r"\$\d")
        self.assertEqual(figure_problems(body), [])
        self.assertIn("sprint.py budget --help exits 2",
                      command_problems("Run `sprint budget --monthly`."))
        self.assertIn("`capacity.dollars` is not a key the config reference documents",
                      command_problems("Set `capacity.dollars`."))
        figure = next(f for c in claims(body) for f in _DOLLARS.findall(c))
        changed = body.replace(figure, figure[:-1] + ("1" if figure[-1] != "1" else "2"), 1)
        self.assertTrue(any("is carried by no signed report" in p
                            for p in figure_problems(changed)), changed)
        for planted in ("$2.0", "$2.10"):
            self.assertIn(f"{planted} is carried by no signed report its claim names",
                          figure_problems(f"RPT0035 states {planted} a point."), planted)
        uncited = _REPORT_ID.sub("the report", body)
        self.assertTrue(any("names no report" in p for p in figure_problems(uncited)))
        with tempfile.TemporaryDirectory() as d:
            for sig in (None, {"report": "RPT0001", "fingerprint": "f", "signed_at": "t"}):
                (Path(d) / "RPT9999.json").write_text(json.dumps({"signature": sig, "sections": [
                    {"rows": [{"est_measure": {"value": "Dollars per point"},
                               "est_actual": {"value": "$9.99"}}]}]}))
                self.assertIn("RPT9999 is not signed",
                              figure_problems("RPT9999 states $9.99 a point.", Path(d)), sig)


if __name__ == "__main__":
    unittest.main()
