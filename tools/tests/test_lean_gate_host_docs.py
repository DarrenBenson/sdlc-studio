"""US1086 and BG1095: the TRD and the TSD describe the gate host a clone can configure, the
fallback and the local override.

The settings are read from the four scripts that choose or report where the gate runs (the
pre-push hook, tools/remote-gate.sh, tools/run-suite.sh and tools/enable-hooks.sh), never typed
here (LL0043): every `git config` key in the `sdlc.` namespace they read, and every
`SDLC_GATE_*` variable. Each derived set first asserts a member known to be in it.

Where the gate runs is a table in each document's push-gate section, compared cell for cell with
TABLE below. TABLE is pinned to the hook by running the hook's own code under each row's cases.
"""
# test-census-subject: sdlc-studio/tsd.md
from __future__ import annotations

import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TRD = REPO / "sdlc-studio" / "trd.md"
TSD = REPO / "sdlc-studio" / "tsd.md"
HOOK = REPO / ".githooks" / "pre-push"
REMOTE_GATE = REPO / "tools" / "remote-gate.sh"
READERS = (HOOK, REMOTE_GATE, REPO / "tools" / "run-suite.sh", REPO / "tools" / "enable-hooks.sh")

HERE = "runs on this machine"
THERE = "runs on that host, through `tools/remote-gate.sh`"
REFUSED = "does not run on this machine in its place: the push is refused"
HEADER = ("`sdlc.gateHost`", "`SDLC_GATE_LOCAL` in the push's environment", "The push gate")
#: The rows both documents' tables hold, each with the cases the hook's code is run under to pin
#: it: (sdlc.gateHost, SDLC_GATE_LOCAL, whether the connection fails), None being unset.
TABLE = (
    (("unset or empty", "any value", HERE),
     ((None, None, False), ("", None, False), (None, "1", False), ("", "0", False))),
    (("set", "`1`", HERE),
     (("gatebox", "1", False),)),
    (("set", "unset, or any value but `1`", THERE),
     (("gatebox", None, False), ("gatebox", "", False), ("gatebox", "yes", False))),
    (("set, and the connection to it fails", "unset, or any value but `1`", REFUSED),
     (("gatebox", None, True), ("gatebox", "0", True))),
)


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


def _push_gate(doc: Path) -> str:
    """A document's push-gate section: the TRD's `The gate host`, and the TSD's pipeline stage
    that names `.githooks/pre-push`, with every line indented under it."""
    if doc == TRD:
        return _section(_read(TRD), "The gate host")
    items: list[list[str]] = []
    for line in _section(_read(TSD), "Pipeline Stages").splitlines():
        if re.match(r"^\d+\.\s", line):
            items.append([line])
        elif items and (not line.strip() or line.startswith(" ")):
            items[-1].append(line)
    stage = [s for s in ("\n".join(i) for i in items) if ".githooks/pre-push" in s]
    if len(stage) != 1:
        raise AssertionError(f"{len(stage)} TSD pipeline stages name .githooks/pre-push, not one")
    return stage[0]


def _tables(text: str) -> list[list[tuple[str, ...]]]:
    """Each table in the text as its rows of stripped cells, the delimiter row dropped."""
    tables, rows = [], []
    for line in [*text.splitlines(), ""]:
        s = line.strip()
        if s.startswith("|"):
            cells = tuple(c.strip() for c in s.strip("|").split("|"))
            if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                rows.append(cells)
        elif rows:
            tables.append(rows)
            rows = []
    return tables


def _settings() -> set[str]:
    """Every `sdlc.` key on a line that runs `git config`, however it is spelt (quoted, after any
    flags, or git's `git config get` form), and every SDLC_GATE_ variable."""
    text = "\n".join(_read(p) for p in READERS)
    keys = {k for line in text.splitlines() if re.search(r"\bgit\s+config\b", line)
            for k in re.findall(r"(?<![\w.])(sdlc\.[A-Za-z]+)", line)}
    return keys | set(re.findall(r"\b(SDLC_GATE_[A-Z_]+)\b", text))


def _hook_code() -> str:
    """The hook's own shell options, its host decision (the `gate_host=` line through the line
    that sets `on_host=1`) and its host branch (the `if [ -n "$on_host" ]; then` block, to its
    closing `fi`, that runs `tools/remote-gate.sh push`), cut from .githooks/pre-push, with the
    pushed commits the branch loops over."""
    lines = _read(HOOK).splitlines()
    opts = [ln for ln in lines if re.match(r"^set -\w", ln)]
    first = [i for i, ln in enumerate(lines) if ln.startswith('gate_host="$(git config --get sdlc.gateHost')]
    last = [i for i, ln in enumerate(lines) if first and i >= first[0] and "on_host=1" in ln]
    blocks = [(i, lines.index("fi", i)) for i, ln in enumerate(lines)
              if ln == 'if [ -n "$on_host" ]; then' and "fi" in lines[i:]]
    branch = [(i, end) for i, end in blocks
              if any("tools/remote-gate.sh push" in ln for ln in lines[i:end])]
    if not (opts and first and last and len(branch) == 1):
        raise AssertionError("the pre-push hook's host decision or its one host branch was not found")
    return "\n".join([opts[0], *lines[first[0]:last[0] + 1], 'commits="0123abcd"; release_commits=""',
                      *lines[branch[0][0]:branch[0][1] + 1]])


def _where(code: str, host: str | None, local: str | None, rc: int) -> str:
    """Which of the table's cells the hook's code gives: run in a scratch repository whose git config
    holds `host`, with `local` as SDLC_GATE_LOCAL and tools/remote-gate.sh a stub that records its
    call and exits `rc`. A line after the host branch stands for the hook's local gate."""
    env = {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "SDLC_GATE_"))}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        subprocess.run(["git", "init", "-q"], cwd=root, env=env, check=True)
        if host is not None:
            subprocess.run(["git", "config", "sdlc.gateHost", host], cwd=root, env=env, check=True)
        if local is not None:
            env["SDLC_GATE_LOCAL"] = local
        (root / "tools").mkdir()
        (root / "tools" / "remote-gate.sh").write_text(f"touch sent\nexit {rc}\n", encoding="utf-8")
        r = subprocess.run(["bash", "-c", f"{code}\necho LOCAL-GATE"], cwd=root, env=env,
                           capture_output=True, text=True, timeout=60)
        sent, ran_here = (root / "sent").exists(), "LOCAL-GATE" in r.stdout
    if ran_here and not sent:
        return HERE
    if sent and not ran_here:
        return THERE if r.returncode == 0 else REFUSED
    return f"no cell: exit {r.returncode}, sent {sent}, ran here {ran_here}: {r.stderr[-400:]}"


class GateHostDocsTests(unittest.TestCase):

    def test_every_gate_host_setting_is_named(self) -> None:
        """US1086 AC1, kept by BG1095 AC2. Mutant: a setting a script reads to choose or report
        where the gate runs left unnamed in either document's push-gate section. A mention
        elsewhere in the document, such as its revision history, does not count."""
        settings = _settings()
        self.assertTrue({"sdlc.gateHost", "SDLC_GATE_LOCAL"} <= settings, settings)
        for doc in (TRD, TSD):
            section = _push_gate(doc)
            for name in sorted(settings):
                with self.subTest(doc=doc.name, setting=name):
                    self.assertIn(name, section)

    def test_the_push_stage_tables_each_gate_location(self) -> None:
        """BG1095 AC1, and US1086 AC2. Each document's push-gate section holds one table, and its
        cells equal TABLE's exactly. Mutants: a row missing, added or reordered; a row naming the
        wrong location, or two rows' locations swapped; a document stating where the gate runs in
        prose with no table, or its table outside the push-gate section.

        TABLE is pinned to the hook: each row's cases run the hook's own host decision and host
        branch, with tools/remote-gate.sh a stub exiting 0, or exiting remote-gate.sh's
        TRANSPORT_FAILED code for a failed connection. So the hook ignoring SDLC_GATE_LOCAL=1,
        honouring a value other than 1, taking the host path with no host or an empty one,
        reading a failed connection as a pass, or running the gate here after one, fails this
        test until TABLE and both tables say so. A real failed connection, before and during the
        run, is test_remote_gate_push.py's AC4, end to end. Prose beside a table is not judged."""
        transport = re.search(r"^TRANSPORT_FAILED=(\d+)$", _read(REMOTE_GATE), re.M)
        self.assertIsNotNone(transport, "tools/remote-gate.sh's TRANSPORT_FAILED code was not read")
        code = _hook_code()
        for row, cases in TABLE:
            for host, local, fails in cases:
                with self.subTest(row=row[:2], host=host, local=local):
                    rc = int(transport.group(1)) if fails else 0
                    self.assertEqual(_where(code, host, local, rc), row[2])
        expected = [HEADER, *(row for row, _ in TABLE)]
        for doc in (TRD, TSD):
            with self.subTest(doc=doc.name):
                tables = _tables(_push_gate(doc))
                self.assertEqual(len(tables), 1, f"{doc.name}'s push-gate section holds {len(tables)} tables, not one")
                self.assertEqual(tables[0], expected, f"{doc.name}'s gate-location table")


if __name__ == "__main__":
    unittest.main()
