FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app.py .
COPY module.py .
COPY gunicorn.config.py .
COPY queries ./queries


CMD ["gunicorn", "app:app", "-c", "gunicorn.config.py"]