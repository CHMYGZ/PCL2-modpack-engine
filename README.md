# PCL 整合包推荐引擎

![[项目横幅]](docs/images/banner.png)

[![更新周期](https://img.shields.io/badge/更新-每日自动-8A2BE2)](https://gitcode.com/2401_84211770/PCL-modpack-engine)
[![版本](https://img.shields.io/badge/版本-2026.05.04--042-blue)](output/version.txt)
[![许可证-代码](https://img.shields.io/badge/代码-MIT-green)](LICENSE-CODE)
[![许可证-内容](https://img.shields.io/badge/内容-CC--BY--NC--SA--4.0-orange)](LICENSE-CONTENT)

PCL 整合包推荐引擎是一个用于 PCL2 启动器的联网自定义主页，面向 Minecraft 玩家提供整合包推荐、视频内容入口、资源站快捷跳转与常用资源导航。它希望把分散在 B站、BBSMC、CurseForge、Modrinth 等平台上的整合包相关信息整理到一个更直观的位置，让玩家在打开 PCL2 时就能快速发现、了解并跳转到感兴趣的整合包资源。

- [PCL 整合包推荐引擎](#pcl2-整合包推荐引擎)
  - [项目简介](#项目简介)
  - [核心功能](#核心功能)
  - [使用说明](#使用说明)
  - [内容模块](#内容模块)
  - [数据来源](#数据来源)
  - [鸣谢](#鸣谢)
  - [版权声明](#版权声明)
    - [内容部分](#内容部分)
    - [代码部分](#代码部分)
  - [免责声明](#免责声明)

---

## 项目简介

一个清爽、实用、直观的 PCL2 自定义主页，围绕 Minecraft 整合包推荐组织内容。

- 面向 PCL2 自定义主页配置
- 聚合整合包相关资源链接
- 提供 CurseForge、Modrinth、BBSMC、B站等平台入口
- 适合玩家快速发现、了解、跳转整合包资源
- 保持轻量、直观、便于长期维护

---

## 核心功能

### 1. **整合包内容聚合** 🗡️
- 展示常见 Minecraft 整合包推荐
- 整合 B站视频、BBSMC、CurseForge、Modrinth 等来源
- 帮助玩家快速了解整合包热度、来源与访问入口

### 2. **常用资源站快捷入口** 🔗
- 提供主流 Minecraft 资源平台一键跳转
- 减少玩家在不同网站间反复搜索的成本
- 适合作为 PCL2 启动器首页入口

### 3. **轻量化主页体验** ⚡
- 使用 PCL2 自定义主页 XAML 实现
- 页面结构清晰，加载负担低
- 适合长期联网更新和维护

### 4. **可持续维护** 🔄
- 支持后续更新推荐列表
- 支持添加新整合包、新视频、新资源站
- 可通过版本文件记录更新状态

---

## 使用说明

在 PCL2 启动器中：

1. 打开 **「设置」**
2. 进入 **「个性化」**
3. 找到 **「自定义主页」**
4. 在 **「联网更新」** 中填入：

```
https://qawsedrftgyhujiko.fun/pcl2/Custom.xaml
```

5. 保存后刷新主页即可使用

> 如果主页没有刷新，请尝试点击主页上的 **「刷新」** 按钮或重启 PCL2。

---

## 内容模块

### 1. **整合包推荐** 🗡️
- 展示精选 Minecraft 整合包
- 提供资源来源、热度信息或简介
- 帮助玩家快速筛选感兴趣的内容

### 2. **视频推荐** 🎬
- 收录与整合包相关的视频内容
- 方便玩家通过视频了解玩法、特色和安装效果

### 3. **资源站入口** 🔗
- 提供 CurseForge、Modrinth、BBSMC、B站等常用入口
- 方便玩家快速跳转到外部资源站

### 4. **关于与说明** ℹ️
- 说明项目用途、数据来源和维护状态
- 明确该主页仅用于资源导航与推荐，不代表官方排名

---

## 数据来源

本主页中的整合包、视频和资源站信息主要来源于公开可访问的平台，包括但不限于：

- [CurseForge](https://curseforge.com/minecraft/modpacks)
- [Modrinth](https://modrinth.com/modpacks)
- [BBSMC](https://bbsmc.net/modpacks)
- [B站](https://search.bilibili.com/all?keyword=Minecraft+整合包)
- 其他 Minecraft 社区公开资源

所有第三方内容的版权归原作者或原平台所有。本项目仅做信息整理、导航与推荐展示。

---

## 鸣谢

- **[龙腾猫跃](https://afdian.com/a/LTCat)** — **[PCL2](https://github.com/Meloong-Git/PCL)** 启动器作者
- **[Light Beacon](https://github.com/Light-Beacon/PCL2-NewsHomepage)** — PCL2 主页生态开创者
- **[EYicheng](https://github.com/EYicheng/PCL2-TodayHomepage)** — README 结构参考
- Minecraft 社区整合包作者、视频作者与资源站维护者
- 为本项目提出建议和反馈的玩家

> （排名不分先后）

---

## 版权声明

### 内容部分

- **范围**：`output/` 目录下的 `.xaml` 文件、`README.md`、`docs/` 说明文档、`screenshots/` 截图
- **采用** **[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)** 许可
- **包含的第三方数据版权归原始平台和原作者所有**

### 代码部分

- **范围**：`src/` 目录下的 Python 脚本、`data/` 目录下的版本与配置脚本
- **采用** **[MIT License](LICENSE-CODE)** 许可

---

## 免责声明

> [!IMPORTANT]
> **重要声明**：本项目仅提供 Minecraft 整合包相关信息的整理、推荐和跳转入口，不托管第三方整合包文件，不代表任何平台或作者的官方立场。页面中涉及的整合包、视频、图片、名称和链接，其版权与解释权归原作者、发布者或对应平台所有。如果相关内容存在侵权、失效或不适合展示的情况，请通过 [Issue](https://gitcode.com/2401_84211770/PCL-modpack-engine/issues) 联系删除或修改。
