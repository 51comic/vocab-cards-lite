#!/usr/bin/env bash
# setup.sh — 一键安装 vocab-cards-lite 的 Python 依赖并校验包内字体。
set -euo pipefail
cd "$(dirname "$0")/.."
echo "==> 安装 Python 依赖"
if command -v pip3 >/dev/null 2>&1; then pip3 install --break-system-packages -r requirements.txt
elif command -v pip >/dev/null 2>&1; then pip install --break-system-packages -r requirements.txt
else python3 -m pip install --break-system-packages -r requirements.txt; fi
echo "==> 校验包内字体"
for f in assets/fonts/NotoSansCJK-Lite-Regular.ttf assets/fonts/NotoSansCJK-Lite-Bold.ttf assets/fonts/DejaVuSans.ttf assets/fonts/DejaVuSans-Bold.ttf; do
  [ -f "$f" ] && echo "   OK  $f" || { echo "   MISS $f"; exit 1; }
done
python3 -c "import PIL, fontTools, qrcode; print('    依赖就绪 ✓')"
echo "完成: python3 scripts/vocab_cards.py <input.json> [output_dir]"
