"""
TerraSpectra - Leaf Symptom Analysis

Purpose:
1. Identify the main tomato leaf.
2. Separate green, yellow and brown regions.
3. Calculate the percentage of each region.
4. Save visualizations and analysis results.
"""

import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

IMAGE_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "rgb"
    / "Alternaria_4th_trial"
    / "1971.png"
)

OUTPUT_DIR = PROJECT_ROOT / "results" / "symptom_analysis"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOAD IMAGE
# --------------------------------------------------

print("\nStarting TerraSpectra Leaf Symptom Analysis")

image = cv2.imread(str(IMAGE_PATH))

if image is None:
    raise FileNotFoundError(f"Image not found: {IMAGE_PATH}")

image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

print("Image loaded successfully!")
print("Image dimensions:", image.shape)


# --------------------------------------------------
# 3. IDENTIFY THE MAIN LEAF REGION
# --------------------------------------------------

# Create a colour-based candidate mask.

lower_leaf = np.array([0, 35, 25])
upper_leaf = np.array([100, 255, 255])

candidate_mask = cv2.inRange(
    hsv,
    lower_leaf,
    upper_leaf
)

# Define a polygon around the central leaf.
# This helps exclude neighbouring leaves.

roi_mask = np.zeros(image.shape[:2], dtype=np.uint8)

leaf_polygon = np.array([
    [65, 285],
    [85, 220],
    [120, 185],
    [145, 190],
    [165, 145],
    [260, 120],
    [350, 125],
    [470, 140],
    [435, 190],
    [395, 235],
    [385, 265],
    [355, 280],
    [385, 310],
    [385, 345],
    [345, 350],
    [330, 405],
    [300, 455],
    [240, 460],
    [170, 450],
    [115, 435],
    [80, 400]
], dtype=np.int32)

cv2.fillPoly(
    roi_mask,
    [leaf_polygon],
    255
)

# Keep only candidate leaf pixels inside the polygon.

candidate_mask = cv2.bitwise_and(
    candidate_mask,
    roi_mask
)

# Remove small noise.

kernel = np.ones((5, 5), np.uint8)

candidate_mask = cv2.morphologyEx(
    candidate_mask,
    cv2.MORPH_OPEN,
    kernel
)

candidate_mask = cv2.morphologyEx(
    candidate_mask,
    cv2.MORPH_CLOSE,
    kernel
)

# Find connected components.

number, labels, stats, centroids = (
    cv2.connectedComponentsWithStats(
        candidate_mask,
        connectivity=8
    )
)

if number <= 1:
    raise RuntimeError("No leaf region detected.")

# Select the largest connected region.

largest_component = 1 + np.argmax(
    stats[1:, cv2.CC_STAT_AREA]
)

leaf_mask = np.zeros(
    candidate_mask.shape,
    dtype=np.uint8
)

leaf_mask[labels == largest_component] = 255

leaf_pixels = leaf_mask > 0

total_leaf_pixels = np.count_nonzero(leaf_pixels)

if total_leaf_pixels == 0:
    raise RuntimeError("Leaf segmentation produced an empty mask.")

print("\nMain leaf segmentation completed!")
print("Main leaf pixels detected:", total_leaf_pixels)
# --------------------------------------------------
# 4. CLASSIFY LEAF COLOURS
# --------------------------------------------------

hue = hsv[:, :, 0]
saturation = hsv[:, :, 1]
value = hsv[:, :, 2]

# Initial colour-based rules.
# These are approximate visual categories, not
# medically confirmed disease measurements.

brown_mask = (
    (hue <= 25)
    & (saturation >= 35)
    & (value <= 180)
    & leaf_pixels
)

yellow_mask = (
    (hue >= 15)
    & (hue <= 38)
    & (saturation >= 35)
    & (value >= 60)
    & (~brown_mask)
    & leaf_pixels
)

green_mask = (
    (hue >= 30)
    & (hue <= 95)
    & (saturation >= 35)
    & (value >= 35)
    & (~brown_mask)
    & (~yellow_mask)
    & leaf_pixels
)

# Count pixels in each category.

green_pixels = np.count_nonzero(green_mask)
yellow_pixels = np.count_nonzero(yellow_mask)
brown_pixels = np.count_nonzero(brown_mask)

classified_pixels = (
    green_pixels + yellow_pixels + brown_pixels
)

other_pixels = total_leaf_pixels - classified_pixels


# --------------------------------------------------
# 5. CALCULATE PERCENTAGES
# --------------------------------------------------

green_percentage = (
    green_pixels / total_leaf_pixels
) * 100

yellow_percentage = (
    yellow_pixels / total_leaf_pixels
) * 100

brown_percentage = (
    brown_pixels / total_leaf_pixels
) * 100

other_percentage = (
    other_pixels / total_leaf_pixels
) * 100


# --------------------------------------------------
# 6. PRINT RESULTS
# --------------------------------------------------

print("\n========== LEAF SYMPTOM ANALYSIS ==========")

print(f"Total leaf pixels : {total_leaf_pixels}")

print(
    f"Green area        : {green_percentage:.2f}%"
)

print(
    f"Yellow area       : {yellow_percentage:.2f}%"
)

print(
    f"Brown area        : {brown_percentage:.2f}%"
)

print(
    f"Other area        : {other_percentage:.2f}%"
)

print("===========================================")


# --------------------------------------------------
# 7. CREATE VISUALIZATION
# --------------------------------------------------

# Green = green tissue
# Yellow = yellow-coloured region
# Red = brown-coloured region
# Black = background

symptom_map = np.zeros_like(image_rgb)

symptom_map[green_mask] = [0, 255, 0]

symptom_map[yellow_mask] = [255, 255, 0]

symptom_map[brown_mask] = [255, 0, 0]


# --------------------------------------------------
# 8. DISPLAY RESULTS
# --------------------------------------------------

fig, axes = plt.subplots(1, 3, figsize=(16, 6))

axes[0].imshow(image_rgb)
axes[0].set_title("Original Tomato Leaf")

axes[1].imshow(leaf_mask, cmap="gray")
axes[1].set_title("Detected Leaf Region")

axes[2].imshow(symptom_map)
axes[2].set_title("Colour-Based Region Analysis")

for ax in axes:
    ax.axis("off")

plt.tight_layout()

graph_path = OUTPUT_DIR / "1971_symptom_analysis.png"

plt.savefig(graph_path, dpi=300, bbox_inches="tight")

plt.show()


# --------------------------------------------------
# 9. SAVE LEAF MASK
# --------------------------------------------------

mask_path = OUTPUT_DIR / "1971_leaf_mask.png"

cv2.imwrite(str(mask_path), leaf_mask)


# --------------------------------------------------
# 10. SAVE NUMERICAL RESULTS
# --------------------------------------------------

results = pd.DataFrame({
    "Image_ID": [1971],
    "Total_Leaf_Pixels": [total_leaf_pixels],
    "Green_Percentage": [green_percentage],
    "Yellow_Percentage": [yellow_percentage],
    "Brown_Percentage": [brown_percentage],
    "Other_Percentage": [other_percentage]
})

csv_path = OUTPUT_DIR / "1971_symptom_results.csv"

results.to_csv(csv_path, index=False)


print("\nFiles saved successfully!")

print("Visualization:", graph_path)

print("Leaf mask:", mask_path)

print("CSV results:", csv_path)

print("\nTerraSpectra analysis completed!")