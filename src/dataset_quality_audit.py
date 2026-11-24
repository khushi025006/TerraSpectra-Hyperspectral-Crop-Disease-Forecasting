from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parent.parent

METADATA_PATH = (
    PROJECT_ROOT / "data" / "processed"
    / "trial_4_temporal_metadata.csv"
)

SEQUENCES_PATH = (
    PROJECT_ROOT / "data" / "processed"
    / "trial_4_temporal_sequences.csv"
)

OUTPUT_DIR = PROJECT_ROOT / "results" / "dataset_quality_audit"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():

    print("\nTERRASPECTRA DATASET QUALITY AUDIT")
    print("=" * 45)

    metadata = pd.read_csv(METADATA_PATH)
    source_sequences = pd.read_csv(SEQUENCES_PATH)

    metadata["date"] = pd.to_datetime(metadata["date"])

    keys = ["trial", "plant", "leaf", "part"]

    # Basic metadata checks
    total_records = len(metadata)
    duplicate_ids = int(metadata["image_id"].duplicated().sum())
    missing_values = int(metadata.isnull().sum().sum())

    # Plant group distribution
    group_distribution = (
        metadata.groupby("plant_group")
        .size()
        .reset_index(name="image_count")
    )

    group_distribution.to_csv(
        OUTPUT_DIR / "plant_group_distribution.csv",
        index=False
    )

    # Build all metadata groups
    records = []

    for key, group in metadata.groupby(keys):

        date_counts = group.groupby("date").size()
        repeated_dates = date_counts[date_counts > 1]

        records.append({
            "trial": key[0],
            "plant": key[1],
            "leaf": key[2],
            "part": key[3],
            "plant_group": group["plant_group"].iloc[0],
            "image_count": len(group),
            "unique_dates": group["date"].nunique(),
            "repeated_capture_count": int(
                (repeated_dates - 1).sum()
            ),
            "repeated_capture_dates": "; ".join(
                date.strftime("%Y-%m-%d")
                for date in repeated_dates.index
            ),
            "first_date": group["date"].min().strftime("%Y-%m-%d"),
            "last_date": group["date"].max().strftime("%Y-%m-%d")
        })

    audit = pd.DataFrame(records)

    # Classify groups
    audit["group_type"] = audit["image_count"].apply(
        lambda count: (
            "single_observation"
            if count == 1
            else "repeated_observation"
        )
    )

    audit.to_csv(
        OUTPUT_DIR / "sequence_quality_audit.csv",
        index=False
    )

    # Save single-observation groups separately
    single_groups = audit[
        audit["group_type"] == "single_observation"
    ]

    single_groups.to_csv(
        OUTPUT_DIR / "single_observation_groups.csv",
        index=False
    )

    # Compare repeated-observation groups with source sequences
    repeated_groups = audit[
        audit["group_type"] == "repeated_observation"
    ]

    comparison = repeated_groups.merge(
        source_sequences[keys + ["image_count", "unique_dates"]],
        on=keys,
        how="outer",
        suffixes=("_calculated", "_source"),
        indicator=True
    )

    comparison["count_matches"] = (
        comparison["image_count_calculated"]
        == comparison["image_count_source"]
    )

    comparison["date_counts_match"] = (
        comparison["unique_dates_calculated"]
        == comparison["unique_dates_source"]
    )

    comparison.to_csv(
        OUTPUT_DIR / "sequence_validation.csv",
        index=False
    )

    # Summary statistics
    summary = {
        "total_metadata_records": total_records,
        "unique_image_ids": int(metadata["image_id"].nunique()),
        "duplicate_image_ids": duplicate_ids,
        "missing_values": missing_values,
        "unique_plants": int(metadata["plant"].nunique()),
        "total_metadata_groups": len(audit),
        "repeated_observation_groups": len(repeated_groups),
        "single_observation_groups": len(single_groups),
        "unique_dates": int(metadata["date"].nunique()),
        "repeated_capture_sequences": int(
            (audit["repeated_capture_count"] > 0).sum()
        ),
        "total_repeated_captures": int(
            audit["repeated_capture_count"].sum()
        ),
        "source_sequence_records": len(source_sequences),
        "sequence_count_mismatches": int(
            (~comparison["count_matches"]).sum()
        ),
        "sequence_date_mismatches": int(
            (~comparison["date_counts_match"]).sum()
        ),
        "start_date": metadata["date"].min().strftime("%Y-%m-%d"),
        "end_date": metadata["date"].max().strftime("%Y-%m-%d")
    }

    # Save summary
    with open(
        OUTPUT_DIR / "audit_summary.txt",
        "w",
        encoding="utf-8"
    ) as file:

        file.write("TERRASPECTRA DATASET QUALITY AUDIT\n")
        file.write("=" * 45 + "\n\n")

        for key, value in summary.items():
            file.write(f"{key}: {value}\n")

    # Display results
    print("\nOVERALL SUMMARY")

    for key, value in summary.items():
        print(f"{key}: {value}")

    print("\nPLANT GROUP DISTRIBUTION")
    print(group_distribution.to_string(index=False))

    print("\nGROUP CLASSIFICATION")
    print(audit["group_type"].value_counts().to_string())

    print("\nSEQUENCE VALIDATION")
    print(
        "Matching source records:",
        (comparison["_merge"] == "both").sum()
    )
    print(
        "Unmatched records:",
        (comparison["_merge"] != "both").sum()
    )

    print("\nReports saved to:")
    print(OUTPUT_DIR)

    print("\nDATASET QUALITY AUDIT COMPLETED")


if __name__ == "__main__":
    main()
