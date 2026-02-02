Get a local CSV file containing earthquake event metadata for the Norcia / Central Italy region, suitable for offline ML experiments.

You are not downloading waveforms — only metadata.

What you are downloading (important clarity)

You are downloading:

earthquake event metadata

time

latitude / longitude

depth

magnitude

event ID

You are not downloading:

seismic waveforms

station response files

raw sensor data

Result:

A single CSV file, a few MB in size.

Step 1 — Decide the scope (do this first)

Before touching anything, decide:

Time window

Example: 2016-01-01 → 2017-12-31

Region

Bounding box around Norcia (≈ 100 km)

Magnitude cutoff

Example: M ≥ 2.5 (or higher if you want fewer rows)

Write these down — they define your dataset.

Step 2 — Install a minimal seismology client locally

On macOS, the standard toolchain is:

Python (via Homebrew, pyenv, or system Python)

A seismic client that understands INGV’s web services

You will install:

ObsPy (the de facto standard in seismology)

This gives you access to INGV’s official FDSN Event service, which is how INGV intends this data to be retrieved.

Step 3 — Query the official INGV catalog service

INGV does not provide a downloadable CSV.

Instead:

You query their FDSN Event Web Service

The service returns structured metadata (QuakeML)

Your local tooling converts that to CSV

This is:

the authoritative source

what papers and researchers use

what INGV documents recommend

You are not scraping a website or downloading a secondary mirror.

Step 4 — Convert metadata to a flat table

Once the catalog is downloaded:

Extract one row per earthquake

Keep only fields needed for ML:

timestamp (UTC)

latitude

longitude

depth

magnitude

magnitude type

event ID

Flattening is your responsibility — the upstream format is hierarchical by design.

This is normal in geophysics.

Step 5 — Save as CSV (your artifact)

Save the result as something like:

ingv_norcia_events_2016_2017.csv


This CSV:

is reproducible

can be versioned

can be shared

becomes the input to your ML feature pipeline

This file is your dataset, derived from INGV.

Step 6 — Sanity-check the data (non-optional)

Before using it:

Confirm the main Norcia events are present:

Aug 24, 2016

Oct 26, 2016

Oct 30, 2016

Check:

number of rows

date range

magnitude distribution

If these don’t match expectations, stop and fix scope.

Step 7 — Keep it separate from waveforms

For now:

Store this CSV in a /data/catalogs/ folder

Do not mix with waveform data

Do not try to “upgrade” it prematurely

This catalog is your Phase-1 baseline input.

Why this is the best local approach

Uses INGV’s official API

Matches how published papers obtain catalogs

Produces a portable CSV

Minimal disk usage

No dependency on Colab or cloud tools

Scales later if you want more regions or years
