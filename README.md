# ⚔ MyWorld · PCL2 整合包推荐引擎

在 **Plain Craft Launcher 2 (PCL2)** 中提供 Minecraft 整合包智能推荐主页，
Gen X Soft Club 暗黑中世纪风格 · 每日自动更新。

**网站地址**：见下方「使用方法」

---

## 🎯 功能特色

- 🎬 **B站热门整合包**：自动抓取 B站 MC 区最新整合包视频，按播放量排序
- 📥 **一键下载**：BBSMC / CurseForge / Modrinth 直链，快速下载整合包
- 👤 **MC 创作者推荐**：籽岷 · 黒山大叔 · 大炒面制造者Cen · Nor叔 · 卡慕SaMa 等
- 🎨 **暗黑中世纪**：Gen X Soft Club 视觉风格，适配 PCL2 窗口

---

## 📥 使用方法

### 推荐：预设链接

在 PCL2 启动器中：

1. 打开 **设置 → 个性化 → 自定义主页**
2. 点击 **「联网更新」**
3. 在「下载地址」中输入：

```
https://raw.gitcode.com/2401_84211770/PCL2-modpack-engine/raw/main/output/Custom.xaml
```

4. 返回启动页，完成！

---

## 📊 数据来源

| 平台 | 说明 |
|------|------|
| 🔍 [B站](https://bilibili.com) | 整合包视频与 UP 主数据 |
| 📥 [BBSMC](https://bbsmc.net) | 中文 MC 资源下载站 |
| 📦 [CurseForge](https://curseforge.com) | 全球最大 MC 模组平台 |
| 📦 [Modrinth](https://modrinth.com) | 开源 MC 整合包平台 |

---

## 📁 项目结构

```
pcl2/
├── src/               ← 生成脚本
│   ├── generator.py      主页生成器
│   └── scrape_links.py   下载链接爬虫
├── data/              ← 数据文件
│   ├── seed_modpacks.json    种子整合包
│   ├── modpack_final.json    整合包终表
│   ├── modpack_ranking.json  排名数据
│   └── ...
├── output/            ← PCL2 直读
│   ├── Custom.xaml        主页文件
│   └── credits.html       致谢页面
└── README.md
```

---

## ⚙ 技术栈

- **XAML** — PCL2 原生自定义主页
- **Python** — 数据采集与主页生成
- **Hermes Agent** — C0 决策团驱动自动更新
- **硅基流动** — 免费视觉 API

---

## 💝 致谢

- **龙腾猫跃** — PCL2 启动器作者
- **Light Beacon** — PCL2 新闻主页开创者
- **Gen X Soft Club** — 视觉风格灵感
- **B站创作者 & 社区维护者**

---

> By GDSGDHG · 2026
