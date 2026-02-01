#!/usr/bin/env python3
"""
Download and filter INSTANCE dataset for Norcia 2016 earthquakes
Two options: 1) Google Colab (recommended for large downloads)
            2) Metadata-first approach (download metadata, filter, then fetch waveforms)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

# =============================================================================
# OPTION 1: Google Colab Setup (Recommended for full dataset)
# =============================================================================

def setup_colab():
    """
    Run this in a Google Colab notebook for free GPU + 100GB+ disk space
    """
    try:
        from google.colab import drive
        drive.mount('/content/drive')
        print("✓ Google Drive mounted")

        # Create dataset directory if it doesn't exist
        os.makedirs('/content/drive/MyDrive/datasets', exist_ok=True)

        # Download INSTANCE directly to Drive (adjust URL as needed)
        # Note: Replace with actual INSTANCE download URL from http://doi.org/10.13127/instance
        print("Downloading INSTANCE dataset to Google Drive...")
        os.system("""
            wget -P /content/drive/MyDrive/datasets/ \
            "https://data.ingv.it/dataset/instance/instance_events_counts.hdf5"
        """)

        return True
    except ImportError:
        print("Not running in Google Colab")
        return False

# =============================================================================
# OPTION 2: Metadata-First Approach (Download metadata, filter, then waveforms)
# =============================================================================

def download_metadata(url=None):
    """
    Step 1: Download only metadata CSV (~100MB)
    From: http://doi.org/10.13127/instance
    """
    if url is None:
        # Placeholder URL - replace with actual metadata URL from INSTANCE
        url = "https://data.ingv.it/dataset/instance/instance_metadata.csv"

    print(f"Downloading metadata from {url}")

    # For actual implementation, use:
    # import urllib.request
    # urllib.request.urlretrieve(url, 'instance_metadata.csv')

    # For now, we'll show the pandas loading approach
    try:
        metadata = pd.read_csv('instance_metadata.csv')
        print(f"✓ Metadata loaded: {len(metadata)} total traces")
        return metadata
    except FileNotFoundError:
        print("⚠ instance_metadata.csv not found. Please download from http://doi.org/10.13127/instance")
        return None

def filter_norcia_events(metadata):
    """
    Step 2: Filter metadata to Norcia 2016 earthquake sequence
    Main event: Oct 30, 2016 M6.5
    """
    if metadata is None:
        print("No metadata to filter")
        return None

    # Filter to Norcia 2016 sequence (Aug 2016 - Jan 2017)
    norcia = metadata[
        (metadata['source_origin_time'] >= '2016-08-01') &
        (metadata['source_origin_time'] <= '2017-01-31') &
        (metadata['source_latitude_deg'].between(42.5, 43.2)) &  # Norcia region
        (metadata['source_longitude_deg'].between(12.8, 13.5))
    ]

    print(f"✓ Norcia 2016 traces: {len(norcia)}")

    # Estimate storage requirements
    n_traces = len(norcia)
    duration_s = 120  # typical trace duration
    sample_rate = 100  # Hz
    n_channels = 3  # 3-component
    bytes_per_sample = 4  # float32

    size_gb = (n_traces * duration_s * sample_rate * n_channels * bytes_per_sample) / (1024**3)
    print(f"  Estimated size: ~{size_gb:.1f} GB")
    print(f"  ({n_traces} traces × {duration_s}s × {sample_rate}Hz × {n_channels} channels)")

    return norcia

def download_waveforms(norcia_metadata, output_dir='norcia_waveforms'):
    """
    Step 3: Download only the filtered waveform trace IDs from full HDF5
    """
    if norcia_metadata is None or norcia_metadata.empty:
        print("No Norcia events to download")
        return

    os.makedirs(output_dir, exist_ok=True)

    # Get unique trace IDs
    trace_ids = norcia_metadata['trace_id'].unique() if 'trace_id' in norcia_metadata.columns else []
    print(f"Downloading {len(trace_ids)} unique traces...")

    # In actual implementation, you would:
    # 1. Connect to INSTANCE data service
    # 2. Request only these specific trace IDs
    # 3. Save to local HDF5 or other format

    print(f"Waveforms would be saved to: {output_dir}/")
    return trace_ids

# =============================================================================
# Working with HDF5 Data
# =============================================================================

def load_and_filter_hdf5(filepath='instance_events_counts.hdf5'):
    """
    Example of working with downloaded HDF5 data
    """
    try:
        import h5py

        with h5py.File(filepath, 'r') as f:
            print(f"HDF5 structure: {list(f.keys())}")

            # Example: Access waveform data (structure depends on INSTANCE format)
            if 'waveforms' in f:
                waveforms = f['waveforms']
                print(f"Waveform shape: {waveforms.shape}")

            # Example: Access metadata within HDF5
            if 'metadata' in f:
                meta = f['metadata']
                print(f"Available metadata: {list(meta.keys())}")

        return True
    except (ImportError, FileNotFoundError) as e:
        print(f"Could not load HDF5: {e}")
        return False

# =============================================================================
# Main execution
# =============================================================================

def main():
    print("INSTANCE Dataset Download for Norcia 2016 Earthquakes")
    print("=" * 60)

    # Check if running in Colab
    in_colab = setup_colab()

    if in_colab:
        print("\n✓ Running in Google Colab - using Option 1")
        print("Large dataset will be downloaded to Google Drive")

        # After download, work with HDF5
        load_and_filter_hdf5('/content/drive/MyDrive/datasets/instance_events_counts.hdf5')
    else:
        print("\n→ Using Option 2: Metadata-first approach")

        # Step 1: Download metadata
        metadata = download_metadata()

        if metadata is not None:
            # Step 2: Filter to Norcia
            norcia = filter_norcia_events(metadata)

            # Step 3: Download filtered waveforms
            if norcia is not None and not norcia.empty:
                trace_ids = download_waveforms(norcia)

                # Save filtered metadata for reference
                norcia.to_csv('norcia_metadata.csv', index=False)
                print(f"\n✓ Filtered metadata saved to: norcia_metadata.csv")
                print(f"  Use this to download specific waveforms from INSTANCE")

    print("\n" + "=" * 60)
    print("Next steps:")
    print("1. Visit http://doi.org/10.13127/instance for download links")
    print("2. Run this script in Google Colab for large downloads")
    print("3. Or use metadata filtering to download only Norcia traces")

if __name__ == "__main__":
    main()