#!/usr/bin/env python3
"""SDLC Studio plan-review gate (schema v3 only - dormant under schema_version: 2).

US0090/CR0194. The N=5 benchmark measured a "bad plan propagates" failure: a planner
mis-pinned a spec rule in a story's ACs and the delivery critic - whose oracle IS the ACs -
approved a faithful build of the wrong plan. No step independently checked the ACs against
the source spec before implementation.

This adds that step as a DETERMINISTIC gate. Before a story with spec-derived ACs is
implemented, an independent reviewer (a separate instance from the plan's author) must
record a plan-review verdict. The trigger fires by rule, never by model judgement (TRD
ADR-006): the same benchmark's headline is that judgement-scaled hygiene is skipped 10/10
under effort pressure, so a review the model may decline is that failure at one remove.

Three checkable signals trip the gate (OR): the story's Affects or ACs cite a configured
spec path, `affects_files` reaches `plan_review.affects_files_threshold`, or the routed
difficulty band reaches `plan_review.min_difficulty`. A skip is possible only through a
recorded operator override (a `> **Plan-Review-Override:**` field, ledger-visible), never
a silent pass. Verdicts live in their own log (`critic.py --phase plan-review`), so a
plan-review APPROVE never satisfies the delivery critique gate and vice versa.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import config  # noqa: E402
import critic  # noqa: E402
import route  # noqa: E402
import telemetry  # noqa: E402

_DEFAULT_SPEC_GLOBS = ["*prd*.md", "*trd*.md", "*tsd*.md", "*requirements*",
                       "*spec*.md", "specs/*", "spec/*", "requirements/*"]
# A path token WITH an extension (docs/prd.md) OR an extension-less token under a directory
# (requirements/r5, specs/design) - the latter matters because spec sections are often
# referenced without a file extension; missing them would under-fire the gate (the dangerous
# direction). Prose without a path never matches - the signal is a document reference.
_PATH_RE = re.compile(r"[\w.-]+/[\w./-]+|[\w./-]+\.[A-Za-z0-9]+")
_AC_RE = re.compile(r"##\s+Acceptance Criteria\b(.*?)(?=\n##\s|\Z)", re.S | re.I)
# Same-line capture: `sdlc_md.extract_field`'s leading \s* crosses newlines, so an EMPTY
# override field would phantom-match the next line as its value (the EP0014 lesson). Bind
# the value to the field's own line so a blank override is None, not the following line.
_OVERRIDE_RE = re.compile(r"^>?[^\S\n]*\*\*Plan-Review-Override:\*\*[^\S\n]*(.*)$", re.M)


def _cfg(root, key: str, default):
    try:
        return config.get(root, f"plan_review.{key}", default)
    except Exception:  # noqa: BLE001 - config must never break the gate
        return default


def spec_globs(root) -> list[str]:
    raw = _cfg(root, "spec_globs", _DEFAULT_SPEC_GLOBS)
    return [str(g) for g in raw] if isinstance(raw, list) and raw else list(_DEFAULT_SPEC_GLOBS)


def affects_files_threshold(root) -> int:
    try:
        return int(_cfg(root, "affects_files_threshold", 5))
    except (TypeError, ValueError):
        return 5


def min_difficulty(root) -> str:
    return str(_cfg(root, "min_difficulty", "medium")).strip().lower()


def _band_rank(band: str | None) -> int:
    try:
        return route.BANDS.index((band or "").strip().lower())
    except ValueError:
        return -1


def _matches_spec(token: str, globs: list[str]) -> bool:
    tok = token.strip().lower()
    base = tok.rsplit("/", 1)[-1]
    return any(fnmatch.fnmatch(tok, g.lower()) or fnmatch.fnmatch(base, g.lower())
               for g in globs)


def cites_spec(text: str, root) -> bool:
    """True when the story's Affects or any path-like token in its body matches a spec glob.
    Prose alone never matches - only path tokens (with an extension) and Affects entries -
    so the signal is about referencing a spec DOCUMENT, not saying the word 'spec'."""
    globs = spec_globs(root)
    candidates = set(sdlc_md.affects_files(text)) | set(_PATH_RE.findall(text))
    return any(_matches_spec(c, globs) for c in candidates)


def _difficulty_band(root, text: str, path: Path | None = None) -> str | None:
    """The routed difficulty band for the unit, computed deterministically (route.estimate).
    When no on-disk path is given, the text is estimated via a temp file - route.estimate
    resolves Affects against `root`, not the unit's location, so the band is identical."""
    try:
        if path is not None:
            return route.estimate(root, path)["difficulty_band"]
        with tempfile.TemporaryDirectory() as d:
            tmp = Path(d) / "unit.md"
            tmp.write_text(text, encoding="utf-8")
            return route.estimate(root, tmp)["difficulty_band"]
    except Exception:  # noqa: BLE001 - a difficulty read must never break the gate
        return None


def triggers(text: str, root, path: Path | None = None) -> dict:
    """Deterministically evaluate the three signals. Pure read; no model judgement, no
    side effects. `fired` is the OR of the signals."""
    threshold = affects_files_threshold(root)
    affects = sdlc_md.affects_files(text)
    spec = cites_spec(text, root)
    affects_over = len(affects) >= threshold
    band = _difficulty_band(root, text, path)
    diff_over = band is not None and _band_rank(band) >= _band_rank(min_difficulty(root))
    signals: list[str] = []
    if spec:
        signals.append("spec-citation")
    if affects_over:
        signals.append(f"affects>={threshold}")
    if diff_over:
        signals.append(f"difficulty>={min_difficulty(root)}")
    return {
        "spec_citation": spec, "affects_count": len(affects), "affects_over": affects_over,
        "difficulty_band": band, "difficulty_over": diff_over,
        "signals": signals, "fired": bool(signals),
    }


def override(text: str) -> str | None:
    """The operator-override value (`> **Plan-Review-Override:**`), or None when absent or
    blank. Ledger-visible because it lives in the story file itself. Same-line capture so a
    blank field is never a phantom match of the next line; the empty-cell sentinel `-` (used
    everywhere else in the codebase for "no value") is not a real override."""
    m = _OVERRIDE_RE.search(text)
    if not m:
        return None
    val = m.group(1).strip()
    return val if val and val != "-" else None


def ac_fingerprint(text: str) -> str:
    """A stable 12-hex digest of the story's Acceptance Criteria section (whitespace- and
    case-normalised). Pins a plan-review verdict to the exact ACs that were reviewed, so an
    edit to the ACs after approval invalidates the verdict (the mis-pinned-AC attack CR0194
    targets - approve a benign plan, then invert a rule, must NOT ride the stale approval)."""
    m = _AC_RE.search(text)
    body = m.group(1) if m else text
    norm = re.sub(r"\s+", " ", body).strip().lower()
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]


_HASH_RE = re.compile(r"ac-hash=([0-9a-f]{12})")


def record_review(root, story_id: str, verdict: str, reviewer: str, author: str,
                  notes: str = "") -> Path:
    """Record a plan-review verdict that PINS the reviewed ACs by fingerprint, so the gate
    can detect a post-approval AC edit. The sprint loop records plan-review verdicts through
    here; the fingerprint is stamped into the verdict's issues field."""
    root = Path(root)
    p = _resolve_story(root, story_id)
    if p is None or not p.exists():
        # Fail loud: a null fingerprint (the old behaviour) recorded an approval that could
        # never match the story's real ACs - an unclearable false block discovered later.
        raise FileNotFoundError(
            f"cannot record a plan review for {story_id}: story not found - "
            "check the id (lowercase filenames and aliases resolve; typos do not)")
    fp = ac_fingerprint(p.read_text(encoding="utf-8"))
    issues = f"ac-hash={fp}" + (f"; {notes}" if notes else "")
    path = critic.record_verdict(root, story_id, verdict, reviewer, author, issues,
                                 phase="plan-review")
    telemetry.record_plan_review(root, story_id, verdict, reviewer, author)
    return path


def _has_independent_plan_approval(root, story_id: str, text: str) -> bool:
    """An independent plan-review APPROVE is on record. When the verdict pins an AC
    fingerprint (recorded via `record_review`), it must match the story's CURRENT ACs - a
    stale approval against edited ACs does not count. A hash-less verdict (the bare
    `critic record --phase plan-review` form) is honoured for back-compatibility."""
    # THE `spec` KIND, named rather than assumed. This gate is the US0090 pre-implementation
    # AC-vs-spec check, and it must not be discharged by an approval of some other pre-code
    # artefact - a test-plan review, say - that its reviewer never read. Naming the kind is what
    # makes the column load-bearing instead of decorative, which is the state `critic brief
    # --tier` was already in.
    v = critic.verdict_for(root, story_id, phase="plan-review", kind=critic.DEFAULT_PLAN_KIND)
    if not (v and v["verdict"] == critic.APPROVE and critic.is_independent(v)):
        return False
    m = _HASH_RE.search(v.get("issues", "") or "")
    return m.group(1) == ac_fingerprint(text) if m else True


def active(root) -> bool:
    """Is the plan-review gate live for this project?

    `plan_review.enabled` when stated, the schema version otherwise - THE shared resolution in
    `config.feature_enabled`, the same one `triage_noise.active` uses.

    This gate was hard-gated on `is_schema_v3` with no knob at all, which made it unreachable
    without adopting the v3 id format, the inbox status and spec-guard across every artefact a
    project holds. It is a review policy and has nothing to do with the shape of artefacts, and
    it is the model the rest of the ceremony work copies - a deterministic, risk-proportional
    gate that `--force` cannot bypass - so leaving it dormant left the model unexercised.
    """
    return config.feature_enabled(root, "plan_review")


#: Where a project's closed sprints are recorded. A retro is COMMITTED and travels with the
#: repository, which is the whole reason it is the source here.
_RETRO_REL = Path("sdlc-studio") / "retros"


def has_run_history(root) -> bool:
    """Whether this project has ever closed a sprint.

    Read from the COMMITTED retros, never from `sdlc-studio/.local/`. The obvious source is the
    run archive, and it is the wrong one: `.local/` is gitignored and documented as state you can
    delete and lose nothing, so a fresh clone, a CI checkout or a cleaned working directory would
    report an established project as brand new - and any concession granted to a new project would
    come back every time, for ever. A retro is written per closed run and is committed, so a clone
    answers this the same way the machine that did the work does.

    FAILS TOWARDS HISTORY. Anything unreadable, absent or ambiguous answers True. The direction
    this must not fail in is a long-lived project being silently treated as new, because that is
    the direction in which a gate quietly stops applying; erring the other way merely asks a new
    project for one more thing, which it can see and act on.
    """
    d = Path(root) / _RETRO_REL
    try:
        if not d.is_dir():
            return False
        return any(f.suffix == ".md" and f.stem.upper().startswith("RETRO")
                   for f in d.iterdir())
    except OSError:
        return True  # unreadable is not the same as absent, and only one of them is safe


def gate(root, story_id: str, path: Path | str | None = None) -> dict:
    """Evaluate the plan-review gate for a story. Returns {ok, reason, fired, override,
    signals}. A no-op (ok True) unless `active(root)` - see there for what decides it."""
    root = Path(root)
    if not active(root):
        # The reason names the KNOB when a project stated one, and the schema version otherwise,
        # because a reader has to be sent to the thing that actually decided. Reporting "schema
        # v2" to a project that deliberately set `plan_review.enabled: false` would send them to
        # a migration they do not need for a decision they already made.
        stated = config.get(root, "plan_review.enabled", None)
        why = ("dormant (plan_review.enabled: false)" if stated is not None
               else "dormant (schema v2)")
        return {"ok": True, "reason": why, "fired": False,
                "override": None, "signals": []}
    p = Path(path) if path else _resolve_story(root, story_id)
    if p is None or not p.exists():
        # Fail closed and loud: a skipped gate over a typo'd id is the vacuous-PASS class.
        return {"ok": False, "reason": (f"story {story_id} not found - the gate cannot "
                                        "evaluate what it cannot resolve (fix the id/path)"),
                "fired": False, "override": None, "signals": []}
    text = p.read_text(encoding="utf-8")
    trig = triggers(text, root, p)
    if not trig["fired"]:
        return {"ok": True, "reason": "plan-review trigger not tripped", "fired": False,
                "override": None, "signals": []}
    ov = override(text)
    if ov:
        return {"ok": True, "reason": f"operator override recorded: {ov}", "fired": True,
                "override": ov, "signals": trig["signals"]}
    if _has_independent_plan_approval(root, story_id, text):
        return {"ok": True, "reason": "independent plan-review APPROVE on record",
                "fired": True, "override": None, "signals": trig["signals"]}
    if not has_run_history(root):
        # A project that has never closed a sprint has never had the chance to meet this gate,
        # and meeting it is the first thing it would be asked to do. Report, do not refuse - the
        # concession expires the moment the first retro exists, so nothing has to switch it back
        # on and no setting can hold it open.
        return {"ok": True, "fired": True, "override": None, "signals": trig["signals"],
                "reason": ("plan-review REPORTED, not required: this project has closed no "
                           "sprint yet, so the gate arms once its first retro exists under "
                           "sdlc-studio/retros/. Trigger: " + ", ".join(trig["signals"]) +
                           ". From the next run this is a refusal, cleared by an independent "
                           "plan-review APPROVE or a `> **Plan-Review-Override:**`")}
    return {"ok": False, "fired": True, "override": None, "signals": trig["signals"],
            "reason": ("plan-review required (trigger: " + ", ".join(trig["signals"]) +
                       ") - record an independent plan-review APPROVE (reviewer != plan "
                       "author) with `critic.py record --phase plan-review`, or a "
                       "`> **Plan-Review-Override:**` on the story")}


def _resolve_story(root: Path, story_id: str) -> Path | None:
    """Delegate to the shared, alias-aware lookup (case-insensitive by construction) - the
    case-sensitive `US*.md` glob this replaced missed lowercase-named stories entirely."""
    hit = sdlc_md.find_by_id(root, story_id)
    return hit[0] if hit and hit[1] == "story" else None


def cmd_check(args: argparse.Namespace) -> int:
    res = gate(args.root, args.id, args.path)
    if getattr(args, "format", "text") == "json":
        print(json.dumps(res, indent=2))
        return 0 if res["ok"] else 1
    print(("OK: " if res["ok"] else "BLOCKED: ") + res["reason"])
    return 0 if res["ok"] else 1  # check-failure: the family returns 1, not 2 (argparse owns 2)


def cmd_record(args: argparse.Namespace) -> int:
    independent, why = critic.independence(args.reviewer, args.author)
    if not independent:
        print(f"WARNING: {why} - this never clears the gate", file=sys.stderr)
    path = record_review(args.root, args.id, args.verdict, args.reviewer, args.author,
                         args.notes)
    print(f"recorded plan-review {args.verdict.upper()} for {args.id} "
          f"(AC-pinned) -> {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="SDLC Studio plan-review gate (schema v3).")
    sub = p.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Evaluate the plan-review gate for a story.")
    c.add_argument("--id", required=True, help="Story id, e.g. US0090")
    c.add_argument("--path", default=None, help="Story file (optional; resolved from --id)")
    c.add_argument("--root", default=".")
    sdlc_md.add_format_arg(c)
    c.set_defaults(func=cmd_check)
    r = sub.add_parser("record", help="Record a plan-review verdict, PINNED to the story's "
                                      "current ACs (a later AC edit invalidates it).")
    r.add_argument("--id", required=True, help="Story id, e.g. US0090")
    r.add_argument("--verdict", required=True,
                   choices=("approve", "reject", "APPROVE", "REJECT"))
    r.add_argument("--reviewer", required=True, help="Reviewing seat (must differ from author)")
    r.add_argument("--author", required=True, help="Plan author (the seat that wrote the ACs)")
    r.add_argument("--notes", default="", help="Optional free-text notes")
    r.add_argument("--root", default=".")
    r.set_defaults(func=cmd_record)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to. The family default `.` means "work it out from here", not "the cwd
    # is the project": otherwise a run from a subdirectory acts on a stray tree and exits 0.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
