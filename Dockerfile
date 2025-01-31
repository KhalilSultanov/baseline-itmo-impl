FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1
ENV UVLOOP_NO_EXTENSIONS=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "main:app", "--workers", "12", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080"]
