# =========================================================
# Stage 1: Builder
# =========================================================
FROM nvidia/cuda:12.4.1-devel-ubuntu22.04 AS builder

WORKDIR /app
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    build-essential cmake git gcc g++ \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN python3 -m pip install --upgrade pip setuptools wheel scikit-build-core

# CUDA build configuration for GTX 1650 with VLM support
ENV FORCE_CMAKE=1
ENV CUDA_HOME="/usr/local/cuda"
ENV PATH="${CUDA_HOME}/bin:${PATH}"

# Critical flags:
# - GGML_CUDA=ON: Enable CUDA backend
# - CMAKE_CUDA_ARCHITECTURES=75: GTX 1650 compute capability
# - LLAVA_BUILD=ON: Enable VLM/MTMD support
# - GGML_CUDA_FORCE_VMM=OFF: Disable VMM (causes cuMemCreate errors)
# - CMAKE_*_LINKER_FLAGS=-lcuda: Explicitly link against libcuda stub
ENV CMAKE_ARGS="\
-DGGML_CUDA=ON \
-DCMAKE_CUDA_ARCHITECTURES=75 \
-DLLAVA_BUILD=ON \
-DGGML_CUDA_FORCE_VMM=OFF \
-DCMAKE_EXE_LINKER_FLAGS=-lcuda \
-DCMAKE_SHARED_LINKER_FLAGS=-lcuda"

# Point linker to CUDA stubs (needed for no-GPU build machine)
ENV LDFLAGS="-L/usr/local/cuda/lib64/stubs"
ENV LD_LIBRARY_PATH="/usr/local/cuda/lib64/stubs:${LD_LIBRARY_PATH}"

COPY requirements.txt .

RUN CMAKE_BUILD_PARALLEL_LEVEL=8 \
    pip install --no-cache-dir --no-build-isolation -r requirements.txt

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

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# At runtime, the real libcuda.so comes from NVIDIA container runtime
# when you run with --gpus all
ENV LD_LIBRARY_PATH="/opt/venv/lib/python3.10/site-packages/llama_cpp:/usr/local/cuda/lib64:${LD_LIBRARY_PATH}"

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