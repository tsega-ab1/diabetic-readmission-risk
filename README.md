# Predicting Hospital Readmission Risk in Diabetic Patients

**FUSE AI-201 — Module 5: AI Model Development and Implementation — Group 2**
(Group Leader: Surafel Asmamaw)

A research/educational **decision-support prototype** that ranks diabetic inpatients by risk of being
readmitted within 30 days of discharge. It is built on the UCI *Diabetes 130-US Hospitals for Years
1999–2008* dataset and continues the approved Module 4 proposal.

> **Disclaimer.** This prototype is for academic and research demonstration purposes only. It is not a
> medical diagnosis, does not replace professional clinical judgment, and has not been clinically
> validated for real-world patient care. The data are U.S. hospital records from 1999–2008; the model
> must not be assumed to generalize to modern hospitals or to other countries or health systems.

## Module 6 portfolio: where to find everything

**Live demo (Streamlit Community Cloud):** https://diabetic-readmission-risk-cx.streamlit.app/
**Source code (GitHub):** <https://github.com/tsega-ab1/diabetic-readmission-risk>
**Presentation video:** submitted as a separate file in Canvas (script: `docs/VIDEO_SCRIPT.md`).

| Module 6 requirement | Where |
|---|---|
| Working prototype and demonstration | `app.py` (Streamlit), `api.py` (FastAPI), `docs/APP_GUIDE.md` (plain-language guide and demo steps) |
| Testing, deployment, experiment tracking | `docs/DEPLOYMENT_AND_TESTING.md`, `docs/EXPERIMENT_TRACKING.md`, `docs/evidence/`, `tests/`, `scripts/log_experiments_mlflow.py` |
| Monitoring, support and maintenance plan | `docs/MONITORING_SUPPORT_MAINTENANCE_PLAN.md` |
| Setup and run instructions | this README, `docs/SETUP_FOR_TEAMMATES.md` |
| Screenshots | `docs/screenshots/` |
| Simulated data statement (Deliverable D) | `docs/SIMULATED_DATA_STATEMENT.md` (**no simulated data** is used for training, testing or evaluation) |
| One-page retrospective (Deliverable C) | `docs/RETROSPECTIVE.md` / `.pdf` |
| Group members and responsibilities | "Team members and contributions" below |

**Quick run:** `python -m pip install -r requirements.txt` then `streamlit run app.py`.
Extras: `requirements-api.txt` (FastAPI), `requirements-mlflow.txt` (MLflow), `requirements-notebook.txt` (Jupyter).
The free Streamlit server sleeps when idle: if the live link shows a "wake up" button, press it and wait about 30 seconds.

## Quick start for teammates

New to the project? Start here:

1. **Set up and run the app:** [`docs/SETUP_FOR_TEAMMATES.md`](docs/SETUP_FOR_TEAMMATES.md) (clone or download, install, `streamlit run app.py`).
2. **Understand what you are looking at:** [`docs/APP_GUIDE.md`](docs/APP_GUIDE.md) explains every field, the result and the limits in plain language, with a 5-minute demo script.
3. **No installation at all:** open the notebook in Colab from GitHub:
   <https://colab.research.google.com/github/tsega-ab1/diabetic-readmission-risk/blob/main/notebooks/module5_ai_project_colab.ipynb>

```bash
git clone https://github.com/tsega-ab1/diabetic-readmission-risk.git
cd diabetic-readmission-risk
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

## Project overview

- **Task:** binary classification. Target `readmitted_30d` = 1 if `readmitted == "<30"`, else 0. The
  prediction is made at discharge, from 46 features known at that time.
- **Final model:** **LightGBM** (class-weighted), chosen by highest validation ROC-AUC among five
  candidates: Logistic Regression (baseline), Random Forest, tuned HistGradientBoosting, XGBoost and
  LightGBM. It beat XGBoost by only 0.0004 and has the largest train–validation gap (0.804 vs 0.674);
  see report Sections 9–10.
- **Result on the held-out, patient-disjoint test set:** ROC-AUC 0.6856, PR-AUC 0.2390, recall 0.5289,
  precision 0.2014, F1 0.2917 (decision threshold 0.51). **5 of 6** Module 4 success criteria are met.
  The "5% AUC gain over logistic regression" criterion is **not** met (+1.71%), and two others are met
  only narrowly (ROC-AUC +0.006, top-20% capture +0.001).
- **Output:** a *model score* between 0 and 1 and a Low / Medium / High risk tier. Because of class
  weighting the score is **not** a literal probability (calibration is poor, report Section 11); use it to
  compare patients, not as an absolute risk.

## What is in this submission

| Item | Location |
|---|---|
| Implementation notebook (all 8 tasks, executed) | `notebooks/module5_ai_project_colab.ipynb` |
| Project report | `PROJECT_REPORT.pdf` / `PROJECT_REPORT.docx` |
| README | this file |
| Dataset | `data/diabetic_data.csv`, `data/IDS_mapping.csv` (see `DATA_DICTIONARY.md`) |
| Requirements | `requirements.txt` (app, prediction code, tests), plus `requirements-notebook.txt`, `requirements-api.txt`, `requirements-mlflow.txt` |
| Guides and Module 6 documents | `docs/` (app guide, setup guide, deployment and testing, monitoring plan, statement, retrospective, video script) |
| Container | `Dockerfile`, `.dockerignore` |
| Saved model + metadata | `models/final_model.joblib`, `models/model_metadata.json` |
| Prototype | in-notebook form (Section 8.4) and `app.py` (Streamlit) |
| Shared code and tests | `src/` (`data_preprocessing.py`, `predict.py`), `tests/`, `scripts/` |
| Figures and results | `report_assets/` (figures used in the report), `outputs/` |

## Run in Google Drive + Google Colab (main route)

1. Upload the whole project folder to Google Drive so it is at `My Drive/Module5_AI_Project/`.
2. In Drive, right-click `notebooks/module5_ai_project_colab.ipynb` → *Open with* → *Google Colaboratory*
   (or upload it at <https://colab.research.google.com>).
3. *Runtime → Run all*. The first cell asks permission to access Drive; allow it. The notebook reads
   `Module5_AI_Project/data/diabetic_data.csv` and writes `models/` and `outputs/` back to the same folder.
4. If the data file is missing, the data-loading cell tries the official UCI download, then an upload dialog.
5. If Drive cannot be mounted (pop-ups blocked, wrong Google account) the notebook falls back to the
   temporary `/content` folder and says so; the model is still downloaded in Section 8.5.
6. The notebook is self-contained (it does not import from `src/`) and takes roughly 5–15 minutes on a
   free Colab CPU. XGBoost and LightGBM (fixed, untuned settings) compete for the final model
   (`PROMOTE_EXTRA_TO_FINAL = True`; set it to `False` to choose among the three scikit-learn models only).
7. The group reflection is at the end of the notebook and in report Section 17.

## Run locally (optional)

```bash
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements-notebook.txt
jupyter notebook notebooks/module5_ai_project_colab.ipynb   # run from the project root
```

The notebook finds `data/diabetic_data.csv` relative to the folder it is started in and writes `models/`
and `outputs/` there. The stored outputs in the notebook are from the group's Colab run.

## Prototype

- **In the notebook (Section 8.4):** an `ipywidgets` form — pick a sample case or edit key fields
  (age band, days in hospital, medications, prior visits, diagnoses, insulin, A1C), press *Predict*, and
  receive the score, tier, flag and disclaimer.
- **Streamlit app:** `streamlit run app.py` from the project root. It loads `models/final_model.joblib`
  and scores records through `src/predict.py` (the same code the tests use). Identifiers are never requested.

## Running the tests

```bash
python3 scripts/run_tests_without_pytest.py     # 16 unit tests; works with the core install (requirements.txt)
pip install -r requirements-api.txt             # adds pytest, FastAPI and httpx
python -m pytest tests -v                       # all 23 tests (16 unit + 7 API)
```

The 16 unit tests cover preprocessing, ICD-9 grouping, leakage exclusions, risk-tier boundaries, model loading,
prediction output format, and invalid/missing input handling; the 7 API tests cover `api.py`. The notebook also
contains 10 in-notebook unit tests and 7 end-to-end workflow cases (all passed in the Colab run). Saved output
of these runs is in `docs/evidence/`.

## API and container (Module 6)

```bash
pip install -r requirements-api.txt
python -m uvicorn api:app --port 8000          # then open http://localhost:8000/docs
docker build -t readmission-risk . && docker run --rm -p 8501:8501 readmission-risk   # optional
```

## Experiment tracking (Module 6)

```bash
pip install -r requirements-mlflow.txt
python scripts/log_experiments_mlflow.py       # also writes outputs/results/experiment_log.csv
mlflow ui --backend-store-uri sqlite:///mlflow.db   # open http://localhost:5000 (can take a minute to start)
```

## Model information

| Item | Value |
|---|---|
| Final model | `LightGBM` in a scikit-learn pipeline: 300 trees, learning rate 0.05, 31 leaves, subsample 0.8, column sample 0.8, class-weighted |
| Features | 46 (8 numeric, 38 categorical incl. 23 medication columns and 3 diagnosis groups); `weight` dropped (96.9% missing); 268 columns after one-hot encoding |
| Rows used | 99,340 after excluding expired/hospice discharges and 3 unknown-gender rows |
| Split | patient-grouped 70 / 15 / 15 (69,613 / 14,868 / 14,859 rows), seed 42, zero patient overlap |
| Decision threshold | 0.51, chosen on the validation set (highest precision with recall ≥ 0.50) |
| Risk tiers | Low below 0.42, Medium 0.42–0.60, High from 0.60 (50th and 85th percentiles of validation scores; demonstration values, not clinically validated) |
| Metadata | `models/model_metadata.json` (features, thresholds, test metrics; no patient data) |

## Prediction workflow

`input record → validation → preprocessing → model → score → risk tier + flag → human review`.
Missing or non-numeric fields do not crash the call: they are imputed by the pipeline and listed as
warnings. Out-of-range values and unseen categories also produce warnings.

## Reproducibility and verification

- **Group Colab run** (Python 3.13, scikit-learn 1.6.1, pandas 2.2.3): all 50 code cells ran without
  errors, with Google Drive mounted; 10/10 unit tests and 7/7 workflow cases passed. The report's numbers
  come from this run.
- **Independent re-run** (Python 3.12, scikit-learn 1.6.1, pandas 2.2.3, LightGBM 4.7.0): the notebook was
  re-executed from scratch on the same data file. It selected LightGBM again and reproduced the test
  metrics, confusion matrix, threshold and risk-tier cut points exactly, and the validation metrics of the
  other four models. The one difference is the logistic baseline's validation metrics, which differ in the
  fourth decimal (ROC-AUC 0.6670 vs 0.6673) because of numerical differences; the 1.71% gain figure is
  unchanged. `models/final_model.joblib` was saved by that re-run.
- The Streamlit app was run headlessly (Streamlit's test runner) on the three sample cases and returned the
  same scores and tiers as the notebook (48.6% Medium, 69.0% High, 23.8% Low). A group member also ran it
  in a web browser (Streamlit, Python 3.12) and it ran without errors.
- XGBoost, LightGBM and SHAP versions were not printed in the Colab run, so exact numerical agreement on
  other versions is not guaranteed; always quote the numbers your own run prints.

## Limitations

U.S. data from 130 hospitals, 1999–2008 (outdated practice, not representative of other settings); modest
performance (ROC-AUC 0.69, precision 0.20: about four of five flags are false alarms, and about half of
readmissions are missed, mostly first-time high-risk patients); poor probability calibration; the selected
model has the largest train–validation gap and a near-tie with XGBoost; small hyperparameter search; no
confidence intervals; subgroup results are noisy and no fairness audit was done (race is a model input);
importance and SHAP values show association, not cause; no clinical or external validation. Full list: report
Section 14.

## Team members and contributions

Participating members, by area, following the responsibility table in the approved Module 4 proposal:

| Area | Responsible member(s) |
|---|---|
| Domain / problem research — problem framing, clinical context, references | Fisehatsion Adisu, Birhan Getachew, Asmelash Abriham, Fasikaw Lakew |
| Data discovery / preparation — cleaning, encoding, EDA, patient-grouped split | Daniel Asele, Tsegaye Abate |
| ML/DL development — baseline and candidate models, tuning, evaluation | Fisehatsion Adisu, Addis Misgana |
| Application implementation — prediction function and prototype interface | Tewoderos Adare |
| Deployment / testing — test cases and end-to-end workflow testing | Abrham Mekbib, Asmelash Abriham |
| Documentation / presentation — report, README, discussion posts | Abraham |

The group reflection is in the report (Section 17) and at the end of the notebook.

## Dataset

`data/diabetic_data.csv` (101,766 rows × 50 columns; 71,518 unique patients) and `data/IDS_mapping.csv`
(code look-ups), from the UCI Machine Learning Repository
(<https://archive.ics.uci.edu/dataset/296/diabetes+130-us+hospitals+for+years+1999-2008>, CC BY 4.0).
Citation: Clore, J., Cios, K., DeShazo, J., & Strack, B. (2014). *Diabetes 130-US hospitals for years
1999–2008* [Data set]. UCI Machine Learning Repository. https://doi.org/10.24432/C5230J
