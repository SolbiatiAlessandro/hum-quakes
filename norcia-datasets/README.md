# Norcia 2016 Earthquake Datasets

This repository contains scripts and documentation for downloading and processing earthquake data from the 2016 Central Italy seismic sequence, including the major Norcia earthquake (M6.5) and related events.

## Overview

The 2016 Central Italy earthquake sequence was a series of destructive earthquakes that struck the Apennines region, including:
- **August 24, 2016**: Amatrice earthquake (M6.0)
- **October 26, 2016**: Visso earthquakes (M5.4 and M5.9)
- **October 30, 2016**: Norcia earthquake (M6.5) - the strongest earthquake in Italy since 1980

This repository provides tools to download and process seismic data from multiple sources to support research and analysis of this significant seismic sequence.

## Repository Structure

```
norcia-datasets/
├── download-norcia/              # Data download scripts
│   ├── download_all.py          # Main download script (run this!)
│   ├── download_norcia.py       # INGV catalog downloader
│   ├── process_instance_metadata.py  # INSTANCE metadata processor
│   └── download_norcia_metadata.md   # Technical documentation
├── datasets.md                  # Dataset descriptions
├── norcia_baseline.md           # Baseline analysis
├── norcia_2016_metadata.parquet # INSTANCE metadata (generated)
└── venv/                        # Python virtual environment
```

## Quick Start

### 1. Setup Python Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install pandas obspy requests pyarrow
```

### 2. Download All Datasets

```bash
# Run the unified download script
cd download-norcia
python download_all.py
```

This will download:
- **INGV Earthquake Catalog** (~400 KB): Seismic events from INGV's FDSN service
- **INSTANCE Metadata** (~106 MB): Detailed waveform metadata from Zenodo

### 3. Alternative: Download Individual Datasets

```bash
# Download only INGV catalog
python download-norcia/download_norcia.py

# Download only INSTANCE metadata
python download-norcia/process_instance_metadata.py
```

## Data Sources

### 1. INGV Earthquake Catalog
- **Source**: INGV (Istituto Nazionale di Geofisica e Vulcanologia) FDSN Web Service
- **Content**: 4,067 seismic events (M≥2.5) from 2016-2017
- **Format**: CSV with columns: time, latitude, longitude, depth, magnitude, magnitude_type
- **Output**: `download-norcia/ingv_norcia_events_2016_2017.csv`

### 2. INSTANCE Metadata
- **Source**: [Zenodo Dataset 4271548](https://zenodo.org/records/4271548)
- **Content**: Waveform metadata for 65,162 three-component records
- **Original Size**: ~2.8 GB CSV (compressed to ~106 MB Parquet)
- **Output**: `download-norcia/norcia_2016_metadata.parquet`
- **Key Information**:
  - Station locations and characteristics
  - Recording parameters
  - Quality metrics (SNR, usable frequency range)
  - Processing metadata

## Dataset Details

The downloaded datasets include:

### Event Statistics
- **Total Events**: 4,067 (M≥2.5)
- **Date Range**: January 1, 2016 - December 31, 2017
- **Magnitude Range**: M2.5 - M6.5
- **Geographic Coverage**:
  - Latitude: 41.5° - 44.0° N
  - Longitude: 11.5° - 14.5° E

### Magnitude Distribution
- M2.5-3.0: 2,223 events
- M3.0-3.5: 715 events
- M3.5-4.0: 169 events
- M4.0-4.5: 38 events
- M4.5-5.0: 6 events
- M5.0-5.5: 5 events
- M5.5-6.0: 2 events
- M6.0-7.0: 1 event

## Usage Examples

### Loading the INGV Catalog
```python
import pandas as pd

# Load earthquake catalog
df_events = pd.read_csv('download-norcia/ingv_norcia_events_2016_2017.csv')
print(f"Total events: {len(df_events)}")

# Filter major events (M≥4.0)
major_events = df_events[df_events['magnitude'] >= 4.0]
print(f"Major events (M≥4.0): {len(major_events)}")
```

### Loading INSTANCE Metadata
```python
import pandas as pd

# Load waveform metadata
df_metadata = pd.read_parquet('download-norcia/norcia_2016_metadata.parquet')
print(f"Total records: {len(df_metadata)}")

# Get unique stations
stations = df_metadata['station_code'].unique()
print(f"Number of stations: {len(stations)}")
```

## Requirements

- Python 3.7+
- Required packages:
  - `pandas`: Data manipulation
  - `obspy`: Seismological data access
  - `requests`: HTTP requests
  - `pyarrow`: Parquet file support

## Documentation

- `datasets.md`: Detailed description of available datasets
- `norcia_baseline.md`: Baseline analysis and research context
- `download-norcia/download_norcia_metadata.md`: Technical documentation for data acquisition

## Citation

If you use this data in your research, please cite:
- **INGV Data**: INGV Seismological Data Centre (2006). Italian Seismological Instrumental and Parametric Database (ISIDe). DOI: 10.13127/ISIDE
- **INSTANCE Data**: Michelini, A., et al. (2020). The Italian National Seismic Network and the earthquake and tsunami monitoring and surveillance systems. DOI: 10.5281/zenodo.4271548

## License

The scripts in this repository are provided under the MIT License. The downloaded data is subject to the original data providers' licenses.

## Contact

For questions or issues, please open an issue on the repository.