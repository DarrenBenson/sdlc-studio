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
    text = "\n".join(_read(p) for p in READERS)
    keys = set(re.findall(r"git config(?:\s+--[\w-]+)*\s+(sdlc\.[A-Za-z]+)", text))
    return keys | set(re.findall(r"\b(SDLC_GATE_[A-Z_]+)\b", text))


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
        with SDLC_GATE_LOCAL=1; an unreachable host said to fall back to running the gate here."""
        stage = [b for b in _blocks(_section(_read(TSD), "Pipeline Stages")) if ".githooks/pre-push" in b]
        self.assertTrue(stage, "no TSD pipeline stage names .githooks/pre-push")
        push = stage[0]
        sentences = re.split(r"(?<=[.;])\s+", push)
        self.assertTrue(any("sdlc.gateHost" in s and re.search(r"(?i)\bhost\b", s) and re.search(r"(?i)\bthere\b|on (?:that|the) host", s)
                            for s in sentences), "the push stage does not say the gate runs on a configured host")
        self.assertTrue(any(re.search(r"(?i)\bunset\b|\bno host\b|\bnone\b", s) and re.search(r"(?i)this machine|locally", s)
                            for s in sentences), "the push stage does not say where the gate runs with no host")
        self.assertTrue(any("SDLC_GATE_LOCAL=1" in s and re.search(r"(?i)this machine|locally", s) for s in sentences),
                        "the push stage does not say SDLC_GATE_LOCAL=1 runs the gate here")
        unreachable = [s for s in sentences if re.search(r"(?i)cannot be reached|unreachable|connection fails", s)]
        self.assertTrue(unreachable, "the push stage does not say what an unreachable host does")
        for s in unreachable:
            self.assertRegex(s, r"(?i)refus", f"an unreachable host is not said to refuse the push: {s}")
            self.assertRegex(s, r"(?i)rather than|not .*(?:here|locally|this machine)",
                             f"an unreachable host is not said to keep the gate off this machine: {s}")
        for doc in (TRD, TSD):
            for s in re.split(r"(?<=[.;])\s+", " ".join(_blocks(_read(doc)))):
                if re.search(r"(?i)cannot be reached|unreachable", s) and re.search(r"(?i)falls? back|runs? (?:the gate )?(?:locally|here)", s):
                    self.assertRegex(s, r"(?i)\bnot\b|rather than|never", f"{doc.name} says an unreachable host falls back: {s}")


if __name__ == "__main__":
    unittest.main()
