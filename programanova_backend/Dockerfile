FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY requirements_pro.txt .

RUN pip install --no-cache-dir -r requirements.txt -r requirements_pro.txt

COPY . .

CMD ["sh", "-c", "python -m uvicorn main_pro:app --host 0.0.0.0 --port $PORT"]
