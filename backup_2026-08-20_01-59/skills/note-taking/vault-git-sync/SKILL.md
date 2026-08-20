---
name: vault-git-sync
description: Sync a git notes vault with git hooks, not cron.
version: 1
author: hermes
license: mit
metadata:
  hermes:
    tags: [obsidian, git, sync, hooks, vault, github]
    related_skills: [obsidian, github-repo-management]
---

# Vault Git Sync (hooks, not cron)

Use this when a notes vault lives in a local folder AND a git remote and the user wants it kept in sync without a polling cron job. The user explicitly prefers **git hooks over cron**: hooks fire only on real commits/fetches, no 15-minute overhead.

## When to use
- Vault is already cloned from a remote repo.
- You want every `git commit` to push, and every `git pull` to rebase, automatically.
- The user said "use hooks, not cron" or dislikes scheduled polling.

## Setup steps
1. Resolve the absolute vault path. File tools do NOT expand `$OBSIDIAN_VAULT_PATH`; pass a concrete path. Persist it in `~/.bashrc` so it survives restarts:
   `export OBSIDIAN_VAULT_PATH="/data/obsidian-vault"`
2. Clone once, set git identity, embed PAT in remote URL (non-interactive push/pull):
   `git config user.name ... && git config user.email ...`
   `git remote set-url origin https://<TOKEN>@github.com/<user>/<repo>.git`
   Token needs `repo` scope (classic PAT) or contents+metadata (fine-grained).
3. Install executable hooks from `references/git-hook-sync.md` into `<vault>/.git/hooks/`:
   - `post-commit` → auto-push after each commit
   - `post-merge` → auto-pull --rebase after a pull/merge
   - `pre-push` → optional pre-check
   `chmod +x .git/hooks/post-commit .git/hooks/post-merge .git/hooks/pre-push`

## Pitfall: 403 on push — "suspended" vs "scope missing"
A raw `git push` can fail with 403 for TWO different reasons. Read the response body to tell them apart:
- **Scope error:** `error validating token: missing required scope 'read:org'` — token lacks a scope. Re-auth `gh auth login --with-token` or mint a broader-scope token.
- **Account suspended (sanctions / OFAC):** `remote: Your account is suspended. Please visit https://support.github.com` — NOT a scope problem. The token still works for `clone`/read API, but **write operations are blocked**. Common for users in sanctioned regions (Iran, Syria, Crimea, Cuba, N. Korea) regardless of public/private repos — GitHub requires a Support review to lift the flag.

If suspended:
- Hooks **fail silently on push** — keep a local-only fallback (vault folder is still fully usable on disk).
- File a Support appeal focused on "flagged in error" + "individual user in Iran, not an SDN/blocked party/government official." GitHub's OFAC license covers BOTH public AND private services for Iran-based individuals, so suspension is usually an erroneous IP/payment flag, NOT automatic due to private repos. Do NOT preemptively make repos public or create a new account (ToS violation → faster ban).
- Ref: https://docs.github.com/en/site-policy/other-site-policies/github-and-trade-controls

## Notes
- Complements the `obsidian` skill (reading/writing vault notes). That skill is bundled/protected; to fold these hooks into it, run `hermes curator adopt obsidian`.
- A cron alternative (every 15m push/pull script) works but is heavier; prefer hooks unless the user needs periodic pull-without-commit.
