#!/usr/bin/env python3
"""
Version tracker for PCL2 modpack engine.
Auto-updates version.json, version.txt, and CHANGELOG.md.
"""
import json
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).parent.parent
VERSION_FILE = REPO_ROOT / "data" / "version.json"
VERSION_TXT = REPO_ROOT / "output" / "version.txt"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"
OUTPUT_DIR = REPO_ROOT / "output"


def get_modpack_count() -> int:
    """Count modpacks from XAML output."""
    xaml = OUTPUT_DIR / "Custom.xaml"
    if not xaml.exists():
        return 0
    text = xaml.read_text(encoding="utf-8")
    count = text.count('Type="Clickable"')
    return count


def bump_version(version: str) -> str:
    """Bump version string like v10 -> v10.1 or v10.1 -> v10.2"""
    v = version.lstrip("v")
    parts = v.split(".")
    if len(parts) == 1:
        parts.append("1")
    else:
        parts[-1] = str(int(parts[-1]) + 1)
    return "v" + ".".join(parts)


def update_changelog(ver: str, today: str):
    """Append entry to CHANGELOG.md if not already present."""
    entry = f"## {ver} ({today})\n\n- 每日同步：数据更新\n"
    if CHANGELOG.exists():
        content = CHANGELOG.read_text(encoding="utf-8")
        if entry.strip() in content:
            return  # already logged
        # Insert after first ## heading block
        lines = content.splitlines(keepends=True)
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("## ") and i > 1:
                insert_at = i
                break
        if insert_at:
            lines.insert(insert_at, "\n" + entry)
        CHANGELOG.write_text("".join(lines), encoding="utf-8")
    else:
        # Create new changelog
        content = f"""# CHANGELOG

> PCL2 整合包推荐引擎 — 版本更新记录

---

{entry}---
"""
        CHANGELOG.write_text(content, encoding="utf-8")
    print(f"changelog updated: {ver}")


def main():
    today = str(date.today())
    if not VERSION_FILE.exists():
        v = {
            "version": "v10",
            "build_date": today,
            "modpack_count": 0,
            "data_sources": ["B站", "BBSMC", "CurseForge", "Modrinth"],
            "changelog": []
        }
    else:
        v = json.loads(VERSION_FILE.read_text(encoding="utf-8"))
        v["version"] = bump_version(v.get("version", "v1"))
        v["build_date"] = today

    v["modpack_count"] = get_modpack_count()

    # Update version.txt
    seq = today.replace("-", ".")
    VERSION_TXT.write_text(f"{seq}-{v['modpack_count']:03d}\n", encoding="utf-8")
    print(f"version.txt: {seq}-{v['modpack_count']:03d}")

    # Update version.json changelog
    changelog = v.setdefault("changelog", [])
    entry = f"{v['version']} - {today}"
    if not changelog or changelog[0] != entry:
        changelog.insert(0, entry)
        changelog[:] = changelog[:10]

    VERSION_FILE.write_text(
        json.dumps(v, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    print(f"version.json: {v['version']}, modpacks={v['modpack_count']}")

    # Update CHANGELOG.md
    update_changelog(v["version"], today)

    return v


if __name__ == "__main__":
    main()
