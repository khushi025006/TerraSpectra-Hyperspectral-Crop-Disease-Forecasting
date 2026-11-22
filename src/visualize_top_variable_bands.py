import logging
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# Configuration
INPUT_FILE = Path("results/features/spectral_band_features.csv")
TOP_BANDS_FILE = Path("results/features/top_variable_bands.csv")
OUTPUT_DIR = Path("results/features/graphs")

IMAGES = [1797, 1827, 1855]
TOP_N = 10


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("TerraSpectra.TopBandsVisualization")


def main():

    logger.info("Starting top variable band visualization")

    df = pd.read_csv(INPUT_FILE)
    top_df = pd.read_csv(TOP_BANDS_FILE)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Plot standard deviation for all bands
    plt.figure(figsize=(14, 7))

    for image_id in IMAGES:

        subset = df[df["image_id"] == image_id]

        plt.plot(
            subset["band"],
            subset["std"],
            label=f"Image {image_id}"
        )

        top = top_df[top_df["image_id"] == image_id]

        plt.scatter(
            top["band"],
            top["std"],
            s=45,
            marker="o",
            label=f"Top 10 - {image_id}"
        )

    plt.title("Top Variable Spectral Bands Comparison")
    plt.xlabel("Spectral Band Index")
    plt.ylabel("Standard Deviation")
    plt.legend(ncol=2)
    plt.grid(alpha=0.3)
    plt.tight_layout()

    output = OUTPUT_DIR / "top_variable_bands_comparison.png"

    plt.savefig(output, dpi=300)
    plt.close()

    logger.info("Saved %s", output)

    # Create individual plots for each image
    for image_id in IMAGES:

        subset = df[df["image_id"] == image_id]
        top = top_df[top_df["image_id"] == image_id]

        plt.figure(figsize=(14, 6))

        plt.plot(
            subset["band"],
            subset["std"],
            label="Standard deviation"
        )

        plt.scatter(
            top["band"],
            top["std"],
            s=60,
            marker="o",
            label="Top 10 variable bands"
        )

        plt.title(
            f"Top Variable Spectral Bands - Image {image_id}"
        )

        plt.xlabel("Spectral Band Index")
        plt.ylabel("Standard Deviation")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()

        output = OUTPUT_DIR / f"{image_id}_top_variable_bands.png"

        plt.savefig(output, dpi=300)
        plt.close()

        logger.info("Saved %s", output)

    print("\nTop variable band visualizations completed!")

    print("\nGenerated files:")
    for file in OUTPUT_DIR.glob("*top_variable_bands*.png"):
        print(file)

    logger.info("Visualization completed successfully")


if __name__ == "__main__":
    main()