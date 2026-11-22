import logging
from pathlib import Path

import numpy as np
import pandas as pd


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

IMAGES = ["1797", "1827", "1855"]

PROCESSED_DIR = Path("data/processed")
MASK_DIR = Path("results/segmentation")
OUTPUT_DIR = Path("results/features")

EXPECTED_SHAPE = (512, 512, 204)


# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("TerraSpectra.FeatureExtraction")


# --------------------------------------------------
# FEATURE EXTRACTION
# --------------------------------------------------

def extract_features(image_id):

    logger.info("Processing image %s", image_id)

    processed_path = (
        PROCESSED_DIR / f"{image_id}_processed.npz"
    )

    mask_path = MASK_DIR / f"{image_id}_mask.npy"

    if not processed_path.exists():
        raise FileNotFoundError(processed_path)

    if not mask_path.exists():
        raise FileNotFoundError(mask_path)

    # Load processed hyperspectral cube
    with np.load(processed_path) as data:
        cube = data["cube"].astype(np.float32)

    # Load external leaf segmentation mask
    mask = np.load(mask_path).astype(bool)

    # Validate dimensions
    if cube.shape != EXPECTED_SHAPE:
        raise ValueError(
            f"Unexpected cube shape: {cube.shape}"
        )

    if mask.shape != cube.shape[:2]:
        raise ValueError(
            f"Mask shape mismatch for image {image_id}"
        )

    if not mask.any():
        raise ValueError(
            f"Empty leaf mask for image {image_id}"
        )

    # Select only leaf pixels
    leaf_spectra = cube[mask]

    if not np.isfinite(leaf_spectra).all():
        raise ValueError(
            f"Non-finite values found in image {image_id}"
        )

    logger.info(
        "Leaf pixels selected: %s",
        leaf_spectra.shape[0]
    )

    # Calculate spectral statistics for all 204 bands
    band_features = []

    for band_index in range(cube.shape[2]):

        values = leaf_spectra[:, band_index]

        band_features.append({
            "image_id": image_id,
            "band": band_index,
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "median": float(np.median(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "p10": float(np.percentile(values, 10)),
            "p90": float(np.percentile(values, 90))
        })

    # Calculate image-level summary
    image_features = {
        "image_id": image_id,
        "leaf_pixels": int(mask.sum()),
        "background_pixels": int(mask.size - mask.sum()),
        "leaf_coverage_percent": float(mask.mean() * 100),
        "spectral_bands": int(cube.shape[2]),
        "overall_mean": float(np.mean(leaf_spectra)),
        "overall_std": float(np.std(leaf_spectra)),
        "overall_median": float(np.median(leaf_spectra))
    }

    logger.info(
        "Feature extraction completed for image %s",
        image_id
    )

    del cube, leaf_spectra

    return band_features, image_features


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    all_band_features = []
    all_image_features = []

    logger.info("Starting TerraSpectra feature extraction")

    for image_id in IMAGES:

        band_features, image_features = extract_features(
            image_id
        )

        all_band_features.extend(band_features)
        all_image_features.append(image_features)

    # Convert results into DataFrames
    band_df = pd.DataFrame(all_band_features)

    image_df = pd.DataFrame(all_image_features)

    # Save feature datasets
    band_output = (
        OUTPUT_DIR / "spectral_band_features.csv"
    )

    image_output = (
        OUTPUT_DIR / "image_level_features.csv"
    )

    band_df.to_csv(band_output, index=False)

    image_df.to_csv(image_output, index=False)

    # Final summary
    print("\n" + "=" * 60)
    print("TERRASPECTRA FEATURE EXTRACTION SUMMARY")
    print("=" * 60)

    print("\nImages processed:", len(IMAGES))

    print("Total spectral features:", len(band_df))

    print("Features per image:", len(band_df) // len(IMAGES))

    print("\nImage-level summary:")
    print(image_df.to_string(index=False))

    print("\nSaved files:")
    print(band_output)
    print(image_output)

    logger.info("Feature extraction completed successfully")


if __name__ == "__main__":
    main()