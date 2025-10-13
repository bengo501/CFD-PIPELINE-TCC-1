# guia: docker-compose e deploy na nuvem

## visão geral

implementação completa de docker-compose para desenvolvimento local e deploy na nuvem com railway, incluindo aplicação web, blender e openfoam.

---

## estrutura do projeto

### onde colocar os arquivos

```
CFD-PIPELINE-TCC-1/
├── docker-compose.yml          # ← aqui (raiz do projeto)
├── docker-compose.prod.yml     # ← aqui (produção)
├── Dockerfile                  # ← aqui (backend)
├── Dockerfile.frontend         # ← aqui (frontend)
├── .env.example               # ← aqui (variáveis)
├── .env                       # ← aqui (local, não commit)
├── backend/
│   ├── app/
│   └── requirements.txt
├── frontend/
│   ├── src/
│   └── package.json
└── scripts/
    ├── blender_scripts/
    └── openfoam_scripts/
```

---

## docker-compose.yml (desenvolvimento)

```yaml
version: '3.8'

services:
  # banco de dados postgresql
  postgres:
    image: postgres:15
    container_name: cfd_postgres
    environment:
      POSTGRES_DB: cfd_pipeline
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # redis para cache e celery
  redis:
    image: redis:7-alpine
    container_name: cfd_redis
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # minio para armazenamento de arquivos
  minio:
    image: minio/minio
    container_name: cfd_minio
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin123
    ports:
      - "9000:9000"
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  # backend fastapi
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: cfd_backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres123@postgres:5432/cfd_pipeline
      REDIS_URL: redis://redis:6379
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin123
      CELERY_BROKER_URL: redis://redis:6379
      CELERY_RESULT_BACKEND: redis://redis:6379
    volumes:
      - ./backend:/app
      - ./scripts:/app/scripts
      - ./output:/app/output
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      minio:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # frontend react
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: cfd_frontend
    ports:
      - "5173:5173"
    environment:
      VITE_API_URL: http://localhost:8000
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    command: npm run dev

  # celery worker para tarefas assíncronas
  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: cfd_celery_worker
    environment:
      DATABASE_URL: postgresql://postgres:postgres123@postgres:5432/cfd_pipeline
      REDIS_URL: redis://redis:6379
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin123
      CELERY_BROKER_URL: redis://redis:6379
      CELERY_RESULT_BACKEND: redis://redis:6379
    volumes:
      - ./backend:/app
      - ./scripts:/app/scripts
      - ./output:/app/output
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: celery -A app.core.celery worker --loglevel=info --concurrency=2

  # celery beat para tarefas agendadas
  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: cfd_celery_beat
    environment:
      DATABASE_URL: postgresql://postgres:postgres123@postgres:5432/cfd_pipeline
      REDIS_URL: redis://redis:6379
      CELERY_BROKER_URL: redis://redis:6379
      CELERY_RESULT_BACKEND: redis://redis:6379
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: celery -A app.core.celery beat --loglevel=info

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

---

## docker-compose.prod.yml (produção)

```yaml
version: '3.8'

services:
  # banco postgresql gerenciado
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: cfd_pipeline
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # redis gerenciado
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # minio gerenciado
  minio:
    image: minio/minio
    environment:
      MINIO_ROOT_USER: ${MINIO_ACCESS_KEY}
      MINIO_ROOT_PASSWORD: ${MINIO_SECRET_KEY}
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

  # backend fastapi
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: ${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: ${MINIO_SECRET_KEY}
      CELERY_BROKER_URL: ${CELERY_BROKER_URL}
      CELERY_RESULT_BACKEND: ${CELERY_RESULT_BACKEND}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      minio:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000

  # frontend react
  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "5173:5173"
    environment:
      VITE_API_URL: ${VITE_API_URL}
    depends_on:
      - backend
    command: npm run build && npm run preview

  # celery worker
  celery-worker:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: ${MINIO_ACCESS_KEY}
      MINIO_SECRET_KEY: ${MINIO_SECRET_KEY}
      CELERY_BROKER_URL: ${CELERY_BROKER_URL}
      CELERY_RESULT_BACKEND: ${CELERY_RESULT_BACKEND}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: celery -A app.core.celery worker --loglevel=info --concurrency=4

  # celery beat
  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: ${DATABASE_URL}
      REDIS_URL: ${REDIS_URL}
      CELERY_BROKER_URL: ${CELERY_BROKER_URL}
      CELERY_RESULT_BACKEND: ${CELERY_RESULT_BACKEND}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    command: celery -A app.core.celery beat --loglevel=info

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

---

## Dockerfile (backend)

```dockerfile
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
```

---

## Dockerfile.frontend

```dockerfile
FROM node:18-alpine

WORKDIR /app

# copiar package files
COPY frontend/package*.json ./

# instalar dependências
RUN npm ci

# copiar código
COPY frontend/ .

# comando padrão
CMD ["npm", "run", "dev"]
```

---

## .env.example

```bash
# banco de dados
DATABASE_URL=postgresql://postgres:postgres123@localhost:5432/cfd_pipeline
POSTGRES_PASSWORD=postgres123

# redis
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379

# minio
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123

# api
API_HOST=localhost
API_PORT=8000
DEBUG=true

# frontend
VITE_API_URL=http://localhost:8000

# segurança
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## comandos para usar

### desenvolvimento local

```bash
# criar .env
cp .env.example .env

# iniciar todos os serviços
docker-compose up -d

# ver logs
docker-compose logs -f

# parar serviços
docker-compose down

# rebuild
docker-compose build --no-cache
```

### produção

```bash
# usar compose de produção
docker-compose -f docker-compose.prod.yml up -d

# com variáveis de ambiente
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d
```

---

## deploy na nuvem com railway

### 1. configuração railway

```bash
# instalar railway cli
npm install -g @railway/cli

# login
railway login

# criar projeto
railway init

# adicionar serviços
railway add postgresql
railway add redis
railway add --service minio
```

### 2. railway.toml

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "docker-compose -f docker-compose.prod.yml up -d"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"

[environments.production]
variables = { NODE_ENV = "production" }
```

### 3. variáveis de ambiente no railway

```bash
# configurar variáveis
railway variables set DATABASE_URL=${{Postgres.DATABASE_URL}}
railway variables set REDIS_URL=${{Redis.REDIS_URL}}
railway variables set MINIO_ENDPOINT=minio:9000
railway variables set MINIO_ACCESS_KEY=minioadmin
railway variables set MINIO_SECRET_KEY=minioadmin123
railway variables set CELERY_BROKER_URL=${{Redis.REDIS_URL}}
railway variables set CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}
railway variables set VITE_API_URL=${{RAILWAY_PUBLIC_DOMAIN}}
```

### 4. deploy

```bash
# deploy
railway up

# ver logs
railway logs

# conectar ao banco
railway connect postgresql
```

---

## arquitetura na nuvem

### componentes rodando na nuvem

```
┌─────────────────────────────────────────────────┐
│                  RAILWAY CLOUD                 │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   FRONTEND  │  │   BACKEND   │  │ CELERY  │ │
│  │   (React)   │  │  (FastAPI)  │  │ WORKERS │ │
│  └─────────────┘  └─────────────┘  └─────────┘ │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │  POSTGRES   │  │    REDIS    │  │  MINIO  │ │
│  │  (Dados)    │  │  (Cache)    │  │ (Files) │ │
│  └─────────────┘  └─────────────┘  └─────────┘ │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐              │
│  │   BLENDER   │  │  OPENFOAM   │              │
│  │ (3D Models) │  │ (CFD Sim)   │              │
│  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────┘
```

### fluxo na nuvem

1. **usuário acessa** → frontend (react) na nuvem
2. **frontend chama** → backend (fastapi) na nuvem
3. **backend salva** → postgresql na nuvem
4. **backend dispara** → celery worker na nuvem
5. **celery executa** → blender/openfoam na nuvem
6. **resultados salvos** → minio na nuvem
7. **usuário visualiza** → resultados via frontend

---

## benefícios do deploy na nuvem

### para o usuário
- **acesso global:** aplicação disponível 24/7
- **sem instalação:** funciona no navegador
- **performance:** recursos escaláveis
- **backup automático:** dados seguros

### para desenvolvimento
- **deploy automático:** git push → deploy
- **monitoramento:** logs e métricas
- **escalabilidade:** mais recursos quando necessário
- **manutenção:** atualizações automáticas

---

## próximos passos

1. **criar arquivos** docker-compose na raiz do projeto
2. **configurar .env** com variáveis locais
3. **testar localmente** com docker-compose
4. **configurar railway** para deploy
5. **fazer deploy** e testar na nuvem

---

**com esta configuração, toda a aplicação (web + blender + openfoam) rodará na nuvem!** 🚀✨
