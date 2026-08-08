#!/usr/bin/env bash
# setup.sh — 一键安装 vocab-cards-lite 的 Python 依赖并校验字体可用性。
# 用法: bash setup.sh    (建议在 skill 目录内运行)
set -euo pipefail

cd "$(dirname "$0")/.."

echo "==> 安装 Python 依赖 (pillow / fonttools / qrcode[pil])"

# v2.0.0: 优先普通安装;仅在系统 Python(PEP 668)下回退 --break-system-packages
pip_install() {
    local pip_cmd="$1"
    if "$pip_cmd" install -r requirements.txt 2>/dev/null; then
        return 0
    fi
    echo "   常规安装失败(可能是系统 Python 的 PEP 668 保护),尝试 --break-system-packages ..."
    "$pip_cmd" install --break-system-packages -r requirements.txt
}

if command -v pip3 >/dev/null 2>&1; then
    pip_install pip3
elif command -v pip >/dev/null 2>&1; then
    pip_install pip
else
    python3 -m pip install -r requirements.txt 2>/dev/null \
        || python3 -m pip install --break-system-packages -r requirements.txt
fi

echo "==> 校验包内 IPA 字体(裁剪版)"
missing=0
for f in \
    assets/fonts/DejaVuSans.ttf \
    assets/fonts/DejaVuSans-Bold.ttf; do
    if [ -f "$f" ]; then
        echo "   OK  $f"
    else
        echo "   MISS $f"
        missing=1
    fi
done

if [ "$missing" -ne 0 ]; then
    echo "!! 缺少包内 IPA 字体。请确认 assets/fonts/ 下有 DejaVuSans.ttf 与 DejaVuSans-Bold.ttf。"
    exit 1
fi

echo "==> 检测系统字体(lite 版中/英文依赖系统字体)"
sys_missing=0

# 逐个路径检测,任一存在即视为该字体可用(避免多行 ls 一错全错)
any_exists() {
    local f
    for f in "$@"; do
        [ -f "$f" ] && return 0
    done
    return 1
}

# 中文: NotoSansCJK(.ttc/.ttf 任一)
if any_exists \
    /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc \
    /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttf \
    /usr/share/fonts/noto/NotoSansCJK-Regular.ttc \
    /usr/local/share/fonts/NotoSansCJK-Regular.ttc \
    "$HOME/.local/share/fonts/NotoSansCJK-Regular.ttc"; then
    echo "   OK  NotoSansCJK(中文)"
else
    echo "   MISS NotoSansCJK(中文系统字体)"
    sys_missing=1
fi

# 英文: DejaVuSans
if any_exists \
    /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf \
    /usr/share/fonts/dejavu/DejaVuSans.ttf \
    "$HOME/.local/share/fonts/DejaVuSans.ttf"; then
    echo "   OK  DejaVuSans(英文)"
else
    echo "   MISS DejaVuSans(英文系统字体)"
    sys_missing=1
fi

if [ "$sys_missing" -ne 0 ]; then
    echo ""
    echo "!! 缺少系统字体,请按你的发行版安装:"
    echo "   Ubuntu/Debian : sudo apt install fonts-noto-cjk fonts-dejavu"
    echo "   CentOS/RHEL   : sudo yum install google-noto-sans-cjk-fonts dejavu-sans-fonts"
    echo "   macOS         : 系统已自带;如需 Noto 可 brew install --cask font-noto-sans-cjk"
    echo "   (或改用内置完整字体的 vocab-cards-pro,开箱即用)"
    exit 1
fi

echo "==> 验证依赖可导入"
python3 -c "import PIL, fontTools, qrcode; print('   全部依赖就绪 ✓')"

echo ""
echo "完成。快速验证(自带示例):"
echo "  python3 scripts/vocab_cards.py examples/sample.json /tmp/vocab_demo"
