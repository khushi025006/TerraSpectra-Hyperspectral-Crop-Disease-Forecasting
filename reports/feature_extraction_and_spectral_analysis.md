# TerraSpectra
## Feature Extraction and Spectral Analysis Report

### 1. Introduction

Feature extraction is an important stage of the TerraSpectra hyperspectral crop disease forecasting project.

The objective of this stage is to extract meaningful statistical information from hyperspectral tomato leaf images and investigate variations in their spectral responses.

Three selected hyperspectral images were analysed:

- Image 1797
- Image 1827
- Image 1855

Each image contains 204 spectral bands with a spatial resolution of 512 × 512 pixels.

### 2. Feature Extraction Methodology

Feature extraction was performed using:

`src/feature_extraction.py`

The following steps were implemented:

1. Loaded preprocessed hyperspectral image cubes.
2. Loaded corresponding external leaf segmentation masks.
3. Validated cube and mask dimensions.
4. Selected only pixels belonging to the segmented leaf regions.
5. Extracted spectral measurements across all 204 bands.
6. Calculated statistical features for every spectral band.
7. Generated image-level statistical summaries.
8. Exported the extracted features into CSV files.

The external segmentation masks were used to exclude background pixels from feature calculations.

### 3. Extracted Statistical Features

Seven statistical measurements were calculated for each spectral band:

| Feature | Description |
|---|---|
| Mean | Average spectral value |
| Standard Deviation | Measures variation in spectral values |
| Median | Middle value of spectral measurements |
| Minimum | Lowest spectral value |
| Maximum | Highest spectral value |
| P10 | 10th percentile |
| P90 | 90th percentile |

These features describe the distribution of spectral values within the segmented leaf regions.

### 4. Feature Extraction Results

| Image ID | Leaf Pixels | Background Pixels | Leaf Coverage |
|---|---:|---:|---:|
| 1797 | 105,627 | 156,517 | 40.29% |
| 1827 | 99,987 | 162,157 | 38.14% |
| 1855 | 99,750 | 162,394 | 38.05% |

Image-level spectral statistics:

| Image ID | Overall Mean | Overall Std | Overall Median |
|---|---:|---:|---:|
| 1797 | 0.233818 | 0.187555 | 0.155627 |
| 1827 | 0.292611 | 0.213296 | 0.247582 |
| 1855 | 0.286154 | 0.221383 | 0.203734 |

### 5. Generated Feature Datasets

Two CSV datasets were generated.

**File 1: spectral_band_features.csv**

Location:
`results/features/spectral_band_features.csv`

Contains:
- 612 records.
- 204 spectral bands per image.
- 3 analysed images.
- 9 columns, including image ID, band index and seven statistical measurements.

**File 2: image_level_features.csv**

Location:
`results/features/image_level_features.csv`

Contains:
- 3 records.
- 8 columns.
- Image-level spectral statistics and leaf coverage information.

### 6. Feature Validation

The extracted datasets were checked for data quality.

| Validation | Result |
|---|---|
| Spectral feature records | 612 |
| Image-level records | 3 |
| Missing spectral values | 0 |
| Missing image-level values | 0 |
| Duplicate spectral records | 0 |
| Non-finite numeric values | None detected |

All validation checks completed successfully.

### 7. Spectral Signature Visualization

Three comparative graphs were generated:

1. Mean Spectral Signature Comparison.
2. Median Spectral Signature Comparison.
3. Spectral Standard Deviation Comparison.

Location:
`results/features/graphs/`

#### 7.1 Mean Spectral Signature Observations

- Images 1827 and 1855 show relatively similar spectral patterns.
- Image 1797 shows lower mean values across several spectral regions.
- All three images show a substantial increase around bands 100–120.
- Image 1797 exhibits a noticeable reduction around bands 180–190.
- Fluctuations are visible near the final spectral bands.

#### 7.2 Median Spectral Signature Observations

- Images 1827 and 1855 have relatively similar median spectral responses.
- Image 1797 exhibits lower median values in several regions.
- Variations are visible around bands 180–203.

#### 7.3 Standard Deviation Observations

- Image 1827 shows relatively high variation around bands 25–40.
- All three images show increased variation around bands 110–130.
- Image 1827 exhibits a prominent variability increase around bands 180–190.

### 8. Top Variable Spectral Band Analysis

The top 10 spectral bands with the highest standard deviation were identified separately for each image.

The analysis was performed using:

`src/analyze_top_variable_bands.py`

Results were saved in:

`results/features/top_variable_bands.csv`

#### 8.1 Image 1797

- Highest variability band: 123
- Standard deviation: 0.063427
- Most variable spectral region: approximately bands 119–128.

#### 8.2 Image 1827

- Highest variability band: 181
- Standard deviation: 0.096163
- Most variable spectral region: approximately bands 180–189.

#### 8.3 Image 1855

- Highest variability band: 181
- Standard deviation: 0.066