# DESIGN.md — PCL 整合包推荐引擎

> 设计系统定义文件 · 暗黑中世纪风格 · Gen X Soft Club  
> AI Agent 读取此文件后可生成风格一致的 UI 代码。

---

## 一、视觉基调

**风格**：暗黑中世纪 · 地牢灯火  
**关键词**：⚔ 剑 · 🛡 盾 · 🏰 城堡 · ⚒ 铁砧 · 🔮 水晶 · 🔥 余烬  
**氛围**：深邃背景 + 暖色高光 + 冷色点缀 · 像在古老图书馆的烛光下翻阅羊皮纸卷

---

## 二、调色板

PCL2 使用 `DynamicResource` 主题色，本设计系统定义各 `ColorBrush` 的**角色映射**：

| Token | 角色 | 样式用法 |
|---|---|---|
| `ColorBrush1` | **主标题/高亮** | 区块标题、重要数字 |
| `ColorBrush2` | 正文主色 | 较重要文本 |
| `ColorBrush3` | 正文辅助 | 内容说明 |
| `ColorBrush4` | 次要信息 | 元数据、副标题 |
| `ColorBrush5` | 弱提示 | 小字、脚注辅助 |
| `ColorBrush6` | 最低强调 | 版本号、时间戳 |
| `ColorBrush7` | 最弱 | 版权/致谢等极次要文字 |

**主题建议**（用于 PCL2 `ColorSetting.xaml`）：
- 背景：深石板灰 `#1a1a24` · 羊皮纸底 `#23222e`
- 主色：琥珀金 `#d4a74c` · 熔岩橙 `#e67e22`
- 强调：冷铁蓝 `#5b7fa5` · 暮色紫 `#7b5ea7`
- 文字：暖白 `#e8e0d0` · 灰烬灰 `#8a8070`

---

## 三、字体层级

| 层级 | FontSize | FontWeight | 颜色 | 场景 |
|---|---|---|---|---|
| H1 | 22 | Bold | Brush1 | 模块大标题 |
| H2 | 18 | Bold | Brush1 | 页脚/区块副标题 |
| H3 | 15 | Bold | Brush1 | 卡片标题、提示框 |
| Body | 13 | Normal | Brush4 | 描述、说明文字 |
| Small | 12 | Normal | Brush5 | 元数据、平台标注 |
| Tiny | 11 | Normal | Brush6 | 版本号、时间戳 |
| Micro | 10 | Normal | Brush7 | 版权、免责声明 |

---

## 四、间距系统

基于 4px 栅格：

| Token | 值 | 用途 |
|---|---|---|
| `space-xs` | 4 | 微间距、图标间距 |
| `space-sm` | 8 | 内联元素间距 |
| `space-md` | 12 | 提示框与内容间距 |
| `space-lg` | 16 | 卡片内边距 |
| `space-xl` | 20 | 卡片间间距 |
| `space-2xl` | 24 | 区块内边距 |
| `space-3xl` | 28-35 | 标题与内容间距 |
| `space-4xl` | 48+ | 大区块间距 |

**卡片内边距模式**：
- 简单卡片（横幅/页脚）：`Margin="16,18,16,14"` ≈ `lg/top:lg+2, bottom:sm+6`
- 内容卡片（导航/推荐）：`Margin="20-24,28-35,20-24,15-18"`
- 列间距：`ColumnDefinition Width="16"` 固定 16px

---

## 五、组件风格

### MyCard（卡片容器）
- `Margin` 底部统一 `0,0,0,20`（卡片间间距），末张 `0,0,0,0`
- `Title` 选配 ⚡/🏠/🏰 等中世纪主题 emoji
- `CanSwap="True"` 可折叠，视频推荐默认折叠 `IsSwaped="True"`

### MyButton（按钮）
- `Padding="14,8,14,8"` 统一
- 水平排列时 `Margin="6,0,6,0"`
- 使用中世纪词汇 ToolTip

### MyListItem（列表项）
- 标题前缀：`🆕` 新条目 · `🔥` 热门 · 分类 emoji
- 信息行前缀：`▸` 箭头分隔 · 🎬B站 · 📥CF/BS/MR
- `Margin="-2,0,10,0"` 左对齐微调

### MyHint（提示条）
- 导航用 `Theme="Blue"` · 推荐用 `Theme="Yellow"` · 视频用 `Theme="Red"`
- `IsWarn="False"` 默认

---

## 六、区块布局

### 1. 顶部横幅 🏠
- 三行文字居中：标题(H3) → 描述(Small) → 元数据(Tiny)
- 最外层 `Margin="0,0,0,16"`

### 2. 快速导航 ⚡
- 提示条 + 水平按钮行
- 按钮：B站 · CurseForge · Modrinth · BBSMC
- 两列 Grid 布局

### 3. 整合包推荐 🗡️
- H1 标题 + 分类提示条
- 两列布局(`ColumnDefinition Width="*"` + 16px 间隔)
- 左列 = 前 half，右列 = 后 half
- 每个条目：Title(emoji + 分类 + 名称) + Info(播放量+版本+平台)

### 4. MC 热门视频 🎬
- 默认折叠 `IsSwaped="True"`
- 三列布局
- 分区：UP主频道(6) → 精选视频(7) → B站搜索(14)

### 5. 页脚 ℹ️
- H2 左侧标题 + 右侧按钮列
- 技术信息（版本 · 更新 · 数据源）
- 致谢 + 反馈按钮

---

## 七、装饰元素

- 注释分隔线 `═══` 使用双线框（═）分区
- 区块注释使用三行包围结构：

```
<!-- ═══  区块名  ═══ -->
```

- emoji 作为视觉锚点前置
- 信息行统一 `▸` 引导

---

## 八、写作风格

- 英文/中文混排时保持自然间距
- 技术描述简短直接
- 不出现"点击""请"等冗余词
- B站视频用 🎬 前缀标记
- 下载平台缩写：CF=CurseForge · MR=Modrinth · BS=BBSMC
- 版本格式：`1.20.1` · 播放量格式：`27万播放`

---

## 九、可访问性

- 使用 `DynamicResource` 确保跟随 PCL2 主题
- 所有图标按钮必须有 `ToolTip`
- 列表项使用 `Type="Clickable"` 暗示可交互

---

*此文件是项目的设计系统定义，AI Agent 或人类开发者应遵循上述规则生成一致的 UI 代码。*
