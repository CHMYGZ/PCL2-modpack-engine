# MyWorld · PCL2 整合包推荐引擎

[![更新周期](https://img.shields.io/badge/更新-每日自动-8A2BE2)](https://gitcode.com/2401_84211770/PCL2-modpack-engine)
[![许可证](https://img.shields.io/badge/许可证-MIT%2FCC--BY--NC--SA--4.0-green)](LICENSE-CODE)

> **在 Plain Craft Launcher 2 中展示 Minecraft 热门整合包推荐主页**  
> Gen X Soft Club 暗黑中世纪风格 · 每日自动更新 · 多平台数据聚合

- [MyWorld · PCL2 整合包推荐引擎](#myworld--pcl2-整合包推荐引擎)
  - [核心功能](#核心功能)
  - [使用说明](#使用说明)
  - [内容模块](#内容模块)
  - [技术架构](#技术架构)
  - [鸣谢](#鸣谢)
  - [版权声明](#版权声明)
    - [内容部分](#内容部分)
    - [代码部分](#代码部分)

---

## 核心功能

### 1. **整合包聚合推荐** ⚔️
- 📥 **BBSMC 直链下载** — 自动采集 BBSMC 平台最新热门整合包，一键直链下载
- 📦 **CurseForge / Modrinth 同步** — 整合国际主流模组平台数据
- 🎬 **B站热门整合包视频** — 精选 B站 MC 区高播放量整合包推荐视频，附视频链接

### 2. **MC 创作者中心** 🛡️
- 👤 **B站 UP 主推荐** — 籽岷 · 黒山大叔 · 大炒面制造者Cen · Nor叔 · 卡慕SaMa 等知名创作者
- 🔗 **一键跳转** — 直接跳转 B站 UP 主主页 / 视频 / 直播间

### 3. **自动化系统** 🔄
- 🤖 **每日自动更新** — 通过自动化流水线定时采集数据、生成 XAML 主页
- 📊 **版本追踪** — 每次更新自动提交到仓库，可追溯历史版本
- ⚡ **增量更新** — 本地数据缓存机制，减少重复采集

---

## 使用说明

在 PCL2 启动器中：

1. 打开 **设置 → 个性化 → 自定义主页**
2. 点击 **「联网更新」**
3. 在「下载地址」中输入：

```
https://raw.gitcode.com/2401_84211770/PCL2-modpack-engine/raw/main/output/Custom.xaml
```

4. 返回启动页，加载完成即可使用

> 💡 **提示**：如果网络波动导致加载失败，刷新主页即可重试。

---

## 内容模块

### 1. **整合包精选** 🗡️
- BBSMC 热门整合包直链列表（含大小、版本、下载量）
- CurseForge / Modrinth 国际平台精选
- 每项包含简介文字、下载来源标识

### 2. **热门视频推荐** 🎬
- B站 MC 区整合包视频推荐
- 按播放量排序展示
- 点击直接跳转 B站视频页面

### 3. **创作者推荐** 👤
- B站知名 MC 创作者卡片展示
- 支持跳转 UP 主主页 / 视频合集 / 直播间
- 持续更新创作者列表

### 4. **资讯动态** 📰
- 更新日志与最新改动
- 主页版本号展示
- 反馈入口

---

## 技术架构

### 数据流

```
[B站 API] ──┐
[BBSMC] ────┤──→ [Python 采集器] ──→ [XAML 生成] ──→ [GitCode 发布] ──→ [PCL2 加载]
[CurseForge] ─┘
[Modrinth] ──┘
```

### 技术栈

| 组件 | 说明 |
|------|------|
| **XAML** | PCL2 原生自定义主页语言，WPF 风格 |
| **Python** | 数据采集、处理与 XAML 自动生成 |
| **GitCode** | 代码托管与原始文件分发（Raw CDN） |
| **PCL2** | Plain Craft Launcher 2 启动器 |

### 目录结构

```
├── output/          # 生成的 XAML 主页文件
├── src/             # Python 采集与生成脚本
├── data/            # 数据缓存与配置
├── docs/            # 文档与设计图
├── LICENSE-CODE     # 代码许可证 (MIT)
├── LICENSE-CONTENT  # 内容许可证 (CC BY-NC-SA 4.0)
└── README.md
```

---

## 鸣谢

- **[龙腾猫跃](https://afdian.com/a/LTCat)** — **[PCL2](https://github.com/Meloong-Git/PCL)** 启动器作者
- **[Light Beacon](https://github.com/Light-Beacon/PCL2-NewsHomepage)** — PCL2 主页生态开创者，灵感来源
- **[Gen X Soft Club](https://genxsoft.club)** — 暗黑中世纪视觉风格灵感
- **B站 MC 区 UP 主与社区维护者** — 持续产出的优质内容

> （排名不分先后）

---

## 版权声明

### 内容部分

- **范围**：`output/` 目录下的 `.xaml` 文件、`docs/` 文档、`README.md`
- **采用** **[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)** 许可
- **包含的第三方数据版权归原始平台所有**（B站视频/UP主信息、BBSMC/CurseForge/Modrinth 整合包信息）

### 代码部分

- **范围**：`src/` 目录下的 Python 脚本
- **采用** **[MIT License](LICENSE-CODE)** 许可

> [!IMPORTANT]
> **重要声明**：本系统采集的整合包数据来自 B站、BBSMC、CurseForge、Modrinth 等公开平台，数据版权归属于原始平台和创作者。本仓库仅提供技术整合与视觉呈现，不对第三方数据的内容与版权负责，用户需自行确保合规使用。
