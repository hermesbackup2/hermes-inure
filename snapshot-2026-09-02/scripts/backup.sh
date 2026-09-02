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
        # if remote is empty, init manually
        mkdir -p "$REPO_DIR"
        cd "$REPO_DIR"
        git init
        git remote add origin "$REMOTE"
    }
fi

cd "$REPO_DIR"

# pull latest first
git -c credential.helper="store --file=$CRED_FILE" pull --rebase origin main 2>/dev/null || \
git -c credential.helper="store --file=$CRED_FILE" pull --rebase origin master 2>/dev/null || true

# --- snapshot critical files ---
SNAP="snapshot-$(date +%Y-%m-%d)"
mkdir -p "$SNAP"

# config
cp /data/.hermes/config.yaml "$SNAP/" 2>/dev/null || true
cp /data/.hermes/SOUL.md "$SNAP/" 2>/dev/null || true

# memories
cp -r /data/.hermes/memories "$SNAP/memories" 2>/dev/null || true

# skills (user-created, not plugin)
cp -r /data/.hermes/skills "$SNAP/skills" 2>/dev/null || true

# cron jobs definition
cp /data/.hermes/cron/jobs.json "$SNAP/" 2>/dev/null || true

# scripts
cp -r /data/.hermes/scripts "$SNAP/scripts" 2>/dev/null || true

# hooks
cp -r /data/.hermes/hooks "$SNAP/hooks" 2>/dev/null || true

# user profile
cp -r /data/.hermes/profiles "$SNAP/profiles" 2>/dev/null || true

# soundcloud bot code (workspace copy)
mkdir -p "$SNAP/soundcloud-bot"
cp /data/workspace/soundcloud-bot/{bot.py,config.py,sessions.py} "$SNAP/soundcloud-bot/" 2>/dev/null || true
cp -r /data/workspace/soundcloud-bot/services "$SNAP/soundcloud-bot/" 2>/dev/null || true

# obsidian vault state
mkdir -p "$SNAP/obsidian-vault"
cd /data/obsidian-vault 2>/dev/null && git log --oneline -1 > "/data/hermes-backup/$SNAP/obsidian-vault/last-commit.txt" 2>/dev/null || true
cd "$REPO_DIR"

# cleanup old snapshots (keep last 7)
ls -d snapshot-* 2>/dev/null | sort -r | tail -n +8 | xargs rm -rf 2>/dev/null || true

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
