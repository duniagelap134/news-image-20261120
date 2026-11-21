#!/usr/bin/env python3
"""World news in one image — Friday 20 November 2026.

A make.fun program/v1 entry (competition news-image-20261120). It draws a
newspaper-style infographic of the day's world news and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output). Python 3.13, standard
library only; no network. The output bytes are deterministic: same input,
same bytes, every run.

Stories are the day's most consequential events as reported on 20 November
2026: the Russian strikes on Kyiv and the Polish airspace incursion, the
US-China-Russia joint declaration from the Shenzhen summit, the ICJ ruling
that Myanmar committed genocide against the Rohingya, Anthropic's record
$81bn IPO sliding on day two as markets fell, plus the Houthi strike on
Riyadh's PIF Tower, the COP31 talks overrunning their deadline, the capture
of a most-wanted cartel boss in Mexico and the US Senate's energy bill.
"""

import os
import struct
import zlib

# ---------------------------------------------------------------------------
# 5x7 pixel font, uppercase + digits + punctuation. Each glyph is 7 rows of
# 5 characters ('#' = ink, '.' = blank), top row first.
# ---------------------------------------------------------------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", "..##.", "..##.", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
    "&": (".#...", "#.#..", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "\u2022": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
}

W, H = 1024, 1024
PAPER = (250, 246, 238)
INK = (22, 35, 58)
RED = (180, 35, 24)
GREY = (90, 96, 110)
CARD = (255, 255, 255)
BORDER = (200, 192, 172)

buf = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i], buf[i + 1], buf[i + 2] = c


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def hline(x, y, w, c, t=1):
    rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    rect(x, y, t, h, c)


def circle(cx, cy, r, c, fill=False):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d2 = (xx - cx) ** 2 + (yy - cy) ** 2
            if fill:
                if d2 <= r * r:
                    px(xx, yy, c)
            else:
                if r * r - 2 * r <= d2 <= r * r:
                    px(xx, yy, c)


def line(x0, y0, x1, y1, c, t=2):
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    for i in range(steps + 1):
        x = x0 + dx * i // steps
        y = y0 + dy * i // steps
        rect(x - t // 2, y - t // 2, t, t, c)


def text_width(s, scale):
    return len(s) * (5 * scale + scale) - scale


def draw_text(s, x, y, scale, color):
    """Draw uppercase text; returns the x just past the last glyph."""
    cx = x
    for ch in s.upper():
        g = FONT.get(ch, FONT[" "])
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == "#":
                    rect(cx + col * scale, y + r * scale, scale, scale, color)
        cx += 5 * scale + scale
    return cx - scale


def draw_text_centered(s, cx, y, scale, color):
    draw_text(s, cx - text_width(s, scale) // 2, y, scale, color)


def wrap_text(s, scale, max_w):
    """Greedy wrap; returns a list of lines."""
    words = s.upper().split(" ")
    lines, cur = [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if text_width(t, scale) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------------------
# Minimal PNG writer (stdlib only): IHDR + IDAT (zlib) + IEND, CRC32 each.
# ---------------------------------------------------------------------------
def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    raw = b"".join(b"\x00" + bytes(buf[y * W * 3:(y + 1) * W * 3]) for y in range(H))
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(raw, 9))
        + _chunk(b"IEND", b"")
    )
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


# ---------------------------------------------------------------------------
# Pictogram icons, drawn with primitives inside a square centred at (cx, cy).
# ---------------------------------------------------------------------------
def icon_burst(cx, cy, s, c):
    # explosion / strike: radiating spikes around a core
    dirs = [(1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1), (0, -1), (1, -1),
            (2, 1), (1, 2), (-1, 2), (-2, 1), (-2, -1), (-1, -2), (1, -2), (2, -1)]
    for dx, dy in dirs:
        line(cx, cy, cx + dx * s // 4, cy + dy * s // 4, c, 3)
    circle(cx, cy, s // 6, c, fill=True)


def icon_circles(cx, cy, s, c):
    # three powers: three overlapping rings
    r = s // 4
    circle(cx - r, cy - r // 3, r, c)
    circle(cx + r, cy - r // 3, r, c)
    circle(cx, cy + r, r, c)


def icon_scales(cx, cy, s, c):
    # scales of justice
    vline(cx, cy - s // 2, s, c, 3)
    hline(cx - s // 2, cy - s // 2, s, c, 3)
    hline(cx - s // 3, cy - s // 2 + s // 6, s * 2 // 3, c, 2)
    # pans: two small triangles
    for sx in (cx - s // 2, cx + s // 2):
        line(sx, cy - s // 2, sx - s // 8, cy - s // 6, c, 2)
        line(sx, cy - s // 2, sx + s // 8, cy - s // 6, c, 2)
        hline(sx - s // 8, cy - s // 6, s // 4, c, 3)


def icon_chart(cx, cy, s, c):
    # rising bars + arrow
    bw = s // 6
    for i, h in enumerate((s // 4, s // 2, s * 3 // 4)):
        x = cx - s // 2 + i * (bw + s // 12)
        rect(x, cy + s // 2 - h, bw, h, c)
    line(cx - s // 2, cy + s // 4, cx + s // 2, cy - s // 2, c, 3)
    line(cx + s // 2, cy - s // 2, cx + s // 2 - s // 6, cy - s // 2, c, 3)
    line(cx + s // 2, cy - s // 2, cx + s // 2, cy - s // 2 + s // 6, c, 3)


# ---------------------------------------------------------------------------
# Layout: newspaper front page, 1024 x 1024.
# ---------------------------------------------------------------------------
def draw_page():
    rect(0, 0, W, H, PAPER)
    # double frame
    rect(10, 10, W - 20, H - 20, INK)
    rect(14, 14, W - 28, H - 28, PAPER)
    rect(20, 20, W - 40, H - 40, INK)
    rect(22, 22, W - 44, H - 44, PAPER)

    # masthead
    draw_text_centered("THE WORLD IN ONE IMAGE", W // 2, 40, 3, GREY)
    draw_text_centered("THE WORLD IN ONE DAY", W // 2, 66, 7, INK)
    draw_text_centered("FRIDAY, 20 NOVEMBER 2026", W // 2, 128, 5, RED)
    hline(48, 176, W - 96, RED, 4)
    draw_text_centered("FOUR STORIES THAT DEFINED THE DAY", W // 2, 190, 3, INK)

    stories = [
        {
            "tag": "UKRAINE  \u2022  EUROPE",
            "color": (180, 35, 24),
            "icon": icon_burst,
            "headline": "KYIV BRIDGES STRUCK",
            "body": "RUSSIAN STRIKES KILL AT LEAST 8; DRONE, MISSILES ENTER POLAND.",
        },
        {
            "tag": "SHENZHEN  \u2022  DIPLOMACY",
            "color": (29, 78, 216),
            "icon": icon_circles,
            "headline": "SHENZHEN DECLARATION",
            "body": "TRUMP, XI AND PUTIN PLEDGE NUCLEAR-RISK TALKS AFTER SUMMIT.",
        },
        {
            "tag": "THE HAGUE  \u2022  JUSTICE",
            "color": (15, 118, 110),
            "icon": icon_scales,
            "headline": "MYANMAR: GENOCIDE",
            "body": "ICJ RULES 9-6: MYANMAR COMMITTED GENOCIDE AGAINST ROHINGYA.",
        },
        {
            "tag": "MARKETS  \u2022  TECH",
            "color": (180, 83, 9),
            "icon": icon_chart,
            "headline": "ANTHROPIC'S $81BN IPO",
            "body": "RECORD $81BN IPO SLIDES DAY TWO; MARKETS FALL INTO CORRECTION.",
        },
    ]

    y = 216
    band_h, gap = 152, 10
    for st in stories:
        c = st["color"]
        rect(48, y, W - 96, band_h, CARD)
        # thin ink outline
        hline(48, y, W - 96, INK, 2)
        hline(48, y + band_h - 2, W - 96, INK, 2)
        vline(48, y, band_h, INK, 2)
        vline(W - 48 - 2, y, band_h, INK, 2)
        rect(50, y + 2, 8, band_h - 4, c)
        # icon in a tinted square
        ix, iy, isz = 72, y + 32, 88
        rect(ix, iy, isz, isz, c)
        st["icon"](ix + isz // 2, iy + isz // 2, 56, CARD)
        tx = 188
        draw_text(st["tag"], tx, y + 14, 3, c)
        draw_text(st["headline"], tx, y + 42, 5, INK)
        lines = wrap_text(st["body"], 4, W - 48 - tx - 24)
        ly = y + 88
        for ln in lines[:2]:
            draw_text(ln, tx, ly, 4, INK)
            ly += 30
        y += band_h + gap

    # also-in-the-news strip
    ay = y + 2
    draw_text("ALSO IN THE NEWS", 48, ay, 3, RED)
    also = [
        "HOUTHI MISSILE DAMAGES RIYADH'S PIF TOWER",
        "COP31 CLIMATE TALKS OVERRUN DEADLINE IN TURKEY",
        "MEXICO CAPTURES FBI MOST-WANTED CARTEL BOSS",
        "US SENATE PASSES ENERGY BILL, 62-33",
    ]
    ly = ay + 26
    for a in also:
        draw_text("\u2022  " + a, 48, ly, 3, INK)
        ly += 22

    draw_text_centered("REPORTED 20 NOV 2026  \u2022  SOURCES: MULTIPLE NEWS OUTLETS",
                        W // 2, 986, 2, GREY)


def main():
    draw_page()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    n = write_png(os.path.join(out_dir, "entry.png"))
    print(f"wrote entry.png ({n} bytes)")


if __name__ == "__main__":
    main()
