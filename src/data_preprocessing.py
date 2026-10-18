"""
Task 3 — Data preparation utilities for the diabetic readmission project.

This module is imported by both the training notebook/script and the
Streamlit prototype, so that *exactly* the same preprocessing logic is
used at train time and at inference time (Module 5 requirement).

Design decisions are documented inline; see the project report (Section 6)
for the full written rationale.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# --------------------------------------------------------------------------
# 1. Discharge-disposition codes that indicate the patient died or was
#    discharged to hospice. These encounters are excluded BEFORE modeling
#    because such patients cannot, by definition, be readmitted -- keeping
#    them would be a data-leakage / label-validity problem (Module 4,
#    Section 8.3; confirmed against data/IDS_mapping.csv).
# --------------------------------------------------------------------------
EXPIRED_HOSPICE_DISCHARGE_CODES = {11, 13, 14, 19, 20, 21}

# Columns that are database identifiers, not predictive features.
ID_COLUMNS = ["encounter_id", "patient_nbr"]

# Raw target column and its recoding (Module 4 / assignment spec).
TARGET_RAW_COL = "readmitted"
TARGET_COL = "readmitted_30d"

# ID-coded columns that are categorical groupings, not continuous measurements.
ID_CODED_CATEGORICAL = ["admission_type_id", "discharge_disposition_id", "admission_source_id"]

NUMERIC_FEATURES = [
    "time_in_hospital", "num_lab_procedures", "num_procedures", "num_medications",
    "number_outpatient", "number_emergency", "number_inpatient", "number_diagnoses",
]

# Medication columns: all share the same {No, Steady, Up, Down} vocabulary.
MEDICATION_COLUMNS = [
    "metformin", "repaglinide", "nateglinide", "chlorpropamide", "glimepiride",
    "acetohexamide", "glipizide", "glyburide", "tolbutamide", "pioglitazone",
    "rosiglitazone", "acarbose", "miglitol", "troglitazone", "tolazamide",
    "examide", "citoglipton", "insulin", "glyburide-metformin", "glipizide-metformin",
    "glimepiride-pioglitazone", "metformin-rosiglitazone", "metformin-pioglitazone",
]

OTHER_CATEGORICAL = [
    "race", "gender", "age", "payer_code", "medical_specialty",
    "max_glu_serum", "A1Cresult", "change", "diabetesMed",
    "diag_1_group", "diag_2_group", "diag_3_group",
] + ID_CODED_CATEGORICAL + MEDICATION_COLUMNS


def icd9_to_category(code) -> str:
    """Group a raw ICD-9 diagnosis code string into one of the nine clinically
    meaningful categories used by Strack et al. (2014) in the original study
    that produced this dataset, and widely replicated since. This is a
    transparent, rule-based mapping on the numeric ICD-9 code range -- it
    does not invent new medical meaning, only reproduces a published scheme.

    Categories: Circulatory, Respiratory, Digestive, Diabetes, Injury,
    Musculoskeletal, Genitourinary, Neoplasms, Other.
    """
    if pd.isna(code) or code == "?":
        return "Missing"
    code = str(code)
    if code.startswith("V") or code.startswith("E"):
        return "Other"  # supplementary classification / external causes
    try:
        # Group on the 3-digit category (integer part): 786.05 is in category 786,
        # 459.81 is in category 459. Comparing the raw float to whole-number
        # bounds would wrongly push every decimal sub-code of 459/519/579/...
        # and 785-788 into "Other".
        num = int(float(code))
    except ValueError:
        return "Other"
    if 390 <= num <= 459 or num == 785:
        return "Circulatory"
    if 460 <= num <= 519 or num == 786:
        return "Respiratory"
    if 520 <= num <= 579 or num == 787:
        return "Digestive"
    if num == 250:
        return "Diabetes"
    if 800 <= num <= 999:
        return "Injury"
    if 710 <= num <= 739:
        return "Musculoskeletal"
    if 580 <= num <= 629 or num == 788:
        return "Genitourinary"
    if 140 <= num <= 239:
        return "Neoplasms"
    return "Other"


def load_raw(path: str) -> pd.DataFrame:
    return pd.read_csv(path)


def apply_target_and_exclusions(df: pd.DataFrame) -> pd.DataFrame:
    """Create the binary target and apply the documented row-level exclusions.

    Exclusions (each counted and logged by the caller for the report):
      1. Expired / hospice discharge dispositions (leakage / label validity).
      2. The 3 rows with gender == 'Unknown/Invalid' (too few to model;
         documented rather than silently dropped).
    """
    df = df.copy()

    df = df[~df["discharge_disposition_id"].isin(EXPIRED_HOSPICE_DISCHARGE_CODES)]
    df = df[df["gender"] != "Unknown/Invalid"]

    df[TARGET_COL] = (df[TARGET_RAW_COL] == "<30").astype(int)
    return df


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered columns (diagnosis groups). Does not drop anything."""
    df = df.copy()
    df["diag_1_group"] = df["diag_1"].apply(icd9_to_category)
    df["diag_2_group"] = df["diag_2"].apply(icd9_to_category)
    df["diag_3_group"] = df["diag_3"].apply(icd9_to_category)
    return df


def clean_missing_markers(df: pd.DataFrame) -> pd.DataFrame:
    """Convert '?' placeholders to an explicit 'Unknown' category for the
    categorical fields where the proposal calls for retaining missingness
    as information (payer_code, medical_specialty, race), and leaves weight
    to be dropped entirely upstream (handled in build_model_frame)."""
    df = df.copy()
    for col in ["payer_code", "medical_specialty", "race"]:
        df[col] = df[col].replace("?", "Unknown")
    for col in ["max_glu_serum", "A1Cresult"]:
        df[col] = df[col].fillna("Not tested")
    return df


def build_model_frame(raw_df: pd.DataFrame):
    """Full Task-3 pipeline from raw CSV rows to a modeling-ready frame.

    Returns (X, y, groups) where groups = patient_nbr, for grouped splitting.
    `weight` is dropped (96.9% missing in this exact file -- confirmed by
    src/inspect_data.py, consistent with the Module 4 proposal).
    Identifier columns are dropped from X but patient_nbr is returned
    separately as the grouping key, never as a predictor.
    """
    df = apply_target_and_exclusions(raw_df)
    df = engineer_features(df)
    df = clean_missing_markers(df)

    groups = df["patient_nbr"].copy()
    y = df[TARGET_COL].copy()

    drop_cols = ID_COLUMNS + [TARGET_RAW_COL, TARGET_COL, "weight", "diag_1", "diag_2", "diag_3"]
    X = df.drop(columns=drop_cols)

    # Make ID-coded categorical columns explicit strings so encoders never
    # treat them as ordered/continuous numeric quantities.
    for col in ID_CODED_CATEGORICAL:
        X[col] = X[col].astype(str)

    return X, y, groups


def build_preprocessor() -> ColumnTransformer:
    """ColumnTransformer shared by every candidate model. Fit ONLY on the
    training split (never on validation/test) so that no information from
    held-out patients leaks into preprocessing statistics."""
    numeric_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("num", numeric_pipe, NUMERIC_FEATURES),
        ("cat", categorical_pipe, OTHER_CATEGORICAL),
    ])


def risk_tier(prob: float, low_cut: float = 0.45, high_cut: float = 0.60) -> str:
    """Project-level (not clinically validated) operational rule for turning
    a predicted probability into a 3-level risk tier for the prototype UI.

    IMPORTANT: because the final model is trained with class_weight="balanced"
    to counter the ~89/11 class imbalance (report Sections 6 and 9),
    its predicted probabilities are deliberately shifted upward relative to
    the true ~11% base rate and should not be read as literal real-world
    probabilities (see the project report, Section 11 (Calibration)). For that
    reason these cut points were NOT chosen as round absolute values; they
    are the approximate 50th and 85th percentiles of the predicted-score
    distribution on the held-out validation set (computed in
    notebook Task 7 / Section 8.1), so that the three tiers
    correspond to roughly "below-median risk", "above-median risk", and
    "top ~15% risk" within this model's own score distribution. Cut points
    are recorded in models/model_metadata.json. They are demonstration
    thresholds only, not clinically validated.
    """
    if prob < low_cut:
        return "Low"
    if prob < high_cut:
        return "Medium"
    return "High"
