---
name: skill-authoring
description: "Author SKILL.md skills for Hermes and OpenClaw."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [skill, authoring, SKILL.md, workflow, validation, openclaw, hermes-agent]
    related_skills: [hermes-agent-skill-authoring, hermes-agent]
    homepage: https://github.com/NousResearch/hermes-agent
---

# Skill Authoring

Comprehensive guide for creating high-quality, reusable agent skills compatible with both **Hermes Agent** and **OpenClaw** ecosystems. Covers the full lifecycle: design → scaffold → validate → test → publish.

## When to Use

- User asks to create a new skill from scratch
- User wants to improve/refactor an existing skill
- User wants to validate skill structure before publishing
- User wants to migrate skills between ecosystems
- User asks "how do I write a good SKILL.md?"

## Quick Reference

| Task | Command / Action |
|------|------------------|
| Scaffold new skill | `skill_manage(action='create', name='my-skill', category='devops', content='...')` |
| Validate frontmatter | `python -c "import yaml; yaml.safe_load(open('skills/my-skill/SKILL.md').read().split('---')[1])"` |
| Quick validate (OpenClaw) | `python skills/skill-creator/scripts/quick_validate.py skills/my-skill` |
| List all skills | `skills_list()` |
| View skill | `skill_view(name='my-skill')` |
| Patch skill | `skill_manage(action='patch', name='my-skill', old_string='...', new_string='...')` |
| Publish to ClawHub | Push to GitHub → Submit PR to `openclaw/clawhub` registry |

---

## Skill Anatomy (Both Ecosystems)

### Directory Structure

```text
my-skill/
├── SKILL.md              # Required: frontmatter + markdown body
├── scripts/              # Optional: deterministic helpers (bash, python)
├── references/           # Optional: docs loaded only when needed
├── assets/               # Optional: templates, media, output resources
└── agents/               # Optional: UI metadata (OpenClaw)
```

### Frontmatter (YAML)

**Hermes Agent (minimal):**
```yaml
---
name: my-skill
description: "One-line trigger phrase. What this skill does."
version: 1.0.0
author: Your Name
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [category, subcategory, keywords]
    related_skills: [other-skill, another-skill]
    homepage: https://github.com/user/repo
---
```

**OpenClaw (extended):**
```yaml
---
name: my-skill
description: "One-line trigger phrase. What this skill does."
homepage: https://github.com/user/repo
metadata:
  openclaw:
    emoji: "🔧"
    requires:
      bins: ["required-cli-tool"]
      env: ["REQUIRED_ENV_VAR"]
    install:
      - id: brew
        kind: brew
        formula: tool-name
        bins: ["tool-name"]
        label: "Install Tool (brew)"
      - id: uv
        kind: uv
        package: package-name
        bins: ["cli-tool"]
        label: "Install via uv"
    allowed-tools: ["terminal", "web_search"]
    user-invocable: true
    license: MIT
---
```

**Unified (recommended — works in both):**
```yaml
---
name: my-skill
description: "One-line trigger phrase. What this skill does."
version: 1.0.0
author: Your Name
license: MIT
platforms: [linux, macos, windows]
homepage: https://github.com/user/repo
metadata:
  hermes:
    tags: [category, subcategory, keywords]
    related_skills: [other-skill]
  openclaw:
    emoji: "🔧"
    requires:
      bins: ["required-cli-tool"]
      env: ["REQUIRED_ENV_VAR"]
    install:
      - kind: brew
        formula: tool-name
        bins: ["tool-name"]
      - kind: uv
        package: package-name
        bins: ["cli-tool"]
    allowed-tools: ["terminal", "web_search"]
    user-invocable: true
---
```

### Frontmatter Fields Explained

| Field | Required | Purpose | Notes |
|-------|----------|---------|-------|
| `name` | ✅ | Skill identifier (lowercase, hyphens) | Must match directory name |
| `description` | ✅ | Trigger phrase for auto-loading | Keep under 120 chars; noun phrase |
| `version` | ✅ | SemVer | Bump on meaningful changes |
| `author` | ✅ | Creator name/handle | |
| `license` | ✅ | SPDX identifier | MIT, Apache-2.0, etc. |
| `platforms` | ✅ | Target OS | `[linux, macos, windows]` |
| `homepage` | 🔶 | Source repo / docs | OpenClaw requires for registry |
| `metadata.heroku.tags` | 🔶 | Categorization | Used for discovery/filtering |
| `metadata.hermes.related_skills` | 🔶 | Cross-references | Enables "load related" |
| `metadata.openclaw.emoji` | 🔶 | Visual identifier | Single emoji char |
| `metadata.openclaw.requires.bins` | 🔶 | CLI dependencies | Auto-checked on load |
| `metadata.openclaw.requires.env` | 🔶 | Env var dependencies | Warn if missing |
| `metadata.openclaw.install` | 🔶 | Installation recipes | Multiple package managers |
| `metadata.openclaw.allowed-tools` | 🔶 | Toolset restriction | Security boundary |
| `metadata.openclaw.user-invocable` | 🔶 | Can user trigger directly? | Default: true |

---

## Markdown Body Structure

```markdown
# Skill Title

One-paragraph summary: what it does, when to use it.

## When to Use

- Trigger condition 1
- Trigger condition 2
- ...

## Prerequisites

- Required CLI tools
- Required env vars
- Required accounts/API keys

## Quick Reference

| Task | Command |
|------|---------|
| Common task | `exact command` |

## Procedure

### 1. Step Name

Explanation. Include exact commands.

```bash
# Copy-pasteable command
command --flags args
```

**Completion criteria:** How to know this step succeeded.

### 2. Next Step
...

## Common Patterns / Recipes

Pattern name: description

```bash
command
```

## Pitfalls

1. **Common mistake** — why it happens, how to avoid
2. **Another pitfall** — ...

## Validation

```bash
# Test the skill works
command-to-verify
```

Expected output: what success looks like.

## Related Skills

- [other-skill](other-skill) — why related
```

---

## Best Practices (Synthesized from Both Ecosystems)

### 1. Trigger-Critical Frontmatter
- **Description** must be a noun phrase: `"Extract text from PDFs"` not `"This skill extracts..."`
- Keep under 120 chars — used in skill index/tooltip
- Tags: 3-6 relevant keywords for discovery

### 2. Lean Body, Rich References
- **Body** = trigger logic + core workflow (what the agent needs to *start*)
- **References** = deep docs, API specs, examples (loaded on demand)
- **Scripts** = deterministic helpers only (no business logic in shell)

### 3. Exact Commands Over Prose
```markdown
# Bad
Run the build command with the right flags.

# Good
```bash
cargo build --release --target x86_64-unknown-linux-gnu
```
```

### 4. Completion Criteria Per Step
Every numbered step should have a verifiable "done" signal:
- File exists at path
- Command exits 0 with specific output
- API returns expected field

### 5. Pitfalls = Real Failure Modes
Document what *actually* broke during development:
- "Container lacks `ping`/`dig` — use `curl` + Python sockets instead"
- "API rate limits at 60/min — batch requests or use fallback"
- "Windows paths need `\\\\?\` prefix for >260 chars"

### 6. No Redundant Advice
Don't repeat what the base model already knows:
- ❌ "Use `await` for async functions"
- ❌ "Handle errors with try/catch"
- ✅ "This API returns 429 with `Retry-After` header — respect it"

### 7. Installation Recipes (OpenClaw)
Provide multiple install methods:
```yaml
install:
  - kind: brew
    formula: tool
  - kind: uv
    package: tool
  - kind: go
    module: github.com/user/tool@latest
  - kind: cargo
    crate: tool
  - kind: npm
    package: tool
```

### 8. Required Binaries Declaration
```yaml
requires:
  bins: ["tool-name"]
  env: ["API_KEY"]
```
Agent can auto-verify before loading.

---

## Validation Checklist

Run before publishing:

```bash
# 1. Frontmatter parses
python -c "
import yaml, sys
text = open('skills/my-skill/SKILL.md').read()
fm = text.split('---')[1]
data = yaml.safe_load(fm)
required = ['name', 'description', 'version', 'author', 'license', 'platforms']
missing = [f for f in required if f not in data]
if missing: sys.exit(f'Missing: {missing}')
print('✅ Frontmatter OK')
"

# 2. Name matches directory
python -c "
import os, yaml
name = yaml.safe_load(open('skills/my-skill/SKILL.md').read().split('---')[1])['name']
dir_name = os.path.basename(os.path.dirname('skills/my-skill/SKILL.md'))
assert name == dir_name, f'Name mismatch: {name} != {dir_name}'
print('✅ Name matches directory')
"

# 3. No broken internal links
python -c "
import re, os
text = open('skills/my-skill/SKILL.md').read()
for m in re.finditer(r'\]\((references|scripts|assets)/([^)]+)\)', text):
    path = f'skills/my-skill/{m.group(1)}/{m.group(2)}'
    if not os.path.exists(path):
        print(f'❌ Broken link: {path}')
    else:
        print(f'✅ Link OK: {path}')
"

# 4. Scripts are executable
for f in skills/my-skill/scripts/*; do
  [ -x "$f" ] || echo "❌ Not executable: $f"
done

# 5. OpenClaw quick_validate (if available)
python skills/skill-creator/scripts/quick_validate.py skills/my-skill
```

---

## Publishing Workflow

### To Hermes Agent (Local/Profile)
```bash
# 1. Place in profile skills dir
cp -r my-skill ~/.hermes/skills/

# 2. Or use skill_manage
skill_manage(action='create', name='my-skill', category='devops', content='...')

# 3. Verify it loads
hermes skills list | grep my-skill
```

### To OpenClaw (ClawHub Registry)
```bash
# 1. Push skill to your GitHub repo
git add skills/my-skill
git commit -m "feat: add my-skill"
git push

# 2. Submit to ClawHub
# Option A: Via CLI
npx clawhub publish skills/my-skill

# Option B: Via Web UI
# Go to https://clawhub.ai → "Publish Skill" → paste GitHub URL

# Option C: PR to openclaw/clawhub (community registry)
# Fork openclaw/clawhub → add entry → PR
```

### Cross-Ecosystem Compatibility
| Feature | Hermes | OpenClaw | Unified Approach |
|---------|--------|----------|------------------|
| Frontmatter | YAML | YAML | **Use unified frontmatter** |
| Body | Markdown | Markdown | **Same** |
| References | `references/` | `references/` | **Same** |
| Scripts | `scripts/` | `scripts/` | **Same** |
| Assets | `assets/` | `assets/` | **Same** |
| Install recipes | ❌ | ✅ | **Add for OpenClaw** |
| Requires bins | ❌ | ✅ | **Add for OpenClaw** |
| Allowed tools | ✅ | ✅ | **Same** |
| Emoji | ❌ | ✅ | **Add for OpenClaw** |
| Skill registry | Local/Profile | ClawHub | **Different** |

---

## Migration: Hermes → OpenClaw

```bash
# 1. Add OpenClaw metadata to frontmatter
# 2. Add install recipes for dependencies
# 3. Add requires.bins/env
# 4. Add emoji
# 5. Push to GitHub
# 6. Publish to ClawHub
```

## Migration: OpenClaw → Hermes

```bash
# 1. Copy skill to ~/.hermes/skills/
# 2. Hermes ignores unknown frontmatter keys (safe)
# 3. Add hermes.metadata.tags + related_skills
# 4. Verify with `hermes skills list`
```

---

## Templates

### Minimal Skill (Hermes-only)
```markdown
---
name: my-skill
description: "What this skill does in one line."
version: 1.0.0
author: Your Name
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [category, keyword]
---
# My Skill

## When to Use
- Trigger condition

## Procedure
1. **Step** — Command and verification
```

### Full Cross-Ecosystem Skill
```markdown
---
name: my-skill
description: "What this skill does in one line."
version: 1.0.0
author: Your Name
license: MIT
platforms: [linux, macos, windows]
homepage: https://github.com/user/repo
metadata:
  hermes:
    tags: [category, keyword1, keyword2]
    related_skills: [other-skill]
  openclaw:
    emoji: "🔧"
    requires:
      bins: ["required-tool"]
      env: ["API_KEY"]
    install:
      - kind: brew
        formula: required-tool
      - kind: uv
        package: required-tool
    allowed-tools: ["terminal", "web_search"]
    user-invocable: true
---
# My Skill

## When to Use
- Trigger condition 1
- Trigger condition 2

## Prerequisites
- `required-tool` — install via `brew install required-tool` or `uv tool install required-tool`
- `API_KEY` env var — get from https://example.com

## Quick Reference
| Task | Command |
|------|---------|
| Main action | `required-tool --flag arg` |

## Procedure
### 1. Setup
```bash
export API_KEY="your-key"
required-tool --version
```
✅ Verification: prints version

### 2. Execute
```bash
required-tool --input input.txt --output output.json
```
✅ Verification: `output.json` exists with expected keys

## Pitfalls
1. **API rate limit** — 60 req/min. Batch or use `--delay`.
2. **Tool missing on Windows** — use WSL or Docker.

## Validation
```bash
required-tool --help
```

## Related Skills
- [other-skill](other-skill) — complementary functionality
```

---

## Common Anti-Patterns to Avoid

| Anti-Pattern | Why It's Bad | Fix |
|--------------|--------------|-----|
| `description` > 200 chars | Truncated in index, not trigger-critical | Shorten to noun phrase |
| No `version` | Can't track updates/breaking changes | Add SemVer |
| Hardcoded paths (`/home/user/...`) | Breaks on other machines | Use `$HOME`, `$HERMES_HOME` |
| Secrets in frontmatter | Leaked in registry/index | Use `requires.env` + `.env` |
| No `pitfalls` section | Users hit same bugs | Document real failures |
| Scripts with business logic | Hard to test/debug | Move logic to references; scripts = glue |
| Missing `license` | Legal ambiguity for reuse | Add SPDX identifier |
| `name` ≠ directory | Loader failures | Keep identical |
| Generic advice ("use await") | Wastes tokens, model knows this | Only skill-specific gotchas |

---

## References

- Hermes Agent Skills: https://hermes-agent.nousresearch.com/docs/skills
- OpenClaw Skills Spec: https://docs.openclaw.ai/skills/getting-started
- ClawHub Registry: https://clawhub.ai
- Awesome OpenClaw Skills: https://github.com/VoltAgent/awesome-openclaw-skills
- Skill Creator (OpenClaw): `skills/skill-creator/`

---

## Validation Script (Copy to `skills/skill-authoring/scripts/validate.py`)

```python
#!/usr/bin/env python3
"""Validate a skill directory for cross-ecosystem compatibility."""
import os, sys, yaml, re
from pathlib import Path

def validate_skill(skill_path: Path) -> list[str]:
    errors = []
    warnings = []
    
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return [f"Missing SKILL.md in {skill_path}"]
    
    text = skill_md.read_text()
    if not text.startswith("---\n"):
        errors.append("Missing YAML frontmatter (must start with '---')")
        return errors
    
    try:
        fm = yaml.safe_load(text.split("---", 2)[1])
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML: {e}")
        return errors
    
    # Required fields
    required = ['name', 'description', 'version', 'author', 'license', 'platforms']
    for f in required:
        if f not in fm:
            errors.append(f"Missing required frontmatter field: {f}")
    
    # Name matches directory
    if fm.get('name') != skill_path.name:
        errors.append(f"name ({fm.get('name')}) != directory ({skill_path.name})")
    
    # Description length
    desc = fm.get('description', '')
    if len(desc) > 120:
        warnings.append(f"Description >120 chars ({len(desc)}), may be truncated in index")
    
    # License SPDX
    license_val = fm.get('license', '')
    if license_val and not re.match(r'^[A-Za-z0-9\-\.]+$', license_val):
        warnings.append(f"License should be SPDX identifier (e.g., MIT, Apache-2.0)")
    
    # OpenClaw recommendations
    openclaw = fm.get('metadata', {}).get('openclaw', {})
    if not openclaw:
        warnings.append("No openclaw metadata — skill won't publish to ClawHub")
    else:
        if 'requires' not in openclaw:
            warnings.append("openclaw.requires missing — declare bins/env dependencies")
        if 'install' not in openclaw:
            warnings.append("openclaw.install missing — add installation recipes")
        if 'emoji' not in openclaw:
            warnings.append("openclaw.emoji missing — add single emoji for UI")
    
    # Check references/scripts/assets links
    for m in re.finditer(r'\]\((references|scripts|assets)/([^)]+)\)', text):
        target = skill_path / m.group(1) / m.group(2)
        if not target.exists():
            errors.append(f"Broken link: {m.group(1)}/{m.group(2)}")
    
    # Scripts executable
    scripts_dir = skill_path / "scripts"
    if scripts_dir.exists():
        for f in scripts_dir.iterdir():
            if f.is_file() and not os.access(f, os.X_OK):
                warnings.append(f"Script not executable: {f.name}")
    
    return errors + [f"WARNING: {w}" for w in warnings]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate.py <skill-dir>")
        sys.exit(1)
    
    skill_path = Path(sys.argv[1])
    issues = validate_skill(skill_path)
    
    if issues:
        for i in issues:
            print(f"  {i}")
        sys.exit(1)
    else:
        print(f"✅ {skill_path.name}: All checks passed")
```

---

## Quick Start: Create a New Skill

```bash
# 1. Create directory
mkdir -p ~/.hermes/skills/my-new-skill/{scripts,references,assets}

# 2. Write SKILL.md (use template above)

# 3. Validate
python skills/skill-authoring/scripts/validate.py ~/.hermes/skills/my-new-skill

# 4. Test load
hermes chat -q "Load my-new-skill skill"
```

---

## Changelog

| Version | Changes |
|---------|---------|
| 1.0.0 | Initial release — unified Hermes + OpenClaw patterns |

---

**Remember:** A skill is a *triggerable workflow*, not documentation. Keep the body lean — put depth in `references/`. The frontmatter is the contract; the body is the entry point.