#!/usr/bin/env python3
"""SDLC Studio GitHub Issues sync.

Two-way sync between local CR / Story / Epic files and GitHub Issues
via the `gh` CLI. No direct API calls, no token handling.

Label convention:
    sdlc:cr                 Issue mirrors a Change Request
    sdlc:story              Issue mirrors a User Story
    sdlc:epic               Issue mirrors an Epic
    sdlc:status:<state>     Current status (proposed, ready, done, ...)
    sdlc:priority:P1..P4    Optional priority
    sdlc:type:<kind>        Optional type

Subcommands:
    pull    Fetch labelled issues, create missing local files
    push    Create or update issues from local files
    cascade List merged PRs since last run, trigger Story Completion
            Cascade on referenced stories
    state   Print the sync state file

State lives in sdlc-studio/.local/github-sync-state.json and is
never committed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

LABEL_PREFIX = "sdlc"

TYPE_LABELS = {
    "cr": f"{LABEL_PREFIX}:cr",
    "story": f"{LABEL_PREFIX}:story",
    "epic": f"{LABEL_PREFIX}:epic",
}

# github_sync mirrors only these artefact types; their directories and id prefixes come from
# the shared `sdlc_md.ARTIFACT_TYPES` map (via `sdlc_md.artifact_files`), so there is no local
# duplicate of the type table to drift out of step.
_MIRRORED = ("cr", "story", "epic")

STATE_PATH = "sdlc-studio/.local/github-sync-state.json"


def _state_path(root: str | Path = ".") -> Path:
    """The sync-state file resolved against `root`, so `--root <dir>` from outside the repo
    reads and writes the state under `<dir>`, not the cwd."""
    return Path(root) / STATE_PATH


# -----------------------------------------------------------------------------
# gh CLI wrapper
# -----------------------------------------------------------------------------


GH_TIMEOUT = 120  # seconds - a hung gh call (proxy, auth prompt) must fail, not block forever


class GhError(RuntimeError):
    """A `gh` CLI call failed (non-zero exit or timeout) - distinct from an empty result."""


def gh(*args: str, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a `gh` subcommand, raising RuntimeError if the CLI is absent. A timeout is
    surfaced as a non-zero CompletedProcess (rc 124), never an indefinite hang."""
    if shutil.which("gh") is None:
        raise RuntimeError("gh CLI not on PATH. Install https://cli.github.com/")
    try:
        return subprocess.run(
            ["gh", *args],
            capture_output=capture,
            text=True,
            check=False,
            timeout=GH_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(
            ["gh", *args], 124, "", f"gh timed out after {GH_TIMEOUT}s")


# Shared JSON-with-default loader (kept under this name for callers/tests).
_loads = sdlc_md.loads


def gh_issue_list(label: str) -> list[dict]:
    """All issues carrying `label` (open and closed). Raises GhError on a gh failure so a
    real error is never conflated with "no issues"; malformed JSON on a clean exit
    still degrades to [] (a parse tolerance, not a failure)."""
    result = gh(
        "issue", "list",
        "--label", label,
        "--state", "all",
        "--json", "number,title,state,body,labels,url,updatedAt,createdAt",
        "--limit", "500",
    )
    if result.returncode != 0:
        raise GhError(f"gh issue list failed ({label}): {result.stderr.strip()}")
    return _loads(result.stdout, [])


def gh_issue_create(title: str, body: str, labels: list[str]) -> int | None:
    """Create an issue, returning its number, or None on failure."""
    args = ["issue", "create", "--title", title, "--body", body]
    for lbl in labels:
        args.extend(["--label", lbl])
    result = gh(*args)
    if result.returncode != 0:
        print(f"gh issue create failed: {result.stderr}", file=sys.stderr)
        return None
    # Output is the issue URL; extract the number
    match = re.search(r"/issues/(\d+)", result.stdout or "")
    return int(match.group(1)) if match else None


def gh_issue_edit(number: int, labels_add: list[str], labels_remove: list[str]) -> bool:
    """Add and remove labels on an issue. Returns True on success."""
    if not labels_add and not labels_remove:
        return True
    args = ["issue", "edit", str(number)]
    for lbl in labels_add:
        args.extend(["--add-label", lbl])
    for lbl in labels_remove:
        args.extend(["--remove-label", lbl])
    result = gh(*args)
    if result.returncode != 0:
        print(f"gh issue edit failed for #{number}: {result.stderr}", file=sys.stderr)
        return False
    return True


def gh_pr_list_merged(since_ref: str | None) -> list[dict]:
    """Return merged PRs, optionally only those merged after `since_ref`."""
    # Use --search to filter by merge date if given; otherwise list the last 100 merged
    args = [
        "pr", "list",
        "--state", "merged",
        "--json", "number,title,body,mergedAt,mergeCommit",
        "--limit", "200",
    ]
    result = gh(*args)
    if result.returncode != 0:
        print(f"gh pr list failed: {result.stderr}", file=sys.stderr)
        return []
    prs = _loads(result.stdout, [])
    if since_ref:
        since = since_ref
        prs = [p for p in prs if (p.get("mergedAt") or "") > since]
    return prs


# -----------------------------------------------------------------------------
# Local file parsing
# -----------------------------------------------------------------------------


@dataclass
class LocalRecord:
    type: str
    rec_id: str  # e.g. CR-0001, US0023, EP0004
    path: Path
    title: str
    status: str
    priority: str | None
    rec_type: str | None  # CR "type" (feature-request, etc.)
    github_issue: int | None
    body: str
    content_hash: str

    def labels(self) -> list[str]:
        """Build the full sdlc label set for this record."""
        labels = [TYPE_LABELS[self.type]]
        if self.status:
            labels.append(f"{LABEL_PREFIX}:status:{_slug(self.status)}")
        if self.priority:
            labels.append(f"{LABEL_PREFIX}:priority:{self.priority}")
        if self.rec_type:
            labels.append(f"{LABEL_PREFIX}:type:{_slug(self.rec_type)}")
        return labels


_slug = sdlc_md.slug


def _hash_body(body: str) -> str:
    """Return a short content hash used to detect local edits since last push."""
    return "sha256:" + hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]


_extract_field = sdlc_md.extract_field


def _extract_github_issue(text: str) -> int | None:
    """Return the linked GitHub issue number from the metadata, if any."""
    value = _extract_field(text, "GitHub Issue")
    if not value:
        return None
    m = re.search(r"(\d+)", value)
    return int(m.group(1)) if m else None


def parse_local_file(path: Path, type_: str) -> LocalRecord | None:
    """Parse one CR/Story/Epic markdown file into a LocalRecord."""
    text = path.read_text(encoding="utf-8")
    title = sdlc_md.extract_h1_title(text) or path.stem
    status = _extract_field(text, "Status") or ""
    priority = _extract_field(text, "Priority")
    rec_type = _extract_field(text, "Type")
    github_issue = _extract_github_issue(text)
    # rec_id is the file's ID prefix (CR-NNNN with a dash; US/EP NNNN without).
    rec_id = sdlc_md.extract_record_id(path.stem) or path.stem
    return LocalRecord(
        type=type_,
        rec_id=rec_id,
        path=path,
        title=title,
        status=status,
        priority=priority,
        rec_type=rec_type,
        github_issue=github_issue,
        body=text,
        content_hash=_hash_body(text),
    )


def walk_local(type_: str, repo_root: str | Path = ".") -> Iterable[LocalRecord]:
    """Yield parsed records for every CR/Story/Epic file of `type_`. Discovery goes through the
    shared `sdlc_md.artifact_files`, so a lowercase-named file (`cr0001.md`) is found too - the
    old `CR*.md` prefix glob was case-sensitive on Linux and silently missed them."""
    if type_ not in _MIRRORED:  # github_sync only mirrors cr/story/epic
        return []
    result: list[LocalRecord] = []
    for p in sdlc_md.artifact_files(type_, Path(repo_root)):
        rec = parse_local_file(p, type_)
        if rec:
            result.append(rec)
    return result


# -----------------------------------------------------------------------------
# State file
# -----------------------------------------------------------------------------


def _empty_state() -> dict:
    """Return a fresh, empty sync-state structure."""
    return {
        "version": 1,
        "last_pull": None,
        "last_push": None,
        "last_cascade_ref": None,
        "mappings": {},
    }


def load_state(path: Path = Path(STATE_PATH)) -> dict:
    """Load the sync state, falling back to an empty state if missing or corrupt."""
    if not path.exists():
        return _empty_state()
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print(
            f"warning: {path} is not valid JSON; starting from empty state",
            file=sys.stderr,
        )
        return _empty_state()


def save_state(state: dict, path: Path = Path(STATE_PATH)) -> None:
    """Write the sync state to disk, creating parent dirs as needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


now_iso = sdlc_md.now_iso8601


# -----------------------------------------------------------------------------
# Local file mutation
# -----------------------------------------------------------------------------


def set_github_issue_field(path: Path, number: int) -> None:
    """Write the `> **GitHub Issue:** #N` metadata line into a local file."""
    text = path.read_text(encoding="utf-8")
    if _extract_github_issue(text) == number:
        return
    if _extract_field(text, "GitHub Issue") is not None:
        # Replace existing line
        new_text = re.sub(
            r"^(>\s*\*\*GitHub Issue:\*\*).*$",
            lambda m: f"{m.group(1)} #{number}",
            text,
            count=1,
            flags=re.M,
        )
    else:
        # Insert after Status line if present, else after the title
        insert_line = f"> **GitHub Issue:** #{number}"
        if re.search(r"^>\s*\*\*Status:\*\*", text, re.M):
            new_text = re.sub(
                r"(^>\s*\*\*Status:\*\*.*$)",
                r"\1\n" + insert_line,
                text,
                count=1,
                flags=re.M,
            )
        else:
            new_text = text.rstrip() + "\n\n" + insert_line + "\n"
    path.write_text(new_text, encoding="utf-8")


# -----------------------------------------------------------------------------
# Secret scanning: a push publishes a record's body to an issue; a secret-shaped
# token in that body must never be leaked to a public repo.
# -----------------------------------------------------------------------------

# High-signal secret shapes. Each is a (name, compiled-pattern) pair; a match is
# reported redacted (prefix + length), never in full.
_SECRET_PATTERNS = [
    ("github-token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("github-pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{22,}\b")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("ai-api-key", re.compile(r"\bsk-(?:ant-)?[A-Za-z0-9_-]{20,}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    ("private-key-block", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("credential-assignment", re.compile(
        r"(?i)\b(?:password|passwd|secret|token|api[_-]?key)\b\s*[:=]\s*"
        r"['\"]?[A-Za-z0-9/+=_-]{12,}")),
]


def _redact(match: str) -> str:
    """A finding shown as prefix + length, never the raw secret."""
    prefix = match[:4]
    return f"{prefix}***(len={len(match)})"


def scan_secrets(text: str) -> list[dict]:
    """Return one finding dict {kind, redacted} per secret-shaped token in `text`.
    Deduplicated by (kind, redacted); empty list when the text looks clean."""
    findings: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for kind, pat in _SECRET_PATTERNS:
        for m in pat.findall(text):
            token = m if isinstance(m, str) else m[0]
            red = _redact(token)
            key = (kind, red)
            if key not in seen:
                seen.add(key)
                findings.append({"kind": kind, "redacted": red})
    return findings


def repo_is_public() -> bool | None:
    """True if the current repo's GitHub visibility is PUBLIC, False if PRIVATE/INTERNAL,
    None when it cannot be determined (gh error / absent). Callers treat None as unsafe
    (assume public) so an unknown target never gets a secret pushed by default."""
    result = gh("repo", "view", "--json", "visibility", "-q", ".visibility")
    if result.returncode != 0:
        return None
    vis = (result.stdout or "").strip().upper()
    if vis == "PUBLIC":
        return True
    if vis in ("PRIVATE", "INTERNAL"):
        return False
    return None


# -----------------------------------------------------------------------------
# Commands
# -----------------------------------------------------------------------------


def cmd_push(args: argparse.Namespace) -> int:
    """Create or update GitHub issues from local CR/Story/Epic files."""
    types = _resolve_types(args.type)
    state = load_state(_state_path(args.root))
    mappings = state.get("mappings", {})
    created = 0
    updated = 0
    blocked = 0
    failed = False  # any gh create/edit failure - BG0092: do not stamp last_push, exit non-zero
    allow_secrets = getattr(args, "allow_secrets", False)
    # Visibility is resolved lazily and cached: only a record that actually carries a
    # secret triggers the `gh repo view` call, so a clean push (or a dry run) makes no
    # extra network call. Unknown (None) is treated as unsafe (assume public).
    _vis_cache: list = []  # empty = unresolved; [value] = cached

    def _target_public():
        if not _vis_cache:
            _vis_cache.append(repo_is_public())
        return _vis_cache[0]

    for type_ in types:
        # Fetch the type's issues at most once per type (lazily, only if a
        # record needs a label sync) rather than once per record.
        issues_by_number: dict[int, dict] | None = None
        for rec in walk_local(type_, args.root):
            if rec.github_issue is None:
                title = f"[{rec.rec_id}] {rec.title}"
                labels = rec.labels()
                # Never publish a secret-shaped token to a public (or unknown-visibility)
                # target. Only a confirmed-private repo, or an explicit --allow-secrets,
                # lets a flagged record through.
                if not allow_secrets:
                    findings = scan_secrets(f"{title}\n{rec.body}")
                    public = _target_public() if findings else False
                    if findings and public is not False:
                        kinds = ", ".join(f"{f['kind']}={f['redacted']}" for f in findings)
                        where = "public" if public else "unknown-visibility"
                        print(
                            f"REFUSED {rec.rec_id}: {len(findings)} secret-shaped token(s) "
                            f"would be pushed to a {where} repo [{kinds}] - remove the secret "
                            f"or pass --allow-secrets for a confirmed-private target",
                            file=sys.stderr,
                        )
                        blocked += 1
                        continue
                if args.dry_run:
                    print(f"[DRY] would create issue for {rec.rec_id}: {title}")
                    continue
                # CR0206: adopt an existing `[rec_id]`-titled issue instead of blind-creating a
                # duplicate. A crash or gh timeout AFTER the server accepted a create but BEFORE
                # the local stamp landed would otherwise mint a second issue on the re-run.
                if issues_by_number is None:
                    issues_by_number = {
                        i.get("number"): i for i in gh_issue_list(TYPE_LABELS[type_])
                    }
                adopt = next((i for i in issues_by_number.values()
                              if str(i.get("title", "")).startswith(f"[{rec.rec_id}]")), None)
                if adopt is not None:
                    set_github_issue_field(rec.path, adopt["number"])
                    print(f"[APL] adopted existing issue #{adopt['number']} for {rec.rec_id} "
                          "(not re-created)")
                    # re-parse for the post-stamp hash, like the create path - so the next push
                    # sees a matching hash and skips instead of an extra no-op label-sync
                    refreshed = parse_local_file(rec.path, type_)
                    mappings[rec.rec_id] = {
                        "type": type_, "issue": adopt["number"],
                        "hash": refreshed.content_hash if refreshed else rec.content_hash,
                        "updated_at": now_iso()}
                    updated += 1
                    continue
                number = gh_issue_create(title, rec.body, labels)
                if number is None:
                    print(f"failed to create issue for {rec.rec_id}", file=sys.stderr)
                    failed = True
                    continue
                set_github_issue_field(rec.path, number)
                # Re-parse to pick up the new hash
                refreshed = parse_local_file(rec.path, type_)
                if refreshed is None:
                    continue
                mappings[refreshed.rec_id] = {
                    "type": type_,
                    "issue": number,
                    "hash": refreshed.content_hash,
                    "updated_at": now_iso(),
                }
                created += 1
                print(f"[APL] created issue #{number} for {rec.rec_id}")
            else:
                mapped = mappings.get(rec.rec_id)
                if mapped and mapped.get("hash") == rec.content_hash:
                    continue  # No local change since last push
                # Label sync: compute current desired labels, diff against
                # the issue's existing labels
                if args.dry_run:
                    print(
                        f"[DRY] would sync labels on issue #{rec.github_issue} "
                        f"for {rec.rec_id}"
                    )
                    continue
                if issues_by_number is None:
                    issues_by_number = {
                        i.get("number"): i for i in gh_issue_list(TYPE_LABELS[type_])
                    }
                issue = issues_by_number.get(rec.github_issue)
                if issue is None:
                    print(
                        f"issue #{rec.github_issue} not found via gh for "
                        f"{rec.rec_id}; skipping",
                        file=sys.stderr,
                    )
                    continue
                existing_labels = {l["name"] for l in issue.get("labels", [])}
                desired_labels = set(rec.labels())
                add = [l for l in desired_labels if l not in existing_labels]
                remove = [
                    l
                    for l in existing_labels
                    if l.startswith(f"{LABEL_PREFIX}:") and l not in desired_labels
                ]
                if gh_issue_edit(rec.github_issue, add, remove):
                    mappings[rec.rec_id] = {
                        "type": type_,
                        "issue": rec.github_issue,
                        "hash": rec.content_hash,
                        "updated_at": now_iso(),
                    }
                    updated += 1
                    print(
                        f"[APL] synced labels on #{rec.github_issue} "
                        f"for {rec.rec_id}: +{add} -{remove}"
                    )
                else:
                    print(f"failed to edit issue #{rec.github_issue} for {rec.rec_id}",
                          file=sys.stderr)
                    failed = True

    if not args.dry_run and not failed:
        # BG0092: only a fully-successful push advances last_push. A failed gh call leaves the
        # timestamp untouched (mirrors the BG0064 pull fix) so nothing keyed on push
        # success/recency is misled; mappings from the calls that DID succeed are still saved.
        state["last_push"] = now_iso()
        state["mappings"] = mappings
        save_state(state, _state_path(args.root))
    elif not args.dry_run and failed:
        # persist the mappings we did land, but not the success stamp
        state["mappings"] = mappings
        save_state(state, _state_path(args.root))
        print("push: a gh call failed; last_push left unchanged", file=sys.stderr)

    print(f"push: created={created} updated={updated} blocked={blocked}")
    return 1 if (blocked or failed) else 0


def cmd_pull(args: argparse.Namespace) -> int:
    """List labelled issues that have no local file and need ingesting."""
    types = _resolve_types(args.type)
    state = load_state(_state_path(args.root))
    mappings = state.get("mappings", {})
    pulled = 0

    # Build a reverse index of local records keyed by github_issue for
    # fast "already synced?" checks
    by_issue: dict[int, LocalRecord] = {}
    for type_ in types:
        for rec in walk_local(type_, args.root):
            if rec.github_issue is not None:
                by_issue[rec.github_issue] = rec

    failed = False
    for type_ in types:
        label = TYPE_LABELS[type_]
        try:
            issues = gh_issue_list(label)
        except GhError as exc:
            print(f"pull: {exc}", file=sys.stderr)
            failed = True
            continue
        for issue in issues:
            number = issue.get("number")
            if number in by_issue:
                continue  # Already linked locally
            title = issue.get("title", "")
            body = issue.get("body") or ""
            if args.dry_run:
                print(f"[DRY] would create local {type_} from issue #{number}: {title}")
                continue
            # Defer to the workflow reference files for actually creating
            # the file correctly from a template. This command prints
            # instructions rather than guessing template field values.
            print(
                f"[TODO] pull: issue #{number} labelled {label} has no local "
                f"{type_} file. Run the matching `/sdlc-studio {type_} create` "
                f"workflow with --from-issue {number} to ingest the body into "
                f"the correct template - the create MUST pass `--provenance "
                f"external` (the verify shell gate reads that stamp) - then "
                f"re-run `github_sync.py push` to write the mapping."
            )
            pulled += 1

    if failed:
        # A gh call failed: do NOT advance last_pull or save state - the file would then
        # assert a pull that never happened, misleading anything keyed on the timestamp.
        print("pull: aborted - a gh call failed; last_pull left unchanged", file=sys.stderr)
        return 1

    if not args.dry_run:
        state["last_pull"] = now_iso()
        state["mappings"] = mappings
        save_state(state, _state_path(args.root))

    print(f"pull: issues_needing_ingest={pulled}")
    return 0


_CLOSES_RE = re.compile(r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)", re.I)
_STORY_REF_RE = re.compile(r"sdlc:story\s+(US\d{4})", re.I)
_CR_REF_RE = re.compile(r"sdlc:cr\s+(CR-\d{4})", re.I)


def cmd_cascade(args: argparse.Namespace) -> int:
    """Find merged PRs whose bodies reference stories/CRs to cascade."""
    state = load_state(_state_path(args.root))
    since = args.since or state.get("last_cascade_ref")
    prs = gh_pr_list_merged(since)
    if not prs:
        print("no merged PRs found in range")
        return 0

    referenced_stories: set[int] = set()
    referenced_story_ids: set[str] = set()
    referenced_cr_ids: set[str] = set()

    for pr in prs:
        body = pr.get("body") or ""
        for m in _CLOSES_RE.finditer(body):
            referenced_stories.add(int(m.group(1)))
        for m in _STORY_REF_RE.finditer(body):
            referenced_story_ids.add(m.group(1).upper())
        for m in _CR_REF_RE.finditer(body):
            referenced_cr_ids.add(m.group(1).upper())

    if not (referenced_stories or referenced_story_ids or referenced_cr_ids):
        print("no sdlc references found in merged PR bodies")
        return 0

    # Map issue numbers back to local stories via github_issue field
    local_stories_by_issue: dict[int, LocalRecord] = {}
    for rec in walk_local("story", args.root):
        if rec.github_issue is not None:
            local_stories_by_issue[rec.github_issue] = rec

    triggered: list[str] = []
    for issue_num in referenced_stories:
        rec = local_stories_by_issue.get(issue_num)
        if rec is None:
            continue
        triggered.append(rec.rec_id)
    for sid in referenced_story_ids:
        triggered.append(sid)
    for cid in referenced_cr_ids:
        triggered.append(cid)

    if not triggered:
        print("found sdlc references but no matching local records")
        return 0

    print(
        "cascade candidates (trigger Story Completion Cascade via reconcile):"
    )
    for ident in sorted(set(triggered)):
        print(f"  - {ident}")
    print(
        "next step: `/sdlc-studio reconcile --story <id>` (or --scope stories)"
        " to mark these Done after PR merge."
    )

    if not args.dry_run and prs:
        # max(mergedAt): gh orders by creation, so prs[0] can be an early-created/
        # late-merged PR - taking the newest merge instant avoids re-reporting.
        state["last_cascade_ref"] = max((pr.get("mergedAt") or "") for pr in prs) or None
        save_state(state, _state_path(args.root))

    return 0


def cmd_state(args: argparse.Namespace) -> int:
    """Print the current sync-state file as JSON."""
    state = load_state(_state_path(args.root))
    print(json.dumps(state, indent=2))
    return 0


def _resolve_types(type_arg: str) -> list[str]:
    """Expand a --type argument (including `all`) into a list of types."""
    if type_arg == "all":
        return ["cr", "story", "epic"]
    if type_arg in TYPE_LABELS:
        return [type_arg]
    raise SystemExit(f"error: unknown --type: {type_arg}")


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for all subcommands."""
    p = argparse.ArgumentParser(
        prog="github_sync.py",
        description="Two-way sync between local sdlc-studio records and GitHub Issues.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    push = sub.add_parser("push", help="Create or update issues from local files")
    push.add_argument("--type", default="cr", choices=["cr", "story", "epic", "all"])
    push.add_argument("--dry-run", action="store_true")
    push.add_argument("--allow-secrets", action="store_true", dest="allow_secrets",
                      help="Push even when a record body carries a secret-shaped token "
                           "(only for a confirmed-private target); default refuses")
    push.add_argument("--root", default=".", help="Repo root (default: .)")
    push.set_defaults(func=cmd_push)

    pull = sub.add_parser("pull", help="Fetch labelled issues for local ingest")
    pull.add_argument("--type", default="cr", choices=["cr", "story", "epic", "all"])
    pull.add_argument("--dry-run", action="store_true")
    pull.add_argument("--root", default=".", help="Repo root (default: .)")
    pull.set_defaults(func=cmd_pull)

    cas = sub.add_parser("cascade", help="Find merged PRs that should trigger cascades")
    cas.add_argument("--since", help="Only consider PRs merged after this ISO timestamp")
    cas.add_argument("--dry-run", action="store_true")
    cas.add_argument("--root", default=".", help="Repo root (default: .)")
    cas.set_defaults(func=cmd_cascade)

    st = sub.add_parser("state", help="Print sync state")
    st.add_argument("--root", default=".", help="Repo root (default: .)")
    st.set_defaults(func=cmd_state)

    return p


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the chosen subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 127


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
