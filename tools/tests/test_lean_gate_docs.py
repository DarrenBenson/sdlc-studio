"""US1084: the TRD and the TSD describe the gate as the hooks and gate.py actually run it.

Every fact is read from the file it describes, never typed here (LL0043):
- the hooks come from `.githooks/`, and each hook's lanes from its own `--list`;
- the boundaries come from `.githooks/pre-push` and the host path's `tools/remote-gate.sh`;
- the manual release steps are the release commands the runbook (reference-sprint-toolchain.md,
  section 6) and SKILL.md's release-tag row name, less any a hook or a workflow calls;
- the `.local` writes come from gate.py and tools/gate_timing.py;
- the budgets come from gate.py and the commit-msg hook.

Each derived set first asserts a member known to be in it, so an empty derivation fails
instead of passing vacuously. The one fact typed here is git's own order of the three hooks,
which belongs to git, not to this repository.
"""
# test-census-subject: sdlc-studio/tsd.md
from __future__ import annotations

import os
import re
import subprocess
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TRD = REPO / "sdlc-studio" / "trd.md"
TSD = REPO / "sdlc-studio" / "tsd.md"
HOOKS = REPO / ".githooks"
SKILL = REPO / ".claude" / "skills" / "sdlc-studio"
GATE_PY = SKILL / "scripts" / "gate.py"

#: The order git runs these hooks in during a commit and a push (githooks(5)).
GIT_ORDER = ("pre-commit", "commit-msg", "pre-push")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
    """The body under the first heading whose title starts with `heading`, up to the next heading
    of the same or a higher level."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^(#+)\s+(.*)$", line)
        if m and m.group(2).startswith(heading):
            level, out = len(m.group(1)), []
            for nxt in lines[i + 1:]:
                n = re.match(r"^(#+)\s", nxt)
                if n and len(n.group(1)) <= level:
                    break
                out.append(nxt)
            return "\n".join(out)
    raise AssertionError(f"no section headed {heading!r}")


def _blocks(text: str) -> list[str]:
    """Paragraphs and list items: each numbered or bulleted item is a block of its own, as is each
    table row, so a claim is judged with the words beside it and no further."""
    blocks, cur = [], []
    for line in text.splitlines():
        starts = bool(re.match(r"^\s*(\d+\.|[-*]|\|)\s", line))
        if not line.strip() or (starts and cur):
            if cur:
                blocks.append(" ".join(cur))
            cur = [line.strip()] if line.strip() else []
        else:
            cur.append(line.strip())
    if cur:
        blocks.append(" ".join(cur))
    return blocks


def _sentences(text: str) -> list[str]:
    """Each block's sentences. Code spans are held out of the split, so `gate.py --boundary push`
    stays inside the sentence it is named in."""
    out = []
    for block in _blocks(text):
        spans: list[str] = []

        def hold(m: re.Match) -> str:
            spans.append(m.group(0))
            return f"\x00{len(spans) - 1}\x00"

        masked = re.sub(r"`[^`]*`", hold, block)
        for s in re.split(r"(?<=[.;:!?])\s+(?=[A-Z(\x00*\"'])", masked):
            out.append(re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], s))
    return out


#: A tag push, however a sentence words it; a run verb; a negation.
TAG_PUSH = r"(?i)\btag push|pushing a tag|a pushed tag|push(?:es|ing)? (?:of )?a tag"
RUNS = r"(?i)\b(?:runs?|triggers?|executes?|calls?)\b"
NEGATED = r"(?i)\bnot\b|\bno\b|\bnever\b|n't\b"


def _hooks() -> list[str]:
    return sorted(p.name for p in HOOKS.iterdir() if p.is_file() and os.access(p, os.X_OK))


def _listing(hook: str) -> list[str]:
    """The lane keys a hook's own `--list` prints, run as the hook documents it: it runs nothing.
    Run in THIS repository on purpose, since its lanes are what the documents describe, with git's
    repository-locating variables dropped so no caller's GIT_DIR can point it elsewhere."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    r = subprocess.run([str(HOOKS / hook), "--list"], cwd=REPO, env=env, capture_output=True,
                       text=True, timeout=60)
    assert r.returncode == 0, r.stderr
    return [line.split("\t", 1)[0] for line in r.stdout.splitlines() if "\t" in line]


def _stage(hook: str) -> str:
    """The TSD pipeline stage that names `.githooks/<hook>`."""
    found = [b for b in _blocks(_section(_read(TSD), "Pipeline Stages")) if f".githooks/{hook}" in b]
    assert found, f"no TSD pipeline stage names .githooks/{hook}"
    return found[0]


class GateDocsTests(unittest.TestCase):

    def test_every_hook_is_named_in_run_order(self) -> None:
        """AC1. Mutants: a hook dropped from either document; the TSD's stages out of git's order,
        or one stage naming several hooks so first mentions fake the order; a hook's lanes restated
        in either document instead of its `--list` named."""
        hooks = _hooks()
        self.assertIn("commit-msg", hooks, "the hooks were not read from .githooks/")
        unknown = [h for h in hooks if h not in GIT_ORDER]
        self.assertEqual(unknown, [], "a hook this test does not know git's order for")
        for doc in (TRD, TSD):
            for hook in hooks:
                with self.subTest(doc=doc.name, hook=hook):
                    self.assertIn(f".githooks/{hook}", _read(doc))
        named = []
        for block in _blocks(_section(_read(TSD), "Pipeline Stages")):
            in_block = [h for h in hooks if f".githooks/{h}" in block]
            self.assertLessEqual(len(in_block), 1, f"one TSD pipeline stage names several hooks: {in_block}")
            named += in_block
        self.assertEqual(named, [h for h in GIT_ORDER if h in hooks],
                         "the TSD's pipeline stages do not give each hook a stage of its own, in git's order")
        listed = [h for h in hooks if re.search(r'"\$\{1:-\}"\s*=\s*"--list"', _read(HOOKS / h))]
        self.assertIn("pre-commit", listed, "the hooks with a --list were not read")
        for hook in listed:
            lanes = _listing(hook)
            self.assertIn("gate" if hook == "pre-commit" else "message-refs", lanes)
            for doc in (TRD, TSD):
                with self.subTest(doc=doc.name, listing=hook):
                    self.assertIn(f".githooks/{hook} --list", _read(doc))
                    for block in _blocks(_read(doc)):
                        if f".githooks/{hook}" in block:
                            restated = [k for k in lanes if f"`{k}`" in block]
                            self.assertLess(len(restated), 3, f"{doc.name} restates {hook}'s lanes "
                                            f"rather than naming its --list: {restated}")

    def test_each_boundary_the_hook_runs_is_named(self) -> None:
        """AC2. Mutants: a boundary the hook runs left unnamed, or swapped with the other so each
        sits beside the wrong push; the push stage without the prerequisite check or the red-main
        acknowledgement, out of the hook's order, or crediting the hook's known-issues check to the
        gate; the whole gate or suite said to run on every commit; the commit's budget misstated."""
        hook = _read(HOOKS / "pre-push")
        tag_b = re.search(r'\*"\s*\$commit\s*"\*\)\s*at="(\w+)"', hook).group(1)
        push_b = re.search(r'\*\)\s*at="(\w+)"\s*;;\s*esac', hook).group(1)
        boundaries = set(re.findall(r"--boundary (\w+)", hook)) | {tag_b, push_b}
        host = re.search(r'case "\$boundary" in ([\w|]+)\)', _read(REPO / "tools" / "remote-gate.sh"))
        boundaries |= set(host.group(1).split("|"))
        self.assertTrue({"push", "release"} <= boundaries, boundaries)
        self.assertEqual(boundaries, {tag_b, push_b}, "a boundary with no push or tag beside it")
        for doc in (TRD, TSD):
            for b in (push_b, tag_b):
                other = tag_b if b == push_b else push_b
                with self.subTest(doc=doc.name, boundary=b):
                    alone = []
                    for s in _sentences(_read(doc)):
                        if f"--boundary {b}" not in s or f"--boundary {other}" in s:
                            continue
                        rest = s.replace(f"--boundary {b}", "")
                        tag_named = re.search(r"(?i)\btag", rest)
                        if (b == tag_b and tag_named) or (b == push_b and re.search(r"(?i)\bpush", rest) and not tag_named):
                            alone.append(s)
                    self.assertTrue(alone, f"{doc.name} names --boundary {b} in no sentence of its own "
                                    f"beside the {'tag' if b == tag_b else 'branch'} push that runs it")
        push = _stage("pre-push")
        for named in ("gate_prereqs.py", "SDLC_PUSH_ACK_RED", "D0181", "full suite"):
            self.assertIn(named, push, f"the TSD's push stage does not name {named}")
        steps = [("gate_prereqs.py", "python3 tools/gate_prereqs.py check"),
                 ("known_issues.py", "python3 tools/known_issues.py check"),
                 ("SDLC_PUSH_ACK_RED", "gh run list"), ("--boundary", '/gate.py" --boundary')]
        in_hook = [hook.find(code) for _, code in steps]
        self.assertTrue(all(i >= 0 for i in in_hook), f"the hook's steps were not read: {in_hook}")
        order = [name for (name, _), _i in sorted(zip(steps, in_hook), key=lambda x: x[1])]
        self.assertEqual([push.find(name) for name in order], sorted(push.find(name) for name in order),
                         f"the TSD's push stage does not give the hook's steps in its order: {order}")
        self.assertTrue(all(push.find(name) >= 0 for name in order), "the push stage misses a step of the hook")
        for s in _sentences(push):
            if "known_issues.py" in s:
                self.assertNotIn("--boundary", s, "the known-issues check, which the hook runs, is credited to the gate")
        budget = re.search(r"^commit_budget=(\d+)", _read(HOOKS / "commit-msg"), re.M).group(1)
        commit = _stage("commit-msg")
        self.assertIn("select", commit, "the commit stage does not say only the selected suites run")
        self.assertIn(f"{budget}-second", commit, "the commit stage does not state the hook's budget")
        self.assertRegex(commit, r"advisory|not refused", "the commit's budget is not called advisory")
        every = (r"(?i)\b(?:whole|full|entire|complete)\s+(?:gate|suite)\b[^.]*\bevery commit"
                 r"|\bevery commit\b[^.]*\b(?:whole|full|entire|complete)\s+(?:gate|suite)\b")
        for doc in (TRD, TSD):
            for s in _sentences(_read(doc)):
                if re.search(every, s):
                    self.assertRegex(s, NEGATED, f"{doc.name} says the whole gate or suite runs on every commit: {s}")

    def test_unrun_release_steps_are_named_manual(self) -> None:
        """AC3. Mutants: a sentence, however worded, saying a tag push runs a release step or these
        steps; one of the steps dropped, or not called manual; a release-gate row made automatic."""
        runbook = _section(_read(SKILL / "reference-sprint-toolchain.md"), "6. Release")
        steps = set(re.findall(r"`((?:release_cut|gate)\.py [\w-]+)", runbook))
        for row in _read(SKILL / "SKILL.md").splitlines():
            if "release tag" in row:
                steps |= {m.replace("scripts/", "") for m in re.findall(r"`(scripts/gate\.py --release)`", row)}
        callers = "\n".join(_read(p) for p in [*HOOKS.iterdir(), *(REPO / ".github" / "workflows").glob("*.yml")]
                            if p.is_file())

        def called(step: str) -> bool:
            script, sub = step.split()
            return bool(re.search(rf"{re.escape(script)}[^\n]*\s{re.escape(sub)}(?=[\s\"']|$)", callers, re.M))

        manual = sorted(s for s in steps if not called(s))
        self.assertIn("release_cut.py tag-check", manual, "the release steps were not read from the runbook")
        self.assertIn("gate.py --release", manual, "SKILL.md's release-tag row was not read")
        tsd = _read(TSD)
        for step in manual:
            with self.subTest(step=step):
                self.assertTrue(any(step in b and re.search(r"manual", b, re.I) for b in _blocks(tsd)),
                                f"the TSD does not name {step} as a manual step")
        named = r"|".join(re.escape(s) for s in manual) + r"|these steps|each of these|the release steps"
        for doc in (TRD, TSD):
            for s in _sentences(_read(doc)):
                if re.search(TAG_PUSH, s) and re.search(named, s) and re.search(RUNS, s):
                    self.assertRegex(s, NEGATED, f"{doc.name} says a tag push runs a manual release step: {s}")
        stage = [b for b in _blocks(tsd) if all(step in b for step in manual)]
        self.assertTrue(stage, "no one TSD block names every manual release step")
        for s in _sentences(stage[0]):
            if re.search(TAG_PUSH, s):
                self.assertRegex(s, NEGATED, f"the manual-steps stage says a tag push runs them: {s}")
        rows = [r for r in tsd.splitlines() if r.startswith("|") and "gate.py --release" in r]
        self.assertGreaterEqual(len(rows), 2, "the TSD's quality-gate rows for the release gate were not read")
        for row in rows:
            self.assertRegex(row, r"(?i)manual", f"a TSD row names the release gate without calling it manual: {row}")

    def test_the_gates_local_writes_are_named(self) -> None:
        """AC4. Mutants: a `.local` path gate.py writes left unnamed; the gate said, in any wording,
        to write nothing or to be read-only."""
        sources = _read(GATE_PY) + _read(REPO / "tools" / "gate_timing.py")
        writes = set(re.findall(r'"sdlc-studio/\.local/([\w.-]+)"', sources))
        writes |= set(re.findall(r'"\.local"\s*/\s*"([\w.-]+)"', sources))
        self.assertTrue({"gate-suite-verdict.json", "gate-timings.json"} <= writes, writes)
        trd = _read(TRD)
        for name in sorted(writes):
            with self.subTest(path=name):
                self.assertIn(name, trd)
        # The gate as the subject of the denial, or the hook-safety inference drawn from it, which
        # TSD-23 wrote with the gate only in its section's heading. "The read path is read-only"
        # names another subject and is not a denial of the gate's writes.
        subject = r"\bgate(?:\.py)?`?(?:\s+\w+){0,3}\s+"
        denies = (rf"(?i){subject}(?:is|stays|remains)\s+(?:read-only|side-effect-free)"
                  rf"|{subject}(?:writes nothing|never writes|writes no\b|does not write|writes none)"
                  r"|read-only,? and (?:therefore |so |thus )?hook-safe")
        for doc in (TRD, TSD):
            for s in _sentences(_read(doc)):
                self.assertNotRegex(s, denies, f"{doc.name} denies the gate's writes")

    def test_the_gate_cost_row_states_the_declared_budget(self) -> None:
        """AC5. Mutants: 'Sub-second' restored for the gate, in the TRD's row, the TSD's NFR row or
        its prose; a budget stated that gate.py does not declare."""
        budget = re.search(r"^GATE_BUDGET_S = (\d+)", _read(GATE_PY), re.M).group(1)
        rows = [r for r in _section(_read(TRD), "10. Performance").splitlines()
                if r.startswith("|") and re.search(r"(?i)\bgate\b", r.split("|")[1])]
        self.assertTrue(rows, "the TRD's performance table has no row for the gate")
        for row in rows:
            self.assertNotRegex(row, r"(?i)sub-second", "the TRD calls the gate sub-second")
        self.assertTrue(any(f"{budget} s" in r and "GATE_BUDGET_S" in r for r in rows),
                        f"the TRD's gate row does not state the {budget} s budget gate.py declares")
        perf = _section(_read(TSD), "Performance Testing")
        self.assertIn(f"{budget} s", perf, "the TSD's performance NFR does not state the budget")
        self.assertIn("GATE_BUDGET_S", perf, "the TSD's budget has no source")
        for s in _sentences(perf):
            self.assertFalse(re.search(r"(?i)\bgate\b", s) and re.search(r"(?i)sub-second", s), s)
        nfr = [r for r in _read(TSD).splitlines() if r.startswith("| **Performance**") and "read path" in r]
        self.assertEqual(len(nfr), 1, "the TSD's performance NFR row was not found")
        gate_cell = nfr[0].split("|")[2]
        self.assertIn(f"{budget} s", gate_cell, "the TSD's performance NFR row does not state the budget")
        self.assertIn("GATE_BUDGET_S", gate_cell, "the TSD's performance NFR row gives the budget no source")
        self.assertNotRegex(gate_cell, r"(?i)sub-second", "the TSD's performance NFR row calls the gate sub-second")

if __name__ == "__main__":
    unittest.main()
