# Capstone video: run-of-show (maximum 10 minutes, maximum 250 MB)

**Target length: 9 min 45 s** (leaves a safety margin). Ten speakers, one segment each, in the order the
assignment lists its content. Each speaker starts with their name and one sentence on what they did.
Segments follow each person's Module 4 area. **Swap names freely, but keep every member who contributed in the
video** (the assignment requires it), and drop anyone who did not take part.

Say things in your own words. The bullets are talking points, not a script to read.

| # | Time | Speaker | Segment | On screen |
|---|---|---|---|---|
| 1 | 0:00–0:50 | Birhan Getachew | Problem and solution | Report Section 2, or one slide |
| 2 | 0:50–1:35 | Fasikaw Lakew | Users, data source, simulated data | Report Sections 3 and 5 |
| 3 | 1:35–2:30 | Daniel Asele | Data preparation | Report Section 6 table |
| 4 | 2:30–3:15 | Tsegaye Abate | Split, leakage and EDA | Report Section 7 charts |
| 5 | 3:15–4:15 | Addis Misgana | Models and results | Report Section 9 table and chart |
| 6 | 4:15–5:00 | Fisehatsion Adisu | Evaluation, strengths and limits | Report Section 11 |
| 7 | 5:00–6:30 | Tewoderos Adare | **Live demo** | The running app |
| 8 | 6:30–7:40 | Abrham Mekbib | Testing and deployment approach | Terminal, API page, MLflow, GitHub |
| 9 | 7:40–8:40 | Asmelash Abriham | Monitoring, support, maintenance, security | Plan document |
| 10 | 8:40–9:45 | Abraham | Implemented vs simulated vs future; reflection | One slide, then the retrospective |

---

## 1. Problem and solution (Birhan Getachew, 0:50)
- "I worked on the domain and problem research."
- When a diabetic patient leaves hospital, some come back within 30 days (about 11 in 100 in our data). That is
  harmful for the patient and costly for the hospital.
- Discharge teams have limited time. Today they judge by experience.
- Module 4: we proposed a model that ranks patients by readmission risk at discharge so staff can follow up
  with the riskiest first.
- Module 5: we built it. It is decision support, not a diagnosis.

## 2. Users, data source, simulated data (Fasikaw Lakew, 0:45)
- Users: discharge nurses and case managers first; doctors and hospital quality staff second.
- Data: the public UCI dataset of 101,766 hospital stays at 130 US hospitals, 1999–2008. It is de-identified.
- **State clearly: we used no simulated data for training or testing.** The only made-up values are hand-made
  odd inputs used to test error handling (show the Simulated Data Statement for two seconds).

## 3. Data preparation (Daniel Asele, 0:55)
- Dropped `weight` (97% missing). Kept `payer_code` and `medical_specialty` gaps as an "Unknown" category.
- Excluded 2,423 patients who died or went to hospice, because they cannot be readmitted (that would leak the answer).
- Grouped diagnosis codes into 9 groups; turned words into numbers; filled gaps. 99,340 stays remained.

## 4. Split, leakage and exploration (Tsegaye Abate, 0:45)
- 23.5% of patients appear more than once, so we split **by patient** (70/15/15): no patient is in both training and test.
- Only about 11% of stays are readmissions, so accuracy is misleading (always saying "no" scores 88%).
- Strongest pattern: readmission rises from 8.6% with no prior admissions to 37.1% with five or more (show the bar chart).

## 5. Models and results (Addis Misgana, 1:00)
- Five models: logistic regression (baseline), random forest, tuned HistGradientBoosting, XGBoost, LightGBM.
- All five landed within about 0.01 ROC-AUC. LightGBM was best on validation by a tiny margin.
- Final model on the untouched test set: ROC-AUC 0.6856, PR-AUC 0.2390, recall 0.5289.
- It beats the baseline by only 1.71%. We report that plainly.

## 6. Evaluation, strengths and limits (Fisehatsion Adisu, 0:45)
- Five of six success criteria met; the "5% better than baseline" one was missed. Two were met by thin margins.
- Catches about half of real readmissions; about four in five flags are false alarms.
- 97% of missed cases were patients with 0 or 1 earlier admission. Scores are **not** true probabilities.
- No fairness audit; not clinically validated.

## 7. LIVE DEMO (Tewoderos Adare, 1:30)
Have the app already open (local and the public link). Do exactly this, and say what you are doing:
1. Point to the yellow disclaimer. "It is a demonstration, not medical advice."
2. Open **"Try a de-identified sample case"** → choose **Higher-risk case** → **Score this sample case**.
   Result: about **69.0%, High**. "These are real test rows without names or ID numbers."
3. Scroll to the form. Leave the defaults → **Predict**: about **44.6%, Medium**. Explain: input → the app checks it
   → converts words to numbers → the LightGBM model scores it → tier.
4. Set **Inpatient visits (prior yr)** to **5** → **Predict**: about **78.5%, High**. "More admissions last year, higher score."
5. Type `XYZ` in **Discharge disposition** → **Predict**: the blue warning box appears. "Odd input gives a warning, not a crash."
6. Say what the score means: a ranking, not a probability.

## 8. Testing and deployment approach (Abrham Mekbib, 1:10)
- Testing: 23 automated tests pass (show terminal), plus 7 end-to-end workflow cases and 10 notebook unit tests.
- Invalid input: missing or text values, unseen categories and extreme numbers give warnings. Malformed API calls return an error code.
- Experiment tracking: MLflow records all five models and the final test results (show the MLflow screen or screenshot).
- How to run it: GitHub repository (clone, install, `streamlit run app.py`); live Streamlit Community Cloud link;
  FastAPI endpoint (show `/docs`); Dockerfile for a container.
- Be honest about status: **FastAPI is implemented and tested. The Dockerfile is written; say whether the group built it** (use the line that is true).

## 9. Monitoring, support, maintenance, security (Asmelash Abriham, 1:00)
- Watch for drift without waiting for outcomes: flagged share, score mix, input changes, warning rate, latency.
- Outcomes arrive 30 days later, so monthly we check ROC-AUC, recall and precision against our test baseline.
- Retrain when quality drops for two months, when inputs drift, or when coding changes (our data uses old ICD-9 codes).
- New model must beat the current one on recent patients and not get worse for any group.
- Security and fairness: no patient values in logs, login and HTTPS needed in real use, review the race input, monitor by subgroup.

## 10. Implemented vs simulated vs future; reflection (Abraham, 1:05)
Show a three-column slide:
- **Implemented:** the model, Streamlit app, FastAPI service, tests, MLflow log, GitHub repository, plan documents.
- **Simulated / hand-made:** only the edge-case test inputs. No simulated training or test data.
- **Future:** recalibration, tuning, newer data with ICD-10, fairness audit, login, monitoring dashboard, hospital integration.

Then the reflection (from the retrospective): the hardest part was honest evaluation; we learned that careful
evaluation matters more than model complexity; limitations are old data and modest accuracy. Close by thanking the team.

---

## How to record (pick one)

**Option A, easiest: one live recording.** Start a Zoom or Google Meet call, share one prepared screen, press
Record, and each person speaks in turn. Download the recording as MP4.

**Option B: each person records their own clip** (phone or OBS Studio, same 1280×720 setting), then join the
clips with a free editor (Clipchamp, Shotcut, CapCut) in the order above.

**Before recording:** have the app running, the report PDF open, and a stopwatch. Rehearse once. Practise each
segment to its time: it is easy to run long.

## Keep the file under 250 MB and 10 minutes
Check the size: `ls -lh video.mp4`. If it is too big, compress with ffmpeg (free):
```
ffmpeg -i video.mp4 -vf "scale=1280:-2" -c:v libx264 -crf 28 -preset medium -c:a aac -b:a 96k video_small.mp4
```
A 10-minute video at this setting is usually 50–100 MB. Keep audio clear and text readable.
Play the finished file once from start to end before uploading.
