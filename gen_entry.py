#!/usr/bin/env python3
"""Render the 23 November 2026 world-news front page, 1024x1024 PNG.

Written from scratch in this session with Pillow and the DejaVu
typefaces: a serif masthead and headlines over sans body copy, on a
newspaper-paper background. The six stories are the verified
23 Nov 2026 headlines from the morning news scan:

  * COP31 collapses in Antalya - 194 nations split, no fossil-fuel deal
  * Gulf tankers struck in the Strait of Hormuz; a Bahrain site hit
  * The Ukraine war spills over - Kyiv drone strike, a Russian cargo
    ship ablaze off Finland, missiles landing in Poland
  * Mexico captures FBI most-wanted cartel boss 'El Chapo Isidro'
  * A factory fire in Indonesia leaves 7 dead and 50 missing
  * India declare a record 720/9 in the Wellington Test

The layout is data driven: STORIES holds the copy, GRID holds the
card geometry, and one small illustration routine per story draws
inside its own box. Output is deterministic - the same fonts, the
same coordinates, no timestamps - so repeated runs are byte
identical. No network, no environment reads.
"""
import os
import textwrap

from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
PAPER = (246, 241, 229)
CARD_FILL = (255, 255, 255)
INK = (26, 32, 48)
NAVY = (22, 38, 74)
RED = (166, 30, 30)
TEAL = (15, 118, 110)
GOLD = (185, 138, 31)
GREY = (96, 102, 116)
RULE = (208, 200, 184)
SEA = (38, 110, 138)
SKY = (214, 232, 240)
FLAME = (232, 120, 30)
SMOKE = (120, 124, 130)
PITCH = (96, 140, 82)
DUSK = (226, 214, 190)
BUILDING = (52, 58, 74)
SAND = (238, 230, 210)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def load(name, size):
    """Load a DejaVu face, falling back to Pillow's built-in font."""
    path = os.path.join(FONT_DIR, name)
    try:
        return ImageFont.truetype(path, size)
    except (OSError, IOError):
        return ImageFont.load_default()


def serif_bold(size):
    return load("DejaVuSerif-Bold.ttf", size)


def serif(size):
    return load("DejaVuSerif.ttf", size)


def sans(size):
    return load("DejaVuSans.ttf", size)


def sans_bold(size):
    return load("DejaVuSans-Bold.ttf", size)


def fit_serif(draw, text, size, max_width):
    """Largest serif-bold size at or below `size` that fits `max_width`."""
    while size > 12:
        font = serif_bold(size)
        if draw.textlength(text, font=font) <= max_width:
            return font
        size -= 2
    return serif_bold(12)


def split_lines(draw, text, font, max_width):
    """Word-wrap `text` so every line fits `max_width` pixels."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        current = ""
        for word in words:
            trial = word if not current else current + " " + word
            if draw.textlength(trial, font=font) <= max_width:
                current = trial
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def draw_wrapped(draw, text, font, x, y, max_width, fill, leading):
    """Draw wrapped text; return the y just below the last line."""
    for line in split_lines(draw, text, font, max_width):
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def centred(draw, text, cx, y, font, fill):
    draw.text((cx - draw.textlength(text, font=font) / 2, y),
              text, font=font, fill=fill)


def star_points(cx, cy, outer, inner, points=5, tilt=-90):
    """Vertices of a star polygon, alternating outer/inner radius."""
    import math
    verts = []
    for i in range(points * 2):
        radius = outer if i % 2 == 0 else inner
        angle = math.radians(tilt + i * 180.0 / points)
        verts.append((cx + radius * math.cos(angle),
                      cy + radius * math.sin(angle)))
    return verts


def flame_burst(draw, cx, cy, size, color=FLAME):
    """A small spiked flame: star polygon over a solid disc."""
    draw.polygon(star_points(cx, cy, size, size * 0.45, 8), fill=color)
    draw.ellipse((cx - size * 0.4, cy - size * 0.4,
                  cx + size * 0.4, cy + size * 0.4), fill=color)


def card_frame(draw, box):
    """White card with a navy top rule and a thin grey border."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=CARD_FILL)
    draw.rectangle((x0, y0, x1, y0 + 3), fill=NAVY)
    draw.rectangle((x0, y0, x1, y1), outline=RULE, width=1)


def art_globe(draw, box):
    """Cracked globe for the collapsed climate talks."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=SKY)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    r = min(x1 - x0, y1 - y0) // 2 - 8
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=SEA)
    draw.ellipse((cx - 78, cy - 52, cx - 26, cy - 8), fill=TEAL)
    draw.ellipse((cx + 18, cy + 22, cx + 66, cy + 66), fill=TEAL)
    draw.ellipse((cx + 44, cy - 66, cx + 78, cy - 34), fill=TEAL)
    draw.line((cx - r, cy, cx + r, cy), fill=CARD_FILL, width=2)
    draw.line((cx, cy - r, cx, cy + r), fill=CARD_FILL, width=2)
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=INK, width=2)
    crack = [(cx - 14, cy - r + 6), (cx + 10, cy - r // 3),
             (cx - 12, cy + r // 4), (cx + 14, cy + r - 8)]
    draw.line(crack, fill=RED, width=4, joint="curve")
    for dx in (-52, 0, 52):
        draw.line((cx + dx, y0 + 10, cx + dx, y0 + 28),
                  fill=FLAME, width=3)


def art_tanker(draw, box):
    """A tanker low in the strait, flames above its deck."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=SKY)
    sea = y1 - 18
    draw.rectangle((x0, sea, x1, y1), fill=SEA)
    for wx in range(x0 + 4, x1 - 12, 30):
        draw.line((wx, y1 - 9, wx + 14, y1 - 9), fill=CARD_FILL, width=2)
    hull_top = sea - 16
    draw.rectangle((x0 + 26, hull_top, x1 - 26, sea), fill=(30, 34, 44))
    draw.rectangle((x0 + 38, hull_top - 14, x0 + 112, hull_top), fill=GOLD)
    draw.rectangle((x0 + 124, hull_top - 14, x0 + 198, hull_top), fill=RED)
    draw.rectangle((x0 + 210, hull_top - 14, x0 + 284, hull_top),
                   fill=(30, 34, 44))
    draw.rectangle((x1 - 68, hull_top - 20, x1 - 54, hull_top),
                   fill=(30, 34, 44))
    flame_burst(draw, x0 + 74, y0 + 16, 11)
    flame_burst(draw, x1 - 98, y0 + 13, 9)
    draw.line((x0 + 74, y0 + 24, x0 + 82, hull_top - 14),
              fill=SMOKE, width=2)
    draw.line((x1 - 98, y0 + 20, x1 - 90, hull_top - 14),
              fill=SMOKE, width=2)


def art_city(draw, box):
    """Dusk skyline with a smoking tower and a drone overhead."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=DUSK)
    heights = (30, 46, 36, 54, 40, 32)
    slot = (x1 - x0) // len(heights)
    for i, height in enumerate(heights):
        bx = x0 + i * slot + 6
        draw.rectangle((bx, y1 - height, bx + slot - 12, y1),
                       fill=BUILDING)
        for wy in range(y1 - height + 9, y1 - 7, 13):
            for wx in range(bx + 5, bx + slot - 17, 11):
                draw.rectangle((wx, wy, wx + 4, wy + 5), fill=GOLD)
    sx = x0 + 3 * slot + slot // 2
    draw.line([(sx, y1 - 54), (sx + 10, y1 - 62), (sx + 4, y1 - 68)],
              fill=SMOKE, width=2)
    flame_burst(draw, sx + 2, y1 - 56, 8)
    dx, dy = x1 - 52, y0 + 16
    draw.rectangle((dx - 13, dy - 2, dx + 13, dy + 2), fill=INK)
    draw.line((dx - 19, dy - 7, dx - 9, dy - 7), fill=INK, width=2)
    draw.line((dx + 9, dy - 7, dx + 19, dy - 7), fill=INK, width=2)
    draw.line((dx, dy + 2, dx, dy + 9), fill=INK, width=2)


def art_badge(draw, box):
    """Gold badge star behind dark jail bars: a cartel boss caught."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=SAND)
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    draw.polygon(star_points(cx - 56, cy, 34, 14), fill=GOLD)
    draw.ellipse((cx - 70, cy - 14, cx - 42, cy + 14), fill=NAVY)
    draw.ellipse((cx - 62, cy - 6, cx - 50, cy + 6), fill=GOLD)
    for bx in (cx + 6, cx + 32, cx + 58):
        draw.rectangle((bx, y0 + 8, bx + 8, y1 - 8), fill=INK)


def art_factory(draw, box):
    """Factory with a sawtooth roof, chimney smoke and flames."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=SKY)
    draw.rectangle((x1 - 54, y1 - 56, x1 - 42, y1 - 8), fill=(90, 92, 98))
    draw.line([(x1 - 48, y1 - 58), (x1 - 60, y1 - 62),
               (x1 - 52, y1 - 66)], fill=SMOKE, width=2)
    roof = []
    for i in range(4):
        tx = x0 + 14 + i * 62
        roof += [(tx, y1 - 36), (tx + 31, y1 - 58), (tx + 62, y1 - 36)]
    draw.polygon(roof, fill=BUILDING)
    draw.rectangle((x0 + 14, y1 - 36, x1 - 66, y1 - 8), fill=BUILDING)
    for wx in range(x0 + 28, x1 - 72, 32):
        draw.rectangle((wx, y1 - 30, wx + 12, y1 - 16), fill=GOLD)
    flame_burst(draw, x0 + 62, y1 - 68, 11)
    flame_burst(draw, x0 + 152, y1 - 74, 9)


def art_cricket(draw, box):
    """Cricket pitch: stumps, a leaning bat and the red ball."""
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=SKY)
    draw.rectangle((x0, y1 - 32, x1, y1), fill=PITCH)
    draw.line((x0 + 10, y1 - 32, x1 - 10, y1 - 32),
              fill=CARD_FILL, width=2)
    sx = x0 + 42
    for dx in (0, 9, 18):
        draw.line((sx + dx, y1 - 68, sx + dx, y1 - 34), fill=GOLD, width=3)
    draw.line((sx, y1 - 70, sx + 18, y1 - 70), fill=GOLD, width=3)
    draw.polygon([(x0 + 86, y1 - 80), (x0 + 102, y1 - 80),
                  (x0 + 102, y1 - 36), (x0 + 86, y1 - 36)],
                 fill=(150, 104, 52))
    draw.rectangle((x0 + 90, y1 - 98, x0 + 98, y1 - 80),
                   fill=(150, 104, 52))
    draw.ellipse((x1 - 62, y1 - 62, x1 - 42, y1 - 42), fill=RED)
    draw.ellipse((x1 - 56, y1 - 56, x1 - 48, y1 - 48), fill=CARD_FILL)


ARTISTS = {
    "globe": art_globe,
    "tanker": art_tanker,
    "city": art_city,
    "badge": art_badge,
    "factory": art_factory,
    "cricket": art_cricket,
}

STORIES = [
    {
        "kicker": "CLIMATE", "accent": RED, "art": "globe",
        "headline": ["COP31 COLLAPSES", "NO FOSSIL-FUEL DEAL"],
        "body": ("194 nations split in Antalya as the longest COP ever "
                 "ends with no pact. First climate summit failure "
                 "since 2009. The EU and island states rejected "
                 "the pact."),
    },
    {
        "kicker": "GULF", "accent": TEAL, "art": "tanker",
        "headline": ["TANKERS HIT IN", "HORMUZ"],
        "body": ("Bahrain site hit; 2 tankers struck in Hormuz. "
                 "25 ships hit in 7 days."),
    },
    {
        "kicker": "UKRAINE", "accent": RED, "art": "city",
        "headline": ["WAR SPILLS OVER"],
        "body": ("Drone hits Kyiv flats: 14 missing. Ship ablaze "
                 "off Finland; missiles land in Poland."),
    },
    {
        "kicker": "MEXICO", "accent": GOLD, "art": "badge",
        "headline": ["EL CHAPO ISIDRO", "CAUGHT"],
        "body": ("FBI most-wanted boss seized in Sinaloa; "
                 "11 killed in firefights."),
    },
    {
        "kicker": "INDONESIA", "accent": RED, "art": "factory",
        "headline": ["FACTORY FIRE"],
        "body": ("7 dead, 50 missing after a factory fire "
                 "in Indonesia."),
    },
    {
        "kicker": "SPORT", "accent": TEAL, "art": "cricket",
        "headline": ["INDIA 720/9", "RECORD IN WELLINGTON"],
        "body": ("India declare a record 720/9 in the Wellington "
                 "Test vs New Zealand."),
    },
]


def paint_masthead(draw):
    draw.rectangle((0, 0, PAGE - 1, 6), fill=GOLD)
    draw.rectangle((14, 14, 1010, 148), fill=NAVY)
    centred(draw, "THE WORLD TODAY", 512, 34, serif_bold(62), CARD_FILL)
    centred(draw, "MONDAY, NOVEMBER 23, 2026", 512, 108,
            sans_bold(24), GOLD)
    centred(draw, "COP31  -  GULF  -  UKRAINE  -  MEXICO  -  "
                   "INDONESIA  -  CRICKET", 512, 164, sans(16), GREY)


def paint_lead(draw, story):
    box = (20, 184, 1004, 448)
    card_frame(draw, box)
    draw.text((44, 202), story["kicker"], font=sans_bold(20),
              fill=story["accent"])
    y = 230
    for line in story["headline"]:
        fitted = fit_serif(draw, line, 46, 580)
        draw.text((44, y), line, font=fitted, fill=INK)
        y += 52
    draw_wrapped(draw, story["body"], sans(19), 44, 340, 556, INK, 26)
    ARTISTS[story["art"]](draw, (636, 200, 988, 432))


def paint_mid(draw, story, box):
    x0, y0, x1, y1 = box
    card_frame(draw, box)
    pad = x0 + 20
    draw.text((pad, y0 + 16), story["kicker"], font=sans_bold(18),
              fill=story["accent"])
    head = serif_bold(34)
    y = y0 + 40
    for line in story["headline"]:
        fitted = fit_serif(draw, line, 34, x1 - x0 - 40)
        draw.text((pad, y), line, font=fitted, fill=INK)
        y += 40
    draw_wrapped(draw, story["body"], sans(17), pad, y + 8,
                 x1 - x0 - 40, INK, 23)
    ARTISTS[story["art"]](draw, (pad, y1 - 62, x1 - 20, y1 - 12))


def paint_small(draw, story, box):
    x0, y0, x1, y1 = box
    card_frame(draw, box)
    pad = x0 + 18
    draw.text((pad, y0 + 14), story["kicker"], font=sans_bold(17),
              fill=story["accent"])
    sub = sans_bold(18)
    y = y0 + 38
    for line in story["headline"]:
        big = len(line) <= 16
        if big:
            font = fit_serif(draw, line, 28, x1 - x0 - 36)
        else:
            font = sub
        draw.text((pad, y), line, font=font, fill=INK)
        y += 36 if big else 26
    draw_wrapped(draw, story["body"], sans(16), pad, y + 4,
                 x1 - x0 - 36, INK, 21)
    ARTISTS[story["art"]](draw, (pad, y1 - 66, x1 - 18, y1 - 14))


def render():
    image = Image.new("RGB", (PAGE, PAGE), PAPER)
    draw = ImageDraw.Draw(image)
    paint_masthead(draw)
    paint_lead(draw, STORIES[0])
    paint_mid(draw, STORIES[1], (20, 464, 502, 700))
    paint_mid(draw, STORIES[2], (522, 464, 1004, 700))
    paint_small(draw, STORIES[3], (20, 716, 336, 958))
    paint_small(draw, STORIES[4], (354, 716, 670, 958))
    paint_small(draw, STORIES[5], (688, 716, 1004, 958))
    centred(draw, "ALL STORIES FIRST REPORTED MONDAY, 23 NOVEMBER 2026",
            512, 978, sans(16), GREY)
    draw.rectangle((0, 1016, PAGE - 1, 1023), fill=GOLD)
    return image


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    image = render()
    target = os.path.join(here, "entry.png")
    image.save(target, format="PNG")
    print("entry.png: %d bytes, %dx%d"
          % (os.path.getsize(target), PAGE, PAGE))


if __name__ == "__main__":
    main()
