from pathlib import Path
import logging

import numpy as np


# ============================================================
# TERRASPECTRA - HYPERSPECTRAL IMAGE LOADER
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data" / "raw"

EXPECTED_BANDS = 204
EXPECTED_HEIGHT = 512
EXPECTED_WIDTH = 512


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("TerraSpectra.HyperspectralLoader")


# ============================================================
# FILE VALIDATION
# ============================================================

def validate_file(file_path):

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(file_path)

    if file_path.suffix.lower() != ".npz":
        raise ValueError("Expected an NPZ file")

    if file_path.stat().st_size == 0:
        raise ValueError("Dataset file is empty")

    logger.info("File validation successful: %s", file_path.name)

    return True


# ============================================================
# LOAD HYPERSPECTRAL CUBE
# ============================================================

def load_cube(file_path, array_name=None):

    validate_file(file_path)

    logger.info("Loading hyperspectral cube")

    with np.load(file_path, allow_pickle=False) as archive:

        available_arrays = archive.files

        if not available_arrays:
            raise ValueError("No arrays found in NPZ archive")

        if array_name is None:
            array_name = available_arrays[0]

        if array_name not in available_arrays:
            raise KeyError(
                f"{array_name} not found. Available: {available_arrays}"
            )

        cube = archive[array_name]

    logger.info("Cube loaded successfully")

    return cube


# ============================================================
# SHAPE VALIDATION
# ============================================================

def validate_cube_shape(cube):

    if cube.ndim != 3:
        raise ValueError(
            f"Expected 3D cube, received {cube.ndim} dimensions"
        )

    height, width, bands = cube.shape

    return {
        "valid": (
            height == EXPECTED_HEIGHT
            and width == EXPECTED_WIDTH
            and bands == EXPECTED_BANDS
        ),
        "height": int(height),
        "width": int(width),
        "bands": int(bands)
    }


# ============================================================
# NUMERICAL VALIDATION
# ============================================================

def validate_numerical_values(cube):

    return {
        "nan_count": int(np.isnan(cube).sum()),
        "positive_infinity": int(
            np.isposinf(cube).sum()
        ),
        "negative_infinity": int(
            np.isneginf(cube).sum()
        ),
        "finite_values": int(
            np.isfinite(cube).sum()
        ),
        "total_values": int(cube.size)
    }


# ============================================================
# FLOAT32 CONVERSION
# ============================================================

def convert_to_float32(cube):

    converted = cube.astype(
        np.float32,
        copy=True
    )

    logger.info("Converted cube to float32")

    return converted


# ============================================================
# GENERAL STATISTICS
# ============================================================

def calculate_statistics(cube):

    valid_values = cube[
        np.isfinite(cube)
    ].astype(np.float32)

    if valid_values.size == 0:
        raise ValueError("No finite values found")

    return {
        "minimum": float(np.min(valid_values)),
        "maximum": float(np.max(valid_values)),
        "mean": float(np.mean(valid_values)),
        "median": float(np.median(valid_values)),
        "standard_deviation": float(
            np.std(valid_values)
        )
    }


# ============================================================
# BAND-WISE STATISTICS
# ============================================================

def calculate_band_statistics(cube):

    cube = cube.astype(
        np.float32,
        copy=False
    )

    band_means = np.nanmean(
        cube,
        axis=(0, 1)
    )

    band_stds = np.nanstd(
        cube,
        axis=(0, 1)
    )

    return {
        "band_means": band_means,
        "band_standard_deviations": band_stds,
        "number_of_bands": int(cube.shape[2])
    }


# ============================================================
# PIXEL SPECTRUM EXTRACTION
# ============================================================

def extract_pixel_spectrum(cube, row, column):

    height, width, _ = cube.shape

    if not (0 <= row < height):
        raise IndexError("Invalid pixel row")

    if not (0 <= column < width):
        raise IndexError("Invalid pixel column")

    spectrum = cube[row, column, :]

    return spectrum.astype(
        np.float32,
        copy=False
    )


# ============================================================
# MEMORY ANALYSIS
# ============================================================

def calculate_memory_usage(cube):

    return {
        "memory_bytes": int(cube.nbytes),
        "memory_megabytes": round(
            cube.nbytes / (1024 * 1024), 2
        ),
        "data_type": str(cube.dtype)
    }


# ============================================================
# DATA QUALITY SUMMARY
# ============================================================

def create_quality_summary(cube):

    shape_report = validate_cube_shape(cube)

    numerical_report = validate_numerical_values(cube)

    memory_report = calculate_memory_usage(cube)

    statistics = calculate_statistics(cube)

    return {
        "shape": shape_report,
        "numerical_quality": numerical_report,
        "memory": memory_report,
        "statistics": statistics
    }


# ============================================================
# COMPLETE IMAGE INSPECTION
# ============================================================

def inspect_hyperspectral_image(file_path):

    cube = load_cube(file_path)

    original_dtype = str(cube.dtype)

    quality_report = create_quality_summary(cube)

    cube_float32 = convert_to_float32(cube)

    band_report = calculate_band_statistics(
        cube_float32
    )

    quality_report["original_data_type"] = original_dtype

    quality_report["band_statistics"] = {
        "mean_of_first_band": float(
            band_report["band_means"][0]
        ),
        "mean_of_last_band": float(
            band_report["band_means"][-1]
        ),
        "band_count": band_report["number_of_bands"]
    }

    return cube_float32, quality_report


# ============================================================
# DISPLAY RESULTS
# ============================================================

def display_report(report):

    print("\n" + "=" * 60)

    print("TERRASPECTRA HYPERSPECTRAL IMAGE REPORT")

    print("=" * 60)

    print("\nIMAGE SHAPE")

    print(report["shape"])

    print("\nNUMERICAL QUALITY")

    print(report["numerical_quality"])

    print("\nMEMORY")

    print(report["memory"])

    print("\nSTATISTICS")

    for key, value in report["statistics"].items():
        print(f"{key}: {value}")

    print("\nBAND STATISTICS")

    print(report["band_statistics"])

    print("\n" + "=" * 60)


# ============================================================
# MAIN EXECUTION
# ============================================================

def main():

    image_path = DATA_DIR / "1797.npz"

    cube, report = inspect_hyperspectral_image(
        image_path
    )

    display_report(report)

    spectrum = extract_pixel_spectrum(
        cube,
        row=256,
        column=256
    )

    print("\nPIXEL SPECTRUM")

    print("Number of spectral values:", len(spectrum))

    print("First 10 spectral values:", spectrum[:10])

    print("\nHyperspectral loading completed successfully!")


if __name__ == "__main__":

    main()
