"""Unit tests for the Three-Amigos consult baked into refine and triage (RFC0039, EP0040).

The consult machinery (`resolve_consult`/`frame`) existed but was unwired; these tests pin the
wiring:

- the shared resolver: open questions -> named seat cards, lead-first, --skip-personas
  byte-equivalent (US0143);
- refine surfaces questions to the resolved seats, engineering-led (US0144);
- triage surfaces questions to the resolved seats, QA-led (US0145);
- the consult is recorded on the request/Issue as an audit trail (US0146);
- graceful degradation to the shipped defaults, the RenderError on a broken project seat, and the
  author!=reviewer independence floor (US0147).

Run from the repo root:
    python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / filename)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sys.path.insert(0, str(_SCRIPTS))
from lib import sdlc_md  # noqa: E402
persona_resolve = _load("persona_resolve", "persona_resolve.py")
artifact = _load("artifact", "artifact.py")
refine = _load("refine", "refine.py")
triage = _load("triage", "triage.py")
reconcile = _load("reconcile", "reconcile.py")
validate = _load("validate", "validate.py")

REPO = str(Path(__file__).resolve().parents[4])   # the real repo, for the shipped default cards


def _enforce(root: Path) -> None:
    p = root / "sdlc-studio" / ".config.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("two_backlog:\n  enforce: true\n", encoding="utf-8")


def _touch(root: Path, *rel: str) -> None:
    for r in rel:
        p = root / r
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("", encoding="utf-8")


def _cr(root: Path) -> str:
    artifact.new(root, "cr", "A change", {"size": "M", "priority": "P2", "affects": "src/a.py",
                 "ctype": "Feature", "summary": "s", "impact": "i", "acs": ["a"]})
    return "CR0001"


def _issue(root: Path) -> str:
    return artifact.new(root, "issue", "Checkout 500s",
                        {"size": "M", "severity": "High", "summary": "s"})["id"]


# --- US0143: the shared resolver -------------------------------------------------------------

class ResolverTests(unittest.TestCase):
    def test_panel_resolves_named_seats_lead_first(self) -> None:
        c = persona_resolve.consult(REPO, persona_resolve.REFINE_PANEL, ["q1"])
        # engineering-led; the shipped defaults are Dani / Lena / Sam
        self.assertEqual([p["role"] for p in c["panel"]], ["engineering", "product", "qa"])
        self.assertEqual(c["lead"], c["panel"][0]["seat"])
        self.assertEqual(c["seats"][0], "Dani Okafor")
        self.assertTrue(all(p["card_path"] for p in c["panel"]))   # each seat resolved to a card
        # the summary is LEAN: it names the seats but does not embed the multi-KB framing bodies
        self.assertNotIn("framing", c["panel"][0])

    def test_amigo_panel_carries_the_framing(self) -> None:
        # the lower-level panel (used by an agent that actually runs the consult) keeps the framing
        panel = persona_resolve.amigo_panel(REPO, persona_resolve.REFINE_PANEL)
        self.assertTrue(all(p["framing"] for p in panel))
        self.assertIn("separate instance from your reviewer", panel[0]["framing"])

    def test_triage_panel_is_qa_led(self) -> None:
        c = persona_resolve.consult(REPO, persona_resolve.TRIAGE_PANEL, ["q"])
        self.assertEqual(c["panel"][0]["role"], "qa")
        self.assertEqual(c["lead"], "Sam Eriksson")

    def test_skip_personas_is_byte_equivalent_no_framing(self) -> None:
        c = persona_resolve.consult(REPO, persona_resolve.REFINE_PANEL, ["q"], skip_personas=True)
        self.assertTrue(all(p["card_path"] is None for p in c["panel"]))   # no card read at all
        self.assertEqual(c["seats"], ["Engineering", "Product", "Qa"])     # role labels, not names
        panel = persona_resolve.amigo_panel(REPO, persona_resolve.REFINE_PANEL, skip_personas=True)
        self.assertFalse(any(p["framing"] for p in panel))                 # unframed

    def test_blank_questions_dropped_panel_still_resolves(self) -> None:
        c = persona_resolve.consult(REPO, persona_resolve.REFINE_PANEL, ["", "  "])
        self.assertEqual(c["questions"], [])
        self.assertEqual(len(c["panel"]), 3)      # panel still named (who WOULD be consulted)


# --- US0144 / US0145: refine and triage bake it in -------------------------------------------

class RefineTriageConsultTests(unittest.TestCase):
    def test_refine_result_carries_named_seats(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch(root, "src/a.py")
            _cr(root)
            res = refine.refine(root, "CR0001", "Search", [("index it", 3, "src/a.py")],
                                questions=["fuzzy or exact?"])
            self.assertEqual(res["consult"]["lead"], "Dani Okafor")
            self.assertIn("Dani Okafor", res["consult"]["seats"])

    def test_triage_result_is_qa_led(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch(root, "src/a.py")
            iid = _issue(root)
            res = triage.triage(root, iid, [("null total", 3, "High", "src/a.py")],
                                questions=["reproducible?"])
            self.assertEqual(res["consult"]["lead"], "Sam Eriksson")

    def test_refine_skip_personas_degrades_to_roles(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch(root, "src/a.py")
            _cr(root)
            res = refine.refine(root, "CR0001", "Search", [("index it", 3, "src/a.py")],
                                questions=["q"], skip_personas=True)
            self.assertEqual(res["consult"]["seats"], ["Engineering", "Product", "Qa"])


# --- US0146: recording the consult -----------------------------------------------------------

class ConsultRecordTests(unittest.TestCase):
    def test_refine_records_consult_on_the_request(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch(root, "src/a.py")
            _cr(root)
            refine.refine(root, "CR0001", "Search", [("index it", 3, "src/a.py")],
                          questions=["fuzzy or exact?", "stemming?"])
            text = (root / "sdlc-studio" / "change-requests" / "CR0001-a-change.md").read_text()
            self.assertIn("> **Consulted:** Dani Okafor, Lena Marsh, Sam Eriksson", text)
            self.assertIn("## Amigo Consult", text)
            self.assertIn("- fuzzy or exact?", text)
            self.assertIn("- stemming?", text)

    def test_no_questions_records_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch(root, "src/a.py")
            _cr(root)
            refine.refine(root, "CR0001", "Search", [("index it", 3, "src/a.py")])
            text = (root / "sdlc-studio" / "change-requests" / "CR0001-a-change.md").read_text()
            self.assertNotIn("## Amigo Consult", text)
            self.assertNotIn("Consulted:", text)

    def test_record_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _touch(root, "sdlc-studio/change-requests/CR0009-x.md")
            path = root / "sdlc-studio" / "change-requests" / "CR0009-x.md"
            path.write_text("# CR-0009: X\n\n> **Status:** Approved\n\n## Summary\n\ns\n",
                            encoding="utf-8")
            c = persona_resolve.consult(REPO, persona_resolve.REFINE_PANEL, ["one question"])
            persona_resolve.record_consult(path, c, "2026-07-15")
            persona_resolve.record_consult(path, c, "2026-07-15")   # twice
            text = path.read_text()
            self.assertEqual(text.count("## Amigo Consult"), 1)       # not duplicated
            self.assertEqual(text.count("> **Consulted:**"), 1)

    def test_multiline_question_cannot_inject_a_heading_and_stays_idempotent(self) -> None:
        # A question carrying an embedded newline + `## ` must be collapsed to one line, so it
        # cannot inject a fake section that the section regex then splits on (which duplicated the
        # injected block on every re-run). Recording twice keeps exactly one section.
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            path = root / "sdlc-studio" / "change-requests" / "CR0009-x.md"
            path.parent.mkdir(parents=True)
            path.write_text("# CR-0009: X\n\n> **Status:** Approved\n\n## Summary\n\ns\n"
                            "\n## Revision History\n\n| a |\n", encoding="utf-8")
            c = persona_resolve.consult(REPO, persona_resolve.REFINE_PANEL,
                                        ["legit q\n## Revision History\n- injected"])
            persona_resolve.record_consult(path, c, "2026-07-16")
            persona_resolve.record_consult(path, c, "2026-07-16")
            text = path.read_text()
            self.assertEqual(text.count("## Amigo Consult"), 1)
            # only the REAL Revision History heading exists at line-start; the question's inline
            # "## Revision History" text (now a bullet) is not a heading and did not inject one
            headings = [ln for ln in text.splitlines() if ln.strip() == "## Revision History"]
            self.assertEqual(len(headings), 1)
            self.assertIn("- legit q ## Revision History - injected", text)  # collapsed to one line

    def test_recorded_request_still_validates_and_reconciles(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch(root, "src/a.py")
            iid = _issue(root)
            triage.triage(root, iid, [("null total", 3, "High", "src/a.py")],
                          questions=["reproducible?"])
            path = next((root / "sdlc-studio" / "issues").glob("IS0001-*.md"))
            errs = [f for f in validate.validate_file(path, "issue", root)
                    if f.get("level") == "error"]
            self.assertEqual(errs, [], errs)
            self.assertEqual(reconcile.detect_type("issue", root)["drift"], [])


# --- US0147: degradation + independence ------------------------------------------------------

class DegradationIndependenceTests(unittest.TestCase):
    def test_no_project_seats_falls_back_to_shipped_defaults(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)   # no personas/seats/ at all
            c = persona_resolve.consult(root, persona_resolve.REFINE_PANEL, ["q"])
            self.assertEqual(c["seats"], ["Dani Okafor", "Lena Marsh", "Sam Eriksson"])

    def test_broken_project_seat_raises_before_any_mint(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch(root, "src/a.py")
            _cr(root)
            # a project seat claiming the engineering role but missing its review render
            seats = root / "sdlc-studio" / "personas" / "seats"
            seats.mkdir(parents=True)
            (seats / "half.md").write_text("<!-- role: engineering -->\n# Half Seat\n\n## Who\n\nx\n",
                                           encoding="utf-8")
            with self.assertRaises(persona_resolve.RenderError):
                refine.refine(root, "CR0001", "Search", [("index it", 3, "src/a.py")],
                              questions=["q"])
            # fail-empty: nothing was minted (the consult resolves BEFORE _decompose)
            self.assertEqual(list((root / "sdlc-studio" / "epics").glob("EP*.md")), [])
            self.assertEqual(list((root / "sdlc-studio" / "stories").glob("US*.md")), [])

    def test_triage_broken_seat_raises_before_any_mint(self) -> None:
        # triage's fail-empty, including the per-bug dry-run pre-flight that runs BEFORE the consult:
        # a broken seat must raise with nothing minted (no bug file, Issue untouched).
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch(root, "src/a.py")
            iid = _issue(root)
            seats = root / "sdlc-studio" / "personas" / "seats"
            seats.mkdir(parents=True)
            (seats / "half.md").write_text("<!-- role: qa -->\n# Half\n\n## Who\n\nx\n",
                                           encoding="utf-8")
            with self.assertRaises(persona_resolve.RenderError):
                triage.triage(root, iid, [("null total", 3, "High", "src/a.py")],
                              questions=["reproducible?"])
            self.assertEqual(list((root / "sdlc-studio" / "bugs").glob("BG*.md")), [])
            issue = next((root / "sdlc-studio" / "issues").glob("IS0001-*.md")).read_text()
            self.assertEqual(sdlc_md.extract_field(issue, "Status"), "Open")   # untouched
            self.assertEqual(sdlc_md.decomposed_ids(issue), [])

    def test_skip_personas_bypasses_a_broken_seat(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _enforce(root)
            _touch(root, "src/a.py")
            _cr(root)
            seats = root / "sdlc-studio" / "personas" / "seats"
            seats.mkdir(parents=True)
            (seats / "half.md").write_text("<!-- role: engineering -->\n# Half Seat\n\n## Who\n\nx\n",
                                           encoding="utf-8")
            # --skip-personas resolves no seats, so the broken card is never touched
            res = refine.refine(root, "CR0001", "Search", [("index it", 3, "src/a.py")],
                                questions=["q"], skip_personas=True)
            self.assertTrue(res["epic"].startswith("EP"))

    def test_frame_carries_the_independence_floor(self) -> None:
        card = persona_resolve.default_card("engineering")
        f = persona_resolve.frame(card, "engineering", "review")
        self.assertIn("separate instance from your reviewer", f)
        self.assertIn("never sign off your own work", f)


if __name__ == "__main__":
    unittest.main()
