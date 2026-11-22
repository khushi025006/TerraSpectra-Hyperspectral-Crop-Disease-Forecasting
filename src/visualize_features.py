import logging
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# Configuration
INPUT_FILE = Path("results/features/spectral_band_features.csv")
OUTPUT_DIR = Path("results/features/graphs")

IMAGES = ["1797", "1827", "1855"]


# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("TerraSpectra.Visualization")


def main():

    logger.info("Starting spectral feature visualization")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(INPUT_FILE)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_FILE)

    # Graph 1: Mean spectral signatures
    plt.figure(figsize=(14, 6))

    for image_id in IMAGES:
        subset = df[df["image_id"] == int(image_id)]

        plt.plot(
            subset["band"],
            subset["mean"],
            label=f"Image {image_id}"
        )

    plt.title("Mean Spectral Signature Comparison")
    plt.xlabel("Spectral Band Index")
    plt.ylabel("Mean Normalized Reflectance")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    output = OUTPUT_DIR / "mean_spectral_signatures.png"
    plt.savefig(output, dpi=300)
    plt.close()

    logger.info("Saved %s", output)

    # Graph 2: Standard deviation comparison
    plt.figure(figsize=(14, 6))

    for image_id in IMAGES:
        subset = df[df["image_id"] == int(image_id)]

        plt.plot(
            subset["band"],
            subset["std"],
            label=f"Image {image_id}"
        )

    plt.title("Spectral Standard Deviation Comparison")
    plt.xlabel("Spectral Band Index")
    plt.ylabel("Standard Deviation")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    output = OUTPUT_DIR / "spectral_standard_deviation.png"
    plt.savefig(output, dpi=300)
    plt.close()

    logger.info("Saved %s", output)

    # Graph 3: Median spectral signatures
    plt.figure(figsize=(14, 6))

    for image_id in IMAGES:
        subset = df[df["image_id"] == int(image_id)]

        plt.plot(
            subset["band"],
            subset["median"],
            label=f"Image {image_id}"
        )

    plt.title("Median Spectral Signature Comparison")
    plt.xlabel("Spectral Band Index")
    plt.ylabel("Median Normalized Reflectance")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()

    output = OUTPUT_DIR / "median_spectral_signatures.png"
    plt.savefig(output, dpi=300)
    plt.close()

    logger.info("Saved %s", output)

    print("\nSpectral visualization completed successfully!")
    print("Generated graphs:")

    for file in OUTPUT_DIR.glob("*.png"):
        print(file)


if __name__ == "__main__":
    main()