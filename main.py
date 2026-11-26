#!/usr/bin/env python3
"""news-image-20261125 — sum up the world's news of Wednesday 25 November 2026
in one image. Facts-fix rewrite: corrected market closes and Hormuz panel.

Renders a 1024x1024 PNG: dark navy background, gold date header, 2x3 grid of
story panels. All people are dark silhouettes only — no recognizable faces.
Deterministic: no network, no clock, no randomness.

Output: writes entry.png into $MAKEFUN_OUTPUT_DIR (fallback: /output).
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- constants
W, H = 1024, 1024

NAVY = (10, 26, 48)          # page background
PANEL = (18, 41, 74)         # panel fill
PANEL_EDGE = (38, 74, 120)   # panel outline
GOLD = (232, 184, 75)        # gold accents / date header
WHITE = (240, 244, 250)
BODY = (205, 216, 230)       # body text
MUTED = (140, 158, 182)      # footer / tag text
SILHOUETTE = (4, 10, 20)     # people: near-black silhouettes
SKY_LINE = (120, 160, 205)   # icon line work

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
F_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
F_REG = os.path.join(FONT_DIR, "DejaVuSans.ttf")

# Fixed star field (deterministic — no random module).
STARS = [
    (52, 88, 2), (118, 40, 1), (205, 118, 2), (318, 52, 1), (430, 96, 2),
    (512, 44, 1), (640, 108, 2), (742, 56, 1), (905, 64, 2), (958, 48, 1),
    (70, 1010, 1), (940, 1012, 1), (990, 140, 2), (34, 150, 1),
]

# ---------------------------------------------------------------- text data
# Six stories of Wednesday 25 November 2026, facts checked against
# Reuters / AP / phys.org / pm.gov.au / CNN reporting.
PANELS = [
    {
        "tag": "SPACE",
        "title": "PAKISTAN REACHES SPACE",
        "body": ("Shenzhou-24 blasts off on Wednesday. Muhammad Zeeshan Ali "
                 "becomes Pakistan's first astronaut - and the first "
                 "foreigner aboard China's Tiangong station."),
        "icon": "rocket",
    },
    {
        "tag": "MARKETS",
        "title": "WALL ST WHIPSAW",
        "body": ("S&P 500 ends -0.3% and Nasdaq -0.6% at the close, after "
                 "plunging as much as 3.2% and 4.6% intraday. The Dow "
                 "fights back to finish +0.3%."),
        "icon": "chart",
    },
    {
        "tag": "STRAIT OF HORMUZ",
        "title": "MINES IN THE STRAIT",
        "body": ("Iran's Revolutionary Guards say two tankers struck mines "
                 "in the Strait of Hormuz on Wednesday. The claim could "
                 "not be independently verified."),
        "icon": "tanker",
    },
    {
        "tag": "COURTS",
        "title": "HUAWEI GUILTY, RICO FAILS",
        "body": ("A US jury convicts Huawei of stealing trade secrets and "
                 "bank fraud - but acquits it of racketeering conspiracy."),
        "icon": "court",
    },
    {
        "tag": "PACIFIC",
        "title": "SOLOMONS PICK AUSTRALIA",
        "body": ("Australia and Solomon Islands sign a security treaty in "
                 "Canberra: no foreign military bases on Solomons soil."),
        "icon": "islands",
    },
    {
        "tag": "COLOMBIA",
        "title": "SIEGE ENDS IN CARTAGENA",
        "body": ("Colombian forces storm an Exito supermarket early "
                 "Wednesday. All 20 remaining hostages are freed; one "
                 "gunman is killed."),
        "icon": "store",
    },
]

HEADER_DATE = "WEDNESDAY 25 NOVEMBER 2026"
HEADER_SUB = "THE WORLD IN ONE IMAGE  ·  SIX STORIES"
FOOTER = "SOURCES: REUTERS  ·  AP  ·  PHYS.ORG  ·  PM.GOV.AU  ·  CNN"


# ---------------------------------------------------------------- helpers
def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def tracked(draw, xy, text, fnt, fill, tracking=3):
    """Draw text with extra letter spacing; returns total width."""
    x, y = xy
    total = 0
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        w = draw.textlength(ch, font=fnt) + tracking
        x += w
        total += w
    return total - tracking


def center_tracked(draw, cx, y, text, fnt, fill, tracking=3):
    w = sum(draw.textlength(c, font=fnt) + tracking for c in text) - tracking
    tracked(draw, (cx - w / 2, y), text, fnt, fill, tracking)


# ---------------------------------------------------------------- icons
# Each icon draws inside a ~120x120 box at (ox, oy). Line-art in gold/sky,
# people as solid dark silhouettes. No faces, no text inside icons.

def icon_rocket(d, ox, oy):
    # Rocket body, nose cone, window, fins, flame; small astronaut silhouette.
    d.polygon([(ox + 60, oy + 6), (ox + 42, oy + 34), (ox + 78, oy + 34)],
              fill=GOLD)
    d.rounded_rectangle([ox + 42, oy + 32, ox + 78, oy + 82], radius=10,
                        fill=WHITE, outline=GOLD, width=2)
    d.ellipse([ox + 52, oy + 46, ox + 68, oy + 62], fill=SKY_LINE)
    d.polygon([(ox + 42, oy + 66), (ox + 28, oy + 92), (ox + 42, oy + 84)],
              fill=GOLD)
    d.polygon([(ox + 78, oy + 66), (ox + 92, oy + 92), (ox + 78, oy + 84)],
              fill=GOLD)
    d.polygon([(ox + 52, oy + 82), (ox + 68, oy + 82), (ox + 60, oy + 108)],
              fill=(235, 120, 60))
    # Astronaut silhouette floating beside the rocket (helmet, body, limbs).
    d.ellipse([ox + 2, oy + 92, ox + 18, oy + 108], fill=SILHOUETTE)
    d.rounded_rectangle([ox + 4, oy + 108, ox + 16, oy + 124], radius=4,
                        fill=SILHOUETTE)
    d.line([(ox + 5, oy + 124), (ox + 1, oy + 136)], fill=SILHOUETTE, width=4)
    d.line([(ox + 15, oy + 124), (ox + 19, oy + 136)], fill=SILHOUETTE, width=4)


def icon_chart(d, ox, oy):
    # Axes + whipsaw line: steep plunge, then a sharp recovery.
    d.line([(ox + 8, oy + 12), (ox + 8, oy + 104)], fill=MUTED, width=2)
    d.line([(ox + 8, oy + 104), (ox + 112, oy + 104)], fill=MUTED, width=2)
    pts = [(ox + 12, oy + 28), (ox + 34, oy + 40), (ox + 52, oy + 88),
           (ox + 70, oy + 96), (ox + 88, oy + 62), (ox + 106, oy + 52)]
    d.line(pts, fill=GOLD, width=4, joint="curve")
    d.ellipse([ox + 102, oy + 48, ox + 110, oy + 56], fill=GOLD)


def icon_tanker(d, ox, oy):
    # Tanker hull + containers, a spiked mine, waves.
    d.polygon([(ox + 8, oy + 62), (ox + 104, oy + 62), (ox + 92, oy + 88),
               (ox + 20, oy + 88)], fill=WHITE)
    d.rectangle([ox + 22, oy + 42, ox + 46, oy + 62], fill=GOLD)
    d.rectangle([ox + 50, oy + 42, ox + 74, oy + 62], fill=SKY_LINE)
    d.rectangle([ox + 78, oy + 48, ox + 96, oy + 62], fill=GOLD)
    # Mine: spiked circle half-submerged at the waterline, right of the hull.
    cx, cy, r = ox + 100, oy + 98, 8
    for ang in range(0, 360, 45):
        x2 = cx + int(14 * math.cos(math.radians(ang)))
        y2 = cy + int(14 * math.sin(math.radians(ang)))
        d.line([(cx, cy), (x2, y2)], fill=GOLD, width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD)
    for wx in (ox + 6, ox + 44):
        d.arc([wx, oy + 96, wx + 30, oy + 110], 0, 180, fill=SKY_LINE, width=3)


def icon_court(d, ox, oy):
    # Courthouse: pediment, columns, steps.
    d.polygon([(ox + 10, oy + 34), (ox + 60, oy + 10), (ox + 110, oy + 34)],
              fill=GOLD)
    d.rectangle([ox + 14, oy + 34, ox + 106, oy + 42], fill=GOLD)
    for cx in (ox + 24, ox + 46, ox + 68, ox + 90):
        d.rectangle([cx - 4, oy + 42, cx + 4, oy + 82], fill=WHITE)
    d.rectangle([ox + 14, oy + 82, ox + 106, oy + 90], fill=WHITE)
    d.rectangle([ox + 8, oy + 90, ox + 112, oy + 98], fill=GOLD)


def icon_islands(d, ox, oy):
    # Two Pacific islands, a flag, and a small shield with a check.
    d.ellipse([ox + 8, oy + 66, ox + 52, oy + 96], fill=SKY_LINE)
    d.ellipse([ox + 58, oy + 74, ox + 104, oy + 98], fill=SKY_LINE)
    d.line([(ox + 30, oy + 66), (ox + 30, oy + 34)], fill=GOLD, width=3)
    d.polygon([(ox + 30, oy + 34), (ox + 52, oy + 42), (ox + 30, oy + 50)],
              fill=GOLD)
    # Small gold star above the second island.
    sx, sy = ox + 82, oy + 54
    d.polygon([(sx, sy - 10), (sx + 3, sy - 3), (sx + 10, sy), (sx + 3, sy + 3),
               (sx, sy + 10), (sx - 3, sy + 3), (sx - 10, sy), (sx - 3, sy - 3)],
              fill=GOLD)


def icon_store(d, ox, oy):
    # Supermarket front: striped awning, sign band, door; two dark
    # silhouettes (rescue figures) in front — helmets, no faces.
    for i, x0 in enumerate(range(ox + 10, ox + 106, 16)):
        col = GOLD if i % 2 == 0 else WHITE
        d.rectangle([x0, oy + 26, x0 + 16, oy + 44], fill=col)
    d.rectangle([ox + 10, oy + 44, ox + 110, oy + 58], fill=PANEL_EDGE)
    d.rectangle([ox + 52, oy + 58, ox + 68, oy + 96], fill=GOLD)
    d.rectangle([ox + 16, oy + 62, ox + 44, oy + 96], outline=SKY_LINE,
                width=2)
    d.rectangle([ox + 76, oy + 62, ox + 104, oy + 96], outline=SKY_LINE,
                width=2)
    # Two silhouettes standing guard beside the door.
    for sx in (ox + 44, ox + 74):
        d.ellipse([sx - 5, oy + 86, sx + 5, oy + 96], fill=SILHOUETTE)
        d.rounded_rectangle([sx - 6, oy + 96, sx + 6, oy + 114], radius=3,
                            fill=SILHOUETTE)

ICONS = {
    "rocket": icon_rocket,
    "chart": icon_chart,
    "tanker": icon_tanker,
    "court": icon_court,
    "islands": icon_islands,
    "store": icon_store,
}


# ---------------------------------------------------------------- render
def render():
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)

    for (sx, sy, r) in STARS:
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(200, 210, 230))

    # Header.
    f_date = font(F_BOLD, 44)
    f_sub = font(F_BOLD, 19)
    center_tracked(d, W / 2, 30, HEADER_DATE, f_date, GOLD, tracking=4)
    center_tracked(d, W / 2, 92, HEADER_SUB, f_sub, MUTED, tracking=5)
    d.line([(40, 126), (W - 40, 126)], fill=GOLD, width=3)

    # Grid: 2 cols x 3 rows.
    margin, gap = 28, 16
    grid_top, grid_bottom = 142, 984
    pw = (W - 2 * margin - gap) // 2
    ph = (grid_bottom - grid_top - 2 * gap) // 3

    f_tag = font(F_BOLD, 15)
    f_title = font(F_BOLD, 24)
    f_body = font(F_REG, 19)

    for i, panel in enumerate(PANELS):
        col, row = i % 2, i // 2
        x = margin + col * (pw + gap)
        y = grid_top + row * (ph + gap)

        d.rounded_rectangle([x, y, x + pw, y + ph], radius=14, fill=PANEL,
                            outline=PANEL_EDGE, width=2)
        d.rectangle([x + 18, y + 16, x + 66, y + 20], fill=GOLD)

        # Tag (top-left), title + body in the left text zone,
        # icon in the right zone.
        text_w = pw - 18 - 132
        tracked(d, (x + 18, y + 28), panel["tag"], f_tag, GOLD, tracking=2)
        title_lines = wrap(d, panel["title"], f_title, text_w)
        ty = y + 52
        for line in title_lines:
            d.text((x + 18, ty), line, font=f_title, fill=WHITE)
            ty += 30
        body_lines = wrap(d, panel["body"], f_body, text_w)
        by = ty + 8
        for line in body_lines[:6]:
            d.text((x + 18, by), line, font=f_body, fill=BODY)
            by += 25

        ICONS[panel["icon"]](d, x + pw - 126, y + (ph - 120) // 2 + 8)

    # Footer.
    f_foot = font(F_REG, 14)
    fw = d.textlength(FOOTER, font=f_foot)
    d.text(((W - fw) / 2, 994), FOOTER, font=f_foot, fill=MUTED)

    return img


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    img = render()
    path = os.path.join(out_dir, "entry.png")
    img.save(path, format="PNG", optimize=True)
    print(f"wrote {path}  {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
