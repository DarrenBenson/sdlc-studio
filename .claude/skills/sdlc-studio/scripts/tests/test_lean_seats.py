"""US0906: the review seats push back on a check that earns nothing.

Engineering pushes back on a new check, refusal, baseline or pin that names no measured yield or
retired constraint, and prefers fixing the failing code path; QA asks whether a check ever caught
a real defect and flags a lane whose refusals caught none; Product pushes back on a unit that
serves the machinery rather than a persona goal. Each holds in this repository's seats and in the
shipped amigo templates a greenfield project falls back to.

Driven through `persona_resolve.main resolve --render review`, the entry point a review brief
uses, once against this repository and once against a throwaway project with no seats.
"""
from __future__ import annotations

import contextlib
import io
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import loader  # noqa: E402

persona_resolve = loader.load_script("persona_resolve")

REPO = loader.SCRIPTS_DIR.parents[3]
SKILL = loader.SCRIPTS_DIR.parent


def _resolve(root: Path, seat: str, *extra: str) -> str:
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
        rc = persona_resolve.main(["resolve", "--seat", seat, "--render", "review",
                                   "--root", str(root), *extra])
    if rc != 0:
        raise AssertionError(f"resolve --seat {seat} exited {rc}: {out.getvalue()}")
    return out.getvalue()


def _bullets(charter: str, heading: str) -> list[str]:
    """The bullets under `## <heading>`, each joined across its wrapped lines."""
    m = re.search(rf"^## {re.escape(heading)}\b.*?\n(.*?)(?=^## |\Z)", charter, re.M | re.S)
    if not m:
        return []
    return [" ".join(b.split()) for b in re.split(r"^- ", m.group(1), flags=re.M)[1:]]


class RatchetWatchTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.greenfield = Path(tmp.name)
        (self.greenfield / "sdlc-studio").mkdir()

    def _sources(self, seat: str):
        """(label, review-render charter) for this repository's seat and the shipped template,
        each checked to have resolved to the card it names."""
        for label, root, card in (
                ("this repository", REPO, REPO / "sdlc-studio" / "personas" / "seats" / f"{seat}.md"),
                ("greenfield", self.greenfield, SKILL / "templates" / "personas" / "amigos"
                 / f"{seat}.md")):
            self.assertEqual(str(card.resolve()), _resolve(root, seat, "--path-only").strip())
            yield label, _resolve(root, seat)

    def _assert_pushes_back(self, seat: str, *terms: str) -> None:
        for label, charter in self._sources(seat):
            with self.subTest(seat=seat, source=label):
                hits = [b for b in _bullets(charter, "Pushes Back When")
                        if all(t.lower() in b.lower() for t in terms)]
                self.assertEqual(1, len(hits), f"no single Pushes Back When bullet in the {label} "
                                 f"{seat} seat names all of {terms}")

    def test_engineering_pushes_back_on_an_unearned_check(self) -> None:
        """MUTANT: add the line to this repository's seat only, or to the Lens rather than
        Pushes Back When - a greenfield review, or the seat's push-back list, never carries it."""
        self._assert_pushes_back("engineering", "check", "refusal", "baseline", "pin",
                                 "measured yield", "retired constraint", "fix the failing code path")

    def test_qa_and_product_watch_the_ratchet(self) -> None:
        """MUTANT: QA asks what a check caught but never flags the noise lane, or Product's line
        lands in one source only - half the ratchet watch ships."""
        self._assert_pushes_back("qa", "ever caught a real defect", "lane whose refusals caught none")
        self._assert_pushes_back("product", "serves the machinery", "persona goal")


if __name__ == "__main__":
    unittest.main()
