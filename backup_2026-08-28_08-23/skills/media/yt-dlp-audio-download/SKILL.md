---
name: yt-dlp-audio-download
description: Use when yt-dlp audio downloads fail to find files.
---

# yt-dlp audio download to a local file

## When to use
- Fixing `yt-dlp` audio downloads when `outtmpl` and `FFmpegExtractAudio` fail to locate the output file.

## The fix
Use `outtmpl: base_out + '.%(ext)s'` and glob fallback.
