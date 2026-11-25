"""BG0974: the filer markdown-safes a finding's title and its Evidence line, so a bare
`snake_case` or leading-underscore identifier there is written inside a code span and
markdownlint's MD037 passes on the bug file and on the index row.

Each finding is filed through the shipped CLI (`file_finding.py file`) into a throwaway fixture
root (`--root`).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_filing_markdown_safe_title.py
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/file_finding.py
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import file_finding  # noqa: E402
import gitutil  # noqa: E402 - confined git, so an inherited GIT_DIR cannot steer the lookup

SCRIPT = Path(__file__).resolve().parent.parent / "file_finding.py"
SKILL = SCRIPT.parent.parent
CONFIG = SKILL / ".markdownlint.json"

EVIDENCE = ("BG0959 Evidence line: _mode_and_cutoff in test_lean_backlog_sweep, "
            "see file_finding.py:2011")


def _markdownlint() -> str | None:
    """The markdownlint the repo's lane runs: on PATH, in this checkout, or in the main checkout
    this worktree hangs off (a worktree carries no `node_modules` of its own)."""
    found = shutil.which("markdownlint")
    if found:
        return found
    roots = [SKILL.parents[1]]
    common = gitutil.git(["rev-parse", "--path-format=absolute", "--git-common-dir"], SKILL,
                         check=False, text=True)
    if common.returncode == 0 and common.stdout.strip():
        roots.append(Path(common.stdout.strip()).parent)
    for root in roots:
        cand = root / "node_modules" / ".bin" / "markdownlint"
        if cand.exists():
            return str(cand)
    return None


def _bare(line: str) -> str:
    """The line with every code span removed: what markdown reads as text."""
    return re.sub(r"`[^`]*`", "", line)


def _file(root: Path, title: str, type_: str = "bug", *extra: str) -> tuple[str, str]:
    """File one finding; return its H1 line and its index row."""
    (root / "src").mkdir(exist_ok=True)
    (root / "src" / "thing.py").write_text("", encoding="utf-8")
    file_finding.ensure_index(root, type_, "2026-11-23")  # the shipped index template
    typed = (["--severity", "low", "--points", "1", "--summary", "s", "--steps", "r",
              "--fix", "f", "--ac", "it holds", "--verify", "pytest tests/test_x.py"]
             if type_ == "bug" else ["--summary", "s"])
    r = subprocess.run(
        [sys.executable, str(SCRIPT), "file", "--root", str(root), "--type", type_,
         "--title", title, "--affects", "src/thing.py", "--author", "Tess Tester",
         *typed, *extra], capture_output=True, text=True, check=False)
    if r.returncode != 0:
        raise AssertionError(f"the filer refused the fixture finding:\n{r.stdout}{r.stderr}")
    folder = {"bug": "bugs", "rfc": "rfcs"}[type_]
    path = next(p for p in (root / "sdlc-studio" / folder).glob("*.md") if p.name != "_index.md")
    index = (root / "sdlc-studio" / folder / "_index.md").read_text(encoding="utf-8")
    row = next(ln for ln in index.splitlines() if ln.startswith("| [") and path.name in ln)
    return path.read_text(encoding="utf-8"), row


class TitleIdentifierTests(unittest.TestCase):
    """AC1: the H1 and the index row of a title holding bare identifiers."""

    TITLE = "test_lean_backlog_sweep reads only the live _index.md"
    SAFE = "`test_lean_backlog_sweep` reads only the live `_index.md`"

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.body, self.row = _file(Path(self._td.name), self.TITLE)
        self.h1 = self.body.splitlines()[0]

    def tearDown(self) -> None:
        self._td.cleanup()

    def test_title_identifier_is_code_spanned_in_the_h1(self) -> None:
        self.assertEqual(self.h1, f"# BG0001: {self.SAFE}")
        self.assertNotIn("_", _bare(self.h1))

    def test_title_identifier_is_code_spanned_in_the_index_row(self) -> None:
        self.assertIn(f"| {self.SAFE} |", self.row)
        self.assertNotIn("_", _bare(self.row))

    def test_title_identifier_is_code_spanned_in_an_rfcs_h1_and_row(self) -> None:
        """The title is safed for every type the filer mints, not the bug layout alone."""
        with tempfile.TemporaryDirectory() as d:
            body, row = _file(Path(d), "keep _cache_dir apart", "rfc", "--option", "do it")
        self.assertTrue(body.splitlines()[0].endswith(": keep `_cache_dir` apart"), body)
        self.assertIn("| keep `_cache_dir` apart |", row)

    def test_the_file_name_is_still_slugged_from_the_title_words(self) -> None:
        self.assertIn("(BG0001-test-lean-backlog-sweep-reads-only-the-live.md)", self.row)


class EvidenceIdentifierTests(unittest.TestCase):
    """AC2: the Evidence line."""

    def test_evidence_identifier_is_code_spanned(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            body, _row = _file(Path(d), "a plain title", "bug", "--evidence", EVIDENCE)
        line = next(ln for ln in body.splitlines() if ln.startswith("> **Evidence:** "))
        value = line[len("> **Evidence:** "):]
        self.assertEqual(value, "BG0959 Evidence line: `_mode_and_cutoff` in "
                                "`test_lean_backlog_sweep`, see `file_finding.py`:2011")
        self.assertNotIn("_", _bare(value))
        self.assertEqual(value.replace("`", ""), EVIDENCE)  # otherwise byte-identical


class TitleMarkdownTests(unittest.TestCase):
    """AC3: a title holding two identifiers that begin with underscores, filed, passes
    markdownlint in the bug file and in the index. Beside the criterion's own title, two with a
    bracket before a parenthetical that is no link destination, which is prose to safe."""

    TITLES = ("_mode_and_cutoff and _check disagree", "arr[0](_a and _b) differs",
              "handlers[kind](_row, _seat) drops the seat")

    @classmethod
    def setUpClass(cls) -> None:
        cls._tds = [tempfile.TemporaryDirectory() for _ in cls.TITLES]
        cls.roots = [Path(td.name) for td in cls._tds]
        cls.filed = [_file(root, title) for root, title in zip(cls.roots, cls.TITLES)]

    @classmethod
    def tearDownClass(cls) -> None:
        for td in cls._tds:
            td.cleanup()

    def _lint(self, path: Path) -> subprocess.CompletedProcess:
        lint = _markdownlint()
        if lint is None:
            self.skipTest("markdownlint is not installed (npm install) - the lint lane enforces this")
        return subprocess.run([lint, "-c", str(CONFIG), str(path)], capture_output=True,
                              text=True, check=False)

    def test_neither_line_holds_an_underscore_outside_a_code_span(self) -> None:
        """Runs with or without markdownlint: the underscores MD037 reads as emphasis."""
        for title, (body, row) in zip(self.TITLES, self.filed):
            with self.subTest(title=title):
                self.assertNotIn("_", _bare(body.splitlines()[0]))
                self.assertNotIn("_", _bare(row))

    def test_the_bug_file_passes_markdownlint(self) -> None:
        for title, root in zip(self.TITLES, self.roots):
            with self.subTest(title=title):
                r = self._lint(next((root / "sdlc-studio" / "bugs").glob("BG*.md")))
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_the_index_passes_markdownlint(self) -> None:
        for title, root in zip(self.TITLES, self.roots):
            with self.subTest(title=title):
                r = self._lint(root / "sdlc-studio" / "bugs" / "_index.md")
                self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def _filed_with(self, title: str, summary: str, steps: str, fix: str) -> tuple[Path, str, str]:
        """One bug filed with the given prose; the fixture root, its file and its index row."""
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        root = Path(td.name)
        body, row = _file(root, title, "bug", "--summary", summary, "--steps", steps,
                          "--fix", fix)
        return root, body, row

    def test_a_bare_double_asterisk_in_the_title_passes_markdownlint_in_file_and_index(
            self) -> None:
        """AC1. Mutant: `_md_safe` leaves a lone `**` as written, so MD037 refuses the bug file
        and the index."""
        root, body, row = self._filed_with("a ** b flips the flag", "the ** marker breaks",
                                           "1. run it", "escape the ** marker")
        self.assertEqual("# BG0001: a \\*\\* b flips the flag", body.splitlines()[0])
        self.assertIn("| a \\*\\* b flips the flag |", row)
        for target in (next((root / "sdlc-studio" / "bugs").glob("BG*.md")),
                       root / "sdlc-studio" / "bugs" / "_index.md"):
            r = self._lint(target)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)

    def test_a_bare_double_asterisk_in_summary_steps_and_fix_is_safed(self) -> None:
        """AC2. Mutants: only the title safed; the Steps (written as given) left out; a marker
        at a line start or end, or beside a code span, not reached."""
        _root, body, _row = self._filed_with(
            "plain", "summary ** here\n** at a line start\nat a line end **",
            "1. run a ** b\n2. then `x` ** y\n```\ngit log ** keep\n```", "fix ** here")
        for want in ("summary \\*\\* here\n\\*\\* at a line start\nat a line end \\*\\*",
                     "1. run a \\*\\* b\n2. then `x` \\*\\* y\n",
                     "git log ** keep\n```",  # a fenced block is the author's, as written
                     "fix \\*\\* here"):
            self.assertIn(want, body)
        bare = re.sub(r"(?s)```.*?```", "", body)
        bare = re.sub(r"`[^`\n]*`", "", bare)
        self.assertNotRegex(bare, r"(?<!\S)\*\*(?!\S)")

    def test_a_glob_in_a_step_command_is_escaped_outside_a_fence_only(self) -> None:
        """What the escape costs a copied command, as `_steps_safe` says: a glob `**` on a step
        or an indented code line is escaped, and the same line in a fence is kept as written."""
        steps = "1. ls ** | wc -l\n       ls ** | wc -l\n```\nls ** | wc -l\n```"
        out = file_finding._steps_safe(steps)
        self.assertEqual("1. ls \\*\\* | wc -l\n       ls \\*\\* | wc -l\n```\nls ** | wc -l\n```", out)

    def test_real_bold_a_field_declaration_and_a_spanned_marker_are_kept(self) -> None:
        """AC3, the controls. Mutants: every asterisk pair escaped; the marker inside a code
        span escaped; the spaceless `**x**` pair escaped."""
        _root, body, _row = self._filed_with(
            "real **bold** stays",
            "a **bold** word, and a `**` kept, and `a ** b` kept, `a`** b and c **`d`",
            "1. run **x** and `a`** b and c **`d`\n2. keep `a ** b` here", "see **Note:** here")
        self.assertEqual("# BG0001: real **bold** stays", body.splitlines()[0])
        self.assertIn("a **bold** word, and a `**` kept, and `a ** b` kept, `a`** b and c **`d`",
                      body)
        self.assertIn("1. run **x** and `a`** b and c **`d`\n2. keep `a ** b` here", body)
        self.assertIn("see **Note:** here", body)
        self.assertIn("> **Status:** Open\n", body)


class LinkDestinationTests(unittest.TestCase):
    """A markdown link to an underscored file keeps working on the lines the filer safes: the
    token pass leaves a `](...)` destination alone (the reviewer's two inputs)."""

    LINK = "[the filer test](scripts/tests/test_file_finding.py)"

    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)

    def tearDown(self) -> None:
        self._td.cleanup()

    def _lint_clean(self) -> None:
        """The bug file and the index under the skill's config and the repository's own."""
        lint = _markdownlint()
        if lint is None:
            self.skipTest("markdownlint is not installed (npm install) - the lint lane enforces this")
        folder = self.root / "sdlc-studio" / "bugs"
        repo = SKILL.parents[1] / ".markdownlint.json"  # absent from an installed copy
        for config in (CONFIG, *[repo][:repo.exists()]):
            r = subprocess.run([lint, "-c", str(config), *map(str, folder.glob("*.md"))],
                               capture_output=True, text=True, check=False)
            self.assertEqual(r.returncode, 0, f"{config}:\n{r.stdout}{r.stderr}")

    def test_an_evidence_link_to_an_underscored_file_is_kept_as_written(self) -> None:
        evidence = f"Found filing BG0959, see {self.LINK} for it"
        body, _row = _file(self.root, "a plain title", "bug", "--evidence", evidence)
        self.assertIn(f"\n> **Evidence:** {evidence}\n", body)
        self._lint_clean()

    def test_a_title_link_to_an_underscored_file_is_kept_in_the_h1_and_the_row(self) -> None:
        title = f"see {self.LINK} for it"
        body, row = _file(self.root, title)
        self.assertEqual(body.splitlines()[0], f"# BG0001: {title}")
        self.assertIn(f"| {title} |", row)
        self._lint_clean()

    def test_only_the_destination_is_exempt_and_the_link_text_is_still_safed(self) -> None:
        self.assertEqual(file_finding._md_safe("see [the my_mod docs](a_b/c_d.md) and e_f (g_h x)"),
                         "see [the `my_mod` docs](a_b/c_d.md) and `e_f` (`g_h` x)")
        self.assertEqual(file_finding._md_safe("![a_b](img_c.png)"), "![`a_b`](img_c.png)")

    def test_a_destination_ends_at_its_line(self) -> None:
        """An unclosed `](` exempts nothing on the lines after it."""
        self.assertEqual(file_finding._md_safe("an open ](here\nand my_var)"),
                         "an open ](here\nand `my_var`)")

    def test_a_parenthetical_holding_whitespace_is_no_destination(self) -> None:
        """The reviewer's two titles, and a parenthetical whose first word reads as a path."""
        self.assertEqual(file_finding._md_safe("arr[0](_a and _b) differs"),
                         "arr[0](`_a` and `_b`) differs")
        self.assertEqual(file_finding._md_safe("handlers[kind](_row, _seat) drops the seat"),
                         "handlers[kind](`_row`, `_seat`) drops the seat")
        self.assertEqual(file_finding._md_safe("f[k](a.b and c_d)"), "f[k](a.b and `c_d`)")

    def test_a_destination_must_read_as_a_path_or_url(self) -> None:
        self.assertEqual(file_finding._md_safe("handlers[kind](_row)"), "handlers[kind](`_row`)")
        self.assertEqual(file_finding._md_safe('[k](_a "t.x")'), '[k](`_a` "t.x")')
        for dest in ("x/my_y", "my_y.md", "#my_anchor", "mailto:my_y"):
            with self.subTest(dest=dest):
                self.assertEqual(file_finding._md_safe(f"[a_b]({dest})"), f"[`a_b`]({dest})")

    def test_a_link_title_and_an_angle_bracket_destination_are_kept(self) -> None:
        for link in ('[a](x/my_y "the t_z")', "[a](x/my_y 'the t_z')", "[a](<my y_z.md>)"):
            with self.subTest(link=link):
                self.assertEqual(file_finding._md_safe(link), link)


if __name__ == "__main__":
    unittest.main()
