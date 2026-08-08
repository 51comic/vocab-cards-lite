# Vocab Cards Lite

专业英语词汇闪卡生成器（精简版）。从 JSON 单词数据一键生成黑白打印优化的**主卡 / 副卡 / 百度百科二维码** PNG。

## 特性

- **主卡**：单词 + UK/US 音标 + 词性徽章 + 难度 + 中文释义 + 英文定义 + 固定搭配 + 丰富例句(含中文) + 文化背景
- **副卡**：相关信息 + 相关词汇 + 地道表达 + 文化背景 + 记忆提示
- **二维码**：右下角自动叠加百度百科二维码，可开关
- **字体架构**：IPA 音标 → 包内裁剪字体(68KB)，中英文/ASCII → 系统字体（NotoSansCJK + DejaVu）
- **智能换行**：英文单词不拆词、括号成对、标点黏连不居行首
- **黑白打印优化**：白底黑字灰线
- **精简包体**：仅内置 IPA 音标字体(68KB)，中英文使用系统字体

## 安装依赖

```bash
bash scripts/setup.sh
```

## 使用方法

```bash
python3 scripts/vocab_cards.py <input.json> [output_dir]
```

输入 JSON 格式见 `SKILL.md`。

输出（示例 `word="New Zealand"`）：
- `new_zealand.png` — 主卡
- `new_zealand_qr.png` — 主卡 + 百度百科二维码
- `new_zealand_side.png` — 副卡

## 目录结构

```
├── SKILL.md              # 技能说明
├── README.md
├── _meta.json            # 元数据
├── requirements.txt      # Python 依赖
├── assets/fonts/         # 内置精简字体
├── scripts/
│   ├── vocab_cards.py    # 主脚本
│   └── setup.sh          # 一键安装依赖
└── _samples/             # 生成样卡示例
```

## License

MIT
