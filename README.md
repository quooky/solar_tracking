# Solar Tracking

A Python tool for tracking sunspots in solar images and analyzing the Sun's differential rotation. Developed as part of a Bachelor's thesis.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Overview

This project processes HMI (Helioseismic and Magnetic Imager) continuum images from the Solar Dynamics Observatory (SDO) to:

- **Detect sunspots** using adaptive thresholding and connected component analysis
- **Track sunspot motion** across image sequences using OpenCV's MIL tracker
- **Convert coordinates** from pixel space to heliographic coordinates (latitude/longitude)
- **Calculate differential rotation** rates and fit to the standard solar rotation model
- **Visualize results** with interactive displays and PDF output

<!--
## Demo

![Sunspot Tracking Demo](docs/images/tracking_demo.gif)

*Example: Interactive sunspot tracking with real-time coordinate overlay*
-->

## Scientific Background

The Sun does not rotate as a rigid body. Instead, it exhibits **differential rotation** - the equator rotates faster (~25 days) than the poles (~35 days). This rotation profile follows the empirical law:

$$\Omega(B) = A + B \cdot \sin^2(B)$$

where $\Omega$ is the angular velocity and $B$ is the heliographic latitude.

This tool measures differential rotation by tracking sunspot positions over time and fitting the observed velocities to this model.

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenCV with GUI support

### Install from source

```bash
git clone https://github.com/quooky/solar_tracking.git
cd solar_tracking
pip install -e .
```

Or install dependencies directly:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

The package provides a `solar-tracking` CLI with three main commands:

#### 1. Download Solar Data

```bash
solar-tracking downloader --start "2023-11-23 00:00:00" --end "2023-11-25 00:00:00" --sample 1
```

Options:
- `--start`: Start time (YYYY-MM-DD HH:MM:SS)
- `--end`: End time (YYYY-MM-DD HH:MM:SS)
- `--instrument`: Instrument name (default: hmi)
- `--sample`: Sampling interval in hours (default: 1)

#### 2. Run Sunspot Tracking

```bash
solar-tracking run_tracking --trace 1
```

Options:
- `--trace`: Trace series number (corresponds to data/TR_0X folder)
- `--no-interactive`: Run without user interaction

**Interactive Controls:**
- `Space`: Pause/resume tracking
- `S`: Skip current spot
- `Q`: Save results and quit
- `N`: Next spot

#### 3. View FITS Files

```bash
solar-tracking view_fits path/to/file.fits
```

### Python API

```python
from solar_tracking.downloader import download_fits
from solar_tracking.tracking import run_tracking
from solar_tracking.sunspot_detection import find_spots_and_bounding_boxes
from solar_tracking.fitting import perform_fitting

# Download data
files = download_fits("2023-11-23 00:00:00", "2023-11-25 00:00:00")

# Run tracking
run_tracking(trace=1, interactive=True)

# Or use individual components
spots, boxes = find_spots_and_bounding_boxes(image, sun_center, sun_radius)
```

## Project Structure

```
solar_tracking/
├── solar_tracking/          # Main package
│   ├── cli.py              # Command line interface
│   ├── downloader.py       # FITS file downloading via SunPy
│   ├── tracking.py         # Main tracking algorithm
│   ├── sunspot_detection.py # Spot detection with OpenCV
│   ├── image_processing.py # FITS preprocessing
│   ├── rotation_analysis.py # Coordinate transformation
│   ├── fitting.py          # Differential rotation fitting
│   └── plotting.py         # Result visualization
├── tests/                  # Test suite
├── data/                   # Solar observation data (not in repo)
├── docs/                   # Documentation and thesis
└── setup.py
```

## Data

The tracking requires HMI continuum intensity images (hmi_ic_45s). Data is automatically downloaded from the [Virtual Solar Observatory](https://sdac.virtualsolar.org/) using SunPy.

Sample data structure:
```
data/
├── TR_01/
│   ├── *.fits          # HMI FITS files
│   ├── names.txt       # File listing
│   └── data_points.csv # Tracking results
```

## Results

The tool outputs:
- **CSV files** with tracked positions (pixel and heliographic coordinates)
- **PDF plots** showing the differential rotation curve with fitted parameters

<!--
![Differential Rotation Results](docs/images/rotation_plot.png)

*Example: Measured rotation rates vs. latitude with fitted curve*
-->

## Dependencies

- [SunPy](https://sunpy.org/) - Solar data analysis
- [OpenCV](https://opencv.org/) - Computer vision and tracking
- [Astropy](https://www.astropy.org/) - FITS handling and coordinates
- [NumPy](https://numpy.org/) - Numerical computing
- [Matplotlib](https://matplotlib.org/) - Visualization
- [SciPy](https://scipy.org/) - Curve fitting

## Testing

```bash
pytest tests/
```

## Thesis

This project was developed as part of a Bachelor's thesis. The full thesis document is available in the `docs/` folder.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Dominic Foerster

## Acknowledgments

- Solar Dynamics Observatory (SDO) for providing HMI data
- SunPy community for the excellent solar physics library
