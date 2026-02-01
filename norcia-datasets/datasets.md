## Datasets for Norcia/Central Italy Earthquake ML

### Primary Seismic Waveform Datasets

| Dataset | URL | Data Type | Size/Coverage | Format | Key Features |
|---------|-----|-----------|---------------|--------|--------------|
| **INSTANCE** | http://doi.org/10.13127/instance | Seismic waveforms + metadata | 1.2M earthquake traces, 130K noise traces (2005-2020) | HDF5 | ML-ready, 115 metadata fields, 120s windows at 100Hz, includes 2016 Norcia sequence |
| **INGV Central Italy Dataset** | https://shake.mi.ingv.it/central-italy/ | Accelerometric & velocimetric waveforms | 434K recordings, 9,948 earthquakes (2009-2023) | SAC/various | Focused on Amatrice-Visso-Norcia region, Fourier spectra |
| **INGV Seismic Waveforms** | https://www.ingv.it | Continuous + event waveforms | Years before & after 2016 | miniSEED | Station metadata included |
| **EIDA Archive** | https://www.orfeus-eu.org/data/eida/ | European seismic waveforms | Multi-decade | miniSEED | Includes temporary arrays |
| **Dense Temporary Networks (2016)** | Via EIDA / INGV | High-resolution local stations | 2016-2017 | miniSEED | Near-fault dense arrays, linked in paper supplements |
| **STEAD** (global reference) | https://github.com/smousavi05/STEAD | Seismic waveforms | 1.2M traces globally | HDF5 | ML benchmark, good for transfer learning |

### Earthquake Catalogs

| Dataset | URL | Data Type | Size/Coverage | Format | Key Features |
|---------|-----|-----------|---------------|--------|--------------|
| **ISIDe** | https://terremoti.ingv.it/en/iside | Earthquake catalog + waveforms | 100K+ events (1985-present) | QuakeML, miniSEED | FDSN web services, full Italian coverage |
| **USGS Earthquake Catalog** | https://earthquake.usgs.gov | Global earthquake catalog | 1900-present | Various | Coarser locally, good for regional context |
| **CLASS Catalog** | https://ingv.github.io/class/locations/ | Relocated earthquake catalog | 400K events (1981-2018) | CSV, KML | 3D probabilistic locations, quality classifications |
| **CFTI5Med** | https://doi.org/10.6092/ingv.it-cfti5 | Historical earthquake catalog | 461 BC - 1997 | Database | Macroseismic intensities, long-term patterns |

### Geodetic / GPS Data

| Dataset | URL | Data Type | Size/Coverage | Format | Key Features |
|---------|-----|-----------|---------------|--------|--------------|
| **RING High-Rate GPS** | http://ring.gm.ingv.it/?p=1333 | GPS displacement time series | 2016 Central Italy sequence | RINEX | 1-20Hz sampling, coseismic displacements |
| **Italian GPS Network (RING)** | https://ring.ingv.it | Italian continuous GNSS | Long-term | RINEX | mm-precision displacement |
| **EarthScope / UNAVCO** | https://www.earthscope.org | Continuous GPS - Central Italy | Pre-2016 to post-2017 | RINEX | Station displacement (mm precision) |

### InSAR / Satellite Data

| Dataset | URL | Data Type | Size/Coverage | Format | Key Features |
|---------|-----|-----------|---------------|--------|--------------|
| **Sentinel-1 InSAR** | https://scihub.copernicus.eu | Satellite radar (InSAR) | 2014-present | GeoTIFF/NetCDF | Surface deformation maps |
| **Processed InSAR Products** | Paper supplements / Zenodo | Interferograms, displacement fields | Event-focused | Various | Linked in Nature/Science papers |

### Supplementary Datasets

| Dataset | URL | Data Type | Size/Coverage | Format | Key Features |
|---------|-----|-----------|---------------|--------|--------------|
| **Coseismic Effects DB** | https://www.nature.com/articles/sdata201849 | Surface faulting, landslides | 7,323 observation points | Georeferenced CSV | 18 fields per observation, post-Norcia Mw 6.5 |
| **Norcia ERT/TDEM/Seismic** | https://data.ingv.it/dataset/696 | Geophysical survey data | Dec 2016 - Jun 2017 | Various (bin, SAC, GX7) | Subsurface structure near Norcia fault |
| **ESM Strong Motion DB** | https://esm-db.eu/ | Strong motion recordings | European M≥4 events | Flat file | Intensity measures, analyst-reviewed |
| **Slow Earthquake / Tremor Catalogs** | EIDA + AGU paper supplements | Low-frequency seismic signals | Partial | Various | Tremor / slow slip detections |
| **Animal Behavior Dataset (2016)** | Wiley ETH paper supplements | Behavioral time series | 2016 | CSV | Animal activity vs seismicity |
| **Fault Geometry & Rupture Models** | USGS + INGV + paper supplements | Structural / geologic | Event-specific | Various | Fault planes, slip models |
| **Tomographic Velocity Models** | GSA Geology paper supplements | 3D crustal velocity | Pre- & post-event | Various | Velocity changes as precursors |

## Papers with Associated Data

| Paper Topic | Citation/URL | Data Type | Relevance to Norcia |
|-------------|--------------|-----------|---------------------|
| Seismic velocity precursors | Geology 2020 (GSA) | Tomographic imaging | Velocity changes before Mw 6.5 |
| GPS preslip detection | Science 2023 (Bletery & Nocquet) | GPS time series | 2-hour precursory signal |
| Preslip rebuttal | EarthArXiv 2023 | GPS reanalysis | Disputes precursor claims |
| Animal behavior precursors | Ethology 2020 (Wikelski) | Motion detector data | Farm animals near Norcia |
| Slow earthquake + DL | AGU 2020 | Seismic continuous data | Deep learning for slow slip |
| Fault patch identification | Nature Sci Rep 2019 | Dense network seismicity | Stress transfer modeling |
