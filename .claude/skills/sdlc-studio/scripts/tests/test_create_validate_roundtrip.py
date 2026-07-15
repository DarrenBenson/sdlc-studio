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
import json
import shutil
import subprocess
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
# The meta types (retro/review/handoff) bootstrap their own `_index.md` on first create, from
# the same index templates and the same shared writer as the pipeline types - so their fresh
# index must lint clean too. Kept beside NEW_TYPES so neither family goes unguarded.
META_TYPES = ("retro", "review", "handoff")

# The rules a CREATOR owns: it holds (or can derive) every input they need, so none of
# them may fire on a freshly minted artefact - filled or not.
CREATOR_RULES = {"id-format", "no-title", "no-status", "status-vocab", "tranche-shape",
                 "authorship-structured", "authorship-type", "authorship-unresolved"}

# What a real caller supplies per type - the content the validator demands under v3
# (bug evidence, CR impact + size), the AC a story is specified by, and the prose the
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
    # A bug and a CR also carry their GROOMING - the files they touch and the job size - because
    # `sprint plan` refuses a unit that declares neither, so a creator that would mint one is
    # minting unplannable work. Both creation paths demand them (BG0136).
    "bug": {"severity": "Medium", "summary": "the id parser drops a trailing dash",
            "steps": "run the parser over a dash-suffixed id", "fix": "strip the trailing dash",
            "affects": "src/id_parser.py, src/ids.py", "points": 3},
    "cr": {"priority": "Medium", "ctype": "Improvement",
           "summary": "carry the size estimate in the skeleton",
           "acs": ["the skeleton carries an impact statement"],
           "impact": "every CR filed today fails its own validator on first check",
           "size": "M", "affects": "src/skeleton.py"},
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
    # The creation-time grooming gate (BG0144) refuses a bug/CR/story whose declared `Affects`
    # paths ALL fail to resolve on disk. Every groomed fixture in this file declares one of the
    # paths below, so materialise them as empty files at the repo root - the SUPERSET of every
    # groomed Affects path - so a groomed unit resolves and can be minted.
    for rel in ("src/thing.py", "src/skeleton.py", "src/id_parser.py", "src/ids.py"):
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text("", encoding="utf-8")


def _errors(root: Path, path: Path, type_: str) -> list[dict]:
    return [v for v in validate.validate_file(path, type_, root) if v["severity"] == "error"]


def _fmt(violations: list[dict]) -> str:
    return "; ".join(f"[{v['rule']}] {v['message']}" for v in violations)


# The house gate lints created artefacts with markdownlint. The skill's own config relaxes
# the table rules (MD055/056/058/060), but a created artefact lands in the project workspace
# under the ROOT ruleset where those rules are live - so a creator whose tables trip them ships
# lint-failing output the validator never sees. This leg pins exactly that table-rule family so
# the class cannot regress. It is a SECOND deterministic guard beside validate.py, not a
# replacement: markdownlint owns table mechanics, validate.py owns artefact structure.
_TABLE_RULES = {"default": False, "MD055": True, "MD056": True, "MD058": True, "MD060": True}

# A freshly written `_index.md` is materialised from its template by dropping the sample
# `{{ }}` rows, which can leave a double blank line where a dropped row sat between two blanks.
# So the index leg pins MD012 (no-multiple-blanks) on top of the table-rule family.
_INDEX_RULES = {**_TABLE_RULES, "MD012": True}


def _markdownlint() -> list[str] | None:
    """The markdownlint CLI, or None when Node is absent. Prefer the repo's pinned binary
    (devDependency), then a PATH install; never fabricate a pass when neither exists."""
    repo_bin = Path(__file__).resolve().parents[5] / "node_modules" / ".bin" / "markdownlint"
    if repo_bin.exists():
        return [str(repo_bin)]
    found = shutil.which("markdownlint")
    return [found] if found else None


def _markdownlint_errors(path: Path, rules: dict | None = None) -> str:
    """Empty string when the file satisfies `rules` (the table-rule family by default);
    otherwise the CLI's report. Raises FileNotFoundError-free: caller must have checked
    _markdownlint() first."""
    cli = _markdownlint()
    assert cli is not None
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as cfg:
        json.dump(rules if rules is not None else _TABLE_RULES, cfg)
        cfg_path = cfg.name
    try:
        proc = subprocess.run([*cli, "--config", cfg_path, str(path)],
                              capture_output=True, text=True)
    finally:
        Path(cfg_path).unlink(missing_ok=True)
    return "" if proc.returncode == 0 else (proc.stdout + proc.stderr).strip()


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
        if fields.get("points"):
            self.assertEqual(sdlc_md.read_points(text), fields["points"],
                             f"{where}: --points never reached the file")
        if fields.get("affects"):
            # Not just present as prose: the planner's own parser must READ it back as the
            # files it declares, or the unit is ungroomed however good the line looks.
            self.assertEqual(sdlc_md.affects_files(text),
                             [p.strip() for p in fields["affects"].split(",")],
                             f"{where}: --affects never reached the file as a readable field")

    def _check_file_finding(self, type_: str, era: str) -> None:
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _workspace(root, era)
            file_finding.ensure_index(root, type_, "2026-07-13")
            fields = dict(CONTENT[type_])
            # The CR filer sizes a CR by its T-shirt `Size` (a CR is a request, decomposed before
            # delivery), not by story points - CONTENT["cr"] carries that Size directly (BG0148).
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


# The grooming a bug or a CR may never be born without, whatever else is left to the agent.
# A scaffold defers the PROSE (summary, steps, fix) to whoever fills it in; it does not get to
# defer the two fields that decide whether the unit can be planned at all - the author knows
# which files they are about to touch, and nobody knows it better at plan time.
GROOM = {"affects": "src/thing.py", "points": 3}
# A CR/RFC/epic is a REQUEST: it grooms with a T-shirt Size (S/M/L/XL), never Points (BG0148).
GROOM_REQUEST = {"affects": "src/thing.py", "size": "M"}


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
                        if type_ == "bug":
                            fields.update(GROOM)  # a delivery unit grooms with Points
                        elif type_ == "cr":
                            fields.update(GROOM_REQUEST)  # a request grooms with a T-shirt Size
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
            res = artifact.new(root, "bug", "unattributed", {"severity": "Medium", **GROOM})
            auth = sdlc_md.parse_authorship(Path(res["path"]).read_text(encoding="utf-8"))
            self.assertIsNotNone(auth)
            self.assertEqual(auth["type"], "agent")
            self.assertTrue(sdlc_md.resolve_author(auth["name"], auth["type"], root))


class MarkdownlintRoundTripTests(unittest.TestCase):
    """A creator must not emit an artefact - or the `_index.md` it touches - whose tables the
    house markdownlint gate rejects.

    BG0108's round trip caught validator mismatches; this leg catches the sibling class - a
    deterministic creator emitting markdownlint-failing tables (unspaced delimiters, or handlebars
    loop markers left inside a table body as pipe-less rows). It degrades honestly: when Node (and
    so markdownlint) is absent, the test SKIPS with a message rather than passing silently.

    The index leg matters because a brand-new index (a consuming project's first artefact of a
    type) is written from the index template as-is - reconcile only rewrites it to compact style
    on a later pass, so a fresh index that carries padded or tight delimiter rows lands failing
    the workspace lint. Linting the artefact alone missed this, so the class is pinned here too.
    The index leg covers the meta types (retro/review/handoff) as well as the eight pipeline
    types, because both families bootstrap their first index from the same templates through the
    same writer - a regression to a meta index template must redden here too.
    """

    def setUp(self) -> None:
        if _markdownlint() is None:
            self.skipTest("markdownlint unavailable (Node absent) - table-lint leg skipped")

    def test_created_artefacts_are_table_lint_clean(self) -> None:
        for type_ in NEW_TYPES:
            for template in ("minimal", "planning", "full"):
                with self.subTest(type=type_, template=template):
                    with tempfile.TemporaryDirectory() as d:
                        root = Path(d)
                        _workspace(root, "v3")
                        fields = dict(CONTENT[type_])
                        if type_ == "story":
                            fields["epic"] = artifact.new(root, "epic", "parent epic",
                                                          dict(CONTENT["epic"]))["id"]
                        res = artifact.new(root, type_, f"a {type_}",
                                           {**fields, "template": template})
                        errs = _markdownlint_errors(Path(res["path"]))
                        self.assertEqual(errs, "", f"{type_}/{template}:\n{errs}")
                        # The freshly written `_index.md` the creator touched must lint clean too:
                        # it is a consuming project's first index of the type, born from the
                        # template with no reconcile pass behind it.
                        idx = Path(res["path"]).parent / "_index.md"
                        idx_errs = _markdownlint_errors(idx, _INDEX_RULES)
                        self.assertEqual(idx_errs, "", f"{type_}/{template} _index.md:\n{idx_errs}")

    def test_created_meta_indexes_are_lint_clean(self) -> None:
        """The meta types (retro/review/handoff) bootstrap their first `_index.md` from the same
        templates through the same writer as the pipeline types - so that fresh index must lint
        clean too. Without this leg a regression to a meta index template escapes the guard."""
        for type_ in META_TYPES:
            with self.subTest(type=type_):
                with tempfile.TemporaryDirectory() as d:
                    root = Path(d)
                    _workspace(root, "v3")
                    res = artifact.meta_new(root, type_, f"a {type_}")
                    idx = Path(res["path"]).parent / "_index.md"
                    self.assertTrue(idx.exists(), f"{type_}: meta index was not bootstrapped")
                    idx_errs = _markdownlint_errors(idx, _INDEX_RULES)
                    self.assertEqual(idx_errs, "", f"{type_} _index.md:\n{idx_errs}")


if __name__ == "__main__":
    unittest.main()
