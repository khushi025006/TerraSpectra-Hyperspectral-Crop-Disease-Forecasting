"""
TerraSpectra - Hyperspectral Data Inspector

Purpose:
    Examine the internal structure of hyperspectral NPZ files.
"""

from pathlib import Path
import numpy as np


PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"


def inspect_hyperspectral_files():

    print("=" * 60)
    print("       TERRASPECTRA - HYPERSPECTRAL INSPECTOR")
    print("=" * 60)

    npz_files = sorted(RAW_DATA_DIR.glob("*.npz"))

    if not npz_files:
        print("No NPZ files found.")
        return

    for file_path in npz_files:

        print(f"\nFile: {file_path.name}")

        with np.load(file_path, allow_pickle=False) as data:

            print(f"Arrays available: {len(data.files)}")

            for array_name in data.files:

                array = data[array_name]

                print(f"\nArray name: {array_name}")
                print(f"Shape: {array.shape}")
                print(f"Dimensions: {array.ndim}")
                print(f"Data type: {array.dtype}")

                if np.issubdtype(array.dtype, np.number):
                    finite_values = array[np.isfinite(array)]

                    if finite_values.size:
                        print(f"Minimum value: {finite_values.min()}")
                        print(f"Maximum value: {finite_values.max()}")

    print("\nHyperspectral inspection completed.")


if __name__ == "__main__":
    inspect_hyperspectral_files()