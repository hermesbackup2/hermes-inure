---
name: github-sanctions-appeal
description: Appeal GitHub Iran/trade-control account suspensions.
version: 1.0.0
author: Hermes Agent (session-derived)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Sanctions, OFAC, Iran, Account-Suspension, Appeal, Troubleshooting]
    related_skills: [github-auth, github-repo-management]
---

# GitHub Sanctions / Trade-Control Account Suspension & Appeal

## When to Use
Use this when a GitHub account shows "suspended" or returns 403 on push, but the token still authenticates for read operations. This is usually a **sanctions/trade-control flag**, not a credential problem. Trigger immediately if the user is in Iran or another restricted region and their account became inaccessible.

## Background
A GitHub account can be flagged under US trade controls (OFAC). For Iran specifically, GitHub holds a license covering public AND private services, so a suspension is most often an erroneous IP/payment-based flag rather than a real sanctions violation.

## Policy (GitHub + OFAC)
- GitHub holds an OFAC license permitting **ALL** GitHub.com cloud services in Iran — public **AND** private, free **AND** paid — for individuals/orgs NOT in a restricted category.
- A "suspended" / 403-on-push state is usually NOT because the user is Iranian. It is typically an **erroneous flag** triggered by:
  - IP-address signals (VPN/proxy/shared IPs common in restricted regions)
  - Payment-history patterns
- Nationality/ethnicity are NOT used to flag users.
- Still restricted wherever located: SDNs (Specially Designated Nationals), other denied/blocked parties, certain government officials.

## Appeal path (when "account suspended")
1. Submit a support ticket at https://support.github.com (or reply to the suspension email).
2. Focus the request on: **manual review of the account flag** + **believed flagged in error**.
3. State: individual user in Iran; under GitHub policy Iran-based users are generally eligible for cloud services (public + private).
4. State: NOT an SDN, NOT a blocked/denied party, NOT a government official.
5. Be ready to provide verification info GitHub Support requests (identity check).
6. If verified not in a restricted category, the flag is removed and sign-in is restored (typically 3–7 business days).

## Do NOT
- Do NOT assume you must make repos public — that path applies to OTHER trade-restricted regions, NOT Iran (Iran has the OFAC license, so private repos stay allowed).
- Do NOT create a new account to bypass — risks ToS violation / faster ban.
- Do NOT lie about location — GitHub detects IP; false info = ToS violation.

## Working appeal template (English — GitHub Support reads English only)
Subject: Appeal: Account <user> suspended in error — request flag review

Body:
"My account <user> is suspended and I cannot sign in. Based on GitHub's published trade-control policy, Iran-based users are eligible for both public and private services under GitHub's OFAC license, so my suspension was likely an erroneous flag rather than a sanctions restriction.

I am an individual developer based in Iran. I am: NOT an SDN, NOT a blocked/denied party, NOT a government official.

My account was likely flagged due to IP-address signals (I use VPN/proxy due to regional network restrictions) or payment-history patterns, not any actual sanctions violation.

I request a manual review of the account flag. Please advise what verification information you need to confirm I am not in a restricted category, and I will provide it promptly."

## Auth workaround when `gh --with-token` fails (related to github-auth)
- `gh auth login --with-token` validates scopes and may reject a token missing `read:org` even if `repo` scopes are present ("error validating token: missing required scope 'read:org'").
- When gh CLI auth is blocked/unavailable, fall back to:
  - git clone/push with token embedded in the remote URL: `git remote set-url origin https://<user>:<token>@github.com/<owner>/<repo>.git`
  - API via `curl -H "Authorization: token $TOKEN" https://api.github.com/...`
- This fallback worked in-session when gh rejected the token but the token was otherwise valid.

## Related skills
- `github-auth` — credential setup, token scopes, headless login pitfalls (bundled; protected).
- `github-repo-management` — clone/create/fork repos, manage remotes.
