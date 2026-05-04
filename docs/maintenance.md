# 维护说明

> 如何维护 PCL2 整合包推荐引擎的推荐列表

---

## 数据来源

| 平台 | 数据类型 | 获取方式 |
|------|---------|---------|
| [B站](https://bilibili.com) | 整合包视频、UP 主信息 | B站 API 搜索 |
| [BBSMC](https://bbsmc.net) | 中文整合包下载链接 | 页面采集 |
| [CurseForge](https://curseforge.com/minecraft/modpacks) | 国际整合包信息 | 页面采集 + API |
| [Modrinth](https://modrinth.com/modpacks) | 开源整合包信息 | API 采集 |

---

## 推荐排序规则

整合包排序基于以下因素综合计算：

1. **热度** — B站视频播放量、BBSMC 下载量、CurseForge 关注数
2. **更新时间** — 近期更新 / 发布的整合包获得加分
3. **可访问性** — 链接有效性、下载源稳定性
4. **多样性** — 平衡不同类型（科技/魔法/冒险/空岛等）

> **重要声明**：本推荐列表为算法自动排序，**不是广告榜单**。收录不收取任何费用，排序不受商业因素影响。

---

## 如何维护

### 自动维护（默认）

- 每日 07:00 (UTC+8) 自动执行数据采集和主页生成
- 数据同步到 GitCode 仓库和 ECS 服务器
- 无需人工干预

### 手动维护

数据采集脚本位于 `src/` 目录：

```bash
# 重新采集全部数据
python3 src/scrape_links.py

# 重新生成 XAML 主页
python3 src/generator.py
```

### 添加/修改推荐

1. 编辑 `data/modpack_links.json` 添加新的整合包条目
2. 运行 `python3 src/generator.py` 重新生成 XAML
3. 提交到 GitCode

---

## 质量要求

- 每个整合包必须有有效的下载来源或视频链接
- 优先收录近期活跃（1年内有更新）的整合包
- 不收录包含恶意软件/盗版内容/违规内容的整合包
- 不收录纯服务器宣传性质的"整合包"

---

## 版本管理

- 版本号记录在 `output/version.txt`（格式：`YYYY.MM.DD-序号`）
- 每次修改 `output/Custom.xaml` 后同步更新版本号
- 重大变更请同步更新 `CHANGELOG.md`
