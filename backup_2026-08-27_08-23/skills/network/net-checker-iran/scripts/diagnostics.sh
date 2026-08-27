#!/bin/bash
# Comprehensive internet diagnostics for Iran's network
# Uses only curl + python3 (no ping/dig dependency)
# Usage: ./diagnostics.sh

set -euo pipefail

TIMEOUT=${TIMEOUT:-3}

echo "╔══════════════════════════════════════════╗"
echo "║   Internet Diagnostics — Iran Network    ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── 1. DNS Resolution via Python (no dig needed) ──
echo "── 1. DNS Resolution ──"
echo "Checking if common domains resolve..."

KNOWN_HIJACK_IPS=("127.0.0.1" "0.0.0.0" "10.10.34.34")

python3 -c "
import socket
domains = ['google.com', 'cloudflare.com', 'github.com', 'wikipedia.org',
           'chatgpt.com', 'youtube.com', 'whatsapp.com', 'twitter.com',
           'facebook.com', 'instagram.com']
hijack = {'127.0.0.1', '0.0.0.0', '10.10.34.34'}
for d in domains:
    try:
        ip = socket.getaddrinfo(d, 443, socket.AF_INET)[0][4][0]
        if ip in hijack:
            print(f'  ⚠️  {d} → {ip} (POSSIBLE HIJACK)')
        else:
            print(f'  ✅ {d} → {ip}')
    except Exception:
        print(f'  ❌ {d} — NO RESOLUTION')
" 2>/dev/null
echo ""

# ── 2. DNS Provider Comparison ──
echo "── 2. DNS Provider Comparison ──"
echo "Resolving google.com via different DNS servers..."

python3 -c "
import socket, subprocess
providers = [
    ('8.8.8.8', 'Google'),
    ('1.1.1.1', 'Cloudflare'),
    ('9.9.9.9', 'Quad9'),
    ('208.67.222.222', 'OpenDNS'),
]
for ip, name in providers:
    try:
        # Use curl to query DNS-over-HTTPS as fallback
        import urllib.request
        url = f'https://dns.google/resolve?name=google.com&type=A'
        req = urllib.request.urlopen(url, timeout=3)
        import json
        data = json.loads(req.read())
        answers = data.get('Answer', [])
        if answers:
            print(f'  ✅ {name} ({ip}) → via DoH → {answers[0][\"data\"]}')
        else:
            print(f'  ❌ {name} ({ip}) — no answer')
    except Exception:
        # Fallback: just try direct DNS via socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(3)
            # Build DNS query for google.com
            q = bytes([0xAB,0xCD,0x01,0x00,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,
                       0x06,0x67,0x6f,0x6f,0x67,0x6c,0x65,0x03,0x63,0x6f,0x6d,0x00,
                       0x00,0x01,0x00,0x01])
            s.sendto(q, (ip, 53))
            data, _ = s.recvfrom(512)
            s.close()
            # Parse answer IP from response (bytes 14-end, find A record)
            if len(data) > 14:
                print(f'  ✅ {name} ({ip}) — responded ({len(data)} bytes)')
            else:
                print(f'  ❌ {name} ({ip}) — empty response')
        except Exception as e:
            print(f'  ❌ {name} ({ip}) — FAILED')
" 2>/dev/null
echo ""

# ── 3. HTTPS / TLS Check ──
echo "── 3. HTTPS / TLS Check ──"
echo "Testing HTTPS connectivity to major sites..."

for domain in "google.com" "github.com" "chatgpt.com" "youtube.com" "whatsapp.com" "instagram.com" "twitter.com"; do
  http_code=$(curl -s -o /dev/null -w "%{http_code}" \
    --connect-timeout "$TIMEOUT" --max-time "$TIMEOUT" \
    -L "https://${domain}" 2>/dev/null) || http_code="000"

  if [ "$http_code" != "000" ] && [ "$http_code" != "0000" ]; then
    echo "  ✅ ${domain} — HTTP ${http_code}"
  else
    echo "  ❌ ${domain} — BLOCKED/FAILED"
  fi
done
echo ""

# ── 4. Protocol Check (HTTP vs HTTPS) ──
echo "── 4. Protocol Check (HTTP vs HTTPS) ──"
echo "Comparing HTTP and HTTPS accessibility..."

for domain in "google.com" "github.com" "youtube.com"; do
  http_code=$(curl -s -o /dev/null -w "%{http_code}" \
    --connect-timeout "$TIMEOUT" --max-time "$TIMEOUT" \
    "http://${domain}" 2>/dev/null) || http_code="000"
  https_code=$(curl -s -o /dev/null -w "%{http_code}" \
    --connect-timeout "$TIMEOUT" --max-time "$TIMEOUT" \
    "https://${domain}" 2>/dev/null) || https_code="000"

  if [ "$http_code" != "000" ] && [ "$https_code" != "000" ]; then
    echo "  ✅ ${domain} — HTTP:${http_code} HTTPS:${https_code}"
  elif [ "$http_code" != "000" ]; then
    echo "  ⚠️  ${domain} — HTTP:${http_code} HTTPS:BLOCKED"
  elif [ "$https_code" != "000" ]; then
    echo "  ⚠️  ${domain} — HTTP:BLOCKED HTTPS:${https_code}"
  else
    echo "  ❌ ${domain} — BOTH BLOCKED"
  fi
done
echo ""

# ── 5. Latency Test ──
echo "── 5. Latency Test ──"
echo "Measuring HTTPS connection latency..."

for domain in "google.com" "github.com" "cloudflare.com"; do
  latency=$(curl -s -o /dev/null -w "%{time_connect}" \
    --connect-timeout "$TIMEOUT" --max-time "$TIMEOUT" \
    "https://${domain}" 2>/dev/null) || latency="N/A"

  if [ "$latency" != "N/A" ] && [ "$latency" != "0.000000" ]; then
    ms=$(python3 -c "print(f'{${latency}*1000:.0f}ms')" 2>/dev/null || echo "${latency}s")
    echo "  ✅ ${domain} — connect: ${ms}"
  else
    echo "  ❌ ${domain} — FAILED"
  fi
done
echo ""

# ── 6. Summary ──
echo "══════════════════════════════════════════"
echo "Diagnostics Complete — $(date '+%Y-%m-%d %H:%M:%S')"
echo "══════════════════════════════════════════"
