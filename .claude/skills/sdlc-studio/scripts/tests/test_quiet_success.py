"""The commands agents filter are quiet on success and whole on refusal, and the markdown
producers write lint-clean files (US1134).

Agents piped these commands through `tail` and hand-built wrappers, and a filter cut to the
success shape hides why a command refused. Each command is driven through its shipped entry
point in a throwaway project, with HOME and the harness stores pointed at the fixture.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
# test-census-subject: .claude/skills/sdlc-studio/scripts/verify_ac.py
# test-census-subject: .claude/skills/sdlc-studio/scripts/docgen.py
# test-census-subject: .claude/skills/sdlc-studio/scripts/sprint.py
# test-census-subject: .claude/skills/sdlc-studio/scripts/file_finding.py
# test-census-subject: .claude/skills/sdlc-studio/scripts/retro.py
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent
REPO = SCRIPTS.parents[3]
sys.path.insert(0, str(SCRIPTS / "tests"))
import gitutil  # noqa: E402
import loader  # noqa: E402

retro = loader.load_script("retro")

URL = "http://127.0.0.1:8080/v1/models"
#: A bare http(s) URL outside a code span or an autolink: markdownlint's MD034 shape.
BARE = re.compile(r"(?<![<`(])https?://")
STORY = ("# {uid}: x\n\n> **Status:** Review\n> **Points:** 1\n> **Epic:** EP0001\n"
         "> **Affects:** src/a.py, tests/test_a.py, changelog.d/{uid}.md\n\n"
         "## Acceptance Criteria\n\n### AC1: it holds\n\n{verify}")


def _markdownlint() -> str | None:
    """The markdown lane's own binary: this tree's, else an enclosing checkout's, else PATH."""
    for base in (REPO, *REPO.parents):
        cand = base / "node_modules" / ".bin" / "markdownlint"
        if cand.is_file() and os.access(cand, os.X_OK):
            return str(cand)
    return shutil.which("markdownlint")


class QuietSuccessTests(unittest.TestCase):

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name) / "p"
        self.home = Path(tmp.name) / "home"
        self.home.mkdir()
        for rel, body in (("src/a.py", "x = 1\n"), ("tests/test_a.py", "def test_a():\n    pass\n"),
                          ("changelog.d/US0101.md", "<!-- section: Fixed -->\n\nx\n"),
                          ("sdlc-studio/personas/seats/qa.md",
                           "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n")):
            self._write(rel, body)
        for uid, verify in (("US0101", "- **Verify:** file src/a.py\n"),
                            ("US0102", "Holds when it holds.\n"),
                            ("US0103", "- **Verify:** file src/missing.py\n")):
            self._write(f"sdlc-studio/stories/{uid}-x.md", STORY.format(uid=uid, verify=verify))
        self.env = gitutil.git_env(
            HOME=str(self.home), XDG_DATA_HOME=str(self.home / "xdg"),
            CLAUDE_CONFIG_DIR=str(self.home / "claude"), CODEX_HOME=str(self.home / "codex"),
            COPILOT_HOME=str(self.home / "copilot"), OPENCODE_DB=str(self.home / "oc.db"))

    def _write(self, rel: str, body: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        return path

    def _run(self, script: str, *argv: str) -> tuple[int, list[str]]:
        r = subprocess.run([sys.executable, "-B", str(SCRIPTS / script), *argv], cwd=self.root,
                           capture_output=True, text=True, env=self.env, timeout=300)
        return r.returncode, (r.stdout + r.stderr).strip().splitlines()

    def test_each_command_is_quiet_on_success_and_verbose_on_refusal(self) -> None:
        """AC2. Each pair is (success argv, refusal argv, a phrase of the refusal's reason).
        MUTANTS: the passing lane return listing each criterion (three lines); the reading-guides
        refusal of a root with no skill tree removed (a refusal path reads as a success); the
        blocked lane return cut to its summary (its criterion output is asserted)."""
        claims = self._write("claims.json", json.dumps(
            [{"surface": "commit message", "claim": "a claim", "ruling": "TRUE"},
             {"surface": "changelog.d/US0101.md", "claim": "a claim", "ruling": "TRUE"}]))
        bad = self._write("bad.json", json.dumps(
            [{"surface": "commit message", "claim": "a claim", "ruling": "PROBABLY"}]))
        mutants = self._write("mutants.json", json.dumps(
            [{"mutant": "x = 2", "test": "tests/test_a.py", "result": "killed"}]))
        root, repo = str(self.root), str(REPO)
        cases = (
            ("critic.py", ["self-check", "record", "--unit", "US0101", "--claims", str(claims),
                           "--mutants", str(mutants), "--author", "builder", "--root", root],
             ["self-check", "record", "--unit", "US0101", "--claims", str(bad),
              "--mutants", str(mutants), "--author", "builder", "--root", root], "PROBABLY"),
            ("verify_ac.py", ["run", "--id", "US0101"], ["run", "--id", "US0102"],
             "NONE carries a `Verify:` line"),
            ("docgen.py", ["surface", "--check", "--root", repo], ["surface", "--root", root],
             "create it with the generation markers first"),
            ("docgen.py", ["reading-guides", "--check", "--root", repo],
             ["reading-guides", "--check", "--root", root], "no skill tree"),
            ("sprint.py", ["lane", "return", "--units", "US0101", "--root", root],
             ["lane", "return", "--units", "US0103", "--root", root], "src/missing.py"),
        )
        for script, ok, refused, reason in cases:
            with self.subTest(script=script, verb=ok[0], path="success"):
                rc, lines = self._run(script, *ok)
                self.assertEqual(0, rc, lines)
                self.assertTrue(1 <= len(lines) <= 2, f"{len(lines)} lines:\n" + "\n".join(lines))
            with self.subTest(script=script, verb=ok[0], path="refusal"):
                rc, lines = self._run(script, *refused)
                self.assertNotEqual(0, rc, lines)
                self.assertIn(reason, "\n".join(lines))
        # the blocked return carries every criterion's state and its output, not a summary
        rc, lines = self._run("sprint.py", "lane", "return", "--units", "US0103", "--root", root)
        text = "\n".join(lines)
        self.assertRegex(text, r"AC1: \w+ \(exit \d+\) <- ")
        self.assertGreater(len(lines), 2, text)

    def _assert_lint_clean(self, path: Path) -> None:
        text = path.read_text(encoding="utf-8")
        self.assertIn("127.0.0.1:8080", text, "premise: the URL reached the file")
        outside = "".join(text.split("`")[0::2])  # the prose outside code spans
        self.assertIsNone(BARE.search(outside), f"a bare URL in {path.name}:\n{text}")
        lint = _markdownlint()
        if lint:
            r = subprocess.run([lint, "--config", str(REPO / ".markdownlint.json"), str(path)],
                               capture_output=True, text=True, env=self.env, timeout=120)
            self.assertEqual(0, r.returncode, r.stdout + r.stderr + "\n" + text)

    def test_the_producers_write_lint_clean_markdown(self) -> None:
        """AC3. MUTANTS: critic's issues cell written without `_code_urls` (a bare URL in the
        ledger); the retro's accuracy block written without it (a bare URL in the retro);
        file_finding's `_code_urls` returning its text unchanged (the BG1227 shape)."""
        with self.subTest(producer="file_finding.py"):
            fields = self._write("finding.json", json.dumps(
                {"type": "bug", "title": "the probe fails", "severity": "low",
                 "summary": f"The probe at {URL} answers 500.",
                 "steps": f"1. Call {URL}.\n2. Read the status.",
                 "fix": f"Serve {URL} again.", "affects": "src/a.py", "points": 1}))
            rc, lines = self._run("file_finding.py", "file", "--fields-file", str(fields),
                                  "--root", str(self.root))
            self.assertEqual(0, rc, lines)
            [bug] = sorted((self.root / "sdlc-studio" / "bugs").glob("BG*.md"))
            self._assert_lint_clean(bug)
        with self.subTest(producer="critic.py record"):
            rc, lines = self._run("critic.py", "record", "--unit", "US0101", "--verdict",
                                  "reject", "--reviewer", "qa-seat", "--author", "builder",
                                  "--issues", f"[new] the endpoint {URL} answers 500",
                                  "--root", str(self.root))
            self.assertEqual(0, rc, lines)
            [ledger] = sorted((self.root / "sdlc-studio" / "reviews").glob("*.md"))
            self._assert_lint_clean(ledger)
        with self.subTest(producer="retro accuracy write"):
            path = self._write("sdlc-studio/retros/RETRO0001-a-sprint.md",
                               "# RETRO0001: a sprint\n\n## Summary\n\nIt ran.\n")
            unit = {"id": "US0001", "points": 2, "state": "measured", "estimate": 50000,
                    "actual_tokens": 40000, "ratio": 1.25, "tokens_per_point": 20000,
                    "oversized": False, "wall_time_s": 60, "model": URL}
            batch = {"points": 2, "estimate": 50000, "actual_tokens": 40000, "ratio": 1.25,
                     "tokens_per_point": 20000, "wall_time_s": 60, "oversized": [],
                     "tokens_per_point_within": 20000, "split_above": 8}
            retro.write_accuracy(self.root, {
                "path": str(path), "batch": batch, "units": [unit], "n_units": 1,
                "n_measured": 1, "n_forecast": 1, "n_sized": 1, "unmeasured": [],
                "unforecast": [], "models": [URL], "constants": None, "sample": None})
            self._assert_lint_clean(path)


if __name__ == "__main__":
    unittest.main()
