FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema necesarias para mysqlclient y otras librerías
RUN apt-get update && apt-get install -y \
    pkg-config \
    default-libmysqlclient-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar TODO el código de la aplicación
COPY . .

# Exponer puerto
EXPOSE 8000

# El comando se define en docker-compose
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]