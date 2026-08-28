---
name: telegram-bot-builder
description: "Build and run Telegram bots with python-telegram-bot."
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [Telegram, Bot, Python, API]
---

# Telegram Bot Builder

Build Telegram bots using Python and `python-telegram-bot`. Supports commands, inline keyboards, callback handlers, and multi-source API integration.

## When to Use

- User asks to build a Telegram bot
- User asks to create a bot for notifications, data fetching, or automation
- User asks to run a bot that shows live data (prices, news, etc.)

## Prerequisites

- Python 3.10+
- `pip install python-telegram-bot requests`
- A bot token from @BotFather
- For 24/7: Railway.app account (free $5/mo credit)

## How to Get a Bot Token

1. Open Telegram → go to **@BotFather**
2. Send `/newbot`
3. Choose a name (e.g., "My Bot")
4. Choose a username (must end in `bot`)
5. Copy the token (format: `123456:ABC-DEF...`)

## Quick Reference

| Task | Command/Code |
|---|---|
| Get token | @BotFather → `/newbot` |
| Run locally | `python3 bot.py` |
| Run background | `nohup python3 bot.py > bot.log 2>&1 &` |
| Deploy Railway | Push to GitHub → Railway → Deploy from repo |
| Set env var | Railway → Variables → `BOT_TOKEN` = value |
| Check logs | Railway → Logs tab |
| Revoke token | @BotFather → `/revoke` |

## Procedure

### 1. Create bot.py

Use this structure:
```python
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "YOUR_TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Button", callback_data="action")]]
    await update.message.reply_text("Hello!", reply_markup=InlineKeyboardMarkup(keyboard))

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    # handle q.data

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(callback_handler))
    app.run_polling()

if __name__ == "__main__":
    main()
```

### 2. Run Directly

```bash
python3 bot.py
```

The bot starts polling immediately. Ctrl+C to stop.

### 3. Run in Background (server)

```bash
nohup python3 bot.py > bot.log 2>&1 &
# or use screen/tmux for detachable session
```

### 4. Test

Send `/start` to the bot in Telegram.

### 5. Deploy to Railway (24/7)

**Files needed:**
- `requirements.txt` — list Python deps
- `Procfile` — contains: `worker: python3 bot.py`

**Steps:**
1. Push code to GitHub (**ASK USER FIRST**)
2. Go to railway.app → Sign in with GitHub
3. New Project → Deploy from GitHub repo
4. In Variables tab, add: `BOT_TOKEN` = user's token
5. Railway auto-deploys

**Railway environment variables:**
```
BOT_TOKEN=your-token-here
```

**Python version:** Railway defaults to Python 3.13. If needed, add `python_version="3.11"` to `nixpacks.toml`.

## Key Patterns

- **Inline keyboards**: `InlineKeyboardButton` + `CallbackQueryHandler`
- **Multi-source APIs**: Try multiple endpoints, merge results, use first successful
- **SoundCloud integration (2026-08 update): use `yt-dlp` as the PRIMARY downloader, NOT the direct API.** Pass the track's `permalink_url` to `yt-dlp` (format `bestaudio/best` + `FFmpegExtractAudio` mp3 192k). Reason: SoundCloud now serves most tracks ONLY as `cbc-encrypted-hls` / `ctr-encrypted-hls` transcodings with NO `progressive` entry, and the direct API's HLS can't be `ffmpeg -c copy`'d (missing DRM keys). `yt-dlp` handles all SoundCloud stream types from datacenter/VPS IPs WITHOUT the YouTube bot-block problem — **YouTube is blocked on servers, SoundCloud is not.** Keep `get_download_url` (direct `progressive` transcoding) only as a FALLBACK when `yt-dlp` fails. Working order in `download_track_audio(track_id, out_path)`: (1) `yt-dlp` on `permalink_url`; (2) if that fails, `get_download_url` → progressive. See `references/soundcloud-api.md` for client_id scraping, and `references/telegram-media-delivery.md` for playlist pagination, cover-art embedding (ID3 tags), and Telegram 50MB file limit + thumb parameter.
- **YouTube vs SoundCloud on Servers**: YouTube blocks nearly all datacenter/VPS IPs with "Sign in to confirm you're not a bot", and even with browser cookies (`cookies.txt`) it often fails due to geo/IP correlation. For Telegram music bots hosted on cloud servers, **avoid YouTube/YouTube Music entirely** and use **SoundCloud** as the primary source, as its API works reliably from VPS/datacenter IPs without bot blocks or cookies.
- **`spotdl` is NOT a YouTube workaround on servers.** `spotdl` pulls metadata from Spotify but downloads the actual audio from YouTube/YouTube Music — so it fails with the same "Sign in to confirm you're not a bot" error on datacenter IPs. Do not suggest `spotdl` as a YouTube replacement for a server-hosted bot; it inherits the exact YouTube block. Use SoundCloud directly instead.
- **Playlist pagination**: SoundCloud playlist API uses `next_href` for pagination — fetch all pages in a loop, then resolve missing track titles individually via `GET /tracks/<id>`. Template shows `send_playlist_page()` with ⬅️/➡️ navigation and `PAGE_SIZE` constant.
- **Playlist multi-select UX (user preference)**: Render each track as an `InlineKeyboardButton` with a ✅/⬜️ toggle (`callback_data="tgl_<idx>"`) so the user can select several tracks. Add a `☑️ انتخاب همه` (select all) button, a `🔲 لغو انتخاب همه` (deselect all) toggle, and a `⬇️ دانلود انتخاب‌شده‌ها (N)` button that downloads only the checked indices and delivers them one-by-one (see Pitfall #6). Store selections in `session['selected'] = set()` of track indices.
- **Batch ZIP download with chunking (FALLBACK only, not default UX)**: Previously the default for "download all", but the user REVERSED this — they now want one-by-one delivery (see Pitfall #6). Keep the ZIP chunking code only as a fallback when a single send would exceed Telegram's 50MB limit or for very large batches (>10 tracks). Pattern: download every track into a temp dir, embed cover art per-track, split into multiple ZIP files each under ~45MB, send via `reply_document(InputFile(...))`. See `references/telegram-media-delivery.md`.
- **Resilient batch downloads (user preference)**: Wrap EACH track download in its own try/except — if one track fails (not streamable, timeout, network error), skip it with `failed.append(title)` and `continue`, never cancel the whole batch. Send a final summary: `✅ X/Y آهنگ ارسال شد` plus the list of failed titles. Users explicitly expect partial success, not total failure.
- **Price formatting**: `f"{int(float(price)):,}"` for comma-separated Iranian numbers
- **Error handling**: Wrap each API call in try/except, log warnings, continue to next source
- **User-Agent header**: Some APIs block bare requests — always set `headers={"User-Agent": "Mozilla/5.0"}`
- **Timeout config for cloud**: Always set 30s timeouts when deploying to Railway/cloud:
  ```python
  app = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).connect_timeout(30).build()
  app.run_polling(drop_pending_updates=True)
  ```
- **Token via env var**: Never hardcode tokens. Use `os.environ.get("BOT_TOKEN")`

## Pitfalls

1. **Don't push bot code to GitHub with the token in it.** The token is a secret. If the repo is public, the token gets scraped and the bot gets hijacked.

2. **SoundCloud downloads: prefer `yt-dlp`, and DO NOT pre-filter by `policy`.** SoundCloud tags MOST tracks with `policy: MONETIZE`. That is NOT a DRM lock — `yt-dlp` downloads these fine. Never filter tracks by `policy` before attempting download; always attempt `yt-dlp` first and only report failure if the download genuinely fails.

3. **SoundCloud playlist pagination missing.** The `/resolve` endpoint only returns the first page of tracks (typically 20-50). The full playlist requires following `next_href` in a loop until exhausted. Then each track missing a title must be resolved individually via `GET /tracks/<id>`. The template `soundcloud_bot.py` implements this in `get_playlist_tracks()` and `send_playlist_page()`.

5. **`reply_audio()` parameter is `thumbnail`, not `thumb`.** In python-telegram-bot v20+, the `thumb` parameter was renamed to `thumbnail`. Using `thumb=` raises `TypeError: Message.reply_audio() got an unexpected keyword argument 'thumb'`. Always use `thumbnail=open(img_path, 'rb')`. For embedding cover art INTO the MP3 itself, use `mutagen` ID3 tags (APIC frame) — see `references/telegram-media-delivery.md`.

- **Playlist delivery: one-by-one, NOT ZIP (user preference, REVISED this session):** When the user selects multiple tracks from a playlist (via checkboxes) and hits "Download Selected", send EACH track as a separate `reply_audio` immediately after it finishes downloading — do NOT bundle into a ZIP. The earlier ZIP-bundling approach was explicitly rejected: user said "دکمه ZIP رو حذف کن... میخوام هر کدوم که کامل شد دونه دونه بفرسته". Remove any "download all as ZIP" button. Keep a progress line (`⏳ در حال دانلود (i/total): title`) and a final `✅ X/Y آهنگ ارسال شد` summary. ZIP chunking (in `references/telegram-media-delivery.md`) is now only a fallback for size/file-count limits, not the default UX.

22. **`download_track_audio` order: `yt-dlp` FIRST, then direct-API fallback.** The correct working order (proven this session on a datacenter/VPS bot): (1) `import yt_dlp`; build opts `{format:'bestaudio/best', outtmpl: out_path, postprocessors:[{key:'FFmpegExtractAudio', preferredcodec:'mp3', preferredquality:'192'}], quiet:True, no_warnings:True, http_headers:{'User-Agent':'Mozilla/5.0'}}`; `ydl.download([permalink_url])`. If the saved file exists and `> 5000` bytes, return True (handle yt-dlp renaming by checking `base+'.mp3'/'.m4a'/'.opus'` and `os.replace`). (2) FALLBACK only: `get_download_url` → a `progressive` transcoding's resolved `url` (must NOT end in `.m3u8`), stream with `requests`. The old guidance ("try progressive first, then yt-dlp") is REVERSED — `yt-dlp` is the reliable path for SoundCloud from servers. Do NOT attempt HLS+ffmpeg for encrypted streams (always fails). Do NOT pre-filter by `policy` (see Pitfall #2).

20. **Explicit duration formatting units (`unit='ms'` vs `unit='s'`).** SoundCloud API returns duration in milliseconds; YouTube/yt-dlp returns seconds. Never guess the unit by comparing `ms > 10000` (that fails on short/long edge cases). Pass an explicit parameter: `fmt_duration(value, unit="ms")` or `fmt_duration(value, unit="s")`.

5. **Don't create GitHub repos without user asking.** Build and run locally first. Only push when explicitly asked.

3. **Iranian APIs may be blocked from non-Iranian servers.** If running outside Iran, some APIs (tala.ir, sarafario.ir) will fail. Add multiple fallback sources.

4. **Bot stops when terminal closes.** Use `nohup`, `screen`, or `systemd` for persistent operation. Or deploy to Railway/VPS.

5. **python-telegram-bot v20+ uses async.** All handlers must be `async def`. Use `await` for API calls.

6. **Railway timeout errors (`httpx.ReadTimeout`).** Default timeouts are too short for cloud. Always set `read_timeout=30`, `write_timeout=30`, `connect_timeout=30`. Add `drop_pending_updates=True` to `run_polling()`.

7. **User wants direct execution, not instructions.** When user asks to build a bot, build and run it directly. Don't just provide code and say "run this yourself." If BotFather token is provided, wire it up and start the bot.

8. **Official vs market exchange rates.** International APIs (exchangerate-api.com) give official government rates, not open market rates. For Iranian market: official ~1,340,000 IRR/USD vs market ~1,890,000 IRR/USD. If accuracy matters, use Iranian APIs (only work from Iran) or show international prices (gold, silver) instead.

9. **Railway deployment workflow.** Push to GitHub → Railway auto-deploys → set `BOT_TOKEN` in Variables tab → wait 1-2 min. If bot crashes, check Logs tab. Common: missing env var, timeout errors, API blocked.

10. **Bot token security.** Never commit token to git. Always use `os.environ.get("BOT_TOKEN")`. If token leaked, revoke via @BotFather → `/revoke`.

11. **Background bot processes don't affect agent resources.** A Python bot running in `terminal(background=true)` is a separate OS process. It consumes server RAM/CPU but does NOT consume agent tokens or slow down the agent conversation. Safe to leave running. User can kill/restart on demand with a simple command.

12. **On-demand bot restart via agent.** Users may want to start/stop bots on demand rather than running 24/7. Store the bot's startup command in memory so the agent can restart it when asked. Pattern:
    - User says something like "ربات X رو روشن کن" (start bot X)
    - Agent looks up the command in memory and runs `terminal(background=true)` with `notify_on_complete=true`
    - User says "خاموشش کن" (shut it down)
    - Agent finds the process session_id and calls `process(action='kill')`
    - Store in memory: `Bot X: when user says "ربات X رو راه بنداز" auto-start /path/to/bot.py with token TOKEN via background terminal.`
    - This is safer than Railway for bots that don't need 24/7 uptime.

13. **Preserve existing features when extending a bot — don't rewrite from scratch.** If the user says "it used to do X" and the on-disk code lacks X, DO NOT assume the feature was never there. First check for git history, backups, or other copies before rewriting. This session the agent rewrote the SoundCloud bot and the user was frustrated that prior behavior (playlist list view, multi-select, single-track downloads) seemed "lost". Lesson: keep bot code in a git repo so features survive edits, and when extending, diff against the original rather than discarding it. Reconstructive rewrites silently drop uncommitted features.

14. **`mutagen` must be installed or cover art silently fails.** `add_cover_art_to_mp3` wraps the `mutagen` import in try/except; if `mutagen` is not pip-installed, the function returns `None` with only a `logger.warning` — the audio is sent WITHOUT cover art and no hard error surfaces. Always include `mutagen` in `requirements.txt`, or move the import to module top-level so a missing dep fails loudly at startup. Verify with: `python3 -c "import mutagen"`.

15. **`fmt_duration` must distinguish SoundCloud (ms) from YouTube (s).** SoundCloud's API returns `duration` in **milliseconds**; YouTube/yt-dlp returns **seconds**. Do NOT sniff `ms > 10000` to guess the unit — that mis-formats edge cases. Use an explicit `unit` parameter: `fmt_duration(value, unit="ms")` for SoundCloud, `fmt_duration(value, unit="s")` for YouTube. Same applies anywhere duration crosses the SC/YT boundary.

16. **`user_sessions` dict leaks memory on long-running bots.** A bare global dict keyed by `user_id` never expires — abandoned playlist/search sessions accumulate forever. Add a TTL cleanup: keep a parallel `_session_timestamps` dict, call `_touch_session(uid)` on every `handle_message` and `callback_handler` hit, and call `_cleanup_old_sessions()` (drop entries older than e.g. 1800s) at the top of `handle_message`. Log each eviction at INFO.

17. **Temp files: prefer `tempfile.TemporaryDirectory()` over `mkdtemp()` + manual `rmdir`.** With `mkdtemp()` you must `os.rmdir(tmp_dir)` in a `finally` block, and any early `continue`/`return` before cleanup can orphan files. Wrap the whole per-track loop body in `with tempfile.TemporaryDirectory() as tmp_dir:` so the directory (and everything written into it) is guaranteed gone when the block exits — even on exception. For `NamedTemporaryFile(delete=False)` you still `unlink` the specific file after sending, but the dir itself needs no manual removal.

18. **Production logging: log with context, not bare warnings.** For batch ops (playlist downloads) log at INFO the start/finish and at WARNING only genuinely skipped items with the track id and reason. Avoid `logger.exception` in user-facing handler paths (it dumps full tracebacks to logs on every transient network blip) — use `logger.warning(f"detail: {e}")` and reserve `logger.exception` for unexpected internal errors.

19. **Cache the SoundCloud `client_id` and degrade gracefully.** Scraping `window.__sc_hydration` from the homepage on every call is fragile (SoundCloud can change markup anytime). Cache it in-memory with a TTL (e.g. 3600s) AND on disk (`/tmp/sc_client_id.txt`) so restarts don't re-scrape. On scrape failure: `logger.error` the cause, then fall back to the stale cached id if present, and only raise a clear "SoundCloud may have changed its page structure" RuntimeError if no cache exists. See Pitfall #2 / `references/soundcloud-api.md`.

20. **YouTube downloads from datacenter/VPS IPs are frequently bot-blocked.** Even with a valid `cookies.txt` (exported from a logged-in browser), `yt-dlp` can still fail with "Sign in to confirm you're not a bot" because YouTube correlates the cookie's origin IP/geo with the server's datacenter IP. `player_client=['ios','android','mweb']` fallbacks help sometimes but are not reliable. If YouTube must work from a server, the robust path is either (a) a residential/IR proxy matching the cookie's geo, or (b) PoToken. Otherwise, prefer SoundCloud for music — its API works fine from datacenter IPs without cookies. Document this trade-off rather than silently failing.

24. **User writes their OWN modular bot code — review, don't rewrite, and STILL ship it.** A capable Python dev user may hand you their own refactored `bot.py` split into `config.py`, `sessions.py`, `services/`. When they say "review my code" or "I rewrote it, just review": (1) Do NOT overwrite their architecture with your single-file version — respect the modular layout. (2) Actually run the code mentally AND via `python3 -c "import ast; ast.parse(...)"` on each file; the user's draft almost always has small but fatal bugs: `logging.getLogger(name)` (should be `__name__`), `if name == "main":` (should be `if __name__ == "__main__":`), unclosed Markdown `**` (telegram raises ParseMode error), `import requests` buried inside a function, typo'd function call (e.g. `send_playlistı_page`), and missing `__init__.py` for package dirs. (3) Build the `_slots` they reference (`config.BOT_TOKEN`, `config.ALLOWED_USER_IDS`, `sessions.user_sessions`, `services/downloader.download_track_audio`, etc.) with the exact names their code imports, then run it. (4) Launch with `ALLOWED_USER_IDS="<user_telegram_id>"` env var set (see Pitfall #25). The user values clean modular architecture + `asyncio.to_thread` for blocking work (yt-dlp, requests) so the Telegram event loop never blocks.

25. **ALWAYS set `ALLOWED_USER_IDS` in production/memory, and expose `is_authorized()` at handler entry.** For a personal/private Telegram bot, gate every `CommandHandler`/`MessageHandler`/`CallbackQueryHandler` with a user-id allowlist check (`ALLOWED_USER_IDS` from env, comma-separated; empty = public). The user explicitly wants this as the #1 security item for a single-user bot. Pattern: `def is_authorized(uid): return not ALLOWED_USER_IDS or uid in ALLOWED_USER_IDS`; in each handler: `if not is_authorized(uid): await reject_unauthorized(update); return`. Launch the bot process with `ALLOWED_USER_IDS="7747086163"` (the user's Telegram id) so only they can drive it. Store this id in memory.

23. **RETIRED — DO NOT reintroduce DRM pre-filtering via `policy` (superseded by #2).** An earlier version of this skill advised pre-filtering tracks by SoundCloud's `policy` field and warning the user `🔒 این ترک رمزنگاری شده (DRM)...` BEFORE download. THIS WAS PROVEN WRONG IN SESSION 2026-08: SoundCloud tags MOST tracks (even plainly downloadable ones) with `policy: MONETIZE`, so the bot reported nearly every track as "locked" and the user rejected it angrily ("ای بابا همه ی اهنگ ها که قفله"). The correct behavior is in **Pitfall #2**: never pre-filter by `policy`; always attempt the actual download (`yt-dlp` first) and ONLY report "not downloadable" if the download genuinely fails. The `is_drm_locked()` helper is RETIRED. If you ever think you need a DRM warning, re-read #2 first.

26. **Modular structure + review checklist for user-authored drafts.** When the user hands you their own refactored bot (split into `config.py`, `sessions.py`, `services/`), do NOT overwrite with a single-file version — respect the modular layout. Review for the recurring fatal typos: `logging.getLogger(name)` (needs `__name__`); `if name == 'main':` (needs `if __name__ == '__main__':`); unclosed Markdown `**` (Telegram ParseMode error); `import requests` buried in a function (move to top); typo'd calls like `send_playlistı_page`; missing `services/__init__.py`; and referenced config/session/service names that don't exist yet (build them with exact names before running). Validate every file with `python3 -c "import ast; ast.parse(open(f).read())"`, then launch.

27. **Some SoundCloud tracks fail ONLY because of per-track Geo/IP blocking — handle gracefully, don't treat as a code bug.** From a datacenter/VPS, MOST tracks download fine via yt-dlp, but a SPECIFIC track (e.g. id 742144921, a re-uploaded/remix with stylized title `𝑱𝑼𝑫𝑨𝑺`) can fail with `ok=False` even though yt-dlp downloads other tracks in the same batch. This is NOT a bug in `download_track_audio` or `download_selected` — it's SoundCloud blocking that one track's stream from this IP (often re-uploads / label-takedown / region-locked). Verify by running `download_track_audio(track_dict, tmp)` directly for the failing id; if it returns False while a sibling id returns True, it's Geo-blocked. Correct handling: (a) keep the per-track try/except so one failure doesn't abort the batch (see Resilience pattern); (b) in the final summary, name the failed tracks so the user knows it was the track, not the bot; (c) do NOT pre-check or skip by any metadata field — attempt the real download and report only genuine failures. Also: when the user reports "0/2 downloaded", confirm whether they actually selected TWO different tracks or the same track twice — a user may have selected the same blocked track for both slots.

- **Launching background processes that use `.env` files**: When launching a background process (e.g. `python3 bot.py`) via `terminal(background=true)` or shell script, do NOT manually set/export environment variables like `BOT_TOKEN="..."` in the command line if the project already loads an `.env` file via `python-dotenv` or a custom `.env` loader. Manually specifying/overriding environment variables in the command invocation risks introducing typos, truncation, or escaping bugs that break authentication (e.g., `InvalidToken` error). Rely on the project's internal `.env` loader, or verify the token with `requests.get("https://api.telegram.org/bot<TOKEN>/getMe")` before launching.
- **User style signal — ship the fix, stop narrating the investigation.** When this user reports a bug/failure, they want the CODE FIX shipped immediately, not a long diagnosis monologue. In one session after several "cut off / ??" pings the user snapped: "just fucking fix this fucking bot". Lesson: on a bug report, go straight to `patch`/`write_file` + a quick direct verification (e.g. `python3 -c` import/ast check or a single targeted download test), then tell them the result in 1-2 lines. Do not paste 30-line stack traces or multi-turn "investigating…" commentary. This overrides the usual "explain root cause" default FOR THIS USER.

## Verification

```bash
# Bot should print "started" and connect to Telegram
python3 bot.py 2>&1 | head -5
# Expected: "✅  ربات در حال اجراست..." or similar
```
