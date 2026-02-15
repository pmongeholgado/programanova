FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Copiamos requirements
COPY requirements.txt .
COPY requirements_pro.txt .

# Instalamos dependencias (uvicorn ya viene en requirements)
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt -r requirements_pro.txt

# Copiamos el código
COPY . .

# Exponemos el puerto (informativo)
EXPOSE 8000

# Puerto por defecto para Railway / Docker
ENV PORT=8000

# Arranque usando shell para que $PORT se expanda
CMD ["sh", "-c", "uvicorn main_portero:app --host 0.0.0.0 --port ${PORT}"]
