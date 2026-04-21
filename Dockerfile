# Stage 1: Build
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        cmake \
        libopenblas-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ENV CMAKE_ARGS="-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS"

COPY requirements.txt .

RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

COPY . .

# Stage 2: Production
FROM python:3.12-slim

WORKDIR /app

# Environment variables for better logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV HF_HUB_VERBOSITY=info

RUN apt-get update && apt-get install -y --no-install-recommends \
        libopenblas0 \
        libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /bin/bash appuser

COPY --from=builder --chown=appuser:appuser /install /usr/local
COPY --from=builder --chown=appuser:appuser /app /app

ENV HOME=/home/appuser

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "info", "--access-log"]