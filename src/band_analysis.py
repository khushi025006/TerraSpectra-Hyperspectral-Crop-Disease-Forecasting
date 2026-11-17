import numpy as np
import pandas as pd
from pathlib import Path

files = ["1797.npz", "1827.npz", "1855.npz"]

Path("reports").mkdir(exist_ok=True)

for name in files:

    image_id = name.replace(".npz", "")

    with np.load(Path("data/raw") / name) as data:
        cube = data["arr_0"].astype(np.float32)

    band_results = []

    for band in range(cube.shape[2]):

        band_data = cube[:, :, band]

        band_results.append({
            "band": band,
            "mean": float(np.mean(band_data)),
            "std": float(np.std(band_data)),
            "minimum": float(np.min(band_data)),
            "maximum": float(np.max(band_data))
        })

    df = pd.DataFrame(band_results)

    output = f"reports/{image_id}_band_analysis.csv"
    df.to_csv(output, index=False)

    print(f"\nImage: {image_id}")
    print("Total spectral bands:", len(df))
    print("\nTop 5 bands by standard deviation:")
    print(
        df.nlargest(5, "std").to_string(index=False)
    )

    print("\nSaved:", output)

print("\nBand analysis completed!")