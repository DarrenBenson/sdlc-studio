"""persona_memory.py: each persona's evidenced learnings, kept in a committed memory file.

The store is `sdlc-studio/personas/memory/<persona>.md`, keyed by a seat's declared role or a
user persona's card stem. These tests drive the shipped CLI (`main`) against a git fixture.
"""
from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import gitutil  # noqa: E402
import lessons  # noqa: E402
from lib import sdlc_md  # noqa: E402


def _load():
    spec = importlib.util.spec_from_file_location("persona_memory", SCRIPTS / "persona_memory.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


pm = _load()

SEAT_CARD = "<!-- role: {role} -->\n# Sam - {role} seat\n\n## Lens\n\nx\n"
USER_CARD = "# Maya Okafor\n\n## Who They Are\n\nA founder engineer.\n"


def entry(id_: str, persona: str, title: str, body: str, state: str,
          added: str = "2026-11-01", review_by: str = "2027-01-30") -> str:
    return (f"## {id_}: {title}\n\n- **Persona:** {persona}\n- **Evidence:** US0001\n"
            f"- **Added:** {added}\n- **Review-by:** {review_by}\n- **State:** {state}\n\n"
            f"{body}\n")


class _Fixture(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        personas = self.root / "sdlc-studio" / "personas"
        (personas / "seats").mkdir(parents=True)
        for role in ("qa", "product"):
            (personas / "seats" / f"{role}.md").write_text(SEAT_CARD.format(role=role),
                                                           encoding="utf-8")
        (personas / "maya-okafor-founder-engineer.md").write_text(USER_CARD, encoding="utf-8")
        stories = self.root / "sdlc-studio" / "stories"
        stories.mkdir(parents=True)
        (stories / "US0001-a-story.md").write_text(
            "# US0001: A story\n\n> **Status:** Done\n", encoding="utf-8")
        gitutil.git(["init", "-q"], self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def run_cli(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = pm.main(["--root", str(self.root), *argv])
        return rc, out.getvalue(), err.getvalue()

    def memory(self, key: str) -> Path:
        return self.root / "sdlc-studio" / "personas" / "memory" / f"{key}.md"


class PersonaMemoryStoreTests(_Fixture):
    def test_add_writes_a_stamped_proposed_learning_with_a_unique_id(self):
        for key in ("qa", "maya-okafor-founder-engineer"):
            rc, _, err = self.run_cli("add", "--persona", key, "--title", f"Learned by {key}",
                                      "--body", "A retry loop hides a race.",
                                      "--evidence", "US0001")
            self.assertEqual(rc, 0, err)
        today = sdlc_md.now_date()
        # Ids are unique across every memory file, so the second persona's first learning is
        # M-0002, never a second M-0001 an approval or a strike could not tell apart.
        for key, want in (("qa", "M-0001"), ("maya-okafor-founder-engineer", "M-0002")):
            text = self.memory(key).read_text(encoding="utf-8")
            self.assertIn(f"## {want}: Learned by {key}", text)
            [e] = pm.read_store(self.memory(key))
            self.assertEqual(e["id"], want)
            self.assertEqual(e["fields"]["persona"], key)
            self.assertEqual(e["fields"]["evidence"], "US0001")
            self.assertEqual(e["fields"]["added"], today)
            self.assertEqual(e["fields"]["review-by"], lessons.add_days(today, 90))
            self.assertEqual(e["fields"]["state"], "proposed")
            self.assertIn("A retry loop hides a race.", e["body"])
        # Every field a later writer sets round-trips through the one helper, which is
        # lessons.upsert_field and not a second copy of it.
        later = ("Approved-by", "Addresses", "Listed-in", "Struck", "Retired")
        self.assertEqual(set(later) - set(pm.FIELDS), set())
        with mock.patch.object(pm.lessons, "upsert_field", wraps=lessons.upsert_field) as spy:
            for name in later:
                pm.set_field(self.root, "M-0001", name, f"value of {name}")
        self.assertEqual([c.args[1] for c in spy.call_args_list], list(later))
        [e] = pm.read_store(self.memory("qa"))
        for name in later:
            self.assertEqual(e["fields"][name.lower()], f"value of {name}")
        self.assertEqual(e["fields"]["state"], "proposed")
        self.assertEqual(pm.read_store(self.memory("maya-okafor-founder-engineer"))[0]["id"],
                         "M-0002")
        with self.assertRaises(pm.MemoryRefusal):
            pm.set_field(self.root, "M-0001", "Colour", "blue")
        with self.assertRaises(pm.MemoryRefusal):
            pm.set_field(self.root, "M-0009", "Struck", "x")

    def test_an_unevidenced_unknown_ambiguous_or_ignored_add_is_refused(self):
        base = ("--title", "t", "--body", "b")
        cases = [
            ("no evidence", ("add", "--persona", "qa", *base), [], "evidence"),
            ("unresolved", ("add", "--persona", "qa", *base, "--evidence", "US9999",
                            "--evidence", "D9999"), [], "US9999"),
            ("unknown", ("add", "--persona", "nobody", *base, "--evidence", "US0001"), [],
             "nobody"),
            ("ambiguous", ("add", "--persona", "qa", *base, "--evidence", "US0001"),
             ["card"], "both"),
            # The rule itself, as `git check-ignore -v` names it (source, line, pattern): the
            # bare directory is also in the path the message names, so it pins nothing.
            ("ignored", ("add", "--persona", "qa", *base, "--evidence", "US0001"),
             ["ignore"], "rule .gitignore:2:sdlc-studio/personas/memory/"),
        ]
        for name, argv, setup, reason in cases:
            with self.subTest(name):
                card = self.root / "sdlc-studio" / "personas" / "qa.md"
                ignore = self.root / ".gitignore"
                if "card" in setup:
                    card.write_text(USER_CARD, encoding="utf-8")
                if "ignore" in setup:
                    ignore.write_text("*.tmp\nsdlc-studio/personas/memory/\n", encoding="utf-8")
                try:
                    rc, out, err = self.run_cli(*argv)
                finally:
                    card.unlink(missing_ok=True)
                    ignore.unlink(missing_ok=True)
                self.assertEqual(rc, 2, out + err)
                self.assertIn(reason, err)
                mem = self.root / "sdlc-studio" / "personas" / "memory"
                self.assertEqual(sorted(mem.glob("*")) if mem.exists() else [], [])
        # An unresolved decision id is named too, not only an artefact id.
        rc, _, err = self.run_cli("add", "--persona", "qa", *base, "--evidence", "D9999")
        self.assertEqual(rc, 2)
        self.assertIn("D9999", err)
        # Positive control: the same add, evidenced and unambiguous, writes.
        rc, _, err = self.run_cli("add", "--persona", "qa", *base, "--evidence", "US0001")
        self.assertEqual(rc, 0, err)
        self.assertTrue(self.memory("qa").is_file())

    def test_list_and_recall_read_one_personas_memory(self):
        mem = self.memory("qa").parent
        mem.mkdir(parents=True)
        self.memory("qa").write_text(
            "# Persona Memory: qa\n\n"
            + entry("M-0001", "qa", "A race in the retry loop", "Retries hid it.", "approved")
            + "\n" + entry("M-0002", "qa", "Fixture order", "A race window opened.", "proposed",
                           review_by="2027-03-01")
            + "\n" + entry("M-0003", "qa", "Docs drift", "Pages go stale.", "approved"),
            encoding="utf-8")
        self.memory("product").write_text(
            "# Persona Memory: product\n\n"
            + entry("M-0004", "product", "Race to market", "Ship first.", "approved"),
            encoding="utf-8")
        rc, out, err = self.run_cli("list", "--persona", "qa", "--query", "race")
        self.assertEqual(rc, 0, err)
        self.assertIn("M-0001", out)
        self.assertIn("M-0002", out)
        self.assertNotIn("M-0003", out)
        self.assertNotIn("M-0004", out)
        line1 = next(ln for ln in out.splitlines() if "M-0001" in ln)
        self.assertIn("approved", line1)
        self.assertIn("2027-01-30", line1)
        line2 = next(ln for ln in out.splitlines() if "M-0002" in ln)
        self.assertIn("proposed", line2)
        self.assertIn("2027-03-01", line2)
        for verb in ("list", "recall"):
            with self.subTest(verb):
                rc, out, err = self.run_cli(verb, "--persona", "qa", "--query", "RACE",
                                            "--format", "json")
                self.assertEqual(rc, 0, err)
                rows = json.loads(out)["learnings"]
                self.assertEqual([r["id"] for r in rows], ["M-0001", "M-0002"])
                self.assertEqual([(r["state"], r["horizon"]) for r in rows],
                                 [("approved", "2027-01-30"), ("proposed", "2027-03-01")])
        rc, out, _ = self.run_cli("list", "--persona", "qa", "--format", "json")
        self.assertEqual([r["id"] for r in json.loads(out)["learnings"]],
                         ["M-0001", "M-0002", "M-0003"])

    def test_memory_files_are_never_read_as_misplaced_persona_cards(self):
        personas = self.root / "sdlc-studio" / "personas"
        (personas / "maya-okafor-founder-engineer.md").unlink()
        self.memory("qa").parent.mkdir(parents=True)
        self.memory("qa").write_text(
            "# Persona Memory: qa\n\n" + entry("M-0001", "qa", "A", "b", "proposed"),
            encoding="utf-8")

        def personas_out() -> str:
            proc = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate.py"), "personas",
                 "--root", str(self.root)], capture_output=True, text=True, check=False)
            return proc.stdout + proc.stderr

        out = personas_out()
        self.assertNotIn("persona-layout", out)
        self.assertNotIn("not in the flat Cooper layout", out)
        # Positive control: a nested card outside the canonical homes still trips it.
        (personas / "team").mkdir()
        (personas / "team" / "x.md").write_text("# X\n\n## Who They Are\n\nx\n", encoding="utf-8")
        self.assertIn("not in the flat Cooper layout", personas_out())


class PersonaMemoryAddGuardTests(_Fixture):
    """`add` writes only what its own reader reads back, and cites only a run that exists."""

    def test_a_body_the_reader_would_refuse_is_refused_and_later_adds_still_work(self):
        rc, _, err = self.run_cli("add", "--persona", "qa", "--title", "first",
                                  "--body", "b", "--evidence", "US0001")
        self.assertEqual(rc, 0, err)
        before = self.memory("qa").read_text(encoding="utf-8")
        bodies = (("a level-two heading line", "Do this.\n## Steps\n1. one",
                   "'## Steps' is a level-two heading"),
                  ("a heading once stripped", "  ## Steps\nthen more",
                   "'## Steps' is a level-two heading"),
                  ("an entry heading with no State", "x\n## M-0042: smuggled\ny", "M-0042"),
                  ("a second State the reader takes", "x\n- **State:** a\n- **State:** b",
                   "State"))
        for name, body, reason in bodies:
            with self.subTest(name):
                rc, out, err = self.run_cli("add", "--persona", "product", "--title", "t",
                                            "--body", body, "--evidence", "US0001")
                self.assertEqual(rc, 2, out + err)
                self.assertIn(reason, err)
                self.assertFalse(self.memory("product").exists())
                self.assertEqual(self.memory("qa").read_text(encoding="utf-8"), before)
        # The store stays readable: the next add, for any persona, still writes and reads back.
        rc, _, err = self.run_cli("add", "--persona", "qa", "--title", "second",
                                  "--body", "b", "--evidence", "US0001")
        self.assertEqual(rc, 0, err)
        self.assertEqual([e["id"] for e in pm.read_store(self.memory("qa"))],
                         ["M-0001", "M-0002"])
        # Positive control: a level-three heading is prose the reader keeps.
        rc, _, err = self.run_cli("add", "--persona", "product", "--title", "t",
                                  "--body", "Do this.\n### Steps\n1. one", "--evidence", "US0001")
        self.assertEqual(rc, 0, err)
        [e] = pm.read_store(self.memory("product"))
        self.assertIn("### Steps", e["body"])

    def test_run_evidence_matches_a_whole_run_id_case_sensitively(self):
        reports = self.root / "sdlc-studio" / "reports"
        reports.mkdir(parents=True)
        (reports / "RPT0001-run.md").write_text(
            "# RPT0001\n\n| Run | RUN-01ABCDEF |\n\nSigned over run-01lower, not RUN-02Xyz "
            "or XRUN-03A.\n", encoding="utf-8")
        for token in ("RUN-0", "RUN-01A", "RUN-01ABCDEFG", "RUN-01LOWER", "RUN-02X", "RUN-03A"):
            with self.subTest(token):
                rc, out, err = self.run_cli("add", "--persona", "qa", "--title", "t",
                                            "--body", "b", "--evidence", token)
                self.assertEqual(rc, 2, out + err)
                self.assertIn(token, err)
                self.assertFalse(self.memory("qa").exists())
        # Positive control: the whole id a report names resolves.
        rc, _, err = self.run_cli("add", "--persona", "qa", "--title", "t", "--body", "b",
                                  "--evidence", "RUN-01ABCDEF")
        self.assertEqual(rc, 0, err)
        self.assertEqual(pm.read_store(self.memory("qa"))[0]["fields"]["evidence"],
                         "RUN-01ABCDEF")

    def test_every_cited_id_must_resolve_and_a_verdict_reference_needs_both_halves(self):
        # One resolvable id does not carry an unresolvable one beside it.
        rc, out, err = self.run_cli("add", "--persona", "qa", "--title", "t", "--body", "b",
                                    "--evidence", "US0001", "--evidence", "US9999")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("--evidence US9999 resolves", err)
        self.assertFalse(self.memory("qa").exists())
        # A verdict reference resolves only when the unit is an artefact AND the ledger holds
        # that round: US0001 has no round 9, and US9999's round 1 names no artefact.
        ledger = [{"unit": "US0001", "round": 1}, {"unit": "US9999", "round": 1}]
        with mock.patch("critic.read_verdicts", return_value=ledger):
            for token in ("US0001 r9", "US9999 r1"):
                with self.subTest(token):
                    rc, out, err = self.run_cli("add", "--persona", "qa", "--title", "t",
                                                "--body", "b", "--evidence", token)
                    self.assertEqual(rc, 2, out + err)
                    self.assertIn(f"--evidence {token} resolves", err)
                    self.assertFalse(self.memory("qa").exists())
            # Positive control: both halves hold, so it writes.
            rc, _, err = self.run_cli("add", "--persona", "qa", "--title", "t", "--body", "b",
                                      "--evidence", "US0001 r1")
        self.assertEqual(rc, 0, err)
        self.assertEqual(pm.read_store(self.memory("qa"))[0]["fields"]["evidence"], "US0001 r1")


class PersonaMemoryReadBackTests(_Fixture):
    """`add` writes only a learning its reader reads back as exactly what it stamped: one new
    entry, the same id and title, every field it set and no other, and the prose as given."""

    FORGERIES = (
        ("two State lines", "x\n- **State:** approved\n- **State:** approved"),
        ("a doubled Review-by", "x\n- **Review-by:** 2099-01-01\n- **Review-by:** 2099-01-01"),
        ("a tab-spaced entry heading with its own State",
         "x\n##\tM-0099: Smuggled\n- **State:** approved"),
        ("one State line", "x\n- **State:** approved"),
        ("a field line the stamp never sets", "x\n- **Why:** because"),
    )

    def assert_nothing_listed(self) -> None:
        self.assertFalse(self.memory("qa").exists())
        rc, out, _ = self.run_cli("list", "--persona", "qa", "--format", "json")
        self.assertEqual((rc, json.loads(out)["learnings"]), (0, []))

    def test_a_body_that_would_read_back_as_another_entry_or_field_is_refused(self):
        for name, body in self.FORGERIES:
            with self.subTest(name):
                rc, out, err = self.run_cli("add", "--persona", "qa", "--title", "t",
                                            "--body", body, "--evidence", "US0001")
                self.assertEqual(rc, 2, out + err)
                self.assertNotIn("M-0099", out)
                self.assert_nothing_listed()

    def test_the_read_back_comparison_refuses_what_no_shape_guard_names(self):
        # Without the field-line guard, the comparison alone still refuses every forgery,
        # naming what the reader would read differently.
        with mock.patch.object(pm, "_field_line", return_value=""):
            for name, body in self.FORGERIES:
                with self.subTest(name):
                    rc, out, err = self.run_cli("add", "--persona", "qa", "--title", "t",
                                                "--body", body, "--evidence", "US0001")
                    self.assertEqual(rc, 2, out + err)
                    self.assertIn("would not read back", err)
                    self.assert_nothing_listed()
            # A State on each side of a smuggled heading parses, as two entries.
            rc, out, err = self.run_cli(
                "add", "--persona", "qa", "--title", "t", "--evidence", "US0001", "--body",
                "x\n- **State:** approved\n##\tM-0099: Smuggled\n- **State:** approved")
            self.assertEqual(rc, 2, out + err)
            self.assertIn("reads back as M-0001, M-0099, not M-0001", err)
            self.assert_nothing_listed()
        # An evidence value the reader splits: a verdict reference whose gap is a line break
        # resolves, but its Evidence field reads back as the unit alone.
        with mock.patch("critic.read_verdicts", return_value=[{"unit": "US0001", "round": 1}]):
            rc, out, err = self.run_cli("add", "--persona", "qa", "--title", "t", "--body", "b",
                                        "--evidence", "US0001\nr1")
            self.assertEqual(rc, 2, out + err)
            self.assertIn("evidence reads back as 'US0001'", err)
            self.assert_nothing_listed()
            # Positive control: a body the reader keeps whole, and a plain reference, write.
            body = "Do this.\n\n- a list item\n##\tNotes, not an entry\n### Steps"
            rc, _, err = self.run_cli("add", "--persona", "qa", "--title", "t", "--body", body,
                                      "--evidence", "US0001 r1")
        self.assertEqual(rc, 0, err)
        [e] = pm.read_store(self.memory("qa"))
        self.assertEqual((e["id"], e["fields"]["state"], e["fields"]["evidence"]),
                         ("M-0001", "proposed", "US0001 r1"))
        self.assertEqual(pm.prose_of(e), body)

    def test_the_comparison_names_a_title_or_a_field_the_stamp_did_not_write(self):
        # The heading writer normalises the title, and a field line the stamp never set also
        # changes the prose, so a CLI case is refused by another half too: pin these directly.
        stamp = {"id": "M-0001", "title": "t", "fields": {"state": "proposed"},
                 "body": "- **State:** proposed\n\nprose"}
        same = {**stamp, "fields": dict(stamp["fields"])}
        self.assertEqual(pm._read_back_drift([same], [stamp], "prose"), "")
        retitled = {**same, "title": "u"}
        self.assertIn("title reads back as 'u'",
                      pm._read_back_drift([retitled], [stamp], "prose"))
        extra = {**same, "fields": {"state": "proposed", "why": "x"}}
        self.assertIn("why reads back as 'x', not '(absent)'",
                      pm._read_back_drift([extra], [stamp], "prose"))


class PersonaMemoryCrossFileIdTests(_Fixture):
    """An id two memory files hold is refused by every write that names or mints one, never
    resolved to whichever file is read first."""

    def test_an_id_two_files_hold_is_refused_by_set_field_add_and_the_close_listing(self):
        mem = self.memory("qa").parent
        mem.mkdir(parents=True)
        self.memory("qa").write_text(
            "# Persona Memory: qa\n\n" + entry("M-0001", "qa", "A", "b", "approved"),
            encoding="utf-8")
        self.memory("product").write_text(
            "# Persona Memory: product\n\n" + entry("M-0001", "product", "B", "c", "approved"),
            encoding="utf-8")
        before = {p: p.read_text(encoding="utf-8") for p in mem.glob("*.md")}
        with self.assertRaises(pm.MemoryRefusal) as ctx:
            pm.set_field(self.root, "M-0001", "Struck", "x")
        for named in ("M-0001", "product.md", "qa.md"):
            self.assertIn(named, str(ctx.exception))
        rc, out, err = self.run_cli("add", "--persona", "qa", "--title", "t", "--body", "b",
                                    "--evidence", "US0001")
        self.assertEqual(rc, 2, out + err)
        self.assertIn("M-0001", err)
        with self.assertRaises(pm.StoreError):
            pm.pending_listing(self.root)
        self.assertEqual({p: p.read_text(encoding="utf-8") for p in mem.glob("*.md")}, before)
        # Positive control: renumber one and every write works again.
        self.memory("product").write_text(
            "# Persona Memory: product\n\n" + entry("M-0002", "product", "B", "c", "approved"),
            encoding="utf-8")
        self.assertEqual(pm.set_field(self.root, "M-0001", "Struck", "x")["fields"]["persona"],
                         "qa")
        rc, out, err = self.run_cli("add", "--persona", "qa", "--title", "t", "--body", "b",
                                    "--evidence", "US0001")
        self.assertEqual(rc, 0, err)
        self.assertIn("M-0003", out)


class PersonaMemoryFieldsFileTests(_Fixture):
    """`add --fields-file` takes the prose from a JSON document no shell has touched."""

    def test_the_prose_comes_verbatim_from_a_fields_file_and_a_flag_still_wins(self):
        doc = self.root / "learning.json"
        body = 'Run `rm -rf "$HOME"/x` only after $(pwd) is checked; a "quoted" race.'
        doc.write_text(json.dumps({"title": "Shell text survives", "body": body}),
                       encoding="utf-8")
        rc, _, err = self.run_cli("add", "--persona", "qa", "--fields-file", str(doc),
                                  "--evidence", "US0001")
        self.assertEqual(rc, 0, err)
        [e] = pm.read_store(self.memory("qa"))
        self.assertEqual((e["title"], pm.prose_of(e)), ("Shell text survives", body))
        rc, _, err = self.run_cli("add", "--persona", "qa", "--fields-file", str(doc),
                                  "--title", "Flag title", "--evidence", "US0001")
        self.assertEqual(rc, 0, err)
        self.assertEqual([x["title"] for x in pm.read_store(self.memory("qa"))],
                         ["Shell text survives", "Flag title"])

    def test_a_missing_field_or_a_bad_document_is_refused_and_nothing_written(self):
        cases = (("no body", {"title": "t"}, "body"),
                 ("unknown key", {"title": "t", "body": "b", "colour": "x"}, "colour"))
        for name, payload, reason in cases:
            with self.subTest(name):
                doc = self.root / "learning.json"
                doc.write_text(json.dumps(payload), encoding="utf-8")
                rc, out, err = self.run_cli("add", "--persona", "qa", "--fields-file",
                                            str(doc), "--evidence", "US0001")
                self.assertEqual(rc, 2, out + err)
                self.assertIn(reason, err)
                self.assertFalse(self.memory("qa").exists())


if __name__ == "__main__":
    unittest.main()
