---
name: github-iran-account
description: GitHub Iran suspension appeal — OFAC scope and appeal steps.
platforms: [linux, macos, windows]
version: 1
author: hermes-curator
license: mit
metadata:
  hermes:
    tags: [github, iran, ofac, sanctions, appeal, account-suspended]
    related_skills: [github/github-auth, github/github-repo-management]
---

## When to Use
- A user reports their GitHub account is suspended (push returns 403 "account suspended"),
  especially an Iran-based user.
- User asks whether making repos public will unban them — it will NOT for Iran.
- Drafting a GitHub support appeal for a trade-control flag.

# GitHub accounts for Iran-based users

Iran-based GitHub users face trade-control (OFAC) flags that can suspend an account or block `git push`. This skill captures the authoritative policy and the working appeal path — and a common misconception to avoid giving wrong advice.

## Authoritative policy (GitHub OFAC license)
- GitHub holds an OFAC license to provide **ALL** GitHub.com cloud services in Iran — **public AND private**, for individuals and organizations, **free AND paid**.
- Therefore an Iran-based account is **NOT** limited to public repositories only.
- Account restriction decisions may be based on signals such as **IP address** and **payment history** — NOT nationality or ethnicity.
- Specially Designated Nationals (SDNs), other denied/blocked parties, and certain government officials remain restricted wherever located.

## Symptom pattern
- `git push` fails with `remote: Your account is suspended` / HTTP 403.
- The PAT token and `git clone` / API reads may still work — only **write** operations are blocked.
- This usually means an **erroneous flag** (e.g. VPN / shared-IP, payment signal), not an actual sanctions violation.

## Appeal workflow (verified working path)
1. Submit a support ticket at support.github.com (or reply to the suspension email).
2. Focus the request on a **manual review of the account flag** and that you believe it was **flagged in error**.
3. State you are an **individual user in Iran** and that, under GitHub's policy, Iran-based users are generally eligible for GitHub cloud services (both public and private).
4. State you are **NOT an SDN, blocked/denied party, or certain government official**.
5. Be ready to provide any **verification information** GitHub Support requests (identity check). If they verify you are not in a restricted category, the flag is removed.

## Common misconception — DO NOT do this for Iran
- Making all repositories **public** is the documented fix for *some other* trade-restricted situations, but **NOT** for Iran — Iran policy already covers private repos.
- Do **not** tell the user to make repos public to get unbanned; that is wrong for Iran and may expose private data unnecessarily.
- Do **not** advise creating a new account via VPN to bypass — that violates ToS and risks a faster ban.

## Pitfalls
- A suspended account blocks push even though the token still authenticates. Git hooks / scripts using the token will fail until the account is restored.
- GitHub may request verification; respond promptly with the requested docs (redact serial numbers / national-ID numbers if sending ID — name + photo usually suffices).

## See also
- `references/github-trade-controls.md` — verbatim quotes from GitHub's official support modal on Iran account restoration.