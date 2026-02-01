# General Context for AI Agents reading this, might not be accurate, just to give a vibe of the project

# [Hum Labs] Earthquake MVP

**Authors**
Alessandro Solbiati
Allie Hutchison ([allie.a.g.hutchison@gmail.com](mailto:allie.a.g.hutchison@gmail.com))

**Creation date**: 9 Dec 2025

---

## 1. Motivation

Earthquake forecasting remains one of the most challenging and controversial problems in geophysics. While real-time **nowcasting** (detection, phase picking, magnitude estimation) has seen major advances with deep learning, **forecasting**—identifying precursory signals before rupture—remains largely unexplored due to data sparsity, noise, and scientific risk.

The 2016 Central Italy (Norcia–Amatrice–Visso) earthquake sequence is uniquely suited for exploratory ML work because it combines:

* Dense seismic instrumentation
* Continuous GPS and InSAR coverage
* Carefully studied pre-slip hypotheses
* A rare animal-behavior dataset temporally co-located with seismic activity

This MVP focuses on assessing whether **animal agitation data contains measurable predictive signal** related to pre-slip processes, and how that signal compares to standard geophysical modalities.

---

## 2. Goal of the MVP

**Primary goal**
Assess the predictive power of animal agitation data for identifying pre-slip processes prior to major earthquakes in the Norcia region.

Concretely:

* Determine whether animal agitation data can predict the occurrence of pre-slip events
* Quantify predictive performance (e.g. accuracy, AUROC, lead time)
* Compare animal-based signals against traditional geophysical data

**Key question**

> Can animal agitation data predict pre-slip events with statistically meaningful accuracy, and does it add information beyond seismic and geodetic data?

---

## 3. Evaluation & Labels

* Pre-slip event labels are **manually vetted by Allie Hutchison** based on published analyses of the 2016 Norcia sequence.
* Labels focus on **pre-slip windows**, not mainshock occurrence.
* Evaluation will use **strict time-based splits** to avoid temporal leakage.

---

## 4. Data Modalities

We consider **five data types**, analyzed independently and comparatively.

### 4.1 Animal Data (Primary Focus)

* Animal activity / agitation time series
* CSV format (to be sourced)
* Limited spatial coverage, high novelty

### 4.2 Seismic Data

* Continuous seismic waveforms
* Event-based and background noise
* Includes slow earthquake / tremor signals

### 4.3 GPS / Geodetic Data

* Continuous station displacement time series
* mm-scale deformation
* Hypothesized short-term pre-slip signals (hours)

### 4.4 InSAR

* Satellite-derived surface deformation fields
* Sparse temporal resolution
* Useful for mechanism understanding, less for short-term prediction

### 4.5 Earthquake Catalogs

* Event times, magnitudes, locations
* Used as context and baseline only

---

## 5. Modeling Strategy

This MVP emphasizes **representation learning and comparative forecasting**, not end-to-end earthquake prediction.

### 5.1 Embedding-First Philosophy

Rather than predicting earthquakes directly, models learn embeddings of time-series behavior and are evaluated on their ability to discriminate:

* Pre-slip vs background periods
* Anomalous vs typical behavior

---

## 6. Model Families Considered

| Model Family                                            | Good for MVP? | Pros                                                                                                          | Cons                                                                         |
| ------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| **Tree Ensembles (XGBoost)**                            | ✅ Yes         | Fast, interpretable, strong with engineered features, works with small datasets, proven in lab EQ forecasting | Requires hand-crafted features, no end-to-end learning, poor transferability |
| **CNN / RNN**                                           | ⚠️ Maybe      | Learns directly from waveforms, established in seismology, captures temporal patterns                         | Needs labeled data, limited long-range context, slower training              |
| **Transformer (from scratch)**                          | ❌ No          | Captures global dependencies, flexible                                                                        | Extremely data-hungry, high overfitting risk, weak inductive bias            |
| **Pretrained Transformer (EQTransformer, Siamese-EQT)** | ✅ Best choice | Strong representations, works with limited labels, fast convergence, proven seismic performance               | Architecture constraints, limited sensor transfer                            |

---

## 7. Forecasting vs Nowcasting

We explicitly distinguish two categories of prior work:

### Category 1: Nowcasting (Not the focus)

* Phase picking
* Detection
* Magnitude/location estimation
* Earthquake early warning

### Category 2: Forecasting (This MVP)

* Pre-slip detection
* Slow earthquake signals
* Multimodal precursors
* Short-term forecasting

This MVP operates **exclusively in Category 2**.

---

## 8. Relevant Literature & Data Sources

Key themes covered in referenced work:

* Seismic velocity precursors
* GPS-based pre-slip detection and rebuttals
* Slow earthquake signals analyzed with deep learning
* Dense seismic networks identifying rupture-prone fault patches
* Animal behavior as a proxy for environmental or electromagnetic changes
* Critical perspectives on AI-based earthquake prediction

(All references tracked separately; links maintained in project notes.)

---

## 9. Action Items

### Alessandro (Alex)

* Read: *Probing slow earthquakes with deep learning*
* Review animal behavior datasets from Italy
* Analyze ~90 earthquakes in the sequence

### Allie

* Locate and deliver animal activity CSVs
* Finalize and validate pre-slip labels

---

## 10. Next Steps

1. Finalize animal dataset ingestion
2. Define pre-slip time windows and baselines
3. Train embedding models per modality
4. Compare predictive signal across modalities
5. Assess multimodal fusion potential

---

## 11. Success Criteria for the MVP

The MVP is successful if we can:

* Quantify predictive performance of animal data
* Show whether animal data adds signal beyond seismic/GPS
* Establish a reproducible baseline pipeline
* Clearly articulate limitations and failure modes

This project is exploratory by design, prioritizing **scientific clarity over headline claims**.

