#!/usr/bin/env python3
"""
CurseForge 整合包数据抓取器
长期使用：自动拉取热门整合包，合并到本地数据
运行：python3 src/curseforge_fetcher.py

环境变量：
  CURSEFORGE_API_KEY - 从 https://console.curseforge.com/ 获取
"""

import json, time, sys, os
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    print("安装依赖: pip install requests")
    sys.exit(1)

# ── 配置 ──
API_KEY = os.environ.get("CURSEFORGE_API_KEY")
if not API_KEY:
    print("❌ 请先设置环境变量 CURSEFORGE_API_KEY")
    print("   从 CurseForge 开发者后台 https://console.curseforge.com/ 获取")
    print("   然后运行: export CURSEFORGE_API_KEY=你的key")
    sys.exit(1)

GAME_ID = 432
CLASS_ID = 4471
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "modpack_curseforge.json"

HEADERS = {
    "x-api-key": API_KEY,
    "Accept": "application/json"
}
