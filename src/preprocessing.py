import logging
from pathlib import Path

import numpy as np


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

DATA_DIR = Path("data/raw")
OUTPUT_DIR = Path("data/processed")

SAMPLES = [1797, 1827, 1855]

LOWER_PERCENTILE = 1
UPPER_PERCENTILE = 99

EXPECTED_SHAPE = (512, 512, 204)


# --------------------------------------------------
# LOGGING
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("TerraSpectra.Preprocessing")


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

def load_cube(image_id):

    file_path = DATA_DIR / f"{image_id}.npz"

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    with np.load(file_path, allow_pickle=False) as data:
        cube = data["arr_0"].astype(np.float32)

    if cube.shape != EXPECTED_SHAPE:
        raise ValueError(
            f"Invalid cube shape for {image_id}: {cube.shape}"
        )

    return cube


# --------------------------------------------------
# BACKGROUND MASKING
# --------------------------------------------------

def create_background_mask(cube):

    finite_pixels = np.all(
        np.isfinite(cube),
        axis=2
    )

    nonzero_pixels = np.any(
        cube != 0,
        axis=2
    )

    mask = finite_pixels & nonzero_pixels

    return mask


# --------------------------------------------------
# INVALID VALUE HANDLING
# --------------------------------------------------

def clean_cube(cube):

    invalid_count = int(
        np.count_nonzero(~np.isfinite(cube))
    )

    cleaned = np.nan_to_num(
        cube,
        nan=0.0,
        posinf=0.0,
        neginf=0.0
    )

    return cleaned, invalid_count


# --------------------------------------------------
# SPECTRAL NORMALIZATION
# --------------------------------------------------

def normalize_cube(cube, mask):

    normalized = np.zeros(
        cube.shape,
        dtype=np.float32
    )

    lower_values = []
    upper_values = []

    for band_index in range(cube.shape[2]):

        band = cube[:, :, band_index]

        valid_values = band[mask]

        if valid_values.size == 0:
            lower_values.append(0.0)
            upper_values.append(0.0)
            continue

        lower = np.percentile(
            valid_values,
            LOWER_PERCENTILE
        )

        upper = np.percentile(
            valid_values,
            UPPER_PERCENTILE
        )

        lower_values.append(float(lower))
        upper_values.append(float(upper))

        if upper <= lower:
            continue

        normalized_band = np.clip(
            (band - lower) / (upper - lower),
            0.0,
            1.0
        )

        normalized[:, :, band_index] = np.where(
            mask,
            normalized_band,
            0.0
        )

    return (
        normalized,
        np.asarray(lower_values, dtype=np.float32),
        np.asarray(upper_values, dtype=np.float32)
    )


# --------------------------------------------------
# SAVE PROCESSED DATA
# --------------------------------------------------

def save_processed_data(
    image_id,
    normalized,
    mask,
    lower_values,
    upper_values,
    invalid_count
):

    output_path = OUTPUT_DIR / f"{image_id}_processed.npz"

    np.savez_compressed(
        output_path,
        cube=normalized,
        mask=mask,
        lower_percentiles=lower_values,
        upper_percentiles=upper_values,
        invalid_count=np.array(invalid_count),
        image_id=np.array(image_id),
        normalization_method=np.array(
            "Per-band percentile normalization (1-99)"
        )
    )

    logger.info("Processed data saved: %s", output_path)


# --------------------------------------------------
# PROCESS ONE IMAGE
# --------------------------------------------------

def process_image(image_id):

    logger.info("Processing image %s", image_id)

    cube = load_cube(image_id)

    logger.info("Original cube shape: %s", cube.shape)

    cleaned, invalid_count = clean_cube(cube)

    mask = create_background_mask(cleaned)

    valid_pixels = int(np.count_nonzero(mask))
    total_pixels = mask.size

    logger.info(
        "Valid foreground pixels: %s / %s",
        valid_pixels,
        total_pixels
    )

    logger.info(
        "Invalid numerical values detected: %s",
        invalid_count
    )

    normalized, lower, upper = normalize_cube(
        cleaned,
        mask
    )

    logger.info(
        "Normalized range: %.4f to %.4f",
        float(np.min(normalized)),
        float(np.max(normalized))
    )

    save_processed_data(
        image_id,
        normalized,
        mask,
        lower,
        upper,
        invalid_count
    )

    del cube, cleaned, normalized

    return {
        "image_id": image_id,
        "valid_pixels": valid_pixels,
        "total_pixels": int(total_pixels),
        "invalid_values": invalid_count
    }


# --------------------------------------------------
# MAIN PIPELINE
# --------------------------------------------------

def main():

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    logger.info("Starting TerraSpectra preprocessing")

    results = []

    for image_id in SAMPLES:

        result = process_image(image_id)

        results.append(result)

    logger.info("PREPROCESSING SUMMARY")

    for result in results:

        logger.info(
            "Image %s | Valid pixels: %s/%s | Invalid values: %s",
            result["image_id"],
            result["valid_pixels"],
            result["total_pixels"],
            result["invalid_values"]
        )

    logger.info(
        "All preprocessing operations completed successfully"
    )


if __name__ == "__main__":
    main()
