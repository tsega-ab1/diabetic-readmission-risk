# How the web app works — a plain-language guide

For teammates with no coding or health background. Everything here describes the app you start with
`streamlit run app.py`.

> **Reminder:** this is a student demonstration. It is **not** a medical tool, it has **not** been tested on
> real patients, and nobody should use it to make a real health decision.

---

## 1. The 30-second version

When a diabetic patient leaves the hospital, some of them come back within 30 days (a **readmission**). That
is bad for the patient and expensive for the hospital. If staff knew in advance *which* patients are most
likely to come back, they could spend their limited time (follow-up calls, extra check-ups) on those
patients first.

Our app does one thing: you type in facts about a hospital stay, and it returns a **risk score** and a
**risk tier (Low / Medium / High)** that say how this patient compares with the thousands of past patients the
model learned from.

Think of it like a weather forecast for a hospital stay: it does not say what *will* happen, it says how
*likely* a bad outcome looks based on similar past cases.

## 2. What happens when you press the button

```
 You fill in the form
        │
        ▼
 1. CHECK       The app makes sure the numbers are really numbers, and notes anything missing or odd.
        │
        ▼
 2. TRANSLATE   Computers only understand numbers. Words like "Female" or "Insulin: Up" are turned into
        │       numbers, blanks are filled with typical values, and sizes are put on the same scale.
        │       (46 questions become 268 number-columns. We used exactly the same recipe when training.)
        ▼
 3. MODEL       The trained model (called LightGBM) looks at the numbers and produces a score.
        │
        ▼
 4. RESULT      Score → Low / Medium / High tier + a yes/no "flag" + warnings + disclaimer
```

**What is "the model"?** LightGBM is a *team of 300 small decision trees*. Each tree asks a few yes/no
questions about the patient (for example, "was there more than one hospital admission last year?") and adds a
small push up or down. The model adds up all 300 pushes to get the score. It learned which questions matter by
studying about 70,000 past hospital stays where we already knew who was readmitted.

**Where does the data come from?** A public research dataset of 101,766 hospital stays at 130 US hospitals
from 1999–2008 (UCI Machine Learning Repository). It contains no names. The model has never seen anything
newer or from other countries.

## 3. A tour of the screen (top to bottom)

| What you see | What it is |
|---|---|
| **Yellow warning banner** | The disclaimer. It stays on screen on purpose. |
| **"Try a de-identified sample case"** (click to open) | Three real rows from our *test* data (no names or ID numbers): *Typical*, *Higher-risk*, *Lower-risk*. Pick one, press **Score this sample case**. Note: picking a sample does **not** fill in the form below; they are separate. |
| **Patient Encounter Information** (3 columns) | The form for a patient you want to score yourself. Fields are explained in section 4. |
| **Prior-year utilization**, **This encounter**, **Diabetes-related** | The rest of the form, grouped by topic. |
| **"Diabetes medication detail (23 fields)"** (click to open) | One drop-down per diabetes drug. Leave on "No" unless you want to experiment. |
| **Predict 30-day readmission risk** (blue button) | Runs steps 1–4 above on the form. |
| **Result** | Score, tier, flag, any warnings, disclaimer. See section 5. |
| **Grey line at the bottom** | Which model is loaded (LightGBM) and its test-set quality score (ROC-AUC 0.6856). |

## 4. What each input means

An **encounter** is one hospital stay. **Inpatient** = admitted to the hospital (usually overnight or longer).
**Outpatient** = a visit without being admitted. **Discharge** = leaving the hospital.

| Field | Plain meaning | Why the model cares |
|---|---|---|
| **Age band** | Age in 10-year groups, e.g. `[70-80)` = 70 to 79. | Risk differs a little by age. |
| **Gender** | Female / Male. | Small effect. |
| **Race** | As recorded in the hospital record. | The model can see it, which is a **fairness concern** (see section 7). |
| **Admission type (coded)** | Why the patient came in: 1 Emergency, 2 Urgent, 3 Elective (planned), 4 Newborn, 5 Not available, 6 Missing, 7 Trauma center, 8 Not mapped. | Emergencies tend to be sicker. |
| **Discharge disposition (coded)** | *Where the patient went after leaving.* 1 = home, 6 = home with a visiting nurse, 3 = nursing facility, 22 = rehab facility, 2 = another hospital, 7 = left against advice. Full list in `data/IDS_mapping.csv`. | One of the strongest signals: where someone goes next says a lot about how sick they are. |
| **Admission source (coded)** | How they arrived: 7 = emergency room, 1 = doctor's referral, 4 = transferred from another hospital, etc. | Context for how serious the stay was. |
| **Length of stay (days)** | Days in hospital (1–14). | Longer stays usually mean more complex illness. |
| **Number of diagnoses** | How many separate conditions were recorded (1–20). | More conditions, more complexity. |
| **Payer code** | Who pays: the insurance type, e.g. `MC` = Medicare. Type `Unknown` if you don't know. | Weak signal; often missing in the data. |
| **Outpatient visits (prior year)** | Visits to hospital clinics in the past year without being admitted. | Shows how much care the patient already needs. |
| **Emergency visits (prior year)** | Emergency-room visits in the past year. | Frequent ER use goes with higher risk. |
| **Inpatient visits (prior year)** | Times admitted to hospital in the past year. | **The single strongest signal.** In our data, patients with 0 prior admissions were readmitted about 8.6% of the time; with 5 or more, about 37.1%. |
| **Lab procedures** | Number of lab tests done during this stay. | A rough measure of how much work-up was needed. |
| **Procedures** | Number of procedures (not counting lab tests), e.g. a surgery. | Same idea. |
| **Medications administered** | How many different medicines were given. | More medicines usually means a sicker patient. |
| **Max glucose serum test** | The highest *blood-sugar* reading in a blood test this stay: Normal, above 200, above 300 (mg/dL), or Not tested. | Shows how well blood sugar was controlled. |
| **A1C test result** | **HbA1c**: a blood test showing *average blood sugar over the last 2–3 months*. Normal, above 7 %, above 8 % (poorly controlled), or Not tested. | In this data, "not tested" went with slightly more readmissions (11.7% vs about 10%). Not testing is not itself harmful; this is just a pattern. |
| **Insulin** | Is insulin prescribed, and was the dose changed: No / Steady / Up (increased) / Down (decreased). | Dose changes can signal unstable blood sugar. |
| **Medication changed this encounter?** | `Ch` = a diabetes medicine was changed during the stay; `No` = no change. | Same idea. |
| **On a diabetes medication?** | Yes / No. | Basic treatment status. |
| **Admitting medical specialty** | The type of doctor who admitted the patient, e.g. `InternalMedicine`, `Cardiology`. `Unknown` if not known. | Weak signal; about half the records leave it blank. |
| **Primary / Secondary / Tertiary diagnosis group** | The main, second and third conditions, sorted into 9 broad groups (Circulatory = heart and blood vessels, Respiratory = lungs, Digestive, Diabetes, Injury, Musculoskeletal = bones and muscles, Genitourinary = kidneys and urinary, Neoplasms = tumours, Other) or Missing. Hospitals record diagnoses with ICD-9 codes; we grouped them. | The type of illness matters. |
| **23 medication fields** | One drop-down per diabetes drug (metformin, glipizide, …): No / Steady / Up / Down. | Detailed treatment picture. |

The app never asks for a name, patient number or encounter number, and the model never uses them.

## 5. How to read the result

1. **Model score (e.g. 48.6%)**. A number from 0% to 100% used to **rank** patients. It is **not** a real
   probability. We told the model to pay extra attention to the rare readmitted patients (about 11 in 100),
   which inflates every score. Use it to say "patient A looks riskier than patient B", never "this patient has a
   48.6% chance".
2. **Risk tier**. The score put into three bands, based on where it falls among our validation patients:
   - 🟢 **Low** — below 42% (roughly the lower half of patients)
   - 🟠 **Medium** — 42% to 60%
   - 🔴 **High** — 60% and above (roughly the top 15% of patients)

   These cut points are for demonstration. They are not medical guidelines.
3. **Flagged as high-risk (True/False)**. A separate yes/no at a score of **0.51**. We picked 0.51 so the model
   catches about half of the patients who really get readmitted. Because 0.51 sits inside the Medium band, a
   patient can be **Medium and still flagged True**. That is expected, not a bug.
4. **Blue "Some fields were missing or invalid…" box.** The app is telling you it noticed something odd (a
   value outside what the model has seen, or a category it doesn't recognise). It still gives a score, but that
   score may be less reliable.
5. **The disclaimer** is shown again under every result.

## 6. Try it yourself (5-minute demo)

Scores below are what our shipped model gives; yours should match.

| Do this | You should see |
|---|---|
| Open the sample box → **Typical case** → **Score this sample case** | about **48.6% — Medium** |
| …**Higher-risk case** | about **69.0% — High** |
| …**Lower-risk case** | about **23.8% — Low** |
| Leave the form on its defaults, press **Predict** | about **44.6% — Medium** |
| Set **Inpatient visits (prior yr)** to **2**, press Predict | about **63.6% — High** |
| Set it to **5**, press Predict | about **78.5% — High** |
| Back to 0. Type `XYZ` in **Discharge disposition**, press Predict | a score plus a blue box saying "Unexpected category 'XYZ' … treated as unknown" |

That inpatient-visits experiment is the easiest way to show the group that the model "learned" something real:
more admissions last year, higher score.

## 7. What it can and cannot do (say this out loud when presenting)

- **It is a ranking aid, not a prediction of a specific person's future.**
- **Quality is modest.** On held-out test patients it finds about **half** of the real readmissions (recall
  0.53) and about **4 out of 5 patients it flags do not come back** (precision 0.20). It mostly misses
  first-time high-risk patients, because its best clue is *prior* admissions.
- **Old, US-only data (1999–2008).** Medicine has changed; other countries differ.
- **Fairness is not proven.** Race is one of the inputs and our subgroup checks were small and noisy. Before any
  real use this would need a proper fairness review.
- **It shows association, not cause.** Being discharged to rehab raises the score because those patients are
  sicker, not because rehab causes readmission.
- **It needs a human.** Every flag would have to be reviewed by a clinician.

## 8. Mini-glossary of the technical words in our report

| Word | Meaning here |
|---|---|
| **Model** | The trained program that turns inputs into a score. |
| **Training / test data** | Patients the model learned from vs. patients kept hidden to check it honestly afterwards. We split by *patient*, so nobody appears in both. |
| **Baseline** | A simple first model (logistic regression) that fancier models must beat. |
| **ROC-AUC** | How well the model ranks risky patients above safe ones. 0.5 = coin flip, 1.0 = perfect. Ours: **0.69**, which is real but modest. |
| **Recall** | Of the patients who really were readmitted, the share we caught. Ours: **53%**. |
| **Precision** | Of the patients we flagged, the share who really were readmitted. Ours: **20%**. |
| **Threshold** | The score above which we raise a flag (0.51). Moving it trades more catches against more false alarms. |
| **Calibration** | Whether a score of 40% really means 40 in 100. Ours does **not**, which is why we call it a score. |
| **Overfitting** | Memorising the training data. Our final model shows some (training 0.80 vs validation 0.67). |
| **SHAP / permutation importance** | Two ways of asking "which inputs mattered most?" Both put prior inpatient visits first. |
