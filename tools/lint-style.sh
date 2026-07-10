#!/usr/bin/env bash
# Style guard for SDLC Studio markdown (house style: see CLAUDE.md).
#
#   1. No em-dash (U+2014). Use an en-dash with spaces ( - ) instead.
#   2. No corporate jargon (synergy, leverage, robust, journey), unless the
#      offending line contains a substring listed in tools/style-allowlist.txt.
#   3. No internal provenance tags in consuming-facing files.
#   4. British English: a bounded list of American spellings is flagged (same
#      allowlist mechanism for cited names, quotations, and API identifiers).
#
# Prints every offender and exits non-zero on any violation. Run via
# `npm run lint` (which CI runs), or directly: bash tools/lint-style.sh
# An optional first argument scans a different tree (used by the unit test);
# the allowlist is taken from that tree when it carries one, else this repo's.
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
scan_root="${1:-$repo_root}"
allowlist="$scan_root/tools/style-allowlist.txt"
[ -f "$allowlist" ] || allowlist="$repo_root/tools/style-allowlist.txt"
status=0
cd "$scan_root"

# 1. Em-dash: never allowed, no exceptions.
em_dash="$(printf '\342\200\224')"  # U+2014 as literal UTF-8 bytes, so no grep -P (absent on BSD/macOS)
if em_hits="$(grep -rIn "$em_dash" --include='*.md' --exclude-dir=node_modules . 2>/dev/null)"; then
  echo "Style error: em-dash (U+2014) found. Use an en-dash with spaces ( - ) instead."
  printf '%s\n' "$em_hits"
  status=1
fi

# 2. Corporate jargon, filtered through the allowlist.
jargon_hits="$(grep -rInwiE 'synergy|leverage|robust|journey' --include='*.md' --exclude-dir=node_modules . 2>/dev/null || true)"
if [ -n "$jargon_hits" ] && [ -f "$allowlist" ]; then
  # Strip comment and blank lines, then drop any hit whose text contains an
  # allowlisted substring (case-insensitive, fixed string).
  allow="$(grep -vE '^[[:space:]]*(#|$)' "$allowlist" || true)"
  if [ -n "$allow" ]; then
    jargon_hits="$(printf '%s\n' "$jargon_hits" | grep -ivF -- "$allow" || true)"
  fi
fi
if [ -n "$jargon_hits" ]; then
  echo "Style error: corporate jargon found. Reword, or add the line's context to tools/style-allowlist.txt."
  printf '%s\n' "$jargon_hits"
  status=1
fi

# 3. No internal provenance tags in consuming-facing docs / shipped code. A change-request id
#    (CRxxxx / BGxxxx / RFCxxxx) in parenthetical form is traceability that belongs in the skill's
#    own change-requests/, CHANGELOG, and git blame - not in files a consuming agent reads against
#    its OWN project, whose id namespace collides. The skill's artifacts keep their ids; this guards
#    only reference-*.md, help/*.md, and scripts/*.py. Two provenance forms are flagged: a
#    CR/BG/RFC id leading a parenthetical (`(CR0186)`), and a US-led provenance PAIR joined by
#    `/` or `;` (`(US0101/CR0186)`, `(US0090/CR0194)`) - the form the old pattern missed. US-form
#    is admitted only in the joined-pair shape because a lone `(US0001)` and comma/hyphen lists
#    (`(US0045, US0046)`, `(US0023-US0064)`) are legitimate example ids in tree diagrams and
#    sample output, indistinguishable from a citation. A bare id or one trailing narrative text
#    (`(e.g. CR0003)`, `(see CR0141)`) is likewise not flagged.
skill="$scan_root/.claude/skills/sdlc-studio"
prov_hits="$(grep -InE '\((CR|BG|RFC)[0-9]{4}|\(US[0-9]{4}[/;]' "$skill"/reference-*.md "$skill"/help/*.md "$skill"/scripts/*.py "$skill"/templates/config*.yaml 2>/dev/null || true)"
if [ -n "$prov_hits" ]; then
  echo "Style error: internal provenance tag in a consuming-facing file. Strip it - traceability lives in change-requests/CHANGELOG/git, not in docs a consuming project reads."
  printf '%s\n' "$prov_hits"
  status=1
fi

# 4. American spellings - the house style is British English (AGENTS.md). A bounded,
#    high-signal word list, filtered through the same allowlist so a cited product
#    name, an external quotation, or an API identifier can be permitted by line
#    context. CODE_OF_CONDUCT.md is excluded: it quotes the Contributor Covenant
#    verbatim, and third-party text is not ours to respell.
am_re='analyz(e|es|ed|ing|er|ers)|behaviors?|behavioral|colors?|colored|coloring|favorite|favorites|flavors?|honors?|honored|optimiz(e|es|ed|ing|ation)|prioritiz(e|es|ed|ing|ation)|customiz(e|es|ed|ing|ation|able)|initializ(e|es|ed|ing)|normaliz(e|es|ed|ing|ation)|standardiz(e|es|ed|ing|ation)|summariz(e|es|ed|ing)|canonicaliz(e|es|ed|ing|ation)|organiz(e|es|ed|ing|ation|ations)|minimiz(e|es|ed|ing)|maximiz(e|es|ed|ing)|serializ(e|es|ed|ing|ation)|synchroniz(e|es|ed|ing|ation)|categoriz(e|es|ed|ing|ation)|finaliz(e|es|ed|ing)'
am_hits="$(grep -rInwiE "$am_re" --include='*.md' --exclude-dir=node_modules --exclude=CODE_OF_CONDUCT.md . 2>/dev/null || true)"
if [ -n "$am_hits" ] && [ -f "$allowlist" ]; then
  allow="$(grep -vE '^[[:space:]]*(#|$)' "$allowlist" || true)"
  if [ -n "$allow" ]; then
    am_hits="$(printf '%s\n' "$am_hits" | grep -ivF -- "$allow" || true)"
  fi
fi
if [ -n "$am_hits" ]; then
  echo "Style error: American spelling found - the house style is British English."
  echo "Use the British form (-ize -> -ise, -ization -> -isation, behavior -> behaviour, color -> colour, analyze -> analyse), or add the line's context to tools/style-allowlist.txt."
  printf '%s\n' "$am_hits"
  status=1
fi

exit "$status"
