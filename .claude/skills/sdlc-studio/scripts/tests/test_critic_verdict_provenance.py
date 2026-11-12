"""US1014: a recorded verdict names the agent that was briefed and wrote it, read from the
harness transcript.

`critic.py record --from-verdict <path>`, for a file a brief issued, reads the session's own
transcripts (the main thread's and each subagent's) for the context briefed with the path and
the writes of it. The `Source` cell gains `session:<id> agent:<id>` when the briefed agent wrote
the bytes on disk; a later write by another context, or bytes no write of the briefed agent's
carried, still records and warns; a store that is not read, or transcripts holding no write,
record `provenance:unknown` and say why, never naming an agent.

Every case drives `critic.py` through its entry point in a throwaway project. The transcripts
are fixtures under a temporary folder named by `SDLC_STUDIO_TRANSCRIPTS`, shaped after Claude
Code 2.1.318's own records, so no case reads or writes a real harness store.
"""
# test-census-subject: .claude/skills/sdlc-studio/scripts/critic.py
from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gitutil  # noqa: E402
import loader  # noqa: E402

SCRIPTS = Path(__file__).resolve().parent.parent
CRITIC = SCRIPTS / "critic.py"
critic = loader.load_script("critic")

SESSION = "acd73b30-154a-4170-83eb-043073708d4b"


def _write(root: Path, rel: str, body: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def _project(root: Path, *units: str) -> None:
    _write(root, "src/widget.py", "def w():\n    return 1\n")
    _write(root, "sdlc-studio/personas/seats/qa.md", "<!-- role: qa -->\n# Sam - QA amigo\n\ncharter\n")
    for unit in units:
        _write(root, f"sdlc-studio/stories/{unit}-widget.md",
               f"# {unit}: widget\n\n> **Status:** Review\n> **Points:** 2\n> **Epic:** EP0001\n"
               "> **Affects:** src/widget.py\n\n## Acceptance Criteria\n\n### AC1: works\n"
               "- **Verify:** shell true\n")


def _env(transcripts: Path, home: Path, harness: str = "claude",
         session: str | None = SESSION) -> dict:
    """The environment of a record run: the harness named outright, the session id the harness
    gives its shells, and every store folder a temporary one."""
    env = gitutil.git_env(SDLC_STUDIO_HARNESS=harness, SDLC_STUDIO_TRANSCRIPTS=str(transcripts),
                          HOME=str(home), XDG_DATA_HOME=str(home / "share"),
                          CLAUDE_CONFIG_DIR=str(home / "claude"))
    env.pop("CLAUDE_CODE_SESSION_ID", None)
    if session:
        env["CLAUDE_CODE_SESSION_ID"] = session
    return env


def _critic(cwd: Path, *args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-B", str(CRITIC), *args], cwd=cwd,
                          capture_output=True, text=True, timeout=300,
                          env=env or gitutil.git_env(), check=False)


def _brief(cwd: Path, root: Path, unit: str) -> tuple[Path, str, list[str]]:
    """Brief the unit: the issued path, its BRIEF stem, and the footer's record argv."""
    r = _critic(cwd, "brief", "--unit", unit, "--seat", "qa", "--root", str(root))
    assert r.returncode == 0, r.stderr
    tail = r.stdout[r.stdout.rindex(critic._RETURN_CONTRACT):]
    path = next(Path(ln.strip()) for ln in tail.splitlines() if ln.strip().endswith(".txt"))
    m = re.search(r"record the verdict with:\s+critic\.py (record .*)$", r.stderr, re.M)
    assert m, r.stderr
    return path, path.stem, [a for a in shlex.split(m.group(1)) if a != "..."]


def _block(unit: str, stem: str, remark: str = "") -> str:
    return (f"UNIT: {unit}\nBRIEF: {stem}\n{remark}VERDICT: APPROVE\nISSUES: none\n"
            "BLOCKING: none\n")


class _Transcripts:
    """A session's transcripts in Claude Code's layout: `<session>.jsonl` for the main thread,
    `<session>/subagents/agent-<id>.jsonl` (with its `.meta.json`) for each subagent. Records
    are written compact, one per line, as the harness writes them."""

    def __init__(self, folder: Path, cwd: Path) -> None:
        self.folder, self.cwd, self.n = folder, str(cwd), 0
        self.files: dict[str | None, list[str]] = {None: []}

    def _rec(self, agent: str | None, kind: str, ts: str, message: dict) -> None:
        self.n += 1
        rec = {"parentUuid": None, "isSidechain": agent is not None, "type": kind,
               "message": message, "uuid": f"00000000-0000-4000-8000-{self.n:012d}",
               "timestamp": f"2026-11-12T10:{ts}.000Z", "userType": "external",
               "entrypoint": "cli", "cwd": self.cwd, "sessionId": SESSION,
               "version": "2.1.318", "gitBranch": "main"}
        if agent is not None:
            rec = {"agentId": agent, **rec}
        self.files.setdefault(agent, []).append(json.dumps(rec, separators=(",", ":")))

    def said(self, agent: str | None, ts: str, text: str) -> None:
        """A user record: a prompt, or a later message handed to the context."""
        self._rec(agent, "user", ts, {"role": "user", "content": text})

    def tool(self, agent: str | None, ts: str, name: str, **tool_input: str) -> None:
        """An assistant record carrying one tool_use."""
        self._rec(agent, "assistant", ts, {
            "model": "claude-opus-5-5", "id": f"msg_{self.n:024d}", "type": "message",
            "role": "assistant", "stop_reason": "tool_use",
            "content": [{"type": "tool_use", "id": f"toolu_{self.n:024d}", "name": name,
                         "input": tool_input, "caller": {"type": "direct"}}]})

    def flush(self) -> Path:
        """Write every file, the main thread's last and so newest, as a live session's is."""
        sub = self.folder / SESSION / "subagents"
        sub.mkdir(parents=True, exist_ok=True)
        for i, (agent, lines) in enumerate(sorted(
                ((a, ls) for a, ls in self.files.items() if a is not None))):
            f = sub / f"agent-{agent}.jsonl"
            f.write_text("\n".join(lines) + "\n", encoding="utf-8")
            (sub / f"agent-{agent}.meta.json").write_text(json.dumps(
                {"agentType": "general-purpose", "description": f"agent {agent}",
                 "toolUseId": f"toolu_{agent}"}), encoding="utf-8")
            os.utime(f, (1_800_000_000 + i, 1_800_000_000 + i))
        main = self.folder / f"{SESSION}.jsonl"
        main.write_text("\n".join(self.files[None]) + "\n", encoding="utf-8")
        os.utime(main, (1_900_000_000, 1_900_000_000))
        return self.folder


def _session(folder: Path, cwd: Path, path: Path, written: str, *, r1_writes: bool = True,
             main_rewrite: str | None = None) -> _Transcripts:
    """A session in which the main thread briefs, an author agent `b1` builds before the path
    exists, reviewer `r1` is handed the path and (when `r1_writes`) writes `written` to it with
    its Write tool, and agent `r2`, the newest subagent, only reads the file afterwards. The main
    thread, the newest transcript, carries the path throughout, rewrites the file when
    `main_rewrite` is given, and runs the record command last."""
    t = _Transcripts(folder, cwd)
    t.said(None, "00:00", "run the review")
    t.said("b1", "00:01", "Build the widget")
    t.tool("b1", "00:02", "Write", file_path=str(cwd / "src" / "widget.py"),
           content="def w():\n    return 1\n")
    t.tool(None, "00:03", "Bash", command="python3 critic.py brief --unit US0001 --seat qa")
    t.said(None, "00:04", f"[tool_result] write your verdict to:\n{path}")
    t.tool(None, "00:05", "Agent", description="review", prompt=f"Review it. Verdict file: {path}")
    t.said("r1", "00:06", f"Review it. Verdict file: {path}")
    t.tool("r1", "00:07", "Bash", command="git diff")
    if r1_writes:
        t.tool("r1", "00:08", "Write", file_path=str(path), content=written)
    t.said("r2", "00:09", f"Summarise the verdict in {path}")
    t.tool("r2", "00:10", "Bash", command=f"cat {path}")
    if main_rewrite is not None:
        t.tool(None, "00:11", "Write", file_path=str(path), content=main_rewrite)
    t.tool(None, "00:12", "Bash", command=f"python3 critic.py record --from-verdict {path}")
    return t


def _cell(data: bytes, path: Path, *later: str) -> str:
    return " ".join([f"sha256:{hashlib.sha256(data).hexdigest()[:16]}", path.name, *later])


def _show_line(cwd: Path, root: Path, unit: str) -> str:
    r = _critic(cwd, "show", "--root", str(root))
    assert r.returncode == 0, r.stderr
    lines = [ln for ln in r.stdout.splitlines() if unit in ln]
    assert len(lines) == 1, r.stdout
    return lines[0]


class VerdictProvenanceTests(unittest.TestCase):

    def _record(self, cwd: Path, root: Path, argv: list[str], env: dict
                ) -> subprocess.CompletedProcess:
        r = _critic(cwd, *argv, "--reviewer", "qa-seat", "--author", "builder",
                    "--root", str(root), env=env)
        self.assertEqual(0, r.returncode, r.stdout + r.stderr)
        self.assertRegex(r.stdout, r"^recorded US000\d APPROVE \[delivery\] round 1 -> ")
        return r

    def test_the_briefed_agent_that_wrote_the_file_is_named_on_the_row(self) -> None:
        """AC1. Mutants: the newest transcript (the main thread's) taken as the writer; the
        newest subagent carrying the path taken as the briefed one; the session id left off the
        cell; any Bash command naming the path counted as a write; `show` giving an agent row no
        writer label."""
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            root, cwd, home = base / "proj", base / "elsewhere", base / "home"
            for p in (root, cwd, home):
                p.mkdir()
            _project(root, "US0001")
            path, stem, argv = _brief(cwd, root, "US0001")
            written = _block("US0001", stem, "The widget holds.\n")
            path.write_text(written, encoding="utf-8")
            folder = _session(base / "transcripts", root, path, written).flush()
            rec = self._record(cwd, root, argv, _env(folder, home))
            self.assertNotIn("WARNING", rec.stderr)
            want = _cell(written.encode(), path, f"session:{SESSION}", "agent:r1")
            self.assertEqual(want, critic.read_verdicts(root)[-1]["source"])
            self.assertIn("written by agent r1", rec.stdout)
            line = _show_line(cwd, root, "US0001")
            self.assertIn("(written by agent r1)", line)
            self.assertIn(f"verdicts/US0001/{path.name}", line)
            rows = json.loads(_critic(cwd, "show", "--format", "json", "--root",
                                      str(root)).stdout)
            self.assertIn("written by agent r1", rows[-1]["provenance"])

    def test_a_file_rewritten_by_another_context_warns(self) -> None:
        """AC2. Mutants: the briefed agent's write matched on the path alone, so the main
        thread's later rewrite is attributed to the reviewer; the bytes on disk never set against
        the content the reviewer's write carried; the warning dropped from `record`'s output."""
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            root, cwd, home = base / "proj", base / "elsewhere", base / "home"
            for p in (root, cwd, home):
                p.mkdir()
            _project(root, "US0001", "US0002")

            # the main thread writes the file after the reviewer did
            path, stem, argv = _brief(cwd, root, "US0001")
            reviewer = _block("US0001", stem, "The widget holds.\n")
            rewritten = _block("US0001", stem, "Edited by the orchestrator.\n")
            path.write_text(rewritten, encoding="utf-8")
            folder = _session(base / "t1", root, path, reviewer,
                              main_rewrite=rewritten).flush()
            rec = self._record(cwd, root, argv, _env(folder, home))
            self.assertRegex(rec.stderr, r"WARNING: .*agent r1.*the main thread")
            want = _cell(rewritten.encode(), path, f"session:{SESSION}", "agent:r1",
                         "last-writer:main")
            self.assertEqual(want, critic.read_verdicts(root)[-1]["source"])
            line = _show_line(cwd, root, "US0001")
            self.assertIn("last written by the main thread", line)
            self.assertNotIn("(written by agent r1)", line)

            # the bytes differ from the reviewer's write and no transcript holds a later one
            path2, stem2, argv2 = _brief(cwd, root, "US0002")
            reviewer2 = _block("US0002", stem2, "The widget holds.\n")
            on_disk = _block("US0002", stem2, "Changed with no tool any transcript holds.\n")
            path2.write_text(on_disk, encoding="utf-8")
            folder2 = _session(base / "t2", root, path2, reviewer2).flush()
            rec2 = self._record(cwd, root, argv2, _env(folder2, home))
            self.assertRegex(rec2.stderr, r"WARNING: .*bytes differ.*agent r1")
            self.assertIn("no transcript of session", rec2.stderr)
            want2 = _cell(on_disk.encode(), path2, f"session:{SESSION}", "agent:r1",
                          "last-writer:unknown")
            self.assertEqual(want2, critic.read_verdicts(root)[-1]["source"])
            self.assertNotIn("(written by agent r1)", _show_line(cwd, root, "US0002"))

    def test_an_unread_store_records_unknown_provenance(self) -> None:
        """AC3. Mutants: the Claude transcripts read whatever harness is named; a fall back to
        the main-thread transcript, or to the newest subagent's, when no write is found; an
        unknown row still carrying an `agent:` token; the reason left unsaid."""
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            root, cwd, home = base / "proj", base / "elsewhere", base / "home"
            for p in (root, cwd, home):
                p.mkdir()
            _project(root, "US0001", "US0002", "US0003")

            # a harness whose store is not read, beside Claude transcripts naming r1 the writer
            path, stem, argv = _brief(cwd, root, "US0001")
            written = _block("US0001", stem)
            path.write_text(written, encoding="utf-8")
            folder = _session(base / "t1", root, path, written).flush()
            rec = self._record(cwd, root, argv, _env(folder, home, harness="cursor"))
            cell = critic.read_verdicts(root)[-1]["source"]
            self.assertEqual(_cell(written.encode(), path, "provenance:unknown"), cell)
            self.assertRegex(rec.stdout, r"provenance is unknown: .*cursor")
            self.assertIn("(provenance unknown)", _show_line(cwd, root, "US0001"))

            # Claude transcripts in which the briefed agent and the newest subagent only read it
            path2, stem2, argv2 = _brief(cwd, root, "US0002")
            written2 = _block("US0002", stem2)
            path2.write_text(written2, encoding="utf-8")
            folder2 = _session(base / "t2", root, path2, written2, r1_writes=False).flush()
            rec2 = self._record(cwd, root, argv2, _env(folder2, home))
            cell2 = critic.read_verdicts(root)[-1]["source"]
            self.assertEqual(_cell(written2.encode(), path2, f"session:{SESSION}",
                                   "provenance:unknown"), cell2)
            self.assertNotIn("agent:", cell2)
            self.assertRegex(rec2.stdout, r"provenance is unknown: .*no write of")
            line2 = _show_line(cwd, root, "US0002")
            self.assertIn("(provenance unknown)", line2)
            self.assertNotIn("written by", line2)

            # Claude named, but no session id to find the session's transcripts by
            path3, stem3, argv3 = _brief(cwd, root, "US0003")
            written3 = _block("US0003", stem3)
            path3.write_text(written3, encoding="utf-8")
            folder3 = _session(base / "t3", root, path3, written3).flush()
            rec3 = self._record(cwd, root, argv3, _env(folder3, home, session=None))
            self.assertEqual(_cell(written3.encode(), path3, "provenance:unknown"),
                             critic.read_verdicts(root)[-1]["source"])
            self.assertRegex(rec3.stdout, r"provenance is unknown: .*CLAUDE_CODE_SESSION_ID")

    def test_a_heredoc_write_names_its_agent_and_a_default_choice_reads_nothing(self) -> None:
        """Mutants: a Bash heredoc that holds the path and the file's text not counted as a
        write; Claude Code chosen only as the default, with no store present, still read, so a
        row recorded outside any harness reads `provenance:unknown` rather than unread."""
        from lib import verdict_provenance as provenance  # noqa: PLC0415
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            home = {"HOME": str(base / "home"), "XDG_DATA_HOME": str(base / "home" / "share"),
                    "XDG_CONFIG_HOME": str(base / "home" / "config")}
            root = base / "proj"
            path = root / "sdlc-studio" / "reviews" / "verdicts" / "US0001" / "a-b.txt"
            path.parent.mkdir(parents=True)
            text = _block("US0001", "a-b")
            path.write_text(text, encoding="utf-8")
            t = _Transcripts(base / "t", root)
            t.tool(None, "00:01", "Agent", prompt=f"Review it. Verdict file: {path}")
            t.said("r1", "00:02", f"Review it. Verdict file: {path}")
            t.tool("r1", "00:03", "Bash", command=f"cat > {path} <<'EOF'\n{text}EOF")
            t.tool(None, "00:04", "Bash", command=f"critic.py record --from-verdict {path}")
            env = {"SDLC_STUDIO_HARNESS": "claude", "SDLC_STUDIO_TRANSCRIPTS": str(t.flush()),
                   "CLAUDE_CODE_SESSION_ID": SESSION, **home}
            with mock.patch.dict(os.environ, home):
                got = provenance.read(root, path, text.encode(), env)
            self.assertEqual([f"session:{SESSION}", "agent:r1"], got["tokens"])
            self.assertIsNone(got["warning"])
            # nothing named or signalled, and the session's home holds no harness store
            with mock.patch.dict(os.environ, home):
                got = provenance.read(root, path, text.encode(),
                                      {"CLAUDE_CODE_SESSION_ID": SESSION, **home})
            self.assertEqual([], got["tokens"])
            self.assertIn("writer was not read", got["note"])
            self.assertIsNone(provenance.label([]))


if __name__ == "__main__":
    unittest.main()
