"""
TerraSpectra - Hyperspectral Dataset Inspector

Purpose:
    Inspect downloaded dataset files and identify their formats,
    file sizes, and availability.
"""

from pathlib import Path


# Project directory
PROJECT_DIR = Path(__file__).resolve().parent.parent

# Raw dataset directory
RAW_DATA_DIR = PROJECT_DIR / "data" / "raw"


def inspect_dataset():
    """Inspect files available in the raw dataset directory."""

    print("=" * 55)
    print("       TERRASPECTRA - DATASET INSPECTOR")
    print("=" * 55)

    print(f"\nDataset location: {RAW_DATA_DIR}")

    # Check whether the directory exists
    if not RAW_DATA_DIR.exists():
        print("\nERROR: Raw dataset directory does not exist.")
        return

    # Find all files
    dataset_files = [
        file for file in RAW_DATA_DIR.rglob("*")
        if file.is_file()
    ]

    if not dataset_files:
        print("\nNo dataset files found.")
        print("Please download the dataset into data/raw/")
        return

    print(f"\nTotal files found: {len(dataset_files)}")

    print("\nDATASET FILE DETAILS")
    print("-" * 55)

    for file in dataset_files:
        file_size = file.stat().st_size / (1024 * 1024)

        print(f"\nFile name: {file.name}")
        print(f"Format: {file.suffix}")
        print(f"Size: {file_size:.2f} MB")

    print("\n" + "=" * 55)
    print("Dataset inspection completed.")
    print("=" * 55)


if __name__ == "__main__":
    inspect_dataset()