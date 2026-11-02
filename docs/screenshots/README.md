# Screenshots for the portfolio

Add your screenshots to this folder with these names (PNG). At least five are needed; more is better.
Run the app first (`streamlit run app.py`) and use the steps in `docs/APP_GUIDE.md` section 6.

| File name | What to capture |
|---|---|
| `01_app_home.png` | The top of the web app, with the yellow disclaimer visible |
| `02_sample_higher_risk.png` | Sample box → *Higher-risk case* → *Score this sample case* → result (about 69.0%, High) |
| `03_form_inpatient_5.png` | Form with *Inpatient visits (prior yr)* = 5 → *Predict* → result (about 78.5%, High) |
| `04_warning_xyz.png` | Type `XYZ` in *Discharge disposition* → *Predict* → the blue warning box |
| `05_tests_passing.png` | Terminal after `python -m pytest tests -v` (last line: 23 passed; needs `requirements-api.txt`) |
| `06_api_docs.png` | `http://localhost:8000/docs` after `python -m uvicorn api:app --port 8000` |
| `07_mlflow_ui.png` | `http://localhost:5000` after `mlflow ui --backend-store-uri sqlite:///mlflow.db` (wait up to a minute), showing the experiment table |
| `08_streamlit_cloud.png` | The deployed app open in the browser, with the public address bar visible |
| `09_github_repo.png` | The GitHub repository page |
