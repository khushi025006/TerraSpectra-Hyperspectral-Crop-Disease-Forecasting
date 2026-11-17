import csv
import numpy as np
from pathlib import Path
from scipy import ndimage

BASE_DIR = Path(__file__).resolve().parent.parent
MASK_DIR = BASE_DIR / "results" / "segmentation"
REPORT_DIR = BASE_DIR / "reports"

REPORT_DIR.mkdir(exist_ok=True)

IMAGE_IDS = ["1797", "1827", "1855"]


def validate_mask(image_id):

    mask_path = MASK_DIR / f"{image_id}_mask.npy"

    if not mask_path.exists():
        raise FileNotFoundError(mask_path)

    mask = np.load(mask_path).astype(bool)

    height, width = mask.shape

    total_pixels = mask.size
    leaf_pixels = int(np.count_nonzero(mask))

    border = np.zeros(mask.shape, dtype=bool)
    border[:10, :] = True
    border[-10:, :] = True
    border[:, :10] = True
    border[:, -10:] = True

    border_pixels = int(np.count_nonzero(mask & border))

    labels, components = ndimage.label(
        mask,
        structure=np.ones((3, 3))
    )

    y, x = np.where(mask)

    if leaf_pixels:
        bbox = [
            int(x.min()), int(y.min()),
            int(x.max()), int(y.max())
        ]
    else:
        bbox = [None, None, None, None]

    return {
        "image_id": image_id,
        "height": height,
        "width": width,
        "leaf_pixels": leaf_pixels,
        "background_pixels": total_pixels - leaf_pixels,
        "leaf_area_percent": round(
            leaf_pixels / total_pixels * 100, 2
        ),
        "border_pixels": border_pixels,
        "border_percent": round(
            border_pixels / leaf_pixels * 100, 2
        ) if leaf_pixels else 0,
        "connected_components": int(components),
        "bbox_x_min": bbox[0],
        "bbox_y_min": bbox[1],
        "bbox_x_max": bbox[2],
        "bbox_y_max": bbox[3]
    }


def main():

    results = []

    for image_id in IMAGE_IDS:
        result = validate_mask(image_id)
        results.append(result)

        print(
            f"Image {image_id}: "
            f"Leaf area = {result['leaf_area_percent']}%, "
            f"Border = {result['border_percent']}%"
        )

    output_path = REPORT_DIR / "segmentation_validation.csv"

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=results[0].keys()
        )
        writer.writeheader()
        writer.writerows(results)

    print("\nValidation completed.")
    print("Report saved:", output_path)


if __name__ == "__main__":
    main()
