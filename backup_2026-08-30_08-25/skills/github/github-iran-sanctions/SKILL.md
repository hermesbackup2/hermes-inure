---
name: github-iran-sanctions
description: Appeal a GitHub suspension and recover an Iran-based account.
version: 1
author: hermes-agent
license: mit
metadata:
  hermes:
    tags: [github, iran, sanctions, account-recovery, appeal]
    related_skills: [github/github-auth, github/github-repo-management]
---

# GitHub Account Recovery — Iran / Trade Controls

## When to Use
- A GitHub account based in Iran shows "account suspended" on login, or push fails with `403 Your account is suspended`.
- The user wants to appeal and restore access rather than create a new account.
- Do NOT use this for ordinary repo/PR work — only for trade-control suspension recovery.

For Iran-based GitHub users whose account is suspended (403 on push, cannot sign in, "account suspended" on login).

## Key policy facts (GitHub OFAC license)
- GitHub holds an OFAC license permitting BOTH public AND private cloud services in Iran, for individuals and orgs, free and paid. Iran-based users are NOT limited to public-only repos.
- Suspension is usually an ERRONEOUS FLAG based on signals like IP address (VPN/proxy) or payment history — NOT nationality or ethnicity.
- Categories still blocked wherever located: SDNs (Specially Designated Nationals), other denied/blocked parties, certain government officials.

## WRONG assumptions to avoid
- Do NOT assume you must make repos public to be unbanned. The "convert to public" path is documented for OTHER trade-restricted situations, NOT Iran. For Iran, private repos are allowed once the flag is cleared.
- Do NOT create a new account on a VPN to bypass — risks ToS violation and faster ban.
- Do NOT proactively change repo visibility before the flag is reviewed; focus the request on a manual flag review.

## Appeal process (verified working path)
1. Submit a support ticket at support.github.com (or reply to the suspension email).
2. Keep focus on: manual review of the account flag; state you believe it was flagged in error.
3. State: you are an individual user in Iran; under GitHub policy Iran-based users are generally eligible for all cloud services (public and private).
4. State: you are NOT an SDN, blocked/denied party, or government official.
5. Be ready to provide any verification information GitHub Support requests (identity proof, etc.).
6. If GitHub verifies you are not in a restricted category, the flag is removed and sign-in returns.

## Reference
- GitHub and Trade Controls: https://docs.github.com/en/site-policy/other-site-policies/github-and-trade-controls
- Typical response time: a few business days. Watch the Spam folder for the verification email.
- Account restriction decisions may be based on IP address and payment history; travel/location signals can trigger flags, and the appeal process exists for unintentional flags.
- `references/appeal-message.md` — Copy-paste appeal message template (verified: successfully moved a suspended Iran account into the Support review queue). Replace <USERNAME> and submit at support.github.com.
