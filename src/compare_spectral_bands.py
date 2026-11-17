import pandas as pd
from pathlib import Path

files = ["1797", "1827", "1855"]

for image in files:

    file_path = Path("reports") / f"{image}_band_analysis.csv"

    df = pd.read_csv(file_path)

    print("\n" + "=" * 45)
    print("IMAGE:", image)
    print("=" * 45)

    top_bands = df.nlargest(5, "std")

    print(top_bands[["band", "mean", "std"]].to_string(index=False))

print("\nComparison completed!")