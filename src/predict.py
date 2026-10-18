"""
Task 8 support — single shared inference path (same logic as predict_one() in the notebook).

Both tests/test_project.py and app.py import predict_one() so that the
prototype and the automated tests exercise exactly the same code, which is
exactly the same preprocessing/model object used for the Module 5 test-set
evaluation (models/final_model.joblib).
"""
import json
from pathlib import Path

import joblib
import pandas as pd

from data_preprocessing import risk_tier, OTHER_CATEGORICAL, NUMERIC_FEATURES, ID_CODED_CATEGORICAL

MODEL_PATH = Path(__file__).parent.parent / "models" / "final_model.joblib"
METADATA_PATH = Path(__file__).parent.parent / "models" / "model_metadata.json"

_model = None
_metadata = None


def _load():
    global _model, _metadata
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    if _metadata is None:
        with open(METADATA_PATH) as f:
            _metadata = json.load(f)
    return _model, _metadata


REQUIRED_FEATURES = NUMERIC_FEATURES + OTHER_CATEGORICAL


def validate_record(record: dict):
    """Returns (is_valid, list_of_problems). Does not raise."""
    problems = []
    for col in REQUIRED_FEATURES:
        if col not in record:
            problems.append(f"Missing required field: {col}")
    for col in NUMERIC_FEATURES:
        if col in record and record[col] is not None:
            try:
                float(record[col])
            except (TypeError, ValueError):
                problems.append(f"Field '{col}' must be numeric, got {record[col]!r}")
    return (len(problems) == 0), problems


def predict_one(record: dict) -> dict:
    """Takes a dict of raw feature values (same schema as the model's
    feature_list, identifiers excluded) and returns probability + risk tier.
    Missing/invalid fields are handled safely: missing categorical fields
    are imputed by the pipeline's most-frequent-value imputer, missing
    numeric fields by the median imputer -- both fit only on the training
    split, so no test/production data leaks into those statistics.
    """
    model, metadata = _load()
    is_valid, problems = validate_record(record)

    row = {}
    for col in REQUIRED_FEATURES:
        row[col] = record.get(col, None)
    df = pd.DataFrame([row])

    # Coerce numeric columns; invalid numeric strings become NaN and are
    # handled by the pipeline's median imputer rather than crashing.
    for col in NUMERIC_FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Warn (but do not fail) about values outside what the model saw in training, and about categories
    # it has never seen; unseen categories are handled by the encoder as "unknown".
    ranges = metadata.get("numeric_ranges", {})
    cats = metadata.get("categories", {})
    for col in NUMERIC_FEATURES:
        v = df[col].iloc[0]
        if pd.notna(v) and col in ranges:
            lo, hi = ranges[col]
            if not (lo <= v <= hi):
                problems.append(f"Value {v:g} for '{col}' is outside the range seen in training "
                                f"({lo:g}-{hi:g}); the prediction may be unreliable")
    for col in OTHER_CATEGORICAL:
        v = record.get(col)
        if v is not None and col in cats and str(v) not in cats[col]:
            problems.append(f"Unexpected category {str(v)!r} for '{col}' (not seen in training); "
                            f"it is treated as unknown")
        if col in ID_CODED_CATEGORICAL and v is not None:
            df[col] = str(v)

    prob = float(model.predict_proba(df)[:, 1][0])
    threshold = metadata["decision_threshold"]
    tiers = metadata["risk_tier_thresholds"]
    tier = risk_tier(prob, low_cut=tiers["low_below"], high_cut=tiers["medium_below"])
    predicted_label = int(prob >= threshold)

    return {
        "probability_30d_readmission": round(prob, 4),
        "risk_tier": tier,
        "predicted_high_risk_flag": bool(predicted_label),
        "decision_threshold_used": threshold,
        "input_warnings": problems if problems else None,
        "disclaimer": ("This prototype is for academic and research demonstration purposes "
                        "only. It is not a medical diagnosis, does not replace professional "
                        "clinical judgment, and has not been clinically validated for "
                        "real-world patient care."),
    }
