"""BG1772: a declared seat card that is not valid UTF-8 no longer stops critic.py.

`critic._declared_reviewers` read each card under `sdlc-studio/personas/seats` and
`sdlc-studio/personas/amigos` as UTF-8 and caught only OSError, so one card holding other bytes
raised UnicodeDecodeError out of every command that resolves the declared seats, `critic.py
record` among them. It now skips that card with one warning on stderr naming it, and reads the
valid cards beside it.

MUTANTS, each of which a test here fails on: (1) the failed decode left to raise, or caught as
OSError only (the record exits 1 with a traceback); (2) the skip turned into a stop, so the
valid card after the bad one in the same folder is lost; (3) no warning, or a warning that does
not name the card's folder and file; (4) the warning printed to stdout, which `sprint lane
accept` parses; (5) the warning repeated each time a command resolves the seats; (6) the warning
remembered by the card's place in the project rather than its own path, so a second project in
the same process is not told about its card; (7) an unreadable card (OSError) now warned about,
where it was skipped silently before.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

critic = loader.load_script("critic")
SCRIPT = Path(critic.__file__)

#: Bytes that are not UTF-8, in front of a header the reader would otherwise accept.
BAD = b"\xff\xfe<!-- role: security -->\n# Bad Card - Security amigo\n"


def _card(root: Path, sub: str, name: str, body: str | bytes) -> Path:
    d = root / "sdlc-studio" / "personas" / sub
    d.mkdir(parents=True, exist_ok=True)
    path = d / name
    if isinstance(body, bytes):
        path.write_bytes(body)
    else:
        path.write_text(body, encoding="utf-8")
    return path


def _declared(root: Path) -> tuple[list[tuple[str, str]], str, str]:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        got = critic._declared_reviewers(root)  # noqa: SLF001 - the reader under test
    return got, out.getvalue(), err.getvalue()


class DeclaredReviewersBadCardTests(unittest.TestCase):
    """AC1 and AC3: the reader skips the card, warns once naming it, and keeps reading."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_the_bad_card_is_skipped_and_the_valid_cards_beside_it_are_read(self) -> None:
        # `bad.md` sorts before `qa.md`, so a stop at the bad card loses the qa seat (mutant 2)
        _card(self.root, "seats", "bad.md", BAD)
        _card(self.root, "seats", "qa.md", "<!-- role: qa -->\n# Sam Eriksson - QA amigo\n")
        _card(self.root, "amigos", "product.md",
              "<!-- role: product -->\n# Lena Fischer - Product amigo\n")
        got, out, err = _declared(self.root)
        self.assertEqual([("qa", "Sam Eriksson"), ("product", "Lena Fischer")], got)
        self.assertEqual("", out)  # mutant 4: stdout is parsed by `sprint lane accept`
        self.assertEqual(
            "WARNING: seat card sdlc-studio/personas/seats/bad.md is not valid UTF-8, so it "
            "declares no seat: skipped\n", err)

    def test_the_warning_names_a_bad_card_under_amigos_by_its_own_folder(self) -> None:
        _card(self.root, "amigos", "bad.md", BAD)
        _card(self.root, "amigos", "qa.md", "<!-- role: qa -->\n# Sam Eriksson - QA amigo\n")
        got, _out, err = _declared(self.root)
        self.assertEqual([("qa", "Sam Eriksson")], got)
        self.assertIn("seat card sdlc-studio/personas/amigos/bad.md is not valid UTF-8", err)

    def test_the_warning_is_given_once_however_often_the_seats_are_resolved(self) -> None:
        _card(self.root, "seats", "bad.md", BAD)
        first, _out, err1 = _declared(self.root)
        second, _out, err2 = _declared(self.root)
        self.assertEqual([], first)
        self.assertEqual([], second)
        self.assertEqual(1, err1.count("bad.md"))
        self.assertEqual("", err2)  # mutant 5

    def test_a_second_project_in_the_same_process_is_told_about_its_own_card(self) -> None:
        # the same place in two projects: remembered by that place, the second goes unwarned
        _card(self.root, "seats", "bad.md", BAD)
        with tempfile.TemporaryDirectory() as other:
            _card(Path(other), "seats", "bad.md", BAD)
            _declared(self.root)
            _got, _out, err = _declared(Path(other))
        self.assertIn("sdlc-studio/personas/seats/bad.md is not valid UTF-8", err)  # mutant 6

    def test_a_card_that_cannot_be_read_at_all_is_still_skipped_silently(self) -> None:
        # a folder named like a card raises IsADirectoryError, an OSError: unchanged (mutant 7)
        (self.root / "sdlc-studio" / "personas" / "seats" / "dir.md").mkdir(parents=True)
        _card(self.root, "seats", "qa.md", "<!-- role: qa -->\n# Sam Eriksson - QA amigo\n")
        got, out, err = _declared(self.root)
        self.assertEqual([("qa", "Sam Eriksson")], got)
        self.assertEqual(("", ""), (out, err))


class RecordPastABadCardTests(unittest.TestCase):
    """AC2: the recorded steps, through the shipped `critic.py record`, no longer reproduce."""

    def _record(self, *valid_cards: str) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "sdlc-studio").mkdir()
            _card(root, "seats", "bad.md", BAD)
            for name in valid_cards:
                _card(root, "seats", name, "<!-- role: qa -->\n# Sam Eriksson - QA amigo\n")
            proc = subprocess.run(
                [sys.executable, str(SCRIPT), "record", "--unit", "US0001",
                 "--verdict", "approve", "--reviewer", "x (qa)", "--author", "y (engineering)"],
                cwd=root, capture_output=True, text=True, timeout=60, check=False)
            self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)  # mutant 1
            self.assertNotIn("Traceback", proc.stderr)
            self.assertNotIn("REFUSED", proc.stdout + proc.stderr)
            self.assertIn("recorded US0001 APPROVE", proc.stdout)
            self.assertNotIn("bad.md", proc.stdout)
            self.assertEqual(1, proc.stderr.count(
                "WARNING: seat card sdlc-studio/personas/seats/bad.md is not valid UTF-8"),
                proc.stderr)
            self.assertEqual("APPROVE", critic.verdict_for(root, "US0001")["verdict"])

    def test_the_recorded_steps_record_the_verdict_and_warn_naming_the_card(self) -> None:
        self._record()

    def test_a_valid_card_beside_it_still_draws_one_warning_only(self) -> None:
        # with a seat declared, `record` resolves the seats more than once (mutant 5)
        self._record("qa.md")


if __name__ == "__main__":
    unittest.main()
