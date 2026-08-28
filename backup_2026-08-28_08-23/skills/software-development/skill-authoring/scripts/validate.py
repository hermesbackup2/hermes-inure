#!/usr/bin/env python3
"""Validate a skill directory for cross-ecosystem compatibility (Hermes + OpenClaw)."""
import os
import sys
import re
import yaml
from pathlib import Path


def validate_skill(skill_path: Path) -> list:
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
        warnings.append("License should be SPDX identifier (e.g., MIT, Apache-2.0)")

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
