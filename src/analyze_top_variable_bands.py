import logging
from pathlib import Path

import pandas as pd


# Configuration
INPUT_FILE = Path("results/features/spectral_band_features.csv")
OUTPUT_DIR = Path("results/features")
OUTPUT_FILE = OUTPUT_DIR / "top_variable_bands.csv"

TOP_N = 10


# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("TerraSpectra.BandAnalysis")


def main():

    logger.info("Starting top variable band analysis")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(INPUT_FILE)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(INPUT_FILE)

    required_columns = ["image_id", "band", "mean", "std", "median"]

    if not all(column in df.columns for column in required_columns):
        raise ValueError("Required feature columns are missing")

    all_results = []

    for image_id, group in df.groupby("image_id"):

        top_bands = group.nlargest(TOP_N, "std").copy()

        top_bands["rank"] = range(1, len(top_bands) + 1)

        all_results.append(top_bands)

        print("\n" + "=" * 55)
        print(f"TOP {TOP_N} MOST VARIABLE BANDS - IMAGE {image_id}")
        print("=" * 55)

        print(
            top_bands[
                ["rank", "band", "mean", "std", "median"]
            ].to_string(index=False)
        )

    result_df = pd.concat(all_results, ignore_index=True)

    result_df.to_csv(OUTPUT_FILE, index=False)

    print("\n" + "=" * 55)
    print("TOP VARIABLE BAND ANALYSIS COMPLETED")
    print("=" * 55)

    print("Images analysed:", df["image_id"].nunique())
    print("Total selected bands:", len(result_df))
    print("Saved report:", OUTPUT_FILE)

    logger.info("Analysis completed successfully")


if __name__ == "__main__":
    main()