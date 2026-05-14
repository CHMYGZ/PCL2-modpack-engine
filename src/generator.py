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
    # ── 精选热门视频 · 更新于2026-05-12 · 按播放量排序 ──
    ("🔥 乌托邦探险3.2 365万", "https://www.bilibili.com/video/BV1Kf421X7cg/"),
    ("🔥 中世纪王国100天 364万", "https://www.bilibili.com/video/BV1bE421P7zG/"),
    ("🔥 年度MC十大神包289万", "https://www.bilibili.com/video/BV1p1421C75Q/"),
    ("🔥 一个包2000万下载256万", "https://www.bilibili.com/video/BV15M4m127dH/"),
    ("🔥 方块宝可梦ZA 254万", "https://www.bilibili.com/video/BV1VNLRzYERC/"),
    ("🔥 愚者第二季 237万", "https://www.bilibili.com/video/BV1eo18BREZi/"),
    ("🔥 10款冒险向神包215万", "https://www.bilibili.com/video/BV1J24y1R7GT/"),
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

def emoji_fix(s):
    """将可能渲染为单色线条的 Unicode 符号替换为彩色 emoji"""
    replacements = {
        '\u2699': '\U0001F527',   # ⚙ → 🔧 (gear → wrench)
        '\u2694': '\u2694\ufe0f', # ⚔ → ⚔️ (add VS16 for emoji presentation)
        '\u26A1': '\u26A1\ufe0f', # ⚡ → ⚡️ (add VS16)
        '\U0001F5E1': '\U0001F5E1\ufe0f', # 🗡 → 🗡️ (add VS16)
        '\U0001F6E1': '\U0001F6E1\ufe0f', # 🛡 → 🛡️ (add VS16)
    }
    for old, new in replacements.items():
        s = s.replace(old, new)
    return s

# emoji → MC 方块图映射
GENRE_BLOCK_MAP = {
    '🔥': ('RedstoneBlock', '硬核'), '🔧': ('Cobblestone', '科技'),
    '🏰': ('Anvil', '冒险'), '🧙': ('CommandBlock', '魔法'),
    '🌿': ('Grass', '休闲'), '🗺': ('Egg', '空岛'),
    '🎮': ('GoldBlock', '宝可梦'), '⚡': ('RedstoneLampOn', '混合'),
    '⚔': ('Anvil', '战斗'), '🗡': ('Anvil', 'RPG'),
    '💀': ('RedstoneLampOff', '恐怖'), '🧟': ('RedstoneLampOff', '末日'),
    '🛡': ('GoldBlock', '防御'), '📦': ('Fabric', '其他'),
}

def make_block_row(emoji_list, item_name, item_info, target_url, is_seed=False):
    """生成带 MC 方块图标的列表行 XAML"""
    # 从 genre 字符串中提取第一个已知 emoji 来匹配方块
    first_block = None
    for genre_str in emoji_list:
        for c in genre_str:
            if c in GENRE_BLOCK_MAP:
                first_block, label = GENRE_BLOCK_MAP[c]
                break
        if first_block:
            break
    if not first_block:
        first_block = 'Fabric'
    
    # 有有效链接才生成可点击事件
    if target_url and target_url != '#':
        click_part = f'''
                    EventType="打开网页"
                    EventData="{escape(target_url)}"
                    Type="Clickable" />'''
    else:
        click_part = ' />'
    
    xaml = f'''          <Grid Margin="-2,0,10,2" VerticalAlignment="Center">
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="22" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
               <local:MyImage Grid.Column="0" Width="18" Height="18"
                    Source="{PACK_URL}{first_block}.png"
                    VerticalAlignment="Center" HorizontalAlignment="Left" />
               <local:MyListItem Grid.Column="1"
                    Title="{item_name}"
                    Info="{escape(item_info)}"{click_part}
          </Grid>'''
    return xaml


PLATFORM_CONFIG = [
    ('curseforge_url', 'CF', 'CurseForge'),
    ('modrinth_url', 'MR', 'Modrinth'),
    ('bbsmc_url', 'BS', 'BBSMC'),
    ('mcmod_url', '百科', 'MC百科'),
]


def make_dl_row(mp, primary_label, is_seed=False):
    """生成平台下载链接行（小按钮），不重复主链接对应平台"""
    buttons = []
    for key, short, full in PLATFORM_CONFIG:
        url = mp.get(key)
        if url:
            # 跳过主链接已覆盖的平台（避免冗余）
            if full == primary_label:
                continue
            buttons.append(f'''                         <local:MyButton Margin="2,0,2,0" Padding="6,2,6,2" Height="24"
                              EventType="打开网页" EventData="{escape(url)}">
                              <TextBlock Text="{full}" />
                         </local:MyButton>''')
    
    if not buttons:
        return ''
    
    btn_xaml = f'''          <Grid Margin="24,0,10,2" VerticalAlignment="Center">
               <StackPanel Orientation="Horizontal">
{chr(10).join(buttons)}
               </StackPanel>
          </Grid>'''
    return btn_xaml

# PCL2 内嵌的 Minecraft 方块图片资源映射
BLOCK_ICONS = {
    'fire': 'RedstoneBlock',
    'tech': 'Cobblestone',
    'castle': 'Anvil',
    'magic': 'CommandBlock',
    'nature': 'Grass',
    'island': 'Egg',
    'games': 'GoldBlock',
    'mixed': 'RedstoneLampOn',
    'home': 'Grass',
    'rpg': 'Anvil',
    'sword': 'Anvil',
    'fight': 'RedstoneBlock',
    'horror': 'RedstoneLampOff',
    'combat': 'RedstoneBlock',
    'other': 'Fabric',
}

PACK_URL = 'pack://application:,,,/images/Blocks/'

def block_img(block_name, size=16):
    """生成引用方块图片的 local:MyImage XAML"""
    return f'<local:MyImage Width="{size}" Height="{size}" Source="{PACK_URL}{block_name}.png" VerticalAlignment="Center" />'

def genre_to_block(genre_emoji):
    """根据 genre emoji 返回对应的方块名"""
    emoji_map = {
        '🔥': 'RedstoneBlock', '🔧': 'Cobblestone', '🏰': 'Anvil',
        '🧙': 'CommandBlock', '🌿': 'Grass', '🗺': 'Egg',
        '🎮': 'GoldBlock', '⚡': 'RedstoneLampOn', '⚔': 'Anvil',
        '🗡': 'Anvil', '💀': 'RedstoneLampOff', '🧟': 'RedstoneLampOff',
        '🛡': 'GoldBlock', '📦': 'Fabric', '🏆': 'GoldBlock',
        '📖': 'CommandBlock',
    }
    return emoji_map.get(genre_emoji)

def escape(s):
    return emoji_fix(s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

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
    """生成单个整合包行: MC方块图 + 版本/平台信息
    主链接按优先级: CurseForge > Modrinth > BBSMC > 百科 > B站
    不混用: 平台包跳平台，B站包跳B站
    """
    name = escape(mp['name'][:25])
    genres = mp.get('genres', ['📦'])
    play = mp.get('bili_play_str', '?')
    
    # 确定主链接（平台优先，无平台才用B站）
    if mp.get('curseforge_url'):
        target_url = escape(mp['curseforge_url'])
        link_label = 'CurseForge'
    elif mp.get('modrinth_url'):
        target_url = escape(mp['modrinth_url'])
        link_label = 'Modrinth'
    elif mp.get('bbsmc_url'):
        target_url = escape(mp['bbsmc_url'])
        link_label = 'BBSMC'
    elif mp.get('mcmod_url'):
        target_url = escape(mp['mcmod_url'])
        link_label = 'MC百科'
    else:
        target_url = mp.get('bili_url', '#')
        link_label = 'B站'
    
    # 版本
    version = mp.get('version', '')
    ver_str = f" · {version}" if version else ""
    
    # 平台可用性（Info行尾部标注，不重复主链接平台）
    platforms = []
    if mp.get('curseforge_url') and link_label != 'CurseForge': platforms.append('CF')
    if mp.get('bbsmc_url') and link_label != 'BBSMC': platforms.append('BS')
    if mp.get('mcmod_url') and link_label != 'MC百科': platforms.append('百科')
    if mp.get('modrinth_url') and link_label != 'Modrinth': platforms.append('MR')
    platform_str = f" · 📥{'/'.join(platforms)}" if platforms else ""
    
    # 构建Info行（主链接信息 + 平台标注）
    if link_label == 'B站' and target_url and target_url != '#':
        info_str = f"▸ 🎬B站 · {play}{ver_str}{platform_str}"
    elif target_url and target_url != '#':
        info_str = f"▸ 📥{link_label}{ver_str}{platform_str}"
    else:
        info_str = f"▸ 待补充{ver_str}{platform_str}"
    
    return make_block_row(genres, name, info_str, target_url, is_seed) + '\n'
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
    # 三列布局
    third = (display_count + 2) // 3
    col0_packs = modpacks[:third]
    col1_packs = modpacks[third:third*2]
    col2_packs = modpacks[third*2:]
    
    # 标记种子条目
    def is_seed(mp, idx):
        return idx < seed_count
    
    col0_items = [make_item(mp, dl_links.get(mp['name']), i, is_seed(mp, i)) for i, mp in enumerate(col0_packs)]
    col1_items = [make_item(mp, dl_links.get(mp['name']), i+third, is_seed(mp, i+third)) for i, mp in enumerate(col1_packs)]
    col2_items = [make_item(mp, dl_links.get(mp['name']), i+third*2, is_seed(mp, i+third*2)) for i, mp in enumerate(col2_packs)]
    
    # ── 快速按钮栏 ──
    buttons = [
        ("B站MC区", "https://search.bilibili.com/all?keyword=Minecraft+整合包&order=click", "搜索Minecraft整合包视频", "RedstoneBlock"),
        ("CurseForge", "https://www.curseforge.com/minecraft/modpacks", "全球最大MC模组平台", "Anvil"),
        ("Modrinth", "https://modrinth.com/modpacks", "开源MC整合包平台", "CommandBlock"),
        ("BBSMC", "https://bbsmc.net/modpacks", "中文MC资源下载站", "Grass"),
    ]
    
    btn_items = []
    for text, url, tooltip, block in buttons:
        btn_items.append(
            f'               <local:MyButton Margin="5,0,5,0" Padding="14,8,14,8" Height="36"\n'
            f'                    ToolTip="{tooltip}"\n'
            f'                    EventType="打开网页" EventData="{escape(url)}">\n'
            f'                    <StackPanel Orientation="Horizontal">\n'
            f'                         <local:MyImage Width="16" Height="16"\n'
            f'                              Source="{PACK_URL}{block}.png"\n'
            f'                              VerticalAlignment="Center" />\n'
            f'                         <TextBlock Text="{text}" VerticalAlignment="Center"\n'
            f'                              Margin="4,0,0,0" />\n'
            f'                    </StackPanel>\n'
            f'               </local:MyButton>'
        )
    
    btn_bar = '\n'.join(btn_items)
    
    # ── 热门视频栏 ──
    vid_icons = ["🎬", "🔧", "😂", "🏗", "🎮", "🌟", "🎨", "🎯", "⚔️", "📖",
                 "🎤", "🤣", "⏱", "🏰", "⚡️", "📦", "✨", "🎞", "💯", "👥",
                 "🔥", "💀", "🗡️", "🛡️", "🧙", "🌍", "🏆", "🎲", "👾", "💎",
                 "🕹️", "🎭", "🗺️", "🌟", "⚗️", "🌿", "🧟", "🔮", "⛏️", "🎪"]
    # 视频条目使用的 MC 方块图
    vid_blocks = ['Grass', 'RedstoneBlock', 'GoldBlock', 'Cobblestone', 'Anvil', 'CommandBlock',
                  'RedstoneLampOn', 'Fabric', 'RedstoneLampOff', 'Egg']
    vid_items = []
    for i, (title, url) in enumerate(HOT_VIDEOS):
        block = vid_blocks[i % len(vid_blocks)]
        escaped_title = escape(title)
        vid_items.append(f'''          <Grid Margin="-2,0,10,2" VerticalAlignment="Center">
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="22" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
               <local:MyImage Grid.Column="0" Width="16" Height="16"
                    Source="{PACK_URL}{block}.png"
                    VerticalAlignment="Center" HorizontalAlignment="Left" />
               <local:MyListItem Grid.Column="1"
                    Title="{escaped_title}"
                    Info="▸ 点击前往 B站观看"
                    EventType="打开网页"
                    EventData="{escape(url)}"
                    Type="Clickable" />
          </Grid>''')

    total_modpacks = len(modpacks)

    xaml = f'''<!--
  ═══════════════════════════════════════════════
   PCL2 整合包推荐引擎 · 暗黑中世纪风格设计
   数据源: B站 + BBSMC + CurseForge + Modrinth
   📥BBSMC:{bbsmc_count} 🎬B站视频:{bili_count} 📥直链下载:{dl_count}
   更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}
  ═══════════════════════════════════════════════
-->

<!-- ================================ -->
<!-- ================================ -->
<!--  顶部横幅  -->
<!-- ================================ -->
<local:MyCard Margin="0,0,0,16" Title="">
     <StackPanel Margin="20,22,20,20">
          <TextBlock Text="PCL2 整合包推荐引擎" FontSize="18" FontWeight="Bold"
               Foreground="{{DynamicResource ColorBrush1}}"
               HorizontalAlignment="Center" />
          <TextBlock Text="聚合 B站 / BBSMC / CurseForge / Modrinth" FontSize="10"
               Foreground="{{DynamicResource ColorBrush5}}"
               HorizontalAlignment="Center" Margin="0,6,0,0" />
     </StackPanel>
</local:MyCard>

<!-- ================================ -->
<!--  🔴 快速导航 · 四大传送门   -->
<!-- ================================ -->
<local:MyCard Margin="0,0,0,20" Title="⚡️ 快速导航">
     <StackPanel Margin="24,30,24,20">
          <local:MyHint IsWarn="False" Theme="Blue"
               Text="常用资源站点一键直达 · B站搜索 + CurseForge + Modrinth + BBSMC 四大数据源"
               Margin="0,0,0,14" />
          <StackPanel Orientation="Horizontal" HorizontalAlignment="Center">
{btn_bar}
          </StackPanel>
     </StackPanel>
</local:MyCard>

<!-- ================================ -->
<!--  🏗 整合包推荐 · 方块精选   -->
<!-- ================================ -->
<local:MyCard Margin="0,0,0,20" Title="Minecraft 整合包推荐">
     <StackPanel Margin="24,35,24,18">
          <TextBlock Text="整合包推荐" FontSize="22" FontWeight="Bold"
               Foreground="{{DynamicResource ColorBrush1}}"
               HorizontalAlignment="Center" Margin="0,0,0,12" />
          <local:MyHint IsWarn="False" Theme="Yellow"
               Text="🔥硬核 🔧科技 🏰冒险 🧙魔法 🌿休闲 🗺空岛 🎮宝可梦 ⚡️混合 | 🎬B站视频推荐 · 下方 📥下载链接"
               Margin="0,0,0,14" />

          <Grid>
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="10" />
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="10" />
                    <ColumnDefinition Width="*" />
               </Grid.ColumnDefinitions>
               <StackPanel Grid.Column="0">
{chr(10).join(col0_items)}
               </StackPanel>
               <StackPanel Grid.Column="2">
{chr(10).join(col1_items)}
               </StackPanel>
               <StackPanel Grid.Column="4">
{chr(10).join(col2_items)}
               </StackPanel>
          </Grid>
     </StackPanel>
</local:MyCard>

<!-- ================================ -->
<!--  🎬 视频推荐 · 映像大厅   -->
<!-- ================================ -->
<local:MyCard Margin="0,0,0,20" Title="Minecraft 视频推荐">
     <StackPanel Margin="24,32,24,18">
          <TextBlock Text="视频推荐" FontSize="22" FontWeight="Bold"
               Foreground="{{DynamicResource ColorBrush1}}"
               HorizontalAlignment="Center" Margin="0,0,0,10" />
          <local:MyHint IsWarn="False" Theme="Red"
               Text="🎬 知名UP主空间 + 🔥 热门搜索主题 · 涵盖实况/红石/建筑/模组/动画/速通"
               Margin="0,0,0,14" />
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

<!-- ================================ -->

<!-- ================================ -->
<!-- ================================ -->

<!-- ================================ -->
<!-- ================================ -->

<!-- ================================ -->
<!-- ================================ -->

<!-- ================================ -->
<!-- ================================ -->

<!-- ================================ -->
<!-- ================================ -->

<!-- ================================ -->
<!-- ================================ -->

<!-- ================================ -->
<!-- ================================ -->

<!-- ================================ -->
<!-- ================================ -->

<!-- ================================ -->
<!-- ================================ -->

<!-- ================================ -->
<!-- ================================ -->

<!-- ================================ -->
<!-- ================================ -->

<!-- ================================ -->
<!--  ⛏ 关于 · 匹配栏目风格         -->
<!-- ================================ -->
<local:MyCard Margin="0,0,0,0" Title="">
     <StackPanel>
          <Grid Margin="24,22,14,22">
               <Grid.ColumnDefinitions>
                    <ColumnDefinition Width="*" />
                    <ColumnDefinition Width="Auto" />
               </Grid.ColumnDefinitions>
               <!-- 左侧：标题 + 作者 -->
               <StackPanel Grid.Column="0" VerticalAlignment="Center">
                    <StackPanel Orientation="Horizontal">
                         <TextBlock Text="PCL2" FontSize="18"
                              Foreground="{{DynamicResource ColorBrush1}}" FontWeight="Bold" VerticalAlignment="Center" />
                         <TextBlock Text=" 整合包推荐引擎" 
                              FontSize="18" FontWeight="Bold"
                              Foreground="{{DynamicResource ColorBrush1}}" VerticalAlignment="Center" />
                    </StackPanel>
                    <StackPanel Orientation="Horizontal" Margin="0,4,0,0">
                         <TextBlock Text="By GDSGDHG" FontSize="11"
                              Foreground="{{DynamicResource ColorBrush5}}" FontWeight="Bold" />
                         <TextBlock Text=" · " FontSize="11"
                              Foreground="{{DynamicResource ColorBrush5}}" FontWeight="Bold" />
                         <TextBlock Text="数据源" FontSize="11"
                              Foreground="{{DynamicResource ColorBrush5}}" FontWeight="Bold" />
                         <TextBlock Text=" B站 · BBSMC · CF · MR" FontSize="11"
                              Foreground="{{DynamicResource ColorBrush5}}" FontWeight="Bold" />
                    </StackPanel>
               </StackPanel>
               <!-- 右侧：刷新 + 反馈（竖排堆叠） -->
               <StackPanel Grid.Column="1" VerticalAlignment="Center">
                    <local:MyButton BorderThickness="0" Padding="14,6,14,6"
                         ToolTip="刷新当前主页内容" EventType="刷新主页">
                         <StackPanel Orientation="Horizontal">
                              <TextBlock Text="↻" FontSize="14" FontWeight="Bold"
                                   Foreground="{{DynamicResource ColorBrush1}}"
                                   VerticalAlignment="Center" Margin="0,0,4,0" />
                              <TextBlock Text="刷新" FontSize="12" FontWeight="Bold"
                                   Foreground="{{DynamicResource ColorBrush1}}"
                                   VerticalAlignment="Center" />
                         </StackPanel>
                    </local:MyButton>
                    <local:MyButton BorderThickness="0" Padding="14,6,14,6" Margin="0,6,0,0"
                         ToolTip="前往GitCode提交Issue"
                         EventType="打开网页"
                         EventData="https://gitcode.com/2401_84211770/PCL2-modpack-engine/issues">
                         <StackPanel Orientation="Horizontal">
                              <TextBlock Text="📮" FontSize="12" FontWeight="Bold"
                                   Foreground="{{DynamicResource ColorBrush1}}"
                                   VerticalAlignment="Center" Margin="0,0,4,0" />
                              <TextBlock Text="反馈" FontSize="12" FontWeight="Bold"
                                   Foreground="{{DynamicResource ColorBrush1}}"
                                   VerticalAlignment="Center" />
                         </StackPanel>
                    </local:MyButton>
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
