import numpy as np
from pathlib import Path

files = ["1797.npz", "1827.npz", "1855.npz"]

for name in files:
    path = Path("data/raw") / name

    print("\n" + "=" * 40)
    print("IMAGE:", name)

    try:
        with np.load(path, allow_pickle=False) as data:
            arr = data[data.files[0]]

            print("Shape:", arr.shape)
            print("Data type:", arr.dtype)
            print("Finite values:", np.isfinite(arr).sum())
            print("Total values:", arr.size)
            print("File size (MB):", round(path.stat().st_size / 1024**2, 2))

    except Exception as e:
        print("ERROR:", repr(e))
