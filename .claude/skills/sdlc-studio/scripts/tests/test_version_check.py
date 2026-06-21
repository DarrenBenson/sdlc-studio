"""Unit tests for version_check.py - skill version check + self-update signal (CR0044).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parent.parent / "version_check.py"


def _load():
    spec = importlib.util.spec_from_file_location("version_check", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["version_check"] = mod
    spec.loader.exec_module(mod)
    return mod


vc = _load()


def _skill(root: Path, version: str = "2.1.0") -> Path:
    sd = root / ".claude" / "skills" / "sdlc-studio"
    sd.mkdir(parents=True, exist_ok=True)
    (sd / "SKILL.md").write_text(
        f'---\nname: sdlc-studio\nmetadata:\n  version: "{version}"\n---\n# SDLC Studio\n',
        encoding="utf-8")
    return sd


def _boom():
    raise RuntimeError("network must not be called")


class SemverTests(unittest.TestCase):
    def test_gt(self) -> None:
        self.assertTrue(vc._gt("2.2.0", "2.1.0"))
        self.assertTrue(vc._gt("2.1.1", "2.1.0"))
        self.assertTrue(vc._gt("2.10.0", "2.9.0"))   # numeric, not lexical
        self.assertFalse(vc._gt("2.1.0", "2.1.0"))
        self.assertFalse(vc._gt("2.0.0", "2.1.0"))
        self.assertFalse(vc._gt(None, "2.1.0"))  # unparseable -> not greater

    def test_installed_version(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d), "2.1.0")
            self.assertEqual(vc.installed_version(sd), "2.1.0")


class CheckTests(unittest.TestCase):
    def test_update_available(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d))
            r = vc.check(sd, _fetch=lambda: "2.2.0", now=1000)
            self.assertEqual(r["status"], "update-available")
            self.assertEqual((r["installed"], r["latest"]), ("2.1.0", "2.2.0"))
            self.assertIn("2.2.0 is available", vc.notice(r))

    def test_up_to_date(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d))
            r = vc.check(sd, _fetch=lambda: "2.1.0", now=1000)
            self.assertEqual(r["status"], "up-to-date")
            self.assertIsNone(vc.notice(r))

    def test_offline_is_silent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d))
            r = vc.check(sd, _fetch=lambda: None, now=1000)
            self.assertEqual(r["status"], "offline")
            self.assertIsNone(vc.notice(r))

    def test_disabled_makes_no_network_call(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d))
            r = vc.check(sd, enabled=False, _fetch=_boom, now=1000)  # _boom proves no fetch
            self.assertEqual(r["status"], "disabled")

    def test_snooze_suppresses_until_newer(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d))
            vc.check(sd, _fetch=lambda: "2.2.0", now=1000)   # populates cache.latest
            vc.snooze(sd)                                     # dismiss 2.2.0
            r = vc.check(sd, _fetch=lambda: "2.2.0", now=1000)
            self.assertEqual(r["status"], "snoozed")
            # a newer release re-surfaces the notice
            r2 = vc.check(sd, _fetch=lambda: "2.3.0", now=10_000_000)  # stale -> refetch
            self.assertEqual(r2["status"], "update-available")

    def test_fetch_raising_is_treated_as_offline(self) -> None:
        # check() must be self-degrading: a raising fetcher -> offline, never propagates.
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d))
            r = vc.check(sd, enabled=True, _fetch=_boom, now=1000)
            self.assertEqual(r["status"], "offline")

    def test_offline_does_not_poison_cache(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d))
            vc.check(sd, _fetch=lambda: "2.2.0", now=1000)             # cache.latest = 2.2.0
            r = vc.check(sd, _fetch=lambda: None, now=10_000_000)      # stale -> offline fetch
            self.assertEqual(r["status"], "offline")
            self.assertEqual(vc._read_cache(sd).get("latest"), "2.2.0")  # not overwritten with None

    def test_corrupt_cache_does_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d))
            vc._cache_path(sd).parent.mkdir(parents=True, exist_ok=True)
            vc._cache_path(sd).write_text("{not json", encoding="utf-8")
            r = vc.check(sd, _fetch=lambda: "2.2.0", now=1000)  # starts fresh, no crash
            self.assertEqual(r["status"], "update-available")

    def test_ttl_cache_avoids_refetch(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d))
            vc.check(sd, _fetch=lambda: "2.2.0", now=1000)         # writes cache @1000
            r = vc.check(sd, _fetch=_boom, now=1000 + 3600)        # +1h, within 24h -> cached
            self.assertEqual(r["status"], "update-available")      # used cache, no fetch
            r2 = vc.check(sd, _fetch=lambda: "2.4.0", now=1000 + 3600 * 25)  # +25h -> refetch
            self.assertEqual(r2["latest"], "2.4.0")


class ScopeTests(unittest.TestCase):
    def test_agents(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = Path(d) / ".agents" / "skills" / "sdlc-studio"
            self.assertEqual(vc.scope(sd), "agents")

    def test_user_when_tooldir_in_home(self) -> None:
        with tempfile.TemporaryDirectory() as home:
            sd = Path(home) / ".claude" / "skills" / "sdlc-studio"
            sd.mkdir(parents=True)
            with mock.patch("pathlib.Path.home", return_value=Path(home)):
                self.assertEqual(vc.scope(sd), "user")

    def test_project_when_not_in_home(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            sd = Path(d) / "proj" / ".claude" / "skills" / "sdlc-studio"
            sd.mkdir(parents=True)
            with mock.patch("pathlib.Path.home", return_value=Path(d) / "elsewhere"):
                self.assertEqual(vc.scope(sd), "project")

    def test_project_checkout_under_home_is_project(self) -> None:
        # The tricky case: a repo cloned under $HOME must still be 'project', not 'user'.
        with tempfile.TemporaryDirectory() as home:
            sd = Path(home) / "code" / "proj" / ".claude" / "skills" / "sdlc-studio"
            sd.mkdir(parents=True)
            with mock.patch("pathlib.Path.home", return_value=Path(home)):
                self.assertEqual(vc.scope(sd), "project")

    def test_stale_cache_older_than_installed_refetches(self) -> None:
        # BG0024: a fresh cache whose latest is older than the installed version is provably stale
        # (a release shipped since the cache) -> refetch, never report the old latest as "latest".
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d), version="2.4.0")
            vc._write_cache(sd, {"latest": "2.1.0", "fetched_at": 1000})  # fresh-but-stale
            r = vc.check(sd, _fetch=lambda: "2.4.0", now=1000 + 3600)     # within 24h TTL
            self.assertEqual(r["latest"], "2.4.0")                         # refetched, not stale 2.1.0
            self.assertEqual(r["status"], "up-to-date")

    def test_fresh_cache_at_installed_version_still_avoids_refetch(self) -> None:
        # no over-refetch: a fresh cache equal to installed is trusted (_boom proves no fetch).
        with tempfile.TemporaryDirectory() as d:
            sd = _skill(Path(d), version="2.4.0")
            vc._write_cache(sd, {"latest": "2.4.0", "fetched_at": 1000})
            r = vc.check(sd, _fetch=_boom, now=1000 + 3600)
            self.assertEqual((r["latest"], r["status"]), ("2.4.0", "up-to-date"))


if __name__ == "__main__":
    unittest.main()
