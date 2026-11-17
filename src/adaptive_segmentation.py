import logging
from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt

from scipy import ndimage


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_DIR = BASE_DIR / "results" / "segmentation"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SELECTED_BANDS = {
    "1797": 114,
    "1827": 167,
    "1855": 182
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("TerraSpectra")


# --------------------------------------------------
# LOAD HYPERSPECTRAL IMAGE
# --------------------------------------------------

def load_band(image_id, band_index):

    file_path = RAW_DIR / f"{image_id}.npz"

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    with np.load(file_path) as data:
        cube = data["arr_0"]

        if cube.ndim != 3:
            raise ValueError(
                f"Unexpected cube dimensions: {cube.shape}"
            )

        if band_index >= cube.shape[2]:
            raise ValueError("Selected band does not exist.")

        band = cube[:, :, band_index].astype(np.float32)

    return band


# --------------------------------------------------
# NORMALIZATION
# --------------------------------------------------

def normalize_band(band):

    finite_mask = np.isfinite(band)

    if not np.any(finite_mask):
        raise ValueError("No finite pixels found.")

    values = band[finite_mask]

    lower = np.percentile(values, 1)
    upper = np.percentile(values, 99)

    if upper <= lower:
        raise ValueError("Invalid normalization range.")

    normalized = np.zeros(band.shape, dtype=np.float32)

    normalized[finite_mask] = np.clip(
        (band[finite_mask] - lower) / (upper - lower),
        0,
        1
    )

    return normalized, finite_mask


# --------------------------------------------------
# OTSU THRESHOLD
# --------------------------------------------------

def calculate_otsu_threshold(image, valid_mask):

    values = image[valid_mask]

    histogram, bin_edges = np.histogram(
        values,
        bins=256,
        range=(0, 1)
    )

    probabilities = histogram.astype(np.float64)
    probabilities /= probabilities.sum()

    bin_centers = (
        bin_edges[:-1] + bin_edges[1:]
    ) / 2

    cumulative_probability = np.cumsum(probabilities)

    cumulative_mean = np.cumsum(
        probabilities * bin_centers
    )

    total_mean = cumulative_mean[-1]

    denominator = (
        cumulative_probability *
        (1 - cumulative_probability)
    )

    numerator = (
        total_mean * cumulative_probability -
        cumulative_mean
    ) ** 2

    between_class_variance = np.zeros_like(numerator)

    valid = denominator > 0

    between_class_variance[valid] = (
        numerator[valid] / denominator[valid]
    )

    threshold_index = np.argmax(
        between_class_variance
    )

    return float(bin_centers[threshold_index])


# --------------------------------------------------
# MORPHOLOGICAL CLEANING
# --------------------------------------------------

def clean_mask(mask):

    structure = np.ones((3, 3), dtype=bool)

    mask = ndimage.binary_opening(
        mask,
        structure=structure
    )

    mask = ndimage.binary_closing(
        mask,
        structure=np.ones((7, 7), dtype=bool)
    )

    mask = ndimage.binary_fill_holes(mask)

    labels, number_of_components = ndimage.label(
        mask,
        structure=np.ones((3, 3), dtype=int)
    )

    if number_of_components == 0:
        return np.zeros(mask.shape, dtype=bool)

    component_sizes = np.bincount(labels.ravel())

    component_sizes[0] = 0

    largest_component = np.argmax(component_sizes)

    final_mask = labels == largest_component

    return final_mask


# --------------------------------------------------
# SEGMENTATION
# --------------------------------------------------

def segment_image(image_id, band_index):

    logger.info(
        "Starting segmentation | Image %s | Band %s",
        image_id,
        band_index
    )

    band = load_band(image_id, band_index)

    normalized, valid_mask = normalize_band(band)

    threshold = calculate_otsu_threshold(
        normalized,
        valid_mask
    )

    initial_mask = (
        (normalized > threshold) & valid_mask
    )

    final_mask = clean_mask(initial_mask)

    total_pixels = final_mask.size

    selected_pixels = int(
        np.count_nonzero(final_mask)
    )

    selected_percentage = (
        selected_pixels / total_pixels
    ) * 100

    logger.info("Otsu threshold: %.5f", threshold)

    logger.info(
        "Selected pixels: %s / %s (%.2f%%)",
        selected_pixels,
        total_pixels,
        selected_percentage
    )

    if selected_percentage < 5 or selected_percentage > 90:
        logger.warning(
            "Unusual segmentation area. Manual inspection required."
        )

    # Save numerical mask
    mask_path = OUTPUT_DIR / f"{image_id}_mask.npy"

    np.save(mask_path, final_mask)

    # Create visual overlay
    fig, axes = plt.subplots(
        1, 3,
        figsize=(15, 5)
    )

    low, high = np.percentile(
        band,
        [1, 99]
    )

    axes[0].imshow(
        band,
        cmap="gray",
        vmin=low,
        vmax=high
    )

    axes[0].set_title("Original spectral band")

    axes[1].imshow(
        final_mask,
        cmap="gray"
    )

    axes[1].set_title("Predicted leaf mask")

    axes[2].imshow(
        band,
        cmap="gray",
        vmin=low,
        vmax=high
    )

    axes[2].imshow(
        final_mask,
        cmap="spring",
        alpha=0.4
    )

    axes[2].set_title("Segmentation overlay")

    for ax in axes:
        ax.axis("off")

    fig.suptitle(
        f"TerraSpectra | Image {image_id} | Band {band_index}"
    )

    plt.tight_layout()

    figure_path = (
        OUTPUT_DIR / f"{image_id}_segmentation.png"
    )

    plt.savefig(
        figure_path,
        dpi=150,
        bbox_inches="tight"
    )

    plt.close(fig)

    logger.info("Mask saved: %s", mask_path)
    logger.info("Visualization saved: %s", figure_path)

    return {
        "image_id": image_id,
        "band": band_index,
        "threshold": threshold,
        "selected_pixels": selected_pixels,
        "selected_percentage": selected_percentage
    }


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    logger.info("TerraSpectra adaptive segmentation started")

    results = []

    for image_id, band_index in SELECTED_BANDS.items():

        try:
            result = segment_image(
                image_id,
                band_index
            )

            results.append(result)

        except Exception:
            logger.exception(
                "Segmentation failed for image %s",
                image_id
            )

    logger.info("------------------------------------")
    logger.info("SEGMENTATION SUMMARY")
    logger.info("------------------------------------")

    for result in results:

        logger.info(
            "Image %s | Band %s | Threshold %.5f | Area %.2f%%",
            result["image_id"],
            result["band"],
            result["threshold"],
            result["selected_percentage"]
        )

    logger.info(
        "Successfully processed %s of %s images",
        len(results),
        len(SELECTED_BANDS)
    )


if __name__ == "__main__":
    main()
