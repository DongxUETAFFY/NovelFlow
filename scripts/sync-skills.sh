#!/usr/bin/env bash
# Sync tracked skills/ to local Claude Code skill directories.
#
# Source of truth:
#   skills/                 - tracked distribution files in this repo
#
# Targets:
#   .claude/skills/         - local project copy used during development (ignored)
#   ~/.claude/skills/       - active user install (Claude Code reads from here)
#
# Usage:
#   ./scripts/sync-skills.sh           # sync both targets
#   ./scripts/sync-skills.sh --local   # sync .claude/skills/ only
#   ./scripts/sync-skills.sh --install # sync ~/.claude/skills/ only
#   ./scripts/sync-skills.sh --check   # verify targets match source

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO_ROOT/skills"
LOCAL="$REPO_ROOT/.claude/skills"
INSTALL="$HOME/.claude/skills"

SYNC_LOCAL=false
SYNC_INSTALL=false
CHECK_ONLY=false

if [ $# -eq 0 ]; then
    SYNC_LOCAL=true
    SYNC_INSTALL=true
else
    case "$1" in
        --local)   SYNC_LOCAL=true ;;
        --install) SYNC_INSTALL=true ;;
        --check)   CHECK_ONLY=true ;;
        *)
            echo "Usage: $0 [--local | --install | --check]"
            echo "  (no args)  sync both targets"
            echo "  --local    sync .claude/skills/ only"
            echo "  --install  sync ~/.claude/skills/ only"
            echo "  --check    verify targets match skills/"
            exit 1
            ;;
    esac
fi

for skill in novel-setup novel-write; do
    if [ ! -d "$SRC/$skill" ]; then
        echo "ERROR: source skill missing: $SRC/$skill"
        exit 1
    fi
done

sync_target() {
    target_root="$1"
    label="$2"

    echo "==> Syncing skills/ -> $label"
    mkdir -p "$target_root"
    for skill in novel-setup novel-write; do
        rm -rf "$target_root/$skill"
        cp -R "$SRC/$skill" "$target_root/$skill"
    done
    echo "    Done."
}

check_target() {
    target_root="$1"
    label="$2"

    if [ ! -d "$target_root" ]; then
        echo "WARN: $label does not exist: $target_root"
        return 0
    fi

    for skill in novel-setup novel-write; do
        if [ ! -d "$target_root/$skill" ]; then
            echo "FAIL: $label missing $skill"
            return 1
        fi
        if ! diff -qr "$SRC/$skill" "$target_root/$skill" >/dev/null; then
            echo "FAIL: $label/$skill differs from skills/$skill"
            return 1
        fi
    done

    echo "PASS: $label matches skills/"
}

if $CHECK_ONLY; then
    check_target "$LOCAL" ".claude/skills"
    check_target "$INSTALL" "~/.claude/skills"
    exit 0
fi

if $SYNC_LOCAL; then
    sync_target "$LOCAL" ".claude/skills/"
fi

if $SYNC_INSTALL; then
    sync_target "$INSTALL" "~/.claude/skills/"
    echo "    Restart Claude Code to pick up changes."
fi
