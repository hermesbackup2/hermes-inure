# Git hook bodies for vault auto-sync

Copy each block into the named file under `<vault>/.git/hooks/`, then `chmod +x`.
Replace `main` with `master` if the default branch differs.

## `.git/hooks/post-commit`
```bash
#!/bin/bash
# Auto-push after each local commit
set -e
VAULT_PATH="/data/obsidian-vault"
cd "$VAULT_PATH"
git push origin main 2>/dev/null || git push origin master 2>/dev/null
echo "[$(date)] post-commit: pushed to origin"
```

## `.git/hooks/post-merge`
```bash
#!/bin/bash
# Auto-pull --rebase after a git pull/merge
set -e
VAULT_PATH="/data/obsidian-vault"
cd "$VAULT_PATH"
git pull --rebase origin main 2>/dev/null || git pull --rebase origin master 2>/dev/null
echo "[$(date)] post-merge: pulled from origin"
```

## `.git/hooks/pre-push`
```bash
#!/bin/bash
# Optional: pre-check before push (runs on `git push`)
set -e
VAULT_PATH="/data/obsidian-vault"
cd "$VAULT_PATH"
git push origin main 2>/dev/null || git push origin master 2>/dev/null
echo "[$(date)] pre-push: pushed to origin"
```

## Notes
- The PAT must already be embedded in the remote URL for these to authenticate:
  `git remote set-url origin https://<TOKEN>@github.com/<user>/<repo>.git`
- If the account is suspended (403 "Your account is suspended"), these hooks fail
  silently on push. The vault folder remains fully usable on disk; commits just
  don't reach the remote until the account is restored.
- To disable a hook temporarily: `chmod -x <vault>/.git/hooks/post-commit`
