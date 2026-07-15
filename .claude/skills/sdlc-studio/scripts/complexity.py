#!/usr/bin/env python3
"""SDLC Studio code-complexity signals.

Computes cognitive complexity (SonarSource / Campbell 2018) and cyclomatic
complexity per function from Python's `ast`, with no third-party dependency. Non-
Python files are scored via `lizard` (a pure-Python multi-language cyclomatic tool)
when it is importable, and reported unscored otherwise - the same soft-dep pattern
as `gh` and the test runners. The signal is advisory: it feeds estimation and a
refactor-first recommendation, never a gate.

Cognitive complexity (the metric this leans on) scores understandability:
+1 for each break in linear flow (if/elif/else, for/while, except, ternary, each
boolean-operator sequence, match), and an extra +1 per nesting level for flow-breakers
nested inside others - the part cyclomatic complexity ignores. Python's parser already
groups a run of one boolean operator (`a and b and c`) into a single node, so each
operator *alternation* is naturally one increment.

Read-only; pure stdlib core.
"""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

DEFAULT_COGNITIVE_HIGH = 15  # SonarQube's "high" threshold; configurable
DEFAULT_CHURN_HIGH = 12      # commits-touching-a-file "high" threshold (calibrated)
# Churn is weighted ~3x complexity in the composite: the 2026-06-21 calibration against
# consuming repo B/consuming repo A found churn discriminates defects ~4.9x vs complexity's ~1.8x.
W_CHURN, W_COGNITIVE = 3, 1
CODE_SUFFIXES = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".rb", ".c",
                 ".cc", ".cpp", ".cs", ".rs", ".php", ".swift", ".kt"}
IGNORE_DIRS = {".git", "__pycache__", "node_modules", ".local", ".venv", "venv",
               "dist", "build", ".mypy_cache", ".pytest_cache"}

_NEST = (ast.If, ast.For, ast.AsyncFor, ast.While)


# --- cognitive complexity -------------------------------------------------

def cognitive_complexity(func: ast.AST) -> int:
    """Cognitive complexity of a function node (its own body; nested defs are
    scored separately, not folded into the parent)."""
    return _cc_seq(getattr(func, "body", []), 0)


def _cc_seq(body, nesting: int) -> int:
    return sum(_cc_stmt(n, nesting) for n in body)


def _cc_stmt(node: ast.AST, nesting: int) -> int:
    if isinstance(node, ast.If):
        t = 1 + nesting + _cc_expr(node.test, nesting) + _cc_seq(node.body, nesting + 1)
        orelse = node.orelse
        # An `elif` is +1 with NO nesting growth; a real `else:` block that happens to
        # contain a single `if` is NOT an elif and DOES nest. The two are
        # AST-distinguishable: an elif's inner `If` shares the outer's column offset,
        # whereas an else-nested `if` is indented one level deeper.
        while (len(orelse) == 1 and isinstance(orelse[0], ast.If)
               and orelse[0].col_offset == node.col_offset):
            e = orelse[0]
            t += 1 + _cc_expr(e.test, nesting) + _cc_seq(e.body, nesting + 1)
            orelse = e.orelse
        if orelse:  # plain else: +1, no nesting, body one level deeper
            t += 1 + _cc_seq(orelse, nesting + 1)
        return t
    if isinstance(node, (ast.For, ast.AsyncFor)):
        t = 1 + nesting + _cc_expr(node.iter, nesting) + _cc_seq(node.body, nesting + 1)
        if node.orelse:
            t += 1 + _cc_seq(node.orelse, nesting + 1)
        return t
    if isinstance(node, ast.While):
        t = 1 + nesting + _cc_expr(node.test, nesting) + _cc_seq(node.body, nesting + 1)
        if node.orelse:
            t += 1 + _cc_seq(node.orelse, nesting + 1)
        return t
    if isinstance(node, ast.Try):
        t = _cc_seq(node.body, nesting)
        for h in node.handlers:
            t += 1 + nesting + _cc_seq(h.body, nesting + 1)
        return t + _cc_seq(node.orelse, nesting) + _cc_seq(node.finalbody, nesting)
    if isinstance(node, getattr(ast, "Match", ())):  # match: +1 for the whole construct
        t = 1 + nesting + _cc_expr(node.subject, nesting)
        for case in node.cases:
            if case.guard is not None:  # a case guard is a flow break
                t += 1 + _cc_expr(case.guard, nesting)
            t += _cc_seq(case.body, nesting + 1)
        return t
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return 0  # nested def/class scored separately
    # other statement: recurse into child statements + expressions at this nesting
    t = 0
    for child in ast.iter_child_nodes(node):
        t += _cc_stmt(child, nesting) if isinstance(child, ast.stmt) else _cc_expr(child, nesting)
    return t


def _cc_expr(node: ast.AST, nesting: int = 0) -> int:
    """Cognitive increments inside an expression: each boolean-operator sequence
    (+1, no nesting), each ternary (+1 + nesting, body nests), and each comprehension
    filter `if` (+1)."""
    if not isinstance(node, ast.AST):
        return 0
    if isinstance(node, ast.BoolOp):
        return 1 + sum(_cc_expr(v, nesting) for v in node.values)
    if isinstance(node, ast.IfExp):
        return (1 + nesting + _cc_expr(node.test, nesting)
                + _cc_expr(node.body, nesting + 1) + _cc_expr(node.orelse, nesting + 1))
    if isinstance(node, ast.comprehension):
        return len(node.ifs) + sum(_cc_expr(c, nesting) for c in ast.iter_child_nodes(node))
    return sum(_cc_expr(c, nesting) for c in ast.iter_child_nodes(node))


# --- cyclomatic complexity ------------------------------------------------

def cyclomatic_complexity(func: ast.AST) -> int:
    """Cyclomatic complexity of a function node (1 + decision points; nested defs
    excluded so it matches the cognitive scope)."""
    score = 1
    for node in _body_nodes(func):
        if isinstance(node, (ast.If, ast.IfExp, ast.For, ast.AsyncFor, ast.While,
                             ast.ExceptHandler)):
            score += 1
        elif isinstance(node, ast.BoolOp):
            score += len(node.values) - 1
        elif isinstance(node, ast.comprehension):
            score += len(node.ifs)
        elif isinstance(node, getattr(ast, "match_case", ())):
            score += 1
    return score


def _body_nodes(func: ast.AST):
    """Every descendant of a function's body, not descending into nested defs."""
    stack = list(getattr(func, "body", []))
    while stack:
        n = stack.pop()
        yield n
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        stack.extend(ast.iter_child_nodes(n))


# --- per-file analysis ----------------------------------------------------

def _functions(tree: ast.AST):
    """Yield (function_node, qualified_name) for every def, prefixing methods with
    their class (Class.method) and nested defs with their encloser."""
    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, ast.ClassDef):
                yield from walk(child, prefix + child.name + ".")
            elif isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                yield child, prefix + child.name
                yield from walk(child, prefix + child.name + ".")
            else:
                yield from walk(child, prefix)
    yield from walk(tree, "")


def analyse_source(code: str) -> list[dict]:
    """Per-function complexity for Python source. Raises SyntaxError on bad source."""
    tree = ast.parse(code)
    return [{"name": qual, "line": node.lineno,
             "cognitive": cognitive_complexity(node),
             "cyclomatic": cyclomatic_complexity(node)}
            for node, qual in _functions(tree)]


def _analyse_with_lizard(path: Path) -> list[dict]:
    """Cyclomatic per function for non-Python files via the lizard soft dep; an
    empty list (unscored) when lizard is not installed or the file cannot be read."""
    try:
        import lizard
    except ImportError:
        return []
    try:
        info = lizard.analyze_file(str(path))
    except Exception:  # noqa: BLE001 - a tool failure must not break the scan
        return []
    return [{"name": f.name, "line": f.start_line,
             "cognitive": None, "cyclomatic": f.cyclomatic_complexity}
            for f in info.function_list]


def analyse_file(path: Path | str) -> list[dict]:
    """Per-function complexity for one file: stdlib for `.py`, lizard for the rest."""
    p = Path(path)
    if p.suffix == ".py":
        try:
            return analyse_source(p.read_text(encoding="utf-8"))
        except (SyntaxError, OSError, UnicodeDecodeError):
            return []
    return _analyse_with_lizard(p)


def cognitive_high(repo_root: Path | str = ".") -> int:
    """The cognitive-complexity 'high' threshold, project-overridable via
    `.config.yaml` `complexity.cognitive_high` (default 15)."""
    val = sdlc_md.project_override(repo_root, "complexity.cognitive_high", DEFAULT_COGNITIVE_HIGH)
    try:
        return int(val)
    except (TypeError, ValueError):
        return DEFAULT_COGNITIVE_HIGH


def churn_high(repo_root: Path | str = ".") -> int:
    """The churn 'high' threshold (commits touching a file), overridable via
    `.config.yaml` `complexity.churn_high` (default 12)."""
    val = sdlc_md.project_override(repo_root, "complexity.churn_high", DEFAULT_CHURN_HIGH)
    try:
        return int(val)
    except (TypeError, ValueError):
        return DEFAULT_CHURN_HIGH


def churn(repo_root: Path | str = ".") -> dict:
    """Commits touching each file (repo-relative) from git history. Empty dict when not
    a git repo or git is unavailable - the composite then degrades to complexity only."""
    try:
        out = subprocess.run(["git", "-C", str(repo_root), "-c", "core.quotepath=false",
                              "log", "--pretty=format:", "--name-only"],
                             capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return {}
    if out.returncode != 0:
        return {}
    counts: dict = {}
    for line in out.stdout.splitlines():
        f = line.strip()
        if f:
            counts[f] = counts.get(f, 0) + 1
    return counts


def composite_risk(cognitive: int, churn_count: int, repo_root: Path | str = ".") -> tuple[str, float]:
    """Churn-weighted composite defect-risk band for a file. Normalises each
    signal to its 'high' threshold and weights churn ~3x complexity (calibrated: churn is
    the stronger defect predictor). Returns (band, score); score 1.0 = both at threshold."""
    cog_high, ch_high = cognitive_high(repo_root), churn_high(repo_root)
    ch = min((churn_count or 0) / ch_high, 2.0)
    cog = min((cognitive or 0) / cog_high, 2.0)
    score = round((W_CHURN * ch + W_COGNITIVE * cog) / (W_CHURN + W_COGNITIVE), 3)
    band = "high" if score >= 1.0 else "medium" if score >= 0.5 else "low"
    # Floor: either signal alone over its 'high' threshold is at least medium - a complex
    # (or hot) file never bands 'low' just because the OTHER signal is quiet (e.g. complex
    # greenfield code with no churn history).
    if band == "low" and ((cognitive or 0) >= cog_high or (churn_count or 0) >= ch_high):
        band = "medium"
    return band, score


def _source_files(root: Path):
    for path in sorted(root.rglob("*")):
        if path.is_dir() or path.suffix not in CODE_SUFFIXES:
            continue
        if any(part in IGNORE_DIRS for part in path.relative_to(root).parts):
            continue
        yield path


def scan(repo_root: Path | str = ".") -> list[dict]:
    """Every scored function under the repo, each tagged with its file (repo-relative)."""
    root = Path(repo_root)
    out: list[dict] = []
    for path in _source_files(root):
        for fn in analyse_file(path):
            fn["file"] = str(path.relative_to(root))
            out.append(fn)
    return out


# --- change blast-radius assessment for `code plan` -----------------------

def assess(repo_root: Path | str, files, threshold: int | None = None) -> dict:
    """Difficulty signal + refactor-first recommendation for a change's blast radius.
    `files` is the set a story will touch (e.g. repo_map's ranked
    neighbourhood). Advisory only: a high score recommends a scoped refactor
    first, it never blocks. Returns the difficulty band, the hot functions, and
    a refactor-first line per hotspot.

    Read `applicable` before `max_cognitive`. When the change touches nothing scoreable (docs,
    config, plain text) the signal is INAPPLICABLE, not zero, and `difficulty` is `unknown`
    rather than `low` - a non-code change is not an easy change, and a caller that reads the
    bare 0 will conclude it is."""
    root = Path(repo_root)
    threshold = threshold if threshold is not None else cognitive_high(root)
    touched: list[dict] = []
    for f in files:
        p = Path(f) if Path(f).is_absolute() else root / f
        for fn in analyse_file(p):
            rec = dict(fn)
            rec["file"] = f
            touched.append(rec)
    cogs = [t["cognitive"] for t in touched if t.get("cognitive") is not None]
    max_cog = max(cogs) if cogs else 0
    # IS THE CODE-COMPLEXITY SIGNAL APPLICABLE AT ALL? A markdown, YAML or plain-text file
    # RESOLVES on disk and then yields no scored function, so `max_cognitive` comes back 0 - and
    # a consumer cannot tell that zero apart from "simple code". It is not simple code. It is not
    # code. A resolved-but-inapplicable signal is more dangerous than an absent one, because
    # absence is visible and a confident zero is not: a docs-only change scored `trivial` with
    # HIGH confidence in the router on exactly this zero, and cost 205,534 tokens.
    #
    # So applicability is reported, and consumers treat an inapplicable signal as MISSING rather
    # than as a measurement of zero. `scored_files` is the evidence for it: the number of touched
    # files that produced at least one scored function.
    scored_files = len({t["file"] for t in touched if t.get("cognitive") is not None})
    applicable = scored_files > 0
    hotspots = sorted((t for t in touched if (t.get("cognitive") or 0) >= threshold),
                      key=lambda t: t["cognitive"], reverse=True)
    difficulty = ("unknown" if not applicable
                  else "high" if max_cog >= threshold
                  else "medium" if max_cog >= threshold / 2 else "low")
    refactor_first = [
        f"{h['file']}:{h['line']} {h['name']} (cognitive {h['cognitive']}) - "
        "reduce before changing; scope the refactor to this change"
        for h in hotspots
    ]
    # churn-weighted composite defect-risk band over the touched files (the worst
    # file's band). Degrades to complexity-only when there is no git churn.
    ch_map = churn(root)

    def _rel_key(f: str) -> str:  # churn keys are repo-relative; normalise absolute/relative paths
        p = Path(f)
        p = p if p.is_absolute() else root / f
        try:
            return str(p.resolve().relative_to(root.resolve()))
        except (ValueError, OSError):
            return f
    for t in touched:
        t["churn"] = ch_map.get(_rel_key(t["file"]), ch_map.get(t["file"], 0))
    risk_band, risk_score = "low", 0.0
    for t in touched:
        b, s = composite_risk(t.get("cognitive") or 0, t.get("churn") or 0, root)
        if s > risk_score:
            risk_band, risk_score = b, s
    # A docs / config file produces no scored function, so it never enters `touched` - but its
    # CHURN is still derivable (how often it changes is a property of the FILE, not its functions).
    # Fold each unscored touched file's churn-only risk in, so a constantly-churning doc is not
    # invisible to the router just because it carries no cognitive score. Code `difficulty` stays
    # `unknown` for a non-code change (that signal really is inapplicable); only the churn-driven
    # `risk_band` picks it up - they were wrongly made to go missing together.
    scored_file_set = {t["file"] for t in touched}
    for f in files:
        if f in scored_file_set:
            continue
        ch = ch_map.get(_rel_key(f), ch_map.get(f, 0))
        if not ch:
            continue
        b, s = composite_risk(0, ch, root)
        if s > risk_score:
            risk_band, risk_score = b, s
    return {"threshold": threshold, "touched_functions": len(touched),
            "max_cognitive": max_cog, "total_cognitive": sum(cogs),
            # `applicable` is False when NOTHING the change touches can carry a code-complexity
            # score (a docs-only or config-only change). `max_cognitive` is still 0 there, for
            # callers that only want a number, but 0 means "no measurement", not "no complexity".
            "applicable": applicable, "scored_files": scored_files,
            "difficulty": difficulty, "risk_band": risk_band, "risk_score": risk_score,
            "hotspots": hotspots, "refactor_first": refactor_first}


# --- CLI ------------------------------------------------------------------

def cmd_scan(args: argparse.Namespace) -> int:
    root = Path(args.root)
    threshold = args.threshold if args.threshold is not None else cognitive_high(root)
    results = scan(root)
    hot = sorted((r for r in results if (r.get("cognitive") or 0) >= threshold),
                 key=lambda r: r["cognitive"], reverse=True)
    if args.format == "json":
        print(json.dumps({"threshold": threshold, "functions": results, "hotspots": hot}, indent=2))
    else:
        print(f"complexity: {len(results)} function(s), {len(hot)} over cognitive {threshold}")
        for r in hot[:args.limit]:
            print(f"  {r['file']}:{r['line']} {r['name']} - cognitive {r['cognitive']}, "
                  f"cyclomatic {r['cyclomatic']}")
        if not hot:
            print("  no hotspots - all functions under the threshold")
    return 0


def cmd_assess(args: argparse.Namespace) -> int:
    result = assess(args.root, args.files, args.threshold)
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(f"difficulty: {result['difficulty']} "
              f"(max cognitive {result['max_cognitive']}, threshold {result['threshold']}, "
              f"{result['touched_functions']} function(s) touched)")
        if result["refactor_first"]:
            print("refactor-first (recommended, not blocking):")
            for line in result["refactor_first"]:
                print(f"  - {line}")
        else:
            print("  no refactor-first hotspots in the blast radius")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Code-complexity signals.")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scan", help="Cognitive + cyclomatic complexity per function.")
    s.add_argument("--root", default=".", help="Repo root (default: .)")
    s.add_argument("--threshold", type=int, default=None,
                   help="Cognitive 'high' threshold (default: config or 15)")
    s.add_argument("--limit", type=int, default=20, help="Max hotspots to print (text mode)")
    s.add_argument("--format", choices=("text", "json"), default="text")
    s.set_defaults(func=cmd_scan)
    a = sub.add_parser("assess", help="Blast-radius difficulty + refactor-first reco for a change.")
    a.add_argument("--root", default=".", help="Repo root (default: .)")
    a.add_argument("--files", nargs="+", required=True, help="Files the change will touch")
    a.add_argument("--threshold", type=int, default=None,
                   help="Cognitive 'high' threshold (default: config or 15)")
    a.add_argument("--format", choices=("text", "json"), default="text")
    a.set_defaults(func=cmd_assess)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
