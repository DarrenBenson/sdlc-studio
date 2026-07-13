"""Create-then-validate round trip: every creator x every type x every schema era.

The class this locks: a deterministic creator must not emit an artefact its own
deterministic validator rejects. Three creators mint artefacts - `artifact.py new`,
`artifact.py batch`, `file_finding.py file` (plus the v3 Low-severity consolidation CR
that both creators route into) - and `validate.py check` is the spec they must all meet.

Two legs, because two different parties own the rules:

* `ContentRoundTripTests` - a creator given the content the type needs must emit an
  artefact with ZERO validator errors, in both eras. This is the whole matrix.
* `ScaffoldRoundTripTests` - a creator given nothing but a title emits a scaffold. The
  content rules (an unfilled `{{placeholder}}`, a story with no AC yet, an unwritten
  evidence section) are the caller's to satisfy and the validator rightly reports them,
  but no CREATOR-owned rule (id, title, status, authorship, tranche) may ever fire.
"""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCR))
from lib import sdlc_md  # noqa: E402
import file_finding  # noqa: E402
import validate  # noqa: E402


def _load():
    spec = importlib.util.spec_from_file_location("artifact", SCR / "artifact.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["artifact"] = mod
    spec.loader.exec_module(mod)
    return mod


artifact = _load()

ERAS = ("v2", "v3")
NEW_TYPES = ("epic", "story", "plan", "test-spec", "workflow", "bug", "cr", "rfc")
FILE_TYPES = ("bug", "cr", "rfc")

# The rules a CREATOR owns: it holds (or can derive) every input they need, so none of
# them may fire on a freshly minted artefact - filled or not.
CREATOR_RULES = {"id-format", "no-title", "no-status", "status-vocab", "tranche-shape",
                 "authorship-structured", "authorship-type", "authorship-unresolved"}

# What a real caller supplies per type - the content the validator demands under v3
# (bug evidence, CR impact + effort), the AC a story is specified by, and the prose the
# caller already holds. Every value is distinctive, so the test can prove it reached the file.
CONTENT: dict[str, dict] = {
    "epic": {"summary": "everything search-shaped",
             "acs": ["every story in this epic is Done"]},
    "plan": {"summary": "how the search index gets built"},
    "test-spec": {"summary": "what proves search works"},
    "workflow": {"summary": "the search rollout run"},
    "story": {"persona": "Alex Rivera",
              "acs": ["the CLI exits 0 for a known id"],
              "verify": ["pytest -k known_id"],
              "target": "functional"},
    "bug": {"severity": "Medium", "summary": "the id parser drops a trailing dash",
            "steps": "run the parser over a dash-suffixed id", "fix": "strip the trailing dash"},
    "cr": {"priority": "Medium", "ctype": "Improvement",
           "summary": "carry the effort estimate in the skeleton",
           "acs": ["the skeleton carries an impact statement"],
           "impact": "every CR filed today fails its own validator on first check",
           "effort": "S"},
    "rfc": {"summary": "how ids should be minted",
            "options": ["A - stay sequential", "B - mint a ULID"],
            "recommendation": "B, once the aliases are in place"},
}

# The content keys whose value must appear verbatim in the rendered artefact. A creator that
# accepts content and drops it is worse than one that never accepted it: the caller sees exit
# 0 and a clean validator over an artefact its words never reached.
PROSE_KEYS = ("persona", "summary", "steps", "fix", "impact", "recommendation", "target")
LIST_KEYS = ("acs", "options", "verify")


def _workspace(root: Path, era: str) -> None:
    """A bare project workspace; `v3` opts into the schema-v3 team rules."""
    (root / "sdlc-studio").mkdir(parents=True, exist_ok=True)
    if era == "v3":
        (root / "sdlc-studio" / ".config.yaml").write_text(
            "schema_version: 3\n", encoding="utf-8")


def _errors(root: Path, path: Path, type_: str) -> list[dict]:
    return [v for v in validate.validate_file(path, type_, root) if v["severity"] == "error"]


def _fmt(violations: list[dict]) -> str:
    return "; ".join(f"[{v['rule']}] {v['message']}" for v in violations)


class ContentRoundTripTests(unittest.TestCase):
    """Content in, validator-clean artefact out - for every creator, type and era."""

    def test_matrix(self) -> None:
        for era in ERAS:
            for type_ in NEW_TYPES:
                # Every scaffold richness: `batch` defaults to the full templates/core body,
                # so the fan-out path a decomposition actually runs is in the matrix too, and
                # the lean `planning` tier is a creator like any other - a tier outside this
                # matrix is exactly the hole the round trip exists to close.
                for creator in ("new", "batch"):
                    for template in ("minimal", "planning", "full"):
                        with self.subTest(creator=creator, type=type_, era=era,
                                          template=template):
                            self._check_artifact(creator, type_, era, template)
            for type_ in FILE_TYPES:
                with self.subTest(creator="file", type=type_, era=era):
                    self._check_file_finding(type_, era)

    def _check_artifact(self, creator: str, type_: str, era: str, template: str) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root, era)
            fields = dict(CONTENT[type_])
            if type_ == "story":
                fields["epic"] = artifact.new(root, "epic", "parent epic",
                                              dict(CONTENT["epic"]))["id"]
            if creator == "new":
                res = artifact.new(root, type_, f"a {type_}", {**fields, "template": template})
            else:
                res = artifact.new_batch(root, type_, [{"title": f"a {type_}", **fields}],
                                         template=template)["created"][0]
            errs = _errors(root, Path(res["path"]), type_)
            self.assertEqual(errs, [], f"{creator}/{type_}/{era}/{template}: {_fmt(errs)}")
            self._assert_content_landed(Path(res["path"]), fields,
                                        f"{creator}/{type_}/{era}/{template}")

    def _assert_content_landed(self, path: Path, fields: dict, where: str) -> None:
        """Every value the caller supplied appears in the artefact. A clean validator over an
        artefact that silently dropped the caller's words is not a round trip."""
        text = path.read_text(encoding="utf-8")
        for key in PROSE_KEYS:
            if str(fields.get(key) or "").strip():
                self.assertIn(fields[key], text, f"{where}: --{key} never reached the file")
        for key in LIST_KEYS:
            for item in fields.get(key) or []:
                self.assertIn(item, text, f"{where}: --{key} item {item!r} never reached the file")
        if fields.get("effort"):
            self.assertIn(f"**Effort:** {fields['effort']}", text,
                          f"{where}: --effort never reached the file")

    def _check_file_finding(self, type_: str, era: str) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root, era)
            file_finding.ensure_index(root, type_, "2026-07-13")
            fields = dict(CONTENT[type_])
            res = file_finding.file_finding(root, type_, f"a {type_}", fields)
            errs = _errors(root, Path(res["path"]), type_)
            self.assertEqual(errs, [], f"file/{type_}/{era}: {_fmt(errs)}")
            self._assert_content_landed(Path(res["path"]), fields, f"file/{type_}/{era}")

    def test_consolidation_cr_validates(self) -> None:
        """The v3 Low-severity consolidation CR is a creator too - and its only era is v3."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root, "v3")
            file_finding.ensure_index(root, "cr", "2026-07-13")
            res = file_finding.file_finding(root, "bug", "a trivial nit",
                                            {**CONTENT["bug"], "severity": "Low"})
            self.assertTrue(res.get("consolidated_into"), "expected the Low finding to fold")
            errs = _errors(root, Path(res["path"]), "cr")
            self.assertEqual(errs, [], f"consolidation CR: {_fmt(errs)}")


class ScaffoldRoundTripTests(unittest.TestCase):
    """A content-less scaffold may report unfilled CONTENT, never a creator-owned defect."""

    def test_matrix(self) -> None:
        for era in ERAS:
            for type_ in NEW_TYPES:
                with self.subTest(type=type_, era=era):
                    with tempfile.TemporaryDirectory() as d:
                        root = Path(d)
                        _workspace(root, era)
                        fields = ({"epic": artifact.new(root, "epic", "parent")["id"]}
                                  if type_ == "story" else {})
                        res = artifact.new(root, type_, f"a bare {type_}", fields)
                        owned = [v for v in _errors(root, Path(res["path"]), type_)
                                 if v["rule"] in CREATOR_RULES]
                        self.assertEqual(owned, [], f"{type_}/{era}: {_fmt(owned)}")

    def test_author_flag_is_stamped(self) -> None:
        """`--author` is the authorship of record; a typed value is carried verbatim."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root, "v3")
            res = artifact.new(root, "epic", "authored", {"author": "Dani Okafor; agent; v2"})
            text = Path(res["path"]).read_text(encoding="utf-8")
            self.assertIn("> **Raised-by:** Dani Okafor; agent; v2", text)

    def test_default_author_is_the_invoking_agent(self) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root, "v3")
            res = artifact.new(root, "bug", "unattributed", {"severity": "Medium"})
            auth = sdlc_md.parse_authorship(Path(res["path"]).read_text(encoding="utf-8"))
            self.assertIsNotNone(auth)
            self.assertEqual(auth["type"], "agent")
            self.assertTrue(sdlc_md.resolve_author(auth["name"], auth["type"], root))


if __name__ == "__main__":
    unittest.main()
