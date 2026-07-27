"""OG Image v21 — 'Smart Router' subtitle readable (black, larger)."""
from PIL import Image, ImageDraw, ImageFont
import os

SRC = r"C:\Users\yican\Downloads\b2b-saas-og-hero-v2_1785127569.png"
OUT = r"D:\WorkBuddy\日常\cost-arbitrage-stack\landing\og-image.jpg"

FONT_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
FONT_REG  = r"C:\Windows\Fonts\segoeui.ttf"

W, H = 1200, 575

BLACK   = "#000000"
GREEN    = "#16a34a"
GRAY_LINE = "#d4d4d8"
WHITE   = "#FFFFFF"
WATERMARK = "#9ca3af"

src = Image.open(SRC).convert("RGB")
sw, sh = src.size
img = Image.new("RGB", (W, H), "#f5f0e6")
ratio = max(W / sw, H / sh)
nw, nh = int(sw * ratio), int(sh * ratio)
resized = src.resize((nw, nh), Image.LANCZOS)
ox = (W - nw) // 2
oy = (H - nh) // 2
img.paste(resized, (ox, oy))

draw = ImageDraw.Draw(img)
font_b = ImageFont.truetype(FONT_BOLD, 58)
font_s = ImageFont.truetype(FONT_REG, 22)
font_p = ImageFont.truetype(FONT_BOLD, 27)
font_sm = ImageFont.truetype(FONT_REG, 13)

def centered_text(draw, cx, cy, text, font, fill):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text((cx - tw // 2, cy - th // 2), text, font=font, fill=fill)

# ═══ LEFT COLUMN ═══
title = "Cut 70\u201390% off your LLM bill"
tx, ty = 48, 52
draw.text((tx, ty), title, font=font_b, fill=BLACK)
tb = draw.textbbox((tx, ty), title, font=font_b)
_, _, tbr, _ = tb
draw.line([(tx, tbr + 10), (tb[2], tbr + 10)], fill=GREEN, width=3)

sub = "Route API traffic to cheaper models \u2014 same quality, fraction of cost"
draw.text((tx, tbr + 28), sub, font=font_s, fill=BLACK)

div_y = 195
draw.line([(tx, div_y), (tx + 520, div_y)], fill=GRAY_LINE, width=1)

bullets = [
    "Same prompts, same quality \u2014 lower cost",
    "Route each task to the right model tier",
    "GDPR-aware: you control data residency",
]
by_start = div_y + 24
line_h = 56
for i, btxt in enumerate(bullets):
    by = by_start + i * line_h
    draw.ellipse([tx, by + 7, tx + 12, by + 19], fill=GREEN)
    draw.text((tx + 24, by), btxt, font=font_p, fill=BLACK)

# ═══ RIGHT SIDE ═══
node_font = ImageFont.truetype(FONT_BOLD, 14)
sub_node_font = ImageFont.truetype(FONT_BOLD, 12)   # v21: black + bold + bigger

nodes_black = {
    "Cloud Asia":     (1059, 176),
    "Western Cloud":  (1059, 278),
    "Self-hosted":    (1059, 386),
}
for label, (nx, ny) in nodes_black.items():
    centered_text(draw, nx, ny, label, node_font, BLACK)

# Gateway: white title + black bold subtitle (readable on pale green)
gx, gy = 368, 290
centered_text(draw, gx, gy, "Gateway", node_font, WHITE)
bbox = draw.textbbox((0, 0), "Gateway", font=node_font)
gh = bbox[3] - bbox[1]
sbbox = draw.textbbox((0, 0), "Smart Router", font=sub_node_font)
stw, sth = sbbox[2] - sbbox[0], sbbox[3] - sbbox[1]
draw.text((gx - stw // 2, gy + gh // 2 + 4), "Smart Router",
          font=sub_node_font, fill=BLACK)

# ═══ Watermark ═══
wm = "ai.acan.ccwu.cc"
wbbox = draw.textbbox((0, 0), wm, font=font_sm)
ww = wbbox[2] - wbbox[0]
draw.text((W - ww - 20, H - 26), wm, font=font_sm, fill=WATERMARK)

img.save(OUT, "JPEG", quality=92)
print(f"Saved {OUT} ({os.path.getsize(OUT)} bytes)")
