#!/usr/bin/env python3
"""
IP Security Analyzer — queries myip.theazizi.ir JSON API
and displays a formatted security report.

Usage: python3 analyze_ip.py [--json] [--ip <address>]
"""

import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

API_BASE = "https://myip.theazizi.ir"


def fetch_json(ip=None):
    """Fetch IP analysis from the API."""
    url = f"{API_BASE}/json"
    if ip:
        url += f"?ip={ip}"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read())
    except urllib.error.URLError as e:
        return {"status": "error", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def risk_color(score):
    """Return emoji based on abuse confidence score."""
    if score is None:
        return "⚪ Unknown"
    if score == 0:
        return "🟢 Clean"
    if score < 25:
        return "🟡 Low risk"
    if score < 75:
        return "🟠 Medium risk"
    return "🔴 High risk"


def format_report(data):
    """Format the API response as a readable report."""
    if data.get("status") != "success":
        return f"❌ Error: {data.get('error', 'Unknown error')}"

    lines = []
    lines.append("╔══════════════════════════════════════════════╗")
    lines.append("║        IP Security Analyzer Report          ║")
    lines.append("╚══════════════════════════════════════════════╝")
    lines.append("")

    # IP
    ip = data.get("ip", {})
    lines.append(f"📡 IP Address: {ip.get('address', 'N/A')} ({ip.get('version', '')})")
    lines.append("")

    # Network
    net = data.get("network", {})
    cls = net.get("localClassification", {})
    flags = cls.get("flags", {})
    lines.append("🌐 Network")
    lines.append(f"   ISP: {net.get('isp', 'N/A')}")
    lines.append(f"   ASN: AS{net.get('asn', 'N/A')}")
    lines.append(f"   Type: {cls.get('type', 'N/A')}")
    lines.append(f"   Hosting: {'✅' if flags.get('hostingName') else '❌'}")
    lines.append(f"   VPN/Proxy: {'⚠️ YES' if flags.get('vpnProxyName') else '❌ No'}")
    lines.append(f"   Mobile: {'📱' if flags.get('mobileName') else '❌'}")
    lines.append(f"   Residential: {'🏠' if flags.get('residentialName') else '❌'}")
    lines.append(f"   Tor: {'🧅 YES' if flags.get('abuseTor') else '❌ No'}")
    lines.append("")

    # Location
    loc = data.get("location", {})
    lines.append("📍 Location")
    lines.append(f"   Country: {loc.get('country', 'N/A')} ({loc.get('countryCode', '')})")
    lines.append(f"   Region: {loc.get('region', 'N/A')}")
    lines.append(f"   City: {loc.get('city', 'N/A')}")
    lines.append(f"   Timezone: {loc.get('timezone', 'N/A')}")
    lines.append(f"   Coordinates: {loc.get('latitude', 'N/A')}, {loc.get('longitude', 'N/A')}")
    lines.append(f"   Cloudflare Colo: {loc.get('colo', 'N/A')}")
    lines.append("")

    # Connection
    conn = data.get("connection", {})
    lines.append("🔗 Connection")
    lines.append(f"   TLS: {conn.get('tlsVersion', 'N/A')}")
    lines.append(f"   Cipher: {conn.get('tlsCipher', 'N/A')}")
    lines.append(f"   HTTP: {conn.get('httpProtocol', 'N/A')}")
    lines.append(f"   User-Agent: {conn.get('userAgent', 'N/A')}")
    if conn.get("ja3Hash"):
        lines.append(f"   JA3: {conn['ja3Hash']}")
    if conn.get("ja4"):
        lines.append(f"   JA4: {conn['ja4']}")
    lines.append("")

    # Browser Fingerprint
    sec_ua = conn.get("secChUa", "")
    sec_fetch = conn.get("secFetchSite", "")
    if sec_ua or sec_fetch:
        lines.append("🔍 Browser Fingerprint")
        lines.append(f"   sec-ch-ua: {conn.get('secChUa', 'N/A')}")
        lines.append(f"   sec-ch-ua-mobile: {conn.get('secChUaMobile', 'N/A')}")
        lines.append(f"   sec-ch-ua-platform: {conn.get('secChUaPlatform', 'N/A')}")
        lines.append(f"   sec-fetch-site: {conn.get('secFetchSite', 'N/A')}")
        lines.append(f"   sec-fetch-mode: {conn.get('secFetchMode', 'N/A')}")
        lines.append(f"   sec-fetch-dest: {conn.get('secFetchDest', 'N/A')}")
        lines.append("")

    # Cloudflare Signals
    cf = data.get("cloudflareSignals", {})
    if cf.get("botScore") is not None:
        lines.append("🤖 Cloudflare Bot Score")
        lines.append(f"   Score: {cf['botScore']}/100")
        lines.append(f"   Verified Bot: {cf.get('verifiedBot', 'N/A')}")
        lines.append(f"   Corporate Proxy: {cf.get('corporateProxy', 'N/A')}")
        lines.append("")

    # External Intel
    ext = data.get("externalIntel", {})

    # IPinfo
    ipinfo = ext.get("ipinfoLite", {})
    if ipinfo.get("ok"):
        parsed = ipinfo.get("parsed", {})
        lines.append("🔎 IPinfo Lite")
        lines.append(f"   ASN: {parsed.get('asn', 'N/A')} ({parsed.get('asName', 'N/A')})")
        lines.append(f"   Domain: {parsed.get('asDomain', 'N/A')}")
        lines.append("")

    # AbuseIPDB
    abuse = ext.get("abuseipdb", {})
    if abuse.get("ok"):
        parsed = abuse.get("parsed", {})
        score = parsed.get("abuseConfidenceScore")
        lines.append("🛡️ AbuseIPDB")
        lines.append(f"   Abuse Score: {score}/100 — {risk_color(score)}")
        lines.append(f"   Total Reports: {parsed.get('totalReports', 0)}")
        lines.append(f"   Distinct Users: {parsed.get('numDistinctUsers', 0)}")
        lines.append(f"   Usage Type: {parsed.get('usageType', 'N/A')}")
        lines.append(f"   ISP: {parsed.get('isp', 'N/A')}")
        lines.append(f"   Is Tor: {'🧅 YES' if parsed.get('isTor') else '❌ No'}")
        lines.append(f"   Whitelisted: {'✅' if parsed.get('isWhitelisted') else '❌'}")
        last_report = parsed.get("lastReportedAt")
        if last_report:
            lines.append(f"   Last Reported: {last_report}")
        lines.append("")

    # WebRTC note
    lines.append("⚠️ WebRTC Leak Test: Requires a browser. Visit the page directly:")
    lines.append(f"   {API_BASE}")
    lines.append("")

    lines.append(f"📅 Generated: {data.get('generatedAt', 'N/A')}")
    lines.append(f"📦 Version: {data.get('version', 'N/A')}")

    return "\n".join(lines)


def main():
    raw_json = "--json" in sys.argv
    target_ip = None

    if "--ip" in sys.argv:
        idx = sys.argv.index("--ip")
        if idx + 1 < len(sys.argv):
            target_ip = sys.argv[idx + 1]

    data = fetch_json(target_ip)

    if raw_json:
        print(json.dumps(data, indent=2))
    else:
        print(format_report(data))


if __name__ == "__main__":
    main()
