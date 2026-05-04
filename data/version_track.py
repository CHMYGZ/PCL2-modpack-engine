#!/usr/bin/env python3
"""
Version tracker for PCL2 modpack engine.
Auto-updates version.json with build date and changelog.
"""
import json
from pathlib import Path
from datetime import date

VERSION_FILE = Path(__file__).parent / "version.json"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def get_modpack_count() -> int:
    """Count modpacks from XAML output."""
    xaml = OUTPUT_DIR / "Custom.xaml"
    if not xaml.exists():
        return 0
    text = xaml.read_text(encoding="utf-8")
    # Count MyListItem entries that look like modpack items (have Title/Info/EventType)
    count = text.count('Type="Clickable"')
    return count


def bump_version(version: str, major: bool = False) -> str:
    """Bump version string like v10 -> v10.1 or v10.1 -> v10.2"""
    v = version.lstrip("v")
    parts = v.split(".")
    if len(parts) == 1:
        # v10 -> v10.1
        return f"v{v}.1"
    else:
        # v10.1 -> v10.2
        parts[-1] = str(int(parts[-1]) + 1)
        return f"v{'.'.join(parts)}"


def main():
    if not VERSION_FILE.exists():
        print("version.json not found, creating default...")
        v = {
            "version": "v10",
            "build_date": str(date.today()),
            "modpack_count": 0,
            "data_sources": ["B站", "BBSMC", "CurseForge", "Modrinth"],
            "changelog": []
        }
    else:
        v = json.loads(VERSION_FILE.read_text(encoding="utf-8"))
        v["version"] = bump_version(v.get("version", "v1"), major=False)
        v["build_date"] = str(date.today())

    v["modpack_count"] = get_modpack_count()

    # Add changelog entry
    changelog = v.setdefault("changelog", [])
    entry = f"v{v['version']} - 每日同步 {v['build_date']}"
    if not changelog or changelog[0] != entry:
        changelog.insert(0, entry)
        changelog[:] = changelog[:10]  # keep last 10 entries

    VERSION_FILE.write_text(
        json.dumps(v, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
    print(f"version bumped to {v['version']}, build_date={v['build_date']}, modpacks={v['modpack_count']}")
    return v


if __name__ == "__main__":
    main()
