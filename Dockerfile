# 1. Imagen base ligera pero con soporte para Python
FROM python:3.10-slim

# 2. Instalamos herramientas de compilación esenciales
# Esto es VITAL para que el motor de la IA (llama-cpp) pueda 'rugir'
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Copiamos las dependencias
# Nota: Usamos rutas relativas al comando de ejecución (el root del proyecto)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiamos toda la estructura de OORAV
COPY . .

# 6. Creamos la carpeta de la base de datos si no existe
RUN mkdir -p /app/memory/chroma_db

# 7. Exponemos el puerto de nuestra API de elite
EXPOSE 8000

# 8. Comando para arrancar el cerebro
CMD ["python", "api/main.py"]