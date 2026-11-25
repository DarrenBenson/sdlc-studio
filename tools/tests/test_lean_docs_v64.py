"""US1171: the help, reference and public pages describe what 6.4 ships.

Each test names its mutant first: the page as it stood when EP0314 was groomed, which must fail
it. What a page claims is read against the code rather than a hand list wherever the code holds
it: the review brief's verdict file, the ledger's `Source` cell, the refusal of a reused file,
the seat's learnings block, the second seat and the bare `--rejoinder` from real `critic.py` runs
on a throwaway high-class unit; the commands the retro help names from each script's own parser;
each linked heading from the page it names; each new key's default from `reference-config.md`
and the shipped defaults; and what a 6.3 project owes `migrate`, and what its eight-column
verdict ledger needs, from real `migrate.py` and `critic.py record` runs on a 6.3-shaped fixture.
"""
# test-census-subject: docs/existing-users.md
from __future__ import annotations

import ast
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
SCRIPTS = SKILL / "scripts"
HELP = SKILL / "help"
CONFIG_REF = SKILL / "reference-config.md"
DEFAULTS = SKILL / "templates" / "config-defaults.yaml"
README = REPO / "README.md"
LLMS = REPO / "llms.txt"
WHY = REPO / "docs" / "why-sdlc-studio.md"
UPGRADE = REPO / "docs" / "existing-users.md"

sys.path.insert(0, str(SCRIPTS / "lib"))
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(REPO / "tools"))
import check_links  # noqa: E402
import critic  # noqa: E402
import escape  # noqa: E402
import prices  # noqa: E402
import retro  # noqa: E402
import sprint  # noqa: E402
import verdict_provenance  # noqa: E402


def _load_gitutil():
    """The shipped git-fixture helper, loaded rather than re-implemented, so every child process
    below runs with the same confinement the skill's own tests use."""
    path = SCRIPTS / "tests" / "gitutil.py"
    spec = importlib.util.spec_from_file_location("_docs_v64_gitutil", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


gitutil = _load_gitutil()

#: The configuration keys 6.4 adds, each with the dotted path its shipped default sits at in
#: `config-defaults.yaml`, or None for a key the price table, not that file, defaults.
NEW_KEYS = {
    "risk.components": "risk.components",
    "routing.effort.builder": "routing.effort.builder",
    "routing.effort.reviewer": "routing.effort.reviewer",
    "routing.effort.reviewer_below_builder": "routing.effort.reviewer_below_builder",
    "personas.memory.validity_days": "personas.memory.validity_days",
    "personas.memory.inject_max": "personas.memory.inject_max",
    "pricing.copilot_billing": None,
    "sprint.fresh_session": "sprint.fresh_session",
}

#: A verdict ledger as 6.3 wrote it: eight columns, no `Source`.
LEDGER_63 = ("# Critic verdicts\n\n"
             "| Unit | Verdict | Reviewer | Author | Date | Brief | Tier | Issues |\n"
             "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
             "| US0001 | APPROVE | Sam (qa) | Ade (product) | 2026-11-01 | - | full | none |\n")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _flat(text: str) -> str:
    """`text` with each run of whitespace read as one space, so a wrapped phrase still matches."""
    return re.sub(r"\s+", " ", text)


def _heading_section(text: str, heading: str) -> str:
    """The body under the heading line `heading`, up to the next heading of its level or higher."""
    found = re.search(rf"(?m)^{re.escape(heading)}\s*$", text)
    if not found:
        return ""
    level = len(heading) - len(heading.lstrip("#"))
    rest = text[found.end():]
    nxt = re.search(rf"(?m)^#{{1,{level}}} ", rest)
    return rest[:nxt.start()] if nxt else rest


def _anchors(path: Path) -> set[str]:
    """Every anchor a page offers: each explicit `{#id}` and each heading's GitHub slug."""
    found = set()
    fenced = False
    for line in _read(path).splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced and (m := re.match(r"^#{1,6}\s+(.+?)\s*$", line)):
            found.update(re.findall(r"\{#([\w-]+)\}", m.group(1)))
            found.add(check_links.slug(m.group(1)))
    return found


def _links(text: str, page: Path) -> dict[str, tuple[Path, str]]:
    """Each Markdown link target in `text` resolved from `page`: target -> (file, anchor)."""
    out = {}
    for target in re.findall(r"\]\(([^)\s]+)\)", text):
        if target.startswith(("http:", "https:", "mailto:")):
            continue
        file, _, anchor = target.partition("#")
        out[target] = ((page.parent / file).resolve() if file else page, anchor)
    return out


def _assert_links_resolve(case: unittest.TestCase, text: str, page: Path) -> None:
    for target, (file, anchor) in _links(text, page).items():
        case.assertTrue(file.is_file(), f"{page.name} links {target}, a file that does not exist")
        if anchor:
            case.assertIn(anchor, _anchors(file), f"{page.name} links {target}, a heading "
                          f"{file.name} does not hold")


def _config_ref_default(key: str) -> str:
    """The default `reference-config.md` states for `key`: the second cell of a row naming it
    first, else the last cell of a row whose first cell names it among others."""
    for line in _read(CONFIG_REF).splitlines():
        if not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split(" | ")]
        named = re.findall(r"`([^`]+)`", cells[0])
        if key not in named:
            continue
        if len(named) == 1 and re.fullmatch(r"`[^`]*`|\d+", cells[1]):
            return cells[1].strip("`")
        return cells[-1].strip("`")
    return ""


def _shipped_default(dotted: str) -> str:
    """The value `config-defaults.yaml` ships at `dotted`, read by indentation (no YAML
    dependency), as written, with any trailing comment and quotes dropped."""
    parts, depth, lines = dotted.split("."), 0, _read(DEFAULTS).splitlines()
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip())
        m = re.match(rf"^{' ' * (2 * depth)}{re.escape(parts[depth])}:\s*(.*)$", line)
        if m and indent == 2 * depth:
            if depth == len(parts) - 1:
                value = re.sub(r"\s+#.*$", "", m.group(1)).strip()
                return '""' if value in ('""', "''") else value
            depth += 1
    return ""


def _constants(path: Path, *names: str) -> dict:
    """The module-level literal each of `names` is bound to in `path`, read without importing."""
    out = {}
    for node in ast.parse(_read(path)).body:
        target = node.targets[0] if isinstance(node, ast.Assign) else (
            node.target if isinstance(node, ast.AnnAssign) else None)
        if isinstance(target, ast.Name) and target.id in names and node.value is not None:
            out[target.id] = ast.literal_eval(node.value)
    return out


class _Fixture:
    """A throwaway project and the confined environment every child process runs in: git
    cannot reach the outer repository, and no harness store or session is the operator's."""

    def __init__(self, tmp: Path):
        self.tmp = tmp
        self.root = tmp / "p"
        self.root.mkdir()
        home = tmp / "home"
        home.mkdir()
        self.env = gitutil.git_env(
            HOME=str(home), XDG_DATA_HOME=str(home), CLAUDE_CONFIG_DIR=str(home),
            CODEX_HOME=str(home), COPILOT_HOME=str(home), OPENCODE_DB=str(home / "oc.db"),
            SDLC_STUDIO_TRANSCRIPTS=str(home / "transcripts"))
        self.env.pop("CLAUDE_CODE_SESSION_ID", None)
        self.env.pop("SDLC_STUDIO_HARNESS", None)

    def write(self, rel: str, body: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path

    def unit(self, unit: str = "US0001", affects: str = "src/pay/charge.py") -> None:
        self.write(affects, "def charge():\n    return 1\n")
        self.write(f"sdlc-studio/stories/{unit}-charge.md",
                   f"# {unit}: charge\n\n> **Status:** Review\n> **Points:** 2\n"
                   f"> **Epic:** EP0001\n> **Affects:** {affects}\n\n"
                   "## Acceptance Criteria\n\n### AC1: works\n- **Verify:** shell true\n")

    def run(self, script: str, *argv: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *argv],
                              cwd=self.tmp, capture_output=True, text=True, check=False,
                              timeout=300, env=self.env)

    def brief(self, seat: str, *extra: str) -> subprocess.CompletedProcess:
        return self.run("critic.py", "brief", "--unit", "US0001", "--seat", seat,
                        "--root", str(self.root), *extra)

    def record(self, path: Path, reviewer: str) -> subprocess.CompletedProcess:
        return self.run("critic.py", "record", "--unit", "US0001", "--from-verdict", str(path),
                        "--reviewer", reviewer, "--author", "Ade (product)",
                        "--root", str(self.root))

    def ledger(self) -> str:
        path = self.root / "sdlc-studio" / "reviews" / "critic-verdicts.md"
        return _read(path) if path.is_file() else ""


def _issued(case: unittest.TestCase, brief: str) -> Path:
    """The verdict file a brief names, checked to open with the `UNIT` and `BRIEF` lines."""
    m = re.search(r"(?m)^(/\S*/sdlc-studio/reviews/verdicts/US0001/(\S+)\.txt)\n"
                  r"UNIT: US0001\nBRIEF: (\S+)$", brief)
    case.assertIsNotNone(m, "the brief names no verdict file under "
                            "sdlc-studio/reviews/verdicts/<unit>/ with its UNIT and BRIEF lines")
    case.assertEqual(m.group(2), m.group(3))
    return Path(m.group(1))


def _block(path: Path, verdict: str, issues: str = "none", blocking: str = "none") -> None:
    head = path.read_text(encoding="utf-8") if path.exists() else ""
    header = "".join(f"{ln}\n" for ln in head.splitlines()[:2])
    if not header:
        unit, stem = "US0001", path.stem
        header = f"UNIT: {unit}\nBRIEF: {stem}\n"
    path.write_text(f"{header}\nVERDICT: {verdict}\nISSUES: {issues}\nBLOCKING: {blocking}\n",
                    encoding="utf-8")


class DocsV64Tests(unittest.TestCase):

    def test_the_review_help_names_the_verdict_file_and_the_second_seat(self):
        """Mutant: help/review.md's brief section as EP0314's grooming found it, listing the
        verify command, the unit diff and the tool-call budget, and naming no verdict file, no
        `Source` column, no self-review, no bare `--rejoinder`, no learnings and no second seat.
        AC1."""
        brief = _flat(_heading_section(_read(HELP / "review.md"), "## The review brief"))
        self.assertTrue(brief, "help/review.md has no review brief section")
        for needle in ("`sdlc-studio/reviews/verdicts/<unit>/`", "`UNIT:`", "`BRIEF:`",
                       "`critic.py record --unit <id> --from-verdict <file>`", "`Source` column",
                       "exact bytes", "an earlier row's `Source` already carries",
                       "exit 2 and nothing written", "transcribed", "self-review",
                       "the context that edited the unit", "`self-review:<path>`",
                       "`--rejoinder`, with no value", "unanswered REJECT",
                       "live learnings", "`personas.memory.inject_max`",
                       "high-class unit", "the first or the second of its two independent seats"):
            self.assertIn(needle, brief, f"the review brief section does not say {needle!r}")
        _assert_links_resolve(self, brief, HELP / "review.md")
        inject = _config_ref_default("personas.memory.inject_max")
        self.assertEqual(inject, _shipped_default("personas.memory.inject_max"))
        self.assertIn(f"`personas.memory.inject_max` ({inject})", brief)

        # The self-review statement against the code: the token a writer adds to `Source` and
        # the mark `show` prints. The writers the page names are read from the page alone.
        self.assertEqual(verdict_provenance.SELF_REVIEW, "self-review")
        self.assertIn("self-review", critic.SELF_REVIEWED)
        for writer in ("`critic.py record`", "`transition.py set --verdict`",
                       "`artifact.py close --verdict`"):
            self.assertIn(writer, brief, f"the brief section does not name {writer}")

        with tempfile.TemporaryDirectory() as tmp:
            fx = _Fixture(Path(tmp))
            fx.write("sdlc-studio/.config.yaml", "risk:\n  components:\n    src/pay: high\n")
            fx.unit()
            other = "engineering" if sprint.FIRST_REVIEW_SEAT != "engineering" else "product"
            for role in (sprint.FIRST_REVIEW_SEAT, other):
                fx.write(f"sdlc-studio/personas/seats/{role}.md",
                         f"<!-- role: {role} -->\n# {role} seat\n\ncharter\n\n## Lens\n\nx\n\n## Pushes Back When\n\nx\n\n## Shadow\n\nx\n")
            first = fx.brief(sprint.FIRST_REVIEW_SEAT)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.assertIn("first of two independent seats", first.stdout)
            self.assertIn(f"--- LEARNINGS: {sprint.FIRST_REVIEW_SEAT}", first.stdout)
            issued = _issued(self, first.stdout)
            self.assertTrue(str(issued).startswith(str(fx.root)))
            second = fx.brief(other)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertIn("You are the second independent seat", second.stdout)
            reject_file = _issued(self, second.stdout)
            self.assertNotEqual(issued, reject_file, "two briefs named one verdict file")

            _block(issued, "APPROVE")
            done = fx.record(issued, f"Sam ({sprint.FIRST_REVIEW_SEAT})")
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            self.assertRegex(fx.ledger(), rf"\| sha256:[0-9a-f]{{16}} {re.escape(issued.name)}\b",
                             "the recorded row's Source cell is not the file's hash and name")
            before = fx.ledger()
            copy = Path(tmp) / "copy.txt"
            shutil.copyfile(issued, copy)
            again = fx.record(copy, f"Sam ({sprint.FIRST_REVIEW_SEAT})")
            self.assertEqual(again.returncode, 2, "a reused verdict file was recorded")
            self.assertIn("recorded once", again.stderr)
            self.assertEqual(fx.ledger(), before, "a refused record wrote to the ledger")

            _block(reject_file, "REJECT", "[new] the charge rounds down (src/pay/charge.py:2)",
                   "the charge rounds down")
            rejected = fx.record(reject_file, f"Eli ({other})")
            self.assertEqual(rejected.returncode, 0, rejected.stdout + rejected.stderr)
            rejoinder = fx.brief(other, "--rejoinder")
            self.assertEqual(rejoinder.returncode, 0, rejoinder.stderr)
            self.assertIn("VERDICT: REJECT", rejoinder.stdout)
            self.assertIn("the charge rounds down", rejoinder.stdout)
            none = fx.brief(sprint.FIRST_REVIEW_SEAT, "--rejoinder")
            self.assertEqual(none.returncode, 2, "a bare --rejoinder quoted another seat's REJECT")
            self.assertIn(f"no unanswered REJECT from a {sprint.FIRST_REVIEW_SEAT} reviewer", none.stderr)

    def test_the_retro_and_sprint_help_name_the_seat_record_and_the_new_keys(self):
        """Mutant: help/retro.md as EP0314's grooming found it, naming `retro seats` without
        the bugs it charges, no persona-learnings step, no `--strike` and no escape trace, and
        linking no reference section for any of them; and help/sprint.md naming neither
        `routing.effort` nor `pricing.copilot_billing`. AC2."""
        page = HELP / "retro.md"
        text = _read(page)
        wants = {
            "## Each seat's own record": (
                ("`retro.py seats --id RETROxxxx", "charges each later bug to the approval that "
                 "missed it", "`Escaped-via`"),
                "../reference-retro.md#seat-evidence-each-seat-on-its-own-record"),
            "## Persona learnings, listed at the close and struck at the signature": (
                ("`persona-memory` step", "`## Persona learnings` block",
                 "`sprint.py sign --strike M-NNNN --strike-reason"),
                "../reference-retro.md#persona-learnings-what-goes-live-when-you-sign"),
            "## An escaped bug": (
                ("`escape.py trace --bug BGxxxx`", "`--confirm <unit>`",
                 "`escape.py to-class --bug BGxxxx", "`sdlc-studio/lessons.jsonl`"),
                "../reference-scripts-review.md#escapepy"),
        }
        for heading, (needles, link) in wants.items():
            section = _flat(_heading_section(text, heading))
            self.assertTrue(section, f"help/retro.md has no {heading!r} section")
            for needle in needles:
                self.assertIn(needle, section, f"{heading!r} does not say {needle!r}")
            self.assertIn(f"]({link})", section, f"{heading!r} does not link {link}")
            _assert_links_resolve(self, section, page)
        learnings = _flat(_heading_section(text, "## Persona learnings, listed at the close and "
                                                 "struck at the signature"))
        self.assertIn("](../reference-persona-learning.md#listed-and-struck)", learnings)

        # The commands the page names, against each script's own parser and the close's chain.
        retro.build_parser().parse_args(["seats", "--id", "RETRO0001", "--format", "json"])
        escape.build_parser().parse_args(["trace", "--bug", "BG0001", "--confirm", "US0001"])
        escape.build_parser().parse_args(["to-class", "--bug", "BG0001", "--class", "c",
                                          "--rule", "r", "--behaviour", "b"])
        sprint.build_parser().parse_args(["sign", "--strike", "M-0001",
                                          "--strike-reason", "why"])
        chain = _constants(SCRIPTS / "sprint.py", "_CLOSE_CHAIN")["_CLOSE_CHAIN"]
        self.assertIn("persona-memory", chain)

        help_sprint = _read(HELP / "sprint.md")
        effort = _flat(next((p for p in re.split(r"\n\s*\n", help_sprint)
                             if p.startswith("**Reasoning effort")), ""))
        self.assertTrue(effort, "help/sprint.md has no reasoning effort paragraph")
        default = _config_ref_default("routing.effort.builder")
        self.assertEqual(default, _config_ref_default("routing.effort.reviewer"))
        self.assertEqual(default, _shipped_default("routing.effort.builder"))
        self.assertEqual(default, sprint.EFFORT_INHERIT)
        for needle in ("`routing.effort.builder`", "`routing.effort.reviewer`",
                       f"`{default}` (the session's own effort, the default)",
                       "`routing.effort.reviewer_below_builder`", "`sprint lane brief`"):
            self.assertIn(needle, effort, f"the effort paragraph does not say {needle!r}")
        for level in sprint.EFFORT_LEVELS:
            self.assertIn(f"`{level}`", effort, f"the effort paragraph does not name {level}")
        self.assertIn("](../reference-config.md#routing)", effort)

        billing = _flat(next((p for p in re.split(r"\n\s*\n", help_sprint)
                              if p.startswith("**Copilot billing")), ""))
        self.assertTrue(billing, "help/sprint.md has no Copilot billing paragraph")
        key = f"pricing.{prices.COPILOT_BILLING}"
        default = _config_ref_default(key)
        self.assertEqual(default, prices.TOKEN_BILLING,
                         "reference-config.md states a Copilot billing default the code does not")
        for needle in (f"`{key}`", f"The default, `{default}`", f"`{prices.REQUEST_BILLING}`",
                       "Copilot Pro or Pro+ annual plan", "premium requests"):
            self.assertIn(needle, billing, f"the Copilot billing paragraph does not say {needle!r}")
        self.assertIn("](../reference-config.md#pricing)", billing)
        _assert_links_resolve(self, effort + billing, HELP / "sprint.md")

    def test_the_public_pages_name_what_64_adds(self):
        """Mutant: README whose newest 'New in' line is 6.3's, llms.txt linking neither
        docs/engineering-leaders.md nor docs/evidence.md, and an evidence section in
        why-sdlc-studio.md that names no evidence pack. AC3."""
        readme = _read(README)
        new = [b for b in re.split(r"\n(?=- )|\n\s*\n", readme) if b.startswith("- **New in 6.4")]
        self.assertEqual(len(new), 1, "README has no single 'New in 6.4' line")
        new = _flat(new[0])
        for needle in ("evidence pack", "change board", "`release_cut.py evidence-pack`",
                       "each review seat's record", "`retro.py seats`", "escaped defect",
                       "approval that missed it", "`escape.py trace`", "forecast", "actual"):
            self.assertIn(needle, new, f"README's 6.4 line does not say {needle!r}")
        self.assertIn("evidence-pack", _read(SCRIPTS / "release_cut.py"))
        _assert_links_resolve(self, new, README)

        llms = _read(LLMS)
        for target in ("docs/engineering-leaders.md", "docs/evidence.md"):
            self.assertIn(f"]({target})", llms, f"llms.txt does not link {target}")
            self.assertTrue((REPO / target).is_file(), f"{target} does not exist")

        evidence = _flat(_heading_section(_read(WHY), "## The evidence"))
        self.assertTrue(evidence, "why-sdlc-studio.md has no evidence section")
        for needle in ("evidence pack", "`release_cut.py evidence-pack`", "](evidence.md)",
                       "change board"):
            self.assertIn(needle, evidence, f"the evidence section does not say {needle!r}")
        _assert_links_resolve(self, evidence, WHY)

    def test_existing_users_has_the_63_to_64_upgrade_path(self):
        """Mutant: the upgrade page whose newest section is still 'From 6.2 to 6.3'. The 6.4
        section is found by name, so a later release's section above it leaves this true. AC4."""
        page = _read(UPGRADE)
        froms = re.findall(r"(?m)^### (From \S+ to \S+)\s*$", page)
        self.assertIn("From 6.3 to 6.4", froms, "the upgrade page has no 6.4 section")
        at = froms.index("From 6.3 to 6.4")
        self.assertEqual(froms[at:at + 4], ["From 6.3 to 6.4", "From 6.2 to 6.3",
                                            "From 6.1 to 6.2", "From 6.0 to 6.1"])
        six_four = _flat(_heading_section(page, "### From 6.3 to 6.4"))
        for needle in ("Reinstall", "`migrate`", "`migrate --apply`", "`sdlc-studio/.version`",
                       "retires no config key or command", "`Source` column",
                       "pads every earlier row with `-`", "needs nothing from you",
                       "`--from-verdict`", "`pricing.copilot_billing: requests`",
                       "premium request", "optional"):
            self.assertIn(needle, six_four, f"the 6.4 section does not say {needle!r}")
        for key, dotted in NEW_KEYS.items():
            stated = _config_ref_default(key) or _shipped_default(dotted)
            self.assertTrue(stated, f"no default is stated or shipped for {key}")
            if dotted and _config_ref_default(key):
                self.assertEqual(stated.strip('"') or '""', _shipped_default(dotted).strip('"')
                                 or '""', f"reference-config.md and the shipped default "
                                          f"disagree on {key}")
            shown = re.escape(f"`{key}`") + r"(?: and `[\w.]+`)? \(" + re.escape(
                stated if re.fullmatch(r"\d+", stated) else f"`{stated}`") + r"\)"
            self.assertRegex(six_four, shown, f"the 6.4 section does not give {key} its default "
                                              f"{stated}")
        _assert_links_resolve(self, six_four, UPGRADE)

        with tempfile.TemporaryDirectory() as tmp:
            fx = _Fixture(Path(tmp))
            made = fx.run("init.py", "--root", str(fx.root), "run")
            self.assertEqual(made.returncode, 0, made.stdout + made.stderr)
            fx.write("sdlc-studio/.version", 'schema_version: 3\nupgraded_from: 6.2.0\n'
                                             'upgraded_at: 2026-11-09\nskill_version: "6.3.0"\n')
            fx.write("sdlc-studio/reviews/critic-verdicts.md", LEDGER_63)
            fx.unit()
            proc = fx.run("migrate.py", "--root", str(fx.root), "--format", "json")
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            owed = [item.get("detail", "") for item in json.loads(proc.stdout)["deterministic"]]
            self.assertTrue(all(".version" in detail for detail in owed),
                            f"migrate owes a 6.3 project more than its version stamp: {owed}")
            self.assertEqual(fx.ledger(), LEDGER_63, "the migrate dry run wrote the ledger")

            eight = [ln for ln in LEDGER_63.splitlines() if ln.startswith("| ")]
            self.assertTrue(all(len(ln.strip().strip("|").split(" | ")) == 8 for ln in eight),
                            "the 6.3 ledger fixture is not eight columns wide")
            self.assertNotIn("Source", LEDGER_63)
            briefed = fx.brief("qa")
            self.assertEqual(briefed.returncode, 0, briefed.stderr)
            issued = _issued(self, briefed.stdout)
            _block(issued, "APPROVE")
            done = fx.record(issued, "Sam (qa)")
            self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
            rows = [ln for ln in fx.ledger().splitlines() if ln.startswith("| US0001 |")]
            self.assertEqual(len(rows), 2, fx.ledger())
            old = rows[0].strip().strip("|").split(" | ")
            self.assertEqual([c.strip() for c in old],
                             ["US0001", "APPROVE", "Sam (qa)", "Ade (product)", "2026-11-01", "-",
                              "full", "-", "none"],
                             "the 6.3 row was not padded with '-' in Source, its cells kept")


if __name__ == "__main__":
    unittest.main()
