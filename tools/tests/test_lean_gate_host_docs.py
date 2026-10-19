"""US1086: the TRD and the TSD describe the gate host a clone can configure, the fallback and the
local override.

The settings are read from the four scripts that choose or report where the gate runs (the
pre-push hook, tools/remote-gate.sh, tools/run-suite.sh and tools/enable-hooks.sh), never typed
here (LL0043): every `git config` key in the `sdlc.` namespace they read, and every
`SDLC_GATE_*` variable. Each derived set first asserts a member known to be in it.
"""
# test-census-subject: sdlc-studio/tsd.md
from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TRD = REPO / "sdlc-studio" / "trd.md"
TSD = REPO / "sdlc-studio" / "tsd.md"
READERS = (REPO / ".githooks" / "pre-push", REPO / "tools" / "remote-gate.sh",
           REPO / "tools" / "run-suite.sh", REPO / "tools" / "enable-hooks.sh")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str:
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


def _settings() -> set[str]:
    """Every `sdlc.` key on a line that runs `git config`, however it is spelt (quoted, after any
    flags, or git's `git config get` form), and every SDLC_GATE_ variable."""
    text = "\n".join(_read(p) for p in READERS)
    keys = {k for line in text.splitlines() if re.search(r"\bgit\s+config\b", line)
            for k in re.findall(r"(?<![\w.])(sdlc\.[A-Za-z]+)", line)}
    return keys | set(re.findall(r"\b(SDLC_GATE_[A-Z_]+)\b", text))


#: A transport failure, however a sentence words it, and a claim that the gate then runs here.
TRANSPORT = r"(?i)cannot be reached|unreachable|transport fail|connection (?:fails|failed|drops|is dropped)|drops mid-run|ssh fails"
FALLS_BACK = r"(?i)\bfall(?:s|ing)? back\b|\bruns? (?:the gate |it )?(?:locally|here|on this machine)\b|\blocal gate\b"
NEGATES = r"(?i)\b(?:never|not|no|without|rather than)\s+(?:\w+\s+){0,2}(?:fall(?:s|ing)? back|run(?:s|ning)?\b)"


class GateHostDocsTests(unittest.TestCase):

    def test_every_gate_host_setting_is_named(self) -> None:
        """AC1. Mutant: a setting a script reads to choose or report where the gate runs left
        unnamed in either document."""
        settings = _settings()
        self.assertTrue({"sdlc.gateHost", "SDLC_GATE_LOCAL"} <= settings, settings)
        for doc in (TRD, TSD):
            for name in sorted(settings):
                with self.subTest(doc=doc.name, setting=name):
                    self.assertIn(name, _read(doc))

    def test_the_push_stage_names_each_gate_location(self) -> None:
        """AC2. Mutants: the push stage silent on where the gate runs with a host, with none, or
        with SDLC_GATE_LOCAL=1, or saying any of the three the wrong way round; an unreachable
        host said to run the gate here, or its refusal and fall-back swapped; a transport failure,
        in any wording and in either document, said to fall back to the local gate."""
        stage = [b for b in _blocks(_section(_read(TSD), "Pipeline Stages")) if ".githooks/pre-push" in b]
        self.assertTrue(stage, "no TSD pipeline stage names .githooks/pre-push")
        sentences = re.split(r"(?<=[.;])\s+", stage[0])
        here = r"(?i)this machine|locally"
        host = [s for s in sentences if re.search(r"sdlc\.gateHost`? set\b", s)]
        self.assertTrue(any(re.search(r"(?i)\bthere\b|on (?:that|the) host", s) for s in host),
                        "the push stage does not say the gate runs on a configured host")
        unset = [s for s in sentences if re.search(r"(?i)\bunset\b|\bno host\b", s)]
        self.assertTrue(unset, "the push stage does not say where the gate runs with no host")
        for s in unset:
            self.assertRegex(s, rf"(?i)gate runs (?:on this machine|locally)", f"no host is not said to run the gate here: {s}")
            self.assertNotRegex(s, r"(?i)refus|\bnever\b|\bnot\b|\bthere\b", f"no host is said the wrong way round: {s}")
        local = [s for s in sentences if "SDLC_GATE_LOCAL=1" in s]
        self.assertTrue(local, "the push stage does not name SDLC_GATE_LOCAL=1")
        for s in local:
            self.assertRegex(s, r"(?i)runs (?:it|the gate) on this machine", f"SDLC_GATE_LOCAL=1 is not said to run the gate here: {s}")
            self.assertNotRegex(s, r"(?i)ignored|still runs there|not on this machine", f"SDLC_GATE_LOCAL=1 is said the wrong way round: {s}")
        unreachable = [s for s in sentences if re.search(TRANSPORT, s)]
        self.assertTrue(unreachable, "the push stage does not say what an unreachable host does")
        self.assertTrue(any(re.search(r"(?i)refus\w*[^.]*\brather than\b[^.]*\brun\w*", s) for s in unreachable),
                        "an unreachable host is not said to refuse the push rather than run the gate here")
        for doc in (TRD, TSD):
            for s in re.split(r"(?<=[.;])\s+", " ".join(_blocks(_read(doc)))):
                if not re.search(TRANSPORT, s):
                    continue
                for clause in re.split(r"(?i),\s*(?:but|and|while|whereas)\s+|\s+but\s+", s):
                    if re.search(FALLS_BACK, clause) and not re.search(NEGATES, clause):
                        self.fail(f"{doc.name} says a transport failure runs the gate here: {s}")

if __name__ == "__main__":
    unittest.main()
