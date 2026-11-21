# Extreme Pixel Spatial Analysis

## Objective
Investigate the spatial distribution of extreme pixel values in hyperspectral images 1797, 1827, and 1855.

## Method
- Examined spectral bands 192 and 203.
- Identified extreme pixels using intensity greater than 100.
- Recorded image ID, band, row, column, and intensity.
- Generated spatial scatter plots for all three images.

## Results

| Image | Band 192 | Band 203 |
|---|---:|---:|
| 1797 | 2 | 123 |
| 1827 | 39 | 295 |
| 1855 | 0 | 41 |
| Total | 41 | 459 |

Total extreme pixels: 500.

## Spatial Observations
- All detected Band 203 extreme pixels occur at column 96.
- Band 192 extreme pixels in images 1797 and 1827 occur at column 222.
- Band 203 pixels show vertically adjacent positions, with some gaps.
- Image 1827 contains the highest number of detected extreme pixels.

These repeated column positions may indicate a systematic spatial pattern. However, the cause is not confirmed and requires further investigation.

## Visualizations Generated
- results/spectral_outliers/1797_extreme_pixel_distribution.png
- results/spectral_outliers/1827_extreme_pixel_distribution.png
- results/spectral_outliers/1855_extreme_pixel_distribution.png

## Conclusion
The investigation identified 500 pixels with intensity greater than 100. Band 203 contains most of these extreme values. Their repeated spatial positions deserve further examination before deciding whether they are sensor artefacts or another type of anomaly.

