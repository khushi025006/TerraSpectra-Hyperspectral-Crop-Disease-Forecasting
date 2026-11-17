import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

images = ["1797", "1827", "1855"]
bands = [192, 203]

output_dir = Path("results/spectral_outliers")
output_dir.mkdir(parents=True, exist_ok=True)

for image in images:

    with np.load(Path("data/raw") / f"{image}.npz") as data:
        cube = data["arr_0"].astype(np.float32)

    for band in bands:

        band_data = cube[:, :, band]

        outlier_mask = band_data > 100

        fig, axes = plt.subplots(1, 2, figsize=(11, 5))

        axes[0].imshow(band_data, cmap="gray", vmin=0,
                       vmax=np.percentile(band_data, 99))
        axes[0].set_title(f"Image {image} - Band {band}")

        axes[1].imshow(outlier_mask, cmap="gray")
        axes[1].set_title("Pixels above 100")

        for ax in axes:
            ax.axis("off")

        plt.tight_layout()

        save_path = output_dir / f"{image}_band_{band}_outliers.png"

        plt.savefig(save_path, dpi=150)
        plt.close()

        print("Saved:", save_path)

print("\nOutlier visualization completed!")