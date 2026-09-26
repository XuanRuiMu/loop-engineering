#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REMOTE=false
FORCE=false
ALLOW_DIRTY=false
RECOVER_STALE_LOCK=false
PURGE_BACKUPS=false
REMOTE_COMMIT=""
MANAGED_MARKER="loop-engineering-managed-v1"
TARGET=""
while [ "$#" -gt 0 ]; do
    case "$1" in
        --remote) REMOTE=true ;;
        --force) FORCE=true ;;
        --allow-dirty) ALLOW_DIRTY=true ;;
        --recover-stale-lock) RECOVER_STALE_LOCK=true ;;
        --purge-backups) PURGE_BACKUPS=true ;;
        --remote-commit) shift; REMOTE_COMMIT="${1:-}" ;;
        --*) echo "Unknown option: $1" >&2; exit 1 ;;
        *) TARGET="$1" ;;
    esac
    shift
done
if [ -z "$TARGET" ]; then
    echo "TARGET_DIR is required; pass the active agent skills directory explicitly." >&2
    exit 1
fi
if [ "$REMOTE" = true ] && ! printf '%s' "$REMOTE_COMMIT" | grep -Eq '^[0-9a-fA-F]{40}$'; then
    echo "--remote requires --remote-commit with a full audited 40-character commit SHA." >&2
    exit 1
fi
if [ -e "$TARGET" ] && [ -L "$TARGET" ]; then
    echo "TARGET_DIR must not be a symlink: $TARGET" >&2
    exit 1
fi
assert_no_reparse_ancestor() {
    current="$1"
    while true; do
        if [ -L "$current" ]; then
            echo "Reparse point is not allowed: $current" >&2
            exit 1
        fi
        parent="$(dirname "$current")"
        [ "$parent" = "$current" ] && break
        current="$parent"
    done
}

assert_safe_source() {
    root="$1"
    while IFS= read -r -d '' item; do
        if [ -L "$item" ]; then
            echo "Source reparse point is not allowed: $item" >&2
            exit 1
        fi
        name="$(basename "$item" | tr '[:upper:]' '[:lower:]')"
        extension="${name##*.}"
        case "$name" in
            .env|.env.*|*.pem|*.key|*.p12|*.pfx|.npmrc|.pypirc|credentials.json|id_rsa)
                echo "Sensitive or secret-like source file is not installable: $item" >&2
                exit 1
                ;;
        esac
        if [ "$extension" = "env" ] || printf '%s' "$name" | grep -Eiq '(^|[._-])(auth|secrets?|credentials?|tokens?|passwords?|private)([._-]|$)|(secret|credential|token|password|private)$'; then
            echo "Sensitive or secret-like source file is not installable: $item" >&2
            exit 1
        fi
    done < <(find "$root" -mindepth 1 -print0)
}

assert_no_reparse_ancestor "$TARGET"
target_created=0
if [ ! -d "$TARGET" ]; then
    mkdir -p "$TARGET"
    target_created=1
fi
if [ ! -d "$TARGET" ]; then
    echo "TARGET_DIR is not a directory: $TARGET" >&2
    exit 1
fi
lock="$TARGET/.loop-install.lock"
if [ -e "$lock" ]; then
    if [ -L "$lock" ]; then
        echo "Installer lock must not be a symlink: $lock" >&2
        exit 1
    fi
    if [ "$RECOVER_STALE_LOCK" = true ]; then
        owner_file="$lock/owner.json"
        if [ ! -f "$owner_file" ]; then
            echo "Installer lock owner metadata is missing; review manually before recovery: $lock" >&2
            exit 1
        fi
        owner_pid="$(sed -n 's/.*"pid"[[:space:]]*:[[:space:]]*\([0-9][0-9]*\).*/\1/p' "$owner_file")"
        owner_host="$(sed -n 's/.*"host"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' "$owner_file")"
        if [ -z "$owner_pid" ] || [ -z "$owner_host" ]; then
            echo "Installer lock owner metadata is invalid; review manually before recovery: $lock" >&2
            exit 1
        fi
        if [ "$owner_host" != "$(hostname)" ]; then
            rm -rf "$lock"
        elif kill -0 "$owner_pid" 2>/dev/null; then
            echo "Installer lock owner is still running (PID $owner_pid)." >&2
            exit 1
        else
            rm -rf "$lock"
        fi
    else
        echo "Installer lock exists; verify no installer is running and use --recover-stale-lock only after review: $lock" >&2
        exit 1
    fi
fi
if ! mkdir "$lock" 2>/dev/null; then
    echo "Another installer is running or target is not writable: $lock" >&2
    exit 1
fi
printf '{"pid":%s,"host":"%s","started":"%s"}\n' "$$" "$(hostname)" "$(date -u +%s)" > "$lock/owner.json"
trap 'rm -rf "$lock"' EXIT

src="$SCRIPT_DIR/skills"
tmp=""
entries=()
stages=()
backups=()
installed=()
backup_root=""
committed=false
cleanup() {
    if [ "$committed" != true ]; then
        for i in "${!entries[@]}"; do
            destination="$TARGET/$(basename "${entries[$i]}")"
            if [ "${installed[$i]:-0}" = 1 ] && [ -e "$destination" ]; then
                rm -rf "$destination"
            fi
            if [ -n "${backups[$i]:-}" ] && [ -e "${backups[$i]}" ]; then
                mv "${backups[$i]}" "$destination"
            fi
        done
    fi
    for stage in "${stages[@]}"; do
        if [ -n "$stage" ] && [ -e "$stage" ]; then
            rm -rf "$stage"
        fi
    done
    if [ -n "$tmp" ] && [ -e "$tmp" ]; then
        rm -rf "$tmp"
    fi
    if [ -n "$backup_root" ] && [ -d "$backup_root" ]; then
        rmdir "$backup_root" 2>/dev/null || true
    fi
    rm -rf "$lock"
    if [ "$target_created" = 1 ] && [ -d "$TARGET" ]; then
        rmdir "$TARGET" 2>/dev/null || true
    fi
}
trap cleanup EXIT

for stale_stage in "$TARGET"/.loop-stage-*; do
    if [ -e "$stale_stage" ] || [ -L "$stale_stage" ]; then
        echo "Stale installer stage requires manual review before retrying: $stale_stage" >&2
        exit 1
    fi
done
if [ "$REMOTE" = true ]; then
    repo="XuanRuiMu/loop-engineering"
    tmp="$(mktemp -d)"
    url="https://github.com/$repo/archive/$REMOTE_COMMIT.tar.gz"
    curl -fsSL "$url" -o "$tmp/loop.tgz"
    tar -xzf "$tmp/loop.tgz" -C "$tmp"
    src="$tmp/loop-engineering-$REMOTE_COMMIT/skills"
else
    if [ "$ALLOW_DIRTY" != true ] && git -C "$SCRIPT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        if [ -n "$(git -C "$SCRIPT_DIR" status --porcelain)" ]; then
            echo "Source worktree is dirty; review it and pass --allow-dirty to install intentionally." >&2
            exit 1
        fi
    fi
fi
if [ ! -d "$src" ]; then
    echo "Skills directory not found: $src" >&2
    exit 1
fi
assert_no_reparse_ancestor "$src"
src_full="$(CDPATH= cd -- "$src" && pwd)"
target_full="$(CDPATH= cd -- "$TARGET" && pwd)"
case "$target_full/" in
    "$src_full"/*) echo "Source and target must not overlap: $src -> $TARGET" >&2; exit 1 ;;
esac
case "$src_full/" in
    "$target_full"/*) echo "Source and target must not overlap: $src -> $TARGET" >&2; exit 1 ;;
esac
assert_safe_source "$src"
while IFS= read -r -d '' entry; do
    [ -e "$entry" ] || continue
    [ "$(basename "$entry")" = "__pycache__" ] && continue
    if [ ! -d "$entry" ]; then
        echo "Managed skills must contain directories only: $entry" >&2
        exit 1
    fi
    if [ ! -f "$entry/SKILL.md" ]; then
        echo "Managed source entries must contain SKILL.md: $entry" >&2
        exit 1
    fi
    destination="$TARGET/$(basename "$entry")"
    if [ -L "$destination" ]; then
        echo "Managed destination must not be a symlink: $destination" >&2
        exit 1
    fi
    if [ -e "$destination" ] && [ ! -d "$destination" ]; then
        echo "Managed destination must be a directory: $destination" >&2
        exit 1
    fi
    if [ -e "$destination" ] && [ "$FORCE" != true ]; then
        echo "Destination exists; use --force to replace managed skill entry: $destination" >&2
        exit 1
    fi
    if [ -e "$destination" ] && [ "$FORCE" = true ]; then
        marker="$destination/.loop-managed"
        if [ ! -f "$marker" ] || [ "$(cat "$marker")" != "$MANAGED_MARKER" ]; then
            echo "Refusing to overwrite an unmarked or foreign destination: $destination" >&2
            exit 1
        fi
    fi
    entries+=("$entry")
    stage="$(mktemp -d "$TARGET/.loop-stage-XXXXXX")"
    cp -r "$entry/." "$stage/"
    find "$stage" -type d -name '__pycache__' -prune -exec rm -rf {} +
    find "$stage" -type f -name '*.pyc' -delete
    printf '%s\n' "$MANAGED_MARKER" > "$stage/.loop-managed"
    stages+=("$stage")
    backups+=("")
    installed+=(0)
done < <(find "$src" -mindepth 1 -maxdepth 1 -print0)
backup_root="$(mktemp -d "$(dirname "$TARGET")/.loop-backups-XXXXXX")"
for i in "${!entries[@]}"; do
    destination="$TARGET/$(basename "${entries[$i]}")"
    if [ -e "$destination" ]; then
        backups[$i]="$backup_root/$(basename "${entries[$i]}")"
        mv "$destination" "${backups[$i]}"
    fi
done
for i in "${!entries[@]}"; do
    destination="$TARGET/$(basename "${entries[$i]}")"
    mv "${stages[$i]}" "$destination"
    stages[$i]=""
    installed[$i]=1
done
committed=true
for backup in "${backups[@]}"; do
    if [ -n "$backup" ] && [ -e "$backup" ]; then
        if [ "$PURGE_BACKUPS" = true ]; then
            rm -rf "$backup"
        else
            echo "Retained recoverable backup: $backup"
        fi
    fi
done
if [ "$PURGE_BACKUPS" = true ]; then
    for backup_directory in "$(dirname "$TARGET")"/.loop-backups-*; do
        if [ -d "$backup_directory" ]; then
            rm -rf "$backup_directory"
        fi
    done
fi

echo "Copied managed skills to $TARGET. Runtime reload/load verification is not implied."
