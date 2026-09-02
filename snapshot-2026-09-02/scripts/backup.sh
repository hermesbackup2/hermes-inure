#!/bin/bash
# Hermes Agent daily backup — pushes critical state to GitHub
set -euo pipefail

REPO_DIR="/data/hermes-backup"
REMOTE="https://github.com/hermesbackup2/hermes-inure.git"
CRED_FILE="/data/.hermes/scripts/.git-credentials-backup"

# --- git config for this repo ---
export GIT_CONFIG_GLOBAL="/dev/null"
export GIT_CONFIG_SYSTEM="/dev/null"

# --- clone or init ---
if [ ! -d "$REPO_DIR/.git" ]; then
    rm -rf "$REPO_DIR"
    git -c credential.helper="store --file=$CRED_FILE" clone "$REMOTE" "$REPO_DIR" 2>&1 || {
        mkdir -p "$REPO_DIR"
        cd "$REPO_DIR"
        git init
        git remote add origin "$REMOTE"
    }
fi

cd "$REPO_DIR"

# git identity
git config user.email "hermes@backup"
git config user.name "Hermes Backup"

# pull latest first
git -c credential.helper="store --file=$CRED_FILE" pull --rebase origin main 2>/dev/null || \
git -c credential.helper="store --file=$CRED_FILE" pull --rebase origin master 2>/dev/null || true

# --- cleanup old snapshots ---
rm -rf snapshot-*

# --- snapshot critical files ---
SNAP="snapshot-$(date +%Y-%m-%d)"
mkdir -p "$SNAP"

# config + soul
cp /data/.hermes/config.yaml "$SNAP/" 2>/dev/null || true
cp /data/.hermes/SOUL.md "$SNAP/" 2>/dev/null || true

# memories
cp -r /data/.hermes/memories "$SNAP/memories" 2>/dev/null || true

# user-created skills only (skip bundled skills/)
mkdir -p "$SNAP/skills"
find /data/.hermes/skills -maxdepth 2 -name "SKILL.md" -exec grep -l "bundled" {} \; 2>/dev/null || true
# Copy all skill dirs but NOT their large nested content
for d in /data/.hermes/skills/*/; do
    dirname=$(basename "$d")
    [ "$dirname" = ".hub" ] && continue
    [ "$dirname" = "skills" ] && continue  # skip nested duplicate
    mkdir -p "$SNAP/skills/$dirname"
    cp "$d"SKILL.md "$SNAP/skills/$dirname/" 2>/dev/null || true
    cp "$d"DESCRIPTION.md "$SNAP/skills/$dirname/" 2>/dev/null || true
done

# cron jobs
cp /data/.hermes/cron/jobs.json "$SNAP/" 2>/dev/null || true

# scripts (flat copy, no recursion into subdirs of scripts/)
mkdir -p "$SNAP/scripts"
for f in /data/.hermes/scripts/*; do
    [ -f "$f" ] && cp "$f" "$SNAP/scripts/" 2>/dev/null || true
done

# hooks
cp -r /data/.hermes/hooks "$SNAP/hooks" 2>/dev/null || true

# profiles
cp -r /data/.hermes/profiles "$SNAP/profiles" 2>/dev/null || true

# soundcloud bot code
mkdir -p "$SNAP/soundcloud-bot/services"
cp /data/workspace/soundcloud-bot/{bot.py,config.py,sessions.py} "$SNAP/soundcloud-bot/" 2>/dev/null || true
cp /data/workspace/soundcloud-bot/services/{__init__.py,soundcloud.py,downloader.py} "$SNAP/soundcloud-bot/services/" 2>/dev/null || true

# obsidian vault state
mkdir -p "$SNAP/obsidian-vault"
cd /data/obsidian-vault 2>/dev/null && git log --oneline -1 > "/data/hermes-backup/$SNAP/obsidian-vault/last-commit.txt" 2>/dev/null || true
cd "$REPO_DIR"

# commit & push
git add -A
if git diff --cached --quiet; then
    echo "No changes to commit."
else
    git commit -m "Backup: $SNAP $(date +%H:%M:%S)"
    git -c credential.helper="store --file=$CRED_FILE" push origin main 2>/dev/null || \
    git -c credential.helper="store --file=$CRED_FILE" push origin master 2>/dev/null
    echo "Pushed: $SNAP"
fi
