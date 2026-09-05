When user grants permission to push code to GitHub, push the complete project (users prefer bulk file access over file-by-file reads). Never push without explicit permission.
§
User's Telegram bot: @inurepricebot, token: 8922929401:***. Deployed on Railway.app. Repo: hermestel/gold-price-bot
§
SoundCloud bot @soundcloud_dl_bot (inure_soundcloudbot): token in .env (python-dotenv). Modular: bot.py/config.py/services/{soundcloud.py,downloader.py}/sessions.py. Run (bg): cd /data/workspace/soundcloud-bot && python3 bot.py. Code in TWO places: workspace (runtime+venv) + Obsidian vault notes/soundcloud-bot/code/ (source-of-truth on GitHub). ALLOWED_USER_IDS gates access. CRITICAL: When replacing module files (soundcloud.py, downloader.py), grep bot.py for ALL imports first — user-provided replacement code often missing functions bot.py needs. downloader.py is SYNC (download_track_audio(data, path)->bool), NOT async.
§
Obsidian vault: /data/obsidian-vault from irobsi/obsidian-valut. Backup: hermesbackup2/hermes-inure via backup.sh, cron every 24h. Both use git credential helpers (NOT embedded tokens — GitHub push protection blocks secrets). Bot code must be synced between workspace and vault.
§
User is a capable Python developer who writes their own modular code (services/, config.py, sessions.py separation). Values clean architecture, async/threading correctness, and structured logging. When reviewing their code, focus on real bugs (NameError, syntax) and architectural issues, not over-engineering.
§
WORKING STYLE: (1) DO THE WHOLE THING, report ONCE — no intermediate messages. (2) Do NOT over-engineer. (3) Use GitHub repos, not /data. (4) User writes their own code and provides COMPLETE replacement files — apply as-is, don't rewrite or 'improve' their code. (5) User gets furious at interruptions mid-task ('تموم کن دیگه کصکش چرا هی قطع میشی') — never stop to chat mid-execution.
§
SoundCloud bot: code vaulted in irobsi/obsidian-valut. Backup: hermes-inure repo.