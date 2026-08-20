#!/usr/bin/env bash
# Hermes daily backup -> https://github.com/hermesbackup2/hermes-inure (private)
# Runs as a no_agent cron job every 24h. HTTPS push only (port 22 is closed on this host).
# Credentials: read from git credential store (never embedded in commands/logs).
set -euo pipefail
export GIT_TERMINAL_PROMPT=0

HERMES_HOME="${HOME}/.hermes"
REPO_DIR="${HOME}/hermes-backup"
CREDS_FILE="${HERMES_HOME}/scripts/.git-credentials-backup"
STAMP="$(date +%Y-%m-%d_%H-%M)"
SNAP="${REPO_DIR}/backup_${STAMP}"

[ -d "${REPO_DIR}/.git" ] || { echo "ERROR: backup repo not cloned at ${REPO_DIR}"; exit 1; }
[ -f "${CREDS_FILE}" ] || { echo "ERROR: git credentials file missing (${CREDS_FILE})"; exit 1; }

mkdir -p "${SNAP}"

# ---- copy critical Hermes state (excluding state.db to avoid GitHub secret scanning push protection) ----
for item in SOUL.md auth.json channel_directory.json config.yaml gateway_state.json kanban.db; do
  [ -e "${HERMES_HOME}/${item}" ] && cp -a "${HERMES_HOME}/${item}" "${SNAP}/"
done
for dir in cron hooks memories pairing platforms sessions skills state logs; do
  [ -d "${HERMES_HOME}/${dir}" ] && cp -a "${HERMES_HOME}/${dir}" "${SNAP}/"
done

# NOTE: .env and state.db (which might contain chat tokens/secrets) are intentionally NOT backed up.

# strip transient lock files from the snapshot
find "${SNAP}" -name '*.lock' -delete 2>/dev/null || true

# ---- MANIFEST ----
{
  echo "# Hermes Backup - ${STAMP}"
  echo
  echo "## Included:"
  du -sh "${SNAP}"/* 2>/dev/null | sed "s|${SNAP}/||; s|^|- |"
  echo
  echo "Total backup size:"
  du -sh "${SNAP}" 2>/dev/null | awk '{print $1}'
} > "${SNAP}/MANIFEST.md"

# keep the backup tooling itself in the repo root
cp "${BASH_SOURCE[0]}" "${REPO_DIR}/backup.sh"

# ---- commit & push (HTTPS via credential store) ----
cd "${REPO_DIR}"
git rm -rf . >/dev/null 2>&1 || true
# Re-copy latest backup into repo root/subdirs or keep separate backup_STAMP dirs.
# The standard script creates backup_STAMP dirs. Let's clean up old uncommitted/failed attempts:
git reset --hard HEAD >/dev/null 2>&1 || true
git clean -fd >/dev/null 2>&1 || true

# Re-run snapshot logic cleanly
rm -rf "${SNAP}"
mkdir -p "${SNAP}"
for item in SOUL.md auth.json channel_directory.json config.yaml gateway_state.json kanban.db; do
  [ -e "${HERMES_HOME}/${item}" ] && cp -a "${HERMES_HOME}/${item}" "${SNAP}/"
done
for dir in cron hooks memories pairing platforms sessions skills state logs; do
  [ -d "${HERMES_HOME}/${dir}" ] && cp -a "${HERMES_HOME}/${dir}" "${SNAP}/"
done
find "${SNAP}" -name '*.lock' -delete 2>/dev/null || true

{
  echo "# Hermes Backup - ${STAMP}"
  echo
  echo "## Included:"
  du -sh "${SNAP}"/* 2>/dev/null | sed "s|${SNAP}/||; s|^|- |"
  echo
  echo "Total backup size:"
  du -sh "${SNAP}" 2>/dev/null | awk '{print $1}'
} > "${SNAP}/MANIFEST.md"
cp "${BASH_SOURCE[0]}" "${REPO_DIR}/backup.sh"

git add -A
if git diff --cached --quiet; then
  echo "Nothing new to back up."
  exit 0
fi
git commit -q -m "backup: ${STAMP}"
git push -q origin HEAD
echo "✅ Hermes backup uploaded: backup_${STAMP}"
