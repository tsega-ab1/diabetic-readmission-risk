# Data Dictionary

Source: `data/diabetic_data.csv` (UCI "Diabetes 130-US Hospitals for Years
1999-2008") + `data/IDS_mapping.csv` (code lookups for the three `*_id`
columns). Raw file: 101,766 rows x 50 columns. After the Task-3 exclusions
(expired/hospice discharges, 3 unknown-gender rows): 99,340 rows used for
modeling.

## Target

| Feature | Data Type | Description | Example | Used in Model? |
|---|---|---|---|---|
| `readmitted` | categorical (raw) | Original 3-class outcome: `<30`, `>30`, `NO` | `<30` | No -- replaced by `readmitted_30d` |
| `readmitted_30d` | binary (engineered) | **Target.** 1 if `readmitted == "<30"`, else 0 | 1 | **Target**, not a predictor |

## Identifiers (excluded from predictors)

| Feature | Data Type | Description | Example | Used in Model? |
|---|---|---|---|---|
| `encounter_id` | integer | Unique ID for this hospital encounter | 2278392 | No -- identifier |
| `patient_nbr` | integer | Unique ID for the patient (repeats across encounters) | 8222157 | No as a predictor -- used **only** as the grouping key for patient-level train/val/test splitting |

## Numeric features (median-imputed, standardized for Logistic Regression; used as-is for tree models)

| Feature | Data Type | Description | Example | Used in Model? |
|---|---|---|---|---|
| `time_in_hospital` | integer (1-14) | Length of stay in days | 4 | Yes |
| `num_lab_procedures` | integer | Number of lab tests performed during the encounter | 43 | Yes |
| `num_procedures` | integer (0-6) | Number of non-lab procedures performed | 1 | Yes |
| `num_medications` | integer | Number of distinct medications administered | 16 | Yes |
| `number_outpatient` | integer | Outpatient visits in the year before this encounter | 0 | Yes |
| `number_emergency` | integer | Emergency visits in the year before this encounter | 0 | Yes |
| `number_inpatient` | integer | Inpatient visits in the year before this encounter (**top predictor** -- see the project report, Section 11) | 0 | Yes |
| `number_diagnoses` | integer | Number of diagnoses entered into the system | 7 | Yes |

## Categorical features (most-frequent-imputed, one-hot encoded)

| Feature | Data Type | Description | Example | Used in Model? |
|---|---|---|---|---|
| `race` | categorical | Patient race; `?` recoded to `"Unknown"` (2.23% of rows) | Caucasian | Yes |
| `gender` | categorical | Female / Male. 3 `Unknown/Invalid` rows dropped (Task 3) | Female | Yes |
| `age` | categorical (banded) | 10-year age bands, e.g. `[70-80)` | `[70-80)` | Yes |
| `weight` | categorical | Weight band; **96.86% `?`-missing** | `?` | **No -- dropped** |
| `payer_code` | categorical | Insurance/payer code; `?` recoded to `"Unknown"` (39.56% of rows) | MC | Yes |
| `medical_specialty` | categorical (73 raw levels) | Admitting physician's specialty; `?` recoded to `"Unknown"` (49.08% of rows) | Cardiology | Yes |
| `admission_type_id` | categorical (ID-coded) | See `data/IDS_mapping.csv`; e.g. 1=Emergency, 3=Elective | 1 | Yes -- treated as category, not a number |
| `discharge_disposition_id` | categorical (ID-coded) | See `data/IDS_mapping.csv`; e.g. 1=Discharged to home | 1 | Yes -- treated as category, not a number |
| `admission_source_id` | categorical (ID-coded) | See `data/IDS_mapping.csv`; e.g. 7=Emergency Room | 7 | Yes -- treated as category, not a number |
| `max_glu_serum` | categorical | Glucose serum test result; missing (no test ordered) recoded to `"Not tested"` (94.75% of rows) | Not tested | Yes |
| `A1Cresult` | categorical | A1C test result; missing recoded to `"Not tested"` (83.28% of rows) | Not tested | Yes |
| `change` | binary categorical | Whether diabetes medication was changed this encounter | No | Yes |
| `diabetesMed` | binary categorical | Whether the patient is on any diabetes medication | Yes | Yes |
| `metformin` ... `metformin-pioglitazone` (23 columns) | categorical (`No`/`Steady`/`Up`/`Down`) | Dosage-change status for 23 individual diabetes medications (see full list in `src/data_preprocessing.py::MEDICATION_COLUMNS`) | Steady | Yes (all 23) |

## Diagnosis fields (raw -> engineered)

| Feature | Data Type | Description | Example | Used in Model? |
|---|---|---|---|---|
| `diag_1` | categorical (717 raw ICD-9 codes) | Primary diagnosis, raw ICD-9 code | 250.83 | No -- replaced by `diag_1_group` |
| `diag_2` | categorical (749 raw ICD-9 codes) | Secondary diagnosis, raw ICD-9 code | 401.9 | No -- replaced by `diag_2_group` |
| `diag_3` | categorical (790 raw ICD-9 codes) | Tertiary diagnosis, raw ICD-9 code | 428 | No -- replaced by `diag_3_group` |
| `diag_1_group` | categorical (engineered, 9 groups + Missing) | `diag_1` grouped into Circulatory / Respiratory / Digestive / Diabetes / Injury / Musculoskeletal / Genitourinary / Neoplasms / Other / Missing, per the rule-based ICD-9 mapping in `src/data_preprocessing.py::icd9_to_category` (Strack et al. 2014 scheme) | Diabetes | Yes |
| `diag_2_group` | categorical (engineered, 9 groups + Missing) | Same mapping applied to `diag_2` | Circulatory | Yes |
| `diag_3_group` | categorical (engineered, 9 groups + Missing) | Same mapping applied to `diag_3` | Other | Yes |

## Missing-value strategy summary

| Field(s) | Raw missingness | Strategy | Rationale |
|---|---|---|---|
| `weight` | 96.86% `?` | Drop column entirely | Too sparse to impute meaningfully; consistent with Module 4 proposal |
| `payer_code` | 39.56% `?` | Recode `?` -> `"Unknown"` category | Too much data to discard; missingness itself may carry signal (e.g. self-pay vs. insured) |
| `medical_specialty` | 49.08% `?` | Recode `?` -> `"Unknown"` category | Same reasoning as `payer_code` |
| `race` | 2.23% `?` | Recode `?` -> `"Unknown"` category | Small enough to keep as its own level rather than impute a guess |
| `diag_1`/`diag_2`/`diag_3` | 0.02% / 0.35% / 1.40% `?` | Mapped to `"Missing"` diagnosis group | Negligible; kept as an explicit category rather than dropped |
| `max_glu_serum` | 94.75% true NaN | Fill with `"Not tested"` | Absence reflects a clinical testing decision, not a data error -- informative in itself (see EDA Task 4) |
| `A1Cresult` | 83.28% true NaN | Fill with `"Not tested"` | Same reasoning; motivated the original Strack et al. (2014) study this dataset comes from |
| All remaining numeric features | 0% missing in this file | Median-impute inside the pipeline (safety net only) | No missing values were actually present, but the pipeline imputes defensively for future/unseen data |

All percentages above are **measured directly from `data/diabetic_data.csv`**
by `src/inspect_data.py` (see `outputs/results/data_inspection.json`), not
assumed from the Module 4 proposal.
