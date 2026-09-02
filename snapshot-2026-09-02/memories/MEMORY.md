When user grants permission to push code to GitHub, push the complete project (users prefer bulk file access over file-by-file reads). Never push without explicit permission.
§
User's Telegram bot: @inurepricebot, token: 8922929401:***. Deployed on Railway.app. Repo: hermestel/gold-price-bot
§
SoundCloud bot @soundcloud_dl_bot (inure_soundcloudbot): token 8912423296:*** in /data/workspace/soundcloud-bot/.env (do NOT pass BOT_TOKEN on cmdline -> InvalidToken crash). Modular bot.py/config.py/services/{soundcloud.py,downloader.py}/sessions.py. Run (bg): cd /data/workspace/soundcloud-bot && python3 bot.py. User 7747086163 gates via ALLOWED_USER_IDS. Fixes: downloader outtmpl w/o ext + glob fallback; playlist API returns only first tracks' metadata -> fetch rest via /tracks/{id} parallel; on.soundcloud.com short links via HEAD redirect. User regretted over-engineering a search filter — keep simple.
§
Second brain / Obsidian: /data/obsidian-vault from github.com/hermesbackup2/obsidian. Store notes there, NOT in /data (disk limited). Shared with another Hermes agent. Helper: /data/.hermes/scripts/save_to_brain.sh (git pull --rebase then push).
§
User is a capable Python developer who writes their own modular code (services/, config.py, sessions.py separation). Values clean architecture, async/threading correctness, and structured logging. When reviewing their code, focus on real bugs (NameError, syntax) and architectural issues, not over-engineering.
§
WORKING STYLE: (1) On 'fix/build X', DO THE WHOLE THING and report ONCE at the end — no intermediate 'working on it'/'step N' messages (user said so repeatedly, Farsi). (2) Do NOT over-engineer; ship the simple working version (user: 'ولش کن رباتو فقط روشن کن پشیمون شدم' re a search filter). (3) Don't store files in /data (~434MB) — use the GitHub repos.
§
User asked to send SoundCloud bot files to another Hermes instance, wanting full context transfer (not just code). User agreed to write a SKILL.md for the bot to ensure knowledge transfer.