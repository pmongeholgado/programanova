FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY requirements_pro.txt .

RUN pip install --no-cache-dir -r requirements.txt -r requirements_pro.txt

COPY . .

CMD ["uvicorn", "main_pro:app", "--host", "0.0.0.0", "--port", "8080"]
