FROM python:3.12-slim

WORKDIR /app

# Instalar y actualidar las dependencias del sistema
RUN apt-get update && apt-get install -y gcc curl wget && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install --no-cache-dir poetry==2.1.1

# Copiar archivos de dependencias Poetry
COPY pyproject.toml poetry.lock ./

# Instalar dependencias sin el proyecto raíz
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

# Instalar Chromium para Playwright ✅
RUN python -m playwright install chromium --with-deps

# Copiar el resto del proyecto
COPY . .

ENV PYTHONPATH=/app

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]