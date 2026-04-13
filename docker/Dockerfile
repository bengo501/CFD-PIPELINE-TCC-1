# imagem backend: contexto = raiz do repositório (docker build -f docker/Dockerfile ..)
# perfil blender (default): WITH_BLENDER=1
# perfil python modeling: build com --build-arg WITH_BLENDER=0 (sem blender na imagem)

FROM python:3.11-slim AS base

WORKDIR /workspace

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ARG WITH_BLENDER=1
ENV WITH_BLENDER=${WITH_BLENDER}

# openfoam (pipeline cfd no container; repo ubuntu focal como no dockerfile anterior)
RUN curl -s https://dl.openfoam.org/gpg.key | apt-key add - \
    && echo "deb http://dl.openfoam.org/ubuntu focal main" >> /etc/apt/sources.list.d/openfoam.list \
    && apt-get update \
    && apt-get install -y openfoam11-dev \
    && rm -rf /var/lib/apt/lists/*

ENV PATH="/opt/openfoam11/platforms/linux64GccDPInt32Opt/bin:${PATH}"

RUN if [ "$WITH_BLENDER" = "1" ]; then \
    wget -q https://download.blender.org/release/Blender4.0/blender-4.0.0-linux-x64.tar.xz \
    && tar -xf blender-4.0.0-linux-x64.tar.xz \
    && mv blender-4.0.0-linux-x64 /opt/blender \
    && rm blender-4.0.0-linux-x64.tar.xz; \
    fi

ENV PATH="/opt/blender:${PATH}"

ENV PYTHONPATH=/workspace

COPY backend/requirements.txt /workspace/backend/requirements.txt
RUN pip install --no-cache-dir -r /workspace/backend/requirements.txt

COPY backend /workspace/backend
COPY scripts /workspace/scripts
COPY dsl /workspace/dsl
COPY tools /workspace/tools

RUN mkdir -p /workspace/generated /workspace/output /workspace/logs

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
