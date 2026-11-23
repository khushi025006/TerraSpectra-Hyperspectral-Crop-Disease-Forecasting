"""
TerraSpectra - Exploratory Temporal Analysis

Analyzes RGB feature changes across seven observations
and examines relationships with image capture conditions.

IMPORTANT:
All RGB features are whole-image measurements.
They are not validated leaf-specific disease severity labels.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# PATHS
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    ROOT / "results" / "temporal" /
    "combined_temporal_dataset.csv"
)

OUTPUT_FOLDER = (
    ROOT / "results" / "temporal" /
    "analysis"
)

GRAPH_FOLDER = OUTPUT_FOLDER / "graphs"

OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
GRAPH_FOLDER.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

TEMPORAL_FEATURES = [
    "red_mean",
    "green_mean",
    "blue_mean",
    "brightness_mean",
    "green_pixel_percent",
    "yellow_pixel_percent",
    "brown_pixel_percent",
    "texture_laplacian_variance",
    "edge_pixel_percent",
]

CAPTURE_FEATURES = [
    "imaging_distance",
    "integration_time",
]


# --------------------------------------------------
# LOAD AND VALIDATE DATA
# --------------------------------------------------

def load_data():

    print("\nLoading combined temporal dataset...")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Input dataset not found: {INPUT_FILE}"
        )

    df = pd.read_csv(INPUT_FILE)

    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    if df["date"].isna().any():
        raise ValueError("Invalid dates found in dataset.")

    required_columns = (
        TEMPORAL_FEATURES + CAPTURE_FEATURES
    )

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing required columns: {missing}"
        )

    df = df.sort_values("date").reset_index(drop=True)

    print(f"Observations loaded: {len(df)}")
    print(f"Features analyzed: {len(TEMPORAL_FEATURES)}")

    return df


# --------------------------------------------------
# TEMPORAL SUMMARY
# --------------------------------------------------

def generate_summary(df):

    print("\nGenerating temporal summary...")

    summary = df[
        ["image_id", "date"] + TEMPORAL_FEATURES
    ].copy()

    summary["date"] = summary["date"].dt.strftime(
        "%Y-%m-%d"
    )

    output = OUTPUT_FOLDER / "temporal_feature_summary.csv"

    summary.to_csv(output, index=False)

    print(f"Saved: {output}")


# --------------------------------------------------
# FEATURE TREND GRAPHS
# --------------------------------------------------

def plot_temporal_trends(df):

    print("\nGenerating temporal trend graphs...")

    for feature in TEMPORAL_FEATURES:

        plt.figure(figsize=(10, 5))

        plt.plot(
            df["date"],
            df[feature],
            marker="o",
            linewidth=2
        )

        plt.title(
            f"Temporal Trend of {feature.replace('_', ' ').title()}"
        )

        plt.xlabel("Observation Date")
        plt.ylabel(feature.replace("_", " ").title())

        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)
        plt.tight_layout()

        output = GRAPH_FOLDER / f"{feature}_temporal.png"

        plt.savefig(output, dpi=300)
        plt.close()

        print(f"Saved: {output.name}")


# --------------------------------------------------
# CAPTURE CONDITION GRAPHS
# --------------------------------------------------

def plot_capture_conditions(df):

    print("\nAnalyzing image capture conditions...")

    for feature in CAPTURE_FEATURES:

        plt.figure(figsize=(10, 5))

        plt.plot(
            df["date"],
            df[feature],
            marker="o",
            linewidth=2
        )

        plt.title(
            f"Temporal Change in {feature.replace('_', ' ').title()}"
        )

        plt.xlabel("Observation Date")
        plt.ylabel(feature.replace("_", " ").title())

        plt.xticks(rotation=45)
        plt.grid(alpha=0.3)
        plt.tight_layout()

        output = GRAPH_FOLDER / f"{feature}_temporal.png"

        plt.savefig(output, dpi=300)
        plt.close()

        print(f"Saved: {output.name}")


# --------------------------------------------------
# CORRELATION ANALYSIS
# --------------------------------------------------

def generate_correlations(df):

    print("\nCalculating exploratory correlations...")

    selected_columns = (
        TEMPORAL_FEATURES + CAPTURE_FEATURES
    )

    numeric_data = df[selected_columns].apply(
        pd.to_numeric,
        errors="coerce"
    )

    # Pearson correlation
    pearson = numeric_data.corr(method="pearson")

    pearson_file = OUTPUT_FOLDER / "pearson_correlations.csv"

    pearson.to_csv(pearson_file)

    # Spearman correlation
    spearman = numeric_data.corr(method="spearman")

    spearman_file = OUTPUT_FOLDER / "spearman_correlations.csv"

    spearman.to_csv(spearman_file)

    print(f"Saved: {pearson_file}")
    print(f"Saved: {spearman_file}")

    # Correlation heatmap
    plt.figure(figsize=(13, 10))

    plt.imshow(
        pearson,
        cmap="coolwarm",
        vmin=-1,
        vmax=1,
        aspect="auto"
    )

    plt.colorbar(label="Pearson Correlation")

    plt.xticks(
        range(len(pearson.columns)),
        pearson.columns,
        rotation=90
    )

    plt.yticks(
        range(len(pearson.index)),
        pearson.index
    )

    plt.title(
        "Exploratory Correlation Heatmap"
    )

    plt.tight_layout()

    heatmap_file = GRAPH_FOLDER / "correlation_heatmap.png"

    plt.savefig(heatmap_file, dpi=300)
    plt.close()

    print(f"Saved: {heatmap_file}")


# --------------------------------------------------
# CHANGE BETWEEN FIRST AND LAST OBSERVATION
# --------------------------------------------------

def calculate_feature_changes(df):

    print("\nCalculating first-to-last observation changes...")

    first = df.iloc[0]
    last = df.iloc[-1]

    results = []

    for feature in TEMPORAL_FEATURES:

        initial = float(first[feature])
        final = float(last[feature])

        absolute_change = final - initial

        if initial != 0:
            percentage_change = (
                absolute_change / abs(initial)
            ) * 100
        else:
            percentage_change = np.nan

        results.append({
            "feature": feature,
            "first_observation": initial,
            "last_observation": final,
            "absolute_change": absolute_change,
            "percentage_change": percentage_change,
        })

    changes = pd.DataFrame(results)

    output = OUTPUT_FOLDER / "first_last_feature_changes.csv"

    changes.to_csv(output, index=False)

    print(f"Saved: {output}")


# --------------------------------------------------
# MAIN
# --------------------------------------------------

def main():

    print("\n======================================")
    print(" TERRASPECTRA TEMPORAL ANALYSIS")
    print("======================================")

    df = load_data()

    generate_summary(df)

    plot_temporal_trends(df)

    plot_capture_conditions(df)

    generate_correlations(df)

    calculate_feature_changes(df)

    print("\n======================================")
    print(" TEMPORAL ANALYSIS COMPLETED")
    print("======================================")

    print(f"\nObservations analyzed: {len(df)}")

    print(f"\nReports saved in:\n{OUTPUT_FOLDER}")

    print(f"\nGraphs saved in:\n{GRAPH_FOLDER}")


if __name__ == "__main__":
    main()