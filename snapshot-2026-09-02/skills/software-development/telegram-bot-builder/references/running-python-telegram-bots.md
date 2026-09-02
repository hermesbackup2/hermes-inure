# Running an Existing python-telegram-bot (ops)

Pitfalls when starting / fixing a long-lived Telegram bot on a server:

- **Source of truth is `.env`, not the CLI.** If `config.py` loads env vars from `.env`, run the bot with `python3 bot.py` and let it load — do NOT pass `BOT_TOKEN=...` on the command line. A truncated/copied token causes `telegram.error.InvalidToken` and the process exits immediately. The real token lives in `.env`.
- **Keep it alive:** launch with `background=true` (or nohup). Then poll the process log for `Application started` / `run_polling` before declaring success. Don't assume it's running.
- **yt-dlp downloads:** when postprocessing to mp3, yt-dlp may write the final file with a different extension (`.m4a`, `.opus`) or a `%(ext)s` name. After download, glob the temp dir for the produced file and rename to the expected `.mp3` — a fixed `outtmpl` with `.mp3` will fail the existence check.
- **Large playlists (SoundCloud API v2):** `resolve` returns only the first ~4 tracks with full metadata; the rest come back as bare `{id}` stubs with `title: null`. Fetch missing track info in parallel (ThreadPoolExecutor, ~15 workers) before displaying, or the user only sees the first few tracks.
- **Short links:** SoundCloud share links use `on.soundcloud.com` (and `app.goo.gl`). `is_sc_url` must include these domains, and the resolver should follow the redirect (HEAD request) before calling the API, or the link is misclassified as a text search and returns "no results".
