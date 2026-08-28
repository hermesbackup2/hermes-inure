# SoundCloud API Integration (Direct, no yt-dlp)

## Problem
yt-dlp's SoundCloud extractor returns HTTP 404 from cloud/VPS servers. The official SoundCloud API requires OAuth. Solution: use SoundCloud's internal API v2 with a scraped `client_id`.

## Step 1: Get client_id from SoundCloud homepage

```python
import requests, re, json

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/120.0.0.0 Safari/537.36'
}

def get_client_id() -> str:
    resp = requests.get('https://soundcloud.com', headers=HEADERS, timeout=15)
    match = re.search(
        r'window\.__sc_hydration\s*=\s*(\[.*?\]);\s*</script>',
        resp.text, re.DOTALL
    )
    data = json.loads(match.group(1))
    for item in data:
        if item.get('hydratable') == 'apiClient':
            return item['data']['id']
    raise RuntimeError("client_id not found")
```

## Step 2: Resolve any SoundCloud URL

```python
def resolve_url(url: str) -> dict:
    client_id = get_client_id()
    resp = requests.get(
        'https://api-v2.soundcloud.com/resolve',
        params={'url': url, 'client_id': client_id},
        headers=HEADERS, timeout=20
    )
    resp.raise_for_status()
    return resp.json()
```

Returns `kind`: `playlist`, `track`, or `user`. Playlists include `tracks[]` array with `id`, `title`, `duration`.

For large playlists, check `next_href` for pagination:
```python
next_href = data.get('next_href')
while next_href:
    page = requests.get(next_href, headers=HEADERS, timeout=20).json()
    tracks.extend(page.get('collection', []))
    next_href = page.get('next_href')
```

## Step 3: Get direct MP3 download URL

```python
def get_download_url(track_id: int) -> str | None:
    client_id = get_client_id()
    track = requests.get(
        f'https://api-v2.soundcloud.com/tracks/{track_id}',
        params={'client_id': client_id},
        headers=HEADERS, timeout=20
    ).json()

    transcodings = track.get('media', {}).get('transcodings', [])
    # Prefer 'progressive' protocol (direct MP3), not 'hls'
    progressive = next(
        (t for t in transcodings if t.get('format', {}).get('protocol') == 'progressive'),
        transcodings[0] if transcodings else None
    )
    if not progressive:
        return None

    stream = requests.get(
        progressive['url'],
        params={'client_id': client_id},
        headers=HEADERS, timeout=20
    ).json()
    return stream.get('url')  # Direct MP3 URL, time-limited
```

## Key API Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /resolve?url=<soundcloud_url>` | Resolve any SC URL to its data |
| `GET /tracks/<id>` | Get full track info including transcodings |
| `GET /users/<id>/playlists` | Get user's playlists (with pagination) |
| `GET /search/playlists?q=<query>` | Search playlists |
| `GET /media/<hash>/stream/progressive` | Get direct MP3 stream URL |

## Response Structure

**Playlist** (`kind: "playlist"`):
- `title`, `track_count`, `tracks[]` (each with `id`, `title`, `duration`, `user`)

**Track** (`kind: "track"`):
- `id`, `title`, `duration`, `streamable`, `downloadable`
- `policy`: **DRM/lock indicator** — see "DRM detection" below
- `media.transcodings[]`: each has `url`, `preset`, `format.protocol`
  - `progressive` = direct MP3 (✅ use this)
  - `hls` = HTTP Live Streaming (needs ffmpeg to convert)
  - `cbc-encrypted-hls` / `ctr-encrypted-hls` = **encrypted HLS — NOT downloadable** (see DRM section)

**Download URL response**: `{ "url": "https://cf-media.sndcdn.com/..." }` — time-limited, generates a fresh signed URL.

## DRM detection (REQUIRED before download — 2026-08 update)

A large and growing fraction of SoundCloud tracks (even non-paid, e.g. Eminem "Rap God") are delivered ONLY as `cbc-encrypted-hls`/`ctr-encrypted-hls` with NO `progressive` transcoding. These are **DRM-protected** and cannot be downloaded by any tool:
- Direct API `GET /transcodings` returns an `.m3u8`; `ffmpeg -c copy` fails (no decryption keys).
- `yt-dlp` on the permalink fails with `ERROR: [soundcloud] <id>: This video is DRM protected`.

**Detect before attempting download** from `GET /tracks/<id>`:
```python
def is_drm_locked(track_info: dict) -> bool:
    policy = (track_info.get('policy') or '').upper()
    # 'ALLOW' or '' (empty) = downloadable; anything else (MONETIZE/BLOCK/SNIP/...) = locked
    return policy not in ('', 'ALLOW')
```
If locked, tell the user the track is encrypted/DRM and not downloadable — do NOT attempt download (it will always fail). This applies to both single-track links and per-track in a playlist batch.

## Pitfalls

- **client_id may rotate.** If resolve returns 404 unexpectedly, re-scrape the homepage for a fresh client_id.
- **Progressive transcoding may not exist** for most 2026-era tracks (they're HLS+encrypted). If NO `progressive` transcoding exists, the track is DRM-locked — use `is_drm_locked()` and warn, do NOT fall back to HLS+ffmpeg (it always fails on encrypted streams).
- **Download URLs are time-limited** (signed with Policy). Don't cache them long.
- **Some tracks are not streamable** (`streamable: false`). These won't have transcodings.
- **Search API returns `collection[]`**, not direct results. Parse accordingly.
## Handling Large Playlists & Missing Titles (CRITICAL)

SoundCloud's `/resolve` endpoint for a playlist returns a `tracks[]` array where **only the first few tracks (typically 4-5) carry full metadata**. All subsequent tracks carry only an `id` (`{id: 12345, title: None}`).

### The 403 Batch Fetch Failure & Parallel Solution
- **Attempting batch fetch** (`GET /tracks?ids=1,2,3`) returns **HTTP 403 Forbidden** on SoundCloud API v2.
- **Solution:** Fetch missing track info individually per ID. To keep it fast (e.g., 210 tracks in under 4 seconds), use **`ThreadPoolExecutor`** with `max_workers=15`:

```python
from concurrent.futures import ThreadPoolExecutor

def get_playlist_tracks(playlist_url: str) -> tuple[str, list]:
    data = resolve_soundcloud_url(playlist_url)
    if not data:
        return "Playlist", []

    kind = data.get('kind')
    title = data.get('title', 'playlist')
    if kind == 'track':
        return title, [data]

    if kind in ('playlist', 'system-playlist'):
        raw_tracks = data.get('tracks', [])
        missing_indices = [
            idx for idx, t in enumerate(raw_tracks)
            if not isinstance(t, dict) or not t.get('title')
        ]

        def fetch_info(i):
            t_id = raw_tracks[i].get('id') if isinstance(raw_tracks[i], dict) else raw_tracks[i]
            if t_id:
                info = get_track_info(t_id)
                if info:
                    return i, info
            return i, None

        if missing_indices:
            with ThreadPoolExecutor(max_workers=15) as executor:
                for i, info in executor.map(fetch_info, missing_indices):
                    if info:
                        raw_tracks[i] = info

        cleaned = [t for t in raw_tracks if isinstance(t, dict) and t.get('id') and t.get('title')]
        return title, cleaned
    return title, []
```
