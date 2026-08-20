Hermes backup cron job: every 24h (job "hermes-backup-24h"), no_agent script /data/.hermes/scripts/backup.sh, snapshots pushed to github.com/hermestel/hermes-backup (local clone /data/hermes-backup, HTTPS only — port 22 closed, token in .git-credentials-backup). Bundle "abzar" created at /data/.hermes/skill-bundles/abzar.yaml (net-checker-iran + ip-security-analyzer). Utilities project (Next.js security dashboard) at /data/workspace/utilities/ — /data partition is only 434MB, node_modules must be installed elsewhere (use /tmp symlink).
§
When user grants permission to push code to GitHub, push the complete project (users prefer bulk file access over file-by-file reads). Never push without explicit permission.
§
User's Telegram bot: @inurepricebot, token: 8922929401:***. Deployed on Railway.app. Repo: hermestel/gold-price-bot
§
SoundCloud bot @soundcloud_dl_bot: token in .env (run `python3 bot.py` without overriding BOT_TOKEN to avoid InvalidToken). Modular at /data/workspace/soundcloud-bot/ (services/downloader.py needs glob fallback for yt-dlp FFmpegExtractAudio).
§
Prefers git hooks over cron for Obsidian vault sync (post-commit push, post-merge pull). Chose option 2 when offered.
§
Obsidian vault at /data/obsidian-vault cloned from hermestel/obsidian-vault. Git hooks configured for auto-sync: post-commit (push), post-merge (pull --rebase). GitHub account hermestel currently suspended (403 on push).
§
GitHub hermestel suspended (erroneous IP flag, Iran+VPN). OFAC license permits public+private for Iran users. Appeal filed as 'flagged in error, individual, not SDN'. Do NOT make repos public to fix. Cannot push until resolved.
§
User is a capable Python developer who writes their own modular code (services/, config.py, sessions.py separation). Values clean architecture, async/threading correctness, and structured logging. When reviewing their code, focus on real bugs (NameError, syntax) and architectural issues, not over-engineering.