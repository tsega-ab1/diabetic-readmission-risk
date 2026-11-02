# One-Page Retrospective (Deliverable C)

**Predicting 30-day readmission risk in diabetic patients, FUSE AI-201, Group 2**

**Achievements.** We took one idea from a written proposal (Module 4) to a working, tested prototype (Modules 5
and 6). We built a five-model comparison on 99,340 real hospital stays with a patient-grouped split, chose
LightGBM, and reached ROC-AUC 0.6856, PR-AUC 0.2390 and recall 0.5289 on a held-out test set, meeting 5 of our 6
numeric success criteria. We delivered a Streamlit web app, a FastAPI service, a Dockerfile, MLflow experiment
tracking, 23 automated tests, a plain-language guide for non-technical teammates, a monitoring and maintenance
plan, and a GitHub repository that teammates can clone and run in minutes.

**Challenges.** Evaluation was the hardest part: many patients appear more than once, so a normal random split
would have leaked patients between training and test, and always predicting "no readmission" already scores 88%
accuracy. Early Colab runs failed to mount Google Drive and left our boosted models out of model selection, so
we fixed the notebook and re-ran it. The five models differed by only about 0.01 ROC-AUC, so choosing a winner
was close to a tie. Coordinating a large group on a short timeline was also difficult, so we agreed roles early and shared
the work among the members who were active.

**Lessons learned.** Careful evaluation design matters more than model complexity. Honest reporting builds more
trust than a good-looking number: our model beats the baseline by only 1.71%, and the report says so. A model
is only useful if someone can run it, so clear setup steps, pinned library versions and tests are part of the
work. Writing the monitoring plan showed us that deploying a model is mostly about watching it afterwards.

**Limitations.** The data are US records from 1999–2008, so the model may not suit modern hospitals. Performance
is modest (about four in five flags are false alarms and about half of readmissions are missed, mostly
first-time high-risk patients). The scores are not calibrated probabilities. Race is a model input and we did not
run a full fairness audit. The model has no clinical validation, and the prototype has no login, no live
monitoring and no connection to hospital systems.

**Planned improvements.** Recalibrate the scores; tune XGBoost and LightGBM with cross-validation; add features
for first-time high-risk patients; run a proper fairness audit and review the race input; validate on newer data
after mapping ICD-10 codes; add per-patient explanations to the app; and add authentication and a monitoring
dashboard before any real use.
