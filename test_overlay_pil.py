from PIL import Image, ImageDraw
import os

PLAYER_IMG = "assets/player_v6/front.png"
TOP_IMG = "assets/v10_items/top_1.png"
BOTTOM_IMG = "assets/v10_items/bottom_1.png"

base = Image.open(PLAYER_IMG).convert("RGBA")
base_w, base_h = base.size

# Let's define manual config for front view
cfg = {
    "top": {"scale_w": 0.50, "y_rel": 0.47},
    "bottom": {"scale_w": 0.45, "y_rel": 0.60}
}

top = Image.open(TOP_IMG).convert("RGBA")
tw, th = top.size
top_new_w = int(base_w * cfg["top"]["scale_w"])
top_new_h = int(th * (top_new_w / tw))
top = top.resize((top_new_w, top_new_h), Image.Resampling.LANCZOS)

bot = Image.open(BOTTOM_IMG).convert("RGBA")
bw, bh = bot.size
bot_new_w = int(base_w * cfg["bottom"]["scale_w"])
bot_new_h = int(bh * (bot_new_w / bw))
bot = bot.resize((bot_new_w, bot_new_h), Image.Resampling.LANCZOS)

out = base.copy()

# Add top
top_x = (base_w - top_new_w) // 2
top_y = int(base_h * cfg["top"]["y_rel"])
out.paste(top, (top_x, top_y), top)

# Add bottom
bot_x = (base_w - bot_new_w) // 2
bot_y = int(base_h * cfg["bottom"]["y_rel"])
out.paste(bot, (bot_x, bot_y), bot)

# Add a red crosshair at the center of the image to debug
draw = ImageDraw.Draw(out)
draw.line((base_w//2, 0, base_w//2, base_h), fill="red")
out.save("/Users/son-yongseok/.gemini/antigravity/brain/4443f849-2af1-4133-a0e2-bc6fa37b30e3/overlay_test1.png")
print("Overlay test saved.")
