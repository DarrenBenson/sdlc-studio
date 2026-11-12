"""US1012: a recorded verdict is bound to the bytes of the file its brief issued.

`critic.py record --from-verdict <path>` writes a ninth `Source` cell: `sha256:<16 hex> <basename>`
of the file's exact bytes when the path is one a brief issued for the unit, and `-` (transcribed)
for anything else. The column is added by padding, so no frozen row identity moves, and `show`
says where each verdict came from without claiming who wrote the file.

Every case drives `critic.py` through its entry point in a throwaway project, from a working
directory that is not the project root.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import collections
import hashlib
import json
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
CRITIC = SCRIPTS / "critic.py"
critic = loader.load_script("critic")
table_cells = critic.sdlc_md.table_cells

UNIT = "US0001"
ISSUED_LABEL = "from the brief's verdict file (writer unread)"


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _project(root: Path, *units: str) -> None:
    """Stories with a QA seat card, in a throwaway project."""
    _write(root, "src/widget.py", "def w():\n    return 1\n")
    _write(root, "sdlc-studio/personas/seats/qa.md", "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n")
    for unit in units or (UNIT,):
        _write(root, f"sdlc-studio/stories/{unit}-widget.md",
               f"# {unit}: widget\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n"
               "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
               "- **Verify:** shell true\n")


def _critic(cwd: Path, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(CRITIC), *args], cwd=cwd, input=stdin,
                          capture_output=True, text=True, timeout=300, env=gitutil.git_env(),
                          check=False)


def _brief(cwd: Path, root: Path, unit: str = UNIT) -> tuple[Path, str, list[str]]:
    """Brief the unit: the issued path, the BRIEF stem it opens with, and the footer's record
    command as argv after `critic.py`."""
    r = _critic(cwd, "brief", "--unit", unit, "--seat", "qa", "--root", str(root))
    assert r.returncode == 0, r.stderr
    tail = r.stdout[r.stdout.rindex(critic._RETURN_CONTRACT):]
    path = next(Path(ln.strip()) for ln in tail.splitlines() if ln.strip().endswith(".txt"))
    m = re.search(r"record the verdict with:\s+critic\.py (record .*)$", r.stderr, re.M)
    assert m, r.stderr
    return path, path.stem, [a for a in shlex.split(m.group(1)) if a != "..."]


def _record(cwd: Path, root: Path, argv: list[str], stdin: str | None = None,
            reviewer: str = "qa-seat") -> subprocess.CompletedProcess:
    r = _critic(cwd, *argv, "--reviewer", reviewer, "--author", "builder", "--root", str(root),
                stdin=stdin)
    assert r.returncode == 0, r.stderr
    return r


def _table(root: Path) -> list[list[str]]:
    """The ledger's table lines as cells, header first, the separator dropped."""
    text = critic.verdicts_path(root).read_text(encoding="utf-8")
    return [table_cells(ln) for ln in text.splitlines()
            if ln.startswith("|") and not set(ln.strip()) <= set("|-: ")]


def _block(stem: str, verdict: str = "APPROVE", issues: str = "none") -> str:
    return (f"UNIT: {UNIT}\nBRIEF: {stem}\nVERDICT: {verdict}\nISSUES: {issues}\n"
            "BLOCKING: none\n")


class VerdictFileBindingTests(unittest.TestCase):

    def test_an_issued_file_is_hashed_as_written(self) -> None:
        """AC1. Mutants: hashing the parsed issues rather than the file; normalising its line
        endings or its trailing whitespace before hashing; the record rewriting the file."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            root, cwd = Path(d), Path(elsewhere)
            _project(root)
            path, stem, argv = _brief(cwd, root)
            # CRLF endings, trailing whitespace and prose either side of the three fields: the
            # bytes a reviewer wrote, which no parse of them gives back
            written = (f"UNIT: {UNIT}\r\nBRIEF: {stem}\r\n"
                       "I read the diff and ran the Verify line; the widget holds.  \r\n\r\n"
                       "VERDICT: APPROVE\r\nISSUES: none\r\nBLOCKING: none\r\n\r\n"
                       "A remark the row cannot carry whole. \t\r\n").encode("utf-8")
            path.write_bytes(written)
            rec = _record(cwd, root, argv)
            self.assertRegex(rec.stdout, rf"^recorded {UNIT} APPROVE \[delivery\] round 1 -> ")
            self.assertNotIn("transcribed", rec.stdout + rec.stderr)
            want = f"sha256:{hashlib.sha256(written).hexdigest()[:16]} {path.name}"
            self.assertEqual(want, critic.read_verdicts(root)[-1]["source"])
            header, *rows = _table(root)
            self.assertEqual(want, rows[-1][header.index("Source")], "the cell on disk")
            self.assertEqual(written, path.read_bytes(), "the record changed the reviewer's file")

    def test_a_verdict_from_no_issued_file_is_marked_transcribed(self) -> None:
        """AC2. Mutants: a directory test, so any file under `verdicts/` reads as issued; hashing
        whichever file `--from-verdict` names; a note matched on its path alone, so a file
        issued for another unit binds this one's row; the notice dropped or printed in place of
        the `recorded` line `sprint lane accept` parses."""
        def flags(_root: Path, _cwd: Path, _stem: str) -> tuple[list[str], str | None]:
            return ["record", "--unit", UNIT, "--verdict", "APPROVE", "--issues", "none"], None

        def piped(_root: Path, _cwd: Path, stem: str) -> tuple[list[str], str | None]:
            return ["record", "--unit", UNIT, "--from-verdict", "-"], _block(stem)

        def outside(_root: Path, cwd: Path, stem: str) -> tuple[list[str], str | None]:
            (cwd / "verdict.txt").write_text(_block(stem), encoding="utf-8")
            return ["record", "--unit", UNIT, "--from-verdict", str(cwd / "verdict.txt")], None

        def unissued(root: Path, _cwd: Path, stem: str) -> tuple[list[str], str | None]:
            mine = root / "sdlc-studio" / "reviews" / "verdicts" / UNIT / "mine.txt"
            mine.write_text(_block(stem), encoding="utf-8")
            return ["record", "--unit", UNIT, "--from-verdict", str(mine)], None

        def other_unit(root: Path, cwd: Path, _stem: str) -> tuple[list[str], str | None]:
            theirs, stem, _ = _brief(cwd, root, "US0002")
            theirs.write_text(_block(stem), encoding="utf-8")
            return ["record", "--unit", UNIT, "--from-verdict", str(theirs)], None

        for way in (flags, piped, outside, unissued, other_unit):
            with self.subTest(way.__name__), tempfile.TemporaryDirectory() as d, \
                    tempfile.TemporaryDirectory() as elsewhere:
                root, cwd = Path(d), Path(elsewhere)
                _project(root, UNIT, "US0002")
                # a brief WAS issued here, so its notes exist and name a file in that folder
                issued, stem, _ = _brief(cwd, root)
                argv, stdin = way(root, cwd, stem)
                rec = _record(cwd, root, argv, stdin=stdin)
                lines = rec.stdout.splitlines()
                self.assertRegex(lines[0], rf"^recorded {UNIT} APPROVE \[delivery\] round 1 -> ")
                self.assertNotIn("transcribed", lines[0])
                self.assertTrue(any("transcribed" in ln for ln in lines[1:]), rec.stdout)
                self.assertEqual("-", critic.read_verdicts(root)[-1]["source"])
                header, *rows = _table(root)
                self.assertEqual("-", rows[-1][header.index("Source")])
                self.assertEqual("APPROVE", rows[-1][header.index("Verdict")])
                self.assertFalse(issued.exists(), "control: the issued file was never written")

    def test_the_source_column_moves_no_frozen_row_identity(self) -> None:
        """AC3. Mutants: the new column named `Verdict`, so the migration never adds it and the
        parsed key overwrites APPROVE and REJECT; the ninth cell added to `row_identity`'s
        digest; a migration that rewrites or reorders an earlier row's cells."""
        seeded = [
            ["US0001", "REJECT", "qa-seat", "builder", "2026-10-01", "abc123abc123", "full",
             "[new] w returns 1 (src/widget.py:2)"],
            ["US0001", "APPROVE", "qa-seat", "builder", "2026-10-02", "def456def456", "light",
             "none"],
            ["US0003", "APPROVE", "eng-seat", "dev", "2026-09-01", "-", "-",
             r"[pre-existing] the `a\|b` probe is slow"],
        ]
        # The identities a signed run record froze from these rows: the eight-cell digest
        # `critic.row_identity` gave at e101adf0, before the column existed, held here as the
        # record holds them, so an identity this change recomputes cannot vouch for itself.
        frozen = ["9943c9513acb776e", "30a68b021c7be5ba", "d3bbb94a6e260106"]
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            root, cwd = Path(d), Path(elsewhere)
            _project(root, "US0001", "US0002")
            path = critic.verdicts_path(root)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "# Critic Verdicts\n\n"
                "| Unit | Verdict | Reviewer | Author | Date | Brief | Tier | Issues |\n"
                "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
                + "".join(f"| {' | '.join(cells)} |\n" for cells in seeded), encoding="utf-8")
            earlier = _table(root)[1:]
            self.assertEqual([8] * 3, [len(r) for r in earlier], "control: eight cells each")
            _record(cwd, root, ["record", "--unit", "US0002", "--verdict", "REJECT",
                                "--issues", "[new] w ignores its input"])
            header, *rows = _table(root)
            self.assertEqual(["Unit", "Verdict", "Reviewer", "Author", "Date", "Brief", "Tier",
                              "Source", "Issues"], header)
            self.assertEqual([len(header)] * 4, [len(r) for r in rows],
                             "a row's cell count differs from the header's")
            for before, after in zip(earlier, rows):
                self.assertEqual(before[:7] + ["-"] + before[7:], after)
            parsed = critic.read_verdicts(root)
            self.assertEqual(["REJECT", "APPROVE", "APPROVE", "REJECT"],
                             [r["verdict"] for r in parsed])
            self.assertEqual(["-"] * 4, [r["source"] for r in parsed])
            held = collections.Counter(critic.row_identity(r) for r in parsed)
            self.assertEqual([], [i for i in frozen if not held[i]],
                             "a frozen row identity is no longer found in the ledger")

    def test_show_says_where_each_verdict_came_from_and_claims_no_writer(self) -> None:
        """AC4. Mutants: the label `reviewer-written`, which claims a writer nothing checked;
        `show` omitting the source from either form."""
        with tempfile.TemporaryDirectory() as d, tempfile.TemporaryDirectory() as elsewhere:
            root, cwd = Path(d), Path(elsewhere)
            _project(root)
            path, stem, argv = _brief(cwd, root)
            path.write_text(_block(stem, "REJECT", "[new] w returns 1 (src/widget.py:2)"),
                            encoding="utf-8")
            _record(cwd, root, argv)
            _record(cwd, root, ["record", "--unit", UNIT, "--verdict", "APPROVE"])
            rel = f"sdlc-studio/reviews/verdicts/{UNIT}/{path.name}"
            shown = _critic(cwd, "show", "--root", str(root))
            self.assertEqual(0, shown.returncode, shown.stderr)
            first, second = [ln for ln in shown.stdout.splitlines() if ln.startswith(UNIT)]
            self.assertIn("REJECT", first)
            self.assertIn(ISSUED_LABEL, first)
            self.assertIn(rel, first)
            self.assertIn("APPROVE", second)
            self.assertIn("transcribed", second)
            self.assertNotIn(ISSUED_LABEL, second)
            self.assertNotIn("transcribed", first)
            self.assertNotIn("reviewer-written", shown.stdout)
            as_json = _critic(cwd, "show", "--format", "json", "--root", str(root))
            self.assertEqual(0, as_json.returncode, as_json.stderr)
            rows = json.loads(as_json.stdout)
            self.assertEqual([ISSUED_LABEL, "transcribed"], [r["provenance"] for r in rows])
            self.assertEqual([rel, None], [r["verdict_file"] for r in rows])


if __name__ == "__main__":
    unittest.main()
