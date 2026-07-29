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
    return True, f"gate green on {commit} matches the tagged commit, and no close is owed"


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
