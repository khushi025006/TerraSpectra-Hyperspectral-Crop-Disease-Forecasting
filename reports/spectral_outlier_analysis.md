# TerraSpectra – Spectral Outlier Analysis Report

## 1. Introduction

Spectral outlier analysis is an important part of hyperspectral image processing. It helps identify unusually high pixel intensity values that may indicate abnormal measurements or possible acquisition-related artefacts.

In this analysis, three hyperspectral tomato leaf images (1797, 1827, and 1855) were examined to investigate unusual spectral values across selected wavelength bands.

## 2. Objectives

- Analyse unusual pixel intensity values.
- Compare spectral behaviour across three hyperspectral images.
- Identify bands containing extreme intensity values.
- Calculate statistical measurements for selected spectral bands.
- Investigate pixels exceeding selected intensity thresholds.
- Generate visualisations for understanding unusual spectral patterns.

## 3. Dataset Information

Three hyperspectral image cubes were selected:

| Image ID | Dimensions | Spectral Bands |
|---|---|---|
| 1797 | 512 × 512 | 204 |
| 1827 | 512 × 512 | 204 |
| 1855 | 512 × 512 | 204 |

The analysis focused on spectral bands 129, 192, and 203.

## 4. Methodology

The analysis was performed using Python and NumPy.

The following steps were implemented:

1. Loaded the hyperspectral image cubes.
2. Converted the image data into float32 format.
3. Selected spectral bands 129, 192, and 203.
4. Extracted pixel intensity values.
5. Calculated minimum, median, 95th percentile, 99th percentile, and maximum values.
6. Counted pixels exceeding intensity thresholds of 1, 10, and 100.
7. Stored the numerical results in a CSV file.
8. Generated visualisations for investigating unusual pixel patterns.

## 5. Statistical Results

| Image | Band | Minimum | Median | P95 | P99 | Maximum |
|---|---:|---:|---:|---:|---:|---:|
| 1797 | 129 | 0.0160 | 0.3398 | 0.5352 | 0.9985 | 1.045 |
| 1797 | 192 | 0.0000 | 0.3333 | 0.4849 | 1.0000 | 2184 |
| 1797 | 203 | 0.0000 | 0.1608 | 0.2456 | 1.0000 | 1311 |
| 1827 | 129 | 0.0173 | 0.0731 | 0.5693 | 0.9814 | 1.028 |
| 1827 | 192 | 0.0000 | 0.1786 | 0.6069 | 0.9644 | 2730 |
| 1827 | 203 | 0.0000 | 0.1600 | 0.3000 | 0.9590 | 1598 |
| 1855 | 129 | 0.0165 | 0.2861 | 0.6108 | 1.0000 | 1.031 |
| 1855 | 192 | 0.0250 | 0.3572 | 0.6191 | 1.0000 | 1.119 |
| 1855 | 203 | 0.0000 | 0.3157 | 0.4473 | 1.0000 | 1928 |

## 6. Threshold-Based Analysis

The number of pixels exceeding the selected thresholds was calculated.

| Image | Band | Above 1 | Above 10 | Above 100 |
|---|---:|---:|---:|---:|
| 1797 | 129 | 2424 | 0 | 0 |
| 1797 | 192 | 1746 | 2 | 2 |
| 1797 | 203 | 2568 | 123 | 123 |
| 1827 | 129 | 1032 | 0 | 0 |
| 1827 | 192 | 1335 | 39 | 39 |
| 1827 | 203 | 1334 | 295 | 295 |
| 1855 | 129 | 2528 | 0 | 0 |
| 1855 | 192 | 2518 | 0 | 0 |
| 1855 | 203 | 2386 | 41 | 41 |

## 7. Key Findings

### Finding 1: Band 129

All three images show maximum values close to 1.0.

No pixels exceed the thresholds