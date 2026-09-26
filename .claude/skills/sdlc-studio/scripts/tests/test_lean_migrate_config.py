"""US0925: an upgrading project's config carries forward without the retired review keys.

A project initialised by v5.1 carries two retired Definition of Done tags and an AGENTS.md that
teaches `review.two_role_after`; a project that hand-set keys (this repository's shape) carries the
retired review keys too. `migrate --apply` strips the tags and keys line by line, reports the
instructions lines for a human, and reports the frozen review ledgers as history. Every fixture is
a temporary directory; nothing here reads this repository's own artefacts.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_SCRIPTS))


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, _SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


migrate = _load("migrate")
from lib import sdlc_md  # noqa: E402
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402 - confined, hermetic git for the release-history check

try:
    import yaml
    HAVE_YAML = True
except ImportError:  # pragma: no cover - the stripper's parse check is skipped without it
    HAVE_YAML = False

TODAY = "2026-09-25"

#: The Story section of the Definition of Done v5.1.0's `init.py` wrote, verbatim.
V51_DOD = """# Definition of Done

## Story

A story or bug is Done when:

- [ ] Its executable acceptance criteria pass and are back-annotated [check: story.verify-ac]
- [ ] An independent critic APPROVE is recorded (author never reviews its own diff) [check: review.critic-approve]
- [ ] The adversarial pass is recorded as evidence and the reviewer of record has signed off [check: review.two-role]
- [ ] Its documentation landed in the same unit (help + reference for any new command/flag)
- [ ] If it is a REPAIR: a mutant was applied to its own changed lines and its test was seen
      to fail on that mutant. A fix's author is not sufficient evidence for that fix - the
      test is written after the answer is known, so it must be shown capable of failing.
      Set `review.mutation_evidence: block` to make a survivor refuse instead
      [check: repair.mutation-evidence]

## Sprint

- [ ] The batch retro exists and validates [check: close.retro]
"""

#: The v5.1 agent-instructions template's review paragraph, verbatim, plus a retired verb.
V51_AGENTS = """# AGENTS.md

**Review is independent of the author.** Whoever wrote the change never records its
sign-off. Two roles, never merged: an **adversarial reviewer** (a fresh context that
did not write the code) files findings as evidence, and a **reviewer of record** - the
operator, or a named delegate in a separate trust boundary - approves. With
`review.two_role_after` set in `.config.yaml`, a unit holds at Review until that
sign-off lands.
"""
V51_CLAUDE = "# CLAUDE.md\n\n@AGENTS.md\n\nBefore a close, run `sprint.py preflight`.\n"

#: A config in this repository's shape: retired keys set by hand among kept ones, with comments.
REPO_CONFIG = """# Project configuration (merged over templates/config-defaults.yaml).
schema_version: 2

conformance:
  adopt_after: 82

review:
  # D0129: a REJECT files its findings and the run ships.
  policy: carry-forward
  # Two-role review gate, stood down for good.
  two_role_after: 99999
  # D0130: the reviewer of record may be a named seat.
  # (continued)
  signoff: operator  # D0255: the operator signs the run once
  test_plan_after: "2026-08-01"
  mutation_evidence: block
  line_coverage: block
  require_brief_provenance: false  # D0255
  line_coverage_after: "2026-09-07"
  # a comment that belongs to the next key
  policy_note: kept

quality:
  epic_requires_test_spec: true
  depth_parity_gate: true

triage:
  enabled: true

# D0255: plan review is deleted.
plan_review:
  enabled: false
  seats:
    - engineering

    - qa
"""
#: The REPO_CONFIG lines `--apply` must remove (1-based): each retired key's own line, and the
#: `plan_review` block with its children, the blank line between two of them included. Every other
#: line is kept verbatim, the comment above each removed key among them.
REMOVED_LINES = {11, 14, 15, 16, 18, 19, 25, 31, 32, 33, 34, 35, 36}
RETIRED_IN_FIXTURE = ("plan_review", "review.test_plan_after", "review.two_role_after",
                      "review.signoff", "review.mutation_evidence", "review.line_coverage_after",
                      "review.require_brief_provenance", "quality.depth_parity_gate")

VERSION = 'schema_version: 2\nskill_version: "4.1.0"\n'


def _w(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _snapshot(root: Path) -> dict[str, bytes]:
    return {str(p.relative_to(root)): p.read_bytes()
            for p in sorted(root.rglob("*")) if p.is_file()}


def _v51(root: Path) -> None:
    """A v5.1-shaped project with this repository's hand-set config."""
    _w(root, "sdlc-studio/.version", VERSION)
    _w(root, "sdlc-studio/.config.yaml", REPO_CONFIG)
    _w(root, "sdlc-studio/definition-of-done.md", V51_DOD)
    _w(root, "AGENTS.md", V51_AGENTS)
    _w(root, "CLAUDE.md", V51_CLAUDE)


def _retired(res: dict) -> list[dict]:
    return [d for d in res["deterministic"] if d["source"] in ("dod", "config")]


#: Calls that put bytes in a file: the path builtins, the shared helper, and critic's row appender.
_WRITES = {"write_text", "write_bytes", "atomic_write", "_append_row", "write"}


def _shipped(scripts: Path = _SCRIPTS) -> list[Path]:
    return sorted([*scripts.glob("*.py"), *(scripts / "lib").glob("*.py")])


def _key_readers(key: str, scripts: Path = _SCRIPTS) -> list[str]:
    """Shipped modules holding `key` (or a distinctive leaf of it) as a string value, outside
    docstrings and the `RETIRED_*` registries that name it so `migrate` can remove it."""
    leaf = key.rsplit(".", 1)[-1]
    names = {key, leaf} if "_" in leaf else {key}
    out = []
    for path in _shipped(scripts):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        skip = {id(n.body[0].value) for n in ast.walk(tree)
                if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef))
                and n.body and isinstance(n.body[0], ast.Expr)}
        skip |= {id(k) for n in ast.walk(tree) if isinstance(n, ast.Assign)
                 and isinstance(n.value, ast.Dict)
                 and any(getattr(t, "id", "").startswith("RETIRED_") for t in n.targets)
                 for k in n.value.keys}
        if any(isinstance(n, ast.Constant) and n.value in names and id(n) not in skip
               for n in ast.walk(tree)):
            out.append(path.name)
    return out


def _ledger_writers(scripts: Path = _SCRIPTS) -> list[str]:
    """`module.function` for each shipped function that makes a write call and names a frozen
    ledger, itself or through a same-module function that does (the path helper)."""
    out = []
    for path in _shipped(scripts):
        if path.name == "migrate.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        consts = {t.id: n.value.value for n in tree.body if isinstance(n, ast.Assign)
                  and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)
                  for t in n.targets if isinstance(t, ast.Name)}
        fns = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]

        def named(fn) -> set[str]:
            vals = {n.value for n in ast.walk(fn)
                    if isinstance(n, ast.Constant) and isinstance(n.value, str)}
            vals |= {consts[n.id] for n in ast.walk(fn) if isinstance(n, ast.Name) and n.id in consts}
            return {led for led in migrate.FROZEN_LEDGERS if any(led in v for v in vals)}

        helpers = {fn.name for fn in fns if named(fn)}
        for fn in fns:
            calls = {getattr(c.func, "attr", getattr(c.func, "id", ""))
                     for c in ast.walk(fn) if isinstance(c, ast.Call)}
            if calls & _WRITES and (named(fn) or calls & (helpers - {fn.name})):
                out.append(f"{path.name}.{fn.name}")
    return out


def _cli(root: Path, *extra: str) -> dict:
    proc = subprocess.run([sys.executable, str(_SCRIPTS / "migrate.py"), "--root", str(root),
                           "--format", "json", *extra],
                          capture_output=True, text=True, timeout=120)
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout)


class MigrateConfigTests(unittest.TestCase):

    def test_retired_dod_tags_are_untagged(self) -> None:
        """AC1. MUTANTS: HEAD's migrate (both tags survive `--apply`); a hand-kept id list in
        migrate.py (the registry-added `close.retro` survives)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v51(root)
            dor = _w(root, "sdlc-studio/definition-of-ready.md",
                     "# Definition of Ready\n\n- [ ] Reviewed twice [check: review.two-role]\n")
            res = _cli(root, "--apply")
            self.assertEqual(dor.read_text(encoding="utf-8"),
                             "# Definition of Ready\n\n- [ ] Reviewed twice\n",
                             "the Definition of Ready is untagged too")
            dod = (root / "sdlc-studio/definition-of-done.md").read_text(encoding="utf-8")
            self.assertEqual(sdlc_md.retired_check_ids(dod), [],
                             f"every retired tag must be gone after --apply:\n{dod}")
            self.assertIn("- [ ] The adversarial pass is recorded as evidence and the reviewer "
                          "of record has signed off\n", dod,
                          "the criterion stays, untagged, as a human-judged item")
            self.assertIn("      Set `review.mutation_evidence: block` to make a survivor "
                          "refuse instead\n\n## Sprint", dod,
                          "a line holding only the retired tag goes; its criterion stays")
            self.assertIn("[check: story.verify-ac]", dod, "a live tag is untouched")
            named = {(e["file"], e["id"], e["line"]) for e in _retired(res)
                     if e["source"] == "dod"}
            self.assertEqual(named, {("definition-of-done.md", "review.two-role", 9),
                                     ("definition-of-done.md", "repair.mutation-evidence", 15),
                                     ("definition-of-ready.md", "review.two-role", 3)},
                             "the report names each retired tag with its line")

            # The ONE registry: an id added to it is stripped with no change to migrate.py.
            _w(root, "sdlc-studio/definition-of-done.md", V51_DOD)
            with mock.patch.dict(sdlc_md.RETIRED_CHECK_IDS, {"close.retro": "a test retirement"}):
                res = migrate.migrate(root, apply=True, today=TODAY)
            dod = (root / "sdlc-studio/definition-of-done.md").read_text(encoding="utf-8")
            self.assertNotIn("[check: close.retro]", dod,
                             "an id added to sdlc_md.RETIRED_CHECK_IDS must be stripped too")
            self.assertIn("- [ ] The batch retro exists and validates\n", dod)
            self.assertIn("close.retro", {e.get("id") for e in _retired(res)})

    def test_instructions_naming_a_retired_surface_are_reported(self) -> None:
        """AC2. MUTANTS: HEAD's migrate (the v5.1 paragraph is not reported); a rewrite of
        either file (their bytes change)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v51(root)
            before = {n: (root / n).read_bytes() for n in ("AGENTS.md", "CLAUDE.md")}
            res = migrate.migrate(root, apply=True, today=TODAY)
            for name, raw in before.items():
                self.assertEqual((root / name).read_bytes(), raw, f"{name} must not be rewritten")
            hits = {(h["file"], h["line"], h["surface"])
                    for h in res["needs_human"] if h["kind"] == "retired-surface"}
            self.assertIn(("AGENTS.md", 7, "review.two_role_after"), hits,
                          "the v5.1 review paragraph is reported with its file and line")
            self.assertIn(("CLAUDE.md", 5, "sprint.py preflight"), hits,
                          "a retired verb is reported with its file and line")
            self.assertIn(("sdlc-studio/definition-of-done.md", 14, "review.mutation_evidence"),
                          hits, "kept DoD prose naming a retired key is reported, not rewritten")
            text = migrate.render(res)
            self.assertIn("AGENTS.md:7", text, "the rendered report names file:line")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_apply_strips_every_retired_key(self) -> None:
        """AC3. MUTANTS: a parse-and-dump rewrite (comments lost, keys reordered); removing only
        a non-default `signoff`; stripping a block's key line but not its children."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v51(root)
            res = migrate.migrate(root, apply=True, today=TODAY)
            after = (root / "sdlc-studio/.config.yaml").read_text(encoding="utf-8")
            expected = [line for n, line in enumerate(REPO_CONFIG.splitlines(keepends=True), 1)
                        if n not in REMOVED_LINES]
            self.assertEqual(after, "".join(expected),
                             "only the retired keys' lines and a removed block's children go; "
                             "every other line, comments included, is byte-identical")
            parsed = yaml.safe_load(after)
            self.assertEqual(parsed["review"]["line_coverage"], "block")
            by_key = {e["key"]: e for e in _retired(res) if e["kind"] == "retired-config-key"}
            self.assertEqual(set(by_key), set(RETIRED_IN_FIXTURE),
                             "the report names each retired key present")
            for key, entry in by_key.items():
                self.assertIn(sdlc_md.RETIRED_CONFIG_KEYS[key], entry["detail"],
                              f"{key}: the report says what replaced it, from the registry")
            self.assertEqual(by_key["review.two_role_after"]["comment_above"], [10, 10])
            self.assertEqual(by_key["review.signoff"]["comment_above"], [12, 13])
            self.assertEqual(by_key["plan_review"]["comment_above"], [30, 30])
            self.assertIsNone(by_key["review.mutation_evidence"]["comment_above"],
                              "a key directly under another key has no comment block to report")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_a_block_left_empty_goes_and_an_unsafe_layout_is_handed_back(self) -> None:
        """AC3's edges. MUTANTS: leaving `quality:` empty (it would read as null and mask every
        shipped `quality.*` default); writing a flow-style mapping the line pass cannot edit."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cfg = _w(root, "sdlc-studio/.config.yaml",
                     "quality:\n  # stood down\n  depth_parity_gate: true\n\n"
                     "triage:\n  enabled: true\n")
            res = migrate.migrate(root, apply=True, today=TODAY)
            self.assertEqual(cfg.read_text(encoding="utf-8"),
                             "  # stood down\n\ntriage:\n  enabled: true\n")
            self.assertIn(("emptied-block", "quality", 1),
                          {(e["kind"], e["key"], e["line"]) for e in _retired(res)})

            flow = "review: {signoff: panel, policy: block}\n"
            cfg.write_text(flow, encoding="utf-8")
            res = migrate.migrate(root, apply=True, today=TODAY)
            self.assertEqual(cfg.read_text(encoding="utf-8"), flow, "nothing is written")
            self.assertEqual(_retired(res), [])
            self.assertTrue(any("review.signoff" in h["detail"] for h in res["needs_human"]
                                if h["kind"] == "retired-config-key"),
                            "a key the line pass cannot remove is handed to a human")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_crlf_files_keep_their_line_endings(self) -> None:
        """AC1/AC3 on a CRLF project. MUTANT: a universal-newline read written back (LF out)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v51(root)
            crlf = {rel: (root / rel).read_text(encoding="utf-8").replace("\n", "\r\n")
                    for rel in ("sdlc-studio/.config.yaml", "sdlc-studio/definition-of-done.md")}
            for rel, text in crlf.items():
                (root / rel).write_bytes(text.encode("utf-8"))
            migrate.migrate(root, apply=True, today=TODAY)
            cfg = (root / "sdlc-studio/.config.yaml").read_bytes().decode("utf-8")
            self.assertEqual(cfg, "".join(
                line for n, line in enumerate(crlf["sdlc-studio/.config.yaml"].splitlines(
                    keepends=True), 1) if n not in REMOVED_LINES))
            dod = (root / "sdlc-studio/definition-of-done.md").read_bytes().decode("utf-8")
            self.assertEqual(dod.count("\n"), dod.count("\r\n"), "every line stays CRLF")
            self.assertEqual(sdlc_md.retired_check_ids(dod), [])

    def test_without_a_parser_retired_keys_are_handed_back_unwritten(self) -> None:
        """AC3 with no PyYAML. MUTANTS: writing the unchecked line pass; staying silent about a
        flow-mapped key the line pass cannot see."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v51(root)
            cfg = root / "sdlc-studio/.config.yaml"
            for text, key in ((REPO_CONFIG, "review.two_role_after"),
                              ("review: {signoff: panel, policy: block}\n", "review.signoff")):
                cfg.write_text(text, encoding="utf-8")
                with mock.patch.dict(sys.modules, {"yaml": None}):
                    res = migrate.migrate(root, apply=True, today=TODAY)
                self.assertEqual(cfg.read_text(encoding="utf-8"), text, "nothing is written")
                self.assertEqual([e for e in _retired(res) if e["source"] == "config"], [])
                self.assertTrue(any(key in h["detail"] for h in res["needs_human"]
                                    if h["kind"] == "retired-config-key"),
                                f"{key} is handed to a human")

    def test_dry_run_writes_nothing_and_a_second_apply_is_a_no_op(self) -> None:
        """AC4. MUTANTS: a stripper that writes in dry-run; one that re-reports every pass."""
        def removals(res: dict) -> set:
            return {(e["source"], e.get("id") or e.get("key"), e["line"]) for e in _retired(res)}

        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v51(root)
            before = _snapshot(root)
            dry = _cli(root)
            self.assertEqual(_snapshot(root), before, "a dry run writes nothing")
            self.assertTrue(all(not e["applied"] for e in _retired(dry)))
            applied = _cli(root, "--apply")
            first = _snapshot(root)
            self.assertEqual({k for k in first if first[k] != before.get(k)},
                             {"sdlc-studio/.version", "sdlc-studio/.config.yaml",
                              "sdlc-studio/definition-of-done.md"},
                             "the first --apply writes the version, the config and the DoD only")
            self.assertEqual(removals(dry), removals(applied),
                             "the dry run lists exactly the removals --apply makes")
            self.assertEqual(len(removals(dry)), 2 + len(RETIRED_IN_FIXTURE))
            once = _snapshot(root)
            again = _cli(root, "--apply")
            self.assertEqual(_snapshot(root), once, "a second --apply changes no byte")
            self.assertEqual(removals(again), set(), "and lists nothing to remove")

    def test_frozen_ledgers_are_reported_with_their_unlicensed_rows(self) -> None:
        """AC5. MUTANTS: silence about rows dated on or after the constant; counting by the
        verdict date rather than the row's own date; editing a frozen ledger."""
        from datetime import date, timedelta
        on = migrate.critic.REPAIR_VERB_RETIRED        # the shipped constant, not a copy
        before, after = (str(date.fromisoformat(on) + timedelta(days=n)) for n in (-1, 1))
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _v51(root)
            for name in ("plan-review-verdicts.md", "signoff-record.md", "critic-evidence.md",
                         "plan-rulings.md"):
                _w(root, f"sdlc-studio/reviews/{name}", f"# {name}\n\n| Unit | Date |\n"
                                                        "| --- | --- |\n| US0001 | 2026-09-30 |\n")
            _w(root, "sdlc-studio/reviews/repair-record.md",
               "# Repair Records\n\n| Unit | Verdict date | Author | Date | Closed |\n"
               "| --- | --- | --- | --- | --- |\n"
               f"| US0001 | {before} | a | {before} | x |\n"
               f"| US0002 | {before} | a | {on} | x |\n"
               f"| US0003 | {after} | a | {after} | x |\n")
            _w(root, "sdlc-studio/reviews/sprint-review-record.md",
               "# Sprint-level Reviews\n\n| Base | Reviewer | Author | Verdict | Date | Units |\n"
               "| --- | --- | --- | --- | --- | --- |\n"
               f"| abc | qa | a | APPROVE | {before} | US0001 |\n"
               f"| def | qa | a | APPROVE | {on} | US0002 |\n")
            held = {p: p.read_bytes() for p in (root / "sdlc-studio/reviews").iterdir()}
            res = migrate.migrate(root, apply=True, today=TODAY)
            for p, raw in held.items():
                self.assertEqual(p.read_bytes(), raw, f"{p.name} is frozen history, left as is")
            frozen = {f["file"]: f for f in res["frozen"]}
            self.assertEqual(set(frozen), {f"reviews/{n}" for n in migrate.FROZEN_LEDGERS})
            self.assertEqual(frozen["reviews/repair-record.md"]["late_rows"], 2)
            self.assertEqual(frozen["reviews/sprint-review-record.md"]["late_rows"], 1)
            self.assertIsNone(frozen["reviews/signoff-record.md"]["late_rows"],
                              "only the two ledgers the historical licence reads are counted")
            text = migrate.render(res)
            self.assertIn(f"2 row(s) dated on or after {on} no longer answer a REJECT", text)
            self.assertIn(f"1 row(s) dated on or after {on} no longer cover a unit", text)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_every_retired_surface_is_really_gone(self) -> None:
        """The registries are facts about this tree, checked rather than trusted: no retired key
        keeps a shipped default or a reader, and no frozen ledger keeps a writer. Yield: on the
        round-1 base (before the deletion units landed) it names three keys still read and four
        ledgers still written, which `migrate` would have stripped and called frozen.
        MUTANTS: register a key config-defaults still declares or a script still reads; call a
        ledger frozen that `critic.py` still appends to."""
        defaults = yaml.safe_load((_SCRIPTS.parent / "templates" / "config-defaults.yaml")
                                  .read_text(encoding="utf-8"))
        for key in sdlc_md.RETIRED_CONFIG_KEYS:
            self.assertFalse(migrate._drop(defaults, key), f"{key} still has a shipped default")
            self.assertEqual(_key_readers(key), [], f"{key} is still read")
        self.assertEqual(_ledger_writers(), [], "a frozen ledger is still written")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_every_default_gone_since_the_last_release_is_registered(self) -> None:
        """The registry's other half, derived from history: a `config-defaults.yaml` key the last
        release shipped and this tree dropped is registered (itself or its block), so `migrate`
        strips it from a project that set it. Yield: against v5.1.0 it found
        `review.plan_falsifiability`, `review.repair_plan_gate` and
        `review.repair_design_threshold` unregistered. Skipped where git or a tag is absent.
        MUTANT: drop one of those three from `sdlc_md.RETIRED_CONFIG_KEYS`."""
        rel = ".claude/skills/sdlc-studio/templates/config-defaults.yaml"
        repo = _SCRIPTS.parents[3]
        try:
            tag = gitutil.git(["describe", "--tags", "--abbrev=0", "--match", "v*"], repo,
                              text=True).stdout.strip()
            old = yaml.safe_load(gitutil.git(["show", f"{tag}:{rel}"], repo, text=True).stdout)
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("no git history or release tag to compare against")

        def flat(d, pre=""):
            return {k for key, v in (d or {}).items() for k in
                    {pre + key} | (flat(v, f"{pre}{key}.") if isinstance(v, dict) else set())}
        gone = flat(old) - flat(yaml.safe_load((repo / rel).read_text(encoding="utf-8")))
        unregistered = sorted(k for k in gone if not any(
            k == r or k.startswith(r + ".") for r in sdlc_md.RETIRED_CONFIG_KEYS))
        self.assertEqual(unregistered, [], f"dropped from the defaults since {tag}, unregistered")

    def test_a_workspace_with_nothing_retired_is_left_alone(self) -> None:
        """AC6. MUTANT: a stripper that rewrites a config holding no retired key (a
        parse-and-dump, or a normalised trailing newline)."""
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            _w(root, "sdlc-studio/.version", VERSION)
            _w(root, "sdlc-studio/.config.yaml",
               "# v4 consuming project\nschema_version: 2\nconformance:\n  adopt_after: 1   "
               "# grandfathered\n\nreview:\n  policy: block\n")
            _w(root, "sdlc-studio/definition-of-done.md",
               "# Definition of Done\n\n## Story\n\n- [ ] Criteria pass [check: story.verify-ac]"
               "\n- [ ] A human-judged item")
            _w(root, "AGENTS.md", "# AGENTS.md\n\nRun `/sdlc-studio status` first.\n")
            _w(root, "CLAUDE.md", "# CLAUDE.md\n\n@AGENTS.md\n")
            _w(root, "sdlc-studio/stories/US0001-a.md",
               "# US0001: A\n\n> **Status:** Done\n> **Epic:** EP0001\n\n"
               "## Acceptance Criteria\n\n### AC1: works\n\n- **Verify:** manual look\n")
            _w(root, "sdlc-studio/stories/US0002-b.md",
               "# US0002: B\n\n> **Status:** Draft\n> **Epic:** EP0001\n")

            def checks() -> list:
                out = []
                for script, verb in (("conformance.py", "check"), ("validate.py", "check")):
                    proc = subprocess.run([sys.executable, str(_SCRIPTS / script), verb,
                                           "--root", str(root), "--format", "json"],
                                          capture_output=True, text=True, timeout=120)
                    report = json.loads(proc.stdout)
                    report.pop("generated_at", None)   # the run's clock, not a result
                    out.append((proc.returncode, report))
                return out

            before, results = _snapshot(root), checks()
            res = _cli(root, "--apply")
            after = _snapshot(root)
            changed = {k for k in before.keys() | after.keys() if before.get(k) != after.get(k)}
            self.assertEqual(changed, {"sdlc-studio/.version"}, "only .version changes")
            self.assertEqual(_retired(res), [])
            self.assertEqual([h for h in res["needs_human"] if h["kind"] == "retired-surface"], [])
            self.assertEqual(checks(), results,
                             "conformance and validate read identically before and after")


if __name__ == "__main__":
    unittest.main()
