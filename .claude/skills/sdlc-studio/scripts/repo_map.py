#!/usr/bin/env python3
"""SDLC Studio repo map: pure-Python source indexer and LEXICAL relevance ranker.

Build an index of symbols and imports across the repository, then query it
with a story description to produce a ranked file list for the Agent Prompt
Template. No ctags dependency.

Ranking is lexical: token overlap between the query and each file's declared
symbols, plus a flat import in-degree hub bonus. It is NOT a semantic call
graph, reference graph, or PageRank over identifiers (imports are matched by
basename, only Python is AST-parsed). For graph-based ranking, use Aider's
repo map / RepoMapper as a soft dependency. See reference-repo-map.md#repo-map-limits.

Subcommands:
  build  Walk the repo, extract symbols and imports, write the index.
  query  Rank files by relevance to a story or free-text query.
  stats  Print index size and top-10 hub files by in-degree.

Output: JSON at sdlc-studio/.local/repo-map.json
"""
from __future__ import annotations

import argparse
import ast
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402
import complexity  # noqa: E402  (sibling; per-function complexity for the map)

# Languages are identified by extension. Each language provides a symbol
# extractor and an import extractor. Python uses the stdlib ast module;
# every other language uses regex. Regex extractors are intentionally
# shallow: they capture names and lines, not types.
SUPPORTED_EXTENSIONS = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".kt": "kotlin",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
}

# Directories to skip by default. Users can extend via --ignore.
DEFAULT_IGNORES = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    "target",
    "out",
    ".next",
    ".nuxt",
    ".svelte-kit",
    "venv",
    ".venv",
    "env",
    ".env",
    ".tox",
    ".vscode",
    ".idea",
    "coverage",
    ".DS_Store",
}

# Regex patterns per language. Each returns an iterable of
# (name, kind, line_number) tuples for symbols, or strings for imports.
_TS_SYMBOL_RE = re.compile(
    r"^\s*(?:export\s+)?(?:default\s+)?"
    r"(?:(?:async\s+)?function\s+(?P<fn>[A-Za-z_$][\w$]*)"
    r"|class\s+(?P<cls>[A-Za-z_$][\w$]*)"
    r"|(?:const|let|var)\s+(?P<var>[A-Za-z_$][\w$]*)\s*="
    r"|interface\s+(?P<iface>[A-Za-z_$][\w$]*)"
    r"|type\s+(?P<ty>[A-Za-z_$][\w$]*)\s*=)",
    re.M,
)
_TS_IMPORT_RE = re.compile(
    r"""(?:import\s+[^"']*?from\s+['"]([^'"]+)['"]|require\(\s*['"]([^'"]+)['"]\s*\))""",
    re.M,
)

_GO_SYMBOL_RE = re.compile(
    r"^\s*(?:func\s+(?:\([^)]*\)\s+)?(?P<fn>[A-Za-z_][\w]*)"
    r"|type\s+(?P<ty>[A-Za-z_][\w]*)\s+(?:struct|interface)\b)",
    re.M,
)
_GO_IMPORT_RE = re.compile(r'^\s*(?:import\s+)?"([^"]+)"', re.M)

_RS_SYMBOL_RE = re.compile(
    r"^\s*(?:pub\s+)?(?:async\s+)?(?:fn\s+(?P<fn>[A-Za-z_][\w]*)"
    r"|struct\s+(?P<st>[A-Za-z_][\w]*)"
    r"|enum\s+(?P<en>[A-Za-z_][\w]*)"
    r"|trait\s+(?P<tr>[A-Za-z_][\w]*))",
    re.M,
)
_RS_IMPORT_RE = re.compile(r"^\s*use\s+([\w:]+)", re.M)

_JAVA_SYMBOL_RE = re.compile(
    r"^\s*(?:public|private|protected)?\s*(?:static\s+)?"
    r"(?:class|interface|enum|record)\s+(?P<cls>[A-Za-z_][\w]*)",
    re.M,
)
_JAVA_IMPORT_RE = re.compile(r"^\s*import\s+(?:static\s+)?([\w.]+)\s*;", re.M)

_CS_SYMBOL_RE = re.compile(
    r"^\s*(?:public|internal|private|protected)?\s*"
    r"(?:class|interface|struct|enum|record)\s+(?P<cls>[A-Za-z_][\w]*)",
    re.M,
)
_CS_IMPORT_RE = re.compile(r"^\s*using\s+([\w.]+)\s*;", re.M)

_RUBY_SYMBOL_RE = re.compile(
    r"^\s*(?:class|module|def)\s+(?P<name>[A-Za-z_][\w]*)",
    re.M,
)
_RUBY_IMPORT_RE = re.compile(r"^\s*require(?:_relative)?\s+['\"]([^'\"]+)['\"]", re.M)

_PHP_SYMBOL_RE = re.compile(
    r"^\s*(?:final|abstract)?\s*(?:class|interface|trait)\s+(?P<cls>[A-Za-z_][\w]*)"
    r"|\s*function\s+(?P<fn>[A-Za-z_][\w]*)",
    re.M,
)
_PHP_IMPORT_RE = re.compile(r"^\s*use\s+([\w\\\\]+)\s*;", re.M)

_SWIFT_SYMBOL_RE = re.compile(
    r"^\s*(?:public|private|internal|open)?\s*"
    r"(?:class|struct|enum|protocol|func)\s+(?P<name>[A-Za-z_][\w]*)",
    re.M,
)
_SWIFT_IMPORT_RE = re.compile(r"^\s*import\s+([\w.]+)", re.M)


@dataclass
class FileEntry:
    language: str
    symbols: list[dict] = field(default_factory=list)
    imports: list[str] = field(default_factory=list)
    in_degree: int = 0

    def to_dict(self) -> dict:
        """Serialise this entry to a plain dict for JSON output."""
        return {
            "language": self.language,
            "symbols": self.symbols,
            "imports": self.imports,
            "in_degree": self.in_degree,
        }


def parse_python(text: str) -> tuple[list[dict], list[str]]:
    """Extract symbols and imports from Python source via the ast module."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return _parse_python_regex(text)

    symbols: list[dict] = []
    imports: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            symbols.append({"name": node.name, "kind": "function", "line": node.lineno,
                            "cognitive": complexity.cognitive_complexity(node),
                            "cyclomatic": complexity.cyclomatic_complexity(node)})
        elif isinstance(node, ast.ClassDef):
            symbols.append({"name": node.name, "kind": "class", "line": node.lineno})
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            imports.append(module)
    return symbols, imports


def _parse_python_regex(text: str) -> tuple[list[dict], list[str]]:
    """Regex fallback when Python syntax fails (e.g., incomplete files)."""
    sym_re = re.compile(
        r"^(?:\s*)(?:async\s+)?(?:def|class)\s+([A-Za-z_][\w]*)",
        re.M,
    )
    imp_re = re.compile(r"^(?:from\s+(\S+)\s+import|import\s+(\S+))", re.M)
    symbols: list[dict] = []
    for m in sym_re.finditer(text):
        line = text[: m.start()].count("\n") + 1
        symbols.append({"name": m.group(1), "kind": "function", "line": line})
    imports: list[str] = []
    for m in imp_re.finditer(text):
        imports.append(m.group(1) or m.group(2) or "")
    return symbols, imports


def parse_with_regex(
    text: str, symbol_re: re.Pattern, import_re: re.Pattern
) -> tuple[list[dict], list[str]]:
    """Extract symbols and imports for non-Python languages via regex."""
    symbols: list[dict] = []
    for m in symbol_re.finditer(text):
        groups = m.groupdict()
        for kind_key, name in groups.items():
            if name:
                line = text[: m.start()].count("\n") + 1
                symbols.append({"name": name, "kind": kind_key, "line": line})
                break
    imports: list[str] = []
    for m in import_re.finditer(text):
        for g in m.groups():
            if g:
                imports.append(g)
                break
    return symbols, imports


LANGUAGE_PARSERS = {
    "python": parse_python,
    "typescript": lambda t: parse_with_regex(t, _TS_SYMBOL_RE, _TS_IMPORT_RE),
    "javascript": lambda t: parse_with_regex(t, _TS_SYMBOL_RE, _TS_IMPORT_RE),
    "go": lambda t: parse_with_regex(t, _GO_SYMBOL_RE, _GO_IMPORT_RE),
    "rust": lambda t: parse_with_regex(t, _RS_SYMBOL_RE, _RS_IMPORT_RE),
    "java": lambda t: parse_with_regex(t, _JAVA_SYMBOL_RE, _JAVA_IMPORT_RE),
    "kotlin": lambda t: parse_with_regex(t, _JAVA_SYMBOL_RE, _JAVA_IMPORT_RE),
    "csharp": lambda t: parse_with_regex(t, _CS_SYMBOL_RE, _CS_IMPORT_RE),
    "ruby": lambda t: parse_with_regex(t, _RUBY_SYMBOL_RE, _RUBY_IMPORT_RE),
    "php": lambda t: parse_with_regex(t, _PHP_SYMBOL_RE, _PHP_IMPORT_RE),
    "swift": lambda t: parse_with_regex(t, _SWIFT_SYMBOL_RE, _SWIFT_IMPORT_RE),
}


def walk_source_files(root: Path, ignores: set[str]) -> Iterable[Path]:
    """Yield source files under root, skipping ignored dirs.

    Hidden directories are pruned everywhere except at the repo root, so
    top-level dotdirs such as .claude/ are indexed while nested caches like
    src/.cache are not.
    """
    root_str = str(root)
    for dirpath, dirnames, filenames in os.walk(root):
        at_root = dirpath == root_str
        # Prune in-place so os.walk doesn't descend into ignored or (below the
        # root) hidden directories.
        dirnames[:] = [
            d for d in dirnames
            if d not in ignores and (at_root or not d.startswith("."))
        ]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if ext in SUPPORTED_EXTENSIONS:
                yield Path(dirpath) / name


def build_index(root: Path, ignores: set[str]) -> dict[str, FileEntry]:
    """Parse every source file and build a path -> FileEntry map."""
    root = root.resolve()
    entries: dict[str, FileEntry] = {}
    for path in walk_source_files(root, ignores):
        rel = str(path.relative_to(root))
        ext = path.suffix.lower()
        language = SUPPORTED_EXTENSIONS[ext]
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        parser = LANGUAGE_PARSERS.get(language)
        if not parser:
            continue
        symbols, imports = parser(text)
        entries[rel] = FileEntry(
            language=language,
            symbols=symbols,
            imports=imports,
        )
    compute_in_degree(entries)
    return entries


def compute_in_degree(entries: dict[str, FileEntry]) -> None:
    """Set in_degree on each entry based on how many other files import it.

    Imports are resolved heuristically: we match import substrings against
    file paths. Exact matches score higher than partial ones. This is
    intentionally crude because a regex indexer cannot do real module
    resolution; the point is to find hub files, not build a call graph.
    """
    if not entries:
        return

    # Build a simple index of basename -> paths for fast import matching
    basenames: dict[str, list[str]] = {}
    for path in entries:
        name = os.path.basename(path)
        stem = os.path.splitext(name)[0]
        basenames.setdefault(stem, []).append(path)
        basenames.setdefault(name, []).append(path)

    for importer, entry in entries.items():
        for imp in entry.imports:
            # Strip quotes, a single leading './', and trailing dots
            imp_clean = imp.strip("\"'").rstrip(".")
            if imp_clean.startswith("./"):
                imp_clean = imp_clean[2:]
            tail = os.path.basename(imp_clean)
            tail_stem = os.path.splitext(tail)[0]
            candidates = basenames.get(tail_stem) or basenames.get(tail)
            if not candidates:
                continue
            for cand in candidates:
                if cand != importer:
                    entries[cand].in_degree += 1


def write_index(entries: dict[str, FileEntry], out_path: Path, root: Path) -> None:
    """Serialise the index to JSON at out_path."""
    data = {
        "version": 1,
        "generated_at": sdlc_md.now_iso8601(),
        "root": str(root.resolve()),
        "files": {path: entry.to_dict() for path, entry in entries.items()},
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# -----------------------------------------------------------------------------
# Query
# -----------------------------------------------------------------------------

_CAMEL_RE = re.compile(r"([a-z0-9])([A-Z])")
_SNAKE_RE = re.compile(r"[_\-]")


def tokenise(text: str) -> set[str]:
    """Break a story or description into relevance tokens.

    Tokens are >=3 char lowercase words, plus CamelCase splits and
    snake_case splits. Stopwords removed to cut noise.
    """
    stop = {
        "the", "and", "for", "with", "that", "this", "from", "into", "when",
        "then", "given", "must", "should", "user", "users", "have", "has",
        "will", "can", "any", "all", "but", "not", "are", "was", "were",
        "new", "old", "been", "their", "its", "own", "use", "using", "via",
        "api", "ui", "page", "file", "class", "type", "function", "method",
        "ac", "story", "epic", "test", "tests",
    }
    words = re.findall(r"[A-Za-z][A-Za-z0-9_]{2,}", text)
    expanded: set[str] = set()
    for w in words:
        # Split CamelCase
        snake = _CAMEL_RE.sub(r"\1_\2", w).lower()
        for part in _SNAKE_RE.split(snake):
            if len(part) >= 3 and part not in stop:
                expanded.add(part)
    return expanded


def score_file(path: str, entry: FileEntry, tokens: set[str]) -> tuple[float, list[str]]:
    """Return (score, matched_tokens) for one file against a token set.

    Files with zero token matches always score 0 regardless of in_degree.
    This prevents hub files from polluting every query result.
    """
    score = 0.0
    matched: set[str] = set()

    path_tokens = tokenise(path)
    for t in tokens:
        if t in path_tokens:
            score += 2.0
            matched.add(t)

    for sym in entry.symbols:
        sym_tokens = tokenise(sym["name"])
        for t in tokens:
            if t in sym_tokens:
                score += 3.0
                matched.add(t)

    if not matched:
        return 0.0, []

    # Hub bonus only when the file was already matched on content
    score += entry.in_degree * 0.5

    return score, sorted(matched)


def query_index(map_path: Path, story_text: str, top_n: int) -> list[dict]:
    """Rank indexed files by relevance to story_text, top_n results."""
    data = sdlc_md.read_json(map_path, None)
    if data is None:
        raise ValueError(f"{map_path} is not valid JSON")
    entries = data.get("files", {})
    tokens = tokenise(story_text)
    if not tokens:
        return []

    scored: list[tuple[float, str, list[str], int]] = []
    for path, file_data in entries.items():
        entry = FileEntry(
            language=file_data.get("language", ""),
            symbols=file_data.get("symbols", []),
            imports=file_data.get("imports", []),
            in_degree=file_data.get("in_degree", 0),
        )
        score, matched = score_file(path, entry, tokens)
        if score > 0:
            scored.append((score, path, matched, entry.in_degree))

    scored.sort(key=lambda t: (-t[0], t[1]))
    top = scored[:top_n]
    return [
        {
            "path": path,
            "score": round(score, 2),
            "matched": matched,
            "in_degree": in_degree,
        }
        for score, path, matched, in_degree in top
    ]


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------


def cmd_build(args: argparse.Namespace) -> int:
    """Walk the repo, build the index, and write it to disk."""
    root = Path(args.root).resolve()
    if not root.exists():
        print(f"error: root does not exist: {root}", file=sys.stderr)
        return 2
    ignores = set(DEFAULT_IGNORES)
    for extra in args.ignore or []:
        ignores.add(extra)
    start = time.time()
    entries = build_index(root, ignores)
    elapsed = time.time() - start
    out = Path(args.out)
    write_index(entries, out, root)
    print(
        f"indexed {len(entries)} files in {elapsed:.2f}s "
        f"-> {out}"
    )
    return 0


def cmd_query(args: argparse.Namespace) -> int:
    """Rank files against a story file or free-text query and print them."""
    map_path = Path(args.map)
    if not map_path.exists():
        print(
            f"error: repo map not found at {map_path}. "
            f"Run `repo_map.py build` first.",
            file=sys.stderr,
        )
        return 2

    story_arg = args.story
    if not story_arg:
        print("error: --story is required", file=sys.stderr)
        return 2

    story_path = Path(story_arg)
    if story_path.exists():
        story_text = story_path.read_text(encoding="utf-8", errors="ignore")
    else:
        story_text = story_arg

    try:
        results = query_index(map_path, story_text, args.top)
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print("no matches")
            return 0
        for r in results:
            matched = ", ".join(r["matched"][:5])
            print(
                f"{r['score']:>6.2f}  in={r['in_degree']:<3}  {r['path']}"
                + (f"  [{matched}]" if matched else "")
            )
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Print index size, language breakdown, and top hub files."""
    map_path = Path(args.map)
    if not map_path.exists():
        print(f"error: repo map not found at {map_path}", file=sys.stderr)
        return 2
    data = sdlc_md.read_json(map_path, None)
    if data is None:
        print(f"error: {map_path} is not valid JSON", file=sys.stderr)
        return 2
    entries = data.get("files", {})
    if not entries:
        print("empty index")
        return 0

    langs: dict[str, int] = {}
    for e in entries.values():
        lang = e.get("language", "unknown")
        langs[lang] = langs.get(lang, 0) + 1

    top_hubs = sorted(
        entries.items(),
        key=lambda kv: kv[1].get("in_degree", 0),
        reverse=True,
    )[:10]

    print(f"generated_at: {data.get('generated_at')}")
    print(f"root:         {data.get('root')}")
    print(f"files:        {len(entries)}")
    print("by language:")
    for lang, n in sorted(langs.items(), key=lambda kv: -kv[1]):
        print(f"  {lang:<12} {n}")
    print("top hubs (by in_degree):")
    for path, info in top_hubs:
        in_deg = info.get("in_degree", 0)
        if in_deg == 0:
            break
        print(f"  {in_deg:>4}  {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the argparse parser for build, query, and stats."""
    p = argparse.ArgumentParser(
        prog="repo_map.py",
        description="Pure-Python repo indexer and relevance ranker.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="Build the index.")
    b.add_argument("--root", default=".", help="Repo root to index (default: .)")
    b.add_argument(
        "--out",
        default="sdlc-studio/.local/repo-map.json",
        help="Output JSON path (default: sdlc-studio/.local/repo-map.json)",
    )
    b.add_argument(
        "--ignore",
        action="append",
        help="Additional directory name to ignore (repeatable)",
    )
    b.set_defaults(func=cmd_build)

    q = sub.add_parser("query", help="Rank files against a story or text.")
    q.add_argument("--story", required=True, help="Story file path or free-text query")
    q.add_argument(
        "--map",
        default="sdlc-studio/.local/repo-map.json",
        help="Repo map JSON path",
    )
    q.add_argument("--top", type=int, default=15, help="Number of results (default 15)")
    q.add_argument("--format", choices=("plain", "json"), default="plain")
    q.set_defaults(func=cmd_query)

    s = sub.add_parser("stats", help="Print index stats.")
    s.add_argument(
        "--map",
        default="sdlc-studio/.local/repo-map.json",
        help="Repo map JSON path",
    )
    s.set_defaults(func=cmd_stats)

    return p


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and dispatch to the chosen subcommand."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001 - top-level guard
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
