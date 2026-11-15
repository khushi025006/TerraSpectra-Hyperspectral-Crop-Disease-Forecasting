import logging
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("results/graphs")
METADATA_FILE = DATA_DIR / "metadata.tab"

SAMPLES = [1797, 1827, 1855]

# RGB band indices from dataset documentation
RGB_BANDS = [70, 53, 19]


# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("TerraSpectra")


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def load_metadata():
    metadata = pd.read_csv(METADATA_FILE, sep="\t")
    metadata["image_id"] = metadata["image_id"].astype(int)
    return metadata


def load_cube(image_id):
    file_path = DATA_DIR / f"{image_id}.npz"

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    with np.load(file_path, allow_pickle=False) as data:
        cube = data["arr_0"].astype(np.float32)

    if cube.shape != (512, 512, 204):
        raise ValueError(
            f"Unexpected shape for {image_id}: {cube.shape}"
        )

    return cube


def normalize_band(band):
    valid = np.isfinite(band)

    if not np.any(valid):
        return np.zeros(band.shape, dtype=np.float32)

    low, high = np.percentile(band[valid], [2, 98])

    if high <= low:
        return np.zeros(band.shape, dtype=np.float32)

    result = np.zeros(band.shape, dtype=np.float32)

    result[valid] = np.clip(
        (band[valid] - low) / (high - low),
        0,
        1
    )

    return result


# --------------------------------------------------
# RGB VISUALIZATION
# --------------------------------------------------

def create_rgb_image(cube, image_id):
    red = normalize_band(cube[:, :, RGB_BANDS[0]])
    green = normalize_band(cube[:, :, RGB_BANDS[1]])
    blue = normalize_band(cube[:, :, RGB_BANDS[2]])

    rgb = np.stack([red, green, blue], axis=-1)

    output_path = OUTPUT_DIR / f"{image_id}_rgb.png"

    plt.figure(figsize=(8, 8))
    plt.imshow(rgb)
    plt.title(f"TerraSpectra - Image {image_id}")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()

    logger.info("RGB image saved: %s", output_path)


# --------------------------------------------------
# SPECTRAL SIGNATURE
# --------------------------------------------------

def calculate_mean_spectrum(cube):
    valid_pixels = np.any(cube > 0, axis=2)

    pixels = cube[valid_pixels]

    if pixels.size == 0:
        raise ValueError("No valid pixels found.")

    return np.mean(pixels, axis=0, dtype=np.float64)


def create_spectral_graph(spectra, metadata, image_id):
    wavelengths = np.arange(1, len(spectra) + 1)

    row = metadata.loc[
        metadata["image_id"] == image_id
    ].iloc[0]

    label = f"Image {image_id} - Plant {row['plant']}"

    plt.figure(figsize=(12, 6))

    plt.plot(
        wavelengths,
        spectra,
        linewidth=1.5,
        label=label
    )

    plt.xlabel("Spectral Band")
    plt.ylabel("Mean Pixel Intensity")
    plt.title(f"Spectral Signature - {image_id}")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()

    output_path = OUTPUT_DIR / f"{image_id}_spectrum.png"

    plt.savefig(output_path, dpi=200)
    plt.close()

    logger.info("Spectral graph saved: %s", output_path)


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------

def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    metadata = load_metadata()

    logger.info("Starting spectral visualization pipeline")

    for image_id in SAMPLES:
        logger.info("Processing image %s", image_id)

        cube = load_cube(image_id)

        create_rgb_image(cube, image_id)

        spectrum = calculate_mean_spectrum(cube)

        create_spectral_graph(
            spectrum,
            metadata,
            image_id
        )

        del cube

    logger.info("All visualizations generated successfully")


if __name__ == "__main__":
    main()
