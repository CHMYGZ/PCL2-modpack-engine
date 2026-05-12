#!/usr/bin/env python3
"""
CurseForge 整合包数据抓取器
长期使用：自动拉取热门整合包，合并到本地数据
运行：python3 src/curseforge_fetcher.py
"""

import json, time, sys
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    print("安装依赖: pip install requests")
    sys.exit(1)

# ── 配置 ──
API_KEY = "CURSEFORGE_API_KEY_FROM_ENV"  # CurseForge API Key
GAME_ID = 432          # Minecraft
CLASS_ID = 4471    # Modpacks
OUTPUT_FILE = Path(__file__).parent.parent / "data" / "modpack_curseforge.json"
# MERGE_TARGET = Path(__file__).parent.parent / "data" / "modpack_final.json"  # 禁用自动合并

HEADERS = {
    "x-api-key": API_KEY,
    "Accept": "application/json"
}


def fetch_top_modpacks(page_size=50, max_pages=3):
    """分页获取下载量最高的整合包"""
    all_mods = []
    for page in range(max_pages):
        index = page * page_size
        try:
            resp = requests.get(
                "https://api.curseforge.com/v1/mods/search",
                params={
                    "gameId": GAME_ID,
                    "classId": CLASS_ID,
                    "sortField": 2,        # 按总下载量排序
                    "sortOrder": "desc",
                    "pageSize": page_size,
                    "index": index
                },
                headers=HEADERS,
                timeout=15
            )
            if resp.status_code != 200:
                print(f"  第{page+1}页失败: HTTP {resp.status_code}")
                if resp.status_code == 403:
                    print("  ❌ API Key 无效，请在脚本顶部填写正确的 Key")
                    return all_mods
                break

            data = resp.json().get('data', [])
            if not data:
                break
            all_mods.extend(data)
            print(f"  第{page+1}页: {len(data)} 个整合包")
            time.sleep(1)  # 频率限制

        except Exception as e:
            print(f"  第{page+1}页错误: {e}")
            break

    return all_mods


def extract_info(mod):
    """从 API 返回的整合包数据中提取关键信息"""
    name = mod.get('name', '?')
    slug = mod.get('slug', '')
    downloads = mod.get('downloadCount', 0)
    summary = mod.get('summary', '')[:200]
    
    # 获取最新支持的MC版本
    mc_versions = []
    for f in mod.get('latestFiles', []):
        for dep in f.get('dependencies', []):
            if dep.get('modId') == 432:  # Minecraft
                continue  # 版本信息在其他字段
        # 直接从 file 的 gameVersion 取
        for gv in f.get('gameVersions', []):
            if gv.startswith('1.'):
                mc_versions.append(gv)
                break
    
    mc_version = mc_versions[0] if mc_versions else "未知"
    curse_url = mod.get('links', {}).get('websiteUrl', f'https://www.curseforge.com/minecraft/modpacks/{slug}')
    
    return {
        "name": name,
        "slug": slug,
        "downloads": downloads,
        "summary": summary,
        "mc_version": mc_version,
        "curse_url": curse_url,
    }


def main():
    if not API_KEY:
        print("❌ 请先在脚本顶部设置 API_KEY")
        print("   从 CurseForge 开发者后台 https://console.curseforge.com/ 获取")
        return
    
    print(f"🔍 开始抓取 CurseForge 热门整合包...")
    print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    mods = fetch_top_modpacks()
    if not mods:
        print("❌ 未获取到数据")
        return
    
    print(f"\n📦 共获取 {len(mods)} 个整合包")
    
    # 提取信息
    extracted = []
    for mod in mods:
        info = extract_info(mod)
        if info:
            extracted.append(info)
    
    # 按下载量排序
    extracted.sort(key=lambda x: x['downloads'], reverse=True)
    
    # 保存原始数据
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(extracted, f, ensure_ascii=False, indent=2)
    print(f"\n💾 已保存到 {OUTPUT_FILE}")
    
    # 输出前20名
    print(f"\n{'#'*60}")
    print(f"{'排名':>4} {'下载量':>10} {'整合包名':<30} {'MC版本':<10}")
    print(f"{'#'*60}")
    for i, info in enumerate(extracted[:20], 1):
        print(f"{i:>4} {info['downloads']:>10,} {info['name'][:30]:<30} {info['mc_version']:<10}")
    
    print(f"\n💡 提示: 要合并到主列表，运行 python3 src/curseforge_fetcher.py --merge")


if __name__ == "__main__":
    main()
