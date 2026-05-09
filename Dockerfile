# =========================================================
# Stage 1: Builder
# =========================================================
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04 AS builder

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    build-essential \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Create venv
RUN python3 -m venv /opt/venv

# Activate venv path
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip
RUN python3 -m pip install --upgrade pip

COPY requirements.txt .

# Install dependencies INTO the venv
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# =========================================================
# Stage 2: Production
# =========================================================
FROM nvidia/cuda:12.4.1-runtime-ubuntu22.04

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy venv
COPY --from=builder /opt/venv /opt/venv

# Use venv
ENV PATH="/opt/venv/bin:$PATH"

# Python env vars
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV HF_HUB_VERBOSITY=info

RUN useradd --create-home --shell /bin/bash appuser

COPY --from=builder --chown=appuser:appuser /app /app

ENV HOME=/home/appuser

USER appuser

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]