# Demonstration container for the readmission-risk prototype (Streamlit app by default, FastAPI on request).
#   Build:        docker build -t readmission-risk .
#   Web app:      docker run --rm -p 8501:8501 readmission-risk
#   API instead:  docker run --rm -p 8000:8000 readmission-risk \
#                   python -m uvicorn api:app --host 0.0.0.0 --port 8000
# Contains the saved model and de-identified sample cases only. It contains no patient data and no secrets.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# LightGBM needs the OpenMP runtime
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-api.txt ./
RUN pip install --no-cache-dir -r requirements-api.txt

COPY app.py api.py ./
COPY src ./src
COPY models ./models
COPY outputs/results ./outputs/results
COPY .streamlit ./.streamlit

# run as a non-root user
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8501 8000
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
