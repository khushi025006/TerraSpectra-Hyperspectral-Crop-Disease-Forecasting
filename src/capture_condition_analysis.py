from pathlib import Path
import logging

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from scipy.stats import spearmanr


# --------------------------------------------------
# 1. PATH CONFIGURATION
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    ROOT_DIR / "results" /
    "plant_level_temporal" /
    "plant_daily_summary.csv"
)

OUTPUT_DIR = (
    ROOT_DIR / "results" /
    "capture_condition_analysis"
)

GRAPH_DIR = OUTPUT_DIR / "graphs"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
GRAPH_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOGGING
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# 3. LOAD DATA
# --------------------------------------------------

def load_data():

    logger.info("Loading plant-level dataset")

    df = pd.read_csv(INPUT_FILE)

    logger.info("Loaded %d records", len(df))

    required_columns = [
        "plant_group",
        "plant",
        "date",
        "imaging_distance_median",
        "integration_time_median",
        "weather",
        "red_mean",
        "green_mean",
        "blue_mean",
        "brightness_mean"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    numeric_columns = [
        "imaging_distance_median",
        "integration_time_median",
        "red_mean",
        "green_mean",
        "blue_mean",
        "brightness_mean"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    weather = df["weather"].fillna("").astype(str)

    df["weather_category"] = np.select(
        [
            weather.str.startswith("Sunny"),
            weather.str.startswith("Cloudy"),
            weather.str.startswith("Partly cloudy")
        ],
        [
            "Sunny",
            "Cloudy",
            "Partly Cloudy"
        ],
        default="Unknown"
    )

    logger.info("Dataset validation completed")

    return df


# --------------------------------------------------
# 4. SPEARMAN CORRELATIONS
# --------------------------------------------------

def calculate_correlations(df):

    logger.info("Calculating Spearman correlations")

    parameters = [
        "imaging_distance_median",
        "integration_time_median"
    ]

    features = [
        "red_mean",
        "green_mean",
        "blue_mean",
        "brightness_mean"
    ]

    records = []

    groups = [("ALL", df)]

    for group_name, group_df in df.groupby("plant_group"):
        groups.append((group_name, group_df))

    for group_name, group_df in groups:

        for parameter in parameters:

            for feature in features:

                valid = group_df[
                    [parameter, feature]
                ].dropna()

                correlation = np.nan
                p_value = np.nan

                if (
                    len(valid) >= 3
                    and valid[parameter].nunique() > 1
                    and valid[feature].nunique() > 1
                ):

                    result = spearmanr(
                        valid[parameter],
                        valid[feature]
                    )

                    correlation = result.statistic
                    p_value = result.pvalue

                records.append({
                    "Group": group_name,
                    "Acquisition_Parameter": parameter,
                    "Image_Feature": feature,
                    "Observations": len(valid),
                    "Spearman_Correlation": correlation,
                    "P_Value": p_value
                })

    result_df = pd.DataFrame(records)

    result_df.to_csv(
        OUTPUT_DIR / "capture_condition_correlations.csv",
        index=False
    )

    logger.info("Correlation report saved")

    return result_df


# --------------------------------------------------
# 5. WEATHER ANALYSIS
# --------------------------------------------------

def analyze_weather(df):

    logger.info("Analyzing weather conditions")

    summary = (
        df.groupby("weather_category")
        .agg(
            observations=("brightness_mean", "count"),
            mean_brightness=("brightness_mean", "mean"),
            median_brightness=("brightness_mean", "median"),
            std_brightness=("brightness_mean", "std")
        )
        .reset_index()
    )

    summary = summary.round(3)

    summary.to_csv(
        OUTPUT_DIR / "weather_brightness_summary.csv",
        index=False
    )

    return summary


# --------------------------------------------------
# 6. SCATTER PLOTS
# --------------------------------------------------

def create_scatter_plots(df):

    logger.info("Creating scatter plots")

    parameters = [
        "imaging_distance_median",
        "integration_time_median"
    ]

    features = [
        "red_mean",
        "green_mean",
        "blue_mean",
        "brightness_mean"
    ]

    for parameter in parameters:

        for feature in features:

            plot_df = df[
                [parameter, feature]
            ].dropna()

            if len(plot_df) < 3:
                continue

            plt.figure(figsize=(8, 6))

            plt.scatter(
                plot_df[parameter],
                plot_df[feature],
                alpha=0.7
            )

            plt.xlabel(parameter)
            plt.ylabel(feature)

            plt.title(
                f"{feature} vs {parameter}"
            )

            plt.grid(alpha=0.3)
            plt.tight_layout()

            plt.savefig(
                GRAPH_DIR /
                f"{feature}_vs_{parameter}.png",
                dpi=300
            )

            plt.close()

    logger.info("Scatter plots completed")


# --------------------------------------------------
# 7. WEATHER GRAPH
# --------------------------------------------------

def create_weather_plot(summary):

    plt.figure(figsize=(8, 6))

    plt.bar(
        summary["weather_category"],
        summary["mean_brightness"]
    )

    plt.xlabel("Weather Condition")
    plt.ylabel("Mean Brightness")

    plt.title(
        "Weather Condition vs Mean Image Brightness"
    )

    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        GRAPH_DIR / "weather_vs_brightness.png",
        dpi=300
    )

    plt.close()


# --------------------------------------------------
# 8. MAIN
# --------------------------------------------------

def main():

    logger.info("CAPTURE CONDITION ANALYSIS STARTED")

    df = load_data()

    correlations = calculate_correlations(df)

    weather_summary = analyze_weather(df)

    create_scatter_plots(df)

    create_weather_plot(weather_summary)

    logger.info("ANALYSIS COMPLETED SUCCESSFULLY")

    print("\n--- DATASET SUMMARY ---")
    print("Observations:", len(df))
    print("Unique plants:", df["plant"].nunique())

    print("\n--- CORRELATION RESULTS ---")
    print(correlations.to_string(index=False))

    print("\n--- WEATHER SUMMARY ---")
    print(weather_summary.to_string(index=False))

    print("\nOutput directory:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
