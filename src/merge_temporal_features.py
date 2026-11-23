"""
TerraSpectra - Merge RGB Temporal Features with Metadata
"""

from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

FEATURES_FILE = (
    ROOT / "results" / "temporal" / "rgb_temporal_features.csv"
)

METADATA_FILE = (
    ROOT / "data" / "processed" / "trial_4_temporal_metadata.csv"
)

OUTPUT_FILE = (
    ROOT / "results" / "temporal" / "combined_temporal_dataset.csv"
)


def main():

    print("\nLoading RGB temporal features...")
    features = pd.read_csv(
        FEATURES_FILE,
        dtype={"image_id": str}
    )

    print("Loading temporal metadata...")
    metadata = pd.read_csv(
        METADATA_FILE,
        dtype={"image_id": str}
    )

    metadata_columns = [
        "image_id",
        "trial",
        "plant",
        "leaf",
        "part",
        "date",
        "weather",
        "imaging_distance",
        "integration_time",
    ]

    missing = [
        col for col in metadata_columns
        if col not in metadata.columns
    ]

    if missing:
        raise ValueError(f"Missing metadata columns: {missing}")

    metadata = metadata[metadata_columns].copy()

    # Check duplicate IDs
    if features["image_id"].duplicated().any():
        raise ValueError("Duplicate IDs in feature dataset.")

    if metadata["image_id"].duplicated().any():
        raise ValueError("Duplicate IDs in metadata.")

    # Merge
    combined = pd.merge(
        features,
        metadata,
        on="image_id",
        how="left",
        suffixes=("_feature", "_metadata"),
        indicator=True,
        validate="one_to_one"
    )

    # Check matching
    unmatched = combined[combined["_merge"] != "both"]

    if not unmatched.empty:
        raise ValueError(
            "Unmatched image IDs:\n"
            + unmatched["image_id"].to_string(index=False)
        )

    # Keep metadata date as the final date
    combined = combined.drop(
        columns=["_merge", "date_feature"]
    )

    combined = combined.rename(
        columns={"date_metadata": "date"}
    )

    combined["date"] = pd.to_datetime(
        combined["date"],
        errors="coerce"
    )

    if combined["date"].isna().any():
        raise ValueError("Invalid dates found.")

    combined = combined.sort_values(
        "date"
    ).reset_index(drop=True)

    combined["date"] = combined["date"].dt.strftime(
        "%Y-%m-%d"
    )

    # Save
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    combined.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print("\nTEMPORAL DATASET MERGE SUMMARY")
    print("--------------------------------")
    print(f"RGB feature records: {len(features)}")
    print(f"Metadata records: {len(metadata)}")
    print(f"Combined records: {len(combined)}")
    print(f"Unmatched records: {len(unmatched)}")

    print(f"\nSaved: {OUTPUT_FILE}")

    print("\nCombined dataset preview:")

    print(
        combined[
            [
                "image_id",
                "date",
                "plant",
                "leaf",
                "part",
                "weather",
                "imaging_distance",
                "integration_time",
                "green_pixel_percent",
                "yellow_pixel_percent",
                "brown_pixel_percent",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()