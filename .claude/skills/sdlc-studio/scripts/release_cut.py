#!/usr/bin/env python3
"""Release cut: turn the accumulated changelog fragments into a versioned section, and guard the
tag so it can never assert a green that was measured on a different tree.

Two verbs:

- `changelog-cut --version X.Y.Z` composes the pending `changelog.d/` fragments into `[Unreleased]`
  (the release-time `compose --apply`), then moves that body under a new `## [X.Y.Z] - <date>`
  header, leaving `[Unreleased]` empty. This is the deterministic cut US0348 requires - the notes
  come from the per-unit fragments, never a hand-written section.

- `record-green --commit <sha>` stamps the commit the pre-tag gate passed on; `tag-check --commit
  <sha>` refuses unless that stamp names the same commit. A tag asserting a green measured on a
  different tree is the false claim this exists to prevent (US0348 AC3).
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import changelog  # noqa: E402
from lib import sdlc_md  # noqa: E402

#: Where the pre-tag gate records the commit it judged. Read by `tag-check`, so a tag can only be
#: cut on the exact tree the gate ran over.
GREEN_MARKER = "release-gate-green.json"


def _green_path(root: Path) -> Path:
    return Path(root) / "sdlc-studio" / ".local" / GREEN_MARKER


def cut_changelog(root: Path | str, version: str) -> str:
    """Compose the pending fragments into `[Unreleased]`, then move its body under a
    `## [version] - <date>` header, leaving `[Unreleased]` empty. Returns the new header line.

    Refuses when the version already has a section (the cut is not idempotent-by-accident: a second
    cut of the same version would silently duplicate it) or when there is no `[Unreleased]`."""
    root = Path(root)
    changelog.compose(root, apply=True)          # the release-time fold + consume of the fragments
    clog = root / "CHANGELOG.md"
    text = clog.read_text(encoding="utf-8")
    header = f"## [{version}]"
    if re.search(rf"(?m)^{re.escape(header)}", text):
        raise ValueError(f"CHANGELOG.md already carries a {header} section - nothing cut")
    if "## [Unreleased]" not in text:
        raise ValueError("CHANGELOG.md has no '## [Unreleased]' section to cut from")
    head, rest = text.split("## [Unreleased]", 1)
    nxt = re.search(r"\n## \[", rest)
    body, tail = (rest[:nxt.start()], rest[nxt.start():]) if nxt else (rest, "")
    date = sdlc_md.now_date()
    new_header = f"## [{version}] - {date}"
    # [Unreleased] is emptied (header only); the accumulated body becomes the versioned section
    out = f"{head}## [Unreleased]\n\n{new_header}{body}{tail}"
    sdlc_md.atomic_write(clog, out)
    return new_header


def record_green(root: Path | str, commit: str) -> Path:
    """Stamp the commit the pre-tag gate passed on."""
    p = _green_path(Path(root))
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"commit": (commit or "").strip()}) + "\n", encoding="utf-8")
    return p


def green_commit(root: Path | str) -> str | None:
    """The commit the gate was last recorded green on, or None."""
    p = _green_path(Path(root))
    if not p.is_file():
        return None
    try:
        return (json.loads(p.read_text(encoding="utf-8")).get("commit") or "").strip() or None
    except (OSError, ValueError):
        return None


#: Conclusions that are not a failure. `skipped` and `neutral` are how a workflow says "this run
#: did not apply", which is not the same as "this run went wrong" - refusing them would make a
#: path-filtered workflow un-taggable. Anything else, including an empty conclusion, blocks.
CI_OK_CONCLUSIONS = frozenset({"success", "skipped", "neutral"})

#: A hung `gh` (proxy, auth prompt) must fail rather than block the release forever.
GH_TIMEOUT = 120


def _has_forge_remote(root: Path | str) -> bool:
    """Whether this clone has any git remote at all - the one honest reason there is no forge
    answer to ask for."""
    try:
        proc = subprocess.run(["git", "remote"], capture_output=True, text=True,
                              cwd=str(root), timeout=30)
    except (OSError, subprocess.SubprocessError):
        return False
    return proc.returncode == 0 and bool(proc.stdout.strip())


def _full_sha(root: Path | str, commit: str) -> str:
    """`gh run list --commit` matches on the FULL sha and silently returns nothing for an
    abbreviated one - which this guard would read as "the forge has never run this commit" and
    refuse. A false refusal on a green tree trains the bypass just as surely as a false pass
    trains the tag, so resolve first and only then ask. An unresolvable ref is passed through
    unchanged: that is the forge's question to answer, not this helper's."""
    try:
        proc = subprocess.run(["git", "rev-parse", f"{commit}^{{commit}}"],
                              capture_output=True, text=True, cwd=str(root), timeout=30)
    except (OSError, subprocess.SubprocessError):
        return commit
    out = (proc.stdout or "").strip()
    return out if proc.returncode == 0 and out else commit


def forge_ci_state(root: Path | str, commit: str) -> tuple[str, str]:
    """`(state, detail)` - what the FORGE says about CI on `commit`, never what a local file says.

    States: `success`, `failed`, `pending`, `none`, `no-forge`, `unknown`. Only `success` and
    `no-forge` may pass a tag.

    The distinctions are the whole point, because collapsing any two of them is how both v5 tags
    were cut over a red CI:

    * `none` - the forge has no run for this commit. Either it was never pushed, or the workflow
      never fired. "Nobody has judged this tree" is not a green, and reading it as one is the
      original defect one step removed.
    * `pending` - a run exists and has not finished. A tag cut now asserts an outcome that has
      not happened yet.
    * `unknown` - `gh` is absent, unauthenticated, timed out, or answered something unparseable.
      "I could not look" must never be reported as "there is nothing wrong"; that is exactly the
      rule `release_assets.published` states for the same question about the same forge.
    * `no-forge` - there is no remote, so there is no CI to ask about and the rule was never
      adopted in this clone. The single honest pass, and distinguished from `unknown` precisely
      so that a missing `gh` cannot borrow it.
    """
    commit = (commit or "").strip()
    if not _has_forge_remote(root):
        return "no-forge", ("no git remote is configured, so there is no forge CI to ask about - "
                            "the tag is judged on the local gate alone")
    if shutil.which("gh") is None:
        return "unknown", ("gh is not on PATH, so whether CI passed on the pushed commit is "
                           "UNKNOWN - install https://cli.github.com/ and authenticate")
    commit = _full_sha(root, commit)
    try:
        proc = subprocess.run(
            ["gh", "run", "list", "--commit", commit, "--limit", "50",
             "--json", "conclusion,status,workflowName"],
            capture_output=True, text=True, cwd=str(root), timeout=GH_TIMEOUT)
    except (OSError, subprocess.SubprocessError) as exc:
        return "unknown", f"the forge could not be asked about {commit} ({exc!r})"
    if proc.returncode != 0:
        return "unknown", (f"gh could not report CI for {commit}: "
                           f"{(proc.stderr or '').strip() or f'exit {proc.returncode}'}")
    try:
        runs = json.loads(proc.stdout or "[]")
    except ValueError:
        return "unknown", f"gh answered something that is not JSON when asked about {commit}"
    if not isinstance(runs, list) or not runs:
        return "none", (f"the forge has no CI run for {commit} - either it has not been pushed, "
                        f"or no workflow fired on it")
    unfinished = [r for r in runs if (r.get("status") or "") != "completed"]
    if unfinished:
        names = ", ".join(sorted({str(r.get("workflowName") or "?") for r in unfinished})[:5])
        return "pending", f"CI on {commit} has not finished ({names})"
    bad = [r for r in runs if (r.get("conclusion") or "") not in CI_OK_CONCLUSIONS]
    if bad:
        names = ", ".join(sorted({f"{r.get('workflowName') or '?'}: "
                                  f"{r.get('conclusion') or 'no conclusion'}" for r in bad})[:5])
        return "failed", f"CI on {commit} did not pass ({names})"
    if not any((r.get("conclusion") or "") == "success" for r in runs):
        return "none", (f"every CI run on {commit} was skipped or neutral, so nothing actually "
                        f"judged this tree")
    return "success", f"CI passed on {commit} on the forge"


def tag_check(root: Path | str, commit: str) -> tuple[bool, str]:
    """(allowed, reason). A tag of `commit` is allowed ONLY when the recorded gate-green commit is
    the same commit - so a tag can never assert a green measured on a different tree."""
    commit = (commit or "").strip()
    green = green_commit(root)
    if not green:
        return False, ("no release gate has been recorded green - run the pre-tag gate and "
                       "`release_cut.py record-green --commit <sha>` on the same commit first")
    if green != commit:
        return False, (f"the gate was recorded green on {green}, not the commit being tagged "
                       f"({commit}) - a tag asserting a green measured on a different tree is "
                       f"refused; re-run the gate on {commit}")
    # No delivery unit may owe a close at a TAG. The specs documented this as enforced "at the
    # push/release moment" and it ran at neither: the gate lane bound only when a flag nobody
    # passed was given, no pre-push hook exists and CI ran the plain gate - a ceremony with no
    # detector, which is the exact failure the lane was built to close. The tag is where the
    # rule is unambiguously right; blocking every mid-sprint push on a trunk-based repo would
    # train the bypass instead.
    owed, unknown = _close_owed_units(root)
    if unknown:
        return False, f"refusing the tag: {unknown}"
    if owed:
        return False, (f"{len(owed)} delivery unit(s) reached a terminal status with no retro "
                       f"behind them ({', '.join(owed[:8])}"
                       f"{', +more' if len(owed) > 8 else ''}) - a release that ships work no "
                       f"sprint closed asserts a record that was never written. Close the "
                       f"sprint, or record the deferral deliberately")
    # Everything above this line is a claim about the LOCAL tree, answered from a local file. That
    # was the whole guard until BG0576, and it is why v5.0.0 and v5.0.1 were both tagged over a CI
    # that had been red for two days: the gate ran green on a developer machine, the runner
    # disagreed, and nothing in the release chain ever asked it. Whether CI passed on the pushed
    # commit is a claim about the remote, and only the remote can answer it.
    state, detail = forge_ci_state(root, commit)
    if state not in ("success", "no-forge"):
        return False, (f"refusing the tag: {detail}. A tag asserts that this tree passed, and "
                       f"the only place that can be answered for a pushed commit is the forge - "
                       f"a local green says nothing about the runner")
    forge_note = "no forge to ask" if state == "no-forge" else "CI green on the forge"
    return True, (f"gate green on {commit} matches the tagged commit, no close is owed, "
                  f"and {forge_note}")


def _close_owed_units(root: Path | str) -> "tuple[list[str], str | None]":
    """`(units owing a close, refusal reason)` - and it FAILS CLOSED.

    The original version returned `[]` on every failure, justified as "a crash in a reporting
    helper must not become a refusal nobody can clear" and as being "a second, narrower net"
    behind a blocking gate lane. Both halves were wrong. There is no gate lane above: the
    `close-owed` lane binds only under `--require-close`, which nothing passes, so this IS the
    only enforcement point. And `[]` collapsed three different states into "clean":

    * no baseline stamped - genuinely nothing to judge, the one case that may pass;
    * baseline UNREADABLE - `gate._close_owed` treats this as a loud blocking refusal, in terms
      ("refusing to pass a close gate over an unreadable baseline that silently disarms the
      close-down"), and here it read as clean;
    * the helper raised - nothing was judged, reported as though everything had been.

    So deleting or truncating one tracked file (`sdlc-studio/.close-owed-baseline.json`) turned
    the release guard off and made the tag assert a positive falsehood. A guard whose failure
    mode is silence is the class this project files bugs about; this one is the guard on the
    release."""
    try:
        import close_owed  # noqa: PLC0415 - deferred; only the tag path pays for it
        report = close_owed.owed(Path(root))
    except Exception as exc:  # noqa: BLE001 - reported, never swallowed
        return [], (f"the close-owed report could not be produced ({exc!r}), so whether any "
                    f"delivery unit owes a close is UNKNOWN - refusing rather than tagging on "
                    f"an unanswered question")
    if report.get("corrupt"):
        return [], ("the close-owed baseline is unreadable, which silently disarms the "
                    "close-down check - restore `sdlc-studio/.close-owed-baseline.json` from "
                    "git; do NOT re-stamp it, which would forgive whatever it was hiding")
    # The scan itself degraded. `read_text_safe` and `walk_glob` swallow by design - one bad
    # artefact must not abort a walk over a thousand - and that silence reached here as an EMPTY
    # tree, which reads identically to a clean one. `chmod 000 sdlc-studio/stories` turned a
    # correct refusal into "no close is owed": the same fail-open this function was rewritten to
    # close, one frame down the stack, because the fix caught only what `owed()` RAISED.
    unreadable = report.get("unreadable") or []
    if unreadable:
        shown = ", ".join(str(d.get("path")) for d in unreadable[:5])
        return [], (f"{len(unreadable)} path(s) in the delivery tree could not be read "
                    f"({shown}{', +more' if len(unreadable) > 5 else ''}), so whether any unit "
                    f"owes a close is UNKNOWN - an unreadable tree is indistinguishable from an "
                    f"empty one, and tagging on it would assert a clean record nobody scanned")
    # No baseline is the one honest pass: the rule was never adopted here, so there is no
    # history to hold this project to. Distinguished from unreadable, which is the whole point.
    if not report.get("baselined"):
        return [], None
    return [str(row[0]) for row in (report.get("owed") or [])], None


def _cmd_cut(args: argparse.Namespace) -> int:
    try:
        header = cut_changelog(args.root, args.version)
    except (ValueError, OSError) as exc:
        print(f"changelog-cut refused: {exc}", file=sys.stderr)
        return 2
    print(f"cut {header} from the fragments; [Unreleased] emptied")
    return 0


def _cmd_record_green(args: argparse.Namespace) -> int:
    record_green(args.root, args.commit)
    print(f"recorded release gate green on {args.commit}")
    return 0


def _cmd_tag_check(args: argparse.Namespace) -> int:
    allowed, reason = tag_check(args.root, args.commit)
    print(reason, file=sys.stderr if not allowed else sys.stdout)
    return 0 if allowed else 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio release cut and tag guard.")
    sdlc_md.add_global_root(parser)
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("changelog-cut", help="compose fragments and cut a versioned section")
    c.add_argument("--version", required=True, help="the release version, e.g. 5.0.0")
    c.set_defaults(func=_cmd_cut)
    r = sub.add_parser("record-green", help="stamp the commit the pre-tag gate passed on")
    r.add_argument("--commit", required=True)
    r.set_defaults(func=_cmd_record_green)
    t = sub.add_parser("tag-check", help="refuse a tag unless the gate was green on that commit")
    t.add_argument("--commit", required=True)
    t.set_defaults(func=_cmd_tag_check)
    for p in (c, r, t):
        # SUPPRESS (not ".") so a global `--root X <verb>` set before the subcommand is not
        # clobbered by the subparser's own default - the family root-placement contract.
        p.add_argument("--root", default=argparse.SUPPRESS, help="Repo root (default: .)")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Anchor the root ONCE before dispatch, so a run from a subdirectory acts on the project it
    # belongs to and a subcommand --root cannot clobber the global value (the family contract).
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
