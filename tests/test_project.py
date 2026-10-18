"""
Task 8 — automated tests for the saved final model and the shared prediction code.

Run from the project root:   pytest tests/
(or, without pytest:         python scripts/run_tests_without_pytest.py)

The tests cover preprocessing, ICD-9 grouping, leakage exclusions, risk-tier boundaries, model loading,
prediction output format, and handling of missing/invalid input. They use models/final_model.joblib.
"""
import sys
import json
from pathlib import Path

import pandas as pd

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

import data_preprocessing as dp
import predict


# ---------------------------------------------------------------------
# Preprocessing
# ---------------------------------------------------------------------

def test_icd9_grouping_diabetes():
    assert dp.icd9_to_category("250.01") == "Diabetes"
    assert dp.icd9_to_category("250") == "Diabetes"


def test_icd9_grouping_circulatory():
    assert dp.icd9_to_category("410") == "Circulatory"
    assert dp.icd9_to_category("785") == "Circulatory"


def test_icd9_grouping_v_e_codes():
    assert dp.icd9_to_category("V27") == "Other"
    assert dp.icd9_to_category("E849") == "Other"


def test_icd9_grouping_missing():
    assert dp.icd9_to_category("?") == "Missing"
    assert dp.icd9_to_category(None) == "Missing"


def test_icd9_grouping_decimal_subcodes():
    # Regression test: decimal sub-codes must be grouped by their 3-digit category.
    # (An earlier version compared the float to whole-number bounds and sent
    # 786.05, 785.51, 787.01, 788.1, 459.81 ... to "Other".)
    assert dp.icd9_to_category("786.05") == "Respiratory"
    assert dp.icd9_to_category("785.51") == "Circulatory"
    assert dp.icd9_to_category("787.01") == "Digestive"
    assert dp.icd9_to_category("788.1") == "Genitourinary"
    assert dp.icd9_to_category("459.81") == "Circulatory"
    assert dp.icd9_to_category("519.1") == "Respiratory"
    assert dp.icd9_to_category("239.9") == "Neoplasms"
    assert dp.icd9_to_category("739.3") == "Musculoskeletal"
    assert dp.icd9_to_category("999.9") == "Injury"
    assert dp.icd9_to_category("250.83") == "Diabetes"
    assert dp.icd9_to_category("249.00") == "Other"   # 249 is not 250


def test_target_recoding():
    raw = pd.DataFrame({
        "readmitted": ["<30", ">30", "NO", "<30"],
        "discharge_disposition_id": [1, 1, 1, 1],
        "gender": ["Female", "Male", "Female", "Male"],
        "encounter_id": [1, 2, 3, 4],
        "patient_nbr": [10, 20, 30, 40],
    })
    out = dp.apply_target_and_exclusions(raw)
    assert out[dp.TARGET_COL].tolist() == [1, 0, 0, 1]


def test_expired_hospice_excluded():
    raw = pd.DataFrame({
        "readmitted": ["NO", "NO", "NO"],
        "discharge_disposition_id": [1, 11, 13],  # 11=Expired, 13=Hospice/home
        "gender": ["Female", "Female", "Female"],
        "encounter_id": [1, 2, 3],
        "patient_nbr": [10, 20, 30],
    })
    out = dp.apply_target_and_exclusions(raw)
    assert len(out) == 1
    assert out["discharge_disposition_id"].tolist() == [1]


def test_unknown_invalid_gender_excluded():
    raw = pd.DataFrame({
        "readmitted": ["NO", "NO"],
        "discharge_disposition_id": [1, 1],
        "gender": ["Female", "Unknown/Invalid"],
        "encounter_id": [1, 2],
        "patient_nbr": [10, 20],
    })
    out = dp.apply_target_and_exclusions(raw)
    assert len(out) == 1


def test_question_mark_recoded_to_unknown():
    df = pd.DataFrame({"payer_code": ["?", "MC"], "medical_specialty": ["?", "Cardiology"],
                        "race": ["?", "Caucasian"], "max_glu_serum": [None, ">200"],
                        "A1Cresult": [None, "Norm"]})
    out = dp.clean_missing_markers(df)
    assert out["payer_code"].tolist() == ["Unknown", "MC"]
    assert out["race"].tolist() == ["Unknown", "Caucasian"]
    assert out["max_glu_serum"].tolist() == ["Not tested", ">200"]


# ---------------------------------------------------------------------
# Risk tier logic
# ---------------------------------------------------------------------

def test_risk_tier_boundaries():
    assert dp.risk_tier(0.0) == "Low"
    assert dp.risk_tier(0.44) == "Low"
    assert dp.risk_tier(0.45) == "Medium"
    assert dp.risk_tier(0.59) == "Medium"
    assert dp.risk_tier(0.60) == "High"
    assert dp.risk_tier(0.99) == "High"


# ---------------------------------------------------------------------
# Model loading / prediction (require models/final_model.joblib to exist;
# skip gracefully if the model has not been trained yet in this checkout)
# ---------------------------------------------------------------------

MODEL_EXISTS = predict.MODEL_PATH.exists()


def test_model_file_exists():
    assert MODEL_EXISTS, "models/final_model.joblib not found -- run the notebook (Section 8.1) to create it"


def test_model_loads():
    if not MODEL_EXISTS:
        return
    model, metadata = predict._load()
    assert model is not None
    assert "decision_threshold" in metadata
    assert "feature_list" in metadata


def test_prediction_output_format():
    if not MODEL_EXISTS:
        return
    sample = json.load(open(Path(__file__).resolve().parent.parent / "outputs/results/sample_typical.json"))
    result = predict.predict_one(sample["input"])
    assert "probability_30d_readmission" in result
    assert 0.0 <= result["probability_30d_readmission"] <= 1.0
    assert result["risk_tier"] in {"Low", "Medium", "High"}
    assert isinstance(result["predicted_high_risk_flag"], bool)
    assert "disclaimer" in result and len(result["disclaimer"]) > 0


def test_prediction_handles_missing_input():
    if not MODEL_EXISTS:
        return
    result = predict.predict_one({})
    assert result["input_warnings"] is not None
    assert len(result["input_warnings"]) > 0
    assert 0.0 <= result["probability_30d_readmission"] <= 1.0  # still returns a usable output


def test_prediction_handles_invalid_numeric_input():
    if not MODEL_EXISTS:
        return
    sample = json.load(open(Path(__file__).resolve().parent.parent / "outputs/results/sample_typical.json"))
    bad_input = dict(sample["input"])
    bad_input["num_medications"] = "not_a_number"
    result = predict.predict_one(bad_input)
    assert any("num_medications" in w for w in result["input_warnings"])
    assert 0.0 <= result["probability_30d_readmission"] <= 1.0  # does not crash


def test_prediction_identifiers_not_used():
    # patient_nbr / encounter_id must not appear among the model's input features
    if not MODEL_EXISTS:
        return
    _, metadata = predict._load()
    assert "patient_nbr" not in metadata["feature_list"]
    assert "encounter_id" not in metadata["feature_list"]
