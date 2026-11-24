from pathlib import Path
import logging
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT / "results" / "comparative_temporal"
    / "comparative_rgb_features.csv"
)

OUTPUT_DIR = ROOT / "results" / "plant_level_temporal"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ============================================================
# HELPER FUNCTION
# ============================================================

def get_mode(series):
    """Return the most frequent non-empty value."""

    values = series.dropna().astype(str)

    if values.empty:
        return None

    modes = values.mode()

    return modes.iloc[0] if not modes.empty else None


# ============================================================
# MAIN ANALYSIS
# ============================================================

def main():

    logger.info("Starting plant-level temporal analysis")

    # --------------------------------------------------------
    # 1. LOAD DATASET
    # --------------------------------------------------------

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    data = pd.read_csv(
        INPUT_FILE,
        dtype={
            "image_id": "string",
            "plant": "string",
            "leaf": "string",
            "part": "string",
            "plant_group": "string"
        }
    )

    logger.info("Loaded %d image records", len(data))

    required_columns = [
        "image_id",
        "trial",
        "plant",
        "leaf",
        "part",
        "date",
        "plant_group",
        "weather",
        "imaging_distance",
        "integration_time"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    if data["image_id"].duplicated().any():
        raise ValueError("Duplicate image IDs detected.")

    data["date"] = pd.to_datetime(
        data["date"],
        errors="coerce"
    )

    if data["date"].isna().any():
        raise ValueError("Invalid or missing dates detected.")

    # --------------------------------------------------------
    # 2. IDENTIFY NUMERIC FEATURES
    # --------------------------------------------------------

    metadata_columns = {
        "image_id",
        "trial",
        "plant",
        "leaf",
        "part",
        "date",
        "plant_group",
        "weather",
        "imaging_distance",
        "integration_time"
    }

    feature_columns = [
        col for col in data.columns
        if col not in metadata_columns
    ]

    for col in feature_columns:
        data[col] = pd.to_numeric(
            data[col],
            errors="coerce"
        )

    if data[feature_columns].isna().any().any():
        raise ValueError(
            "Missing or invalid numeric feature values detected."
        )

    logger.info(
        "Numeric feature columns identified: %d",
        len(feature_columns)
    )

    # --------------------------------------------------------
    # 3. LEAF-PART DAILY AGGREGATION
    # --------------------------------------------------------

    logger.info(
        "Creating leaf-part daily summaries"
    )

    leaf_part_keys = [
        "plant_group",
        "plant",
        "trial",
        "leaf",
        "part",
        "date"
    ]

    leaf_part_records = []

    grouped = data.groupby(
        leaf_part_keys,
        dropna=False,
        sort=True
    )

    for keys, group in grouped:

        record = dict(
            zip(leaf_part_keys, keys)
        )

        # Number of original image captures
        record["capture_count"] = len(group)

        # Preserve original image IDs
        record["image_ids"] = ", ".join(
            group["image_id"].astype(str)
        )

        # Acquisition conditions
        record["imaging_distance_median"] = (
            group["imaging_distance"].median()
        )

        record["integration_time_median"] = (
            group["integration_time"].median()
        )

        record["weather"] = get_mode(
            group["weather"]
        )

        # Median of every numeric feature
        for feature in feature_columns:
            record[feature] = group[feature].median()

        leaf_part_records.append(record)

    leaf_part_df = pd.DataFrame(
        leaf_part_records
    )

    leaf_part_df["date"] = (
        leaf_part_df["date"].dt.strftime("%Y-%m-%d")
    )

    leaf_part_file = (
        OUTPUT_DIR / "leaf_part_daily_summary.csv"
    )

    leaf_part_df.to_csv(
        leaf_part_file,
        index=False
    )

    logger.info(
        "Leaf-part daily records: %d",
        len(leaf_part_df)
    )

    # --------------------------------------------------------
    # 4. PLANT DAILY AGGREGATION
    # --------------------------------------------------------

    logger.info(
        "Creating plant daily summaries"
    )

    plant_keys = [
        "plant_group",
        "plant",
        "trial",
        "date"
    ]

    plant_records = []

    grouped_plants = leaf_part_df.groupby(
        plant_keys,
        dropna=False,
        sort=True
    )

    for keys, group in grouped_plants:

        record = dict(
            zip(plant_keys, keys)
        )

        # Number of distinct leaf-part measurements
        record["leaf_part_count"] = len(group)

        # Total original captures represented
        record["total_capture_count"] = int(
            group["capture_count"].sum()
        )

        # Acquisition condition summaries
        record["imaging_distance_median"] = (
            group["imaging_distance_median"].median()
        )

        record["integration_time_median"] = (
            group["integration_time_median"].median()
        )

        record["weather"] = get_mode(
            group["weather"]
        )

        # Median across leaf-part daily measurements
        for feature in feature_columns:
            record[feature] = group[feature].median()

        plant_records.append(record)
    # Convert collected plant records into a DataFrame
    plant_df = pd.DataFrame(plant_records)

    plant_file = (
        OUTPUT_DIR / "plant_daily_summary.csv"
    )

    plant_df.to_csv(
        plant_file,
        index=False
    )

    # --------------------------------------------------------
    # 5. VALIDATION
    # --------------------------------------------------------

    logger.info("Validating aggregated datasets")

    if plant_df.duplicated(
        subset=["plant", "date"]
    ).any():
        raise ValueError(
            "Duplicate plant-date records detected."
        )

    if leaf_part_df.duplicated(
        subset=[
            "plant",
            "leaf",
            "part",
            "date"
        ]
    ).any():
        raise ValueError(
            "Duplicate leaf-part-date records detected."
        )

    if len(data) != leaf_part_df["capture_count"].sum():
        raise ValueError(
            "Capture counts do not match original records."
        )

    if len(leaf_part_df) != plant_df["leaf_part_count"].sum():
        raise ValueError(
            "Leaf-part aggregation counts do not match."
        )

    if len(data) != plant_df["total_capture_count"].sum():
        raise ValueError(
            "Plant-level capture totals do not match."
        )

    # --------------------------------------------------------
    # 6. GROUP DISTRIBUTION
    # --------------------------------------------------------

    print("\n" + "=" * 65)
    print("PLANT-LEVEL TEMPORAL ANALYSIS SUMMARY")
    print("=" * 65)

    print("\nORIGINAL DATASET")
    print("Image records:", len(data))

    print("\nLEAF-PART DAILY SUMMARY")
    print("Total records:", len(leaf_part_df))

    print("\nPLANT DAILY SUMMARY")
    print("Total records:", len(plant_df))

    print("\nPLANT GROUP DISTRIBUTION")

    print(
        plant_df.groupby("plant_group")["plant"]
        .nunique()
        .to_string()
    )

    print("\nPLANT-LEVEL DATE COVERAGE")

    coverage = (
        plant_df.groupby("plant")
        .agg(
            observation_dates=("date", "nunique"),
            first_date=("date", "min"),
            last_date=("date", "max")
        )
    )

    print(coverage.to_string())

    print("\nREPEATED CAPTURE GROUPS")

    repeated = leaf_part_df[
        leaf_part_df["capture_count"] > 1
    ]

    if repeated.empty:
        print("No repeated capture groups.")
    else:
        print(
            repeated[
                [
                    "plant",
                    "leaf",
                    "part",
                    "date",
                    "image_ids",
                    "capture_count"
                ]
            ].to_string(index=False)
        )

    print("\nOUTPUT FILES")
    print(leaf_part_file)
    print(plant_file)

    print("\nAll aggregation validations passed!")

    logger.info(
        "Plant-level temporal analysis completed successfully"
    )


# ============================================================
# EXECUTION
# ============================================================

if __name__ == "__main__":
    main()
