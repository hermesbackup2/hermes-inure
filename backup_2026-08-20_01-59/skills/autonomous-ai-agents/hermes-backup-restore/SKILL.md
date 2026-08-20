---
name: hermes-backup-restore
description: Use when backing up/restoring Hermes state via GitHub repos.
---

# Hermes Backup & Restore

Snapshot critical `~/.hermes` state into a git repo (e.g. `github.com/<user>/hermes-backup`) and restore it on a fresh environment. Proven pattern from a live deployment: timestamped snapshot directories `backup_YYYY-MM-DD_HH-MM/` pushed to a private repo, plus a `no_agent` cron job running the push every 24h.

## Backup side

1. Keep a local clone of the backup repo (e.g. `~/hermes-backup`).
2. Each run creates `backup_$(date +%Y-%m-%d_%H-%M)/` inside the clone and copies the critical state in (see "What a snapshot contains").
3. Strip `*.lock` files from the snapshot (transient).
4. Write a `MANIFEST.md` (item list + sizes) inside the snapshot.
5. Commit as `Hermes Backup <backup@hermes-agent>` and push over HTTPS. Do NOT use SSH — these hosts commonly have port 22 closed.
6. Reference implementation: `scripts/backup.sh` — install it to `~/.hermes/scripts/backup.sh`.

### What a snapshot contains
Files: `SOUL.md`, `auth.json`, `channel_directory.json`, `config.yaml`, `gateway_state.json`, `kanban.db`, `state.db`.
Dirs: `cron`, `hooks`, `memories`, `pairing`, `platforms`, `sessions`, `skills`, `state`, `logs`.
Deliberately excluded: `.env` (API keys/secrets) — only include with explicit user consent, even in a private repo.

### Push credentials (HTTPS-only environments)
- Write the PAT once to a dedicated credential-store file, e.g. `~/.hermes/scripts/.git-credentials-backup`, containing `https://<user>:<token>@github.com`; `chmod 600`.
- In the clone: `git config credential.helper "store --file=.../.git-credentials-backup"`.
- Never paste the token into shell commands — the security scanner flags it and it leaks into logs. If the user pasted a PAT in chat, recommend rotating it (revoke + new token; update only the creds file).

### Recurring cron job
- Create with `cronjob(action=create, no_agent=true, script="backup.sh", schedule="every 24h", name="hermes-backup-24h")`.
- PITFALL: `script` must be a RELATIVE filename resolved under `~/.hermes/scripts/` — absolute or `~/` paths are rejected by the cronjob tool.
- Test immediately: `cronjob(action=run, job_id=...)`, then verify REMOTELY via GitHub API `GET /repos/<owner>/<repo>/commits?per_page=3` — confirm the newest commit message `backup: <stamp>`. Local git success alone is not proof of upload.
- `no_agent=true` delivers the script's stdout verbatim to the origin chat; empty stdout = silent success.

## Restore side

1. Clone the backup repo (token via credential store, same as above).
2. Pick the latest snapshot dir; read its `MANIFEST.md`.
3. Memories: `cp memories/MEMORY.md memories/USER.md ~/.hermes/memories/` (backup is the source of truth here — overwrite).
4. Custom skills: `diff -rq <snap>/skills <live>/skills` and copy ONLY the dirs listed as "Only in <backup>" — never blindly copy the whole skills tree over the live one.
5. `config.yaml`: DIFF first. A stale backup may lack newer keys (`_config_version`, `platforms`, etc.). Keep the live config unless the user explicitly wants the backup's.
6. Session history: do NOT replace the live `state.db` (the gateway holds it open). Merge instead — see `scripts/merge_state.py`. Sessions use TEXT ids (no collision, `INSERT OR IGNORE`); messages use INTEGER ids (remap by `+max(local id)`); FTS triggers auto-index inserted rows. Verify with a `MATCH` query and `session_search`.
7. Cron jobs from the backup (`cron/jobs.json`) are not auto-restored — recreate with `cronjob(action=create)` as needed.

## Pitfalls
- Never copy a DB file over another live DB file — SQLite merge only (open fds, FTS rebuild).
- `state.db` schemas evolve between versions; derive column lists via `PRAGMA table_info` at runtime instead of hard-coding them.
- Keep the backup tooling itself (`backup.sh`) in the repo root so a fresh clone is self-documenting.
- The backup routine is user-critical: after any change to the script or creds, run a test backup and confirm the commit landed before declaring success.

## Support files (in this skill directory)
- `scripts/backup.sh` — the exact `no_agent` script installed to `~/.hermes/scripts/backup.sh` and wired via `cronjob(script="backup.sh")`.
- `scripts/merge_state.py` — merge a backup `state.db` into the live one (usage: `python3 merge_state.py <backup_state.db> [live_state.db]`).
