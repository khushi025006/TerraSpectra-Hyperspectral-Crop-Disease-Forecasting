from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import pandas as pd
import math

image_ids = ["1754", "1780", "1821", "1852", "1892", "1932", "1971"]

dates = [
    "04 July 2025",
    "07 July 2025",
    "10 July 2025",
    "14 July 2025",
    "17 July 2025",
    "21 July 2025",
    "24 July 2025"
]

root = Path("data/raw/rgb/Alternaria_4th_trial")
output = Path("results/temporal")
output.mkdir(parents=True, exist_ok=True)

thumb_width = 450
thumb_height = 350
label_height = 55
columns = 4
rows = math.ceil(len(image_ids) / columns)

sheet = Image.new(
    "RGB",
    (columns * thumb_width, rows * (thumb_height + label_height)),
    "white"
)

draw = ImageDraw.Draw(sheet)

for index, (image_id, date) in enumerate(zip(image_ids, dates)):
    image_path = root / f"{image_id}.png"

    with Image.open(image_path) as img:
        img = img.convert("RGB")
        img.thumbnail((thumb_width - 20, thumb_height - 20))

        x = (index % columns) * thumb_width
        y = (index // columns) * (thumb_height + label_height)

        position = (
            x + (thumb_width - img.width) // 2,
            y + (thumb_height - img.height) // 2
        )

        sheet.paste(img, position)

        draw.text(
            (x + 10, y + thumb_height + 5),
            f"Image {image_id} | {date}",
            fill="black"
        )

output_file = output / "028_I_leaf2_part7_contact_sheet.png"
sheet.save(output_file)

print("Contact sheet created successfully!")
print("Saved:", output_file)
print("Images included:", len(image_ids))
