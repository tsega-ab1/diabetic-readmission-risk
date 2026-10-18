# Setup guide for teammates — get the project and run the app

You do **not** need to know how to code. You need to copy and paste the commands below.
Time: about 10 minutes (most of it is a download).

Replace `REPO_URL` / `diabetic-readmission-risk` below if the repository has a different name.
Repository: **https://github.com/tsega-ab1/diabetic-readmission-risk**

---

## Step 0 — Check Python

You need **Python 3.10, 3.11, 3.12 or 3.13** (3.12 is best). **Python 3.14 will not work.**

Open a terminal (see Step 2 for how) and run:

```
python3 --version        # Mac / Linux
python --version         # Windows
```

If it says "not found" or the version is wrong, install Python 3.12 from <https://www.python.org/downloads/>.
On **Windows**, tick **"Add python.exe to PATH"** on the first installer screen.

## Step 1 — Get the project (pick ONE option)

**Option A — no Git needed (easiest)**
1. Open the repository page in your browser.
2. Click the green **Code** button → **Download ZIP**.
3. Unzip it. You get a folder (e.g. `diabetic-readmission-risk-main`). Remember where it is.

**Option B — with Git**
```
git clone https://github.com/tsega-ab1/diabetic-readmission-risk.git
cd diabetic-readmission-risk
```
(If the repository is private, you must be added as a collaborator first, accept the email invitation, and
sign in when Git asks. If that is confusing, use Option A while logged in to GitHub.)

## Step 2 — Open a terminal *inside* the project folder

- **Windows:** open the folder in File Explorer, click the address bar, type `cmd`, press Enter.
- **Mac:** right-click the folder → *New Terminal at Folder* (or open Terminal and `cd` into it).
- **Linux:** right-click inside the folder → *Open Terminal Here*.

You should be in the folder that contains `app.py`. Check with `dir` (Windows) or `ls` (Mac/Linux).

## Step 3 — Create a private Python environment (keeps your computer tidy)

| | Windows (cmd) | Mac / Linux |
|---|---|---|
| Create | `python -m venv .venv` | `python3 -m venv .venv` |
| Activate | `.venv\Scripts\activate` | `source .venv/bin/activate` |

After activating, your prompt starts with `(.venv)`. **Do this activation again every time you open a new
terminal.**

- *Ubuntu / Linux Mint / Debian:* if `venv` fails, first run `sudo apt install python3-venv`.
- *Windows PowerShell blocks activation?* Use `cmd` as above, or run
  `Set-ExecutionPolicy -Scope Process Bypass` and then `.venv\Scripts\Activate.ps1`.

## Step 4 — Install the libraries

```
python -m pip install --default-timeout=120 --retries 10 -r requirements-app.txt
```

This installs only what the app needs (a few hundred MB). If your internet is slow and it stops with a
"timed out" error, **just run the same command again**: it continues from what it already downloaded.

> Want the full notebook environment too (Jupyter, XGBoost, SHAP)? Use `requirements.txt` instead. It is
> much bigger.

## Step 5 — Run the app

```
streamlit run app.py
```

- Your browser opens at <http://localhost:8501>. If not, copy that address into your browser.
- If it asks for an email, just press **Enter** to skip.
- To stop the app, click the terminal and press **Ctrl + C**.

## Step 6 — Use it

Open `docs/APP_GUIDE.md` for a plain-language explanation of every field and a 5-minute demo script.
Quick check that everything works: open the *sample case* box, choose **Higher-risk case**, press
**Score this sample case**. You should see about **69.0% — High**.

## Optional extras

- **Run the automated tests (16 checks):** `python scripts/run_tests_without_pytest.py`
  (expected last line: `16 passed, 0 failed, 0 errors out of 16`).
- **Read the full report:** `PROJECT_REPORT.pdf`.
- **Run the notebook with no installation, in the browser:** open this link (works for a public repo) and
  choose *Runtime → Run all*:
  <https://colab.research.google.com/github/tsega-ab1/diabetic-readmission-risk/blob/main/notebooks/module5_ai_project_colab.ipynb>
  (the notebook downloads the data itself if it cannot find it).
- **Get the latest version later (Git users):** `git pull`.

## If something goes wrong

| Problem | Fix |
|---|---|
| `python` / `python3` not found | Install Python 3.12 (Step 0). On Windows try `py` instead of `python`. |
| `No matching distribution found for pandas==2.2.3` | Your Python is too new (3.14) or too old (below 3.10). Install Python 3.12. |
| `streamlit` is not recognized | The environment is not active. Repeat Step 3's *Activate* line, then try `python -m streamlit run app.py`. |
| Install stops with *timed out* / *Read timed out* | Slow internet. Run the Step 4 command again (it resumes). |
| `No trained model found at models/final_model.joblib` | You are not in the project folder, or the download is incomplete. Re-download the ZIP and check that `models/final_model.joblib` exists. |
| Error mentioning `scikit-learn` or `pickle` version | You installed different library versions. Delete the `.venv` folder and redo Steps 3–4. |
| Browser shows nothing | Go to <http://localhost:8501> manually; check the terminal for a different port number. |
| Anything else | Take a screenshot of the terminal **and** the browser and send it to Tsega. |

## Rules for the shared repository

- Don't edit or delete anything in `models/` or `data/`; the report's numbers depend on those files.
- If you want to change something, tell Tsega first, or edit a copy.
