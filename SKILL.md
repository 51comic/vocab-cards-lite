---
name: vocab-cards-lite
slug: vocab-cards-lite
version: 1.0.4
displayName: 英语词汇闪卡 Lite
description: 专业英语词汇闪卡生成器(精简版)。从 JSON 单词数据一键生成黑白打印优化的主卡/副卡/百度百科二维码 PNG。仅内置 IPA 音标字体(68KB)，中英文使用系统字体。
---

# Vocab Cards Lite — 专业英语词汇闪卡生成器(精简版)

从 JSON 单词数据生成黑白打印优化的专业英语闪卡 PNG。**主卡 + 副卡 + 百度百科二维码**三件套，功能与完整版完全一致，区别仅在于**仅内置 IPA 音标字体(68KB)，中英文使用系统字体**（完整版内置完整 CJK 字体，约 40MB）。

## 与完整版 vocab-cards-pro 的区别

| | vocab-cards-lite | vocab-cards-pro |
|---|---|---|
| 包体大小 | **68KB** (仅 IPA 字体) | 约 40MB (完整 CJK 字体) |
| 中文字体 | 系统字体（需自行安装 NotoSansCJK） | 全量 NotoSansCJK |
| 适用场景 | 通用词汇闪卡发布/分发（需系统有中文字体） | 开箱即用，覆盖任意生僻汉字 |
| 功能 | 完全相同 | 完全相同 |

> 仅内置 IPA 音标字体（69 个字符，64KB），中英文/ASCII 使用系统字体（NotoSansCJK + DejaVu），足以满足中学/大学/四六级/雅思等常见词汇闪卡需求。

## 使用场景

- 需要把一批英文单词（音标/词性/释义/搭配/例句/文化背景）批量生成闪卡 PNG
- 生成面向**黑白打印**的简洁卡片（白底黑字灰线）
- 中英文混排，IPA 音标、CJK 中文、英文字体分别处理，根治"豆腐块"

## 核心能力

- **主卡**：单词 + UK/US 音标 + 词性徽章 + 难度 + 中文释义 + 英文定义 + 固定搭配 + 丰富例句(含中文) + 文化背景
- **副卡**：相关信息 + 相关词汇 + 地道表达 + 文化背景 + 记忆提示
- **二维码**：右下角自动叠加 180px 百度百科二维码，标注 "Baidu Baike"，可开关
- **字体架构**：IPA 音标 → 包内裁剪字体(68KB)，中英文/ASCII → 系统字体（NotoSansCJK + DejaVu）
- **智能换行**：英文单词不拆词、括号成对、标点黏连不居行首
- **黑白打印优化**：白底 #fff / 黑字 #000 / 灰阶 #374151、#6b7280、#d1d5db
- **文件命名**：按英文单词 slug 化（`new_zealand.png` / `red_army.png` / `red_army_side.png`）

## 环境依赖（已随包打包 ✅）

Python 库（`pillow` / `fonttools` / `qrcode[pil]`）需安装，**系统需有 NotoSansCJK 和 DejaVu 中文字体**。

### 一键安装依赖

```shell
bash scripts/setup.sh
```

自动：安装三个 Python 库 → 校验字体可用性 → 验证可导入。

### 字体架构

| 字体 | 来源 | 用途 |
|------|------|------|
| NotoSansCJK (.ttc) | 系统字体 | 中文/CJK |
| DejaVuSans (.ttf) | 系统字体 | 英文/ASCII |
| DejaVuSans-IPA (.ttf) | **包内自带 (68KB)** | IPA 音标专用 |

> 脚本优先读取包内 IPA 字体，中英文/ASCII 使用系统字体。包体仅 68KB，无需随包分发大型字体文件。

## 输入 JSON 格式

```json
[
  {
    "word": "New Zealand",
    "ipa_uk": "njuː ˈziːlənd",
    "ipa_us": "nuː ˈziːlənd",
    "pos": "n.",
    "level": "C1",
    "cn": "新西兰",
    "en": "An island country in the southwestern Pacific Ocean.",
    "coll": ["New Zealanders", "North Island", "Maori culture"],
    "examples": [["I visited New Zealand last summer.", "我去年夏天去了新西兰。"]],
    "note": "位于南太平洋的岛国，毛利文化是其独特标识。",
    "baike_url": "https://baike.baidu.com/item/新西兰",
    "side": {
      "category": "Geography",
      "info": "毛利语 Aotearoa，意为“长白云之乡”。",
      "related": ["Auckland", "Wellington", "Kiwi"],
      "expressions": ["Kia ora — 毛利语问候"],
      "culture": "毛利文化与英式文化交融。",
      "tip": "aotearoa → 长白云之地，记住白云即新西兰。"
    }
  }
]
```

## 调用方式

```shell
python3 scripts/vocab_cards.py <input.json> [output_dir]
```

输出示例（`word="New Zealand"`）：
- `new_zealand.png` — 主卡
- `new_zealand_qr.png` — 主卡 + 百度百科二维码
- `new_zealand_side.png` — 副卡（仅当条目含 `side` 字段）

## 注意事项

- 生僻字显示依赖系统字体；若遇生僻字显示方框，请安装系统字体 NotoSansCJK 或改用完整版 `vocab-cards-pro`
- 图片固定 **1000 × 1700** 竖向排版，为 A4 黑白打印/卡片设计
- 单个单词失败不中断整批（逐条 try/except）
