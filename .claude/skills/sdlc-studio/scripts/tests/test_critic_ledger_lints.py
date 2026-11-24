"""BG1073: `critic.py record` wrote a reviewer's finding naming an email-shaped token or a `www.`
address bare, and markdownlint's MD034 (no bare URLs) then refused the verdict ledger at the next
commit that touched it. The ledger already code-spanned a bare http(s) URL; a bare email address
and a bare `www.` address are now spanned the same way, and a token already in a code span, in
angle brackets, or in a link destination is written as it was.

Each case records through `critic.py record` in a throwaway project and lints the ledger under
the repository's markdownlint config.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import contextlib
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

critic = loader.load_script("critic")
SKILL = Path(__file__).resolve().parents[1]
REPO = Path(__file__).resolve().parents[5]
CONFIG = REPO / ".markdownlint.json"
UNIT = "US0001"


def _markdownlint() -> str | None:
    """The markdownlint the repo's lane runs: on PATH, in this checkout, or in the main checkout
    this worktree hangs off (a worktree carries no `node_modules` of its own)."""
    found = shutil.which("markdownlint")
    if found:
        return found
    roots = [REPO]
    common = gitutil.git(["rev-parse", "--path-format=absolute", "--git-common-dir"], SKILL,
                         check=False, text=True)
    if common.returncode == 0 and common.stdout.strip():
        roots.append(Path(common.stdout.strip()).parent)
    for root in roots:
        cand = root / "node_modules" / ".bin" / "markdownlint"
        if cand.exists():
            return str(cand)
    return None


def _record(root: Path, issues: str) -> str:
    """Record one REJECT carrying `issues`; the Issues cell of the row it wrote, as written."""
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        rc = critic.main(["record", "--unit", UNIT, "--verdict", "reject", "--reviewer",
                          "qa-seat", "--author", "eng-seat", "--issues", issues,
                          "--root", str(root)])
    assert rc == 0, f"the record was refused: {issues!r}"
    row = [ln for ln in critic.verdicts_path(root).read_text(encoding="utf-8").splitlines()
           if ln.startswith(f"| {UNIT} |")][-1]
    return row.rstrip(" |").rsplit(" | ", 1)[1]


class CriticLedgerBareUrlTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)

    def _lints(self) -> None:
        """The ledger passes markdownlint with no finding at all, MD034 included."""
        mdl = _markdownlint()
        if mdl is None:
            self.skipTest("markdownlint is not installed (run `npm install`)")
        r = subprocess.run([mdl, "--config", str(CONFIG), "--json",
                            str(critic.verdicts_path(self.root))],
                           capture_output=True, text=True, check=False, timeout=300)
        out = (r.stderr or r.stdout).strip()
        self.assertEqual([], json.loads(out) if out else [], out)

    def test_an_email_shaped_finding_lints(self) -> None:
        """AC1. Mutant: the email address left bare, as HEAD wrote it (MD034)."""
        cell = _record(self.root, "[new] the gate host is boundary-push@gatehost.test, "
                                  "named in the hook")
        self.assertIn("`boundary-push@gatehost.test`", cell)
        self.assertEqual(1, cell.count("boundary-push@gatehost.test"))
        self.assertEqual([{"origin": "new", "text": "the gate host is "
                                                    "`boundary-push@gatehost.test`, named in "
                                                    "the hook"}],
                         critic.parse_findings(cell), "the finding no longer names the token")
        self._lints()

    def test_a_www_address_finding_lints(self) -> None:
        """AC2. Mutant: the `www.` address left bare (MD034). Its trailing full stop and an
        unbalanced closing bracket stay outside the span, as an http URL's do."""
        cell = _record(self.root, "[new] see www.example.com. (also www.example.org/a)")
        self.assertIn("see `www.example.com`. (also `www.example.org/a`)", cell)
        self._lints()

    def test_a_spanned_or_bracketed_token_is_left_as_written(self) -> None:
        """AC3, the control: an email in a code span, one in angle brackets and an `https://`
        URL are written exactly as before. Mutants: the `<...>` autolink not kept, so its
        address is spanned inside the brackets; the pass run inside code spans too."""
        issues = ("[new] mail `ops@example.com` or <ops@example.org>, "
                  "see `https://example.net/a`")
        cell = _record(self.root, issues)
        self.assertEqual(issues, cell)
        self._lints()
        bare = _record(self.root, "[new] read https://example.net/b")
        self.assertEqual("[new] read `https://example.net/b`", bare,
                         "premise: a bare https URL is spanned once, as before")

    def test_a_token_markdown_does_not_link_is_left_as_written(self) -> None:
        """A link destination, and a `www.` inside a longer host name, are no bare URL to
        markdownlint, so they are written as given. Mutants: the link destination not kept, so
        the link is broken by a span inside it; the `www.` pass without its look-behind, so a
        host name is split by a span."""
        issues = ("[new] the [mail](mailto:ops@example.com) link, and the hosts "
                  "cdn.www.example.com and xwww.example.com")
        self.assertEqual(issues, _record(self.root, issues))
        self._lints()

    def test_an_escaped_semicolon_after_an_address_stays_one_finding(self) -> None:
        """The escape a reviewer writes for a semicolon inside one finding (`\\;`) may follow an
        address straight on: the address is spanned, the escape stays outside the span, and
        the finding is one finding, as it was before addresses were spanned. Mutant: the
        `www.` pass running on through the backslash, so the span closes after it and the
        record is refused for an odd backtick the reviewer never wrote."""
        cell = _record(self.root, "[new] see www.example.com\\; mail ops@example.com\\; "
                                  "still one finding")
        self.assertIn("see `www.example.com`\\; mail `ops@example.com`\\; still", cell)
        self.assertEqual(1, len(critic.parse_findings(cell)), cell)
        self._lints()

    def test_a_url_holding_an_address_is_one_span(self) -> None:
        """An http(s) URL whose host starts `www.` or whose authority holds an address is one
        code span, as the URL pass writes it, since that pass runs before the address pass.
        Mutant: the address pass first, so the scheme is left bare beside a span of the rest."""
        cell = _record(self.root, "[new] see https://www.example.com/x and "
                                  "https://ops@example.com/x here")
        self.assertEqual("[new] see `https://www.example.com/x` and "
                         "`https://ops@example.com/x` here", cell)
        self._lints()

    def test_a_www_address_in_any_case_lints(self) -> None:
        """markdownlint reads `WWW.` as it reads `www.`, so an upper-case or mixed-case address
        is spanned too. Mutant: the `www.` pass matching lower case alone, leaving the host
        bare (MD034)."""
        cell = _record(self.root, "[new] host WWW.EXAMPLE.COM and Www.Example.org/a upper")
        self.assertIn("host `WWW.EXAMPLE.COM` and `Www.Example.org/a` upper", cell)
        self._lints()


class LedgerLintTests(unittest.TestCase):

    def test_a_url_followed_by_an_escaped_semicolon_is_recorded(self) -> None:
        """AC2. Mutant: the URL span closing after the backslash, which the tick counter reads
        as an escaped backtick, so the span never closes and the record is refused."""
        with tempfile.TemporaryDirectory() as tmp:
            cell = _record(Path(tmp), "[new] see https://example.com/a\\; then more")
            self.assertIn("see `https://example.com/a`\\; then more", cell)
            self.assertEqual(1, len(critic.parse_findings(cell)), cell)


if __name__ == "__main__":
    unittest.main()
