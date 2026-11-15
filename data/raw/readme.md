# Dataset description

Title: Hyperspectral imaging (HS) of tomato leaves inoculated with Alternaria protenta

Description: The dataset consists of hyperspectral images (HS) and associated data of tomato leaves captured during a disease development study. Number of trials took place in an experimental greenhouse where tomatoes of cultivar *Encore* were inoculated with *Alternaria protenta* pathogens, and the development of the disease on leaves was captured on a regular basis using an HS camera over the course of several weeks. Additional data were obtained via basic image preprocessing and feature extraction procedures. The dataset is suitable for in-depth disease development studies based both on statistical approaches (e.g. spectral index calculations) as well as deep learning models (e.g., semantic segmentation).

File formats: RAW, PNG, BMP, TAB

Language used: English

Keywords: hyperspectral imaging, tomatoes disease, Alternaria protenta


# Authors and contact information

Co-authors:

- Vitalijs Komasilovs<sup>1,*</sup>, 0000-0003-2797-633X
- Maksims Filipovics<sup>1</sup>, 0000-0002-0577-6073
- Olvija Komasilova<sup>1</sup>, 0000-0001-9248-3836

Involved persons:
- Guna Bundzena<sup>1</sup>
- Gunita Bimsteine<sup>1</sup>
- Inta Jakobija<sup>1</sup>
- Viktorija Zagorska<sup>1</sup>
- Aleksejs Zacepins<sup>1</sup>

<sup>1</sup> Latvia University of Life Sciences and Technologies

<sup>*</sup> Correspondence: vitalijs.komasilovs@lbtu.lv


# Data collection

Date of data collection: 11.04.2025 to 28.08.2025

Geographical origin: Latvia, Europe

Information on measuring instruments: Specim IQ, Specim Spectral Imaging Ltd., Oulu, Finland

Data collection methods: HS images were captured in experimental greenhouse with natural lighting (sunlight).
Individual leaves were isolated using black background plate.
White reference was added to the frame for spectral calibration.
Capturing distance varied from `13` to `48` mm and integration period varied from `15` to `100` seconds depending on lighting conditions.

# Data structure

The dataset consists of `1000` HS images and is organized as several related entities:
- Raw HS captures as produced by camera
- Calibrated capture cubes
- RGB images
- Imaging metadata

The details for each of these are explained below.

## Raw HS captures

Specim IQ camera captures each HS image as a dedicated folder named as image ID. It contains generic metadata and several previews as RGB images. Raw captures are stored in following files:

- `*.hdr` - header (text) files with technical information about the capture, includes image resolution, number of channels, captured light wavelengths, etc.
- `*.raw` - raw capture bytes, `512 x 204 x 512` pixels of type `uint16`.
- `DARKREF_*.raw` and `WHITEREF_*.raw` - raw references bytes used for calibration, `204 x 512` pixels of type `uint16`.

**NB!** Due to limited storage space, only few examples of such raw capture are uploaded to the Dataverse platform. Full dataset is available upon request.

## Calibrated capture cubes

During raw HS image preprocessing capture cubes are extracted, calibrated and stored as binary NumPy array in `*.npz` files. Each array has shape of `(512, 512, 204)` elements of type `float16`.

**NB!** Due to limited storage space, only few examples of such capture cubes are uploaded to the Dataverse platform. Full dataset is available upon request.

## RGB images

During raw HS image preprocessing RGB images are extracted and stored as `*.png` files.
The channels used to produce RGB image are `70`, `53`, `19`, which correspond to light wavelengths of `598.60`, `548.55` and `449.35` nanometers.
Gamma correction procedure is applied to RGB images.
These images are used for visual inspection, annotation process and other purposes.

## Imaging metadata

Metadata recorded during the imaging process is provided in tabular form.

Column Name	| Description			| Type			| Notes
----------- | --------------- | ----------- |--------
image_id | Unique image identifier | Integer | Sequential, provided by the camera.
trial | Trial number | Integer | Sequential, 5 trials in total.
plant | Plant identifier | String | `028/*`, `065/*` - plants inoculated with different *Alternaria protenta* isolates;<br>`K/*` - control plants.
leaf | Leaf identifier | String | Sequential leaf number as it grows on the plant.<br>Special values:<br>`A*`, `P*` - side shoots (suckers),<br>`NA` - whole plant is imaged.
part | Part identifier of the complex leaf | List of strings | Sequential number of leaf part(s).<br>Special values:<br>`G` - terminal leaflet,<br>`NA` - whole leaf is imaged.
date | Date when the image was taken | Date | Format: `YYYY-MM-DD`
imaging_distance | Distance from camera to the subject | Integer | Units: `cm`
integration_time | Integration time of the imaging | Integer | Units: `sec`
weather | Weather description when image was taken | String | Used as hint of lighting conditions

The specific object (leaf part) can be uniquely identified on multiple images by combination of `trial`, `plant`, `leaf` and `part` identifiers. Thus the same object can be tracked across multiple imaging dates.


# Access rights and references

Data license and terms of use: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
