import logging
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

INPUT_FILE = Path(
    "results/plant_level_temporal/plant_daily_summary.csv"
)

OUTPUT_DIR = Path(
    "results/plant_level_temporal/graphs"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------
# FEATURES
# ---------------------------------------------------------

FEATURES = {
    "RGB Mean": [
        "red_mean",
        "green_mean",
        "blue_mean"
    ],

    "Colour Percentages": [
        "green_pixel_percent",
        "yellow_pixel_percent",
        "brown_pixel_percent"
    ],

    "Brightness": [
        "brightness_mean"
    ],

    "Image Texture": [
        "texture_laplacian_variance"
    ],

    "Edge Percentage": [
        "edge_pixel_percent"
    ]
}


GROUP_ORDER = ["028", "065", "K"]


# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

def load_data():

    logger.info("Loading plant-level temporal dataset")

    df = pd.read_csv(INPUT_FILE)

    df["date"] = pd.to_datetime(df["date"])

    logger.info("Loaded %d plant-date records", len(df))

    return df


# ---------------------------------------------------------
# INDIVIDUAL PLANT TRAJECTORIES
# ---------------------------------------------------------

def plot_individual_plants(df, feature):

    fig, ax = plt.subplots(figsize=(12, 7))

    for plant in sorted(df["plant"].unique()):

        plant_data = df[
            df["plant"] == plant
        ].sort_values("date")

        ax.plot(
            plant_data["date"],
            plant_data[feature],
            marker="o",
            linewidth=1.8,
            label=plant
        )

    ax.set_title(
        f"Individual Plant Temporal Trend: {feature}"
    )

    ax.set_xlabel("Observation Date")
    ax.set_ylabel(feature)

    ax.grid(True, alpha=0.3)

    ax.legend(
        title="Plant",
        bbox_to_anchor=(1.02, 1),
        loc="upper left"
    )

    fig.autofmt_xdate()
    fig.tight_layout()

    output_file = OUTPUT_DIR / (
        f"individual_{feature}.png"
    )

    fig.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    logger.info("Saved %s", output_file)


# ---------------------------------------------------------
# GROUP-LEVEL TEMPORAL TRENDS
# ---------------------------------------------------------

def plot_group_trends(df, feature):

    fig, ax = plt.subplots(figsize=(11, 7))

    for group in GROUP_ORDER:

        group_data = df[
            df["plant_group"] == group
        ]

        # First calculate the median across plants
        daily_median = (
            group_data.groupby("date")[feature]
            .median()
            .reset_index()
            .sort_values("date")
        )

        ax.plot(
            daily_median["date"],
            daily_median[feature],
            marker="o",
            linewidth=2,
            label=f"Group {group}"
        )

    ax.set_title(
        f"Exploratory Group-Level Trend: {feature}"
    )

    ax.set_xlabel("Observation Date")
    ax.set_ylabel(feature)

    ax.grid(True, alpha=0.3)

    ax.legend()

    fig.autofmt_xdate()
    fig.tight_layout()

    output_file = OUTPUT_DIR / (
        f"group_{feature}.png"
    )

    fig.savefig(
        output_file,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    logger.info("Saved %s", output_file)


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

def main():

    logger.info(
        "Starting plant-level temporal visualization"
    )

    df = load_data()

    all_features = []

    for feature_list in FEATURES.values():

        all_features.extend(feature_list)

    missing_features = [
        feature
        for feature in all_features
        if feature not in df.columns
    ]

    if missing_features:

        raise ValueError(
            f"Missing features: {missing_features}"
        )

    # Individual plant graphs
    logger.info("Generating individual plant trajectories")

    for feature in all_features:

        plot_individual_plants(
            df,
            feature
        )

    # Group-level exploratory graphs
    logger.info("Generating group-level temporal trends")

    for feature in all_features:

        plot_group_trends(
            df,
            feature
        )

    logger.info(
        "Generated %d graph files",
        len(all_features) * 2
    )

    print("\n" + "=" * 60)
    print("TEMPORAL VISUALIZATION COMPLETED")
    print("=" * 60)

    print("Plant-date observations:", len(df))
    print("Unique plants:", df["plant"].nunique())
    print("Features visualized:", len(all_features))
    print("Graphs generated:", len(all_features) * 2)

    print("\nOutput directory:")
    print(OUTPUT_DIR.resolve())


if __name__ == "__main__":

    main()