---
name: git-vault-sync
description: "Sync Git-backed vaults via hooks, cron, or manual workflows."
version: 1.0.0
platforms: [linux, macos, windows]
tags: [git, sync, vault, obsidian, hooks, cron, automation]
---

# Git-Backed Vault Sync

Many users store their knowledge vault (Obsidian, Foam, custom notes) in a Git repository for version history, backup, and multi-device sync. This skill covers three sync strategies with trade-offs.

## Strategy Comparison

| Strategy | Mechanism | Pros | Cons | Best For |
|----------|-----------|------|------|----------|
| **Event-driven Git Hooks** | `post-commit` push, `post-merge` pull | Zero polling, instant sync, no overhead | Requires git CLI, hooks not synced via git | Single-user, primary device |
| **Periodic Cron** | Scheduled `git pull --rebase && git push` | Works everywhere, no hook setup | Polling overhead, delay, conflicts possible | Shared vaults, headless servers, CI |
| **Manual** | Run `git sync` alias when needed | Full control, no surprises | Human-dependent | Infrequent changes, paranoid users |

---

## 1. Event-Driven Git Hooks (Recommended)

### Hook Files (place in `.git/hooks/`, `chmod +x`)

#### `post-commit` — Auto-push after local commit
```bash
#!/bin/bash
# Runs after every successful commit
git push origin main 2>/dev/null || git push origin master 2>/dev/null
```

#### `post-merge` — Auto-pull after `git pull` or merge
```bash
#!/bin/bash
# Runs after git pull / merge completes
git pull --rebase origin main 2>/dev/null || git pull --rebase origin master 2>/dev/null
```

#### `pre-push` — Optional pre-push checks
```bash
#!/bin/bash
# Runs before push; exit non-zero to abort
# Example: validate note format, run linter
exit 0
```

### Installation
```bash
VAULT_PATH="/path/to/vault"
cd "$VAULT_PATH"
chmod +x .git/hooks/post-commit .git/hooks/post-merge .git/hooks/pre-push
```

### Notes
- Hooks live in `.git/hooks/` — **not tracked by git**. Re-install on each clone.
- For team vaults: commit hook templates to `.githooks/` and use `git config core.hooksPath .githooks`
- `post-commit` runs after commit message editor closes — push is async from user perspective
- `post-merge` runs after `git pull` but NOT after `git fetch` alone

---

## 2. Periodic Cron Sync (Hermes cronjob)

### Sync Script Template (`scripts/vault-sync.sh`)
```bash
#!/bin/bash
set -e
VAULT_PATH="${VAULT_PATH:-$HOME/obsidian-vault}"
cd "$VAULT_PATH"

# Commit local changes if any
if [[ -n $(git status --porcelain) ]]; then
    git add -A
    git commit -m "Auto-sync: $(date '+%Y-%m-%d %H:%M:%S')"
fi

# Pull remote (rebase local on top)
git pull --rebase origin main 2>/dev/null || git pull --rebase origin master 2>/dev/null

# Push
git push origin main 2>/dev/null || git push origin master 2>/dev/null
```

### Create Cron Job (Hermes)
```python
cronjob(action="create", name="vault-sync", schedule="every 1h", script="vault-sync.sh", no_agent=True)
```

### Schedule Guidelines
- `every 15m` — High-frequency collaboration
- `every 1h` — Standard single-user
- `every 6h` — Low-churn backup vault
- `0 3 * * *` — Nightly (cron syntax)

---

## 3. Manual Sync Alias

Add to shell config (`.bashrc`, `.zshrc`):
```bash
alias vault-sync='cd ~/obsidian-vault && git pull --rebase && git push'
alias vault-status='cd ~/obsidian-vault && git status'
```

---

## Vault Path Detection

```bash
# 1. Env var (highest priority)
if [[ -n "$OBSIDIAN_VAULT_PATH" ]]; then
    VAULT_PATH="$OBSIDIAN_VAULT_PATH"
# 2. Default Obsidian location
elif [[ -d "$HOME/Documents/Obsidian Vault" ]]; then
    VAULT_PATH="$HOME/Documents/Obsidian Vault"
# 3. Any git repo with .obsidian/ folder
else
    VAULT_PATH=$(find ~ -maxdepth 3 -name ".obsidian" -type d 2>/dev/null | head -1 | xargs dirname)
fi

# Validate
if [[ -d "$VAULT_PATH/.git" && -d "$VAULT_PATH/.obsidian" ]]; then
    echo "Git-backed Obsidian vault: $VAULT_PATH"
else
    echo "Not a git-backed Obsidian vault"
fi
```

---

## Common Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| Push rejected (non-fast-forward) | Remote has commits you don't | `git pull --rebase` then push |
| Hook not running | Not executable / wrong path | `chmod +x .git/hooks/*` |
| Merge conflicts on pull | Local + remote both changed same file | Resolve manually, `git rebase --continue` |
| Duplicate commits | Hook pushes, cron also pushes | Use ONE strategy, not both |
| Auth fails in cron | No credential helper in non-interactive shell | Use token in remote URL or `git config credential.helper store` |

---

## References
- `references/git-hooks.md` — Ready-to-use hook templates
- `references/sync-script.md` — Full-featured sync script with logging, conflict detection
- `references/cron-setup.md` — Hermes cronjob examples for vault sync