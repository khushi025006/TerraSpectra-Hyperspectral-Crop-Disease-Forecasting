import json
from pathlib import Path

import pandas as pd


# Project directories
ROOT = Path(__file__).resolve().parent.parent

RESULTS = ROOT / "results"
OUTPUT = ROOT / "frontend" / "public" / "data" / "dashboard_summary.json"


# Source CSV files
GROUP_FILE = (
    RESULTS / "dataset_quality_audit" /
    "plant_group_distribution.csv"
)

VALIDATION_FILE = (
    RESULTS / "dataset_quality_audit" /
    "sequence_validation.csv"
)

PLANT_DAILY_FILE = (
    RESULTS / "plant_level_temporal" /
    "plant_daily_summary.csv"
)

LEAF_PART_FILE = (
    RESULTS / "plant_level_temporal" /
    "leaf_part_daily_summary.csv"
)


def main():

    print("\n===== TERRASPECTRA DASHBOARD DATA EXPORT =====")

    # Check source files
    source_files = [
        GROUP_FILE,
        VALIDATION_FILE,
        PLANT_DAILY_FILE,
        LEAF_PART_FILE,
    ]

    for file in source_files:
        if not file.exists():
            raise FileNotFoundError(
                f"Required dataset not found: {file}"
            )

    # Load actual research data
    groups = pd.read_csv(GROUP_FILE)
    validation = pd.read_csv(VALIDATION_FILE)
    plant_daily = pd.read_csv(PLANT_DAILY_FILE)
    leaf_part_daily = pd.read_csv(LEAF_PART_FILE)

    # Plant group distribution
    distribution = [
        {
            "group": (
                "Control K" if str(row["plant_group"]) == "K"
                else f"Group {row['plant_group']}"
            ),
            "images": int(row["image_count"]),
        }
        for _, row in groups.iterrows()
    ]

    # Validation statistics
    total_sequences = len(validation)

    image_matches = int(
        validation["count_matches"].astype(str)
        .str.lower().eq("true").sum()
    )

    date_matches = int(
        validation["date_counts_match"].astype(str)
        .str.lower().eq("true").sum()
    )

    image_mismatches = total_sequences - image_matches
    date_mismatches = total_sequences - date_matches

    repeated_captures = int(
        validation["repeated_capture_count"].sum()
    )

    # Unique biological plants
       # Unique biological plants
    unique_plants = validation["plant"].dropna().astype(str).nunique()

    # Dashboard summary
    dashboard_data = {        "dataset": {
            "name": "Trial 4 Dataset",
            "total_images": int(groups["image_count"].sum()),
            "monitored_plants": int(unique_plants),
            "plant_groups": int(groups["plant_group"].nunique()),
            "plant_day_records": int(len(plant_daily)),
            "leaf_part_records": int(len(leaf_part_daily)),
        },

        "plant_group_distribution": distribution,

        "validation": {
            "total_sequences": int(total_sequences),
            "image_count_matches": image_matches,
            "date_count_matches": date_matches,
            "image_count_mismatches": image_mismatches,
            "date_count_mismatches": date_mismatches,
            "repeated_captures": repeated_captures,
        },
    }

    # Export JSON
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT, "w", encoding="utf-8") as file:
        json.dump(
            dashboard_data,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print("\nExport successful!")

    print(f"Total images: {dashboard_data['dataset']['total_images']}")
    print(f"Unique plants: {unique_plants}")
    print(f"Plant groups: {len(distribution)}")
    print(f"Observation sequences: {total_sequences}")
    print(f"Repeated captures: {repeated_captures}")

    print(f"\nJSON saved to:\n{OUTPUT}")


if __name__ == "__main__":
    main()