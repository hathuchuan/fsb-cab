#!/usr/bin/env python3
"""Dựng index.html từ _template.html và các slide deck trong modules/.

Quy ước đặt tên: file (hoặc thư mục) trong modules/ bắt đầu bằng mã buổi,
ví dụ `B5_prompting-chuyen-sau.html` hoặc `B6_.../index.html`.
- Có deck khớp mã buổi  -> thẻ "Đã mở", nút "Mở bài giảng".
- Chưa có deck          -> thẻ "Sắp mở" (mờ, không bấm được).
- Deck không khớp mã nào -> thêm thẻ riêng, lấy tên từ <title>.
Mô tả thẻ lấy từ <meta name="description"> của deck nếu có, không thì dùng mô tả mặc định bên dưới.

Chạy: python3 build_index.py   (GitHub Actions tự chạy mỗi lần push)
"""
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODULES = ROOT / "modules"

# Danh sách buổi theo syllabus CD3 (B11–B13)
SESSIONS = [
    ("B11", "Tư duy tự động hóa, chuẩn hóa SOP & câu lệnh mẫu biến số",
     "Ma trận chọn việc nên tự động hóa, SOP cho AI (Đầu vào, Logic, Ranh giới, Đầu ra), 5 bước tự động hóa và câu lệnh mẫu có biến số."),
    ("B12", "Quy trình tự chạy theo lịch trên Claude Desktop & hướng dẫn vận hành",
     "Luồng Kích hoạt, Xử lý, Lưu kết quả, Thông báo; 3 case study mẫu; kiểm thử dữ liệu thiếu/lỗi và hướng dẫn vận hành 1–2 trang."),
    ("B13", "Kiểm thử chéo & hoàn thiện quy trình tự chạy",
     "Học viên kiểm thử chéo quy trình của nhau, hoàn thiện và chốt quy trình tự chạy để nộp cuối khóa."),
]

ARROW = '<svg class="icon" style="width:14px;height:14px"><use href="#i-arrow"/></svg>'


def find_decks():
    """Trả về list (tên hiển thị trong modules/, đường dẫn file html)."""
    decks = []
    if not MODULES.is_dir():
        return decks
    for p in sorted(MODULES.iterdir()):
        if p.name.startswith((".", "_")) or p.name == "index.html":
            continue
        if p.is_file() and p.suffix.lower() in (".html", ".htm"):
            decks.append((p.name, p))
        elif p.is_dir() and (p / "index.html").is_file():
            decks.append((p.name + "/", p / "index.html"))
    return decks


def read_meta(path):
    text = path.read_text(encoding="utf-8", errors="ignore")[:20000]
    t = re.search(r"<title>(.*?)</title>", text, re.S | re.I)
    d = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', text, re.S | re.I)
    title = html.unescape(t.group(1).strip()) if t else path.stem
    title = re.split(r"\s+\|\s+", title)[0]  # bỏ phần "| Tên khóa — FSB"
    return title, (html.unescape(d.group(1).strip()) if d else None)


def code_of(name):
    m = re.match(r"(B\d+)(?!\d)", name, re.I)
    return m.group(1).upper() if m else None


def card(code, title, desc, href=None):
    e = html.escape
    if href:
        status = '<span class="status ready">Đã mở</span>'
        btn = f'<a class="csv-btn" href="./modules/{e(href)}" target="_blank" rel="noopener noreferrer">Mở bài giảng {ARROW}</a>'
        cls = "mod-card"
    else:
        status = '<span class="status">Sắp mở</span>'
        btn = '<span class="csv-btn disabled">Chưa mở</span>'
        cls = "mod-card locked"
    return f"""      <article class="{cls}">
        <div>
          <div class="mod-top"><span class="mod-num">{e(code)}</span>{status}</div>
          <h2>{e(title)}</h2>
          <p>{e(desc)}</p>
        </div>
        {btn}
      </article>"""


def main():
    by_code, extras = {}, []
    for href, path in find_decks():
        c = code_of(href)
        if c and c not in by_code and any(c == s[0] for s in SESSIONS):
            by_code[c] = (href, path)
        else:
            extras.append((href, path))

    cards, bar = [], []
    for code, title, desc in SESSIONS:
        num = code[1:]
        if code in by_code:
            href, path = by_code[code]
            meta_desc = read_meta(path)[1]
            cards.append(card(code, f"Buổi {num}: {title}", meta_desc or desc, href))
            bar.append('      <div style="flex:1; background:var(--orange);"></div>')
        else:
            cards.append(card(code, f"Buổi {num}: {title}", desc))
            bar.append('      <div style="flex:1; background:var(--line);"></div>')
    for href, path in extras:
        title, meta_desc = read_meta(path)
        cards.append(card(code_of(href) or "+", title, meta_desc or "Học liệu bổ sung.", href))

    out = (ROOT / "_template.html").read_text(encoding="utf-8")
    out = out.replace("{{CARDS}}", "\n".join(cards))
    out = out.replace("{{BAR}}", "\n".join(bar))
    out = out.replace("{{READY}}", str(len(by_code)))
    (ROOT / "index.html").write_text(out, encoding="utf-8")

    # Nút "trang chủ" trong deck trỏ tới index.html cùng thư mục -> chuyển về trang chính
    MODULES.mkdir(exist_ok=True)
    (MODULES / "index.html").write_text(
        '<!DOCTYPE html><meta charset="utf-8"><meta http-equiv="refresh" content="0; url=../index.html">'
        '<link rel="canonical" href="../index.html"><title>Claude Automation Builder</title>',
        encoding="utf-8")

    print(f"index.html: {len(by_code)}/{len(SESSIONS)} buổi đã mở, {len(extras)} học liệu bổ sung")


if __name__ == "__main__":
    main()
