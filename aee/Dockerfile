# AEE Protocol v2.2.0 - Dockerfile
# Motor de Certificación de Evidencia Digital con Seguridad Híbrida Post-Cuántica

FROM python:3.11-slim

# Metadatos
LABEL maintainer="Desarrollo AEE"
LABEL version="2.2.0"
LABEL description="AEE Protocol: The Quantum-Resistant Immutable Truth"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY aee/ ./aee/
COPY VERSION .

# Crear directorio para logs
RUN mkdir -p /app/logs

# Exponer puerto
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health', timeout=5)" || exit 1

# Comando por defecto
CMD ["python", "-m", "uvicorn", "aee.api.fastapi_server:app", "--host", "0.0.0.0", "--port", "8000"]

