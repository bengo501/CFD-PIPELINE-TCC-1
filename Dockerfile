#dockerfile para containerização do projeto TCC
#geração de Leitos de extração com Blender
FROM ubuntu:22.04
# evitar prompts interativos durante a instalação
ENV DEBIAN_FRONTEND=noninteractive
# definir diretório de trabalho
WORKDIR /app
#instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    wget \
    curl \
    unzip \
    xz-utils \
    libgl1-mesa-glx \
    libglu1-mesa \
    libxrender1 \
    libxext6 \
    libxrandr2 \
    libxinerama1 \
    libxi6 \
    libxfixes3 \
    libxcursor1 \
    libxcomposite1 \
    libxdamage1 \
    libxss1 \
    libxtst6 \
    libgconf-2-4 \
    libasound2 \
    libpulse0 \
    libdrm2 \
    libxkbcommon0 \
    libxcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-shm0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xkb1 \
    libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*
#criar usuario nao-root
RUN useradd -m -s /bin/bash blender_user
USER blender_user
# definir variaveis de ambiente
ENV HOME=/home/blender_user
ENV PATH="/home/blender_user/.local/bin:$PATH"
# Instalar Blender
RUN mkdir -p /home/blender_user/blender && \
    cd /home/blender_user/blender && \
    wget https://download.blender.org/release/Blender4.0/blender-4.0.2-linux-x64.tar.xz && \
    tar -xf blender-4.0.2-linux-x64.tar.xz && \
    rm blender-4.0.2-linux-x64.tar.xz && \
    ln -s /home/blender_user/blender/blender-4.0.2-linux-x64/blender /home/blender_user/.local/bin/blender
# copiar arquivos do projeto
COPY --chown=blender_user:blender_user . /app/
#instalar dependências Python
RUN pip3 install --user argparse pathlib
# Configurar PATH
ENV PATH="/home/blender_user/.local/bin:$PATH"
# Verificar instalação do Blender
RUN blender --version
# Executar setup automático
RUN python3 scripts/setup_project.py --no-auto-install --no-sample
# Expor porta (se necessário para interface web)
EXPOSE 8000
# Comando padrão
CMD ["python3", "scripts/leito_standalone.py", "--help"]
