#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vocab_cards.py — 专业英语词汇闪卡生成器(主卡 / 副卡 / 百度百科二维码)
====================================================================
从 JSON 单词数据生成黑白打印优化的专业闪卡 PNG。

特性:
  - 段级字体选择:IPA 音标用 DejaVu,中文/CJK 用 NotoSansCJK,
    根治"豆腐块"(缺失字形)问题。
  - 主卡:单词 + UK/US 音标 + 词性 + 双语释义 + 固定搭配 + 例句 + 文化背景。
  - 副卡:相关信息 + 相关词汇 + 地道表达 + 文化背景 + 记忆提示。
  - 二维码:右下角 180px,指向百度百科,可开关。
  - 文件以英文单词命名(如 new_zealand.png / red_army.png)。

依赖: pip install --break-system-packages pillow fonttools qrcode[pil]
系统字体:NotoSansCJK(.ttc, face index 2) 与 DejaVuSans(.ttf)
"""
import json, os, re, sys
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont, TTCollection

# ---------------- 字体策略 ----------------
# 中英文/ASCII: 系统字体（NotoSansCJK + 系统DejaVu）
# IPA 音标: 包内裁剪字体（仅69个字符，约34KB）
_SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_BUNDLED_FONTS = os.path.join(_SKILL_DIR, "assets", "fonts")

# CJK: 仅系统字体
CAND_CJK_R = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttf",
    "/usr/share/fonts/noto/NotoSansCJK-Regular.ttc",
    "/usr/local/share/fonts/NotoSansCJK-Regular.ttc",
    "C:/Windows/Fonts/NotoSansCJK-Regular.ttc",
]
CAND_CJK_B = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttf",
    "/usr/share/fonts/noto/NotoSansCJK-Bold.ttc",
    "/usr/local/share/fonts/NotoSansCJK-Bold.ttc",
    "C:/Windows/Fonts/NotoSansCJK-Bold.ttc",
]
# Latin/ASCII: 仅系统字体（完整版DejaVu）
CAND_LATIN_R = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",
    "C:/Windows/Fonts/DejaVuSans.ttf",
]
CAND_LATIN_B = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/DejaVuSans-Bold.ttf",
]
# IPA: 包内裁剪字体优先，系统回退
CAND_IPA_R = [
    os.path.join(_BUNDLED_FONTS, "DejaVuSans.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
CAND_IPA_B = [
    os.path.join(_BUNDLED_FONTS, "DejaVuSans-Bold.ttf"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
]

def _find(paths):
    for p in paths:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"字体未找到,请安装以下其一: {paths}")

CJK_R = _find(CAND_CJK_R)
CJK_B = _find(CAND_CJK_B)
LATIN_R = _find(CAND_LATIN_R)
LATIN_B = _find(CAND_LATIN_B)
IPA_R = _find(CAND_IPA_R)
IPA_B = _find(CAND_IPA_B)
CJK_FACE = 2  # 简体中文 face index

# ---------------- 字体 cmap 加载 ----------------
def _load_cmap(path):
    if path.lower().endswith(".ttc"):
        return TTCollection(path)[CJK_FACE].getBestCmap()
    return TTFont(path).getBestCmap()

_cjk_cmap = _load_cmap(CJK_R)
_ipa_cmap = _load_cmap(IPA_R)  # 包内裁剪字体的 cmap

# ---------------- 字体缓存 ----------------
_font_cache = {}

def _get_font(key_prefix, path_r, path_b, size, bold):
    key = (key_prefix, size, bold)
    if key not in _font_cache:
        p = path_b if bold else path_r
        if p.lower().endswith('.ttc'):
            _font_cache[key] = ImageFont.truetype(p, size, index=CJK_FACE)
        else:
            _font_cache[key] = ImageFont.truetype(p, size)
    return _font_cache[key]

def _get_cjk(size, bold):
    return _get_font('cjk', CJK_R, CJK_B, size, bold)

def _get_latin(size, bold):
    return _get_font('latin', LATIN_R, LATIN_B, size, bold)

def _get_ipa(size, bold):
    return _get_font('ipa', IPA_R, IPA_B, size, bold)

def font_for(ch, size, bold=False):
    cp = ord(ch)
    # IPA 字符 → 包内裁剪字体
    if cp in _ipa_cmap:
        return _get_ipa(size, bold)
    # ASCII → 系统 DejaVu（完整英文）
    if cp < 128:
        return _get_latin(size, bold)
    # CJK → 系统 NotoSansCJK
    if cp in _cjk_cmap:
        return _get_cjk(size, bold)
    # 兜底 → 系统 CJK
    return _get_cjk(size, bold)

def _segment_text(text, size, bold):
    """将文本按字体分段，返回 [(font_obj, segment_string), ...]"""
    if not text:
        return []
    segments = []
    cur_font = font_for(text[0], size, bold)
    cur_chars = [text[0]]
    for ch in text[1:]:
        f = font_for(ch, size, bold)
        if f is cur_font:
            cur_chars.append(ch)
        else:
            segments.append((cur_font, ''.join(cur_chars)))
            cur_font = f
            cur_chars = [ch]
    if cur_chars:
        segments.append((cur_font, ''.join(cur_chars)))
    return segments

def text_w(d, text, size, bold=False):
    w = 0
    for font, seg in _segment_text(text, size, bold):
        w += d.textlength(seg, font=font)
    return w

def draw_t(d, x, y, text, size, fill, bold=False, indent=0):
    """分段渲染文本，通过 'x' 基线对齐不同字体段。"""
    cx = x + indent
    if not text:
        return cx
    segments = _segment_text(text, size, bold)
    if not segments:
        return cx
    # 以第一段的 'x' 基线为参考
    ref_baseline = segments[0][0].getbbox('x')[3]
    for font, seg in segments:
        seg_baseline = font.getbbox('x')[3]
        y_off = ref_baseline - seg_baseline
        d.text((cx, y + y_off), seg, font=font, fill=fill)
        cx += d.textlength(seg, font=font)
    return cx

def text_tokens(text):
    """Split text into logical break units for smart wrapping.

    Rules:
      - Consecutive ASCII letters/digits form ONE token (an English word) that
        is never broken mid-word.
      - Full-width parentheses/quotes/brackets pair with their content so they
        don't get separated from what they enclose.
      - A plain space is a soft break point.
      - CJK runs break between characters, but trailing punctuation (，。、；：？！”’）】』!?) stays
        glued to the preceding CJK char (so punctuation never starts a line).
    """
    import re
    tokens = []
    i, n = 0, len(text)
    while i < n:
        ch = text[i]
        # English word: ascii letters/digits joined by - or '
        if ch.isascii() and (ch.isalnum() or ch in "-'"):
            j = i
            while j < n and (text[j].isascii() and (text[j].isalnum() or text[j] in "-'.")):
                j += 1
            # don't include trailing dot if it's sentence end (it's ascii punctuation, keep in word is fine)
            tokens.append(text[i:j])
            i = j
            continue
        # space: soft break token
        if ch == ' ':
            tokens.append(' ')
            i += 1
            continue
        # opening bracket -> capture up to matching close
        pairs = {'(': ')', '[': ']', '『': '』', '「': '」', '“': '”', '【': '】'}
        if ch in pairs:
            j = i
            while j < n and text[j] != pairs[ch]:
                j += 1
            if j < n:
                j += 1
            tokens.append(text[i:j])
            i = j
            continue
        # CJK char + following punctuation glued
        if ord(ch) > 0x2E7F and not ch.isascii():
            j = i + 1
            while j < n and text[j] in "，。、；：？！”’）】』…—～·":
                j += 1
            tokens.append(text[i:j])
            i = j
            continue
        # anything else: single char
        tokens.append(ch)
        i += 1
    return tokens


def _join(parts):
    """Join tokens into a line, preserving original space tokens (a space token
    is kept as-is so inter-word gaps are exact)."""
    # parts already include ' ' tokens where spaces existed in the source
    out = []
    for t in parts:
        out.append(t)
    s = ''.join(out)
    # collapse multiple spaces and strip leading space
    import re
    s = re.sub(r' {2,}', ' ', s)
    return s.lstrip()


def wrap(d, text, size, maxw, bold=False):
    """Smart wrap: never break an English word; keep brackets/punctuation paired;
    use spaces as soft break points. Fallback to per-char if a token is overwide."""
    tokens = text_tokens(text)  # includes ' ' tokens
    lines = []
    cur = []
    cur_w = 0.0

    def flush():
        nonlocal cur, cur_w
        if cur:
            lines.append(_join(cur))
            cur = []
            cur_w = 0.0

    for tok in tokens:
        tw = text_w(d, tok, size, bold)
        # A token wider than maxw: flush and force it on its own line
        if tw > maxw:
            flush()
            lines.append(tok)
            continue
        if tok == ' ':
            # trailing space at line end: drop it (handled by lstrip on next flush),
            # but keep it if we have content to separate
            if cur:
                # tentative: add space, will be stripped if it ends up at line end
                cur.append(' ')
                cur_w += text_w(d, ' ', size, bold)
            continue
        sep = text_w(d, ' ', size, bold) if (cur and cur[-1] == ' ') else 0.0
        if cur and cur_w + tw > maxw:
            flush()
            sep = 0.0
        if not cur and tw > maxw:
            lines.append(tok)
        else:
            cur.append(tok)
            cur_w += tw

    flush()
    return [ln.rstrip() for ln in lines]



# ---------------- 配色(黑白打印优化) ----------------
BG = "#ffffff"; BK = "#000000"; GRAY = "#374151"; SUB = "#6b7280"; LGRAY = "#d1d5db"

def _hline(d, y, x1=60, x2=940, color=LGRAY, w=2):
    d.line([x1, y, x2, y], fill=color, width=w)

# ---------------- 主卡 ----------------
def gen_main(word, ipa_uk, ipa_us, pos, level, cn, en, coll, examples, note, outfile):
    W, H = 1000, 1700
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    y = 50; maxw = W - 130
    fw = 62 if len(word) <= 16 else 44
    draw_t(d, 60, y, word, fw, BK, bold=True); y += 86
    draw_t(d, 62, y, f"英 /{ipa_uk}/   美 /{ipa_us}/", 28, BK); y += 50
    pos_w = text_w(d, pos, 26, bold=True)
    d.rounded_rectangle([62, y, 62 + pos_w + 28, y + 48], radius=8, outline=BK, width=2)
    draw_t(d, 76, y + 8, pos, 26, BK, bold=True)
    draw_t(d, 62 + pos_w + 48, y + 10, level, 24, BK); y += 72
    _hline(d, y, color=BK); y += 22
    draw_t(d, 60, y, "中文释义:", 36, BK, bold=True); y += 54
    for ln in wrap(d, cn, 42, maxw, bold=True):
        draw_t(d, 60, y, ln, 42, BK, bold=True); y += 58
    draw_t(d, 60, y, "English Definition:", 30, BK, bold=True); y += 44
    for ln in wrap(d, en, 30, maxw):
        draw_t(d, 60, y, ln, 30, BK); y += 42
    y += 8; _hline(d, y); y += 22
    draw_t(d, 60, y, "▍固定搭配:", 36, BK, bold=True); y += 52
    for ph in coll:
        for ln in wrap(d, "- " + ph, 30, maxw):
            draw_t(d, 60, y, ln, 30, BK); y += 42
    y += 10; _hline(d, y); y += 22
    draw_t(d, 60, y, "▍丰富例句:", 36, BK, bold=True); y += 52
    for i, (e, cn2) in enumerate(examples, 1):
        for ln in wrap(d, f"{i}. {e}", 30, maxw):
            draw_t(d, 60, y, ln, 30, BK); y += 40
        for ln in wrap(d, f"    {cn2}", 28, maxw):
            draw_t(d, 60, y, ln, 28, BK); y += 36
    y += 6; _hline(d, y); y += 22
    draw_t(d, 60, y, "▍文化背景:", 34, BK, bold=True); y += 50
    for ln in wrap(d, note, 28, maxw):
        draw_t(d, 60, y, ln, 28, BK); y += 38
    img.save(outfile, "PNG")

# ---------------- 副卡 ----------------
def gen_side(word, category, info, related, expressions, culture, tip, outfile):
    W, H = 1000, 1700
    img = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(img)
    y = 50; maxw = W - 130
    fw = 52 if len(word) <= 16 else 36
    draw_t(d, 60, y, word, fw, BK, bold=True); y += 74
    if category:
        cw = text_w(d, category, 24, bold=True)
        d.rounded_rectangle([62, y, 62 + cw + 28, y + 42], radius=8, outline=BK, width=2)
        draw_t(d, 76, y + 7, category, 24, BK, bold=True); y += 60
    y += 6; _hline(d, y, color=BK); y += 24
    draw_t(d, 60, y, "相关信息:", 34, BK, bold=True); y += 46
    for ln in wrap(d, info, 30, maxw):
        draw_t(d, 60, y, ln, 30, BK); y += 40
    y += 8; _hline(d, y); y += 22
    draw_t(d, 60, y, "▍相关词汇 Related Words:", 32, BK, bold=True); y += 46
    rel_list = [related] if isinstance(related, str) else related
    for item in rel_list:
        for ln in wrap(d, item, 28, maxw):
            draw_t(d, 60, y, ln, 28, BK); y += 36
    y += 6; _hline(d, y); y += 22
    draw_t(d, 60, y, "▍地道表达 Expressions:", 32, BK, bold=True); y += 46
    exp_list = [expressions] if isinstance(expressions, str) else expressions
    for item in exp_list:
        for ln in wrap(d, item, 28, maxw):
            draw_t(d, 60, y, ln, 28, BK); y += 36
    y += 6; _hline(d, y); y += 22
    draw_t(d, 60, y, "▍文化背景 Culture:", 32, BK, bold=True); y += 46
    for ln in wrap(d, culture, 28, maxw):
        draw_t(d, 60, y, ln, 28, BK); y += 38
    y += 6; _hline(d, y); y += 22
    draw_t(d, 60, y, "▍记忆提示 Memory Tip:", 32, BK, bold=True); y += 46
    for ln in wrap(d, tip, 28, maxw):
        draw_t(d, 60, y, ln, 28, BK); y += 36
    img.save(outfile, "PNG")

# ---------------- 二维码 ----------------
def add_qr(card_path, baike_url, outfile, qr_size=180, margin=50,
           caption="Baidu Baike", caption_size=22):
    import qrcode
    img = Image.open(card_path).convert("RGB")
    W, H = img.size; d = ImageDraw.Draw(img)
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=8, border=2)
    qr.add_data(baike_url); qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_img = qr_img.resize((qr_size, qr_size), Image.NEAREST)
    qr_x = W - margin - qr_size; qr_y = H - margin - qr_size
    img.paste(qr_img, (qr_x, qr_y))
    f = font_for("A", caption_size)
    cb = d.textbbox((0, 0), caption, font=f)
    cw = cb[2] - cb[0]
    d.text((qr_x + (qr_size - cw) // 2, qr_y + qr_size + 8), caption, font=f, fill="#6b7280")
    img.save(outfile, "PNG")

# ---------------- 工具 ----------------
def slugify(word):
    s = word.lower().replace("the ", "").strip()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")

def main():
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    data = json.load(open(sys.argv[1], encoding="utf-8"))
    outdir = sys.argv[2] if len(sys.argv) > 2 else "."
    os.makedirs(outdir, exist_ok=True)
    for item in data:
        name = slugify(item["word"])
        try:
            # 主卡
            main_p = os.path.join(outdir, f"{name}.png")
            gen_main(item["word"], item["ipa_uk"], item["ipa_us"], item["pos"],
                     item["level"], item["cn"], item["en"], item["coll"],
                     item["examples"], item["note"], main_p)
            # 二维码卡(若提供 baike_url)
            if item.get("baike_url"):
                qr_p = os.path.join(outdir, f"{name}_qr.png")
                add_qr(main_p, item["baike_url"], qr_p)
            # 副卡
            if item.get("side"):
                s = item["side"]
                side_p = os.path.join(outdir, f"{name}_side.png")
                gen_side(item["word"], s.get("category", ""), s["info"], s["related"],
                         s["expressions"], s["culture"], s["tip"], side_p)
            print(f"OK: {name}", flush=True)
        except Exception as e:
            print(f"FAIL: {name} -> {e}", flush=True)

if __name__ == "__main__":
    main()
