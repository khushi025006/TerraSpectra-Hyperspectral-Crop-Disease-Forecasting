import numpy as np
import pandas as pd
from pathlib import Path

files = ["1797.npz", "1827.npz", "1855.npz"]

results = []

for name in files:

    path = Path("data/raw") / name

    with np.load(path, allow_pickle=False) as data:
        cube = data["arr_0"].astype(np.float32)

    results.append({
        "image_id": name.replace(".npz", ""),
        "minimum": float(np.min(cube)),
        "maximum": float(np.max(cube)),
        "mean": float(np.mean(cube)),
        "standard_deviation": float(np.std(cube)),
        "median": float(np.median(cube))
    })

df = pd.DataFrame(results)

print("\nHYPERSPECTRAL STATISTICS")
print("=" * 70)
print(df.to_string(index=False))

Path("reports").mkdir(exist_ok=True)

df.to_csv(
    "reports/spectral_statistics.csv",
    index=False
)

print("\nReport saved: reports/spectral_statistics.csv")