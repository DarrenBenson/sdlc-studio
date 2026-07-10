"""US0082/CR0179: mechanical digests of closed artefacts, drift-checked, originals preserved."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, SCR / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


digest = _load("digest")

from unittest import mock

status = _load("status")
reconcile = _load("reconcile")
sdlc_md = digest.sdlc_md


def _many(root: Path, n_closed: int, n_open: int = 2, config: str | None = None) -> None:
    """n_closed closed + n_open open bug files (+ optional .config.yaml)."""
    d = root / "sdlc-studio" / "bugs"; d.mkdir(parents=True, exist_ok=True)
    for i in range(1, n_closed + 1):
        (d / f"BG{i:04d}-closed.md").write_text(
            f"# BG{i:04d}: closed {i}\n\n> **Status:** Closed\n> **Severity:** Low\n",
            encoding="utf-8")
    for j in range(1, n_open + 1):
        k = n_closed + j
        (d / f"BG{k:04d}-open.md").write_text(
            f"# BG{k:04d}: open {k}\n\n> **Status:** Open\n> **Severity:** Low\n",
            encoding="utf-8")
    if config is not None:
        cfg = root / "sdlc-studio" / ".config.yaml"
        cfg.write_text(config, encoding="utf-8")


def _closed_paths(root: Path):
    return {str(p) for p in (root / "sdlc-studio" / "bugs").glob("BG*-closed.md")}


class _ReadSpy:
    """Records every Path.read_text target so a test can assert an original was NOT re-read."""
    def __enter__(self):
        self.reads = []
        self._orig = Path.read_text
        spy = self
        def wrapped(pself, *a, **k):
            spy.reads.append(str(pself))
            return spy._orig(pself, *a, **k)
        self._patch = mock.patch.object(Path, "read_text", wrapped)
        self._patch.start()
        return self
    def __exit__(self, *exc):
        self._patch.stop()


def _bugs(root: Path) -> None:
    d = root / "sdlc-studio" / "bugs"; d.mkdir(parents=True)
    (d / "BG0001-closed.md").write_text(
        "# BG0001: a closed bug\n\n> **Status:** Closed\n> **Severity:** Low\n\n"
        "Relates to CR0042.\n", encoding="utf-8")
    (d / "BG0002-open.md").write_text(
        "# BG0002: still open\n\n> **Status:** Open\n> **Severity:** Low\n", encoding="utf-8")


class DigestTests(unittest.TestCase):
    def test_digests_only_closed_artefacts(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _bugs(root)
            res = digest.build(root)
            self.assertEqual(res["count"], 1)  # only the Closed bug
            e = res["digests"][0]
            self.assertEqual(e["id"], "BG0001")
            self.assertIn("CR0042", e["refs"])

    def test_originals_untouched(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _bugs(root)
            before = (root / "sdlc-studio" / "bugs" / "BG0001-closed.md").read_text(encoding="utf-8")
            digest.build(root)
            after = (root / "sdlc-studio" / "bugs" / "BG0001-closed.md").read_text(encoding="utf-8")
            self.assertEqual(before, after)  # digest never rewrites the source

    def test_drift_detected_and_cleared(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _bugs(root)
            self.assertTrue(digest.is_stale(root))   # nothing written yet
            digest.main(["build", "--root", str(root)])
            self.assertFalse(digest.is_stale(root))  # fresh
            # close another bug -> the digest is now stale
            (root / "sdlc-studio" / "bugs" / "BG0002-open.md").write_text(
                "# BG0002: now closed\n\n> **Status:** Closed\n> **Severity:** Low\n", encoding="utf-8")
            self.assertTrue(digest.is_stale(root))


class DigestReadPathTests(unittest.TestCase):
    """AC1: with 500+ closed artefacts digested, status reads the digest, not the originals."""
    def test_status_does_not_reread_closed_originals(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _many(root, 501)
            digest.main(["build", "--root", str(root)])
            self.assertTrue(digest.enabled(root))         # 501 >= default 500
            with _ReadSpy() as spy:
                res = status.count_by_status("bug", root)
            self.assertEqual(res["total"], 503)
            self.assertEqual(res["by_status"].get("Closed"), 501)
            reads = set(spy.reads)
            leaked = _closed_paths(root) & reads
            self.assertEqual(leaked, set(), f"{len(leaked)} closed originals were re-read")


class DigestCostTests(unittest.TestCase):
    """AC2: the read cost of status against digests is measurably lower than full-corpus."""
    def test_digest_reads_fewer_originals(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _many(root, 501)
            digest.main(["build", "--root", str(root)])
            with _ReadSpy() as spy:
                status.count_by_status("bug", root)
            with_digest = len(_closed_paths(root) & set(spy.reads))
            # remove the digest -> full-corpus read path
            (root / "sdlc-studio" / ".local" / "digests.json").unlink()
            with _ReadSpy() as spy2:
                status.count_by_status("bug", root)
            without_digest = len(_closed_paths(root) & set(spy2.reads))
            self.assertEqual(with_digest, 0)
            self.assertGreaterEqual(without_digest, 501)
            self.assertLess(with_digest, without_digest)   # measurably lower


class DigestDriftTests(unittest.TestCase):
    """AC3: digests are byte-stable and reconcile flags drift from the source batch."""
    def test_byte_stable_regeneration(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _many(root, 5)
            digest.main(["build", "--root", str(root)])
            p = root / "sdlc-studio" / ".local" / "digests.json"
            first = p.read_bytes()
            digest.main(["build", "--root", str(root)])
            self.assertEqual(p.read_bytes(), first)        # deterministic, byte-identical

    def test_reconcile_flags_and_clears_digest_drift(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _many(root, 5)
            self.assertIsNone(reconcile.digest_drift_advisory(root))  # no digest yet -> silent
            digest.main(["build", "--root", str(root)])
            self.assertIsNone(reconcile.digest_drift_advisory(root))  # fresh
            # close another bug after the digest was written
            (root / "sdlc-studio" / "bugs" / "BG0006-open.md").write_text(
                "# BG0006: now closed\n\n> **Status:** Closed\n> **Severity:** Low\n",
                encoding="utf-8")
            adv = reconcile.digest_drift_advisory(root)
            self.assertIsNotNone(adv)
            self.assertIn("digest.py build", adv)
            digest.main(["build", "--root", str(root)])
            self.assertIsNone(reconcile.digest_drift_advisory(root))  # regenerated -> clears


class DigestIdResolveTests(unittest.TestCase):
    """AC4: a closed artefact whose row lives in a digest still resolves by id to the original."""
    def test_find_by_id_returns_original(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _many(root, 501)
            # add an alias to one closed bug
            bp = root / "sdlc-studio" / "bugs" / "BG0001-closed.md"
            bp.write_text(bp.read_text(encoding="utf-8").replace(
                "> **Severity:** Low\n",
                "> **Severity:** Low\n> **Aliases:** BG9001\n"), encoding="utf-8")
            digest.main(["build", "--root", str(root)])
            found = sdlc_md.find_by_id(root, "BG0001")
            self.assertIsNotNone(found)
            self.assertEqual(found[0], bp)                 # the full original file
            self.assertEqual(found[1], "bug")
            aliased = sdlc_md.find_by_id(root, "BG9001")    # resolves via the alias
            self.assertIsNotNone(aliased)
            self.assertEqual(aliased[0], bp)


class DigestThresholdTests(unittest.TestCase):
    """AC5: below the size threshold the feature is dormant - no digest read, behaviour unchanged."""
    def test_below_threshold_is_dormant(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); _many(root, 3)               # 3 closed, default threshold 500
            digest.main(["build", "--root", str(root)])   # a digest exists but is under threshold
            self.assertFalse(digest.enabled(root))
            self.assertEqual(digest.status_by_id(root), {})
            with _ReadSpy() as spy:
                status.count_by_status("bug", root)
            # dormant: every closed original IS read, exactly as before digests existed
            self.assertTrue(_closed_paths(root) <= set(spy.reads))

    def test_config_override_lowers_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _many(root, 3, config="digests:\n  min_closed: 2\n")
            digest.main(["build", "--root", str(root)])
            self.assertEqual(digest.min_closed(root), 2)
            self.assertTrue(digest.enabled(root))         # 3 >= 2 -> active
            self.assertEqual(set(digest.status_by_id(root).values()), {"Closed"})

if __name__ == "__main__":
    unittest.main()
