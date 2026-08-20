#!/bin/bash
# Domain accessibility checker — no ping dependency
# Usage: ./domain_check.sh [custom_domain1 custom_domain2 ...]

set -euo pipefail

TIMEOUT=${TIMEOUT:-3}
CONCURRENT=${CONCURRENT:-10}

DEFAULT_DOMAINS=(
  "google.com" "gmail.com" "github.com" "youtube.com" "wikipedia.org"
  "chatgpt.com" "whatsapp.com" "instagram.com" "twitter.com" "facebook.com"
  "tiktok.com" "reddit.com" "linkedin.com" "amazon.com" "microsoft.com"
  "apple.com" "vercel.com" "netlify.com" "cloudflare.com" "cdnjs.com"
  "jsdelivr.com" "medium.com" "npmjs.com" "play.google.com" "speedtest.net"
  "deepseek.com" "nodejs.org" "stackoverflow.com" "telegram.org"
  "dropbox.com" "zoom.us" "notion.so"
)

if [ $# -gt 0 ]; then
  DOMAINS=("$@")
else
  DOMAINS=("${DEFAULT_DOMAINS[@]}")
fi

echo "=== Domain Accessibility Check ==="
echo "Timeout: ${TIMEOUT}s | Domains: ${#DOMAINS[@]}"
echo "-----------------------------------"

check_domain() {
  local domain="$1"
  local http_code latency_start latency_end latency_ms

  latency_start=$(date +%s%N)
  http_code=$(curl -s -o /dev/null -w "%{http_code}" \
    --connect-timeout "$TIMEOUT" --max-time "$TIMEOUT" \
    -L "https://${domain}" 2>/dev/null) || http_code="000"
  latency_end=$(date +%s%N)
  latency_ms=$(( (latency_end - latency_start) / 1000000 ))

  if [ "$http_code" != "000" ] && [ "$http_code" != "0000" ]; then
    echo "✅ ${domain} — HTTP ${http_code} — ${latency_ms}ms"
  else
    echo "❌ ${domain} — FAILED — ${latency_ms}ms"
  fi
}

for domain in "${DOMAINS[@]}"; do
  check_domain "$domain" &
  while [ "$(jobs -r | wc -l)" -ge "$CONCURRENT" ]; do
    sleep 0.1
  done
done

wait
echo ""
echo "=== Check Complete ==="
