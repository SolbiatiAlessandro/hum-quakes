#!/usr/bin/env python3
"""
Download earthquake metadata for the Norcia/Central Italy region from INGV's FDSN service.

This script queries the official INGV (Istituto Nazionale di Geofisica e Vulcanologia)
FDSN Event Web Service to retrieve earthquake catalog data for the Norcia region during
the 2016-2017 seismic sequence.

Output: CSV file with earthquake metadata (time, location, magnitude, etc.)
"""

import csv
from datetime import datetime
from obspy import UTCDateTime
from obspy.clients.fdsn import Client
import pandas as pd

def download_norcia_catalog():
    """
    Download earthquake catalog from INGV for the Norcia region.
    """

    # Initialize INGV FDSN client
    print("Connecting to INGV FDSN service...")
    client = Client("INGV")

    # Define parameters for the query
    # Time window: 2016-01-01 to 2017-12-31
    starttime = UTCDateTime("2016-01-01T00:00:00")
    endtime = UTCDateTime("2017-12-31T23:59:59")

    # Region: Bounding box around Norcia (~100km radius)
    # Norcia coordinates: approximately 42.79°N, 13.09°E
    minlatitude = 41.5
    maxlatitude = 44.0
    minlongitude = 11.5
    maxlongitude = 14.5

    # Magnitude cutoff: M ≥ 2.5
    minmagnitude = 2.5

    print(f"Query parameters:")
    print(f"  Time window: {starttime} to {endtime}")
    print(f"  Region: Lat {minlatitude}°-{maxlatitude}°, Lon {minlongitude}°-{maxlongitude}°")
    print(f"  Minimum magnitude: {minmagnitude}")
    print()

    # Query the INGV catalog
    print("Querying INGV catalog...")
    try:
        catalog = client.get_events(
            starttime=starttime,
            endtime=endtime,
            minlatitude=minlatitude,
            maxlatitude=maxlatitude,
            minlongitude=minlongitude,
            maxlongitude=maxlongitude,
            minmagnitude=minmagnitude
        )
        print(f"Successfully retrieved {len(catalog)} events")
    except Exception as e:
        print(f"Error querying INGV service: {e}")
        return None

    return catalog

def catalog_to_dataframe(catalog):
    """
    Convert ObsPy Catalog object to pandas DataFrame.
    """

    events_data = []

    for event in catalog:
        # Get the preferred origin (location and time)
        origin = event.preferred_origin() or event.origins[0]

        # Get the preferred magnitude
        magnitude = event.preferred_magnitude() or (event.magnitudes[0] if event.magnitudes else None)

        event_dict = {
            'event_id': str(event.resource_id).split('/')[-1],
            'time': origin.time.datetime,
            'latitude': origin.latitude,
            'longitude': origin.longitude,
            'depth_km': origin.depth / 1000.0 if origin.depth is not None else None,
            'magnitude': magnitude.mag if magnitude else None,
            'magnitude_type': magnitude.magnitude_type if magnitude else None,
            'event_type': event.event_type,
            'evaluation_mode': origin.evaluation_mode,
            'evaluation_status': origin.evaluation_status
        }

        events_data.append(event_dict)

    df = pd.DataFrame(events_data)

    # Sort by time
    df = df.sort_values('time').reset_index(drop=True)

    return df

def validate_major_events(df):
    """
    Check if the major Norcia events are present in the dataset.
    """

    print("\nValidating major events:")

    major_events = [
        ("2016-08-24", "Amatrice earthquake", 6.0),
        ("2016-10-26", "First Visso earthquake", 5.9),
        ("2016-10-30", "Norcia earthquake", 6.5)
    ]

    for date_str, name, expected_mag in major_events:
        date = pd.to_datetime(date_str)

        # Find events on that date with magnitude > expected_mag - 0.3
        day_events = df[
            (df['time'].dt.date == date.date()) &
            (df['magnitude'] >= expected_mag - 0.3)
        ]

        if not day_events.empty:
            max_event = day_events.loc[day_events['magnitude'].idxmax()]
            print(f"  ✓ {date_str}: {name} - Found M{max_event['magnitude']:.1f} event")
        else:
            print(f"  ✗ {date_str}: {name} - NOT FOUND")

    # Print summary statistics
    print("\nDataset summary:")
    print(f"  Total events: {len(df)}")
    print(f"  Date range: {df['time'].min().date()} to {df['time'].max().date()}")
    print(f"  Magnitude range: {df['magnitude'].min():.1f} to {df['magnitude'].max():.1f}")
    print(f"  Magnitude distribution:")

    mag_bins = [2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 7.0]
    mag_counts = pd.cut(df['magnitude'], bins=mag_bins).value_counts().sort_index()
    for interval, count in mag_counts.items():
        print(f"    M{interval.left:.1f}-{interval.right:.1f}: {count} events")

def main():
    """
    Main function to download and save Norcia earthquake catalog.
    """

    # Download catalog
    catalog = download_norcia_catalog()
    if catalog is None:
        return

    # Convert to DataFrame
    print("\nConverting to DataFrame...")
    df = catalog_to_dataframe(catalog)

    # Validate major events
    validate_major_events(df)

    # Save to CSV
    output_file = "ingv_norcia_events_2016_2017.csv"
    print(f"\nSaving to {output_file}...")
    df.to_csv(output_file, index=False, date_format='%Y-%m-%d %H:%M:%S.%f')

    print(f"Successfully saved {len(df)} events to {output_file}")

    # Display first few rows
    print("\nFirst 5 events in the catalog:")
    print(df.head()[['time', 'latitude', 'longitude', 'depth_km', 'magnitude', 'magnitude_type']])

if __name__ == "__main__":
    main()