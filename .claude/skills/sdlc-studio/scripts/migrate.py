#!/usr/bin/env python3
"""migrate - one command that reviews every artefact and upgrades where it safely can.

`project upgrade` refreshes conventions and the version; `migrate_v3 sizing` converts a
container's legacy Effort/Points to a T-shirt Size; `reconcile` finds an accepted item that was
never decomposed. Each is sound on its own, but an operator upgrading a project had to know to run
all three and read three reports. `migrate` is the ORCHESTRATOR: it runs the
existing pieces in order, adds the artefact-review sweep, and emits ONE report split into what it
upgraded DETERMINISTICALLY and what NEEDS A HUMAN.

The honesty rule (the estimator finding): it auto-applies only the deterministic, reversible set -
the version stamp, the config scaffold, a container's sizing conversion. It never GUESSES a
judgement: a request's breakdown (`refine`), an Issue's triage (`triage`), a delivery unit's
re-size (there is no honest Effort->Points map) are REPORTED with the exact command, never done for
you. Dry-run by default; `--apply` writes only the deterministic set.

Skill/consuming-project tool: it operates on the `sdlc-studio/` workspace under the root. Reuses
`project_upgrade`, `migrate_v3` and `reconcile`; pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import project_upgrade  # noqa: E402
import migrate_v3  # noqa: E402

# Each needs-human bucket, its human label, and how to render the command that resolves it. The
# artefact-review sweep (US0155): every open item that cannot be upgraded deterministically is named
# here with the CEREMONY that turns it into current-shape work - never guessed.
_HUMAN = {
    "needs_refine": ("a request accepted but never decomposed",
                     lambda x: f"refine apply --request {x['id']} --epic-title \"...\" --story \"title|points\" ..."),
    "needs_triage": ("an Issue accepted but never triaged",
                     lambda x: f"triage apply --issue {x['id']} --bug \"title|points|severity\" ..."),
    "needs_resize": ("a delivery unit sized in legacy Effort (no honest Effort->Points map)",
                     lambda x: f"re-size {x['id']}: set its `Points` on the Fibonacci scale by judgement"),
    "needs_manual": ("convertible but malformed (no Status line to anchor a Size)",
                     lambda x: f"fix {x['id']}'s metadata (add a `> **Status:**` line), then re-run"),
}
_HUMAN_ORDER = ("needs_refine", "needs_triage", "needs_resize", "needs_manual")


def migrate(repo_root: Path | str, *, apply: bool = False, with_default_amigos: bool = False,
            today: str | None = None) -> dict:
    """Run the upgrade sweep. Returns
    `{applicable, applied, deterministic: [...], needs_human: [...], summary}`. `deterministic`
    lists what was (or would be) auto-applied - conventions/version from `project_upgrade` and
    sizing conversions from `migrate_v3`. `needs_human` lists every item that needs judgement, each
    with the exact command. `apply` performs only the deterministic set."""
    root = Path(repo_root)
    if not (root / "sdlc-studio").is_dir():
        return {"applicable": False, "applied": apply, "deterministic": [], "needs_human": [],
                "summary": {}}

    # 1. conventions + version. Classify from `audit()` in BOTH modes - never from `apply()`'s
    # free-text action strings, which mix real changes with advisories and warnings (the team-offer
    # nudge, the BG0150 "version NOT stamped" warning, "SKIPPED" notes). Reporting an advisory as an
    # applied deterministic upgrade breaks the honest split this command exists for; using the one
    # `audit` classification keeps dry-run and apply agreeing on what is deterministic vs needs-human.
    # `audit` is honest about BG0150 (an unreadable install version -> a `manual` item, not `auto`),
    # so `auto` is a faithful preview of what apply will write.
    au = project_upgrade.audit(root)
    if apply:
        project_upgrade.apply(root, with_reconcile=False, today=today,
                              with_default_amigos=with_default_amigos)

    # 2. ids/sizing. Converts a container's legacy Effort/Points to a Size deterministically, and
    # reports the delivery units and undecomposed requests/issues it cannot convert safely.
    sizing = migrate_v3.migrate_sizing(root, dry_run=not apply)

    # 3. aggregate into one report. Deterministic = the conventions auto-fixes + the sizing
    # conversions; `applied` reflects the mode, and the classification is identical either way.
    deterministic: list[dict] = []
    for a in au["auto"]:
        deterministic.append({"source": "conventions", "kind": a["kind"],
                              "detail": a["detail"], "applied": apply})
    converted_ids = set()
    for c in sizing["converted"]:
        converted_ids.add(c["id"])
        deterministic.append({"source": "sizing", "id": c["id"],
                              "detail": f"{c['id']}: Size {c['size']} (from {c['from']})",
                              "applied": apply})

    needs_human: list[dict] = []
    for m in au["manual"]:                       # conventions that need judgement (index drift, etc.)
        needs_human.append({"kind": m["kind"], "detail": m["detail"], "command": None})
    for bucket in _HUMAN_ORDER:                  # the artefact-review sweep, per ceremony
        label, cmd = _HUMAN[bucket]
        for item in sizing.get(bucket, []):
            # a container can be size-converted (deterministic) AND still need refining - two
            # orthogonal facts about one id. Note the overlap so the report does not read as "you
            # fixed it / you must fix it" about the same artefact.
            also = " (its Size was converted above; this is the separate decomposition)" \
                if item["id"] in converted_ids else ""
            needs_human.append({"kind": bucket.replace("_", "-"), "id": item["id"],
                                "detail": f"{item['id']} ({item['type']}): {label}{also}",
                                "command": cmd(item)})

    return {"applicable": True, "applied": apply, "deterministic": deterministic,
            "needs_human": needs_human,
            "summary": {"deterministic": len(deterministic), "needs_human": len(needs_human),
                        "applied": apply}}


def render(result: dict) -> str:
    if not result["applicable"]:
        return "migrate: no sdlc-studio/ under this root - not an sdlc-studio project."
    verb = "applied" if result["applied"] else "would apply"
    out = [f"migrate: {result['summary']['deterministic']} deterministic upgrade(s) {verb}, "
           f"{result['summary']['needs_human']} need(s) a human.", ""]
    if result["deterministic"]:
        out.append(f"## Deterministic ({verb})")
        for d in result["deterministic"]:
            out.append(f"  - [{d['source']}] {d['detail']}")
        out.append("")
    if result["needs_human"]:
        out.append("## Needs a human (reported, never guessed)")
        for h in result["needs_human"]:
            out.append(f"  - {h['detail']}")
            if h.get("command"):
                out.append(f"      -> {h['command']}")
        out.append("")
    if not result["applied"] and result["deterministic"]:
        out.append("Re-run with --apply to write the deterministic set (the needs-human items are "
                   "never auto-applied).")
    return "\n".join(out).rstrip("\n") + "\n"


def cmd_run(args: argparse.Namespace) -> int:
    result = migrate(args.root, apply=args.apply, with_default_amigos=args.with_default_amigos)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(render(result), end="")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="migrate", description=__doc__)
    p.add_argument("--root", default=".", help="repo root")
    p.add_argument("--apply", action="store_true",
                   help="write the deterministic set (conventions, version, sizing conversions); "
                        "the needs-human items are always only reported")
    p.add_argument("--with-default-amigos", dest="with_default_amigos", action="store_true",
                   help="install the shipped default amigo cards for roles no seat covers "
                        "(passed through to project upgrade)")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_run)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
