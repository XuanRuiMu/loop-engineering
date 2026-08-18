#!/usr/bin/env bash
# Loop Engineering installer — copies the bundled skills into your agent's skills dir.
# Usage: bash install.sh [TARGET_DIR]
#   default TARGET_DIR = ~/.claude/skills  (Claude Code global skills)
set -euo pipefail

REPO="XuanRuiMu/loop-engineering"
BRANCH="main"
TARGET="${1:-$HOME/.claude/skills}"

echo "Loop Engineering installer"
echo "Target skills dir: $TARGET"

mkdir -p "$TARGET"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

url="https://github.com/$REPO/archive/refs/heads/$BRANCH.tar.gz"
echo "Downloading $url"
curl -fsSL "$url" -o "$tmp/loop.tgz"
tar -xzf "$tmp/loop.tgz" -C "$tmp"
src="$tmp/loop-engineering-$BRANCH/skills"
cp -r "$src/." "$TARGET/"

echo "Installed. Restart your agent (or run its /skills reload) to load the skills."
