import sys
import base64

# Read splash_logo.png and convert indexed/palette with (40,40,40) to RGBA transparent PNG
# Using PIL or pure Python
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

img = Image.open(r'E:\AI_Projects\## REA (Reverse Engineering Anything)\.agents\splash_logo.png').convert("RGBA")
datas = img.getdata()

new_data = []
# Background color is (40, 40, 40)
for item in datas:
    # If pixel is close to (40, 40, 40), make it completely transparent
    r, g, b, a = item
    if abs(r - 40) <= 5 and abs(g - 40) <= 5 and abs(b - 40) <= 5:
        new_data.append((0, 0, 0, 0))
    else:
        new_data.append((r, g, b, 255))

img.putdata(new_data)
out_path = r'E:\AI_Projects\## REA (Reverse Engineering Anything)\.agents\splash_logo_transparent.png'
img.save(out_path, "PNG")

# Convert to base64
with open(out_path, "rb") as f:
    b64_str = base64.b64encode(f.read()).decode('utf-8')

print("Created transparent PNG! Length of Base64:", len(b64_str))
with open(r'E:\AI_Projects\## REA (Reverse Engineering Anything)\.agents\transparent_logo_b64.txt', 'w', encoding='utf-8') as f:
    f.write("data:image/png;base64," + b64_str)
print("Saved transparent_logo_b64.txt")
