# Ready-to-Use Git Hook Templates

Copy these to `.git/hooks/` in your vault and `chmod +x`.

---

## post-commit — Auto-push after commit

```bash
#!/bin/bash
# Runs after every successful commit
# Place in .git/hooks/post-commit

set -e
cd "$(git rev-parse --show-toplevel)"

# Push to origin (try main then master)
git push origin main 2>/dev/null || git push origin master 2>/dev/null

echo "[$(date '+%Y-%m-%d %H:%M:%S')] post-commit: pushed to origin"
```

---

## post-merge — Auto-pull after git pull/merge

```bash
#!/bin/bash
# Runs after git pull or merge completes
# Place in .git/hooks/post-merge

set -e
cd "$(git rev-parse --show-toplevel)"

# Pull latest (rebase local commits on top)
git pull --rebase origin main 2>/dev/null || git pull --rebase origin master 2>/dev/null

echo "[$(date '+%Y-%m-%d %H:%M:%S')] post-merge: pulled from origin"
```

---

## pre-push — Optional validation before push

```bash
#!/bin/bash
# Runs before push; exit non-zero to abort
# Place in .git/hooks/pre-push

set -e
cd "$(git rev-parse --show-toplevel)"

# Example: validate all .md files have frontmatter
# for f in $(git diff --cached --name-only -- '*.md'); do
#     if ! head -1 "$f" | grep -q '^---$'; then
#         echo "ERROR: $f missing frontmatter"
#         exit 1
#     fi
# done

# Example: run markdown linter
# npx markdownlint '**/*.md' --config .markdownlint.json

exit 0
```

---

## Install All at Once

```bash
VAULT_PATH="/path/to/your/vault"
cd "$VAULT_PATH"

cat > .git/hooks/post-commit << 'EOF'
#!/bin/bash
set -e
cd "$(git rev-parse --show-toplevel)"
git push origin main 2>/dev/null || git push origin master 2>/dev/null
echo "[$(date '+%Y-%m-%d %H:%M:%S')] post-commit: pushed to origin"
EOF

cat > .git/hooks/post-merge << 'EOF'
#!/bin/bash
set -e
cd "$(git rev-parse --show-toplevel)"
git pull --rebase origin main 2>/dev/null || git pull --rebase origin master 2>/dev/null
echo "[$(date '+%Y-%m-%d %H:%M:%S')] post-merge: pulled from origin"
EOF

cat > .git/hooks/pre-push << 'EOF'
#!/bin/bash
set -e
cd "$(git rev-parse --show-toplevel)"
exit 0
EOF

chmod +x .git/hooks/post-commit .git/hooks/post-merge .git/hooks/pre-push
echo "Hooks installed and executable"
```

---

## For Team Vaults: Track Hooks in Repo

```bash
# In vault root
mkdir -p .githooks
cp .git/hooks/post-commit .githooks/
cp .git/hooks/post-merge .githooks/
cp .git/hooks/pre-push .githooks/
git add .githooks/
git commit -m "Add git hook templates"
git config core.hooksPath .githooks
```

Now hooks are versioned and shared. New clones run:
```bash
git config core.hooksPath .githooks
```