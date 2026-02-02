# Seismic Multimodal Transformer Project: Context Document

## Project Overview

This project investigates whether animal behavior data adds predictive signal for earthquake precursors beyond seismic data alone. The long-term vision is a multimodal foundation model that integrates seismic waveforms, earthquake catalogs, GPS/InSAR deformation data, and animal behavior into a unified framework for anomaly detection before major earthquakes.

The research is a collaboration with the Wikelski group (Max Planck Institute), authors of the 2020 animal behavior paper showing collective behavioral changes in farm animals before the 2016 Norcia earthquake sequence in Italy. This is an offline ML research project with no publication pressure — the goal is rigorous scientific exploration.

---

## Scientific Motivation

### The Core Question

Earthquake prediction remains one of the hardest problems in geophysics. While deterministic prediction (exact time, location, magnitude) is likely impossible, detecting regime changes or anomalies in the period before major earthquakes may be feasible.

The Wikelski et al. (2020) study documented unusual collective animal behavior (cattle, sheep, dogs) in the weeks and hours before the Norcia mainshocks. The hypothesis is that animals may sense precursory signals (electromagnetic changes, gas emissions, micro-vibrations) that are difficult to detect with conventional instruments.

### Why This Matters

- If animal behavior adds signal beyond seismic data → novel precursor monitoring approach
- If animal behavior adds no signal → still valuable null result, closes a research avenue
- Either outcome contributes to scientific understanding

### The 2016 Norcia Earthquake Sequence

Target events for the study:
- 2016-08-24 01:36 UTC: M6.0 Amatrice earthquake
- 2016-10-26 19:18 UTC: M5.9 Visso earthquake  
- 2016-10-30 06:40 UTC: M6.5 Norcia mainshock

Geographic region: Central Italy (lat 42.5-43.2, lon 12.8-13.5)

---

## Methodological Approach: Anomaly Detection, Not Forecasting

A critical framing decision: this is **anomaly detection**, not earthquake forecasting.

### Why Not Forecasting

- Earthquake forecasting claims are scientifically contentious
- Class imbalance is extreme (0.1% positive rate for major events)
- Would require making claims about "predicting earthquakes"

### Anomaly Detection Framing

- Question: "Is there detectable regime change in seismic activity before mainshocks?"
- Animal question: "Does adding animal features increase that signal?"
- Labels are balanced by design (pre-event windows vs background windows)
- Failure mode: "No detectable regime change" — still a valid scientific finding
- Animal integration: Add features as columns, compare AUC with and without

---

## Phase 1: Seismic Baseline (Current Focus)

Before adding animal data, we must establish whether seismic data alone shows detectable pre-event anomalies.

### Data Sources

**INGV Earthquake Catalog**
- Already downloaded: 4,067 events for Norcia region
- Basic fields: time, lat, lon, magnitude, depth
- Used for simple catalog-based features

**INSTANCE Dataset (Italian Seismic Dataset)**
- Metadata: ~1.2M traces, 115 columns including waveform statistics
- Source: http://repo.pi.ingv.it/instance/
- Contains pre-computed features: SNR, PGA, RMS, station info
- Norcia 2016 subset: estimated 50-150K traces
- Full waveforms available (156GB HDF5) but not needed for baseline

### Baseline Implementation Plan

**Phase 0: Data Preparation**
- Load INSTANCE metadata
- Filter to Norcia region and Aug 2016 - Jan 2017
- Output: norcia_events.parquet

**Phase 1: Time Window Definition (Critical Design Step)**
- Pre-event windows: Fixed duration before each mainshock (test 2h, 6h, 12h, 24h horizons)
- Background windows: Random quiet periods (no M≥4 within ±48h)
- Post-event windows: 1-2h after mainshocks (sanity check)
- Output: windows.csv

**Phase 2: Feature Engineering**
- Event-based: n_events, max_magnitude, cumulative_moment, spatial_spread
- Network-based: n_stations, n_traces
- Waveform-derived (from metadata): mean_snr, max_pga, mean_rms
- Advanced: b-value, magnitude of completeness
- Output: features.csv

**Phase 3: Baseline Analysis**
- Statistical comparison: Mann-Whitney U, t-test, Cohen's d
- Seismic score options: best single feature, composite z-score, Mahalanobis distance, logistic regression
- Evaluation: AUC-ROC, precision at fixed recall
- Expected outcome: AUC 0.6-0.7 (weak but detectable) or AUC ~0.5 (null result)

**Phase 4: Sanity Checks**
- Label shuffle → AUC should drop to ~0.5
- Post-event windows → should score high (aftershocks)
- Different time period (2015) → no systematic elevation
- Time-of-day control → not learning diurnal patterns

**Phase 5: Prepare for Animal Integration**
- Final table: [window_id, start_time, end_time, window_type, seismic_score, features..., animal_activity (NaN)]
- When animal data arrives: compute animal features per window, add columns, re-run analysis, compare AUC

---

## Literature Review: Transformer Architectures for Seismology

### The "Fake Transformer" Problem

Many seismic papers use "transformer" or "attention" loosely. Important distinction:

**Hybrid Models (Not True Transformers)**
- EQTransformer (2020): CNN + ResNet + Bi-LSTM + Attention
- Core architecture is CNN/LSTM; attention is auxiliary
- Very successful for phase picking but not foundation models

**True Transformer Models**
- Self-attention is the primary mechanism
- Follow BERT, GPT, ViT, or Wav2Vec2 patterns
- Use patch/token embeddings fed directly into transformer blocks

### Key Seismic Foundation Models

**SeisLM (Oct 2024, NeurIPS Workshop)**
- Architecture: ConvNet → Vector Quantization → Masked Transformer (BERT-style)
- Training: Self-supervised contrastive loss on unlabeled waveforms
- Tasks: Event detection, phase-picking, foreshock-aftershock classification
- Datasets: INSTANCE, STEAD, ETHZ, and others
- Code: https://github.com/liutianlin0121/seisLM

**SeisMoLLM (Feb 2025)**
- Architecture: Multi-scale ConvNet → Latent patching → Frozen GPT-2 with LoRA
- Key insight: Cross-modal transfer from language model to seismic domain
- State-of-the-art on DiTing and STEAD across five tasks
- Demonstrates that LLM pretraining transfers to waveforms

**SeisCLIP (Sep 2023, IEEE TGRS 2024)**
- Architecture: Transformer encoder (spectrum) + MLP encoder (metadata)
- Training: CLIP-style contrastive learning
- Two modalities: Seismic waveform spectra + event metadata (8 types)
- Most relevant to our multimodal goals

**SafeNet (Mar 2025, Nature Scientific Reports)**
- Architecture: ResNet (maps) + FC layers (catalog) → LSTM → Vision Transformer
- Two modalities: Geologic/fault maps + earthquake catalog features
- Task: Intermediate-term earthquake forecasting

### Gap in Literature

No published work combines:
- Seismic data (waveforms or catalogs) with animal behavior
- Modern transformer architectures for earthquake precursor detection
- Multimodal fusion for non-seismic precursor signals

---

## Multimodal Transformer Architectures: Background

### Fusion Strategies

**Early Fusion (Single Transformer)**
```
[Modality_A tokens][SEP][Modality_B tokens] → Single Transformer → Output
```
- All tokens attend to all tokens
- Full cross-modal interaction
- Expensive: O(n²) attention

**Late Fusion (Separate Encoders)**
```
Modality_A → Encoder_A → emb_A ─┐
                                 ├→ Combine → Output
Modality_B → Encoder_B → emb_B ─┘
```
- Modalities processed independently
- Combined only at embedding level
- Cheaper, modular, can use pretrained encoders

**Cross-Attention (Middle Fusion)**
```
Modality_A → Self-attention → Cross-attend to B → Output
                                     ↑
Modality_B → Self-attention ─────────┘
```
- One modality queries the other
- Selective attention, more efficient than full concatenation

### CLIP Architecture (Foundational)

CLIP is **not** a multimodal transformer — it's two separate unimodal encoders trained together:

```
Image → Image Encoder → image_emb ─┐
                                    ├→ Contrastive Loss
Text  → Text Encoder  → text_emb  ─┘
```

Training objective: Maximize similarity for matching (image, text) pairs, minimize for non-matching.

SeisCLIP follows this pattern exactly: spectrum encoder + metadata encoder + contrastive loss.

### Many-Modality Models

**ImageBind (Meta, 2023) — 6 Modalities**
- Images, text, audio, depth, thermal, IMU
- Key insight: Only need image-paired data; other modalities align transitively
- Image serves as "anchor" modality

**Meta-Transformer (2023) — 12 Modalities**
- Text, images, point clouds, audio, video, time series, tabular data
- Frozen encoder with modality-specific tokenizers

**4M-21 (EPFL, 2024) — 21+ Modalities**
- RGB, depth, normals, segmentation, edges, text, poses, bounding boxes
- Discrete tokenization for all modalities

### The Anchor Modality Insight

ImageBind's key contribution: You don't need paired data for all modality combinations.

```
Training pairs needed:          NOT needed:
(Image, Text)    ✓              (Audio, Text)
(Image, Audio)   ✓              (Depth, IMU)
(Image, Depth)   ✓              (Audio, Thermal)
```

After training, Audio↔Text alignment emerges because both are aligned to Image.

For seismology, the anchor could be:
- Waveform/spectrogram (everything relates to seismic signal)
- Time window (all modalities share timestamps)
- Event (earthquake occurrence links everything)

---

## Architectural Decision: SeisCLIP → SeisImageBind Path

### Why SeisCLIP is the Right Starting Point

1. **Proven architecture**: CLIP-style contrastive learning works
2. **Directly applicable**: Spectrum + metadata mirrors our spectrum + catalog
3. **Extensible**: Add modalities by adding (anchor, new_modality) pairs
4. **Interpretable**: Late fusion allows understanding each modality's contribution

### Extension Path to Many Modalities

**Current SeisCLIP:**
```
(Spectrum, Metadata) → contrastive loss
```

**Phase 2 — Add catalog:**
```
(Spectrum, Metadata) → contrastive loss
(Spectrum, Catalog)  → contrastive loss
```

**Phase 3 — Add animal:**
```
(Spectrum, Metadata) → contrastive loss
(Spectrum, Catalog)  → contrastive loss
(Spectrum, Animal)   → contrastive loss
```

Emergent alignment: Catalog ↔ Animal alignment emerges even though never directly trained.

### Compatibility with ImageBind Methodology

Contrastive learning is exactly how ImageBind works. The math is identical:

```python
# For batch of N pairs (Anchor, X)
similarity = anchor_emb @ x_emb.T  # (N, N) matrix
labels = torch.arange(N)           # diagonal = matches
loss = cross_entropy(similarity, labels)

# ImageBind: apply to each (Image, X) pair
# SeisImageBind: apply to each (Spectrum, X) pair
```

No architectural change needed. Just more training pairs with spectrum as anchor.

---

## Practical Implementation Path

### Near-term (Catalog Baseline)

1. Compute catalog features per time window
2. Train simple classifier (logistic regression)
3. Evaluate AUC for pre-event vs background
4. When animal data arrives: add animal features, compare AUC

### Medium-term (SeisCLIP Features)

1. Download INSTANCE waveforms for Norcia region
2. Run pretrained SeisCLIP (or train on INSTANCE)
3. Extract spectrum embeddings per time window
4. Use embeddings as features instead of hand-crafted catalog features
5. Compare: AUC_catalog vs AUC_seisclip

### Long-term (Full Multimodal)

1. Add GPS/InSAR deformation data as modality
2. Add animal behavior as modality  
3. Train SeisImageBind with spectrum as anchor
4. Evaluate cross-modal retrieval and anomaly detection
5. Analyze which modalities contribute signal

---

## Key Open Questions

1. **Animal data timing**: What did Wikelski claim for animal response timing? (Determines which horizons to emphasize: 2h, 6h, 12h, 24h)

2. **Animal data format**: What format will the bio-logger data arrive in? (GPS tracks, accelerometer, activity indices?)

3. **Animal data coverage**: Do we have animal data for all three mainshocks or subset?

4. **Waveform necessity**: Is catalog baseline sufficient, or do we need INSTANCE waveforms?

5. **Compute resources**: Training SeisCLIP from scratch vs using pretrained weights?

---

## File Locations

- Transcript of full conversation: `/mnt/transcripts/2026-02-01-18-54-16-norcia-earthquake-ml-baseline-plan.txt`
- Previous planning document: `/mnt/user-data/outputs/norcia_anomaly_detection_plan.md`
- Download instructions: `/mnt/user-data/outputs/download_instance_metadata_instructions.md`

---

## Summary of Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framing | Anomaly detection, not forecasting | Avoids controversial claims, balanced labels |
| Baseline approach | Catalog features first | Simple, interpretable, establishes signal existence |
| Target dataset | INSTANCE metadata | Has pre-computed waveform statistics, avoids 156GB download |
| Multimodal architecture | SeisCLIP → ImageBind pattern | Proven, extensible, compatible with contrastive learning |
| Fusion strategy | Late fusion (separate encoders) | Simpler with limited animal data, interpretable |
| Anchor modality | Waveform/spectrum | Natural pairing with all other modalities |

---

## References

### Seismic ML
- SeisLM: https://arxiv.org/abs/2410.15765
- SeisMoLLM: https://arxiv.org/abs/2502.19960  
- SeisCLIP: https://arxiv.org/abs/2309.02320
- EQTransformer: https://www.nature.com/articles/s41467-020-17591-w
- SafeNet: https://www.nature.com/articles/s41598-025-93877-7

### Multimodal Foundations
- CLIP: https://arxiv.org/abs/2103.00020
- ImageBind: https://arxiv.org/abs/2305.05665
- Meta-Transformer: https://arxiv.org/abs/2307.10802

### Animal Behavior
- Wikelski et al. (2020): Animal behavior before earthquakes (Norcia study)

---

*Document created: February 2026*
*For use by AI agents working on this project*
