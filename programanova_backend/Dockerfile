FROM python:3.12-slim

WORKDIR /app

# Evitar venvs implícitos
ENV VIRTUAL_ENV=""
ENV PYTHONUNBUFFERED=1

# Copiamos requirements
COPY requirements.txt .
COPY requirements_pro.txt .

# Instalamos TODO en el python del sistema
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt -r requirements_pro.txt \
 && pip install --no-cache-dir uvicorn

# Copiamos el código
COPY . .

# Arranque DIRECTO (sin python -m)
CMD ["uvicorn", "main_pro:app", "--host", "0.0.0.0", "--port", "$PORT"]
