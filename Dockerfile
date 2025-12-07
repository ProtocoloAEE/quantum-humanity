# AEE v8 - Dockerfile para producción
FROM python:3.9-slim
WORKDIR /app
# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gnupg \
    && rm -rf /var/lib/apt/lists/*
# Copiar requirements
COPY requirements.txt .
# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt
# Copiar código
COPY . .
# Crear usuario no-root
RUN useradd -m -u 1000 aeeuser
USER aeeuser
# Exponer puerto
EXPOSE 8000
# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]