# Hermes Cronjob Examples for Vault Sync

Hermes `cronjob` tool with `no_agent=true` runs scripts directly — no LLM overhead, perfect for sync.

---

## Basic Vault Sync Cron

```python
# Create hourly sync for vault at /data/obsidian-vault
cronjob(action="create",
        name="obsidian-vault-sync",
        schedule="every 1h",
        script="vault-sync.sh",
        no_agent=True,
        workdir="/data/obsidian-vault")
```

**Requirements:**
- `vault-sync.sh` in `~/.hermes/scripts/` (or vault's `scripts/`)
- `workdir` sets cwd, script uses `VAULT_PATH` env or detects

---

## With Explicit VAULT_PATH

```python
cronjob(action="create",
        name="vault-sync",
        schedule="every 1h",
        script="vault-sync.sh",
        no_agent=True,
        workdir="/data/obsidian-vault")
# Script reads VAULT_PATH from workdir automatically
```

---

## Multiple Vaults

```python
# Personal notes
cronjob(action="create",
        name="notes-sync",
        schedule="every 1h",
        script="vault-sync.sh",
        no_agent=True,
        workdir="$HOME/notes")

# Team wiki
cronjob(action="create",
        name="wiki-sync",
        schedule="every 30m",
        script="vault-sync.sh",
        no_agent=True,
        workdir="/data/team-wiki")

# Config dotfiles
cronjob(action="create",
        name="dotfiles-sync",
        schedule="every 6h",
        script="vault-sync.sh",
        no_agent=True,
        workdir="$HOME/dotfiles")
```

---

## Schedule Patterns

```python
# Every N minutes/hours
"every 15m"
"every 1h"
"every 6h"

# Cron syntax (full control)
"0 * * * *"      # Hourly at minute 0
"*/30 * * * *"   # Every 30 minutes
"0 3 * * *"      # Daily 3 AM
"0 3 * * 0"      # Weekly Sunday 3 AM
"0 3 1 * *"      # Monthly 1st day 3 AM

# One-shot (ISO timestamp)
"2026-08-03T14:30:00"
```

---

## Management Commands

```python
# List all jobs
cronjob(action="list")

# Pause/resume
cronjob(action="pause", job_id="...")
cronjob(action="resume", job_id="...")

# Run once manually
cronjob(action="run", job_id="...")

# Remove
cronjob(action="remove", job_id="...")

# Update schedule
cronjob(action="update", job_id="...", schedule="every 30m")
```

---

## Debugging

```bash
# View last run output (cronjob deliveries)
# Check Hermes logs:
tail -f ~/.hermes/logs/cron.log

# Or check specific job delivery
# (delivered to origin chat by default)

# Test script manually
VAULT_PATH=/data/obsidian-vault ~/.hermes/scripts/vault-sync.sh
```

---

## Common Issues

| Problem | Solution |
|---------|----------|
| `script not found` | Place `.sh` in `~/.hermes/scripts/` |
| `permission denied` | `chmod +x ~/.hermes/scripts/vault-sync.sh` |
| Auth fails in cron | Use token in remote URL: `https://TOKEN@github.com/user/repo.git` |
| Conflicts on pull | Script detects rebase, exits with instructions — resolve manually |
| Duplicate jobs | `cronjob list` then `remove` old ones |

---

## Token in Remote URL (for Cron)

```bash
# In vault
cd /data/obsidian-vault
git remote set-url origin https://ghp_xxx@github.com/hermestel/obsidian-vault.git
```

Or in script env:
```bash
export GIT_ASKPASS=echo
export GIT_TERMINAL_PROMPT=0
# Then use credential helper or token URL
```

---

## Best Practice: ONE Strategy Per Vault

**Don't mix hooks + cron on same vault** — causes duplicate commits, race conditions.

| Vault Type | Strategy |
|------------|----------|
| Personal, primary device | Git hooks (instant, zero overhead) |
| Headless server, shared | Cron (no interactive session needed) |
| Multiple devices, occasional | Manual alias or on-demand script |
| Team vault | Cron + shared hook templates (`.githooks/`) |