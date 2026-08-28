#!/usr/bin/env bash
# Hermes periodic backup -> private GitHub repo. HTTPS push only (port 22 closed on these hosts).
# Install to ~/.hermes/scripts/backup.sh and wire as a no_agent cron job (script="backup.sh").
# Credentials: read from git credential store file — never embedded in commands/logs.
# Override paths via env: HERMES_HOME, REPO_DIR, CREDS_FILE.
set -euo pipefail
export GIT_TERMINAL_PROMPT=0

HERMES_HOME="${HERMES_HOME:-${HOME}/.hermes}"
REPO_DIR="${REPO_DIR:-${HOME}/hermes-backup}"
CREDS_FILE="${CREDS_FILE:-${HERMES_HOME}/scripts/.git-credentials-backup}"
STAMP="$(date +%Y-%m-%d_%H-%M)"
SNAP="${REPO_DIR}/backup_${STAMP}"

[ -d "${REPO_DIR}/.git" ] || { echo "ERROR: backup repo not cloned at ${REPO_DIR}"; exit 1; }
[ -f "${CREDS_FILE}" ] || { echo "ERROR: git credentials file missing (${CREDS_FILE})"; exit 1; }

mkdir -p "${SNAP}"

# ---- copy critical Hermes state ----
for item in SOUL.md auth.json channel_directory.json config.yaml gateway_state.json kanban.db; do
  [ -e "${HERMES_HOME}/${item}" ] && cp -a "${HERMES_HOME}/${item}" "${SNAP}/"
done
for dir in cron hooks memories pairing platforms sessions skills state logs; do
  [ -d "${HERMES_HOME}/${dir}" ] && cp -a "${HERMES_HOME}/${dir}" "${SNAP}/"
done
[ -f "${HERMES_HOME}/state.db" ] && cp -a "${HERMES_HOME}/state.db" "${SNAP}/"

# NOTE: .env (API keys) is intentionally NOT backed up — secrets stay out of the repo.

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
git add -A
if git diff --cached --quiet; then
  echo "Nothing new to back up."
  exit 0
fi
git commit -q -m "backup: ${STAMP}"
git push -q origin HEAD
echo "Hermes backup uploaded: backup_${STAMP}"
