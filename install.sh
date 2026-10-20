#!/usr/bin/env bash
#
# Install the myanmar-writing skill and its slash commands.
#
#   ./install.sh              link globally (~/.config/opencode)
#   ./install.sh --project X  also link into project X/.opencode
#   ./install.sh --copy       copy instead of symlink
#   ./install.sh --uninstall  remove the global links
#
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="$REPO_DIR/.opencode/skills/myanmar-writing"
COMMANDS_SRC="$REPO_DIR/.opencode/commands"
GLOBAL_ROOT="$HOME/.config/opencode"

MODE="link"
PROJECT_DIR=""
UNINSTALL=0

while [ $# -gt 0 ]; do
  case "$1" in
    --copy) MODE="copy" ;;
    --project) PROJECT_DIR="${2:-}"; shift ;;
    --uninstall) UNINSTALL=1 ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
    *) echo "unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

link_or_copy() {
  local src="$1" dest="$2"
  mkdir -p "$(dirname "$dest")"
  rm -rf "$dest"
  if [ "$MODE" = "copy" ]; then
    cp -R "$src" "$dest"
    echo "copied  $dest"
  else
    ln -s "$src" "$dest"
    echo "linked  $dest -> $src"
  fi
}

if [ "$UNINSTALL" -eq 1 ]; then
  rm -f "$GLOBAL_ROOT/skills/myanmar-writing"
  for c in burmese burmese-casual burmese-formal burmese-diaspora; do
    rm -f "$GLOBAL_ROOT/commands/$c.md"
  done
  echo "removed global skill and commands from $GLOBAL_ROOT"
  exit 0
fi

if [ ! -d "$SKILL_SRC" ]; then
  echo "error: skill not found at $SKILL_SRC" >&2
  exit 1
fi

link_or_copy "$SKILL_SRC" "$GLOBAL_ROOT/skills/myanmar-writing"

for c in burmese burmese-casual burmese-formal burmese-diaspora; do
  [ -f "$COMMANDS_SRC/$c.md" ] && link_or_copy "$COMMANDS_SRC/$c.md" "$GLOBAL_ROOT/commands/$c.md"
done

if [ -n "$PROJECT_DIR" ]; then
  PROJECT_DIR="$(cd "$PROJECT_DIR" 2>/dev/null && pwd || echo "$PROJECT_DIR")"
  link_or_copy "$SKILL_SRC" "$PROJECT_DIR/.opencode/skills/myanmar-writing"
  for c in burmese burmese-casual burmese-formal burmese-diaspora; do
    [ -f "$COMMANDS_SRC/$c.md" ] && link_or_copy "$COMMANDS_SRC/$c.md" "$PROJECT_DIR/.opencode/commands/$c.md"
  done
  echo
  echo "Project linked into: $PROJECT_DIR/.opencode"
fi

cat <<EOF

Done.

  Skill id : myanmar-writing
  Global   : $GLOBAL_ROOT/skills/myanmar-writing
  Commands : /burmese  /burmese-casual  /burmese-formal  /burmese-diaspora

OpenCode picks up new skills and commands automatically — no restart needed.
Verify with:

  opencode api get /api/skill

Optional, enables accurate Zawgyi detection in the validator:

  pip3 install -r $SKILL_SRC/scripts/requirements.txt
EOF
