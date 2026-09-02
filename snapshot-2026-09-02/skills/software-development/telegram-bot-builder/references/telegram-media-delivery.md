# Telegram Bot Media Delivery Notes

Session-specific learnings from building a SoundCloud download bot.

## SoundCloud API Notes (verified working)

### Client ID scraping
```python
def get_client_id() -> str:
    resp = requests.get('https://soundcloud.com', headers=HEADERS, timeout=15)
    match = re.search(r'window\.__sc_hydration\s*=\s*(\[.*?\]);\s*</script>', resp.text, re.DOTALL)
    data = json.loads(match.group(1))
    for item in data:
        if item.get('hydratable') == 'apiClient':
            return item['data']['id']
```

### Playlist pagination (critical)
- `resolve` returns first ~5-20 tracks with full metadata
- Rest are `{id}` only, no `title`/`media`
- Must follow `next_href` for ALL pages:
```python
next_href = data.get('next_href')
while next_href:
    page = requests.get(next_href, headers=HEADERS, timeout=20).json()
    tracks.extend(page.get('collection', []))
    next_href = page.get('next_href')
```
- Then resolve each title-less track via `GET /tracks/<id>` individually

### Progressive vs HLS
- `progressive` protocol → direct MP3 URL (128kbps for free accounts)
- `hls` → needs ffmpeg conversion
- Prefer progressive, fall back to HLS + ffmpeg

### Cover art embedding (ID3 tags)
```python
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, error as mutagen_error
from mutagen.mp3 import MP3

# artwork_url → largest size via -t500x500
# Fallback: user avatar_url
# Detect PNG vs JPEG via magic bytes: b'\x89PNG\r\n\x1a\n'
# Add TIT2/TPE1/TALB tags while embedding cover
```

### Telegram audio constraints
- Bot limit: 50MB per file
- `reply_audio` accepts `thumbnail=open(path,'rb')` for cover display (NOT `thumb` — that was removed in python-telegram-bot v20+)
- Set `read_timeout/write_timeout/connect_timeout=30` for cloud deploys

## Batch ZIP Download with Chunking (verified working)

For "📦 دانلود همه (ZIP)" buttons on playlists with many tracks:

1. **Download ALL tracks first** into a temp dir (`tempfile.mkdtemp()`), one `try/except` PER track:
```python
downloaded = []  # list of (mp3_path, safe_name)
failed = []      # list of titles that failed

for i, track in enumerate(tracks):
    try:
        dl_url = get_download_url(track['id'])
        if not dl_url:
            failed.append(title); continue
        # stream download to NamedTemporaryFile(suffix='.mp3', dir=tmp_dir)
        # add_cover_art_to_mp3(mp3_path, track_info)
        downloaded.append((mp3_path, safe))
    except Exception as e:
        logger.warning(...); failed.append(title)  # NEVER cancel the whole batch
```
2. **Chunk into ZIPs under 45MB** (Telegram bot limit is 50MB — leave headroom):
```python
MAX_ZIP_SIZE = 45 * 1024 * 1024
for chunk_start in range(0, len(downloaded), 50):  # max 50 files per zip
    chunk = downloaded[chunk_start:chunk_start + 50]
    # if total size > MAX_ZIP_SIZE, fall back to previous chunk
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for mp3_path, safe_name in chunk:
            zf.write(mp3_path, f"{safe_name}.mp3")
```
3. **Send each ZIP** via `reply_document(InputFile(zf_file, filename=zip_filename))` with a caption showing range (`آهنگ X تا Y از N`).
4. **Clean up** every temp MP3 + ZIP after sending; remove temp dir at the end.
5. **Final summary message**: `✅ X/Y آهنگ ارسال شد` + list of failed titles (first 5).

**User preference:** partial success is REQUIRED — if one track fails (not streamable, timeout, network error), skip it and keep going. Never cancel the whole batch because of one failure. Users explicitly expect this.

## Pitfalls Hit

1. **`Update.callback_query | None` type annotation fails** — `Update.callback_query` is a `member_descriptor`, not a class. Use `Optional["Update.callback_query"]` (string forward ref) or no annotation. Python <3.10 doesn't support `X | None` syntax at runtime for arbitrary attribute types.

2. **In-memory `user_sessions` dict resets on restart** — any bot restart loses playlist state. Acceptable for single-user; use SQLite for multi-user persistent state.

3. **Playlist track title resolution is O(n) API calls** — for 100+ track playlists, this takes time. Show "در حال پردازش" status and let it run.

4. **Telegram inline keyboard limit** — max buttons per message is limited; paginate at 15/page (PAGE_SIZE=15 works well).

5. **python-telegram-bot v22.x parameter name is `thumbnail`, not `thumb`** — The `thumb` parameter was removed in v20+. Use `thumbnail=open(image_path, 'rb')` when calling `reply_audio()`. Same applies to `reply_document`/`send_audio` — all use `thumbnail`.

6. **Large batch downloads take minutes** — update the status message as each track completes (`⏳ در حال دانلود (i/N): title...`) so the user sees progress and the callback doesn't time out (Telegram callback queries expire after ~60s but editing a message keeps it alive).
