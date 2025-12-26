FROM python:3.9.21-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt


COPY app.py .
COPY module.py .
COPY template_prompt.py .
COPY queries ./queries


CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]