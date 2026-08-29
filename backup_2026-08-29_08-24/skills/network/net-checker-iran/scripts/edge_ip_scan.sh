#!/bin/bash
# Cloudflare Edge IP scanner
# Tests connectivity to Cloudflare Edge IPs on port 443
# Usage: ./edge_ip_scan.sh [test_domain] [max_ips]

set -euo pipefail

TEST_DOMAIN=${1:-"chatgpt.com"}
MAX_IPS=${2:-50}
TIMEOUT=${TIMEOUT:-3}
CONCURRENT=${CONCURRENT:-20}

# Cloudflare IP ranges (subset of common ones for Iran)
CLOUDFLARE_IPS=(
  "104.16.0.0" "104.16.1.0" "104.16.2.0" "104.16.3.0"
  "104.16.4.0" "104.16.5.0" "104.16.6.0" "104.16.7.0"
  "104.16.8.0" "104.16.9.0" "104.16.10.0" "104.16.11.0"
  "104.16.12.0" "104.16.13.0" "104.16.14.0" "104.16.15.0"
  "104.17.0.0" "104.17.1.0" "104.17.2.0" "104.17.3.0"
  "104.17.4.0" "104.17.5.0" "104.17.6.0" "104.17.7.0"
  "104.18.0.0" "104.18.1.0" "104.18.2.0" "104.18.3.0"
  "104.19.0.0" "104.19.1.0" "104.19.2.0" "104.19.3.0"
  "104.20.0.0" "104.20.1.0" "104.20.2.0" "104.20.3.0"
  "104.21.0.0" "104.21.1.0" "104.21.2.0" "104.21.3.0"
  "104.22.0.0" "104.22.1.0" "104.22.2.0" "104.22.3.0"
  "104.23.0.0" "104.23.1.0" "104.23.2.0" "104.23.3.0"
  "104.24.0.0" "104.24.1.0" "104.24.2.0" "104.24.3.0"
  "104.25.0.0" "104.25.1.0" "104.25.2.0" "104.25.3.0"
  "104.26.0.0" "104.26.1.0" "104.26.2.0" "104.26.3.0"
  "104.27.0.0" "104.27.1.0" "104.27.2.0" "104.27.3.0"
  "172.64.0.0" "172.64.1.0" "172.64.2.0" "172.64.3.0"
  "172.64.4.0" "172.64.5.0" "172.64.6.0" "172.64.7.0"
  "172.64.8.0" "172.64.9.0" "172.64.10.0" "172.64.11.0"
  "172.64.12.0" "172.64.13.0" "172.64.14.0" "172.64.15.0"
  "172.65.0.0" "172.65.1.0" "172.65.2.0" "172.65.3.0"
  "172.66.0.0" "172.66.1.0" "172.66.2.0" "172.66.3.0"
  "172.67.0.0" "172.67.1.0" "172.67.2.0" "172.67.3.0"
)

# Trim to MAX_IPS
IPS=("${CLOUDFLARE_IPS[@]:0:$MAX_IPS}")

echo "=== Cloudflare Edge IP Scanner ==="
echo "Test domain: ${TEST_DOMAIN} | Port: 443 | IPs: ${#IPS[@]}"
echo "-----------------------------------"

scan_ip() {
  local ip="$1"
  local latency_start latency_end latency_ms result

  latency_start=$(date +%s%N)
  # Test TCP connection to port 443
  result=$(timeout "$TIMEOUT" bash -c "echo >/dev/tcp/${ip}/443" 2>/dev/null && echo "OK" || echo "FAIL")
  latency_end=$(date +%s%N)
  latency_ms=$(( (latency_end - latency_start) / 1000000 ))

  if [ "$result" = "OK" ]; then
    echo "✅ ${ip} — ${latency_ms}ms — OPEN"
  fi
}

echo "Scanning..."
for ip in "${IPS[@]}"; do
  scan_ip "$ip" &
  while [ "$(jobs -r | wc -l)" -ge "$CONCURRENT" ]; do
    sleep 0.05
  done
done

wait
echo ""
echo "=== Scan Complete ==="
