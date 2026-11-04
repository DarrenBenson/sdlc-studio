#!/usr/bin/env python3
"""Cursor's token reader, the module `token_meters` loads for the Cursor harness.

A Cursor cloud agent writes no Claude transcript, so its spend is read from Cursor's cloud usage
API, `GET /v1/agents/{id}/usage`, whose `totalUsage` holds `inputTokens`, `outputTokens`,
`cacheWriteTokens`, `cacheReadTokens` and `totalTokens`. The call is opt-in: it is made only
when a Cursor API key (`KEY_ENV`) and the agent's id (`AGENT_ENV`) are both set, and otherwise
no request is made and the reading names the variable that is missing.

`tokens` is input + output + cache write, the basis every reader counts on; the cache reads are
`cache_read`, apart from it, and `totalTokens`, which holds them, is never the figure. An answer
carrying a `totalTokens` that is not the sum of the four is refused, since the four would then
overlap.

The call never holds the close: it runs on a worker thread joined for at most
`TIMEOUT_SECONDS`, and an HTTP error, a timeout, an unreachable API, a malformed answer or a
run with no usage recorded yet is tokens None with the reason, never zero. A redirect is
refused, not followed, so the key is never sent where a redirect points. The key is sent in one
request header and nowhere else: no reason quotes an exception's message, an error's body or
its headers, and `source` is built from the agent id, never from the URL.

`read` decides which surface a reading comes from; today the cloud API is the only one.
"""
from __future__ import annotations

import json
import threading
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Mapping
from pathlib import Path

from .token_meters import CACHE_READ

#: The Cursor API key. It is sent as the request's bearer token and is never written into a
#: reading, a reason or a source.
KEY_ENV = "CURSOR_API_KEY"
#: The Cursor cloud agent's id, the usage API's path parameter.
AGENT_ENV = "SDLC_STUDIO_CURSOR_AGENT_ID"
#: The API's base URL, overridable so a test reaches a local stub and never the network.
API_ENV = "SDLC_STUDIO_CURSOR_API"
API_BASE = "https://api.cursor.com"
#: The longest the close waits for the usage API, connect and answer together.
TIMEOUT_SECONDS = 5.0
#: The largest answer read; a longer one is refused rather than parsed.
MAX_BYTES = 1 << 20
#: The agent id signals Cursor to `token_meters`. The key does not: a key exported in another
#: harness's shell is not a Cursor run.
SIGNALS = (AGENT_ENV,)
#: The `totalUsage` fields `tokens` sums, and the cache reads it leaves out.
COUNTED = ("inputTokens", "outputTokens", "cacheWriteTokens")
CACHE_READS = "cacheReadTokens"
TOTAL = "totalTokens"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Refuses every redirect, which then surfaces as its HTTP status: a followed redirect
    carries the request's headers, the key among them, to wherever it points."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ARG002
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


def read(repo_root: Path, env: Mapping) -> dict:  # noqa: ARG001 - the reader interface
    """This Cursor run's reading: the cloud usage API's when `KEY_ENV` and `AGENT_ENV` are both
    set, else tokens None naming the one or two that are not, with no request made."""
    key = (env.get(KEY_ENV) or "").strip()
    agent = (env.get(AGENT_ENV) or "").strip()
    missing = [name for name, value in ((KEY_ENV, key), (AGENT_ENV, agent)) if not value]
    if missing:
        return {"tokens": None, "reason": (
            f"{' and '.join(missing)} {'is' if len(missing) == 1 else 'are'} not set, so the "
            f"Cursor cloud usage API is not called and this run's tokens cannot be read")}
    base = (env.get(API_ENV) or "").strip() or API_BASE
    return read_cloud(key, agent, base)


def read_cloud(key: str, agent: str, base: str = API_BASE) -> dict:
    """Agent `agent`'s reading from the usage API at `base`, or tokens None with the reason."""
    url = f"{base.rstrip('/')}/v1/agents/{urllib.parse.quote(agent, safe='')}/usage"
    got = _get(url, key)
    if isinstance(got, str):
        return {"tokens": None, "reason": f"the Cursor cloud usage API, for agent {agent}: {got}"}
    return _reading(got, agent)


def _get(url: str, key: str) -> bytes | str:
    """The answer's body, or the reason there is none, built from the HTTP status or the
    exception's type alone: a message, a body or a header may echo the key."""
    req = urllib.request.Request(url, headers={"Accept": "application/json",
                                               "Authorization": f"Bearer {key}"})
    box: dict = {}

    def call() -> None:
        try:
            with _OPENER.open(req, timeout=TIMEOUT_SECONDS) as resp:
                box["body"] = resp.read(MAX_BYTES + 1)
        except urllib.error.HTTPError as exc:
            exc.close()
            box["error"] = exc
        except Exception as exc:  # noqa: BLE001 - every failure is a reason, never a raise
            box["error"] = exc

    worker = threading.Thread(target=call, name="cursor-usage", daemon=True)
    worker.start()
    worker.join(TIMEOUT_SECONDS)
    if worker.is_alive():
        return f"it did not answer within {TIMEOUT_SECONDS:g} seconds"
    exc = box.get("error")
    if exc is None:
        body = box["body"]
        return body if len(body) <= MAX_BYTES else f"its answer exceeds {MAX_BYTES} bytes"
    if isinstance(exc, urllib.error.HTTPError):
        return f"it answered HTTP {exc.code}"
    cause = exc.reason if isinstance(exc, urllib.error.URLError) else exc
    if isinstance(cause, TimeoutError):
        return f"it did not answer within {TIMEOUT_SECONDS:g} seconds"
    if isinstance(exc, urllib.error.URLError):
        named = type(cause).__name__ if isinstance(cause, BaseException) else "URLError"
        return f"it could not be reached ({named})"
    return f"the call failed ({type(exc).__name__})"


def _count(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _reading(body: bytes, agent: str) -> dict:
    """The reading in the usage API's answer `body`, or tokens None with the reason."""
    def none(why: str) -> dict:
        return {"tokens": None, "reason": f"the Cursor cloud usage API, for agent {agent}: {why}"}
    try:
        doc = json.loads(body)
    except ValueError:
        return none("its answer is not JSON")
    usage = doc.get("totalUsage") if isinstance(doc, dict) else None
    if usage is None:
        return none("it records no usage for this agent yet")
    if not isinstance(usage, dict):
        return none("its totalUsage is not an object")
    for field in (*COUNTED, CACHE_READS):
        if not _count(usage.get(field)):
            return none(f"its totalUsage {field} is {usage.get(field)!r}, not a count")
    tokens = sum(usage[f] for f in COUNTED)
    total = usage.get(TOTAL)
    if total is not None and total != tokens + usage[CACHE_READS]:
        return none(f"its totalTokens {total!r} is not the sum of the four counts, so they "
                    f"overlap and no figure is formed")
    if tokens == 0:
        return none("it records no usage for this agent yet")
    return {"tokens": tokens, CACHE_READ: usage[CACHE_READS], "agent_id": agent,
            "source": f"the Cursor cloud usage API, agent {agent}",
            "basis": ("Cursor cloud usage API totalUsage for the agent, every run of it: input "
                      "+ output + cache write, cache reads apart; totalTokens, which holds "
                      "them, is not used"),
            "includes_subagents": True}

