#!/bin/bash
# DNS latency test using raw UDP sockets via Python
# No dig/ping dependency
# Usage: ./dns_latency.sh

set -euo pipefail

TIMEOUT=${TIMEOUT:-2}

echo "=== DNS Latency Test ==="
echo "Timeout: ${TIMEOUT}s"
echo "-----------------------------------"

python3 -c "
import socket, time

dns_servers = [
    ('8.8.8.8', 'Google DNS'),
    ('8.8.4.4', 'Google DNS Secondary'),
    ('1.1.1.1', 'Cloudflare DNS'),
    ('1.0.0.1', 'Cloudflare DNS Secondary'),
    ('9.9.9.9', 'Quad9 DNS'),
    ('208.67.222.222', 'OpenDNS'),
    ('208.67.220.220', 'OpenDNS Secondary'),
    ('64.6.64.6', 'Verisign DNS'),
    ('64.6.65.6', 'Verisign DNS Secondary'),
    ('185.228.168.9', 'CleanBrowsing'),
    ('76.76.19.19', 'Alternate DNS'),
    ('94.140.14.14', 'AdGuard DNS'),
    ('4.2.2.1', 'Level3 DNS'),
    ('4.2.2.2', 'Level3 DNS Secondary'),
]

# DNS query for google.com A record
dns_query = bytes([
    0xAB, 0xCD,  # Transaction ID
    0x01, 0x00,  # Flags: standard query, recursion desired
    0x00, 0x01,  # Questions: 1
    0x00, 0x00,  # Answer RRs: 0
    0x00, 0x00,  # Authority RRs: 0
    0x00, 0x00,  # Additional RRs: 0
    # Query: google.com
    0x06, 0x67, 0x6f, 0x6f, 0x67, 0x6c, 0x65,  # 'google'
    0x03, 0x63, 0x6f, 0x6d,  # 'com'
    0x00,        # End of name
    0x00, 0x01,  # Type: A
    0x00, 0x01,  # Class: IN
])

timeout = ${TIMEOUT}

for ip, name in dns_servers:
    start = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(timeout)
        sock.sendto(dns_query, (ip, 53))
        data, _ = sock.recvfrom(512)
        elapsed = (time.time() - start) * 1000
        sock.close()
        print(f'  ✅ {name} ({ip}) — {elapsed:.0f}ms — {len(data)} bytes')
    except socket.timeout:
        elapsed = (time.time() - start) * 1000
        print(f'  ❌ {name} ({ip}) — TIMEOUT ({elapsed:.0f}ms)')
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        print(f'  ⚠️  {name} ({ip}) — ERROR: {e}')
" 2>/dev/null

echo ""
echo "=== Test Complete ==="
