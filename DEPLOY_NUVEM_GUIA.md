# guia: deploy completo na nuvem

## visão geral

deploy completo da aplicação cfd pipeline na nuvem usando railway, incluindo aplicação web, blender e openfoam rodando juntos.

---

## arquitetura na nuvem

### componentes na nuvem

```
┌─────────────────────────────────────────────────────────┐
│                    RAILWAY CLOUD                       │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │   FRONTEND  │  │   BACKEND   │  │   CELERY        │ │
│  │   (React)   │  │  (FastAPI)  │  │   WORKERS       │ │
│  │             │  │             │  │   (Blender +    │ │
│  │             │  │             │  │    OpenFOAM)    │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  POSTGRES   │  │    REDIS    │  │     MINIO       │ │
│  │  (Dados)    │  │  (Cache +   │  │   (Arquivos)    │ │
│  │             │  │   Queue)    │  │                 │ │
│  └─────────────┘  └─────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### fluxo de dados na nuvem

1. **usuário acessa** → frontend react (railway)
2. **frontend chama** → backend fastapi (railway)
3. **backend salva** → postgresql (railway)
4. **backend dispara** → celery worker (railway)
5. **celery executa** → blender/openfoam (railway)
6. **resultados salvos** → minio (railway)
7. **usuário visualiza** → resultados via frontend

---

## configuração railway

### 1. instalação railway cli

```bash
# instalar railway cli
npm install -g @railway/cli

# ou usando curl
curl -fsSL https://railway.app/install.sh | sh

# verificar instalação
railway --version
```

### 2. login e setup

```bash
# fazer login
railway login

# criar projeto
railway init

# nome do projeto: cfd-pipeline
```

### 3. adicionar serviços

```bash
# adicionar postgresql
railway add postgresql

# adicionar redis
railway add redis

# adicionar minio (serviço customizado)
railway add --service minio
```

### 4. configurar variáveis de ambiente

```bash
# configurar variáveis do banco
railway variables set DATABASE_URL=${{Postgres.DATABASE_URL}}

# configurar redis
railway variables set REDIS_URL=${{Redis.REDIS_URL}}
railway variables set CELERY_BROKER_URL=${{Redis.REDIS_URL}}
railway variables set CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}

# configurar minio
railway variables set MINIO_ENDPOINT=minio:9000
railway variables set MINIO_ACCESS_KEY=minioadmin
railway variables set MINIO_SECRET_KEY=minioadmin123

# configurar frontend
railway variables set VITE_API_URL=${{RAILWAY_PUBLIC_DOMAIN}}

# configurar segurança
railway variables set SECRET_KEY=your-super-secret-key-here
railway variables set ALGORITHM=HS256
```

---

## docker-compose para produção

### docker-compose.prod.yml

```yaml
version: '3.8'

services:
  # banco postgresql (gerenciado pelo railway)
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

  # redis (gerenciado pelo railway)
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

  # minio (gerenciado pelo railway)
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

  # celery worker (blender + openfoam)
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

  # celery beat (tarefas agendadas)
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

## railway.toml

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

---

## dockerfile otimizado para produção

### Dockerfile (backend)

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
```

### Dockerfile.frontend

```dockerfile
FROM node:18-alpine

WORKDIR /app

# copiar package files
COPY frontend/package*.json ./

# instalar dependências
RUN npm ci --only=production

# copiar código
COPY frontend/ .

# build para produção
RUN npm run build

# comando padrão
CMD ["npm", "run", "preview"]
```

---

## comandos de deploy

### 1. deploy inicial

```bash
# fazer login no railway
railway login

# criar projeto
railway init

# adicionar serviços
railway add postgresql
railway add redis
railway add --service minio

# configurar variáveis
railway variables set DATABASE_URL=${{Postgres.DATABASE_URL}}
railway variables set REDIS_URL=${{Redis.REDIS_URL}}
railway variables set MINIO_ENDPOINT=minio:9000
railway variables set MINIO_ACCESS_KEY=minioadmin
railway variables set MINIO_SECRET_KEY=minioadmin123
railway variables set CELERY_BROKER_URL=${{Redis.REDIS_URL}}
railway variables set CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}
railway variables set VITE_API_URL=${{RAILWAY_PUBLIC_DOMAIN}}

# fazer deploy
railway up
```

### 2. deploy contínuo

```bash
# conectar repositório github
railway connect

# deploy automático a cada push
git add .
git commit -m "deploy para produção"
git push origin main
```

### 3. monitoramento

```bash
# ver logs
railway logs

# ver status dos serviços
railway status

# conectar ao banco
railway connect postgresql

# ver métricas
railway metrics
```

---

## teste da aplicação na nuvem

### 1. verificar serviços

```bash
# verificar se todos os serviços estão rodando
railway status

# ver logs de todos os serviços
railway logs -f
```

### 2. testar endpoints

```bash
# testar health check
curl https://seu-dominio.railway.app/health

# testar api
curl https://seu-dominio.railway.app/api/v1/beds/

# testar frontend
# acessar: https://seu-dominio.railway.app
```

### 3. testar funcionalidades

```bash
# criar leito via api
curl -X POST "https://seu-dominio.railway.app/api/v1/beds/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "leito_teste_nuvem",
    "diameter": 0.025,
    "height": 0.1,
    "particle_diameter": 0.003,
    "particle_count": 100,
    "particle_shape": "sphere"
  }'

# gerar modelo 3d
curl -X POST "https://seu-dominio.railway.app/api/v1/beds/1/generate"

# verificar status da tarefa
curl "https://seu-dominio.railway.app/api/v1/beds/task/{task_id}"
```

---

## benefícios do deploy na nuvem

### para o usuário final
- **acesso global:** aplicação disponível 24/7 de qualquer lugar
- **sem instalação:** funciona diretamente no navegador
- **performance:** recursos escaláveis conforme necessidade
- **backup automático:** dados seguros e redundantes

### para desenvolvimento
- **deploy automático:** git push → deploy automático
- **monitoramento:** logs e métricas em tempo real
- **escalabilidade:** mais recursos quando necessário
- **manutenção:** atualizações automáticas e rollback fácil

### para o projeto
- **profissionalismo:** aplicação em produção
- **demonstração:** fácil de mostrar para orientador/banca
- **colaboração:** equipe pode acessar e testar
- **portfólio:** projeto real em funcionamento

---

## custos estimados

### railway (por mês)
- **hobby plan:** $5/mês
  - 512mb ram
  - 1gb storage
  - domínio personalizado
  - postgresql + redis incluídos

- **pro plan:** $20/mês
  - 8gb ram
  - 100gb storage
  - domínio personalizado
  - todos os serviços incluídos

### alternativas gratuitas
- **render.com:** plano gratuito com limitações
- **fly.io:** créditos gratuitos
- **heroku:** plano gratuito removido
- **vercel + railway:** frontend na vercel, backend no railway

---

## próximos passos

1. **testar localmente** com docker-compose
2. **configurar railway** e serviços
3. **fazer deploy inicial** e testar
4. **configurar domínio** personalizado
5. **implementar monitoramento** e alertas
6. **otimizar performance** e custos

---

## troubleshooting comum

### problemas de deploy
```bash
# ver logs detalhados
railway logs --tail 100

# verificar variáveis
railway variables

# rebuild completo
railway up --detach
```

### problemas de performance
```bash
# verificar recursos
railway metrics

# escalar serviços
railway scale backend=2
```

### problemas de banco
```bash
# conectar ao banco
railway connect postgresql

# verificar tabelas
\dt

# verificar dados
SELECT * FROM beds LIMIT 5;
```

---

**com esta configuração, toda a aplicação (web + blender + openfoam) rodará na nuvem de forma profissional!** 🚀✨

**a aplicação ficará disponível 24/7 para qualquer usuário acessar via navegador, sem necessidade de instalação local!**
