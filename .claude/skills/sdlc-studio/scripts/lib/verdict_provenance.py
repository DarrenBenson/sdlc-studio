"""Who wrote a verdict file a brief issued, read from the harness's own session store.

A brief issues a verdict path, a reviewer agent writes the file, and the orchestrator records
it. Nothing in the file says which context wrote it, and the environment cannot say either: a
subagent's shell carries its parent's session id and no agent id of its own, so an author agent
and a reviewer agent look the same there. The session's transcripts are the only witness.

There is one reader per harness. Claude Code's comes first; every other harness answers
`unknown`, and says so. The harness is the one `token_meters.select` chooses, so
`SDLC_STUDIO_HARNESS` wins outright. Claude Code keeps a session's main thread at
`<transcripts>/<session>.jsonl` and each subagent's at
`<transcripts>/<session>/subagents/agent-<id>.jsonl`; the session is the one
`CLAUDE_CODE_SESSION_ID` names, and the folder is the meter's (`SDLC_STUDIO_TRANSCRIPTS`, else
the harness's project folder for this repo). No transcript is taken as the writer for being
the newest (the newest is the main thread's, running the record); a context is named only for
a write its transcript holds.

Each transcript line is tested for the path before any JSON is parsed, which bounds the scan.
The briefed agent is the subagent whose earliest record carrying the path comes first: the
prompt with the brief pasted in, or a later message handing it over. A write of the path is a
Write tool_use naming it (with the content it carried), an Edit naming it (whose result is not
compared), or a Bash tool_use whose command holds the path and the file's text, as a heredoc
does. A Bash command naming the path without its text, the record command among them, is not a
write.

`read` returns the tokens the row's `Source` cell carries after the hash and basename:

- `session:<id> agent:<id>` when the briefed agent's write is the last one and carried the
  bytes on disk;
- `session:<id> agent:<id> last-writer:<context>` when another context wrote the file after
  it (`main` for the main thread, `agent-<id>` for another subagent), or `last-writer:unknown`
  when the bytes on disk are no write's any transcript of the session holds; a warning names
  both;
- `provenance:unknown` (after `session:<id>` when one was read) when the store is not read or
  holds no write of the path by an agent briefed with it; the row then names no agent;
- nothing when no harness can be chosen, or Claude Code is chosen only as the default with no
  store present, so the row reads as one whose writer was never read.

`self_review` asks a second question of the same transcripts: did the context that wrote the
verdict edit the unit's files before it was briefed? The judged context is the issued file's
writer (the context whose write carried the bytes on disk), or, for a verdict given on the
command line, the context whose transcript holds the running command. Its authoring evidence is
a Write, Edit, MultiEdit or NotebookEdit call naming an Affects path, matched
repository-relative through the subagent's `worktreePath`, made before its first record
carrying a verdict path a brief issued for the unit, and no earlier than `since`, the start of
the unit's delivery. An edit made through Bash is not counted. The writer appends the answer to
the row's `Source` cell as `self-review:<path>`, which `self_reviewed` reads back.
"""
from __future__ import annotations

import json
import os
import re
import shlex
from collections.abc import Mapping
from pathlib import Path

from lib import run_state, sdlc_md

#: The variable Claude Code sets in its shells, a subagent's included, to the session's id.
SESSION_ENV = "CLAUDE_CODE_SESSION_ID"
#: The context name the main thread's writes carry in a `last-writer:` token.
MAIN = "main"
UNKNOWN = "unknown"
SESSION, AGENT, LAST_WRITER, PROVENANCE = "session", "agent", "last-writer", "provenance"
#: The `Source` token naming the Affects file the verdict's own context edited before its brief.
SELF_REVIEW = "self-review"
#: The key of a subagent's `.meta.json` naming the worktree it ran in.
WORKTREE_KEY = "worktreePath"
#: The tool_use names whose input names a file they rewrite in place; their result is unread.
EDIT_TOOLS = ("Edit", "MultiEdit", "NotebookEdit")
_PLAIN = re.compile(r"[A-Za-z0-9_-]+")
_AGENT_PREFIX = "agent-"


def read(repo_root: Path | str, path: Path | str, data: bytes,
         env: Mapping | None = None) -> dict:
    """Who wrote the verdict file at `path`, whose bytes are `data`: {"tokens", "note",
    "warning"}. `tokens` go on the row after the hash; `note` ends the sentence `record` prints
    after "<unit>'s verdict file", naming the writer or saying why none is named; `warning` is
    None or the line naming the briefed agent and the context that last wrote the file."""
    from lib import token_meters  # noqa: PLC0415 - only a bound record chooses a harness
    env = os.environ if env is None else env
    claude = _ClaudeStore()
    chosen = token_meters.select(repo_root, claude, env)
    harness = chosen.get(token_meters.HARNESS)
    if harness == token_meters.CLAUDE and _by_default(repo_root, env, claude):
        chosen = {"reason": "no harness is named or signalled and no harness store is present"}
        harness = None
    if harness is None:
        return {"tokens": [], "warning": None,
                "note": f"writer was not read: {chosen.get('reason') or 'no harness chosen'}"}
    if harness != token_meters.CLAUDE:
        return _unknown([], f"{harness} is the harness ({chosen.get('selected_by')}), and its "
                            f"session store is not read for verdict provenance; only Claude "
                            f"Code's transcripts are")
    return _claude(Path(repo_root), Path(path), data, env)


def _by_default(repo_root, env: Mapping, claude) -> bool:
    """True when Claude Code was chosen only as the default: not named, not signalled, and with
    no store of its own here, so there is nothing to read and the writer reads as unread."""
    from lib import token_meters  # noqa: PLC0415 - as `read`
    named = str(env.get(token_meters.HARNESS_ENV) or "").strip()
    signalled = any(env.get(v) for v in token_meters.SIGNALS[token_meters.CLAUDE])
    return not named and not signalled and not claude.store(repo_root, env)


class _ClaudeStore:
    """Claude Code's store as `token_meters.select` probes it, the meter's own finder."""

    @staticmethod
    def store(root, env):
        return run_state._claude_store(root, None, env)


def _unknown(tokens: list[str], why: str, warning: str | None = None) -> dict:
    return {"tokens": [*tokens, f"{PROVENANCE}:{UNKNOWN}"], "warning": warning,
            "note": f"provenance is unknown: {why}"}


def _claude(repo_root: Path, path: Path, data: bytes, env: Mapping) -> dict:
    session = str(env.get(SESSION_ENV) or "").strip()
    if not _PLAIN.fullmatch(session):
        said = "is not set" if not session else f"is {session!r}, not a plain session id"
        return _unknown([], f"{SESSION_ENV} {said}, so no session's transcripts are read")
    folder, contexts = _contexts(repo_root, session, env)
    tokens = [f"{SESSION}:{session}"]
    if not contexts[0][1].is_file() and len(contexts) == 1:
        return _unknown(tokens, f"session {session} has no transcript in {folder}")
    target = path.resolve()
    needles = {json.dumps(str(p), ensure_ascii=False)[1:-1].encode("utf-8")
               for p in (path.absolute(), target)}
    text = data.decode("utf-8", "replace")
    carries, writes = [], []
    for order, (ctx, f) in enumerate(contexts):
        _scan(f, ctx, order, needles, target, text, carries, writes)
    if not writes:
        return _unknown(tokens, f"the transcripts of session {session} hold no write of {path}")
    writes.sort(key=lambda w: w[0])
    agents = [c for c in carries if c[1] != MAIN]
    briefed = min(agents, key=lambda c: c[0])[1] if agents else None
    own = [w for w in writes if w[1] == briefed]
    last = writes[-1]
    if not own:
        handed = (f"no agent of session {session} was handed the path" if briefed is None
                  else f"{_words(briefed)}, briefed with it, never wrote it")
        why = f"{handed}, and {_words(_last_writer(last, data))} last wrote it"
        return _unknown(tokens, why, f"{path} carries no write by an agent briefed with it: {why}")
    agent = briefed[len(_AGENT_PREFIX):]
    tokens.append(f"{AGENT}:{agent}")
    if last[1] == briefed and _carried(last, data):
        return {"tokens": tokens, "warning": None,
                "note": f"was written by agent {agent} (session {session})"}
    lw = _last_writer(last, data)
    tokens.append(f"{LAST_WRITER}:{lw}")
    if lw == UNKNOWN:
        warning = (f"{path}'s bytes differ from the content agent {agent}'s write carried, and "
                   f"no transcript of session {session} holds the write that made them; the "
                   f"row names agent {agent}, the briefed writer, and an unknown last writer")
    else:
        warning = (f"{path} was briefed to agent {agent}, which wrote it, but {_words(lw)} "
                   f"last wrote it; the row names both")
    return {"tokens": tokens, "warning": warning,
            "note": f"was briefed to agent {agent} (session {session}) and last written by "
                    f"{_words(lw)}"}


def _contexts(repo_root: Path, session: str, env: Mapping) -> tuple[Path, list]:
    """The transcripts folder and the session's contexts in it, as (name, transcript) pairs:
    the main thread's first, then each subagent's, by name."""
    folder = Path(env.get(run_state.TRANSCRIPTS_ENV)
                  or run_state._harness_transcript_dir(repo_root))
    sub = folder / session / run_state.SUBAGENTS_DIR
    return folder, [(MAIN, folder / f"{session}.jsonl")] + [
        (_AGENT_PREFIX + f.stem[len(_AGENT_PREFIX):], f)
        for f in (sorted(sub.glob(run_state.SUBAGENT_GLOB)) if sub.is_dir() else [])
        if _PLAIN.fullmatch(f.stem[len(_AGENT_PREFIX):])]


def _records(f: Path, keep):
    """Each record of transcript `f` whose raw line `keep` accepts, as (line, raw, record). A
    line `keep` refuses is never parsed; one that does not parse costs only itself."""
    try:
        fh = f.open("rb")
    except OSError:
        return
    with fh:
        for n, raw in enumerate(fh):
            if not keep(raw):
                continue
            try:
                rec = json.loads(raw)
            except ValueError:
                continue
            if isinstance(rec, dict):
                yield n, raw, rec


def _tool_uses(rec: dict) -> list[dict]:
    """The tool_use blocks an assistant record carries; [] for any other record."""
    content = (rec.get("message") or {}).get("content") if rec.get("type") == "assistant" else None
    return [u for u in content if isinstance(u, dict) and u.get("type") == "tool_use"
            ] if isinstance(content, list) else []


def _scan(f: Path, ctx: str, order: int, needles: set[bytes], target: Path, text: str,
          carries: list, writes: list) -> None:
    """Append to `carries` each record of `f` that holds the path, and to `writes` each write
    of it, as ((timestamp, order, line), context, content); content is None for an edit. A line
    without the path is never parsed; one that does not parse costs only itself."""
    for n, _raw, rec in _records(f, lambda raw: any(nd in raw for nd in needles)):
        key = (str(rec.get("timestamp") or ""), order, n)
        carries.append((key, ctx))
        for use in _tool_uses(rec):
            wrote = _write_of(use, target, text)
            if wrote is not False:
                writes.append((key, ctx, wrote))


def _write_of(use: dict, target: Path, text: str):
    """The content a tool_use wrote to `target`, None for an edit of it, False for no write."""
    name, given = use.get("name"), use.get("input")
    given = given if isinstance(given, dict) else {}
    if name == "Write" and _names(given.get("file_path"), target):
        content = given.get("content")
        return content if isinstance(content, str) else None
    if name in EDIT_TOOLS and _names(given.get("file_path") or given.get("notebook_path"),
                                     target):
        return None
    command, body = given.get("command"), text.rstrip("\n")
    if name == "Bash" and isinstance(command, str) and body and body in command:
        return text
    return False


def _names(value, target: Path) -> bool:
    return isinstance(value, str) and bool(value) and Path(value).resolve() == target


def _carried(write: tuple, data: bytes) -> bool:
    """True when `write` carried `data`, or was an edit, whose result is not compared."""
    return write[2] is None or write[2].encode("utf-8") == data


def _last_writer(last: tuple, data: bytes) -> str:
    """The context that wrote the bytes on disk: the newest write's, when it carried them (or
    was an edit); `unknown` when the newest write carried other bytes."""
    return last[1] if _carried(last, data) else UNKNOWN


def _words(context: str) -> str:
    if context == MAIN:
        return "the main thread"
    if context.startswith(_AGENT_PREFIX):
        return f"agent {context[len(_AGENT_PREFIX):]}"
    return "a writer no transcript of the session holds"


def label(tokens: list[str]) -> str | None:
    """What `show` says, in brackets, of a bound row's tokens after its hash and basename: the
    agent that wrote it, the briefed agent and the last writer, or `provenance unknown`; None
    for a row carrying none, recorded before the writer was read or where no harness was
    chosen."""
    fields = dict(t.split(":", 1) for t in tokens if ":" in t)
    if fields.get(PROVENANCE) == UNKNOWN:
        return "provenance unknown"
    agent = fields.get(AGENT)
    if not agent:
        return None
    if last := fields.get(LAST_WRITER):
        return f"briefed agent {agent}, last written by {_words(last)}"
    return f"written by agent {agent}"


def self_reviewed(source: str) -> str | None:
    """The file a row's `Source` cell names as edited by the context that wrote the verdict
    (its `self-review:<path>` token), or None for a cell carrying no such token."""
    for token in str(source or "").split():
        name, _, path = token.partition(":")
        if name == SELF_REVIEW and path:
            return path
    return None


def self_review(repo_root: Path | str, affects: list[str], issued: list[str], *,
                verdict: tuple | None = None, argv: list[str] | None = None,
                since: str | None = None, env: Mapping | None = None) -> dict | None:
    """{"path", "context"} when the context that wrote this verdict edited one of the unit's
    `affects` before it first received a verdict path in `issued`, else None.

    The judged context is the writer of `verdict`, a (path, bytes) pair, when one is given, or
    else the context whose transcript holds the running command `argv`. None when the unit
    declares no Affects or Claude Code is not the harness (with no transcript read), or when no
    context is found. An edit before `since`, an ISO stamp, belongs to an earlier delivery."""
    from lib import token_meters  # noqa: PLC0415 - as `read`
    env = os.environ if env is None else env
    affects = [a.strip().strip("/") for a in affects if a and a.strip().strip("/")]
    session = str(env.get(SESSION_ENV) or "").strip()
    if not affects or not _PLAIN.fullmatch(session):
        return None
    claude = _ClaudeStore()
    chosen = token_meters.select(repo_root, claude, env).get(token_meters.HARNESS)
    if chosen != token_meters.CLAUDE or _by_default(repo_root, env, claude):
        return None
    contexts = _contexts(Path(repo_root), session, env)[1]
    judged = _writer(contexts, *verdict) if verdict else _recorder(contexts, argv or [])
    if judged is None:
        return None
    edited = _edited_before_brief(Path(repo_root), dict(contexts)[judged], affects, issued,
                                  since)
    return {"path": edited, "context": judged} if edited else None


def _writer(contexts: list, path: Path | str, data: bytes) -> str | None:
    """The context whose write of `path` is the newest and carried `data`, or None."""
    path = Path(path)
    target = path.resolve()
    needles = {json.dumps(str(p), ensure_ascii=False)[1:-1].encode("utf-8")
               for p in (path.absolute(), target)}
    carries, writes = [], []
    for order, (ctx, f) in enumerate(contexts):
        _scan(f, ctx, order, needles, target, data.decode("utf-8", "replace"), carries, writes)
    last = max(writes, key=lambda w: w[0]) if writes else None
    return last[1] if last and _carried(last, data) else None


def _recorder(contexts: list, argv: list[str]) -> str | None:
    """The context whose newest Bash call runs `argv`: its command names the script and holds
    every argument as a word. None when no transcript holds it."""
    args = [str(a) for a in argv[1:] if str(a)]
    if not argv or not args:
        return None
    script = Path(str(argv[0])).name
    needles = [json.dumps(a, ensure_ascii=False)[1:-1].encode("utf-8") for a in (script, *args)]
    best = None
    for order, (ctx, f) in enumerate(contexts):
        for n, _raw, rec in _records(f, lambda raw: all(nd in raw for nd in needles)):
            key = (str(rec.get("timestamp") or ""), order, n)
            if any(_runs(u, script, args) for u in _tool_uses(rec)) and (
                    best is None or key > best[0]):
                best = (key, ctx)
    return best[1] if best else None


def _runs(use: dict, script: str, args: list[str]) -> bool:
    command = (use.get("input") or {}).get("command") if use.get("name") == "Bash" else None
    if not isinstance(command, str):
        return False
    try:
        words = shlex.split(command)
    except ValueError:
        words = command.split()
    return script in {Path(w).name for w in words} and all(a in words for a in args)


def _edited_before_brief(repo_root: Path, f: Path, affects: list[str], issued: list[str],
                         since: str | None) -> str | None:
    """The repository-relative Affects file transcript `f` edited before its first record
    carrying an issued verdict path, and at or after `since`; None when it edited none."""
    try:
        meta = json.loads(f.with_suffix(".meta.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        meta = {}
    tree = meta.get(WORKTREE_KEY) if isinstance(meta, dict) else None
    roots = [Path(r).resolve() for r in (tree, repo_root) if isinstance(r, (str, Path)) and r]
    briefs = {json.dumps(str(v), ensure_ascii=False)[1:-1].encode("utf-8")
              for p in issued for v in (Path(p), Path(p).resolve())}
    names = {json.dumps(a, ensure_ascii=False)[1:-1].encode("utf-8") for a in affects}
    floor = sdlc_md.parse_iso8601(since) if since else None
    wanted = briefs | names
    for _n, raw, rec in _records(f, lambda raw: any(nd in raw for nd in wanted)):
        if any(nd in raw for nd in briefs):
            return None
        stamp = sdlc_md.parse_iso8601(rec.get("timestamp"))
        if floor and stamp and stamp < floor:
            continue
        for use in _tool_uses(rec):
            given = use.get("input") if isinstance(use.get("input"), dict) else {}
            if use.get("name") in ("Write", *EDIT_TOOLS) and (
                    rel := _affected(given.get("file_path") or given.get("notebook_path"),
                                     roots, affects)):
                return rel
    return None


def _affected(value, roots: list[Path], affects: list[str]) -> str | None:
    """`value`, an absolute path, relative to the first of `roots` holding it, when that names
    an Affects file or a file under an Affects folder; else None."""
    if not isinstance(value, str) or not Path(value).is_absolute():
        return None
    path = Path(value).resolve()
    for root in roots:
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            continue
        if any(rel == a or rel.startswith(a + "/") for a in affects):
            return rel
    return None
