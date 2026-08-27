---
name: ip-security-analyzer
description: "Analyze IP addresses for security, location, and abuse data."
version: 0.1.0
author: Hermes
metadata:
  hermes:
    tags: [IP, Security, AbuseIPDB, VPN, Cloudflare]
---

# IP Security Analyzer

Analyze any IP address (or your own) using the [myip.theazizi.ir](https://myip.theazizi.ir) API. Returns network classification (hosting/VPN/mobile/residential), geographic location, TLS fingerprint, AbuseIPDB abuse score, IPinfo ASN data, and Cloudflare bot signals.

This is a read-only lookup tool. It does NOT block, scan, or modify anything.

## When to Use

- User asks "what's my IP" or "where am I"
- User asks to analyze an IP for abuse/safety
- User asks if an IP is a VPN, proxy, datacenter, or residential
- User asks about ISP, ASN, or hosting provider for an IP
- User asks about AbuseIPDB reports for an IP
- User asks to check if an IP is on a blocklist

## Prerequisites

- `python3` — stdlib only, no pip installs
- Network access to `myip.theazizi.ir`
- No API keys required (free public API)

## How to Run

Invoke through the `terminal` tool:

```bash
# Analyze your own IP
terminal(command="python3 /data/.hermes/skills/network/ip-security-analyzer/scripts/analyze_ip.py")

# Analyze a specific IP
terminal(command="python3 /data/.hermes/skills/network/ip-security-analyzer/scripts/analyze_ip.py --ip 8.8.8.8")

# Get raw JSON output
terminal(command="python3 /data/.hermes/skills/network/ip-security-analyzer/scripts/analyze_ip.py --json")
```

## Quick Reference

| Flag | Purpose |
|---|---|
| `--ip <addr>` | Analyze a specific IP instead of your own |
| `--json` | Output raw JSON instead of formatted report |

## Procedure

1. **Run the script** via `terminal` with the appropriate flags.
   - Completion: formatted report or JSON output printed.

2. **Parse the output** for the user's question.
   - IP & location → first section
   - VPN/hosting detection → Network section flags
   - Abuse score → AbuseIPDB section

3. **Report findings** in a concise summary.

## Pitfalls

1. **403 Forbidden without User-Agent.** The API blocks bare `curl`/`urllib` without a browser-like User-Agent. The script includes one automatically.

2. **WebRTC leak test is browser-only.** The API page has a client-side WebRTC test. From CLI you can only get server-side data. Direct users to `https://myip.theazizi.ir` for the full browser test.

3. **Rate limits.** The API is free and public. Avoid hammering it — one request per analysis is enough.

4. **Datacenter IPs may show high abuse scores.** Hosting providers like Railway, AWS, GCP naturally accumulate reports. A score <25 on a datacenter IP is normal.

## Verification

```bash
terminal(command="python3 /data/.hermes/skills/network/ip-security-analyzer/scripts/analyze_ip.py 2>&1 | head -5")
```

Expected: "IP Security Analyzer Report" header and a valid IP address on the second content line.
