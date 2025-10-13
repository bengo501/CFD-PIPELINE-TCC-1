FROM python:3.11-slim

WORKDIR /app

# instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    wget \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# instalar openfoam
RUN curl -s https://dl.openfoam.org/gpg.key | apt-key add - \
    && echo "deb http://dl.openfoam.org/ubuntu focal main" >> /etc/apt/sources.list.d/openfoam.list \
    && apt-get update \
    && apt-get install -y openfoam11-dev

# instalar blender
RUN wget https://download.blender.org/release/Blender4.0/blender-4.0.0-linux-x64.tar.xz \
    && tar -xf blender-4.0.0-linux-x64.tar.xz \
    && mv blender-4.0.0-linux-x64 /opt/blender \
    && rm blender-4.0.0-linux-x64.tar.xz

# adicionar ao path
ENV PATH="/opt/blender:${PATH}"
ENV PATH="/opt/openfoam11/platforms/linux64GccDPInt32Opt/bin:${PATH}"

# copiar requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar código
COPY backend/ .
COPY scripts/ ./scripts/

# criar diretórios
RUN mkdir -p output logs

# comando padrão
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]