#!/usr/bin/env python3
"""
B站整合包下载链接批量抓取器
策略: web_search找候选 → web_extract扒简介 → 提取下载链接 → 缓存JSON
绕过B站API 412风控
"""
import json, re, time, sys
from pathlib import Path
from datetime import datetime

# These need to be called via the hermes_tools interface in execute_code
# For standalone script, we'll use requests directly
import requests

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
REF = "https://www.bilibili.com"

CACHE_FILE = Path(__file__).parent / "download_links_cache.json"
MODPACK_FILE = Path(__file__).parent / "modpack_final.json"

DOWNLOAD_PATTERNS = [
    r'curseforge\.com', r'modrinth\.com', r'mcmod\.cn',
    r'pan\.baidu\.com', r'pan\.quark\.cn', r'123pan\.com',
    r'aliyundrive\.com', r'lanzou[wx]?\.com', r'lanzoux\.com',
    r'github\.com/.*/releases', r'下载链接', r'下载地址',
    r'网盘', r'整合包下载',
]

def has_download(text):
    if not text: return False
    tl = text.lower()
    return any(re.search(p, tl) for p in DOWNLOAD_PATTERNS)

def extract_download_links(text):
    links = re.findall(r'https?://[^\s\n\]）】)]+', text)
    return [l.rstrip('.,;:') for l in links if any(kw in l.lower() for kw in [
        'curseforge', 'modrinth', 'pan.baidu', 'pan.quark', '123pan',
        'aliyundrive', 'lanzou', 'github.com', 'download', '下载', 'pan.',
        'wwue', 'wwa', 'wwx',  # lanzou variants
    ])]

def search_bili_videos(pack_name):
    """Search B站 for videos about a modpack, return list of {title, bvid, url}"""
    try:
        resp = requests.get(
            "https://api.bilibili.com/x/web-interface/search/type",
            params={"keyword": f"{pack_name} 整合包 下载 教程", "search_type": "video", "page": 1},
            headers={"User-Agent": UA, "Referer": REF}, timeout=10
        )
        if resp.status_code != 200:
            return []
        data = resp.json()
        results = []
        for v in data.get("data", {}).get("result", [])[:8]:
            title = re.sub(r'<[^>]+>', '', v.get("title", ""))
            bvid = v.get("bvid", "")
            play = v.get("play", 0)
            if bvid and title and play > 500:
                results.append({
                    "title": title, "bvid": bvid, "play": play,
                    "url": f"https://www.bilibili.com/video/{bvid}"
                })
        results.sort(key=lambda x: x['play'], reverse=True)
        return results
    except:
        return []

def get_video_description(bvid):
    """Get full video description via API (may still work with fewer calls)"""
    try:
        resp = requests.get(
            f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}",
            headers={"User-Agent": UA, "Referer": REF}, timeout=8
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("data", {}).get("desc", "")
    except:
        pass
    return ""

def scrape_one(pack_name, max_attempts=3):
    """Scrape download links for one modpack"""
    # Step 1: Search B站
    candidates = search_bili_videos(pack_name)
    if not candidates:
        return {"status": "no_videos", "links": [], "video_url": None}
    
    # Step 2: Check candidate descriptions for download links
    for i, c in enumerate(candidates[:max_attempts]):
        desc = get_video_description(c['bvid'])
        if desc and has_download(desc):
            links = extract_download_links(desc)
            return {
                "status": "found",
                "links": links[:3],
                "video_url": c['url'],
                "video_title": c['title'][:40],
                "video_play": c['play'],
            }
        time.sleep(0.3)
    
    # Step 3: No download links found in any candidate
    return {
        "status": "no_download_links",
        "links": [],
        "video_url": candidates[0]['url'] if candidates else None,
        "video_title": candidates[0]['title'][:40] if candidates else None,
        "video_play": candidates[0]['play'] if candidates else 0,
    }

def main():
    # Load modpacks
    if not MODPACK_FILE.exists():
        print(f"ERROR: {MODPACK_FILE} not found")
        sys.exit(1)
    
    with open(MODPACK_FILE, 'r', encoding='utf-8') as f:
        modpacks = json.load(f)
    
    print(f"Starting scrape for {len(modpacks)} modpacks...\n")
    
    results = {}
    found_count = 0
    
    for i, mp in enumerate(modpacks):
        name = mp['name']
        print(f"[{i+1}/{len(modpacks)}] {name}...", end=" ", flush=True)
        
        try:
            result = scrape_one(name)
            results[name] = result
            
            if result['status'] == 'found':
                found_count += 1
                link_preview = result['links'][0][:50] if result['links'] else '?'
                print(f"✅ {link_preview}")
            elif result['status'] == 'no_download_links':
                print(f"⚠ 无下载链接 ({result.get('video_play', 0)}播放)")
            else:
                print(f"❌ 无视频")
        except Exception as e:
            print(f"💥 {e}")
            results[name] = {"status": "error", "links": [], "video_url": None}
        
        time.sleep(0.5)  # Rate limit
    
    # Save cache
    cache = {
        "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(modpacks),
        "found": found_count,
        "results": results
    }
    
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)
    
    print(f"\nDone. {found_count}/{len(modpacks)} modpacks have download links.")
    print(f"Cache saved to {CACHE_FILE}")

if __name__ == "__main__":
    main()
