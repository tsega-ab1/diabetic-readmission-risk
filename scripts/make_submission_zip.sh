#!/usr/bin/env bash
# Builds the Module 6 portfolio ZIP from what is committed in Git, after checking that it is ready.
#   bash scripts/make_submission_zip.sh          (run from anywhere inside the repository)
set -u
cd "$(dirname "$0")/.."
fail=0

if grep -rIn "STREAMLIT_URL""_HERE" --exclude-dir=.git --exclude-dir=.venv . ; then
  echo "-> Replace the placeholder above with your real Streamlit address."; fail=1
fi
n=$(ls docs/screenshots/*.png 2>/dev/null | wc -l)
if [ "$n" -lt 5 ]; then echo "-> Only $n screenshots in docs/screenshots/ (need at least 5; see the README there)."; fail=1; fi
for f in app.py README.md requirements.txt models/final_model.joblib docs/MONITORING_SUPPORT_MAINTENANCE_PLAN.md \
         docs/SIMULATED_DATA_STATEMENT.md docs/RETROSPECTIVE.pdf; do
  [ -f "$f" ] || { echo "-> Missing file: $f"; fail=1; }
done
if [ -n "$(git status --porcelain)" ]; then
  echo "-> You have changes that are not committed:"; git status --short
  echo "   Run:  git add . && git commit -m \"Module 6 final\" && git push"; fail=1
fi
if [ "$fail" -ne 0 ]; then echo; echo "NOT READY: fix the lines above and run this script again."; exit 1; fi

out="../Module6_Portfolio.zip"
git archive --format=zip --prefix=diabetic-readmission-risk/ -o "$out" HEAD
echo "Created $(cd .. && pwd)/Module6_Portfolio.zip"; ls -lh "$out"
echo "Files in the ZIP: $(unzip -l "$out" | tail -1)"
