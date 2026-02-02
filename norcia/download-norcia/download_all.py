#!/usr/bin/env python3
"""
Unified download script for all Norcia 2016 earthquake datasets.
This script downloads data from both INGV and INSTANCE catalogs.
"""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    required_packages = ['pandas', 'obspy', 'requests', 'pyarrow']
    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("Missing required packages:", ', '.join(missing_packages))
        print("\nPlease install them using:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    return True

def download_ingv_catalog():
    """Download INGV catalog data using ObsPy FDSN."""
    print("\n" + "="*60)
    print("DOWNLOADING INGV CATALOG DATA")
    print("="*60)

    script_path = Path(__file__).parent / "download_norcia.py"

    if not script_path.exists():
        print(f"Error: {script_path} not found!")
        return False

    try:
        result = subprocess.run([sys.executable, str(script_path)],
                                capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ INGV catalog downloaded successfully")
            # Check if file was created - try both possible filenames
            output_file = Path(__file__).parent / "ingv_norcia_events_2016_2017.csv"
            if not output_file.exists():
                output_file = Path(__file__).parent.parent / "ingv_norcia_events_2016_2017.csv"
            if output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                print(f"  Output: {output_file.name} ({size_mb:.2f} MB)")
            return True
        else:
            print("✗ Error downloading INGV catalog:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"✗ Error running download_norcia.py: {e}")
        return False

def download_instance_metadata():
    """Download and process INSTANCE metadata."""
    print("\n" + "="*60)
    print("DOWNLOADING INSTANCE METADATA")
    print("="*60)

    script_path = Path(__file__).parent / "process_instance_metadata.py"

    if not script_path.exists():
        print(f"Error: {script_path} not found!")
        return False

    print("This will download a large file (~2.8 GB) and process it.")
    print("The download may take several minutes depending on your connection.")

    try:
        result = subprocess.run([sys.executable, str(script_path)],
                                capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ INSTANCE metadata downloaded and processed successfully")
            # Check if file was created - try both possible locations
            output_file = Path(__file__).parent / "norcia_2016_metadata.parquet"
            if not output_file.exists():
                output_file = Path(__file__).parent.parent / "norcia_2016_metadata.parquet"
            if output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                print(f"  Output: {output_file.name} ({size_mb:.2f} MB)")
            return True
        else:
            print("✗ Error processing INSTANCE metadata:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"✗ Error running process_instance_metadata.py: {e}")
        return False

def main():
    """Main function to coordinate all downloads."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Download Norcia 2016 earthquake datasets')
    parser.add_argument('-y', '--yes', action='store_true',
                        help='Skip confirmation prompt and proceed with downloads')
    parser.add_argument('--ingv-only', action='store_true',
                        help='Download only INGV catalog')
    parser.add_argument('--instance-only', action='store_true',
                        help='Download only INSTANCE metadata')
    args = parser.parse_args()

    print("\n" + "="*60)
    print("NORCIA 2016 EARTHQUAKE DATASET DOWNLOADER")
    print("="*60)

    # Check if we're in the right directory
    current_dir = Path.cwd()
    if current_dir.name == "download-norcia":
        # Change to parent directory
        os.chdir(current_dir.parent)
        print(f"Changed to parent directory: {Path.cwd()}")

    # Check requirements
    if not check_requirements():
        print("\nPlease install missing requirements and run again.")
        return 1

    print("\nThis script will download:")
    if not args.instance_only:
        print("1. INGV earthquake catalog via ObsPy FDSN (~400 KB)")
    if not args.ingv_only:
        print("2. INSTANCE metadata from Zenodo (~106 MB after processing)")

    # Ask for confirmation unless -y flag is provided
    if not args.yes:
        response = input("\nProceed with downloads? (y/n): ").strip().lower()
        if response != 'y':
            print("Download cancelled.")
            return 0

    # Track success
    success_count = 0
    total_tasks = 0

    # Determine what to download
    if not args.instance_only:
        total_tasks += 1
    if not args.ingv_only:
        total_tasks += 1

    # Download INGV catalog
    if not args.instance_only:
        if download_ingv_catalog():
            success_count += 1
        else:
            print("Warning: INGV catalog download failed, continuing...")

    # Download INSTANCE metadata
    if not args.ingv_only:
        if download_instance_metadata():
            success_count += 1
        else:
            print("Warning: INSTANCE metadata download failed.")

    # Summary
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    print(f"Completed: {success_count}/{total_tasks} downloads")

    if success_count == total_tasks:
        print("\n✓ All downloads completed successfully!")
        print("\nGenerated files:")
        # Check for files in both locations
        files_to_check = [
            ("ingv_norcia_events_2016_2017.csv", ["download-norcia", "."]),
            ("norcia_2016_metadata.parquet", ["download-norcia", "."])
        ]
        for filename, locations in files_to_check:
            for location in locations:
                if location == ".":
                    filepath = Path.cwd() / filename
                else:
                    filepath = Path.cwd() / location / filename
                if filepath.exists():
                    size_mb = filepath.stat().st_size / (1024 * 1024)
                    print(f"  - {filename} ({size_mb:.2f} MB)")
                    break
    else:
        print("\n⚠ Some downloads failed. Please check the error messages above.")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())