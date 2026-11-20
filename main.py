#!/usr/bin/env python3
"""Draw a newspaper front page summing up Thursday 19 November 2026.

Standard library only. Writes a deterministic PNG to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
Anchor: makefun anchor b51cb18168ebdf602cc005a43020b4eaf8c161b5 round 34127258
"""
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (247, 242, 230)
INK = (18, 18, 18)
RED = (178, 28, 28)
DARKRED = (130, 20, 20)
GREY = (92, 88, 80)
LIGHT = (232, 224, 204)
BLUE = (30, 64, 140)
GREEN = (28, 110, 60)
GOLD = (196, 148, 28)
WHITE = (255, 255, 255)
SKY = (168, 200, 226)

# ---------------------------------------------------------------- canvas
buf = bytearray(PAPER * (W * H))


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i:i + 3] = bytes(c)


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def frame(x, y, w, h, c, t=2):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


def hline(x, y, w, c, t=2):
    rect(x, y, w, t, c)


def vline(x, y, h, c, t=2):
    rect(x, y, t, h, c)


def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                px(xx, yy, c)


def triangle(x1, y1, x2, y2, x3, y3, c):
    minx, maxx = min(x1, x2, x3), max(x1, x2, x3)
    miny, maxy = min(y1, y2, y3), max(y1, y2, y3)
    d = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
    if d == 0:
        return
    for yy in range(miny, maxy + 1):
        for xx in range(minx, maxx + 1):
            a = ((y2 - y3) * (xx - x3) + (x3 - x2) * (yy - y3)) / d
            b = ((y3 - y1) * (xx - x3) + (x1 - x3) * (yy - y3)) / d
            g = 1 - a - b
            if a >= 0 and b >= 0 and g >= 0:
                px(xx, yy, c)


def line(x1, y1, x2, y2, c, t=2):
    steps = max(abs(x2 - x1), abs(y2 - y1), 1)
    for i in range(steps + 1):
        x = x1 + (x2 - x1) * i // steps
        y = y1 + (y2 - y1) * i // steps
        rect(x, y, t, t, c)


# ------------------------------------------------------------------ font
# 5x7 glyphs, '#' = ink.
GLYPHS = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".#.##"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    '0': (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    '$': ("..#..", ".####", "#.#..", ".###.", "..##.", "####.", "..#.."),
    '%': ("##..#", "##.#.", "...#.", "..#..", ".#...", ".#.##", "#..##"),
    '+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '(': ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ')': ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
    '&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    '*': (".....", "#.#.#", ".###.", "#####", ".###.", "#.#.#", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
    ';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    '<': ("....#", "...#.", "..#..", ".#...", "..#..", "...#.", "....#"),
    '>': ("#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."),
}


def text_w(s, scale):
    return len(s) * 6 * scale - scale if s else 0


def draw_text(x, y, s, scale, c=INK):
    s = s.upper()
    cx = x
    for ch in s:
        g = GLYPHS.get(ch, GLYPHS[' '])
        for r, row in enumerate(g):
            for col, bit in enumerate(row):
                if bit == '#':
                    rect(cx + col * scale, y + r * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def centered(y, s, scale, c=INK, cx0=0, cx1=W):
    x = cx0 + (cx1 - cx0 - text_w(s, scale)) // 2
    draw_text(x, y, s, scale, c)


def wrap(s, max_chars):
    words, lines, cur = s.upper().split(), [], ""
    for w in words:
        if len(cur) + (1 if cur else 0) + len(w) <= max_chars:
            cur = (cur + " " + w) if cur else w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def body(x, y, s, max_chars, scale=2, c=INK, leading=19):
    for ln in wrap(s, max_chars):
        draw_text(x, y, ln, scale, c)
        y += leading
    return y


def headline(x, y, lines, scale, c=INK, leading=None):
    leading = leading or (7 * scale + 7)
    for ln in lines:
        draw_text(x, y, ln, scale, c)
        y += leading
    return y


# -------------------------------------------------------------- visuals
def courthouse(x, y):
    # pediment, columns, base, scales on top
    triangle(x + 10, y + 28, x + 90, y, x + 170, y + 28, INK)
    rect(x + 82, y - 16, 4, 16, RED)
    circle(x + 84, y - 20, 6, RED)
    for i in range(4):
        cx = x + 22 + i * 38
        rect(cx, y + 36, 14, 62, INK)
        rect(cx - 3, y + 32, 20, 5, INK)
        rect(cx - 3, y + 96, 20, 5, INK)
    rect(x + 8, y + 104, 164, 7, INK)
    rect(x + 2, y + 114, 176, 6, RED)


def flags(x, y):
    # three simple national flags side by side on poles
    for i, fx in enumerate((x, x + 62, x + 124)):
        vline(fx, y, 74, INK, 3)
    # USA: stripes + blue canton
    for i in range(6):
        rect(x + 3, y + i * 7, 52, 4, RED if i % 2 == 0 else WHITE)
    rect(x + 3, y, 24, 21, BLUE)
    # China: red + gold dots
    rect(x + 65, y, 52, 42, RED)
    circle(x + 76, y + 11, 5, GOLD)
    circle(x + 90, y + 7, 3, GOLD)
    circle(x + 92, y + 15, 3, GOLD)
    circle(x + 90, y + 23, 3, GOLD)
    # Russia: white / blue / red bands
    rect(x + 127, y, 52, 14, WHITE)
    rect(x + 127, y + 14, 52, 14, BLUE)
    rect(x + 127, y + 28, 52, 14, RED)
    frame(x + 3, y, 52, 42, INK, 1)
    frame(x + 65, y, 52, 42, INK, 1)
    frame(x + 127, y, 52, 42, INK, 1)


def sun_icon(x, y):
    circle(x + 22, y + 22, 13, GOLD)
    for dx, dy in ((0, -20), (0, 20), (-20, 0), (20, 0), (-15, -15),
                   (15, -15), (-15, 15), (15, 15)):
        line(x + 22 + dx // 2, y + 22 + dy // 2,
             x + 22 + dx, y + 22 + dy, GOLD, 3)


def tanker_icon(x, y):
    rect(x + 4, y + 26, 86, 12, RED)
    triangle(x + 90, y + 26, x + 90, y + 38, x + 102, y + 38, RED)
    rect(x + 22, y + 16, 34, 10, INK)
    rect(x + 62, y + 10, 10, 16, INK)
    rect(x + 8, y + 42, 96, 3, BLUE)
    rect(x + 20, y + 47, 60, 3, BLUE)


def controller_icon(x, y):
    rect(x + 6, y + 12, 78, 34, INK)
    circle(x + 6, y + 29, 17, INK)
    circle(x + 84, y + 29, 17, INK)
    rect(x + 22, y + 24, 16, 5, WHITE)
    rect(x + 27, y + 19, 5, 16, WHITE)
    circle(x + 66, y + 22, 4, RED)
    circle(x + 76, y + 31, 4, GOLD)
    circle(x + 56, y + 31, 4, GREEN)


def chart_icon(x, y):
    vline(x + 6, y + 4, 44, INK, 3)
    hline(x + 6, y + 46, 84, INK, 3)
    line(x + 10, y + 40, x + 32, y + 28, GREEN, 3)
    line(x + 32, y + 28, x + 52, y + 33, GREEN, 3)
    line(x + 52, y + 33, x + 80, y + 10, GREEN, 3)
    triangle(x + 80, y + 10, x + 68, y + 12, x + 79, y + 22, GREEN)


def flame_icon(x, y):
    triangle(x + 22, y, x + 4, y + 34, x + 40, y + 34, RED)
    triangle(x + 22, y + 14, x + 12, y + 36, x + 32, y + 36, GOLD)
    rect(x + 4, y + 38, 36, 5, INK)


# ---------------------------------------------------------------- page
def main():
    M = 28  # margin
    # masthead
    hline(M, 18, W - 2 * M, INK, 4)
    centered(30, "THE WORLD IN ONE DAY", 7, INK)
    hline(M, 88, W - 2 * M, RED, 5)
    # date bar
    rect(M, 102, W - 2 * M, 54, INK)
    centered(116, "THURSDAY 19 NOVEMBER 2026", 5, WHITE)
    centered(166, "THE DAY'S WORLD NEWS ON ONE PAGE - HAGUE * SHENZHEN * ANTALYA * KYIV", 2, GREY)

    # ---- lead row ------------------------------------------------------
    ly = 196
    # left: ICJ lead
    draw_text(M, ly, "THE HAGUE - WORLD COURT", 2, RED)
    headline(M, ly + 22, ["MYANMAR COMMITTED", "GENOCIDE AGAINST", "ROHINGYA: ICJ RULES"], 4)
    courthouse(M + 6, ly + 122)
    body(M + 196, ly + 124,
         "THE INTERNATIONAL COURT OF JUSTICE RULED 9-6 THAT MYANMAR "
         "COMMITTED GENOCIDE AGAINST THE ROHINGYA. JUDGES ORDERED "
         "RESTITUTION AND INVESTIGATIONS.", 34, 2)
    vline(636, ly, 218, GREY, 2)
    # right: Shenzhen summit
    rx = 656
    draw_text(rx, ly, "SHENZHEN - HISTORIC SUMMIT", 2, RED)
    headline(rx, ly + 22, ["TRUMP, XI + PUTIN", "HOLD FIRST EVER", "TRILATERAL SUMMIT"], 3)
    flags(rx + 8, ly + 112)
    body(rx, ly + 174,
         "NUCLEAR WAR CAN NEVER BE WON, LEADERS AGREE. NO MAJOR "
         "PEACE DEAL ON UKRAINE.", 28, 2)
    hline(M, ly + 238, W - 2 * M, INK, 3)

    # ---- middle row: three boxes ---------------------------------------
    my = 444
    boxes = [
        ("COP31 ANTALYA", "CLIMATE TALKS STALL: FOSSIL FUELS CUT FROM DRAFT",
         "MINISTERS FAILED TO UNBLOCK TALKS IN TURKEY.", sun_icon),
        ("HORMUZ CRISIS", "3 TANKERS BURN AFTER STRIKING MINES IN STRAIT",
         "US + IRAN TRADED STRIKES. IEA WARNS ON ENERGY SECURITY.",
         tanker_icon),
        ("GTA VI IS HERE", "GAME LAUNCHES TO RAVE REVIEWS AFTER 13 YEARS",
         "MILLIONS PLAYED ON DAY ONE, 13 YEARS AFTER GTA V.",
         controller_icon),
    ]
    bw = (W - 2 * M - 24) // 3
    for i, (kick, head, txt, icon) in enumerate(boxes):
        bx = M + i * (bw + 12)
        frame(bx, my, bw, 190, INK, 2)
        draw_text(bx + 12, my + 10, kick, 2, RED)
        yy = body(bx + 12, my + 32, head, 19, 2, INK, 19)
        icon(bx + 12, yy + 4)
        body(bx + 116, yy + 4, txt, 16, 2, INK, 19)
    hline(M, my + 202, W - 2 * M, INK, 3)

    # ---- lower row: four columns ---------------------------------------
    ky = 658
    cols = [
        ("BANGLADESH", ["TURMOIL AS TROOPS", "DEPLOY ON STREETS"],
         "PARAMILITARY OUT AS UNREST OVER HASINA RETURN GROWS. "
         "YUNUS HOME TORCHED. RIOTS IN 28 DISTRICTS."),
        ("UKRAINE WAR", ["CRIMEA BRIDGE HIT", "BY MISSILE STRIKE"],
         "MISSILE CRIPPLED THE CRIMEA BRIDGE. DUTCH EMBASSY HIT "
         "IN KYIV. EU PLANS 45BN LOAN."),
        ("WASHINGTON", ["JEFFRIES SET TO BE", "FIRST BLACK SPEAKER"],
         "PELTOLA WIN IN ALASKA SEALS 56-44 SENATE MAJORITY. "
         "IRAN WAR-POWERS VOTE FAILS 51-48."),
        ("ART RECORD", ["VAN GOGH SELLS FOR", "RECORD $190.4M"],
         "NEW RECORD FOR THE ARTIST. ANTHROPIC IPO RAISED "
         "$81.3BN AT $83 A SHARE."),
    ]
    cw = (W - 2 * M - 36) // 4
    for i, (kick, head, txt) in enumerate(cols):
        cx = M + i * (cw + 12)
        if i:
            vline(cx - 7, ky, 158, GREY, 2)
        draw_text(cx, ky, kick, 2, RED)
        yy = headline(cx, ky + 22, head, 2, INK, 19)
        body(cx, yy + 4, txt, 19, 2, INK, 19)

    # ---- markets strip ---------------------------------------------------
    ty = 830
    rect(M, ty, W - 2 * M, 54, INK)
    draw_text(M + 12, ty + 7, "MARKETS", 2, GOLD)
    draw_text(M + 118, ty + 7,
              "S&P 500 7,323.63 -0.23%   NASDAQ +0.42%   FTSE 100 -1.30%",
              2, WHITE)
    draw_text(M + 12, ty + 31,
              "BRENT OIL $89.59   COPPER -5% ON AI WORRIES   "
              "WALMART SALES $188.8BN +5.2%", 2, WHITE)

    # ---- in brief --------------------------------------------------------
    by = 896
    hline(M, by, W - 2 * M, RED, 4)
    draw_text(M, by + 10, "IN BRIEF", 3, RED)
    briefs_l = [
        "* VOYAGER 1 NOW ONE LIGHT-DAY FROM EARTH",
        "* WORD OF THE YEAR 2026: 'HUMAN'",
        "* US + VENEZUELA RESTORE MILITARY TIES",
    ]
    briefs_r = [
        "* HAITI: 34 KILLED IN POLICE GANG RAID",
        "* POTATOES GROWN IN MOON SOIL",
        "* ISLAM TO BE TOP FAITH BY 2035",
    ]
    yy = by + 48
    for b in briefs_l:
        draw_text(M, yy, b, 2, INK)
        yy += 20
    yy = by + 48
    for b in briefs_r:
        draw_text(M + 500, yy, b, 2, INK)
        yy += 20
    hline(M, 1010, W - 2 * M, INK, 3)

    # ---- write PNG -------------------------------------------------------
    raw = b"".join(b"\x00" + bytes(buf[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(png)


if __name__ == "__main__":
    main()
