"""
Experiment tracking: records the five candidate models (validation results) and the final model (held-out test
results) in MLflow, and ALWAYS also writes a plain CSV log, so tracking works even without MLflow installed.

    python scripts/log_experiments_mlflow.py            # run from the project root
    mlflow ui --backend-store-uri sqlite:///mlflow.db    # then open http://localhost:5000

It does NOT retrain anything. The numbers are read from outputs/results/notebook_results.json and
models/model_metadata.json, which the notebook writes (Section 8.1). Training parameters are the ones set in the
notebook (Sections 6.1-6.2b).

Outputs:  mlflow.db + mlartifacts/ (MLflow store, git-ignored)
          outputs/results/experiment_log.csv   (one row per run: parameters and metrics)
          docs/experiment_table.md             (same table in Markdown)
"""
import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RES = json.loads((ROOT / "outputs/results/notebook_results.json").read_text())
META = json.loads((ROOT / "models/model_metadata.json").read_text())

COMMON = {"dataset": "UCI Diabetes 130-US Hospitals 1999-2008 (dataset 296)", "target": "readmitted_30d",
          "split": "patient-grouped 70/15/15", "random_seed": 42, "imbalance_handling": "class weighting",
          "n_features_in": 46}
PARAMS = {
    "LogisticRegression (baseline)": {"family": "LogisticRegression", "max_iter": 1000, "class_weight": "balanced"},
    "RandomForest": {"family": "RandomForestClassifier", "n_estimators": 200, "max_depth": 10,
                     "class_weight": "balanced_subsample"},
    "HistGradientBoosting (tuned)": {"family": "HistGradientBoostingClassifier", "class_weight": "balanced",
                                     "max_iter": 150, "min_samples_leaf": 50, "learning_rate": 0.1,
                                     "l2_regularization": 1.0, "max_leaf_nodes": 31,
                                     "tuning": "6 random configurations x 3 patient-grouped folds"},
    "XGBoost": {"family": "XGBClassifier", "n_estimators": 300, "learning_rate": 0.05, "max_depth": 4,
                "subsample": 0.8, "colsample_bytree": 0.8, "scale_pos_weight": "n_neg/n_pos", "tuning": "none"},
    "LightGBM": {"family": "LGBMClassifier", "n_estimators": 300, "learning_rate": 0.05, "num_leaves": 31,
                 "subsample": 0.8, "colsample_bytree": 0.8, "class_weight": "balanced", "tuning": "none"},
}
VAL_KEYS = ["roc_auc", "pr_auc", "recall", "precision", "f1", "accuracy", "brier_score"]


def rows():
    out = []
    for name, p in PARAMS.items():
        m = {f"val_{k}": RES["validation_comparison"][k][name] for k in VAL_KEYS}
        out.append({"run": name, "stage": "validation", "selected": name == RES["selected_model"],
                    "params": {**COMMON, **p}, "metrics": m})
    t = RES["test_metrics"]
    cm = t["confusion_matrix"]
    met = {f"test_{k}": t[k] for k in ("roc_auc", "pr_auc", "recall", "precision", "f1", "accuracy", "brier_score")}
    met.update({"test_true_negatives": cm[0][0], "test_false_positives": cm[0][1],
                "test_false_negatives": cm[1][0], "test_true_positives": cm[1][1],
                "decision_threshold": t["threshold_used"],
                "tier_low_below": META["risk_tier_thresholds"]["low_below"],
                "tier_medium_below": META["risk_tier_thresholds"]["medium_below"],
                "criteria_met": sum(str(c["met"]) == "True" for c in RES["success_criteria"]),
                "criteria_total": len(RES["success_criteria"])})
    out.append({"run": f"FINAL {RES['selected_model']} (held-out test)", "stage": "test", "selected": True,
                "params": {**COMMON, **PARAMS[RES["selected_model"]]}, "metrics": met})
    return out


def write_csv_and_md(data):
    mkeys = sorted({k for r in data for k in r["metrics"]})
    with open(ROOT / "outputs/results/experiment_log.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["run", "stage", "selected", "params_json"] + mkeys)
        for r in data:
            w.writerow([r["run"], r["stage"], r["selected"], json.dumps(r["params"])] +
                       [r["metrics"].get(k, "") for k in mkeys])
    lines = ["| Run | Stage | Selected | ROC-AUC | PR-AUC | Recall | Precision | F1 |", "|---|---|---|---|---|---|---|---|"]
    for r in data:
        pre = "val_" if r["stage"] == "validation" else "test_"
        g = lambda k: f"{r['metrics'][pre + k]:.4f}"
        lines.append(f"| {r['run']} | {r['stage']} | {'yes' if r['selected'] else ''} | {g('roc_auc')} | "
                     f"{g('pr_auc')} | {g('recall')} | {g('precision')} | {g('f1')} |")
    (ROOT / "docs/experiment_table.md").write_text("\n".join(lines) + "\n")


def log_to_mlflow(data, uri, log_model):
    import mlflow
    mlflow.set_tracking_uri(uri)
    mlflow.set_experiment("diabetic-readmission-30d")
    for r in data:
        with mlflow.start_run(run_name=r["run"]):
            mlflow.log_params({k: str(v) for k, v in r["params"].items()})
            mlflow.log_metrics(r["metrics"])
            mlflow.set_tags({"stage": r["stage"], "selected": str(r["selected"]),
                             "note": "numbers read from notebook_results.json; not retrained here"})
            if r["stage"] == "test":
                for rel in ("models/model_metadata.json", "outputs/results/notebook_results.json"):
                    mlflow.log_artifact(str(ROOT / rel))
                for fig in sorted((ROOT / "outputs/figures").glob("*.png")):
                    mlflow.log_artifact(str(fig), artifact_path="figures")
                if log_model:
                    mlflow.log_artifact(str(ROOT / "models/final_model.joblib"), artifact_path="model")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--tracking-uri", default=f"sqlite:///{ROOT / 'mlflow.db'}")
    ap.add_argument("--no-model", action="store_true", help="do not copy the model file into MLflow artifacts")
    a = ap.parse_args()
    data = rows()
    write_csv_and_md(data)
    print(f"wrote outputs/results/experiment_log.csv and docs/experiment_table.md ({len(data)} runs)")
    try:
        log_to_mlflow(data, a.tracking_uri, not a.no_model)
        print(f"logged {len(data)} runs to MLflow at {a.tracking_uri}")
        print("view them with:  mlflow ui --backend-store-uri sqlite:///mlflow.db   (http://localhost:5000)")
    except ImportError:
        print("MLflow is not installed; the CSV/Markdown log was still written. "
              "Install it with: pip install -r requirements-mlflow.txt")
