"""
TerraSpectra - Comparative RGB Feature Extraction

Purpose:
Extract RGB, HSV, colour, brightness, texture and edge features
from all Trial 4 RGB images (control and inoculated groups).

Groups:
028 - Inoculated
065 - Inoculated
K   - Control

IMPORTANT:
These are whole-image exploratory descriptors.
They are NOT validated leaf-specific disease severity measurements.
Green, yellow and brown masks are independent and may overlap.
"""

from pathlib import Path
import logging

import cv2
import numpy as np
import pandas as pd


# ==================================================
# 1. PATHS AND CONFIGURATION
# ==================================================

ROOT = Path(__file__).resolve().parents[1]

RGB_FOLDER = ROOT / "data" / "raw" / "rgb"

METADATA_FILE = (
    ROOT / "data" / "processed" /
    "trial_4_temporal_metadata.csv"
)

OUTPUT_FOLDER = (
    ROOT / "results" / "comparative_temporal"
)

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

OUTPUT_CSV = (
    OUTPUT_FOLDER / "comparative_rgb_features.csv"
)

FAILED_CSV = (
    OUTPUT_FOLDER / "failed_images.csv"
)

EXPECTED_IMAGES = 247


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# ==================================================
# 2. LOAD METADATA
# ==================================================

def load_metadata():

    logging.info("Loading Trial 4 metadata")

    if not METADATA_FILE.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {METADATA_FILE}"
        )

    metadata = pd.read_csv(
        METADATA_FILE,
        dtype={"image_id": "string"}
    )

    required_columns = [
        "image_id",
        "trial",
        "plant",
        "leaf",
        "part",
        "date",
        "imaging_distance",
        "integration_time",
        "weather",
        "plant_group"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in metadata.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing metadata columns: {missing_columns}"
        )

    metadata["image_id"] = (
        metadata["image_id"].astype(str).str.strip()
    )

    if metadata["image_id"].duplicated().any():
        raise ValueError(
            "Duplicate image IDs found in metadata."
        )

    metadata["date"] = pd.to_datetime(
        metadata["date"],
        errors="coerce"
    )

    if metadata["date"].isna().any():
        raise ValueError(
            "Invalid or missing dates found in metadata."
        )

    logging.info(
        "Metadata loaded: %s records",
        len(metadata)
    )

    return metadata


# ==================================================
# 3. FIND RGB IMAGES
# ==================================================

def find_rgb_images():

    logging.info("Searching for Trial 4 RGB images")

    image_files = sorted(
        RGB_FOLDER.glob("Alternaria_4th_*/*.png")
    )

    if not image_files:
        raise FileNotFoundError(
            "No Trial 4 RGB images found."
        )

    image_ids = [
        path.stem for path in image_files
    ]

    if len(image_ids) != len(set(image_ids)):
        raise ValueError(
            "Duplicate RGB image IDs found."
        )

    logging.info(
        "RGB images discovered: %s",
        len(image_files)
    )

    return image_files


# ==================================================
# 4. EXTRACT FEATURES FROM ONE IMAGE
# ==================================================

def extract_features(image_path):

    image = cv2.imread(
        str(image_path),
        cv2.IMREAD_COLOR
    )

    if image is None:
        raise ValueError(
            f"Unable to read image: {image_path}"
        )

    # Convert BGR to RGB, HSV and grayscale

    rgb = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2RGB
    )

    hsv = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2HSV
    )

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    height, width = image.shape[:2]

    total_pixels = height * width

    features = {
        "image_height": height,
        "image_width": width
    }

    # ----------------------------------------------
    # RGB STATISTICS
    # ----------------------------------------------

    channels = [
        "red",
        "green",
        "blue"
    ]

    for index, channel in enumerate(channels):

        channel_data = rgb[:, :, index]

        features[f"{channel}_mean"] = float(
            np.mean(channel_data)
        )

        features[f"{channel}_std"] = float(
            np.std(channel_data)
        )

        features[f"{channel}_median"] = float(
            np.median(channel_data)
        )

    # ----------------------------------------------
    # HSV STATISTICS
    # ----------------------------------------------

    hsv_names = [
        "hue",
        "saturation",
        "value"
    ]

    for index, channel in enumerate(hsv_names):

        channel_data = hsv[:, :, index]

        features[f"{channel}_mean"] = float(
            np.mean(channel_data)
        )

        features[f"{channel}_std"] = float(
            np.std(channel_data)
        )

        features[f"{channel}_median"] = float(
            np.median(channel_data)
        )

    # ----------------------------------------------
    # COLOUR INDICATORS
    # ----------------------------------------------

    hue = hsv[:, :, 0]
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]

    # OpenCV HSV hue range: 0-179

    green_mask = (
        (hue >= 25) &
        (hue <= 95) &
        (saturation >= 35) &
        (value >= 30)
    )

    yellow_mask = (
        (hue >= 15) &
        (hue < 35) &
        (saturation >= 40)
    )

    brown_mask = (
        (hue >= 5) &
        (hue < 25) &
        (saturation >= 30) &
        (value < 180)
    )

    features["green_pixel_percent"] = float(
        np.count_nonzero(green_mask)
        / total_pixels * 100
    )

    features["yellow_pixel_percent"] = float(
        np.count_nonzero(yellow_mask)
        / total_pixels * 100
    )

    features["brown_pixel_percent"] = float(
        np.count_nonzero(brown_mask)
        / total_pixels * 100
    )

    # ----------------------------------------------
    # BRIGHTNESS AND CONTRAST
    # ----------------------------------------------

    features["brightness_mean"] = float(
        np.mean(gray)
    )

    features["brightness_std"] = float(
        np.std(gray)
    )

    features["brightness_min"] = int(
        np.min(gray)
    )

    features["brightness_max"] = int(
        np.max(gray)
    )

    # ----------------------------------------------
    # TEXTURE
    # ----------------------------------------------

    laplacian = cv2.Laplacian(
        gray,
        cv2.CV_64F
    )

    features["texture_laplacian_variance"] = float(
        laplacian.var()
    )

    # ----------------------------------------------
    # EDGE DENSITY
    # ----------------------------------------------

    edges = cv2.Canny(
        gray,
        100,
        200
    )

    features["edge_pixel_percent"] = float(
        np.count_nonzero(edges)
        / total_pixels * 100
    )

    return features


# ==================================================
# 5. MAIN FEATURE EXTRACTION PIPELINE
# ==================================================

def main():

    logging.info(
        "Starting comparative RGB feature extraction"
    )

    metadata = load_metadata()

    image_files = find_rgb_images()

    # ----------------------------------------------
    # VERIFY IMAGE AND METADATA MATCHING
    # ----------------------------------------------

    metadata_ids = set(
        metadata["image_id"]
    )

    rgb_ids = {
        path.stem for path in image_files
    }

    missing_ids = metadata_ids - rgb_ids
    extra_ids = rgb_ids - metadata_ids

    print("\nIMAGE-METADATA VALIDATION")
    print("-------------------------")
    print("Metadata records:", len(metadata))
    print("RGB images:", len(image_files))
    print("Missing RGB images:", len(missing_ids))
    print("Extra RGB images:", len(extra_ids))

    if missing_ids or extra_ids:
        raise ValueError(
            "RGB and metadata IDs do not match."
        )

    if len(image_files) != EXPECTED_IMAGES:
        raise ValueError(
            f"Expected {EXPECTED_IMAGES} images, "
            f"found {len(image_files)}."
        )

    # ----------------------------------------------
    # IMAGE PROCESSING
    # ----------------------------------------------

    all_features = []
    failed_images = []

    for index, image_path in enumerate(
        image_files,
        start=1
    ):

        image_id = image_path.stem

        logging.info(
            "Processing image %s (%s/%s)",
            image_id,
            index,
            len(image_files)
        )

        try:

            features = extract_features(
                image_path
            )

            features["image_id"] = image_id

            all_features.append(features)

        except Exception as error:

            logging.exception(
                "Failed to process image %s",
                image_id
            )

            failed_images.append({
                "image_id": image_id,
                "error": str(error)
            })

    # ----------------------------------------------
    # CHECK PROCESSING RESULTS
    # ----------------------------------------------

    if failed_images:

        pd.DataFrame(
            failed_images
        ).to_csv(
            FAILED_CSV,
            index=False
        )

        raise RuntimeError(
            f"{len(failed_images)} images failed. "
            f"See: {FAILED_CSV}"
        )

    if len(all_features) != EXPECTED_IMAGES:

        raise RuntimeError(
            "Processed image count does not match "
            "expected image count."
        )

    # ----------------------------------------------
    # CREATE FEATURE DATAFRAME
    # ----------------------------------------------

    features_df = pd.DataFrame(
        all_features
    )

    features_df["image_id"] = (
        features_df["image_id"].astype(str)
    )

    # ----------------------------------------------
    # MERGE WITH METADATA
    # ----------------------------------------------

    final_df = metadata.merge(
        features_df,
        on="image_id",
        how="inner",
        validate="one_to_one"
    )

    if len(final_df) != EXPECTED_IMAGES:

        raise RuntimeError(
            "Unexpected row count after metadata merge."
        )

    # ----------------------------------------------
    # SORT RESULTS
    # ----------------------------------------------

    final_df = final_df.sort_values(
        [
            "plant_group",
            "plant",
            "date",
            "image_id"
        ]
    ).reset_index(drop=True)

    # Format dates for CSV

    final_df["date"] = (
        final_df["date"].dt.strftime("%Y-%m-%d")
    )

    # ----------------------------------------------
    # SAVE FINAL DATASET
    # ----------------------------------------------

    final_df.to_csv(
        OUTPUT_CSV,
        index=False
    )

    # ----------------------------------------------
    # PRINT SUMMARY
    # ----------------------------------------------

    print("\n" + "=" * 55)
    print("COMPARATIVE RGB FEATURE EXTRACTION SUMMARY")
    print("=" * 55)

    print("Total images processed:", len(final_df))

    print(
        "Total extracted features:",
        len(features_df.columns) - 1
    )

    print(
        "Total final columns:",
        len(final_df.columns)
    )

    print("\nPLANT GROUP DISTRIBUTION")

    print(
        final_df.groupby("plant_group")[
            "image_id"
        ].count().to_string()
    )

    print("\nPLANT DISTRIBUTION")

    print(
        final_df.groupby(
            ["plant_group", "plant"]
        )["image_id"].count().to_string()
    )

    print("\nFEATURE PREVIEW")

    preview_columns = [
        "image_id",
        "plant_group",
        "plant",
        "date",
        "red_mean",
        "green_mean",
        "blue_mean",
        "green_pixel_percent",
        "yellow_pixel_percent",
        "brown_pixel_percent",
        "brightness_mean"
    ]

    print(
        final_df[preview_columns]
        .head(10)
        .to_string(index=False)
    )

    print("\nOUTPUT FILE")
    print(OUTPUT_CSV)

    print("\nFailed images:", len(failed_images))

    print("\nFeature extraction completed successfully!")


# ==================================================
# 6. EXECUTION
# ==================================================

if __name__ == "__main__":

    main()