"""BG0831: the configuration reference documents only keys the code honours.

Three drifts. `reference-config.md` documented `sprint.split_above`, but the split threshold is
read from `sprint.points_split_above`, so the documented key changed nothing. `review.policy:
carry-forward` was documented as filing a REJECT's findings and shipping, but nothing outside
tests called the carry-forward module since the lean loop began carrying every unit at the round
cap; the key is retired (migrate strips it) and the module deleted. And the defaults' comment on
`review.max_rounds` said two consumers read it, when only critic.py's round cap does.

Driven through the shipped CLIs (`sprint.py plan`, `migrate.py --apply`) in throwaway trees.

BG1497 adds the converse: every key the scripts read through `config.get` is named in
reference-config.md and declared in config-defaults.yaml, found by reading the scripts' source,
and the two keys that bug names carry the defaults the code uses.
"""
# test-census-subject: .claude/skills/sdlc-studio/reference-config.md
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
SKILL = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
from lib import sdlc_md  # noqa: E402

try:
    import yaml
    HAVE_YAML = True
except ImportError:  # pragma: no cover - config is read through PyYAML
    HAVE_YAML = False


def _env() -> dict:
    return {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}


def _cli(script: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], capture_output=True,
                          text=True, timeout=300, check=False, env=_env())


def _w(root: Path, rel: str, text: str) -> Path:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return p


def _pointed_bug(root: Path, points: int) -> None:
    _w(root, "src/widget.py", "x = 1\n")
    _w(root, "sdlc-studio/bugs/BG0001-x.md",
       "# BG0001: b\n\n> **Status:** Open\n> **Severity:** Medium\n> **Affects:** src/widget.py\n"
       f"> **Points:** {points}\n\n## Acceptance Criteria\n\n### AC1: it behaves\n\n"
       "- **Given** the recorded state\n- **Verify:** shell true\n")


def _rows(text: str) -> list[str]:
    """The setting names a reference table documents: the first cell of each table row."""
    return re.findall(r"^\|\s*`([a-z_]+(?:\.[a-z_]+)+)`\s*\|", text, re.M)


REFERENCE = SKILL / "reference-config.md"
DEFAULTS = SKILL / "templates" / "config-defaults.yaml"


def _str_constants(tree: ast.Module) -> dict:
    """Module-level `NAME = <literal>` assignments, so a key or a default spelt as a named
    constant is read by its value."""
    out = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1 \
                and isinstance(node.targets[0], ast.Name):
            try:
                out[node.targets[0].id] = ast.literal_eval(node.value)
            except ValueError:
                pass
    return out


#: The calls a script reads its configuration through: `config.get` and
#: `config.feature_enabled` (which reads `<feature>.enabled`) over the merged configuration,
#: `config.load_config`, the whole of it, and `project_override`, the project's own file.
READERS = ("get", "feature_enabled", "load_config", "project_override")
_DEFS = (ast.FunctionDef, ast.AsyncFunctionDef)


def _reader(node) -> str | None:
    """Which of `READERS` a call is, or None; a `get` counts only as `config.get`."""
    if not isinstance(node, ast.Call):
        return None
    f = node.func
    name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
    if name == "get" and getattr(getattr(f, "value", None), "id", None) != "config":
        return None
    return name if name in READERS else None


class _Script:
    """One script, and what a key it reads is resolved against: its module constants, a
    sibling's, the loops and parameters a name is bound by, and the blocks it reads whole."""

    def __init__(self, scripts: Path, path: Path) -> None:
        self.scripts, self.rel = scripts, str(path.relative_to(scripts))
        self.tree = ast.parse(path.read_text(encoding="utf-8"))
        self.consts = _str_constants(self.tree)
        self.calls = [n for n in ast.walk(self.tree) if isinstance(n, ast.Call)]
        self.top, self.helpers, self.assigns = set(), {}, {}
        self.live = any(_reader(c) for c in self.calls)
        if not self.live:
            return
        self.parent = {c: p for p in ast.walk(self.tree) for c in ast.iter_child_nodes(p)}
        for s in ast.walk(self.tree):
            if isinstance(s, ast.Assign) and len(s.targets) == 1 \
                    and isinstance(s.targets[0], ast.Name):
                self.assigns.setdefault((self._scope(s), s.targets[0].id), []).append(s.value)
        # A name spelt as a top-level key read whole is that block, wherever it is bound.
        self.top = {v for c in self.calls if _reader(c) in ("get", "project_override")
                    and len(c.args) > 1 for v in self.values(c.args[1]) or [] if "." not in v}
        # A function holding a reader that returns a block is a helper returning that block.
        for c in self.calls:
            fn = self._scope(c) if _reader(c) else None
            for ret in (n for n in ast.walk(fn) if isinstance(n, ast.Return)) if fn else ():
                got = self.block(ret.value) if ret.value is not None else None
                if got is not None:
                    self.helpers[fn.name] = got

    def _scope(self, node):
        while node in self.parent:
            node = self.parent[node]
            if isinstance(node, _DEFS):
                return node
        return None

    def _up(self, node):
        while node in self.parent and not isinstance(node, _DEFS):
            node = self.parent[node]
            yield node

    def _assigned(self, name: ast.Name) -> list:
        """The values the enclosing function, or the module, assigns to `name`."""
        return self.assigns.get((self._scope(name), name.id), [])

    def values(self, node, depth: int = 0) -> list | None:
        """Every string `node` can hold, or None when any one of them is out of reach."""
        if depth > 12 or node is None:
            return None
        if isinstance(node, ast.Constant):
            return [node.value] if isinstance(node.value, str) else None
        if isinstance(node, ast.JoinedStr):
            out = [""]
            for part in node.values:
                got = [part.value] if isinstance(part, ast.Constant) else \
                    self.values(part.value, depth + 1)
                if got is None:
                    return None
                out = [head + str(tail) for head in out for tail in got]
            return out
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            for path in (self.scripts / f"{node.value.id}.py",
                         self.scripts / "lib" / f"{node.value.id}.py"):
                if path.is_file():
                    got = _str_constants(ast.parse(path.read_text(encoding="utf-8")))
                    return [got[node.attr]] if isinstance(got.get(node.attr), str) else None
            return None
        if not isinstance(node, ast.Name):
            return None
        for up in self._up(node):
            for gen in [up] if isinstance(up, ast.For) else getattr(up, "generators", []):
                first = gen.target.elts[0] if isinstance(gen.target, ast.Tuple) else gen.target
                if getattr(first, "id", None) == node.id:
                    return self._items(gen.iter, depth)
        fn = self._scope(node)
        if fn is not None and node.id in [a.arg for a in fn.args.args]:
            return self._passed(fn, node.id, depth)
        if isinstance(self.consts.get(node.id), str):
            return [self.consts[node.id]]
        got = self._assigned(node)
        return self.values(got[0], depth + 1) if len(got) == 1 else None

    def _items(self, it, depth: int) -> list | None:
        """The strings a loop over `it` binds: a literal, or a module constant, of strings."""
        if isinstance(it, ast.Call) and getattr(it.func, "attr", None) in ("items", "keys"):
            it = it.func.value
        if isinstance(it, (ast.Tuple, ast.List, ast.Set)):
            got = [self.values(e, depth + 1) for e in it.elts]
            return None if None in got else [v for vs in got for v in vs]
        held = self.consts.get(getattr(it, "id", None))
        if isinstance(held, (tuple, list, set, dict)) and all(isinstance(v, str) for v in held):
            return list(held)
        return None

    def _passed(self, fn, param: str, depth: int) -> list | None:
        """Every value this script's callers of `fn` pass as `param`, its default where a caller
        leaves it out; None with no caller, or with one out of reach."""
        names = [a.arg for a in fn.args.args]
        defaults = dict(zip(names[len(names) - len(fn.args.defaults):], fn.args.defaults))
        at = names.index(param) - (names[:1] == ["self"])
        out = []
        for call in (c for c in self.calls
                     if getattr(c.func, "id", getattr(c.func, "attr", None)) == fn.name):
            arg = next((k.value for k in call.keywords if k.arg == param),
                       call.args[at] if at < len(call.args) else defaults.get(param))
            got = self.values(arg, depth + 1)
            if got is None:
                return None
            out += got
        return out or None

    def block(self, node, depth: int = 0) -> tuple | None:
        """The key path of the block `node` holds, `()` for the whole configuration, or None."""
        if depth > 12:
            return None
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.Or):
            return self.block(node.values[0], depth + 1)
        if isinstance(node, ast.IfExp):
            got = self.block(node.body, depth + 1)
            return got if got is not None else self.block(node.orelse, depth + 1)
        kind = _reader(node)
        if kind == "load_config":
            return ()
        if kind in ("get", "project_override"):
            got = self.values(node.args[1]) if len(node.args) > 1 else None
            return tuple(got[0].split(".")) if got and len(got) == 1 else None
        if isinstance(node, ast.Call) and getattr(node.func, "id", None) in self.helpers:
            return self.helpers[node.func.id]
        if isinstance(node, ast.Name):
            for value in self._assigned(node):
                got = self.block(value, depth + 1)
                if got is not None:
                    return got
            return (node.id,) if node.id in self.top else None
        path, subs = self.taken(node, depth)
        return path + (subs[0],) if path is not None and subs and len(subs) == 1 else None

    def taken(self, node, depth: int = 0) -> tuple:
        """`(block path, [keys])` for `<block>.get(<key>)` or `<block>[<key>]`, the keys None
        when out of reach; `(None, None)` for anything else."""
        if isinstance(node, ast.Call) and getattr(node.func, "attr", None) == "get" \
                and node.args and _reader(node) is None:
            base, key = node.func.value, node.args[0]
        elif isinstance(node, ast.Subscript):
            base, key = node.value, node.slice
        else:
            return None, None
        path = self.block(base, depth + 1)
        return path, (self.values(key) if path is not None else None)

    def reads(self) -> tuple:
        """`([(line, key)], [line])`: each key this script reads, and each read whose key the
        scan cannot resolve."""
        found, lost = [], []
        for node in ast.walk(self.tree) if self.live else ():
            kind, line = _reader(node), getattr(node, "lineno", 0)
            if kind in ("get", "feature_enabled", "project_override"):
                arg = node.args[1] if len(node.args) > 1 else None
                keys = self.values(arg)
                if keys is None and isinstance(arg, ast.JoinedStr) \
                        and isinstance(arg.values[0], ast.Constant):
                    keys = [arg.values[0].value.rstrip(".")]   # a map keyed at run time
                found += [(line, k + ".enabled" * (kind == "feature_enabled")) for k in keys or []]
                lost += [] if keys else [line]
            # A key out of reach on a block is a map keyed at run time (a model id), read as the
            # block the read that produced it already holds; on the whole configuration it is
            # a read out of reach, but in config.py, which is the reader itself.
            path, subs = self.taken(node)
            if subs:
                found += [(line, ".".join(path + (sub,))) for sub in subs]
            elif path == () and self.rel != "config.py":
                lost.append(line)
        return found, lost


def keys_read(scripts: Path = SCRIPTS) -> tuple:
    """`({config key: the first file:line reading it}, [file:line of each read out of reach])`
    over `scripts/*.py` and `scripts/lib/*.py`. A key is read when one of `READERS` is passed it
    as a string, a constant (a sibling script's too), a name assigned one, a loop over a literal
    or a constant, an f-string of those, or a parameter every caller in the script fills that
    way; and when `.get(<key>)` or `[<key>]` is taken on a block a reader returns, held in a
    name, returned by a helper, chained, or defaulted with `or` or `if`, as `<block>.<key>`. A key
    built at run time inside a block, a model id or an artefact type, reads as that block."""
    found, lost = {}, []
    for path in sorted([*scripts.glob("*.py"), *(scripts / "lib").glob("*.py")]):
        script = _Script(scripts, path)
        got, out = script.reads()
        for line, key in sorted(got):
            found.setdefault(key, f"{script.rel}:{line}")
        lost += [f"{script.rel}:{line}" for line in sorted(set(out))]
    return found, lost


_ABSENT = object()


def undocumented(keys: dict, reference: str, defaults: dict) -> list:
    """One line for each key the reference page does not name, and one for each the defaults do
    not declare (a null value declares it), each naming the key, where it is read and the file
    that lacks it."""
    out = []
    for key, where in sorted(keys.items()):
        if not re.search(rf"(?<![\w.]){re.escape(key)}(?!\w)", reference):
            out.append(f"{key} ({where}) is not in reference-config.md")
        cur = defaults
        for part in key.split("."):
            cur = cur.get(part, _ABSENT) if isinstance(cur, dict) else _ABSENT
        if cur is _ABSENT:
            out.append(f"{key} ({where}) is not in config-defaults.yaml")
    return out


class ConfigKeysReadTests(unittest.TestCase):
    """AC1-AC3."""

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_the_documented_split_key_is_the_one_read(self) -> None:
        """AC1. MUTANTS: (1) document `sprint.split_above` again - the row is found; (2) drop the
        `sprint.points_split_above` row - the documented key is missing; (3) read a key other than
        the one documented in `points_split_above()` - the unit over 5 plans.

        The unit is an 8, not the criterion's 6: `6` is off the modified Fibonacci scale, so it is
        refused as unsized ("lacks Points") whatever the threshold, and a 6 cannot tell a ceiling
        of 5 from the default 8 (mutant 3 survived it). An 8 is on the scale, legal by default
        and over a ceiling of 5, so only the configured threshold refuses it; a 5 is the control."""
        def plan(points: int) -> subprocess.CompletedProcess:
            with tempfile.TemporaryDirectory() as d:
                root = Path(d)
                _w(root, "sdlc-studio/.config.yaml", "sprint:\n  points_split_above: 5\n")
                _pointed_bug(root, points)
                return _cli("sprint.py", "plan", "--bugs", "Open", "--root", str(root),
                            "--no-fetch", "--skip-personas")
        r = plan(8)
        out = r.stdout + r.stderr
        self.assertNotEqual(0, r.returncode, "an 8-point unit planned under a ceiling of 5:\n" + out)
        self.assertIn("BG0001", r.stderr, out)
        self.assertNotIn("lacks Points", r.stderr, "refused as unsized, not as over the threshold")
        # The ceiling as the refusal states it: a bare "5" is satisfied by any temp path.
        self.assertIn("are above 5 points", r.stderr, "the refusal does not name the ceiling")
        self.assertRegex(r.stderr, r"BG0001\s+8 points\s+\(ceiling 5\)",
                         "the refused unit is not named against the configured ceiling")
        self.assertNotIn("batch:", r.stdout, "a plan was printed for a refused batch")
        control = plan(5)
        self.assertEqual(0, control.returncode, "a unit at the ceiling was refused:\n"
                         + control.stdout + control.stderr)
        rows = _rows((SKILL / "reference-config.md").read_text(encoding="utf-8"))
        self.assertIn("sprint.points_split_above", rows,
                      "reference-config.md does not document the key the code reads")
        self.assertNotIn("sprint.split_above", rows,
                         "reference-config.md documents `sprint.split_above`, which nothing reads")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_the_documented_risk_key_is_the_one_read(self) -> None:
        """The component map key `refine` reads is the one the reference and the defaults
        declare. MUTANT: the reader moves to another key -> the documented key changes nothing."""
        from lib import risk_class  # noqa: PLC0415
        self.assertEqual("risk.components", risk_class.CONFIG_KEY)
        self.assertIn(f"`{risk_class.CONFIG_KEY}` (default `{{}}`)",
                      (SKILL / "reference-config.md").read_text(encoding="utf-8"))
        self.assertIn("risk:\n  components: {}\n",
                      (SKILL / "templates" / "config-defaults.yaml").read_text(encoding="utf-8"))

    def test_review_policy_is_retired_not_documented(self) -> None:
        """AC2. MUTANTS: (1) leave `review.policy` out of `RETIRED_CONFIG_KEYS` - migrate keeps
        the line; (2) keep shipping `carry_forward.py`; (3) keep the `review.policy` row in
        reference-config.md, the `carry_forward.py` entry naming it in reference-scripts-review.md,
        or `policy:` under `review:` in config-defaults.yaml."""
        self.assertIn("review.policy", sdlc_md.RETIRED_CONFIG_KEYS)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cfg = _w(root, "sdlc-studio/.config.yaml",
                     "review:\n  policy: carry-forward\n  blocking_priority: high\n")
            r = _cli("migrate.py", "--apply", "--root", str(root))
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            after = yaml.safe_load(cfg.read_text(encoding="utf-8"))
            self.assertNotIn("policy", after.get("review") or {},
                             "migrate kept the retired review.policy key")
            self.assertEqual("high", after["review"]["blocking_priority"],
                             "migrate removed a key that is not retired")
            self.assertIn("review.policy", r.stdout, "the removal is not reported")
        self.assertFalse((SCRIPTS / "carry_forward.py").exists(), "carry_forward.py still ships")
        docs = [*SKILL.glob("reference-*.md"), *(SKILL / "help").rglob("*.md")]
        self.assertGreater(len(docs), 40, "premise: the reference and help pages were found")
        for path in docs:
            with self.subTest(doc=str(path.relative_to(SKILL))):
                self.assertNotIn("review.policy", path.read_text(encoding="utf-8"))
        defaults = yaml.safe_load((SKILL / "templates" / "config-defaults.yaml")
                                  .read_text(encoding="utf-8"))
        self.assertNotIn("policy", defaults.get("review") or {},
                         "config-defaults.yaml still declares review.policy")

    def test_max_rounds_comment_names_one_reader(self) -> None:
        """AC3. MUTANTS: (1) keep the two-consumer comment; (2) a comment that names no reader."""
        text = (SKILL / "templates" / "config-defaults.yaml").read_text(encoding="utf-8")
        lines = text.splitlines()
        at = next((i for i, ln in enumerate(lines) if "review.max_rounds" in ln), None)
        self.assertIsNotNone(at, "config-defaults.yaml says nothing about review.max_rounds")
        start = at
        while start > 0 and lines[start - 1].lstrip().startswith("#"):
            start -= 1
        end = at
        while end + 1 < len(lines) and lines[end + 1].lstrip().startswith("#"):
            end += 1
        comment = " ".join(ln.strip().lstrip("#").strip() for ln in lines[start:end + 1])
        self.assertIn("critic.py", comment, "the comment does not name critic.py as the reader")
        self.assertRegex(comment, r"\bonly reader\b",
                         "the comment does not say critic.py is the only reader")
        for stale in ("two consumers", "close-attempt"):
            self.assertNotIn(stale, comment, f"the comment still says {stale!r}:\n{comment}")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_require_ac_verification_is_retired_by_migrate(self) -> None:
        """BG1063 AC1. MUTANTS: (1) leave `require_ac_verification` out of `RETIRED_CONFIG_KEYS`
        - migrate keeps the line; (2) retire `quality.done_requires_verified` with it - the gate
        the key claimed to be is lost."""
        self.assertIn("require_ac_verification", sdlc_md.RETIRED_CONFIG_KEYS)
        self.assertIn("quality.done_requires_verified",
                      sdlc_md.RETIRED_CONFIG_KEYS["require_ac_verification"])
        self.assertNotIn("quality.done_requires_verified", sdlc_md.RETIRED_CONFIG_KEYS)
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            cfg = _w(root, "sdlc-studio/.config.yaml",
                     "require_ac_verification: true\nquality:\n  done_requires_verified: false\n")
            r = _cli("migrate.py", "--apply", "--root", str(root))
            self.assertEqual(0, r.returncode, r.stdout + r.stderr)
            after = yaml.safe_load(cfg.read_text(encoding="utf-8"))
            self.assertNotIn("require_ac_verification", after,
                             "migrate kept the retired require_ac_verification key")
            self.assertIs(False, after["quality"]["done_requires_verified"],
                          "migrate removed the key that replaced it")
            self.assertIn("require_ac_verification", r.stdout, "the removal is not reported")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_require_ac_verification_is_not_documented(self) -> None:
        """BG1063 AC2. MUTANTS: (1) name `require_ac_verification` again in any reference, help
        page or template; (2) declare it in config-defaults.yaml; (3) leave the gated-completion
        section naming neither the live key nor `transition.py`."""
        pages = [*SKILL.glob("reference-*.md"), *(SKILL / "help").rglob("*.md"),
                 *(SKILL / "templates").rglob("*")]
        pages = [p for p in pages if p.is_file()]
        self.assertGreater(len(pages), 100, "premise: the pages were found")
        for path in pages:
            with self.subTest(doc=str(path.relative_to(SKILL))):
                self.assertNotIn("require_ac_verification", path.read_text(encoding="utf-8"))
        defaults = yaml.safe_load((SKILL / "templates" / "config-defaults.yaml")
                                  .read_text(encoding="utf-8"))
        self.assertNotIn("require_ac_verification", defaults)
        text = (SKILL / "reference-verify.md").read_text(encoding="utf-8")
        gated = text.split("## Gated Completion", 1)[1].split("\n### ", 1)[0]
        self.assertIn("quality.done_requires_verified", gated)
        self.assertIn("transition.py", gated)

    def test_fresh_session_is_documented_with_the_default_the_code_uses(self) -> None:
        """BG1497 AC1. The reference's `sprint.fresh_session` row states the default and every
        mode `sprint.py` reads. MUTANTS: the row deleted; its default `block` or `off`; a mode
        dropped from its notes; the code's default changed while the row stays."""
        code = _str_constants(ast.parse((SCRIPTS / "sprint.py").read_text(encoding="utf-8")))
        default, modes = code["FRESH_SESSION_DEFAULT"], code["FRESH_SESSION_MODES"]
        self.assertEqual(("warn", ("warn", "block", "off")), (default, modes),
                         "premise: the modes and default sprint.py reads")
        rows = re.findall(r"^\|\s*`sprint\.fresh_session`\s*\|\s*`([^`]*)`\s*\|(.*)\|\s*$",
                          REFERENCE.read_text(encoding="utf-8"), re.M)
        self.assertEqual(1, len(rows), "reference-config.md has no one `sprint.fresh_session` row")
        documented, notes = rows[0]
        self.assertEqual(default, documented, "the row's default is not the one sprint.py uses")
        for mode in modes:
            self.assertIn(f"`{mode}`", notes, f"the row does not document `{mode}`")

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_copilot_billing_ships_with_the_default_the_code_uses(self) -> None:
        """BG1497 AC2. config-defaults.yaml declares `pricing.copilot_billing` as the value
        lib/prices.py falls back to, and the shipped `pricing` block prices an unconfigured
        project exactly as no block at all. MUTANTS: the key deleted; `requests` shipped; any
        other shipped `pricing` value changed (`stale_after_days: 60`)."""
        from lib import prices  # noqa: PLC0415
        block = (yaml.safe_load(DEFAULTS.read_text(encoding="utf-8")) or {}).get("pricing")
        self.assertIsInstance(block, dict, "config-defaults.yaml declares no `pricing` block")
        self.assertIn(prices.COPILOT_BILLING, block)
        self.assertEqual(prices.TOKEN_BILLING, block[prices.COPILOT_BILLING])
        bare = prices.load(pricing={})
        self.assertEqual(bare, prices.load(pricing=block), "the shipped block changes the prices")
        with tempfile.TemporaryDirectory() as d:
            unconfigured = prices.load(Path(d))
        self.assertEqual(bare, unconfigured, "an unconfigured project is not priced as no block")
        self.assertEqual(("tokens", ()), (unconfigured.copilot_billing,
                                         unconfigured.billed_by_request))

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_a_key_the_code_reads_must_be_in_the_reference_and_the_defaults(self) -> None:
        """BG1497 AC3. Every key the scripts read, through any of `READERS` on any route, is
        named in reference-config.md and declared in config-defaults.yaml, and no read is out
        of the scan's reach. MUTANTS: a key the scan sees dropped from either file
        (`report.enabled`, `pricing.copilot_billing`, `version_check.ttl_hours`,
        `complexity.cognitive_high`); `project_override`, `feature_enabled` or `load_config`
        left out of `READERS`; the scan losing its named-constant keys, a sibling's constant,
        its loops, its helper parameters, its helper-returned blocks, its chained or `or`- or
        `if`-defaulted blocks, its f-string block, its reads out of reach or its first reader's
        line; a near miss (`a.bc`, `x.a.b`) read as naming the key; a declared null read as
        undeclared; a block read through a helper renamed in a script (`route.py`,
        `.get("models")` to `.get("modelz")`)."""
        defaults = yaml.safe_load(DEFAULTS.read_text(encoding="utf-8")) or {}
        here = {"a.b": "x.py:1"}
        self.assertEqual([], undocumented(here, "set `a.b` to 1", {"a": {"b": None}}))
        for page in ("nothing", "`a.bc`", "`x.a.b`", "`a`"):
            with self.subTest(page=page):
                self.assertEqual(["a.b (x.py:1) is not in reference-config.md"],
                                 undocumented(here, page, {"a": {"b": 1}}))
        for declared in ({}, {"a": {}}, {"a": None}, {"a": {"c": 1}}):
            with self.subTest(declared=declared):
                self.assertEqual(["a.b (x.py:1) is not in config-defaults.yaml"],
                                 undocumented(here, "`a.b`", declared))
        with tempfile.TemporaryDirectory() as d:
            _w(Path(d), "lib/reader.py",
               'KEY = "blk.named"\nSUB = "via_constant"\n'
               'def f(root, n):\n'
               '    config.get(root, "top.literal", 1)\n'
               '    config.get(root, KEY)\n'
               '    config.get(root, f"top.{n}")\n'
               '    blk = config.get(root, "blk", {})\n'
               '    other.get("unread")\n'
               '    config.get(root, "top.literal")\n'
               '    blk.get("via_get")\n'
               '    return blk.get("via_get"), blk[SUB], blk[n]\n')
            _w(Path(d), "unscanned/elsewhere.py", 'config.get(root, "never.seen")\n')
            _w(Path(d), "names.py", 'SIBLING = "sib.key"\n')
            _w(Path(d), "routes.py",
               'import names\nMOMENTS = ("first", "second")\n'
               'def _routing(root):\n'
               '    return config.get(root, "routing", None) or {}\n'
               'def _cfg(root, key, default):\n'
               '    return config.get(root, f"param.{key}", default)\n'
               'def g(root, flag, name):\n'
               '    _cfg(root, "one", 1)\n'
               '    _cfg(root, key="two", default=2)\n'
               '    sdlc_md.project_override(root, "own.file", 0)\n'
               '    config.feature_enabled(root, "feat")\n'
               '    for m in MOMENTS:\n'
               '        config.get(root, f"moment.{m}")\n'
               '    config.get(root, names.SIBLING)\n'
               '    whole = config.load_config(root)\n'
               '    sizing = ((whole.get("story") or {}).get("sizing") or {})\n'
               '    sizing.get("max_ac")\n'
               '    _routing(root).get("models")\n'
               '    picked = config.get(root, "cond", None) if flag else {}\n'
               '    picked.get("k")\n'
               '    config.get(root, name)\n'
               '    whole[name]\n')
            self.assertEqual(({"top.literal": "lib/reader.py:4", "blk.named": "lib/reader.py:5",
                               "top": "lib/reader.py:6", "blk": "lib/reader.py:7",
                               "blk.via_get": "lib/reader.py:10",
                               "blk.via_constant": "lib/reader.py:11",
                               "routing": "routes.py:4", "param.one": "routes.py:6",
                               "param.two": "routes.py:6", "own.file": "routes.py:10",
                               "feat.enabled": "routes.py:11", "moment.first": "routes.py:13",
                               "moment.second": "routes.py:13", "sib.key": "routes.py:14",
                               "story": "routes.py:16", "story.sizing": "routes.py:16",
                               "story.sizing.max_ac": "routes.py:17",
                               "routing.models": "routes.py:18", "cond": "routes.py:19",
                               "cond.k": "routes.py:20"},
                              ["routes.py:21", "routes.py:22"]), keys_read(Path(d)))
        keys, lost = keys_read()
        self.assertEqual([], lost, "a read the scan cannot resolve to a key")
        for key in ("sprint.fresh_session", "pricing.copilot_billing", "routing.models",
                    "complexity.cognitive_high", "version_check.ttl_hours", "triage.enabled",
                    "triage.session_cap", "test_execution.at_release", "story_quality.sizing.max_ac",
                    "status_vocab", "report.enabled"):
            self.assertIn(key, keys, "premise: the scan finds each route's keys")
        self.assertEqual([], undocumented(keys, REFERENCE.read_text(encoding="utf-8"), defaults))


if __name__ == "__main__":
    unittest.main()
