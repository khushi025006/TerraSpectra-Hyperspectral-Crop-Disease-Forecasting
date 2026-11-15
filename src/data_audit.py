from pathlib import Path
from datetime import datetime
import json
import logging

import pandas as pd
import numpy as np


# ============================================================
# TERRASPECTRA - DATASET AUDIT MODULE
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = PROJECT_ROOT / "data" / "raw" / "metadata.tab"

REPORT_DIR = PROJECT_ROOT / "reports"

REPORT_DIR.mkdir(parents=True, exist_ok=True)

REPORT_PATH = REPORT_DIR / "data_audit_report.json"

REQUIRED_COLUMNS = [
    "image_id",
    "trial",
    "plant",
    "leaf",
    "part",
    "date",
    "imaging_distance",
    "integration_time",
    "weather"
]


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("TerraSpectra.DataAudit")


# ============================================================
# DATASET LOADER
# ============================================================

def load_metadata(file_path=DATA_PATH):

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"Metadata file not found: {file_path}"
        )

    logger.info("Loading hyperspectral metadata")

    dataframe = pd.read_csv(
        file_path,
        sep="\t"
    )

    logger.info(
        "Loaded %s records and %s columns",
        dataframe.shape[0],
        dataframe.shape[1]
    )

    return dataframe


# ============================================================
# SCHEMA VALIDATION
# ============================================================

def validate_schema(dataframe):

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in dataframe.columns
    ]

    extra_columns = [
        column
        for column in dataframe.columns
        if column not in REQUIRED_COLUMNS
    ]

    return {
        "valid": len(missing_columns) == 0,
        "missing_columns": missing_columns,
        "extra_columns": extra_columns,
        "total_columns": len(dataframe.columns)
    }


# ============================================================
# MISSING VALUE ANALYSIS
# ============================================================

def analyze_missing_values(dataframe):

    missing_count = dataframe.isnull().sum()

    missing_percentage = (
        missing_count / len(dataframe)
    ) * 100

    report = {}

    for column in dataframe.columns:

        report[column] = {
            "missing_count": int(
                missing_count[column]
            ),
            "missing_percentage": round(
                float(missing_percentage[column]), 2
            )
        }

    return report


# ============================================================
# DUPLICATE ANALYSIS
# ============================================================

def analyze_duplicates(dataframe):

    duplicate_rows = int(
        dataframe.duplicated().sum()
    )

    duplicate_image_ids = int(
        dataframe["image_id"].duplicated().sum()
    )

    return {
        "duplicate_rows": duplicate_rows,
        "duplicate_image_ids": duplicate_image_ids
    }


# ============================================================
# DATE ANALYSIS
# ============================================================

def analyze_dates(dataframe):

    dates = pd.to_datetime(
        dataframe["date"],
        errors="coerce"
    )

    valid_dates = dates.dropna()

    if valid_dates.empty:

        return {
            "valid_dates": 0,
            "invalid_dates": len(dataframe),
            "start_date": None,
            "end_date": None,
            "unique_dates": 0
        }

    return {
        "valid_dates": int(valid_dates.count()),
        "invalid_dates": int(dates.isna().sum()),
        "start_date": str(valid_dates.min().date()),
        "end_date": str(valid_dates.max().date()),
        "unique_dates": int(valid_dates.nunique())
    }


# ============================================================
# PLANT ANALYSIS
# ============================================================

def analyze_plants(dataframe):

    plant_counts = (
        dataframe["plant"]
        .value_counts()
        .to_dict()
    )

    return {
        "unique_plants": int(
            dataframe["plant"].nunique()
        ),
        "plant_record_counts": {
            str(key): int(value)
            for key, value in plant_counts.items()
        }
    }


# ============================================================
# TRIAL ANALYSIS
# ============================================================

def analyze_trials(dataframe):

    trial_counts = (
        dataframe["trial"]
        .value_counts()
        .sort_index()
        .to_dict()
    )

    return {
        "unique_trials": int(
            dataframe["trial"].nunique()
        ),
        "trial_record_counts": {
            str(key): int(value)
            for key, value in trial_counts.items()
        }
    }


# ============================================================
# IMAGING CONDITION ANALYSIS
# ============================================================

def analyze_imaging_conditions(dataframe):

    numerical_columns = [
        "imaging_distance",
        "integration_time"
    ]

    report = {}

    for column in numerical_columns:

        values = pd.to_numeric(
            dataframe[column],
            errors="coerce"
        )

        report[column] = {
            "mean": (
                round(float(values.mean()), 2)
                if values.notna().any()
                else None
            ),
            "median": (
                round(float(values.median()), 2)
                if values.notna().any()
                else None
            ),
            "minimum": (
                float(values.min())
                if values.notna().any()
                else None
            ),
            "maximum": (
                float(values.max())
                if values.notna().any()
                else None
            ),
            "missing": int(values.isna().sum())
        }

    return report


# ============================================================
# WEATHER ANALYSIS
# ============================================================

def analyze_weather(dataframe):

    weather_counts = (
        dataframe["weather"]
        .value_counts(dropna=False)
        .to_dict()
    )

    return {
        "unique_weather_conditions": int(
            dataframe["weather"].nunique()
        ),
        "weather_record_counts": {
            str(key): int(value)
            for key, value in weather_counts.items()
        }
    }


# ============================================================
# TEMPORAL PLANT TRACKING
# ============================================================

def analyze_temporal_tracking(dataframe):

    working = dataframe.copy()

    working["date"] = pd.to_datetime(
        working["date"],
        errors="coerce"
    )

    valid = working.dropna(
        subset=["date", "plant"]
    )

    tracking = (
        valid.groupby("plant")["date"]
        .agg(["min", "max", "nunique", "count"])
    )

    repeated_plants = tracking[
        tracking["nunique"] > 1
    ]

    return {
        "plants_with_multiple_observation_dates": int(
            len(repeated_plants)
        ),
        "plants_with_single_observation_date": int(
            len(tracking) - len(repeated_plants)
        ),
        "total_plant_groups": int(len(tracking)),
        "tracking_available": bool(
            len(repeated_plants) > 0
        )
    }


# ============================================================
# COMPLETE DATASET AUDIT
# ============================================================

def run_complete_audit(dataframe):

    logger.info("Starting complete dataset audit")

    schema = validate_schema(dataframe)

    if not schema["valid"]:
        raise ValueError(
            f"Invalid dataset schema: {schema}"
        )

    report = {

        "project": "TerraSpectra",

        "audit_timestamp": datetime.now().isoformat(),

        "dataset": {
            "rows": int(dataframe.shape[0]),
            "columns": int(dataframe.shape[1]),
            "memory_usage_bytes": int(
                dataframe.memory_usage(
                    deep=True
                ).sum()
            )
        },

        "schema_validation": schema,

        "missing_values": analyze_missing_values(
            dataframe
        ),

        "duplicates": analyze_duplicates(
            dataframe
        ),

        "date_analysis": analyze_dates(
            dataframe
        ),

        "plant_analysis": analyze_plants(
            dataframe
        ),

        "trial_analysis": analyze_trials(
            dataframe
        ),

        "imaging_conditions": analyze_imaging_conditions(
            dataframe
        ),

        "weather_analysis": analyze_weather(
            dataframe
        ),

        "temporal_tracking": analyze_temporal_tracking(
            dataframe
        )
    }

    return report


# ============================================================
# REPORT EXPORT
# ============================================================

def save_report(report, output_path=REPORT_PATH):

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False
        )

    logger.info(
        "Audit report saved to %s",
        output_path
    )


# ============================================================
# REPORT DISPLAY
# ============================================================

def display_summary(report):

    print("\n" + "=" * 60)

    print("TERRASPECTRA DATASET AUDIT SUMMARY")

    print("=" * 60)

    print(
        "Total records:",
        report["dataset"]["rows"]
    )

    print(
        "Total columns:",
        report["dataset"]["columns"]
    )

    print(
        "Schema valid:",
        report["schema_validation"]["valid"]
    )

    print(
        "Duplicate rows:",
        report["duplicates"]["duplicate_rows"]
    )

    print(
        "Duplicate image IDs:",
        report["duplicates"]["duplicate_image_ids"]
    )

    print(
        "Unique plants:",
        report["plant_analysis"]["unique_plants"]
    )

    print(
        "Unique trials:",
        report["trial_analysis"]["unique_trials"]
    )

    print(
        "Unique observation dates:",
        report["date_analysis"]["unique_dates"]
    )

    print(
        "Plants with multiple observation dates:",
        report["temporal_tracking"][
            "plants_with_multiple_observation_dates"
        ]
    )

    print("\nMissing value analysis:")

    for column, values in report["missing_values"].items():

        print(
            f"{column}: "
            f"{values['missing_count']} "
            f"({values['missing_percentage']}%)"
        )

    print("\n" + "=" * 60)


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():

    try:

        dataframe = load_metadata()

        report = run_complete_audit(
            dataframe
        )

        save_report(report)

        display_summary(report)

        logger.info(
            "Dataset audit completed successfully"
        )

    except Exception:

        logger.exception(
            "Dataset audit failed"
        )

        raise


if __name__ == "__main__":

    main()
