"""
FastAPI service around the saved final model (demonstration only).

Run from the project root:
    python -m pip install -r requirements-api.txt
    python -m uvicorn api:app --port 8000
Then open http://localhost:8000/docs for the interactive page (Swagger UI), or call it from a terminal:
    curl -s localhost:8000/health
    curl -s -X POST localhost:8000/predict -H "Content-Type: application/json" \
         -d @outputs/results/sample_typical_request.json

It uses exactly the same prediction code as the Streamlit app and the tests (src/predict.py), so a record
returns the same score here as in the app. Patient values are never written to the log: each request logs only
the time, the score, the tier, the number of warnings and the latency.
"""
from __future__ import annotations

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
import predict  # noqa: E402
from data_preprocessing import MEDICATION_COLUMNS  # noqa: E402,F401

log = logging.getLogger("readmission_api")
if not log.handlers:
    logging.basicConfig(level=logging.INFO, format="%(message)s")

DISCLAIMER = (
    "Academic demonstration only. Not a medical diagnosis, not a substitute for clinical judgment, "
    "and not clinically validated. The score ranks patients; it is not a literal probability."
)

app = FastAPI(
    title="Diabetic 30-day readmission risk (demonstration API)",
    version="1.0.0",
    description=DISCLAIMER,
)


class PredictRequest(BaseModel):
    record: Dict[str, Any] = Field(
        ...,
        description="One hospital stay as {feature name: value}. See DATA_DICTIONARY.md and "
                    "models/model_metadata.json (feature_list). Missing fields are imputed; identifiers "
                    "(patient_nbr, encounter_id) are ignored.",
    )


class PredictResponse(BaseModel):
    risk_score: float = Field(..., description="Relative model score 0-1 (class-weighted; NOT a calibrated probability)")
    risk_tier: str = Field(..., description="Low / Medium / High, from validation-score percentiles")
    high_risk_flag: bool = Field(..., description="True when risk_score >= decision_threshold")
    decision_threshold: float
    input_warnings: List[str] = Field(default_factory=list)
    ignored_fields: List[str] = Field(default_factory=list, description="Keys in the request that the model does not use")
    disclaimer: str = DISCLAIMER


@app.get("/health")
def health() -> Dict[str, Any]:
    """Liveness check: confirms the model file loads."""
    model, meta = predict._load()
    return {"status": "ok", "model_loaded": model is not None, "model_name": meta.get("model_name")}


@app.get("/model-info")
def model_info() -> Dict[str, Any]:
    """Which model is being served, its thresholds and its held-out test metrics (for monitoring baselines)."""
    _, meta = predict._load()
    return {
        "model_name": meta.get("model_name"),
        "decision_threshold": meta.get("decision_threshold"),
        "risk_tier_thresholds": meta.get("risk_tier_thresholds"),
        "n_features": len(meta.get("feature_list", [])),
        "test_metrics": meta.get("evaluation_metrics_test_set"),
        "sklearn_version_at_training": meta.get("sklearn_version"),
        "disclaimer": DISCLAIMER,
    }


@app.post("/predict", response_model=PredictResponse)
def predict_endpoint(req: PredictRequest) -> PredictResponse:
    """Score one record. Bad or missing values never crash the call: they come back as input_warnings."""
    t0 = time.perf_counter()
    _, meta = predict._load()
    known = set(meta.get("feature_list", []))
    ignored = sorted(k for k in req.record if k not in known)
    out = predict.predict_one(req.record)
    latency_ms = round((time.perf_counter() - t0) * 1000, 1)
    warnings = list(out["input_warnings"] or [])
    # privacy-safe monitoring line: no patient values
    log.info(json.dumps({"event": "predict", "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
                         "score": out["probability_30d_readmission"], "tier": out["risk_tier"],
                         "n_warnings": len(warnings), "n_ignored": len(ignored), "latency_ms": latency_ms}))
    return PredictResponse(
        risk_score=out["probability_30d_readmission"],
        risk_tier=out["risk_tier"],
        high_risk_flag=out["predicted_high_risk_flag"],
        decision_threshold=out["decision_threshold_used"],
        input_warnings=warnings,
        ignored_fields=ignored,
    )
