FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema para MySQL
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar TODO el proyecto
COPY . .

# Crear carpeta static si no existe
RUN mkdir -p static

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]