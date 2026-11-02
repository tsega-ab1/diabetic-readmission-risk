"""Tests for the FastAPI wrapper (api.py). Needs: pip install -r requirements-api.txt ; run: pytest tests/test_api.py"""
import json
import sys
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")
from fastapi.testclient import TestClient  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import api  # noqa: E402

client = TestClient(api.app)
SAMPLE = json.loads((ROOT / "outputs" / "results" / "sample_typical.json").read_text())["input"]


def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok" and r.json()["model_loaded"] is True


def test_model_info_has_thresholds_and_metrics():
    j = client.get("/model-info").json()
    assert j["model_name"] == "LightGBM" and j["decision_threshold"] == 0.51
    assert 0.68 < j["test_metrics"]["roc_auc"] < 0.69


def test_predict_matches_streamlit_path():
    r = client.post("/predict", json={"record": SAMPLE})
    assert r.status_code == 200
    j = r.json()
    assert j["risk_score"] == 0.4857 and j["risk_tier"] == "Medium" and j["input_warnings"] == []
    assert "not a literal probability" in j["disclaimer"]


def test_missing_and_invalid_values_do_not_crash():
    rec = dict(SAMPLE); rec.pop("number_inpatient"); rec["num_medications"] = "not_a_number"
    r = client.post("/predict", json={"record": rec})
    assert r.status_code == 200 and r.json()["input_warnings"]


def test_unexpected_category_and_extreme_values_warn():
    rec = dict(SAMPLE, race="Martian", time_in_hospital=60, number_inpatient=90)
    j = client.post("/predict", json={"record": rec}).json()
    assert any("Unexpected category" in w for w in j["input_warnings"])
    assert any("outside the range" in w for w in j["input_warnings"])


def test_identifiers_are_ignored_not_used():
    base = client.post("/predict", json={"record": SAMPLE}).json()
    with_ids = client.post("/predict", json={"record": dict(SAMPLE, patient_nbr=123, encounter_id=456)}).json()
    assert with_ids["risk_score"] == base["risk_score"]
    assert set(with_ids["ignored_fields"]) == {"patient_nbr", "encounter_id"}


def test_malformed_request_is_rejected_cleanly():
    assert client.post("/predict", json={"record": "not a dict"}).status_code == 422
    assert client.post("/predict", json={}).status_code == 422
