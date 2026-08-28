---
name: github-account-appeal
description: Appeal a suspended GitHub account for Iran-region users.
platforms: [linux, macos, windows]
---

# GitHub Account Appeal (suspension / trade-control flag)

Use when a GitHub account is **suspended**, shows "account suspended" on sign-in, or push returns `403 Your account is suspended`. Especially relevant for users in Iran or other US-sanctioned regions.

## Key policy facts (non-obvious, verified Aug 2026)
- GitHub holds an **OFAC license** that lets it provide **all cloud services — public AND private, free AND paid — to individuals and orgs in Iran**. Sanctioned-region users are NOT limited to public repos only.
- GitHub does **NOT** flag users based on **nationality or ethnicity**. Flags are based on signals like **IP address** (e.g. VPN/proxy shared IPs) and **payment history**.
- The "make your repos public to restore access" path is documented for *some other* trade-restricted situations — **but NOT for Iran**. For Iran-based accounts the documented fix is a **manual review / appeal with verification info**.
- Restricted categories that may still be blocked wherever located: SDNs (Specially Designated Nationals), other denied/blocked parties, certain government officials.

## Appeal process
1. Open a ticket at https://support.github.com (or reply to the suspension email from `support@github.com`).
2. State clearly: individual user in Iran; believe the account was **flagged in error**; under GitHub policy Iran-based users are eligible for cloud services; you are **not** an SDN / blocked party / government official.
3. Keep focus on a **manual review of the account flag** — do NOT volunteer to make repos public (unnecessary and may expose private data).
4. GitHub will request **verification information** to confirm you're not in a restricted category. Provide it promptly.
5. If verified, the flag is removed and sign-in/push are restored.

## Pitfalls
- **Do NOT create a new account** to work around the suspension — that's a ToS violation and risks a faster, harder ban.
- **Do NOT lie about your location** — GitHub detects IP region; dishonesty violates ToS and can forfeit the account.
- **Do NOT delete/convert private repos preemptively** — wait for Support's actual reason before changing anything. The cause may simply be an IP/payment flag, not the repo visibility.
- A read-only PAT may still work (clone/API) while write (push) is blocked — this pattern suggests a write restriction, not full account deletion.

## Templates
See `references/iran-appeal.md` for a ready-to-send appeal draft (English, since GitHub Support only handles English).
