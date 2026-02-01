# Norcia 2016 Earthquake Anomaly Detection Baseline

## Project Goal

Determine whether there is a detectable regime change in seismic activity before the Norcia 2016 mainshocks, and later evaluate whether animal behavior data adds predictive value.

**Core question**: "Is there a measurable, reproducible signal change in the hours–days before the Norcia mainshocks?"

**Animal question** (later): "Does adding animal features increase that signal?"

---

## Notebooks

| Phase | Notebook | Purpose |
| --- | --- | --- |
| 0 | `norcia_phase0_explore.ipynb` | Load `norcia_2016_metadata.parquet`, summarize, and save `norcia_events.parquet`. |
| 1 | `norcia_phase1_windows.ipynb` | Define pre-event/background/post-event windows and export `windows.csv`. |

---

## Input Data

`norcia_2016_metadata.parquet` is the pre-filtered metadata table for the Norcia 2016 sequence (derived from INSTANCE metadata). It should live alongside the notebooks and is the default input for Phase 0 and an accepted input for Phase 1 if Phase 0 has not been run.

---

## Implementation Plan (Phase 0 → Phase 1)

1. **Phase 0 notebook:** Load `norcia_2016_metadata.parquet`, validate key columns, filter to the Norcia region/time window (if needed), summarize counts and magnitudes, and save `norcia_events.parquet` for reuse.
2. **Windowing draft:** Enumerate pre-event, background, and post-event window definitions for each mainshock (2h/6h/12h/24h horizons), and ensure non-overlap rules are explicit.
3. **Data checklist:** Record required columns and any missing fields from metadata; document fallbacks (e.g., skip waveform-derived stats if absent).
4. **Plot review:** Verify that timeline and spatial plots look reasonable (e.g., elevated counts around mainshocks, locations inside bounding box).
5. **Readiness gate:** Proceed to Phase 1 once the parquet is saved and summary stats match expectations (event counts, magnitude ranges).

---

## Approach: Anomaly Detection (Not Forecasting)

We are NOT building an earthquake predictor. We are building a **regime change detector** that asks: "Does this time window look different from normal?"

| Aspect | Forecasting (avoided) | Anomaly Detection (our approach) |
|--------|----------------------|----------------------------------|
| Claim | "I predict earthquakes" | "Something changed before this earthquake" |
| Labels | Rare binary (0.1% positive) | Balanced by design |
| Failure mode | "Model doesn't work" | "No detectable regime change exists" (still a finding) |
| Adding animals | Retrain whole model | Just add column, compare scores |

---

## Data Source

**INSTANCE Dataset** (Italian Seismic Dataset for ML)
- Metadata CSV: ~1.1 GB (all we need for baseline)
- 115 pre-computed features per trace
- Includes source info (time, location, magnitude) and trace-level stats (SNR, PGA, RMS)

**Key insight**: The metadata already contains aggregated waveform statistics. We don't need to load the 156GB waveform HDF5 for the baseline.

---

## Target Events: Norcia 2016 Mainshocks

| Date | Time (UTC) | Magnitude | Name |
|------|------------|-----------|------|
| 2016-08-24 | 01:36 | M6.0 | Amatrice |
| 2016-10-26 | 19:18 | M5.9 | Visso |
| 2016-10-30 | 06:40 | M6.5 | Norcia (main) |

Geographic filter: lat 42.5–43.2, lon 12.8–13.5

---

## Phase 0: Understand the Data

**Objective**: Load and explore the INSTANCE metadata for the Norcia region.

**Tasks**:
1. Load metadata CSV
2. Verify column names match documentation
3. Filter to Norcia region and time window (Aug 2016 – Jan 2017)
4. Generate summary statistics: event counts, magnitude distribution, temporal patterns
5. Visualize: event timeline, epicenter map, magnitude histogram
6. Save filtered dataset as parquet for faster reloading

**Output**: `norcia_events.parquet`, basic understanding of data structure

**Key columns to verify**:
- source_origin_time, source_latitude_deg, source_longitude_deg
- source_magnitude, source_depth_km
- trace_E_snr_db, trace_pga_perc, station_code

---

## Phase 1: Define Time Windows

**Objective**: Create labeled time windows for analysis (pre-event, background, post-event).

This is the most important design decision.

### Window Types

**Pre-event windows**
- Definition: Fixed-duration windows ending before each mainshock
- Horizons to test: 2h, 6h, 12h, 24h before mainshock
- Window duration: 1 hour
- Example: For 6h horizon before Oct 30 M6.5, window = [Oct 30 00:40, Oct 30 01:40]

**Background windows**
- Definition: Random windows from "quiet" periods
- Constraints:
  - No M≥4 event within ±48 hours
  - Match time-of-day distribution of pre-event windows (control for diurnal effects)
  - Sample 5–10x more background than pre-event windows
- Purpose: Establish baseline "normal" activity

**Post-event windows**
- Definition: Windows immediately after mainshocks (1–2 hours post)
- Purpose: Sanity check — these should score high (aftershocks)
- Helps verify we're detecting real activity, not noise

### Critical Design Choices

- **No overlap**: Pre-event windows must not overlap with each other or aftershock sequences
- **Parametrize horizons**: Run analysis for 2h, 6h, 12h, 24h separately to find where signal is strongest
- **Control for time-of-day**: Background windows should have same distribution of hours as pre-event

**Output**: `windows.csv` with columns [window_id, start_time, end_time, window_type, hours_before_mainshock]

---

## Phase 2: Compute Features Per Window

**Objective**: For each time window, compute aggregate seismic features from all events within that window.

### Feature Categories

**Event-based features** (from source columns):
| Feature | Computation | Interpretation |
|---------|-------------|----------------|
| n_events | count of events | Activity level |
| max_magnitude | max(source_magnitude) | Largest event |
| mean_magnitude | mean(source_magnitude) | Typical size |
| cumulative_moment | sum(10^(1.5*mag)) | Total energy release |
| mean_depth_km | mean(source_depth_km) | Average depth |
| depth_std_km | std(source_depth_km) | Depth variability |
| spatial_spread_km | std of lat/lon converted to km | Clustering vs. dispersion |

**Network-based features** (from station columns):
| Feature | Computation | Interpretation |
|---------|-------------|----------------|
| n_stations | nunique(station_code) | Detection coverage |
| n_traces | count of traces | Data volume |

**Waveform-derived features** (from trace columns, already in metadata):
| Feature | Computation | Interpretation |
|---------|-------------|----------------|
| mean_snr | mean(trace_E_snr_db) | Average signal quality |
| max_snr | max(trace_E_snr_db) | Best signal in window |
| mean_pga | mean(trace_pga_perc) | Average ground motion |
| max_pga | max(trace_pga_perc) | Peak ground motion |
| mean_rms | mean(trace_E_rms_counts) | Average energy |

**Advanced features** (if enough events per window):
| Feature | Computation | Interpretation |
|---------|-------------|----------------|
| b_value | Gutenberg-Richter slope | Stress state indicator |
| mc | Magnitude of completeness | Catalog quality |

### Handling Empty Windows

Some background windows may have zero events. Options:
- Set features to 0 or NaN
- Use small epsilon for log-transformed features
- Document which windows are empty

**Output**: `features.csv` with columns [window_id, window_type, hours_before, n_events, max_magnitude, ...]

---

## Phase 3: Baseline Analysis

**Objective**: Compare feature distributions between pre-event and background windows. Compute a seismic anomaly score.

### Statistical Comparison

For each feature:
1. Compare distributions: pre-event vs background
2. Statistical tests: Mann-Whitney U (non-parametric), t-test
3. Effect size: Cohen's d or similar
4. Visualize: boxplots, histograms with both distributions

### Seismic Score Options

**Option A: Single best feature**
- seismic_score = normalized(n_events) or normalized(cumulative_moment)
- Simplest, most interpretable

**Option B: Composite z-score**
- seismic_score = mean of z-scores across top features
- Combines multiple signals

**Option C: Mahalanobis distance**
- seismic_score = distance from background centroid in feature space
- Accounts for feature correlations

**Option D: Simple classifier**
- Train logistic regression: background vs pre-event
- seismic_score = predicted probability
- Risk: overfitting with small pre-event sample

Recommendation: Start with Option A or B, try others if needed.

### Evaluation Metrics

| Metric | What it measures |
|--------|------------------|
| AUC-ROC | Overall separability |
| Precision at fixed recall | How many false alarms for X% detection |
| Statistical significance | Is the difference real or noise? |

### Expected Outcomes

**Success looks like**:
- Pre-event windows have systematically higher seismic_score than background
- AUC 0.6–0.7 = weak but detectable signal
- p < 0.05 for key features

**Null result**:
- AUC ~0.5, no significant differences
- Still valuable: tells us there's no catalog-level precursor

**Output**: 
- `seismic_scores.csv`: [window_id, window_type, seismic_score]
- Summary statistics and plots
- Reported AUC and p-values

---

## Phase 4: Sanity Checks

**Objective**: Verify the baseline is working correctly and not learning spurious patterns.

### Required Tests

**Test 1: Label shuffle**
- Randomly permute window_type labels
- Re-run analysis
- Expected: AUC drops to ~0.5

**Test 2: Post-event windows**
- Apply seismic_score to post-event windows
- Expected: High scores (aftershocks create activity)
- If post-event scores are low, something is wrong

**Test 3: Different time period**
- Apply same analysis to 2015 (no major mainshocks)
- Pick arbitrary "mainshock" times
- Expected: No systematic pre-"event" elevation

**Test 4: Time-of-day control**
- Check if pre-event windows happen at different hours than background
- If yes, we might be learning diurnal patterns, not precursors

**Test 5: Feature importance**
- Which features drive the seismic_score?
- Are they physically meaningful?

### Failure Modes to Watch For

| Problem | Symptom | Solution |
|---------|---------|----------|
| Overfitting | Perfect train AUC, poor test | Simpler model, more background windows |
| Leakage | Using future information | Check window definitions |
| Aftershock contamination | Pre-event includes aftershocks from previous mainshock | Increase gap between events |
| Class imbalance | Model predicts all background | Ensure balanced evaluation |

**Output**: Documented validation results, confidence in (or concerns about) the baseline

---

## Phase 5: Prepare for Animal Data

**Objective**: Create a clean, documented table ready for animal feature integration.

### Final Table Structure

```
window_id | start_time | end_time | window_type | seismic_score | n_events | ... | animal_activity
001       | 2016-10-29 23:40 | 2016-10-30 00:40 | pre_event | 0.72 | 45 | ... | NaN
002       | 2016-09-15 14:00 | 2016-09-15 15:00 | background | 0.23 | 12 | ... | NaN
```

### Documentation for Animal Merge

- Timestamp format: ISO 8601 UTC
- Window duration: 1 hour
- Required animal columns: timestamp, activity metrics
- Alignment method: match animal data to window start_time

### Analysis Plan When Animals Arrive

1. Compute animal features per window (activity level, variance, anomaly score)
2. Add to feature table
3. Re-run Phase 3 analysis with combined features
4. Compare: AUC_seismic_only vs AUC_combined
5. Report improvement (or lack thereof)

**Key question**: Does adding animal_score increase separability beyond seismic_score alone?

**Output**: `final_features.csv` with placeholder for animal columns, documentation of format

---

## Success Criteria

### Minimum Viable Result

- Complete pipeline from metadata to seismic_score
- Documented AUC for seismic-only baseline
- Clean table ready for animal data

### Ideal Result

- Weak but consistent signal in pre-event windows (AUC 0.6–0.7)
- Clear feature interpretation (e.g., "event rate increases 6h before")
- Sanity checks all pass
- Ready to answer: "Does animal data improve AUC by X%?"

### Valuable Null Result

- No detectable regime change in catalog data
- Documents that precursor signal (if any) is not in event statistics
- Motivates looking at waveform-level features or other data

---

## Future Extensions (Out of Scope for Baseline)

- Waveform embeddings using CNN or pretrained EQTransformer
- Multiple prediction horizons (operational forecasting)
- GPS/InSAR data integration
- Proper train/test splits across different earthquake sequences
- Hyperparameter optimization

---

## Timeline Estimate

| Phase | Effort | Dependencies |
|-------|--------|--------------|
| Phase 0: Explore data | 2–4 hours | Metadata downloaded |
| Phase 1: Define windows | 2–4 hours | Phase 0 complete |
| Phase 2: Compute features | 2–4 hours | Phase 1 complete |
| Phase 3: Baseline analysis | 4–6 hours | Phase 2 complete |
| Phase 4: Sanity checks | 2–4 hours | Phase 3 complete |
| Phase 5: Prepare for animals | 1–2 hours | Phase 4 complete |

**Total**: ~15–25 hours of focused work

---

## Open Questions

1. What is Wikelski's claimed timing for animal response? (Determines which horizons to emphasize)
2. Are there other M≥5 events in the sequence we should include as additional mainshocks?
3. What format will the animal data arrive in?
4. Do we have animal data coverage for all three mainshocks or only some?
