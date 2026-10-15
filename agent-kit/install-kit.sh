#!/usr/bin/env bash
# Compass agent kit installer (bash: Linux, macOS, Git Bash, WSL).
# Copies the kit into a target repository. Never overwrites existing files: they are skipped and reported.
#
# Usage: ./install-kit.sh <target-repo-path> [--with-vendor] [--dry-run]
#   --with-vendor  also copy unmodified third-party originals into <target>/.agent-kit/vendor/
#   --dry-run      show what would be copied, change nothing
set -euo pipefail

usage() { sed -n '2,8p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

TARGET=""
WITH_VENDOR=0
DRY_RUN=0
for arg in "$@"; do
  case "$arg" in
    --with-vendor) WITH_VENDOR=1 ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help) usage 0 ;;
    -*) echo "Unknown option: $arg" >&2; usage 1 ;;
    *) if [ -z "$TARGET" ]; then TARGET="$arg"; else echo "Only one target path allowed" >&2; usage 1; fi ;;
  esac
done
[ -n "$TARGET" ] || usage 1
[ -d "$TARGET" ] || { echo "Target directory not found: $TARGET" >&2; exit 1; }

KIT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$(cd "$TARGET" && pwd)"
if [ "$KIT" = "$TARGET" ]; then echo "Target must be a different directory than the kit." >&2; exit 1; fi
[ -d "$TARGET/.git" ] || echo "Note: $TARGET does not look like a git repository root (no .git). Continuing."

copied=0; skipped=0
SKIPPED_LIST=""

copy_file() { # $1 = source file, $2 = destination file
  local src="$1" dst="$2"
  if [ -e "$dst" ]; then
    skipped=$((skipped + 1)); SKIPPED_LIST="${SKIPPED_LIST}  ${dst#"$TARGET"/}"$'\n'
    return
  fi
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "would copy: ${dst#"$TARGET"/}"
  else
    mkdir -p "$(dirname "$dst")"
    cp "$src" "$dst"
  fi
  copied=$((copied + 1))
}

copy_tree() { # $1 = source dir (relative to kit), $2 = destination dir (relative to target)
  local srcdir="$KIT/$1" dstdir="$TARGET/$2"
  [ -d "$srcdir" ] || return 0
  while IFS= read -r -d '' f; do
    copy_file "$f" "$dstdir/${f#"$srcdir"/}"
  done < <(find "$srcdir" -type f -print0)
}

# Files agents read in place
copy_file "$KIT/AGENTS.md" "$TARGET/AGENTS.md"
copy_file "$KIT/CLAUDE.md" "$TARGET/CLAUDE.md"
copy_tree ".github" ".github"
copy_tree ".claude" ".claude"

# Reference material (not auto-loaded by any tool)
copy_file "$KIT/README.md" "$TARGET/.agent-kit/README.md"
copy_file "$KIT/tool-routing-guide.md" "$TARGET/.agent-kit/tool-routing-guide.md"
copy_tree "devin" ".agent-kit/devin"
copy_tree "prompt-library" ".agent-kit/prompt-library"
[ "$WITH_VENDOR" -eq 1 ] && copy_tree "vendor" ".agent-kit/vendor"

echo
echo "Compass agent kit -> $TARGET"
[ "$DRY_RUN" -eq 1 ] && echo "(dry run: nothing was written)"
echo "Copied:  $copied file(s)"
echo "Skipped: $skipped file(s) that already exist (left untouched)"
[ -n "$SKIPPED_LIST" ] && printf '%s' "$SKIPPED_LIST"
cat <<'NEXT'

Next steps:
  1. Fill {{PLACEHOLDERS}} in AGENTS.md and .github/copilot-instructions.md
     (or ask an agent: Copilot "/create-agents-md", Claude Code "/create-agents-md").
  2. For skipped files, merge the kit's version by hand (see .agent-kit/README.md).
  3. VS Code: enable "chat.useAgentsMdFile" if you want Copilot to read AGENTS.md.
  4. Devin: create Playbooks and Knowledge from .agent-kit/devin/ (see its README).
  5. Commit on a branch and open a PR for review.
NEXT
