"""
TerraSpectra - RGB Temporal Feature Extraction

Extracts whole-image colour, brightness, contrast, and texture features
from seven RGB observations of the same candidate plant/leaf region.

IMPORTANT:
These are whole-image descriptors, NOT validated leaf-specific disease
severity measurements.
"""

from pathlib import Path
import logging

import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# PATHS AND CONFIGURATION
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

RGB_FOLDER = ROOT / "data" / "raw" / "rgb" / "Alternaria_4th_trial"

OUTPUT_FOLDER = ROOT / "results" / "temporal"
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

OBSERVATIONS = [
    {"image_id": 1754, "date": "2025-07-04"},
    {"image_id": 1780, "date": "2025-07-07"},
    {"image_id": 1821, "date": "2025-07-10"},
    {"image_id": 1852, "date": "2025-07-14"},
    {"image_id": 1892, "date": "2025-07-17"},
    {"image_id": 1932, "date": "2025-07-21"},
    {"image_id": 1971, "date": "2025-07-24"},
]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# --------------------------------------------------
# IMAGE FEATURE EXTRACTION
# --------------------------------------------------

def extract_features(image_path, image_id, date):

    image = cv2.imread(str(image_path))

    if image is None:
        raise ValueError(f"Unable to read image: {image_path}")

    # Convert BGR to RGB and HSV
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    features = {
        "image_id": image_id,
        "date": date,
        "image_height": image.shape[0],
        "image_width": image.shape[1],
    }

    # RGB statistics
    for index, channel in enumerate(["red", "green", "blue"]):

        channel_data = rgb[:, :, index]

        features[f"{channel}_mean"] = float(np.mean(channel_data))
        features[f"{channel}_std"] = float(np.std(channel_data))
        features[f"{channel}_median"] = float(np.median(channel_data))

    # HSV statistics
    hsv_names = ["hue", "saturation", "value"]

    for index, channel in enumerate(hsv_names):

        channel_data = hsv[:, :, index]

        features[f"{channel}_mean"] = float(np.mean(channel_data))
        features[f"{channel}_std"] = float(np.std(channel_data))

    # Whole-image colour proportions
    total_pixels = image.shape[0] * image.shape[1]

    green_mask = (
        (hsv[:, :, 0] >= 25) &
        (hsv[:, :, 0] <= 95) &
        (hsv[:, :, 1] >= 35) &
        (hsv[:, :, 2] >= 30)
    )

    yellow_mask = (
        (hsv[:, :, 0] >= 15) &
        (hsv[:, :, 0] < 35) &
        (hsv[:, :, 1] >= 40)
    )

    brown_mask = (
        (hsv[:, :, 0] >= 5) &
        (hsv[:, :, 0] < 25) &
        (hsv[:, :, 1] >= 30) &
        (hsv[:, :, 2] < 180)
    )

    features["green_pixel_percent"] = (
        np.sum(green_mask) / total_pixels
    ) * 100

    features["yellow_pixel_percent"] = (
        np.sum(yellow_mask) / total_pixels
    ) * 100

    features["brown_pixel_percent"] = (
        np.sum(brown_mask) / total_pixels
    ) * 100

    # Brightness and contrast
    features["brightness_mean"] = float(np.mean(gray))
    features["brightness_std"] = float(np.std(gray))
    features["brightness_min"] = int(np.min(gray))
    features["brightness_max"] = int(np.max(gray))

    # Texture: Laplacian variance
    features["texture_laplacian_variance"] = float(
        cv2.Laplacian(gray, cv2.CV_64F).var()
    )

    # Edge density
    edges = cv2.Canny(gray, 100, 200)

    features["edge_pixel_percent"] = (
        np.count_nonzero(edges) / total_pixels
    ) * 100

    return features


# --------------------------------------------------
# PROCESS ALL OBSERVATIONS
# --------------------------------------------------

def main():

    logging.info("Starting RGB temporal feature extraction")

    all_features = []

    for observation in OBSERVATIONS:

        image_id = observation["image_id"]
        date = observation["date"]

        image_path = RGB_FOLDER / f"{image_id}.png"

        if not image_path.exists():
            logging.warning(
                "Image %s not found. Skipping.", image_id
            )
            continue

        logging.info("Processing image %s", image_id)

        try:
            features = extract_features(
                image_path,
                image_id,
                date
            )

            all_features.append(features)

            logging.info(
                "Successfully extracted features for %s",
                image_id
            )

        except Exception as error:
            logging.exception(
                "Failed to process image %s: %s",
                image_id,
                error
            )

    if not all_features:
        raise RuntimeError("No images were successfully processed.")

    dataframe = pd.DataFrame(all_features)

    dataframe["date"] = pd.to_datetime(dataframe["date"])

    dataframe = dataframe.sort_values("date")

    dataframe["date"] = dataframe["date"].dt.strftime("%Y-%m-%d")

    # Save CSV
    output_csv = OUTPUT_FOLDER / "rgb_temporal_features.csv"

    dataframe.to_csv(output_csv, index=False)

    logging.info("Saved features: %s", output_csv)

    # --------------------------------------------------
    # TEMPORAL VISUALIZATIONS
    # --------------------------------------------------

    graph_folder = OUTPUT_FOLDER / "graphs"
    graph_folder.mkdir(exist_ok=True)

    plot_columns = [
        "red_mean",
        "green_mean",
        "blue_mean",
        "brightness_mean",
        "green_pixel_percent",
        "yellow_pixel_percent",
        "brown_pixel_percent",
        "texture_laplacian_variance",
    ]

    for column in plot_columns:

        plt.figure(figsize=(10, 5))

        plt.plot(
            dataframe["date"],
            dataframe[column],
            marker="o",
            linewidth=2
        )

        plt.title(f"Temporal Trend: {column}")
        plt.xlabel("Observation Date")
        plt.ylabel(column.replace("_", " ").title())

        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        graph_path = graph_folder / f"{column}_trend.png"

        plt.savefig(graph_path, dpi=300)
        plt.close()

        logging.info("Saved graph: %s", graph_path)

    logging.info(
        "RGB temporal feature extraction completed. "
        "Images processed: %s",
        len(dataframe)
    )

    print("\nFEATURE EXTRACTION SUMMARY")
    print("--------------------------")
    print(f"Images processed: {len(dataframe)}")
    print(f"CSV saved: {output_csv}")
    print(f"Graphs saved: {graph_folder}")

    print("\nSelected feature results:")
    print(
        dataframe[
            [
                "image_id",
                "date",
                "green_pixel_percent",
                "yellow_pixel_percent",
                "brown_pixel_percent",
                "brightness_mean",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()