#!/usr/bin/env python3
"""
SoundCloud Telegram Bot Template — accepts playlist/track URLs, resolves via SoundCloud API v2,
downloads progressive MP3 streams. Demonstrates patterns from telegram-bot-builder skill:
- Inline keyboards for track selection
- SoundCloud API v2 (client_id scraping + resolve + progressive download)
- **Playlist pagination**: follows `next_href` to fetch all pages, resolves missing titles individually
- Background execution via terminal(background=true)
- On-demand start/stop via agent (pitfall #12)
- Token from env var BOT_TOKEN
"""

import os
import re
import json
import logging
import requests
import tempfile
import asyncio
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN env var not set")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/120.0.0.0 Safari/537.36'
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# SoundCloud API helpers (see references/soundcloud-api.md)
# ──────────────────────────────────────────────────────────────────────────────

_client_id_cache = None

def get_client_id() -> str:
    global _client_id_cache
    if _client_id_cache:
        return _client_id_cache
    resp = requests.get('https://soundcloud.com', headers=HEADERS, timeout=15)
    match = re.search(
        r'window\.__sc_hydration\s*=\s*(\[.*?\]);\s*</script>',
        resp.text, re.DOTALL
    )
    if not match:
        raise RuntimeError("client_id not found in SoundCloud homepage")
    data = json.loads(match.group(1))
    for item in data:
        if item.get('hydratable') == 'apiClient':
            _client_id_cache = item['data']['id']
            return _client_id_cache
    raise RuntimeError("client_id not found in hydration data")


def resolve_url(url: str) -> dict:
    client_id = get_client_id()
    resp = requests.get(
        'https://api-v2.soundcloud.com/resolve',
        params={'url': url, 'client_id': client_id},
        headers=HEADERS, timeout=20
    )
    resp.raise_for_status()
    return resp.json()


def get_track_info(track_id: int) -> dict:
    client_id = get_client_id()
    resp = requests.get(
        f'https://api-v2.soundcloud.com/tracks/{track_id}',
        params={'client_id': client_id},
        headers=HEADERS, timeout=20
    )
    resp.raise_for_status()
    return resp.json()


def get_download_url(track_id: int) -> str | None:
    track = get_track_info(track_id)
    transcodings = track.get('media', {}).get('transcodings', [])
    progressive = next(
        (t for t in transcodings if t.get('format', {}).get('protocol') == 'progressive'),
        transcodings[0] if transcodings else None
    )
    if not progressive:
        return None
    client_id = get_client_id()
    stream = requests.get(
        progressive['url'],
        params={'client_id': client_id},
        headers=HEADERS, timeout=20
    ).json()
    return stream.get('url')


def get_playlist_tracks(playlist_data: dict) -> list[dict]:
    """Resolve full track info for all tracks in a playlist (including lazy-loaded ones via pagination)."""
    tracks = playlist_data.get('tracks', [])
    client_id = get_client_id()

    # First, fetch all pages via next_href
    next_href = playlist_data.get('next_href')
    while next_href:
        try:
            resp = requests.get(next_href, headers=HEADERS, timeout=20)
            resp.raise_for_status()
            page = resp.json()
            tracks.extend(page.get('collection', []))
            next_href = page.get('next_href')
        except Exception as e:
            logger.warning(f"Failed to fetch playlist page: {e}")
            break

    # Now resolve tracks missing title
    unresolved = [t for t in tracks if t and not t.get('title') and t.get('id')]
    for t in unresolved:
        try:
            full = get_track_info(t['id'])
            t['title'] = full.get('title', f"Track #{t['id']}")
            t['duration'] = full.get('duration')
            t['media'] = full.get('media', {})
        except Exception as e:
            logger.warning(f"Failed to resolve track {t['id']}: {e}")
            t['title'] = f"Track #{t['id']}"
    return tracks


# ──────────────────────────────────────────────────────────────────────────────
# Telegram handlers
# ──────────────────────────────────────────────────────────────────────────────

user_sessions = {}

PAGE_SIZE = 15  # tracks per page


def fmt_duration(ms: int | None) -> str:
    if not ms:
        return "—"
    s = ms // 1000
    return f"{s//60}:{s%60:02d}"


async def send_playlist_page(q: Optional["Update.callback_query"], status_msg, session: dict, uid: int, is_new: bool = False):
    """Send or edit message with paginated playlist view."""
    tracks = session['tracks']
    page = session.get('page', 0)
    start = page * PAGE_SIZE
    end = min(start + PAGE_SIZE, len(tracks))
    page_tracks = tracks[start:end]

    keyboard = []
    for i, t in enumerate(page_tracks):
        idx = start + i
        title = t.get('title', f"Track #{t.get('id')}")
        dur = fmt_duration(t.get('duration'))
        keyboard.append([
            InlineKeyboardButton(f"{idx+1}. {title[:45]} ({dur})", callback_data=f"dl_{idx}")
        ])

    # Navigation buttons
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Previous", callback_data="page_prev"))
    if end < len(tracks):
        nav.append(InlineKeyboardButton("➡️ Next", callback_data="page_next"))
    if nav:
        keyboard.append(nav)

    keyboard.append([
        InlineKeyboardButton("📦 Download All (ZIP)", callback_data="dl_all"),
        InlineKeyboardButton("❌ Cancel", callback_data="cancel")
    ])

    text = (
        f"🎵 **{session['playlist_title']}**\n"
        f"🎶 {len(tracks)} tracks — page {page+1}/{(len(tracks)-1)//PAGE_SIZE + 1}\n\n"
        "Tap a track to download, or navigate pages:"
    )

    if is_new:
        await status_msg.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        await q.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 **SoundCloud Downloader Bot**\n\n"
        "Send a SoundCloud playlist/track/user link → I'll show tracks for download.\n\n"
        "Examples:\n"
        "`https://soundcloud.com/user/sets/playlist-name`\n"
        "`https://soundcloud.com/user/track-name`\n\n"
        "Commands:\n"
        "/start — Help\n"
        "/cancel — Cancel current session",
        parse_mode="Markdown"
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in user_sessions:
        del user_sessions[uid]
    await update.message.reply_text("✅ Session cancelled. Send a new link.")


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    url = update.message.text.strip()

    if not re.match(r'https?://(www\.)?soundcloud\.com/', url):
        await update.message.reply_text("❌ Not a valid SoundCloud link.")
        return

    status_msg = await update.message.reply_text("⏳ Processing link...")

    try:
        data = resolve_url(url)
        kind = data.get('kind')

        if kind == 'playlist':
            tracks = get_playlist_tracks(data)
            if not tracks:
                await status_msg.edit_text("❌ Playlist empty or unreadable.")
                return

            user_sessions[uid] = {
                'playlist_title': data.get('title', 'Playlist'),
                'tracks': tracks,
                'message_id': status_msg.message_id,
                'chat_id': update.effective_chat.id,
                'page': 0,
            }

            await send_playlist_page(q=None, status_msg=status_msg, session=user_sessions[uid], uid=uid, is_new=True)

        elif kind == 'track':
            track = data
            track_id = track.get('id')
            title = track.get('title', 'Unknown')
            dur = fmt_duration(track.get('duration'))

            download_url = get_download_url(track_id)
            if not download_url:
                await status_msg.edit_text("❌ Track not downloadable (streamable: false).")
                return

            keyboard = [
                [InlineKeyboardButton("⬇️ Download MP3", callback_data=f"dl_track_{track_id}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ]
            await status_msg.edit_text(
                f"🎵 **{title}**\n⏱ {dur}\n\nReady to download:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

        else:
            await status_msg.edit_text(f"❌ Unsupported link type: {kind}")

    except requests.HTTPError as e:
        await status_msg.edit_text(f"❌ API error: {e.response.status_code}")
    except Exception as e:
        logger.exception("handle_url error")
        await status_msg.edit_text(f"❌ Error: {e}")


async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    data = q.data

    if data == "cancel":
        if uid in user_sessions:
            del user_sessions[uid]
        await q.edit_message_text("✅ Cancelled.")
        return

    if data == "page_prev":
        session = user_sessions.get(uid)
        if not session:
            await q.edit_message_text("❌ Session expired. Resend the link.")
            return
        session['page'] = max(0, session.get('page', 0) - 1)
        await send_playlist_page(q=q, status_msg=None, session=session, uid=uid)
        return

    if data == "page_next":
        session = user_sessions.get(uid)
        if not session:
            await q.edit_message_text("❌ Session expired. Resend the link.")
            return
        session['page'] = session.get('page', 0) + 1
        await send_playlist_page(q=q, status_msg=None, session=session, uid=uid)
        return

    if data == "dl_all":
        session = user_sessions.get(uid)
        if not session:
            await q.edit_message_text("❌ Session expired. Resend the link.")
            return
        await q.edit_message_text("⏳ Preparing ZIP... (TODO)")
        return

    if data == "more":
        await q.edit_message_text("⚠️ Full list not implemented. Resend the link.")
        return

    if data.startswith("dl_"):
        parts = data.split("_")
        if parts[1] == "track":
            track_id = int(parts[2])
            await download_and_send_track(q, track_id)
        else:
            idx = int(parts[1])
            session = user_sessions.get(uid)
            if not session or idx >= len(session['tracks']):
                await q.edit_message_text("❌ Session expired or invalid index.")
                return
            track = session['tracks'][idx]
            track_id = track.get('id')
            await download_and_send_track(q, track_id)


async def download_and_send_track(q: Update.callback_query, track_id: int):
    await q.edit_message_text(f"⏳ Getting download link for track #{track_id}...")

    try:
        download_url = get_download_url(track_id)
        if not download_url:
            await q.edit_message_text("❌ No download link (not streamable).")
            return

        track_info = get_track_info(track_id)
        title = track_info.get('title', f'track_{track_id}')
        safe_title = re.sub(r'[^\w\s-]', '', title).strip()[:100]
        filename = f"{safe_title}.mp3"

        await q.edit_message_text(f"⬇️ Downloading: {title}...")

        with requests.get(download_url, headers=HEADERS, stream=True, timeout=60) as r:
            r.raise_for_status()
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        tmp.write(chunk)
                tmp_path = tmp.name

        await q.message.reply_audio(
            audio=open(tmp_path, 'rb'),
            title=title,
            performer=track_info.get('user', {}).get('username', 'SoundCloud'),
            duration=track_info.get('duration', 0) // 1000,
            caption=f"🎵 {title}"
        )

        os.unlink(tmp_path)
        await q.edit_message_text(f"✅ Sent: {title}")

    except Exception as e:
        logger.exception("download error")
        await q.edit_message_text(f"❌ Download failed: {e}")


# ──────────────────────────────────────────────────────────────────────────────
# Main — run with: BOT_TOKEN=xxx python3 soundcloud_bot.py
# Background: terminal(background=true, notify_on_complete=false)
# ──────────────────────────────────────────────────────────────────────────────

def main():
    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .read_timeout(30)
        .write_timeout(30)
        .connect_timeout(30)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    app.add_handler(CallbackQueryHandler(callback_handler))

    print("✅ SoundCloud bot started (polling)...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()