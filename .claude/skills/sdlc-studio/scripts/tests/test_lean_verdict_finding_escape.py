"""BG0885: a finding that reads as markdown is recorded so the ledger lints and reads back.

`critic.py record` copied `--issues` into `critic-verdicts.md` as raw markdown, so a finding
quoting a regex such as `[A-Z][A-Z_]{4,}` was read as an undefined reference link (MD052) and
the paperwork commit carrying the verdict was refused until the ledger was hand-edited.

The verdict is briefed and recorded through the shipped CLI in a throwaway `init run` project,
linted with this repository's markdownlint config, and read back through the ledger's reader.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

_SCRIPTS = Path(__file__).resolve().parent.parent
_REPO = Path(__file__).resolve().parents[5]
_ID = re.compile(r"created (\S+)")
FINDING = "the shape [A-Z][A-Z_]{4,} matches UNKNOWN"


def _cli(root: Path, script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-B", str(_SCRIPTS / script), *args, "--root", str(root)],
        cwd=root, env=gitutil.git_env(), capture_output=True, text=True, timeout=300)


def _ok(root: Path, script: str, *args: str) -> str:
    proc = _cli(root, script, *args)
    if proc.returncode != 0:
        raise AssertionError(f"{script} {' '.join(args)} exited {proc.returncode}:\n"
                             f"{proc.stdout}\n{proc.stderr}")
    return proc.stdout


def _markdownlint() -> str | None:
    local = _REPO / "node_modules" / ".bin" / "markdownlint"
    return str(local) if local.exists() else shutil.which("markdownlint")


class VerdictFindingEscapeTests(unittest.TestCase):
    def _record_and_lint(self, finding: str) -> tuple[list[dict], str | None, str]:
        """Record `[new] finding` through the shipped CLI in a throwaway project: the findings
        the ledger's reader returns, markdownlint's output on the ledger (None when markdownlint
        is absent), and the ledger text."""
        critic = loader.load_script("critic")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            subprocess.run(["git", "init", "-q", "-b", "main", str(root)],
                           env=gitutil.git_env(), check=True, capture_output=True)
            _ok(root, "init.py", "run")
            bug = _ID.search(_ok(
                root, "artifact.py", "new", "--type", "bug", "--title", "a widget defect",
                "--severity", "low", "--points", "1", "--affects", "src/widget.py",
                "--ac", "the widget holds", "--verify", "shell test -f src/widget.py")).group(1)
            _ok(root, "critic.py", "brief", "--unit", bug, "--seat", "qa")
            _ok(root, "critic.py", "record", "--unit", bug, "--verdict", "REJECT",
                "--reviewer", "qa seat", "--author", "engineering seat",
                "--issues", f"[new] {finding}")
            [row] = [r for r in critic.read_verdicts(root) if r["verdict"] == "REJECT"]
            ledger = root / "sdlc-studio" / "reviews" / "critic-verdicts.md"
            mdl = _markdownlint()
            lint = None if mdl is None else subprocess.run(
                [mdl, "--config", str(_REPO / ".markdownlint.json"), "--", str(ledger)],
                capture_output=True, text=True, timeout=120)
            return (critic.parse_findings(row["issues"]),
                    None if lint is None else lint.stdout + lint.stderr,
                    ledger.read_text(encoding="utf-8"))

    def test_a_bracketed_finding_lints_and_reads_back(self) -> None:
        """AC1. MUTANT: HEAD's `_clean`, which escapes only `_` outside code spans - the
        brackets reach the ledger raw and markdownlint reports MD052 on `[A-Z]`. MUTANT: an
        escape the reader does not undo - the finding reads back as `[A-Z]\\[A-Z\\_]...`,
        not as given."""
        findings, lint, ledger = self._record_and_lint(FINDING)
        self.assertEqual([{"origin": "new", "text": FINDING}], findings)
        if lint is None:
            self.skipTest("markdownlint not installed - the pre-commit markdown lane runs it")
        self.assertNotIn("MD052", lint, ledger)

    def test_an_escaped_bracket_the_author_typed_reads_back_byte_for_byte(self) -> None:
        """A finding already holding `]\\[` reads back with its backslash. MUTANT: a writer
        that escapes only a bare `[` after `]` (stores `]\\[` unchanged) - the reader takes the
        author's backslash for its own escape and returns `[a-z][q]`."""
        finding = r"the class [a-z]\[q] and ([a-z])\[0-9] stay as typed"
        findings, lint, ledger = self._record_and_lint(finding)
        self.assertEqual([{"origin": "new", "text": finding}], findings)
        if lint is None:
            self.skipTest("markdownlint not installed - the pre-commit markdown lane runs it")
        self.assertNotIn("MD052", lint, ledger)

    def test_a_reversed_link_lints_and_reads_back(self) -> None:
        """`(state)[2]` is a reversed link (MD011) unless its bracket is escaped. MUTANT: the
        escape narrowed to a bracket after `]` only - the bracket after `)` reaches the ledger
        raw and markdownlint reports MD011."""
        finding = "the lookup (state)[2] picks the wrong field"
        findings, lint, ledger = self._record_and_lint(finding)
        self.assertEqual([{"origin": "new", "text": finding}], findings)
        if lint is None:
            self.skipTest("markdownlint not installed - the pre-commit markdown lane runs it")
        self.assertNotIn("MD011", lint, ledger)


if __name__ == "__main__":
    unittest.main()
