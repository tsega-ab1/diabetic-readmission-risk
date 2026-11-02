# Simulated Data Statement (Deliverable D)

**Project:** Predicting 30-day hospital readmission risk in diabetic patients, FUSE AI-201, Group 2

## Statement

**This project does not use simulated or synthetic data to train, tune, test or evaluate the model.** All
modelling and all reported results use one real, public dataset. A small number of hand-made input values were
created only to test error handling; they are listed below and are not used as evidence of model performance.

## Data source

| Item | Detail |
|---|---|
| Dataset | *Diabetes 130-US Hospitals for Years 1999–2008* |
| Provider | UCI Machine Learning Repository, dataset 296 |
| Link | https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008 |
| Citation | Clore, J., Cios, K., DeShazo, J., & Strack, B. (2014). *Diabetes 130-US hospitals for years 1999–2008* [Data set]. UCI Machine Learning Repository. https://doi.org/10.24432/C5230J |
| Size | 101,766 hospital stays (71,518 patients), 50 columns; 99,340 stays used after exclusions |
| Licence | CC BY 4.0 (stated on the UCI page) |
| Privacy | De-identified research data. It contains no names and no contact details. We did not try to re-identify anyone and used no other data about these patients. The model never uses `patient_nbr` or `encounter_id` as inputs |
| Limits | US hospitals, 1999–2008; results from this data say nothing certain about today's hospitals or other countries |

## Where made-up or non-real values appear in the project

| Where | What it is | Is it simulated data? |
|---|---|---|
| Edge-case tests (notebook Section 8.2, `tests/`, `docs/evidence/api_session.txt`) | Hand-made inputs such as a 60-day stay, 300 medications, 90 prior inpatient visits, race "Martian", insulin "Sideways", or text in a number field | **Yes, hand-made test inputs.** They are not patients. They exist only to check that invalid or unusual input produces warnings and no crash. Their scores are not performance results |
| Sample cases in the Streamlit app and API sample request | Three real, de-identified rows from our held-out **test set** (typical, higher-risk, lower-risk) | **No.** They are real records from the dataset, without identifiers |
| Default values in the app form | Illustrative starting values so the form is filled in | **Not patient data.** They are not a real person and not used for any result |
| Threshold and example values in the monitoring plan | Proposed alert levels based on our test results | **No simulated data.** No production data exists, so none is simulated |

## What we do *not* claim

- We do not claim any real-world or production performance. All results come from a held-out part of the
  1999–2008 dataset.
- We do not present the edge-case test outputs as evidence of accuracy.
- The prototype has not been validated on real patients and is not a medical tool.

## Why no simulated data was needed

A real, public, de-identified dataset large enough to train and evaluate the model was available, so no data
had to be invented. No live hospital data was available or appropriate for a student project.
