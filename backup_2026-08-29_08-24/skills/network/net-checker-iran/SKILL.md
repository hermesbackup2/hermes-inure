---
name: net-checker-iran
description: "Network diagnostics and connectivity checks for Iran."
version: 0.2.0
author: Hermes
metadata:
  hermes:
    tags: [Network, Iran, DNS, Connectivity, Diagnostics]
related_skills:
  - network/ip-security-analyzer
---

# Network Checker — Iran Edition

A set of CLI-based network diagnostic tools tailored for Iran's internet censorship landscape. Inspired by [mirarr-app/network-checker](https://github.com/mirarr-app/network-checker).

These scripts check domain accessibility, DNS latency, Cloudflare Edge IP reachability, and perform comprehensive internet diagnostics including SNI spoof detection and DNS hijack identification.

## When to Use

- User asks to check if websites are accessible from their network
- User asks about DNS latency or DNS provider comparison
- User asks to scan Cloudflare Edge IPs for clean connectivity
- User asks about internet censorship or blocking status
- User asks about DNS hijacking or SNI spoofing
- User wants a full network diagnostic report

## Prerequisites

- `curl` — for HTTP/HTTPS checks
- `python3` — for raw UDP DNS queries and DNS resolution tests
- No external packages or APIs required (no `dig`/`ping` needed — scripts use curl + python3 only)

## Related Skills

- **ip-security-analyzer** — Deep IP reputation analysis, ASN lookup, geolocation, and threat intelligence for suspicious IPs found during network diagnostics

## How to Run

Invoke scripts via the `terminal` tool:

```bash
# Full diagnostics (recommended first step)
terminal(command="bash /data/.hermes/skills/network/net-checker-iran/scripts/diagnostics.sh")

# Check specific domains
terminal(command="bash /data/.hermes/skills/network/net-checker-iran/scripts/domain_check.sh google.com github.com youtube.com")

# DNS latency test
terminal(command="bash /data/.hermes/skills/network/net-checker-iran/scripts/dns_latency.sh")

# Scan Cloudflare Edge IPs
terminal(command="bash /data/.hermes/skills/network/net-checker-iran/scripts/edge_ip_scan.sh chatgpt.com 30")
```

## Quick Reference

| Script | Purpose | Key Env Vars |
|---|---|---|
| `diagnostics.sh` | Full network diagnostic suite | `TIMEOUT` |
| `domain_check.sh` | HTTP check for popular domains | `TIMEOUT`, `CONCURRENT` |
| `dns_latency.sh` | UDP DNS query latency to resolvers | `TIMEOUT` |
| `edge_ip_scan.sh` | Cloudflare Edge IP TCP scan | `TIMEOUT`, `CONCURRENT` |

## Procedure

1. **Run full diagnostics first** to get a baseline.
   - Completion: all 6 test sections output results.

2. **Run domain_check.sh** with specific domains if the user reports a site issue.
   - Completion: every requested domain shows ✅ or ❌.

3. **Run dns_latency.sh** if DNS performance is suspected.
   - Completion: all DNS servers show latency or TIMEOUT.

4. **Run edge_ip_scan.sh** if looking for clean Cloudflare IPs.
   - Completion: scan finishes and lists open IPs.

## Pitfalls

1. **Iran's GFW behavior varies by ISP and time of day.** Results may differ between Shatel, Irancell, Hamrah-e-Aval, etc. Always note which ISP when reporting.

2. **Container/VM environments often lack `ping` and `dig`** (raw ICMP/UDP requires CAP_NET_RAW). This skill uses only `curl` (TCP) and `python3` (UDP via sockets) — so it works in containers without extra capabilities.

3. **Concurrency limits.** Default `CONCURRENT=10` keeps system load reasonable. On slow connections, reduce to 5.

4. **DNS hijack IPs.** Known hijack IPs: `127.0.0.1`, `0.0.0.0`, `10.10.34.34`. If a domain resolves to these, it's likely censored.

5. **SNI-based blocking.** Some domains are accessible via IP but blocked when the SNI field contains the domain name. The diagnostics script tests for this pattern.

## Verification

After running diagnostics, verify the script executed correctly:

```bash
terminal(command="bash /data/.hermes/skills/network/net-checker-iran/scripts/diagnostics.sh 2>&1 | tail -5")
```

Expected: "Diagnostics Complete" timestamp line with no traceback errors.
