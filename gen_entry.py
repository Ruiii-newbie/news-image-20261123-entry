#!/usr/bin/env python3
"""Draw the 23 November 2026 world-news front page as a 1024x1024 PNG.

Pure standard library: a hand-built RGB pixel buffer is encoded to PNG
with zlib, so the program is deterministic and needs no network.
The six stories are the verified 23 Nov 2026 headlines from the morning
news scan: COP31 collapses in Antalya with no fossil-fuel deal, Iran
strikes a Bahrain site and tankers in the Strait of Hormuz, the Ukraine
war spills over (Kyiv drone strike, a Russian ship ablaze off Finland,
missiles landing in Poland), Mexico captures FBI most-wanted cartel boss
'El Chapo Isidro', a factory fire in Indonesia leaves 50 missing, and
India posts a record 720/9 in the Wellington Test.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024
PAPER = (246, 241, 229)
CARD = (255, 255, 255)
INK = (24, 30, 44)
NAVY = (22, 38, 66)
CRIMSON = (166, 30, 30)
TEAL = (15, 118, 110)
GOLD = (185, 138, 31)
GREY = (96, 102, 116)
RULE = (208, 200, 184)
SEA = (38, 110, 138)
SKY = (214, 232, 240)
FLAME = (232, 120, 30)
SMOKE = (120, 124, 130)
PITCH = (96, 140, 82)

# 5x7 pixel font. Each glyph is 7 rows of 5 cells, '#' = ink, '.' = empty.
FONT = {
    "A": ("#...#", "##.##", "#.#.#", "#.#.#", "#####", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.#.", "#..##"),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
}


class Canvas:
    """A plain RGB pixel buffer with tiny drawing helpers."""

    def __init__(self, width, height, background):
        self.width = width
        self.height = height
        self.pixels = bytearray(background * (width * height))

    def put(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            base = (y * self.width + x) * 3
            self.pixels[base:base + 3] = bytes(color)

    def rect(self, x0, y0, x1, y1, color):
        for y in range(max(0, y0), min(self.height, y1 + 1)):
            for x in range(max(0, x0), min(self.width, x1 + 1)):
                self.put(x, y, color)

    def hline(self, x0, x1, y, color):
        for x in range(x0, x1 + 1):
            self.put(x, y, color)

    def vline(self, x, y0, y1, color):
        for y in range(y0, y1 + 1):
            self.put(x, y, color)

    def line(self, x0, y0, x1, y1, color):
        steps = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(steps + 1):
            x = x0 + (x1 - x0) * i // steps
            y = y0 + (y1 - y0) * i // steps
            self.put(x, y, color)

    def disc(self, cx, cy, r, color):
        for y in range(cy - r, cy + r + 1):
            for x in range(cx - r, cx + r + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    self.put(x, y, color)

    def ring(self, cx, cy, r, color):
        for angle in range(360):
            rad = math.radians(angle)
            self.put(int(cx + r * math.cos(rad)), int(cy + r * math.sin(rad)),
                     color)

    def triangle(self, ax, ay, bx, by, cx, cy, color):
        top, bottom = min(ay, by, cy), max(ay, by, cy)
        for y in range(top, bottom + 1):
            xs = []
            for (px, py, qx, qy) in ((ax, ay, bx, by), (bx, by, cx, cy),
                                     (cx, cy, ax, ay)):
                if py == qy:
                    continue
                if min(py, qy) <= y <= max(py, qy):
                    xs.append(px + (qx - px) * (y - py) // (qy - py))
            if len(xs) >= 2:
                for x in range(min(xs), max(xs) + 1):
                    self.put(x, y, color)

    def text(self, string, x, y, scale, color):
        cursor = x
        for char in string:
            glyph = FONT.get(char.upper(), FONT[" "])
            for row in range(7):
                for col in range(5):
                    if glyph[row][col] == "#":
                        self.rect(cursor + col * scale, y + row * scale,
                                  cursor + col * scale + scale - 1,
                                  y + row * scale + scale - 1, color)
            cursor += 6 * scale
        return cursor

    def text_width(self, string, scale):
        return len(string) * 6 * scale - scale

    def centred(self, string, cx, y, scale, color):
        self.text(string, cx - self.text_width(string, scale) // 2,
                  y, scale, color)


def wrap(string, limit):
    """Greedy word wrap into lines of at most `limit` characters."""
    lines, current = [], ""
    for word in string.split(" "):
        trial = word if not current else current + " " + word
        if len(trial) <= limit:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def card(canvas, x0, y0, x1, y1):
    canvas.rect(x0, y0, x1, y1, CARD)
    canvas.rect(x0, y0, x1, y0 + 2, NAVY)
    for x in range(x0, x1 + 1):
        canvas.put(x, y1, RULE)
    for y in range(y0, y1 + 1):
        canvas.put(x0, y, RULE)
        canvas.put(x1, y, RULE)


def burst(canvas, cx, cy, r, color):
    """A starburst: a disc plus eight spikes."""
    canvas.disc(cx, cy, r // 2, color)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                   (1, 1), (-1, -1), (1, -1), (-1, 1)):
        canvas.line(cx, cy, cx + dx * r, cy + dy * r, color)


def draw_globe_crack(canvas, x0, y0, x1, y1):
    """A cracked globe: the climate talks broke apart over fossil fuels."""
    canvas.rect(x0, y0, x1, y1, SKY)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    radius = min((x1 - x0) // 2, (y1 - y0) // 2) - 6
    canvas.disc(cx, cy, radius, SEA)
    canvas.disc(cx - 26, cy - 18, 16, TEAL)
    canvas.disc(cx + 24, cy + 20, 13, TEAL)
    canvas.disc(cx + 30, cy - 26, 9, TEAL)
    canvas.line(cx - radius, cy, cx + radius, cy, CARD)
    canvas.line(cx, cy - radius, cx, cy + radius, CARD)
    canvas.ring(cx, cy, radius, INK)
    # A red crack zigzags down the face of the globe, drawn twice so
    # it reads at a glance.
    for off in (0, 2):
        canvas.line(cx - 12 + off, cy - radius + 4, cx + 8 + off,
                    cy - radius // 3, CRIMSON)
        canvas.line(cx + 8 + off, cy - radius // 3, cx - 10 + off,
                    cy + radius // 4, CRIMSON)
        canvas.line(cx - 10 + off, cy + radius // 4, cx + 12 + off,
                    cy + radius - 6, CRIMSON)
    # Heat rays above the globe.
    for dx in (-46, 0, 46):
        canvas.line(cx + dx, y0 + 8, cx + dx, y0 + 26, FLAME)


def draw_tanker_fire(canvas, x0, y0, x1, y1):
    """A low tanker in the strait with flames above its deck.

    Drawn for a short, wide box: sea band, low hull, three small
    containers, a bridge tower and two flame bursts just above deck.
    Every coordinate stays inside the box.
    """
    canvas.rect(x0, y0, x1, y1, SKY)
    sea_top = y1 - 16
    canvas.rect(x0, sea_top, x1, y1, SEA)
    for wx in range(x0, x1, 26):
        canvas.hline(wx, wx + 12, y1 - 8, CARD)
    # Low hull and three small containers on its deck.
    hull_top, hull_bottom = y1 - 30, sea_top
    canvas.rect(x0 + 24, hull_top, x1 - 24, hull_bottom, (30, 34, 44))
    canvas.rect(x0 + 36, hull_top - 12, x0 + 110, hull_top, GOLD)
    canvas.rect(x0 + 122, hull_top - 12, x0 + 196, hull_top, CRIMSON)
    canvas.rect(x0 + 208, hull_top - 12, x0 + 282, hull_top, (30, 34, 44))
    # Bridge tower at the stern.
    canvas.rect(x1 - 66, hull_top - 18, x1 - 52, hull_top, (30, 34, 44))
    # Flames above the deck, smoke rising from them.
    burst(canvas, x0 + 72, y0 + 12, 9, FLAME)
    burst(canvas, x1 - 96, y0 + 9, 7, FLAME)
    canvas.line(x0 + 72, y0 + 20, x0 + 80, hull_top - 12, SMOKE)
    canvas.line(x1 - 96, y0 + 16, x1 - 88, hull_top - 12, SMOKE)


def draw_skyline_drone(canvas, x0, y0, x1, y1):
    """A city skyline at dusk with a drone above a smoking tower.

    Drawn for a short, wide box: building heights are capped so no
    roof rises above the box, and the smoke and drone stay inside it.
    """
    canvas.rect(x0, y0, x1, y1, (226, 214, 190))
    heights = (26, 40, 32, 46, 34, 28)
    bw = (x1 - x0) // len(heights)
    for i, hgt in enumerate(heights):
        bx = x0 + i * bw + 6
        canvas.rect(bx, y1 - hgt, bx + bw - 12, y1, (52, 58, 74))
        for wy in range(y1 - hgt + 8, y1 - 6, 12):
            for wx in range(bx + 5, bx + bw - 16, 10):
                canvas.rect(wx, wy, wx + 4, wy + 5, GOLD)
    # Smoke curling from the tallest tower, inside the box.
    sx = x0 + 3 * bw + bw // 2
    canvas.line(sx, y1 - 46, sx + 10, y1 - 54, SMOKE)
    canvas.line(sx + 10, y1 - 54, sx + 4, y1 - 58, SMOKE)
    burst(canvas, sx + 2, y1 - 50, 7, FLAME)
    # A small drone in the sky, inside the box.
    dx, dy = x1 - 48, y0 + 14
    canvas.rect(dx - 12, dy - 2, dx + 12, dy + 2, INK)
    canvas.hline(dx - 18, dx - 8, dy - 6, INK)
    canvas.hline(dx + 8, dx + 18, dy - 6, INK)
    canvas.vline(dx, dy + 2, dy + 8, INK)


def draw_badge_bars(canvas, x0, y0, x1, y1):
    """A gold badge star behind dark jail bars: a cartel boss caught."""
    canvas.rect(x0, y0, x1, y1, (238, 230, 210))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    burst(canvas, cx - 52, cy, 30, GOLD)
    canvas.disc(cx - 52, cy, 12, NAVY)
    canvas.disc(cx - 52, cy, 5, GOLD)
    # Three jail bars on the right.
    for bx in (cx + 8, cx + 34, cx + 60):
        canvas.rect(bx, y0 + 8, bx + 8, y1 - 8, INK)


def draw_factory_fire(canvas, x0, y0, x1, y1):
    """A factory with a sawtooth roof, chimney smoke and flames.

    Drawn for a short box: the hall and its sawtooth roof fill the
    lower half, the chimney stands on the roof at the right, and the
    flames sit just above the roofline.
    """
    canvas.rect(x0, y0, x1, y1, SKY)
    # Chimney standing on the roof, with smoke drifting up-left.
    canvas.rect(x1 - 52, y1 - 52, x1 - 40, y1 - 8, (90, 92, 98))
    canvas.line(x1 - 46, y1 - 54, x1 - 58, y1 - 58, SMOKE)
    canvas.line(x1 - 58, y1 - 58, x1 - 50, y1 - 62, SMOKE)
    # Sawtooth roof and hall.
    canvas.rect(x0 + 12, y1 - 34, x1 - 64, y1 - 8, (52, 58, 74))
    for i in range(3):
        tx = x0 + 24 + i * 62
        canvas.triangle(tx, y1 - 34, tx + 31, y1 - 56, tx + 62, y1 - 34,
                        (52, 58, 74))
    for wx in range(x0 + 26, x1 - 70, 30):
        canvas.rect(wx, y1 - 28, wx + 12, y1 - 14, GOLD)
    # Flames over the roof.
    burst(canvas, x0 + 60, y1 - 64, 10, FLAME)
    burst(canvas, x0 + 150, y1 - 70, 8, FLAME)


def draw_cricket(canvas, x0, y0, x1, y1):
    """A cricket pitch: stumps, a bat and the red ball."""
    canvas.rect(x0, y0, x1, y1, SKY)
    canvas.rect(x0, y1 - 30, x1, y1, PITCH)
    canvas.hline(x0 + 10, x1 - 10, y1 - 30, CARD)
    # Stumps and bails.
    sx = x0 + 40
    for dx in (0, 8, 16):
        canvas.vline(sx + dx, y1 - 66, y1 - 32, GOLD)
    canvas.hline(sx, sx + 16, y1 - 68, GOLD)
    # Bat leaning on the stumps, ball in play.
    canvas.rect(x0 + 84, y1 - 78, x0 + 100, y1 - 34, (150, 104, 52))
    canvas.rect(x0 + 88, y1 - 96, x0 + 96, y1 - 78, (150, 104, 52))
    canvas.disc(x1 - 52, y1 - 52, 10, CRIMSON)
    canvas.disc(x1 - 52, y1 - 52, 4, CARD)


def build():
    canvas = Canvas(W, H, PAPER)
    canvas.rect(0, 0, W - 1, 7, GOLD)
    canvas.rect(0, H - 8, W - 1, H - 1, GOLD)

    # Masthead.
    canvas.rect(16, 16, 1008, 138, NAVY)
    canvas.centred("THE WORLD TODAY", 512, 34, 6, CARD)
    canvas.centred("MONDAY, NOVEMBER 23, 2026", 512, 102, 3, GOLD)

    # Kicker strip under the masthead.
    canvas.centred("COP31  -  GULF  -  UKRAINE  -  MEXICO  -  INDONESIA  -  CRICKET",
                   512, 156, 2, GREY)

    # Lead story: COP31 collapses.
    card(canvas, 24, 184, 1000, 452)
    canvas.text("CLIMATE", 48, 206, 2, CRIMSON)
    canvas.text("COP31 COLLAPSES", 48, 240, 4, INK)
    canvas.text("NO FOSSIL-FUEL DEAL", 48, 280, 4, INK)
    body = wrap("194 nations split in Antalya as the longest COP ever "
                "ends with no pact. First climate summit failure "
                "since 2009. The EU and island states rejected "
                "the pact.", 44)
    for i, line in enumerate(body):
        canvas.text(line, 48, 336 + i * 22, 2, INK)
    draw_globe_crack(canvas, 624, 206, 976, 428)

    # Middle row: Gulf tankers and the Ukraine war spilling over.
    card(canvas, 24, 468, 494, 700)
    canvas.text("GULF", 44, 486, 2, TEAL)
    canvas.text("TANKERS HIT IN", 44, 514, 3, INK)
    canvas.text("HORMUZ", 44, 544, 3, INK)
    for i, line in enumerate(wrap("Bahrain site hit; 2 tankers struck "
                                  "in Hormuz. 25 ships hit in 7 days.", 34)):
        canvas.text(line, 44, 584 + i * 20, 2, INK)
    draw_tanker_fire(canvas, 44, 626, 474, 684)

    card(canvas, 530, 468, 1000, 700)
    canvas.text("UKRAINE", 550, 486, 2, CRIMSON)
    canvas.text("WAR SPILLS OVER", 550, 514, 3, INK)
    for i, line in enumerate(wrap("Drone hits Kyiv flats: 14 missing. "
                                  "Ship ablaze off Finland; missiles "
                                  "land in Poland.", 34)):
        canvas.text(line, 550, 552 + i * 20, 2, INK)
    draw_skyline_drone(canvas, 550, 626, 980, 684)

    # Bottom row: Mexico, Indonesia, cricket.
    card(canvas, 24, 716, 330, 962)
    canvas.text("MEXICO", 42, 732, 2, GOLD)
    canvas.text("EL CHAPO ISIDRO", 42, 758, 3, INK)
    canvas.text("CAUGHT", 42, 788, 2, INK)
    for i, line in enumerate(wrap("FBI most-wanted boss seized "
                                  "in Sinaloa; 11 killed in "
                                  "firefights.", 26)):
        canvas.text(line, 42, 820 + i * 18, 2, INK)
    draw_badge_bars(canvas, 42, 886, 312, 946)

    card(canvas, 358, 716, 664, 962)
    canvas.text("INDONESIA", 376, 732, 2, CRIMSON)
    canvas.text("FACTORY FIRE", 376, 758, 3, INK)
    for i, line in enumerate(wrap("7 dead, 50 missing after "
                                  "a factory fire in Indonesia.", 24)):
        canvas.text(line, 376, 792 + i * 18, 2, INK)
    draw_factory_fire(canvas, 376, 886, 646, 946)

    card(canvas, 692, 716, 1000, 962)
    canvas.text("SPORT", 710, 732, 2, TEAL)
    canvas.text("INDIA 720/9", 710, 758, 3, INK)
    canvas.text("RECORD IN WELLINGTON", 710, 788, 2, INK)
    for i, line in enumerate(wrap("India declare a record 720/9 in the "
                                  "Wellington Test vs New Zealand.", 26)):
        canvas.text(line, 710, 820 + i * 18, 2, INK)
    draw_cricket(canvas, 710, 886, 982, 946)

    # Footer.
    canvas.centred("ALL STORIES FIRST REPORTED MONDAY, 23 NOVEMBER 2026",
                   512, 984, 2, GREY)
    return canvas


def encode_png(canvas):
    """Encode the canvas as a deterministic RGB PNG (filter 0 rows)."""
    raw = bytearray()
    stride = canvas.width * 3
    for y in range(canvas.height):
        raw.append(0)
        start = y * stride
        raw += canvas.pixels[start:start + stride]
    payload = zlib.compress(bytes(raw), 9)

    def chunk(kind, body):
        data = struct.pack(">I", len(body)) + kind + body
        return data + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", canvas.width, canvas.height, 8, 2, 0, 0, 0)
    blob = b"\x89PNG\r\n\x1a\n"
    blob += chunk(b"IHDR", ihdr)
    blob += chunk(b"IDAT", payload)
    blob += chunk(b"IEND", b"")
    return blob


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    blob = encode_png(build())
    with open(os.path.join(here, "entry.png"), "wb") as handle:
        handle.write(blob)
    print(f"entry.png: {len(blob)} bytes, {W}x{H}")


if __name__ == "__main__":
    main()
