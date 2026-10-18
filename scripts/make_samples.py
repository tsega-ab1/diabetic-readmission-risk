"""Regenerates the de-identified sample cases used by the Streamlit prototype, plus the workflow-test
results:   python scripts/make_samples.py     (run from the project root)

It rebuilds the same patient-grouped 70/15/15 split as the notebook (seed 42) from data/diabetic_data.csv,
scores the test rows with models/final_model.joblib, and saves three real test-set feature rows (no
patient_nbr / encounter_id) picked at the 65th (typical), 95th (higher-risk) and 10th (lower-risk)
percentile of the model score.
"""
import json, sys
from pathlib import Path
import numpy as np
from sklearn.model_selection import GroupShuffleSplit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import predict
from data_preprocessing import load_raw, build_model_frame

SEED = 42
raw = load_raw(str(ROOT / "data" / "diabetic_data.csv"))
X, y, groups = build_model_frame(raw)
tr, tmp = next(GroupShuffleSplit(n_splits=1, train_size=0.70, random_state=SEED).split(X, y, groups=groups))
_, te_rel = next(GroupShuffleSplit(n_splits=1, train_size=0.50, random_state=SEED).split(X.iloc[tmp], y.iloc[tmp], groups=groups.iloc[tmp]))
X_test = X.iloc[tmp[te_rel]]

model, _ = predict._load()
probs = model.predict_proba(X_test)[:, 1]
order = np.argsort(probs)
clean = lambda row: {k: (v.item() if hasattr(v, "item") else v) for k, v in row.items()}
rows = {"typical": X_test.iloc[order[int(.65 * len(order))]].to_dict(),
        "higher_risk": X_test.iloc[order[int(.95 * len(order))]].to_dict(),
        "lower_risk": X_test.iloc[order[int(.10 * len(order))]].to_dict()}
out_dir = ROOT / "outputs" / "results"
out_dir.mkdir(parents=True, exist_ok=True)
res = {}
for name, row in rows.items():
    row = clean(row)
    out = predict.predict_one(row)
    res[name] = out
    json.dump({"input": row, "output": out}, open(out_dir / f"sample_{name}.json", "w"), indent=2, default=str)
edge = dict(rows["typical"], time_in_hospital=14, num_medications=81, number_inpatient=15, number_emergency=20, num_lab_procedures=132)
res["edge_extreme_values"] = predict.predict_one(clean(edge))
res["missing_invalid"] = predict.predict_one({"age": "[70-80)", "time_in_hospital": "oops"})
json.dump(res, open(out_dir / "workflow_tests.json", "w"), indent=2, default=str)
for k, v in res.items():
    print(f"{k:22s} score={v['probability_30d_readmission']}  tier={v['risk_tier']}")
