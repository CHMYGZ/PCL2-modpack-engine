#!/usr/bin/env python3
"""
PCL2 自定义主页生成器 v10
数据源: B站+BBSMC+CurseForge+Modrinth · 全B站视频推荐+下方下载链接
"""

import hashlib, json, re
from datetime import datetime
from pathlib import Path

OUTPUT = Path(__file__).parent.parent / "output" / "Custom.xaml"
VERSION = Path(__file__).parent.parent / "output" / "Custom.xaml.ini"
MODPACK_FILE = Path(__file__).parent.parent / "data" / "modpack_final.json"
ENRICHED_FILE = Path(__file__).parent.parent / "data" / "modpack_enriched.json"
LINKS_CACHE = Path(__file__).parent.parent / "data" / "download_links_cache.json"
SEED_FILE = Path(__file__).parent.parent / "data" / "seed_modpacks.json"

# B站MC热门视频（精简版·同类型保留最高播放）
# 结构: UP主频道(6) + 精选视频(7) + B站搜索话题(14) = 27条
HOT_VIDEOS = [
    # ── UP主频道 · 按类型精简 ──
    ("籽岷 · MC模组推荐合集", "https://space.bilibili.com/686127/video"),
    ("黒山大叔 · 红石科技", "https://space.bilibili.com/19428259/video"),
    ("老迪来咯 · MC搞笑实况", "https://space.bilibili.com/27996286/video"),
    ("Nor叔 · MC极限生存", "https://space.bilibili.com/17425003/video"),
    ("大炒面制造者Cen · MC热门", "https://space.bilibili.com/14890801/video"),
    ("Minecraft官方频道", "https://space.bilibili.com/43310262/video"),
    # ── 精选热门视频 · 同合集保留最高播放 ──
    ("🔥 年度MC十大神包289万", "https://www.bilibili.com/video/BV1p1421C75Q/"),
    ("🔥 一个包2000万下载256万", "https://www.bilibili.com/video/BV15M4m127dH/"),
    ("🔥 10款冒险向神包215万", "https://www.bilibili.com/video/BV1J24y1R7GT/"),
    ("🔥 五个僵尸末日神包124万", "https://www.bilibili.com/video/BV1Zp4y1o71R/"),
    ("🔥 远梦之棺 超长版93万", "https://www.bilibili.com/video/BV1Z4zYBnE4T/"),
    ("🔥 恐怖模组排名92万", "https://www.bilibili.com/video/BV1ff5KzTE9A/"),
    ("🔥 ATM10双人生存81万", "https://www.bilibili.com/video/BV1ugG1z4EG8/"),
    # ── B站搜索话题 · 合并同类 ──
    ("MC热门作品搜索", "https://search.bilibili.com/all?keyword=Minecraft+整合包+推荐"),
    ("我的世界搞笑瞬间", "https://search.bilibili.com/all?keyword=我的世界+搞笑"),
    ("MC速通世界纪录", "https://search.bilibili.com/all?keyword=Minecraft+速通"),
    ("我的世界建筑欣赏", "https://search.bilibili.com/all?keyword=我的世界+建筑"),
    ("MC红石机械", "https://search.bilibili.com/all?keyword=Create+机械动力+Minecraft"),
    ("我的世界模组推荐", "https://search.bilibili.com/all?keyword=我的世界+模组+推荐"),
    ("MC光影材质展示", "https://search.bilibili.com/all?keyword=Minecraft+光影"),
    ("Minecraft动画短片", "https://search.bilibili.com/all?keyword=Minecraft+动画"),
    ("我的世界100天挑战", "https://search.bilibili.com/all?keyword=我的世界+100天"),
    ("MC多人生存系列", "https://search.bilibili.com/all?keyword=MC+多人+生存"),
    ("MC空岛生存", "https://search.bilibili.com/all?keyword=MC+空岛+生存"),
    ("MC宝可梦世界", "https://search.bilibili.com/all?keyword=MC+宝可梦+整合包"),
    ("MC魔法冒险", "https://search.bilibili.com/all?keyword=Minecraft+魔法+整合包"),
    ("MC暮色森林", "https://search.bilibili.com/all?keyword=暮色森林+Minecraft"),
]

def escape(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def load_modpacks():
    """加载整合包数据 — 种子优先，enriched覆盖，缓存补全"""
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
    
    # 3. Enriched数据覆盖（补充版本/平台等字段）
    if ENRICHED_FILE.exists():
        with open(ENRICHED_FILE, 'r', encoding='utf-8') as f:
            enriched_list = json.load(f)
        enriched_map = {e['name']: e for e in enriched_list}
        for mp in packs:
            if mp['name'] in enriched_map:
                e = enriched_map[mp['name']]
                for key in ('version', 'curseforge_url', 'bbsmc_url', 'mcmod_url',
                           'modrinth_url', 'baidu_pan', 'quark_pan', 'note',
                           'bili_url', 'bili_play_str'):
                    if key in e and e[key]:
                        mp[key] = e[key]
    
    return packs

# ── 已知下载链接（CurseForge / Modrinth / 网盘）──
KNOWN_DOWNLOADS = {
    "RLCraft": ("CurseForge", "https://www.curseforge.com/minecraft/modpacks/rlcraft"),
    "RLCraft Dregora": ("CurseForge", "https://www.curseforge.com/minecraft/modpacks/rlcraft-dregora"),
    "GreedyCraft": ("CurseForge", "https://www.curseforge.com/minecraft/modpacks/greedycraft"),
    "Better MC": ("CurseForge", "https://www.curseforge.com/minecraft/modpacks/better-mc-forge-bmc4"),
    "BMC4": ("CurseForge", "https://www.curseforge.com/minecraft/modpacks/better-mc-forge-bmc4"),
    "SkyFactory 4": ("CurseForge", "https://www.curseforge.com/minecraft/modpacks/skyfactory-4"),
    "ATM9": ("CurseForge", "https://www.curseforge.com/minecraft/modpacks/all-the-mods-9"),
    "All The Mods 10": ("CurseForge", "https://www.curseforge.com/minecraft/modpacks/all-the-mods-10"),
    "Vault Hunters 3": ("CurseForge", "https://www.curseforge.com/minecraft/modpacks/vault-hunters-1-18-2"),
    "GregTech New Horizons": ("CurseForge", "https://www.curseforge.com/minecraft/modpacks/gt-new-horizons"),
    "GTNH": ("CurseForge", "https://www.curseforge.com/minecraft/modpacks/gt-new-horizons"),
    "Cobblemon": ("Modrinth", "https://modrinth.com/modpack/cobblemon-fabric"),
    "Create: Above and Beyond": ("CurseForge", "https://www.curseforge.com/minecraft/modpacks/create-above-and-beyond"),
}

def load_download_links():
    """加载下载链接: 已知链接 + 缓存推理"""
    dl_map = dict(KNOWN_DOWNLOADS)  # (label, url)
    
    # 补充 BBSMC 链接
    packs = load_modpacks()
    for mp in packs:
        if mp.get('bbsmc_url') and mp['name'] not in dl_map:
            dl_map[mp['name']] = ("BBSMC", mp['bbsmc_url'])
    
    # 补充抓取链接
    if LINKS_CACHE.exists():
        with open(LINKS_CACHE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        for name, r in cache.get('results', {}).items():
            if name in dl_map:
                continue
            if r['status'] == 'found' and r.get('links'):
                url = r['links'][0]
                # 确定平台标签
                if 'curseforge' in url.lower():
                    label = "CurseForge"
                elif 'modrinth' in url.lower():
                    label = "Modrinth"
                elif 'pan.baidu' in url.lower():
                    label = "百度网盘"
                elif 'pan.quark' in url.lower():
                    label = "夸克网盘"
                elif 'pan.huang1111' in url.lower():
                    label = "huang1111网盘"
                else:
                    label = "直链"
                dl_map[name] = (label, url)
    
    return dl_map

def make_item(mp, dl_info, index, is_seed=False):
    """生成单个整合包: B站视频 + 版本/平台信息"""
    name = escape(mp['name'][:25])
    genres = mp.get('genres', ['📦'])
    genre_str = ' '.join(genres[:2])
    play = mp.get('bili_play_str', '?')
    bili_url = escape(mp.get('bili_url', '#'))
    prefix = "🆕 " if is_seed else ""
    
    # 版本
    version = mp.get('version', '')
    ver_str = f" · {version}" if version else ""
    
    # 平台可用性 (从enriched数据)
    platforms = []
    if mp.get('curseforge_url'): platforms.append('CF')
    if mp.get('bbsmc_url'): platforms.append('BS')
    if mp.get('mcmod_url'): platforms.append('百科')
    if mp.get('modrinth_url'): platforms.append('MR')
    platform_str = f" · 📥{'/'.join(platforms)}" if platforms else ""
    
    return f'''                    <local:MyListItem Margin="-2,0,10,0"
                         Title="{prefix}{genre_str}  {name}"
                         Info="▸ 🎬B站 · {play}{ver_str}{platform_str}"
                         EventType="打开网页"
                         EventData="{bili_url}"
                         Type="Clickable" />'''
def generate():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    modpacks = load_modpacks()
    dl_links = load_download_links()
    
    if not modpacks:
        print("ERROR: modpack_final.json not found")
        return ""
    
    dl_count = sum(1 for m in modpacks if m['name'] in dl_links)
    bili_count = len(modpacks)
    bbsmc_count = sum(1 for m in modpacks if m.get('bbsmc_url'))
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
    
    left_items = [make_item(mp, dl_links.get(mp['name']), i, is_seed(mp, i)) for i, mp in enumerate(left_packs)]
    right_items = [make_item(mp, dl_links.get(mp['name']), i+half, is_seed(mp, i+half)) for i, mp in enumerate(right_packs)]
    
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
                 "🎤", "🤣", "⏱", "🏰", "⚡", "📦", "✨", "🎞", "💯", "👥",
                 "🔥", "💀", "🗡️", "🛡️", "🧙", "🌍", "🏆", "🎲", "👾", "💎",
                 "🕹️", "🎭", "🗺️", "🌟", "⚗️", "🌿", "🧟", "🔮", "⛏️", "🎪"]
    vid_items = []
    for i, (title, url) in enumerate(HOT_VIDEOS):
        icon = vid_icons[i % len(vid_icons)]
        vid_items.append(f'''          <local:MyListItem Margin="-2,0,10,0"
               Title="{icon}  {escape(title)}"
               Info="▸ 点击前往 B站观看"
               EventType="打开网页"
               EventData="{escape(url)}"
               Type="Clickable" />''')

    total_modpacks = len(modpacks)

    xaml = f'''<!--
  ═══════════════════════════════════════════════
  PCL2 整合包推荐引擎
  数据源: B站 + BBSMC + CurseForge + Modrinth
  📥BBSMC:{bbsmc_count} 🎬B站视频:{bili_count} 📥直链下载:{dl_count}
  更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}
  ═══════════════════════════════════════════════
-->

<!-- ═══════════════════════════════════════════ -->
<!-- ═══  顶部横幅  ═══ -->
<!-- ═══════════════════════════════════════════ -->
<local:MyCard Margin="0,0,0,16" Title="🏠">
     <StackPanel Margin="16,18,16,14">
          <TextBlock Text="感谢您订阅 PCL2 整合包推荐引擎" FontSize="15" FontWeight="Bold"
               Foreground="{{DynamicResource ColorBrush1}}"
               HorizontalAlignment="Center" />
          <TextBlock Text="聚合 B站 / BBSMC / CurseForge / Modrinth 的 Minecraft 整合包推荐主页" FontSize="11"
               Foreground="{{DynamicResource ColorBrush5}}"
               HorizontalAlignment="Center" Margin="0,4,0,0" />
          <TextBlock Text="PCL2 · 整合包推荐 · 每日自动更新 · 数据仅供参考，非广告推荐" FontSize="10"
               Foreground="{{DynamicResource ColorBrush6}}"
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
               Text="🔥硬核 ⚙科技 🏰冒险 🧙魔法 🌿休闲 🗺空岛 🎮宝可梦 ⚡混合 | 🎬B站视频推荐 · 下方 📥下载链接"
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
                    <ColumnDefinition Width="16" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
               <StackPanel Grid.Column="0">
{chr(10).join(vid_items[:9])}
               </StackPanel>
               <StackPanel Grid.Column="2">
{chr(10).join(vid_items[9:18])}
               </StackPanel>
               <StackPanel Grid.Column="4">
{chr(10).join(vid_items[18:])}
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
                    <TextBlock Text="PCL2 整合包推荐引擎" FontSize="18" FontWeight="Bold"
                         Foreground="{{DynamicResource ColorBrush1}}" Margin="0,0,0,8" />
                    <TextBlock Text="By GDSGDHG · 版本号见 output/version.txt" FontSize="13" TextWrapping="Wrap"
                         Foreground="{{DynamicResource ColorBrush4}}" Margin="0,0,0,6" />
                    <TextBlock Text="数据来源: B站视频 + CurseForge/Modrinth 下载" FontSize="12" TextWrapping="Wrap"
                         Foreground="{{DynamicResource ColorBrush5}}" Margin="0,0,0,4" />
                    <TextBlock Text="最后更新: {datetime.now().strftime('%Y-%m-%d')} · 共{total_modpacks}个整合包" FontSize="11" TextWrapping="Wrap"
                         Foreground="{{DynamicResource ColorBrush6}}" Margin="0,0,0,4" />
                    <TextBlock Text="数据仅供参考，非广告推荐" FontSize="10" TextWrapping="Wrap"
                         Foreground="{{DynamicResource ColorBrush7}}" Margin="0,0,0,2" />
                    <TextBlock Text="致谢: PCL2 · B站创作者 · 社区维护者" FontSize="11" TextWrapping="Wrap"
                         Foreground="{{DynamicResource ColorBrush6}}" Margin="0,0,0,0" />
               </StackPanel>
               <StackPanel Grid.Column="1" VerticalAlignment="Center">
                    <local:MyButton Text="⟳ 刷新主页" Padding="16,10,16,10"
                         EventType="刷新主页" Margin="0,0,0,8" />
                    <local:MyButton Text="📮 反馈" Padding="16,10,16,10"
                         ToolTip="前往GitCode提交Issue"
                         EventType="打开网页" EventData="https://gitcode.com/2401_84211770/PCL2-modpack-engine/issues" />
               </StackPanel>
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
    bili = sum(1 for m in modpacks if m.get('bili_url', '#') != '#')
    dl = sum(1 for m in modpacks if m['name'] in dl_links)
    print(f"   🎬 B站视频: {bili}")
    print(f"   📥 下载链接: {dl}")
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
