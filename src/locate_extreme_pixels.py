import numpy as np
import pandas as pd
from pathlib import Path

images = ["1797", "1827", "1855"]
bands = [192, 203]

results = []

for image in images:

    print(f"\nAnalyzing Image: {image}")

    with np.load(Path("data/raw") / f"{image}.npz") as data:
        cube = data["arr_0"].astype(np.float32)

    for band in bands:

        band_data = cube[:, :, band]

        rows, cols = np.where(band_data > 100)

        print(f"\nBand {band}")
        print(f"Extreme pixels found: {len(rows)}")

        for row, col in zip(rows, cols):

            intensity = band_data[row, col]

            results.append({
                "image": image,
                "band": band,
                "row": int(row),
                "column": int(col),
                "intensity": float(intensity)
            })

df = pd.DataFrame(results)

output_path = Path("reports/extreme_pixel_locations.csv")

df.to_csv(output_path, index=False)

print("\n" + "=" * 60)
print("EXTREME PIXEL LOCATION ANALYSIS")
print("=" * 60)

print(f"Total extreme pixels: {len(df)}")
print(f"Report saved to: {output_path}")

if not df.empty:
    print("\nFirst 10 extreme pixels:")
    print(df.head(10).to_string(index=False))
else:
    print("\nNo extreme pixels found.")