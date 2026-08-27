# Full-Featured Vault Sync Script

Save as `scripts/vault-sync.sh` in your vault or in `~/.hermes/scripts/`.

```bash
#!/bin/bash
# vault-sync.sh — Robust sync for Git-backed vaults (Obsidian, notes, configs)
# Usage: VAULT_PATH=/path/to/vault ./vault-sync.sh
# Cron:  0 * * * * VAULT_PATH=/path/to/vault /path/to/vault-sync.sh >> /var/log/vault-sync.log 2>&1

set -euo pipefail

# Configuration
VAULT_PATH="${VAULT_PATH:-${OBSIDIAN_VAULT_PATH:-$HOME/obsidian-vault}}"
REMOTE="${REMOTE:-origin}"
BRANCH_MAIN="${BRANCH_MAIN:-main}"
BRANCH_MASTER="${BRANCH_MASTER:-master}"
COMMIT_PREFIX="${COMMIT_PREFIX:-Auto-sync}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"  # DEBUG, INFO, WARN, ERROR

# Colors (only if TTY)
if [[ -t 1 ]]; then
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; BLUE=''; NC=''
fi

log() {
    local level="$1"; shift
    local msg="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    case "$level" in
        DEBUG) [[ "$LOG_LEVEL" == "DEBUG" ]] && echo -e "${BLUE}[$timestamp] DEBUG:${NC} $msg" ;;
        INFO)  [[ "$LOG_LEVEL" != "ERROR" && "$LOG_LEVEL" != "WARN" ]] && echo -e "${GREEN}[$timestamp] INFO:${NC} $msg" ;;
        WARN)  [[ "$LOG_LEVEL" != "ERROR" ]] && echo -e "${YELLOW}[$timestamp] WARN:${NC} $msg" ;;
        ERROR) echo -e "${RED}[$timestamp] ERROR:${NC} $msg" >&2 ;;
    esac
}

# Validate vault
if [[ ! -d "$VAULT_PATH" ]]; then
    log ERROR "Vault not found: $VAULT_PATH"
    exit 1
fi

if [[ ! -d "$VAULT_PATH/.git" ]]; then
    log ERROR "Not a git repository: $VAULT_PATH"
    exit 1
fi

cd "$VAULT_PATH"
log INFO "Syncing vault: $VAULT_PATH"

# Detect default branch
DEFAULT_BRANCH=$(git symbolic-ref refs/remotes/$REMOTE/HEAD 2>/dev/null | sed 's@^refs/remotes/.*/@@') || DEFAULT_BRANCH="$BRANCH_MAIN"
if ! git show-ref --verify --quiet "refs/heads/$DEFAULT_BRANCH"; then
    DEFAULT_BRANCH="$BRANCH_MASTER"
fi
log DEBUG "Using branch: $DEFAULT_BRANCH"

# 1. Commit local changes if any
if [[ -n $(git status --porcelain) ]]; then
    log INFO "Local changes detected, committing..."
    git add -A
    COMMIT_MSG="$COMMIT_PREFIX: $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$COMMIT_MSG"
    log INFO "Committed: $COMMIT_MSG"
else
    log DEBUG "No local changes to commit"
fi

# 2. Pull remote changes (rebase)
log INFO "Pulling from $REMOTE/$DEFAULT_BRANCH..."
if git pull --rebase "$REMOTE" "$DEFAULT_BRANCH"; then
    log INFO "Pull successful"
else
    log WARN "Pull failed (may be up to date or conflict)"
    # Check for rebase in progress
    if [[ -d ".git/rebase-merge" || -d ".git/rebase-apply" ]]; then
        log ERROR "Rebase in progress! Resolve conflicts manually:"
        log ERROR "  git status"
        log ERROR "  git add <resolved-files>"
        log ERROR "  git rebase --continue"
        exit 1
    fi
fi

# 3. Push local commits
log INFO "Pushing to $REMOTE/$DEFAULT_BRANCH..."
if git push "$REMOTE" "$DEFAULT_BRANCH"; then
    log INFO "Push successful"
else
    log ERROR "Push failed"
    exit 1
fi

log INFO "Sync complete ✓"
```

## Installation

```bash
# Option 1: In vault (recommended for portability)
VAULT_PATH="/path/to/vault"
cat > "$VAULT_PATH/scripts/vault-sync.sh" << 'EOF'
# ... paste script above ...
EOF
chmod +x "$VAULT_PATH/scripts/vault-sync.sh"

# Option 2: In Hermes scripts (for cron)
cat > ~/.hermes/scripts/vault-sync.sh << 'EOF'
# ... paste script above ...
EOF
chmod +x ~/.hermes/scripts/vault-sync.sh
```

## Cron Integration (Hermes)

```python
# Using Hermes cronjob tool
cronjob(action="create",
        name="vault-sync",
        schedule="every 1h",
        script="vault-sync.sh",
        no_agent=True,
        workdir="/path/to/vault")  # sets VAULT_PATH
```

Or with environment:
```python
cronjob(action="create",
        name="vault-sync",
        schedule="every 1h",
        script="vault-sync.sh",
        no_agent=True)
# Ensure VAULT_PATH is set in ~/.bashrc or cron env
```

## Features

| Feature | Description |
|---------|-------------|
| **Auto-detect branch** | Tries `main` then `master` |
| **Safe rebase** | Detects rebase conflicts, exits with instructions |
| **Idempotent** | No changes = no commit, clean pull/push |
| **Structured logging** | DEBUG/INFO/WARN/ERROR levels, timestamps |
| **Color output** | When run in TTY |
| **Config via env** | VAULT_PATH, REMOTE, BRANCH, LOG_LEVEL |
| **Exit codes** | 0=success, 1=error (cron-friendly) |

## Common Cron Schedules

```bash
# Every 15 minutes (high churn)
*/15 * * * *

# Hourly (standard)
0 * * * *

# Every 6 hours (low churn)
0 */6 * * *

# Nightly at 3 AM
0 3 * * *

# On boot + hourly
@reboot
0 * * * *
```