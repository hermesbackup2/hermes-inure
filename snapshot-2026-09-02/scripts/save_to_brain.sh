#!/bin/bash
set -e
VAULT="/data/obsidian-vault"
cd "$VAULT"
if [[ -n $(git status --porcelain) ]]; then
    git add -A
    git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M:%S')"
fi
git pull --rebase origin main 2>/dev/null || git pull --rebase origin master 2>/dev/null
git push origin main 2>/dev/null || git push origin master 2>/dev/null
