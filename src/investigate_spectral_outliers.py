import numpy as np
import pandas as pd
from pathlib import Path

images = ["1797", "1827", "1855"]
bands = [129, 192, 203]

results = []

for image in images:

    with np.load(Path("data/raw") / f"{image}.npz") as data:
        cube = data["arr_0"].astype(np.float32)

    for band in bands:

        values = cube[:, :, band].ravel()

        results.append({
            "image": image,
            "band": band,
            "minimum": np.min(values),
            "median": np.median(values),
            "p95": np.percentile(values, 95),
            "p99": np.percentile(values, 99),
            "maximum": np.max(values),
            "pixels_above_1": np.sum(values > 1),
            "pixels_above_10": np.sum(values > 10),
            "pixels_above_100": np.sum(values > 100)
        })

df = pd.DataFrame(results)

print("\nSPECTRAL OUTLIER INVESTIGATION")
print("=" * 100)
print(df.to_string(index=False))

df.to_csv(
    "reports/spectral_outlier_investigation.csv",
    index=False
)

print("\nReport saved successfully!")