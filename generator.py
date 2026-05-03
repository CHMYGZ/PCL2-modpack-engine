#!/usr/bin/env python3
"""
PCL2 自定义主页生成器 v10
数据源: B站+BBSMC+CurseForge+Modrinth · 热门视频取代直播模块
"""

import hashlib, json, re
from datetime import datetime
from pathlib import Path

OUTPUT = Path(__file__).parent / "Custom.xaml"
VERSION = Path(__file__).parent / "version.ini"
MODPACK_FILE = Path(__file__).parent / "modpack_final.json"
LINKS_CACHE = Path(__file__).parent / "download_links_cache.json"
SEED_FILE = Path(__file__).parent / "seed_modpacks.json"

# B站MC热门视频（定期更新）
HOT_VIDEOS = [
    ("籽岷 · MC模组推荐合集", "https://space.bilibili.com/686127"),
    ("黒山大叔 · 红石科技", "https://space.bilibili.com/19428259"),
    ("老迪来咯 · MC搞笑实况", "https://space.bilibili.com/27996286"),
    ("大橙子 · 建筑教程", "https://space.bilibili.com/887004"),
    ("黑猫大少爷 · MC生存", "https://space.bilibili.com/4831263"),
    ("卡慕SaMa · MC日常", "https://space.bilibili.com/9596327"),
    ("抽风Crazy · MC动画", "https://space.bilibili.com/25067900"),
    ("MaxKim · MC小游戏", "https://space.bilibili.com/470465/video"),
    ("红叔 · MC模组挑战", "https://space.bilibili.com/680447/video"),
    ("萌新小百科 · MC教程", "https://space.bilibili.com/1370257"),
    ("Minecraft Live 合集", "https://search.bilibili.com/all?keyword=Minecraft+Live"),
    ("我的世界搞笑瞬间", "https://search.bilibili.com/all?keyword=我的世界+搞笑"),
    ("MC速通世界纪录", "https://search.bilibili.com/all?keyword=Minecraft+速通"),
    ("我的世界建筑欣赏", "https://search.bilibili.com/all?keyword=我的世界+建筑"),
    ("MC红石黑科技", "https://search.bilibili.com/all?keyword=MC+红石"),
    ("我的世界模组推荐", "https://search.bilibili.com/all?keyword=我的世界+模组+推荐"),
    ("MC光影材质展示", "https://search.bilibili.com/all?keyword=Minecraft+光影"),
    ("Minecraft动画短片", "https://search.bilibili.com/all?keyword=Minecraft+动画"),
    ("我的世界100天挑战", "https://search.bilibili.com/all?keyword=我的世界+100天"),
    ("MC多人生存系列", "https://search.bilibili.com/all?keyword=MC+多人+生存"),
]

def escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def load_modpacks():
    """加载整合包数据 — 种子优先，缓存补全"""
    packs = []
    seen = set()
    
    # 1. 种子文件（最高优先级）
    if SEED_FILE.exists():
        with open(SEED_FILE, 'r', encoding='utf-8') as f:
            seeds = json.load(f)
        for s in seeds:
            name = s['name']
            if name not in seen:
                seen.add(name)
                packs.append(s)
    
    # 2. 缓存文件
    if MODPACK_FILE.exists():
        with open(MODPACK_FILE, 'r', encoding='utf-8') as f:
            cached = json.load(f)
        for mp in cached:
            name = mp['name']
            if name not in seen:
                seen.add(name)
                packs.append(mp)
    
    return packs

def load_download_links():
    if not LINKS_CACHE.exists():
        return {}
    with open(LINKS_CACHE, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    TRUSTED = {
        'DawnCraft': 'curseforge.com/minecraft/modpacks/dawn-craft',
        'FTB Skies': 'pan.quark.cn',
        'Vault Hunters': 'curseforge.com/minecraft/modpacks/vault-hunters-',
    }
    verified = {}
    for name, r in cache.get('results', {}).items():
        if r['status'] == 'found' and r.get('links') and name in TRUSTED:
            clean = [l for l in r['links'] if TRUSTED[name] in l.lower()]
            if clean:
                verified[name] = clean[0]
    return verified
def make_item(mp, dl_links, index, is_seed=False):
    """生成单个整合包的 MyListItem"""
    name = escape(mp['name'][:25])
    genres = mp.get('genres', ['📦'])
    genre_str = ' '.join(genres[:2])
    play = mp.get('bili_play_str', '?播放')
    
    # 链接优先级: BBSMC > 抓取 > B站视频
    if mp.get('bbsmc_url'):
        url = escape(mp['bbsmc_url'])
        link_type = "📥BBSMC下载"
    elif mp['name'] in dl_links:
        url = escape(dl_links[mp['name']])
        link_type = "📥直链下载"
    else:
        url = escape(mp.get('bili_url', '#'))
        link_type = "🎬B站视频"
    
    prefix = "🆕 " if is_seed else ""
    
    return f'''                    <local:MyListItem Margin="-2,0,10,0"
                         Title="{prefix}{genre_str}  {name}"
                         Info="▸ {link_type} · {play}"
                         EventType="打开网页"
                         EventData="{url}"
                         Type="Clickable" />'''
def generate():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    modpacks = load_modpacks()
    dl_links = load_download_links()
    
    if not modpacks:
        print("ERROR: modpack_final.json not found")
        return ""
    
    bbsmc_count = sum(1 for m in modpacks if m.get('bbsmc_url'))
    scraped_count = sum(1 for m in modpacks if m['name'] in dl_links and not m.get('bbsmc_url'))
    bili_count = len(modpacks) - bbsmc_count - scraped_count
    # 取前50，分左右两列。种子条目插在最前面
    # 识别种子条目数量
    seed_count = 0
    if SEED_FILE.exists():
        with open(SEED_FILE, 'r', encoding='utf-8') as f:
            seed_count = len(json.load(f))
    
    display_count = len(modpacks)
    half = (display_count + 1) // 2
    left_packs = modpacks[:half]
    right_packs = modpacks[half:]
    
    # 标记种子条目
    def is_seed(mp, idx):
        return idx < seed_count
    
    left_items = [make_item(mp, dl_links, i, is_seed(mp, i)) for i, mp in enumerate(left_packs)]
    right_items = [make_item(mp, dl_links, i+half, is_seed(mp, i+half)) for i, mp in enumerate(right_packs)]
    
    # ── 快速按钮栏 ──
    buttons = [
        ("🎬 B站MC区", "https://search.bilibili.com/all?keyword=Minecraft+整合包&order=click", "搜索Minecraft整合包视频"),
        ("📥 CurseForge", "https://www.curseforge.com/minecraft/modpacks", "全球最大MC模组平台"),
        ("📦 Modrinth", "https://modrinth.com/modpacks", "开源MC整合包平台"),
        ("🏠 BBSMC", "https://bbsmc.net/modpacks", "中文MC资源下载站"),
    ]
    
    btn_items = []
    for text, url, tooltip in buttons:
        btn_items.append(
            f'               <local:MyButton Text="{text}" Margin="6,0,6,0" Padding="14,8,14,8"\n'
            f'                    ToolTip="{tooltip}"\n'
            f'                    EventType="打开网页" EventData="{escape(url)}" />'
        )
    
    btn_bar = '\n'.join(btn_items)
    
    # ── 热门视频栏 ──
    vid_icons = ["🎬", "🔧", "😂", "🏗", "🎮", "🌟", "🎨", "🎯", "⚔", "📖",
                 "🎤", "🤣", "⏱", "🏰", "⚡", "📦", "✨", "🎞", "💯", "👥"]
    vid_items = []
    for i, (title, url) in enumerate(HOT_VIDEOS):
        icon = vid_icons[i % len(vid_icons)]
        vid_items.append(f'''          <local:MyListItem Margin="-2,0,10,0"
               Title="{icon}  {escape(title)}"
               Info="▸ 点击前往 B站观看"
               EventType="打开网页"
               EventData="{escape(url)}"
               Type="Clickable" />''')
    
    xaml = f'''<!--
  ═══════════════════════════════════════════════
  PCL2 · MyWorld B站热门整合包推荐 v10
  数据源: B站 + BBSMC + CurseForge + Modrinth
  📥BBSMC:{bbsmc_count} 📥直链:{scraped_count} 🎬B站:{bili_count}
  更新: (bimal)
  ═══════════════════════════════════════════════
-->

<!-- ═══════════════════════════════════════════ -->
<!-- ═══  顶部横幅  ═══ -->
<!-- ═══════════════════════════════════════════ -->
<local:MyCard Margin="0,0,0,16" Title="🏠">
     <StackPanel Margin="16,18,16,14">
          <TextBlock Text="感谢您订阅 Minecraft 推荐引擎" FontSize="15" FontWeight="Bold"
               Foreground="{{DynamicResource ColorBrush1}}"
               HorizontalAlignment="Center" />
          <TextBlock Text="MyWorld · B站热门整合包 · 每日自动更新" FontSize="11"
               Foreground="{{DynamicResource ColorBrush4}}"
               HorizontalAlignment="Center" Margin="0,4,0,0" />
     </StackPanel>
</local:MyCard>

<!-- ═══════════════════════════════════════════ -->
<!-- ═══  快速导航  ═══ -->
<!-- ═══════════════════════════════════════════ -->
<local:MyCard Margin="0,0,0,20" Title="⚡ 快速导航" CanSwap="True">
     <StackPanel Margin="20,28,20,18">
          <local:MyHint IsWarn="False" Theme="Blue"
               Text="常用资源站点一键直达 · B站搜索 + CurseForge + Modrinth + BBSMC 四大数据源"
               Margin="0,0,0,12" />
          <StackPanel Orientation="Horizontal" HorizontalAlignment="Center">
{btn_bar}
          </StackPanel>
     </StackPanel>
</local:MyCard>

<!-- ═══════════════════════════════════════════ -->
<!-- ═══  整合包推荐  ═══ -->
<!-- ═══════════════════════════════════════════ -->
<local:MyCard Margin="0,0,0,20" Title="Minecraft 整合包推荐" CanSwap="True">
     <StackPanel Margin="24,35,24,15">
          <TextBlock Text="Minecraft 整合包推荐" FontSize="22" FontWeight="Bold"
               Foreground="{{DynamicResource ColorBrush1}}"
               HorizontalAlignment="Center" Margin="0,0,0,10" />
          <local:MyHint IsWarn="False" Theme="Yellow"
               Text="🔥硬核 ⚙科技 🏰冒险 🧙魔法 🌿休闲 🗺空岛 🎮宝可梦 ⚡混合 | 📥BBSMC · 📥直链 · 🎬B站视频 · CurseForge/Modrinth收录"
               Margin="0,0,0,12" />

          <Grid>
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="16" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
               <StackPanel Grid.Column="0">
{chr(10).join(left_items)}
               </StackPanel>
               <StackPanel Grid.Column="2">
{chr(10).join(right_items)}
               </StackPanel>
          </Grid>
     </StackPanel>
</local:MyCard>

<!-- ═══════════════════════════════════════════ -->
<!-- ═══  MC热门视频  ═══ -->
<!-- ═══════════════════════════════════════════ -->
<local:MyCard Margin="0,0,0,20" Title="Minecraft 视频推荐" CanSwap="True" IsSwaped="True">
     <StackPanel Margin="24,30,24,15">
          <TextBlock Text="Minecraft 视频推荐" FontSize="22" FontWeight="Bold"
               Foreground="{{DynamicResource ColorBrush1}}"
               HorizontalAlignment="Center" Margin="0,0,0,8" />
          <local:MyHint IsWarn="False" Theme="Red"
               Text="🎬 知名UP主空间 + 🔥 热门搜索主题 · 涵盖实况/红石/建筑/模组/动画/速通"
               Margin="0,0,0,12" />
          <Grid>
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="16" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
               <StackPanel Grid.Column="0">
{chr(10).join(vid_items[:10])}
               </StackPanel>
               <StackPanel Grid.Column="2">
{chr(10).join(vid_items[10:])}
               </StackPanel>
          </Grid>
     </StackPanel>
</local:MyCard>

<!-- ═══════════════════════════════════════════ -->
<!-- ═══  页脚  ═══ -->
<!-- ═══════════════════════════════════════════ -->
<local:MyCard Margin="0,0,0,0" Title="关于">
     <StackPanel Margin="24,32,24,28">
          <Grid>
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="Auto" />
               </Grid.ColumnDefinitions>
               <StackPanel Grid.Column="0">
                    <TextBlock Text="MyWorld · 整合包推荐引擎" FontSize="18" FontWeight="Bold"
                         Foreground="{{DynamicResource ColorBrush1}}" Margin="0,0,0,8" />
                    <TextBlock Text="By GDSGDHG" FontSize="13"
                         Foreground="{{DynamicResource ColorBrush4}}" Margin="0,0,0,6" />
                    <TextBlock Text="数据来源: B站 · BBSMC · CurseForge · Modrinth" FontSize="12"
                         Foreground="{{DynamicResource ColorBrush5}}" Margin="0,0,0,4" />
                    <TextBlock Text="仅收录2025年1月起发布的整合包视频 · (bimal)" FontSize="11"
                         Foreground="{{DynamicResource ColorBrush6}}" Margin="0,0,0,4" />
                    <TextBlock Text="致谢: PCL2 · B站创作者 · 社区维护者" FontSize="11"
                         Foreground="{{DynamicResource ColorBrush6}}" Margin="0,0,0,0" />
               </StackPanel>
               <local:MyButton Grid.Column="1" Text="⟳ 刷新主页" Padding="16,10,16,10"
                    VerticalAlignment="Center" EventType="刷新主页" />
          </Grid>
     </StackPanel>
</local:MyCard>'''
    return xaml

def update_version(xaml):
    md5 = hashlib.md5(xaml.encode("utf-8")).hexdigest()[:8]
    date = datetime.now().strftime("%y%m%d")
    v = f"{date}:{md5}"
    with open(VERSION, "w") as f:
        f.write(v)
    return v

def main():
    modpacks = load_modpacks()
    dl_links = load_download_links()
    
    print(f"📦 整合包数据: {len(modpacks)} 个")
    bbsmc = sum(1 for m in modpacks if m.get('bbsmc_url'))
    scraped = sum(1 for m in modpacks if m['name'] in dl_links and not m.get('bbsmc_url'))
    print(f"   📥 BBSMC直链: {bbsmc}")
    print(f"   📥 抓取直链: {scraped}")
    print(f"   🎬 B站视频: {len(modpacks) - bbsmc - scraped}")
    print(f"   🎬 热门视频: {len(HOT_VIDEOS)} 个")
    
    print("\n生成 XAML...")
    xaml = generate()
    if not xaml:
        return
    
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(xaml)
    
    v = update_version(xaml)
    print(f"   版本 {v} | {len(xaml)} 字符")
    print("✓ 完成 — PCL2 刷新 http://localhost:8765/Custom.xaml")

if __name__ == "__main__":
    main()
