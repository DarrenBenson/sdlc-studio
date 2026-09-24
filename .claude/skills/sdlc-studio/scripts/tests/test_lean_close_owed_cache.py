"""US0894: the close-owed report walks the artefact corpus once per call, not once per epic.

`owed` asked `children_of` and `find_by_id` once per terminal epic, and each walked and read the
whole tree: 201 calls and 515k reads on this repository, 55 s for one `close_owed.py detect`.
The report now runs inside `sdlc_md.corpus_cache()`, the scoped sweep `status` already uses.
MUTANTS: drop the sweep (every epic re-reads the tree); hold one sweep open for the process (an
artefact written between two calls goes unseen - retros are never cached, so the test's new bug
BG0003 and its no-sweep-left-open assertion are what catch it); change any answer while caching (the report is no
longer byte-identical to the uncached walk).
"""
import collections
import contextlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import close_owed  # noqa: E402
from lib import sdlc_md  # noqa: E402


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _epic(root: Path, eid: str, breakdown: tuple = ()) -> None:
    boxes = "".join(f"- [x] {i} thing\n" for i in breakdown)
    _write(root / "sdlc-studio" / "epics" / f"{eid}-e.md",
           f"# {eid}: An epic\n\n> **Status:** Done\n> **Derived Point Total:** 4\n\n"
           f"## Story Breakdown\n\n{boxes}")


def _story(root: Path, sid: str, epic: str) -> None:
    _write(root / "sdlc-studio" / "stories" / f"{sid}-s.md",
           f"# {sid}: A story\n\n> **Status:** Done\n> **Epic:** {epic}\n> **Points:** 2\n")


def _bug(root: Path, bid: str) -> None:
    _write(root / "sdlc-studio" / "bugs" / f"{bid}-b.md",
           f"# {bid}: A bug\n\n> **Status:** Fixed\n> **Points:** 1\n")


def _retro(root: Path, rid: str, batch: list) -> None:
    _write(root / "sdlc-studio" / "retros" / f"{rid}-r.md",
           f"# {rid}: a sprint\n\n> **Date:** 2026-02-01\n> **Batch:** {', '.join(batch)}\n\n"
           "## Delivered\n- shipped\n")


def _baseline(root: Path, grandfathered: list) -> None:
    _write(root / close_owed.BASELINE_FILE,
           json.dumps({"stamped": "2026-01-01", "grandfathered": grandfathered}))


def _twenty_epics(root: Path) -> None:
    """20 terminal epics with three covered stories each, so every epic takes the per-epic
    children path, plus two uncovered bugs so the per-unit lookups run too."""
    stories = []
    for e in range(1, 21):
        eid = f"EP{e:04d}"
        ids = [f"US{e * 10 + s:04d}" for s in range(3)]
        _epic(root, eid, tuple(ids))
        for sid in ids:
            _story(root, sid, eid)
        stories += ids
    _bug(root, "BG0001")
    _bug(root, "BG0002")
    _retro(root, "RETRO0001", stories)
    _baseline(root, [])


def _cases(root: Path) -> None:
    """Covered, grandfathered, epic-inherited, dead-id and owed units side by side."""
    _story(root, "US0001", "EP0009")                     # covered by the retro
    _story(root, "US0002", "EP0009")                     # grandfathered by the baseline
    _epic(root, "EP0001", ("US0003", "US0004", "US9999", "CR0001"))  # inherits; two dead ids
    _story(root, "US0003", "EP0001")
    _story(root, "US0004", "EP0001")
    _write(root / "sdlc-studio" / "change-requests" / "CR0001-c.md",
           "# CR0001: a request\n\n> **Status:** Complete\n> **Size:** S\n")
    _epic(root, "EP0002", ("US0005", "US0006"))          # one child uncovered: owed
    _story(root, "US0005", "EP0002")
    _story(root, "US0006", "EP0002")
    _bug(root, "BG0001")                                 # uncovered: owed
    _retro(root, "RETRO0001", ["US0001", "US0003", "US0004", "US0005"])
    _baseline(root, ["US0002"])


def _uncached():
    """Turn the sweep off: `owed` then runs exactly the walk it ran before the cache."""
    return mock.patch.object(close_owed.sdlc_md, "corpus_cache", contextlib.nullcontext)


class CloseOwedCacheTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="close_owed_cache_"))
        self.addCleanup(shutil.rmtree, self.root, True)
        self.assertFalse(sdlc_md.corpus_cache_active(), "a sweep leaked in from another test")

    def _count_reads(self, call) -> collections.Counter:
        reads: collections.Counter = collections.Counter()
        real = Path.read_text
        base = str(self.root / "sdlc-studio")

        def spy(path, *a, **k):
            if str(path).startswith(base) and path.suffix == ".md":
                reads[str(path)] += 1
            return real(path, *a, **k)

        with mock.patch.object(Path, "read_text", spy):
            call()
        return reads

    def test_one_call_walks_the_corpus_once(self) -> None:
        _twenty_epics(self.root)
        reads = self._count_reads(lambda: close_owed.owed(self.root))
        files = len(list((self.root / "sdlc-studio").rglob("*.md")))
        self.assertEqual(files, len(reads), "the spy did not see every artefact read")
        # the artefact tree `children_of` and `find_by_id` walk: each file read once per call
        retros = str(self.root / "sdlc-studio" / "retros")
        twice = {Path(p).name: n for p, n in reads.items() if n > 1 and not p.startswith(retros)}
        self.assertEqual({}, twice, f"{len(twice)} artefact(s) re-read within one owed() call")
        # the retro ledger sits outside that tree and is read by the report's own passes, a
        # fixed number per call - never once per epic
        retro_reads = [n for p, n in reads.items() if p.startswith(retros)]
        self.assertTrue(retro_reads, "the retro ledger was never read")
        self.assertLess(max(retro_reads), 20, "the retro ledger was re-read once per epic")
        # the control: without the sweep the same call re-reads the tree once per epic, so the
        # fixture does reach the per-epic path the cache exists for
        with _uncached():
            uncached = self._count_reads(lambda: close_owed.owed(self.root))
        self.assertGreaterEqual(max(uncached.values()), 20,
                                "the fixture never drove the per-epic walk")

    def test_the_report_is_byte_identical_to_the_uncached_walk(self) -> None:
        _cases(self.root)

        def detect() -> str:
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                close_owed.main(["--root", str(self.root), "detect", "--format", "json"])
            return out.getvalue()

        cached = detect()
        with _uncached():
            uncached = detect()
        self.assertEqual(uncached, cached)
        report = json.loads(cached)
        # every case the fixture sets up is present in the answer being compared
        self.assertEqual([["BG0001", "bug"], ["EP0002", "epic"], ["US0006", "story"]],
                         report["owed"])
        self.assertEqual(1, report["grandfathered"])
        self.assertEqual([["EP0001", "CR0001"], ["EP0001", "US9999"]], report["dead_breakdown_ids"])

    def test_a_write_between_calls_is_seen(self) -> None:
        _twenty_epics(self.root)
        first = {cid for cid, _ in close_owed.owed(self.root)["owed"]}
        self.assertEqual({"BG0001", "BG0002"}, first)
        _retro(self.root, "RETRO0002", ["BG0001"])  # the retro covers an owed unit
        _bug(self.root, "BG0003")                    # and an artefact the sweep walked changes
        second = {cid for cid, _ in close_owed.owed(self.root)["owed"]}
        self.assertEqual({"BG0002", "BG0003"}, second,
                         "the second call answered from the first call's corpus")
        self.assertFalse(sdlc_md.corpus_cache_active(), "owed() left its sweep open")


if __name__ == "__main__":
    unittest.main()
