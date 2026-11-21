import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

images = ["1797", "1827", "1855"]
bands = [192, 203]

df = pd.read_csv("reports/extreme_pixel_locations.csv")

output_dir = Path("results/spectral_outliers")
output_dir.mkdir(parents=True, exist_ok=True)

for image in images:

    fig, axes = plt.subplots(1, 2, figsize=(12, 6))

    for ax, band in zip(axes, bands):

        subset = df[
            (df["image"].astype(str) == image) &
            (df["band"] == band)
        ]

        ax.scatter(
            subset["column"],
            subset["row"],
            s=8,
            marker="s"
        )

        ax.set_title(
            f"Image {image} - Band {band}"
        )

        ax.set_xlabel("Column")
        ax.set_ylabel("Row")

        ax.set_xlim(0, 511)
        ax.set_ylim(511, 0)

        ax.grid(alpha=0.2)

    plt.suptitle(
        f"Extreme Pixel Spatial Distribution - Image {image}"
    )

    plt.tight_layout()

    output_path = output_dir / f"{image}_extreme_pixel_distribution.png"

    plt.savefig(output_path, dpi=200)
    plt.close()

    print(f"Saved: {output_path}")

print("\nAll spatial visualisations generated successfully!")
