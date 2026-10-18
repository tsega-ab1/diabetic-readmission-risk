"""
Working prototype: Streamlit form around the saved final model.

Run with:  streamlit run app.py
(from the project root, after `pip install -r requirements.txt`)

The app loads models/final_model.joblib (the final LightGBM pipeline) and scores records through
src/predict.py::predict_one -- the same inference path used by tests/test_project.py.
Outputs are a relative model score and a Low / Medium / High tier, for decision support only.
"""
import json
from pathlib import Path

import streamlit as st
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))
import predict  # noqa: E402
from data_preprocessing import MEDICATION_COLUMNS  # noqa: E402

st.set_page_config(page_title="30-Day Diabetic Readmission Risk — Demo", layout="centered")

DISCLAIMER = (
    "This prototype is for academic and research demonstration purposes only. "
    "It is not a medical diagnosis, does not replace professional clinical "
    "judgment, and has not been clinically validated for real-world patient care."
)


def show_result(result):
    """Display one prediction. The same code path is used for typed-in and sample cases."""
    st.subheader("Result")
    tier_color = {"Low": "green", "Medium": "orange", "High": "red"}[result["risk_tier"]]
    st.markdown(f"**Model score (relative, not a literal probability):** {result['probability_30d_readmission']:.1%}")
    st.markdown(f"**Risk tier:** :{tier_color}[{result['risk_tier']}]")
    st.markdown(f"**Flagged as high-risk at the model's decision threshold "
                f"({result['decision_threshold_used']}):** {result['predicted_high_risk_flag']}")
    st.caption("Scores come from a class-weighted model and are inflated relative to the true ~11% "
               "readmission rate; use them to compare patients, not as an absolute probability. "
               "Tiers are project-level percentile cut points, not clinically validated.")
    if result["input_warnings"]:
        st.info("Some fields were missing or invalid and were safely imputed/ignored:\n\n" +
                "\n".join(f"- {w}" for w in result["input_warnings"]))
    st.caption(DISCLAIMER)


st.title("Diabetic Patient 30-Day Readmission Risk — Decision-Support Prototype")
st.warning(DISCLAIMER)

st.markdown(
    "Enter discharge-time patient information below. This demonstration tool "
    "gives a **relative risk score** for the patient being **readmitted to the "
    "hospital within 30 days** of this discharge, based on a model trained on "
    "the UCI *Diabetes 130-US Hospitals (1999\u20132008)* dataset. "
    "Identifiers such as patient or encounter numbers are never used as model inputs."
)

if not predict.MODEL_PATH.exists():
    st.error("No trained model found at models/final_model.joblib. Run the notebook "
             "(notebooks/module5_ai_project_colab.ipynb, Section 8.1) to create it before using this app.")
    st.stop()

_, metadata = predict._load()

sample_map = {
    "Typical case": "outputs/results/sample_typical.json",
    "Higher-risk case": "outputs/results/sample_higher_risk.json",
    "Lower-risk case": "outputs/results/sample_lower_risk.json",
}
with st.expander("Try a de-identified sample case (real test-set feature values, no identifiers)"):
    sample_choice = st.selectbox("Sample", ["(none)"] + list(sample_map))
    if sample_choice != "(none)" and Path(sample_map[sample_choice]).exists():
        sample_record = json.load(open(sample_map[sample_choice]))["input"]
        st.json(sample_record, expanded=False)
        if st.button("Score this sample case"):
            show_result(predict.predict_one(sample_record))

st.subheader("Patient Encounter Information")

col1, col2, col3 = st.columns(3)
with col1:
    AGE_BANDS = ["[0-10)", "[10-20)", "[20-30)", "[30-40)", "[40-50)", "[50-60)", "[60-70)", "[70-80)", "[80-90)", "[90-100)"]
    age = st.selectbox("Age band", AGE_BANDS, index=7)
    gender = st.selectbox("Gender", ["Female", "Male"])
    race = st.selectbox("Race", ["Caucasian", "AfricanAmerican", "Hispanic", "Asian", "Other", "Unknown"])
with col2:
    admission_type_id = st.selectbox("Admission type (coded)", ["1", "2", "3", "4", "5", "6", "7", "8"],
                                      help="1=Emergency, 2=Urgent, 3=Elective, 7=Trauma Center, etc. (see DATA_DICTIONARY.md)")
    discharge_disposition_id = st.text_input("Discharge disposition (coded)", value="1",
                                              help="1=Discharged to home. See DATA_DICTIONARY.md for the full code list.")
    admission_source_id = st.text_input("Admission source (coded)", value="7",
                                         help="7=Emergency Room, 1=Physician Referral, etc.")
with col3:
    time_in_hospital = st.number_input("Length of stay (days)", min_value=1, max_value=14, value=4)
    number_diagnoses = st.number_input("Number of diagnoses", min_value=1, max_value=20, value=7)
    payer_code = st.text_input("Payer code (or 'Unknown')", value="Unknown")

st.markdown("**Prior-year utilization**")
col4, col5, col6 = st.columns(3)
with col4:
    number_outpatient = st.number_input("Outpatient visits (prior yr)", min_value=0, max_value=50, value=0)
with col5:
    number_emergency = st.number_input("Emergency visits (prior yr)", min_value=0, max_value=50, value=0)
with col6:
    number_inpatient = st.number_input("Inpatient visits (prior yr)", min_value=0, max_value=50, value=0,
                                        help="The single strongest predictor in this model \u2014 see the project report, Section 11 (Interpretability).")

st.markdown("**This encounter**")
col7, col8, col9 = st.columns(3)
with col7:
    num_lab_procedures = st.number_input("Lab procedures", min_value=0, max_value=150, value=43)
with col8:
    num_procedures = st.number_input("Procedures", min_value=0, max_value=10, value=1)
with col9:
    num_medications = st.number_input("Medications administered", min_value=0, max_value=100, value=16)

st.markdown("**Diabetes-related**")
col10, col11, col12 = st.columns(3)
with col10:
    max_glu_serum = st.selectbox("Max glucose serum test", ["Not tested", "Norm", ">200", ">300"])
with col11:
    A1Cresult = st.selectbox("A1C test result", ["Not tested", "Norm", ">7", ">8"])
with col12:
    insulin = st.selectbox("Insulin", ["No", "Steady", "Up", "Down"])

change = st.selectbox("Medication changed this encounter?", ["No", "Ch"])
diabetesMed = st.selectbox("On a diabetes medication?", ["Yes", "No"])
medical_specialty = st.text_input("Admitting medical specialty (or 'Unknown')", value="Unknown")

diag_1_group = st.selectbox("Primary diagnosis group", ["Circulatory", "Respiratory", "Digestive", "Diabetes",
                                                          "Injury", "Musculoskeletal", "Genitourinary",
                                                          "Neoplasms", "Other", "Missing"],
                             help="Pre-grouped per the ICD-9 scheme in src/data_preprocessing.icd9_to_category")
diag_2_group = st.selectbox("Secondary diagnosis group", ["Circulatory", "Respiratory", "Digestive", "Diabetes",
                                                            "Injury", "Musculoskeletal", "Genitourinary",
                                                            "Neoplasms", "Other", "Missing"])
diag_3_group = st.selectbox("Tertiary diagnosis group", ["Circulatory", "Respiratory", "Digestive", "Diabetes",
                                                           "Injury", "Musculoskeletal", "Genitourinary",
                                                           "Neoplasms", "Other", "Missing"])

with st.expander("Diabetes medication detail (23 fields \u2014 defaults to 'No' / not prescribed)"):
    med_values = {}
    cols = st.columns(3)
    for i, med in enumerate(MEDICATION_COLUMNS):
        with cols[i % 3]:
            med_values[med] = st.selectbox(med, ["No", "Steady", "Up", "Down"], key=med)

if st.button("Predict 30-day readmission risk", type="primary"):
    record = {
        "age": age, "gender": gender, "race": race,
        "admission_type_id": admission_type_id,
        "discharge_disposition_id": discharge_disposition_id,
        "admission_source_id": admission_source_id,
        "time_in_hospital": time_in_hospital,
        "number_diagnoses": number_diagnoses,
        "payer_code": payer_code,
        "number_outpatient": number_outpatient,
        "number_emergency": number_emergency,
        "number_inpatient": number_inpatient,
        "num_lab_procedures": num_lab_procedures,
        "num_procedures": num_procedures,
        "num_medications": num_medications,
        "max_glu_serum": max_glu_serum,
        "A1Cresult": A1Cresult,
        "insulin": insulin,
        "change": change,
        "diabetesMed": diabetesMed,
        "medical_specialty": medical_specialty,
        "diag_1_group": diag_1_group,
        "diag_2_group": diag_2_group,
        "diag_3_group": diag_3_group,
        **med_values,
    }
    show_result(predict.predict_one(record))

st.divider()
_test = metadata.get("evaluation_metrics_test_set", {})
st.caption(
    f"Model: {metadata.get('model_name', 'unknown')} | "
    f"Test-set ROC-AUC: {_test.get('roc_auc', 'n/a')} | "
    "See PROJECT_REPORT.pdf for the full evaluation, limitations, and ethical considerations."
)
