#!/usr/bin/env python3
"""
Process INSTANCE metadata for Norcia 2016 earthquake sequence.

This script:
1. Verifies the INSTANCE metadata structure
2. Filters to Norcia region (2016-2017)
3. Validates major events are present
4. Saves filtered subset as Parquet for efficient loading
"""

import pandas as pd
import numpy as np
from datetime import datetime

def verify_metadata_structure(df_sample):
    """
    Verify the metadata has the expected columns.
    """
    print("=== VERIFICATION ===")
    print(f"Columns: {len(df_sample.columns)}")
    print(f"Expected: ~115 columns")
    print()

    # Check for key columns we need
    required_columns = [
        'source_origin_time',
        'source_latitude_deg',
        'source_longitude_deg',
        'source_magnitude',
        'source_depth_km',
        'trace_E_snr_db',
        'trace_pga_perc',
        'station_code',
        'trace_name'
    ]

    missing = [col for col in required_columns if col not in df_sample.columns]

    if missing:
        print(f"❌ MISSING COLUMNS: {missing}")
        return False
    else:
        print("✅ All required columns present")

    print()
    print("Sample columns found (first 20):")
    for i, col in enumerate(df_sample.columns[:20]):
        print(f"  {i+1}. {col}")

    # Check for waveform-derived columns
    trace_cols = [col for col in df_sample.columns if col.startswith('trace_')]
    print(f"\nTrace/waveform columns found: {len(trace_cols)}")
    print("Sample trace columns:", trace_cols[:5])

    return True

def filter_norcia_region(df):
    """
    Filter to Norcia region and time window.
    """
    print("\n=== FILTERING TO NORCIA REGION ===")

    # Convert time column
    df['source_origin_time'] = pd.to_datetime(df['source_origin_time'])

    # Filter to Norcia region and time window
    # Extended time window for aftershock sequence: Aug 2016 - Jan 2017
    norcia = df[
        (df['source_origin_time'] >= '2016-08-01') &
        (df['source_origin_time'] <= '2017-01-31') &
        (df['source_latitude_deg'].between(42.5, 43.2)) &
        (df['source_longitude_deg'].between(12.8, 13.5))
    ].copy()

    print(f"Original traces: {len(df):,}")
    print(f"Norcia 2016 traces: {len(norcia):,}")
    print(f"Unique events: {norcia['source_id'].nunique():,}")
    print(f"Magnitude range: {norcia['source_magnitude'].min():.1f} - {norcia['source_magnitude'].max():.1f}")

    # Show temporal distribution
    norcia['month'] = norcia['source_origin_time'].dt.to_period('M')
    monthly_counts = norcia.groupby('month')['source_id'].nunique()
    print("\nEvents per month:")
    for month, count in monthly_counts.items():
        print(f"  {month}: {count} events")

    return norcia

def validate_mainshocks(norcia):
    """
    Check for the major Norcia sequence mainshocks.
    """
    print("\n=== VALIDATING MAINSHOCKS ===")

    # Find large events (M >= 5.5)
    mainshocks = norcia[norcia['source_magnitude'] >= 5.5].copy()

    if not mainshocks.empty:
        # Group by event and show first trace per event
        mainshock_events = mainshocks.groupby('source_id').first().reset_index()
        mainshock_events = mainshock_events.sort_values('source_origin_time')

        print(f"Found {len(mainshock_events)} mainshocks (M >= 5.5):")
        print()

        for idx, event in mainshock_events.iterrows():
            print(f"Event {idx+1}:")
            print(f"  Time: {event['source_origin_time']}")
            print(f"  Magnitude: M{event['source_magnitude']:.1f}")
            print(f"  Location: {event['source_latitude_deg']:.3f}°N, {event['source_longitude_deg']:.3f}°E")
            print(f"  Depth: {event['source_depth_km']:.1f} km")
            print()

        # Check for specific expected events
        expected_dates = [
            ("2016-08-24", "Amatrice", 6.0),
            ("2016-10-26", "Visso", 5.9),
            ("2016-10-30", "Norcia", 6.5)
        ]

        print("Checking for expected mainshocks:")
        for date_str, name, expected_mag in expected_dates:
            date = pd.to_datetime(date_str)
            # Look for events on that day with similar magnitude
            day_events = mainshock_events[
                (mainshock_events['source_origin_time'].dt.date == date.date()) &
                (mainshock_events['source_magnitude'] >= expected_mag - 0.3)
            ]

            if not day_events.empty:
                event = day_events.iloc[0]
                print(f"  ✓ {date_str} {name}: Found M{event['source_magnitude']:.1f}")
            else:
                print(f"  ✗ {date_str} {name}: NOT FOUND")
    else:
        print("❌ No mainshocks found (M >= 5.5)")

    return mainshocks

def main():
    """
    Main processing function.
    """

    # First, load a sample to verify structure
    print("Loading sample to verify structure...")
    df_sample = pd.read_csv('metadata_Instance_events_v3.csv', nrows=1000)

    if not verify_metadata_structure(df_sample):
        print("\n❌ Metadata structure verification failed!")
        return

    # Now load the full dataset
    print("\n" + "="*50)
    print("Loading full INSTANCE metadata (this may take a minute)...")
    df = pd.read_csv('metadata_Instance_events_v3.csv')
    print(f"Loaded {len(df):,} traces")

    # Filter to Norcia region
    norcia = filter_norcia_region(df)

    if norcia.empty:
        print("\n❌ No data found for Norcia region!")
        return

    # Validate mainshocks
    mainshocks = validate_mainshocks(norcia)

    # Save filtered dataset
    print("\n=== SAVING FILTERED DATASET ===")

    # Save as Parquet for efficient loading
    output_file = 'norcia_2016_metadata.parquet'
    norcia.to_parquet(output_file, index=False)
    print(f"Saved {len(norcia):,} traces to {output_file}")

    # Also save just the event catalog (unique events)
    events = norcia.groupby('source_id').first()[
        ['source_origin_time', 'source_latitude_deg', 'source_longitude_deg',
         'source_depth_km', 'source_magnitude']
    ].reset_index()
    events.to_csv('norcia_2016_events_from_instance.csv', index=False)
    print(f"Saved {len(events):,} unique events to norcia_2016_events_from_instance.csv")

    # Print summary statistics
    print("\n=== SUMMARY ===")
    print(f"Total traces: {len(norcia):,}")
    print(f"Unique events: {norcia['source_id'].nunique():,}")
    print(f"Unique stations: {norcia['station_code'].nunique():,}")
    print(f"Date range: {norcia['source_origin_time'].min()} to {norcia['source_origin_time'].max()}")
    print(f"Magnitude range: M{norcia['source_magnitude'].min():.1f} to M{norcia['source_magnitude'].max():.1f}")

    # Sample of available features
    print("\nSample waveform features available:")
    trace_cols = [col for col in norcia.columns if col.startswith('trace_')]
    for col in trace_cols[:10]:
        print(f"  - {col}")
    print(f"  ... and {len(trace_cols)-10} more trace features")

if __name__ == "__main__":
    main()