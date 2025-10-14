# guia completo: deploy na nuvem com containers

## visão geral

documentação detalhada para fazer deploy do projeto cfd pipeline na nuvem usando docker containers e railway.

---

## 📚 índice de etapas

### [etapa 1: introdução ao deploy](01_INTRODUCAO_DEPLOY.md)
**o que é:** conceitos, arquitetura e visão geral

**conteúdo:**
- o que é deploy na nuvem
- por que usar containers (docker)
- arquitetura na nuvem
- componentes containerizados
- fluxo de deploy
- plataformas disponíveis
- custos estimados

**tempo:** 20 minutos de leitura

---

### [etapa 2: preparar código](02_PREPARAR_CODIGO.md)
**o que é:** ajustar código para deploy

**conteúdo:**
- configurar variáveis de ambiente
- ajustar caminhos de arquivo
- remover secrets do código
- verificar dependências
- criar .dockerignore
- configurar cors
- health check endpoint

**tempo:** 1-2 horas

**comandos principais:**
```bash
# criar env.example
cp .env .env.example

# testar com variáveis
python -c "from app.core.config import settings; print(settings)"
```

---

### etapa 3: criar dockerfiles ⚙️

**o que é:** containerizar aplicação

**conteúdo:**
- dockerfile backend (python + blender + openfoam)
- dockerfile frontend (node + react)
- docker-compose local
- docker-compose produção
- build e test

**tempo:** 2-3 horas

**arquivos:**
- `Dockerfile` - backend
- `Dockerfile.frontend` - frontend
- `docker-compose.yml` - local
- `docker-compose.prod.yml` - produção

---

### etapa 4: testar containers ✅

**o que é:** validar containers localmente

**conteúdo:**
- build containers
- executar docker-compose
- testar serviços
- verificar logs
- validar volumes
- troubleshooting

**tempo:** 30-60 minutos

**comandos:**
```bash
# build
docker-compose build

# executar
docker-compose up -d

# logs
docker-compose logs -f

# parar
docker-compose down
```

---

### etapa 5: configurar railway 🚂

**o que é:** setup plataforma cloud

**conteúdo:**
- criar conta railway
- criar projeto
- adicionar serviços (postgres, redis)
- configurar variáveis
- conectar github
- configurar domínio

**tempo:** 30-45 minutos

**passos:**
1. railway.app → sign up
2. new project
3. add database → postgresql
4. add database → redis
5. add service → github repo

---

### etapa 6: fazer deploy 🚀

**o que é:** subir para produção

**conteúdo:**
- git push
- railway auto-deploy
- monitorar build
- verificar logs
- acessar aplicação
- troubleshooting deploy

**tempo:** 15-30 minutos

**comandos:**
```bash
# commit changes
git add .
git commit -m "deploy to railway"

# push para trigger deploy
git push origin main

# ou usar railway cli
railway up
```

---

### etapa 7: validar e monitorar 📊

**o que é:** garantir funcionamento

**conteúdo:**
- testar aplicação online
- verificar funcionalidades
- monitorar logs
- configurar alertas
- backup banco de dados
- manutenção contínua

**tempo:** 30 minutos

**urls:**
- aplicação: https://seu-projeto.railway.app
- logs: railway dashboard
- métricas: railway metrics

---

## 🎯 quick start (experiente)

### setup completo:

```bash
# 1. preparar código (etapa 2)
cd backend
cp env.example .env
pip freeze > requirements.txt

# 2. criar dockerfiles (etapa 3)
# criar Dockerfile na raiz
# criar Dockerfile.frontend na raiz
# criar docker-compose.yml

# 3. testar local (etapa 4)
docker-compose build
docker-compose up -d
docker-compose logs -f

# 4. configurar railway (etapa 5)
railway login
railway init
railway add postgresql
railway add redis

# 5. deploy (etapa 6)
git add .
git commit -m "deploy"
git push

# railway auto-deploys!
```

---

## 📋 dockerfile resumido

### backend (Dockerfile):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# instalar dependências sistema
RUN apt-get update && apt-get install -y \
    gcc g++ libpq-dev curl wget blender

# instalar openfoam
RUN curl -s https://dl.openfoam.org/gpg.key | apt-key add - \
    && apt-get install -y openfoam11-dev

# copiar e instalar requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar código
COPY backend/ .
COPY scripts/ ./scripts/

# expor porta
EXPOSE 8000

# comando
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

### frontend (Dockerfile.frontend):
```dockerfile
FROM node:18-alpine

WORKDIR /app

# copiar package files
COPY frontend/package*.json ./

# instalar deps
RUN npm ci --only=production

# copiar código
COPY frontend/ .

# build
RUN npm run build

# expor porta
EXPOSE 5173

# comando
CMD ["npm", "run", "preview"]
```

---

## 🐳 docker-compose resumido

### local (docker-compose.yml):
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: cfd_pipeline
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres123@postgres:5432/cfd_pipeline
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    ports:
      - "5173:5173"
    environment:
      VITE_API_URL: http://localhost:8000
    depends_on:
      - backend

volumes:
  postgres_data:
```

---

## 🚂 railway setup resumido

### comandos railway cli:

```bash
# instalar
npm install -g @railway/cli

# login
railway login

# criar projeto
railway init

# adicionar postgres
railway add postgresql

# adicionar redis
railway add redis

# configurar variáveis
railway variables set DATABASE_URL=${{Postgres.DATABASE_URL}}
railway variables set REDIS_URL=${{Redis.REDIS_URL}}

# deploy
railway up
```

---

## ⏱️ tempo estimado total

### primeira vez (deploy completo):
- ler documentação: 30 min
- preparar código: 1-2h
- criar dockerfiles: 2-3h
- testar containers: 30-60 min
- configurar railway: 30-45 min
- fazer deploy: 15-30 min
- validar: 30 min
- **total:** 6-8 horas

### deploys subsequentes:
```bash
git add .
git commit -m "update"
git push
# auto-deploy: 2-5 min
```

---

## 💰 custos mensais

### railway (recomendado):

**hobby ($5/mês):**
- 512mb ram
- 1gb storage
- ❌ não suficiente (blender + openfoam pesados)

**pro ($20/mês):**
- 8gb ram
- 100gb storage
- ✅ adequado
- postgresql incluído
- redis incluído

---

## ✅ checklist completo

### pré-deploy:
- [ ] mvp local funcionando
- [ ] código com variáveis ambiente
- [ ] secrets removidos do código
- [ ] dockerfiles criados
- [ ] docker-compose testado localmente

### deploy:
- [ ] conta railway criada
- [ ] projeto railway configurado
- [ ] serviços adicionados (postgres, redis)
- [ ] variáveis configuradas
- [ ] github conectado

### pós-deploy:
- [ ] aplicação acessível online
- [ ] funcionalidades testadas
- [ ] logs monitorados
- [ ] backup configurado
- [ ] domínio customizado (opcional)

---

## 🎯 resultado esperado

### aplicação online:
- ✅ url: https://seu-projeto.railway.app
- ✅ frontend react acessível
- ✅ backend api respondendo
- ✅ banco postgresql gerenciado
- ✅ redis funcionando

### funcionalidades na nuvem:
- ✅ criar leitos via web
- ✅ gerar modelos 3d (blender na nuvem)
- ✅ executar simulações cfd (openfoam na nuvem)
- ✅ visualizar resultados 3d
- ✅ download de arquivos

### benefícios:
- ✅ acesso global (24/7)
- ✅ deploy automático (git push)
- ✅ escalável
- ✅ profissional para tcc/portfólio

---

## 🔧 arquivos importantes

### na raiz do projeto:
```
CFD-PIPELINE-TCC-1/
├── Dockerfile              # backend + celery
├── Dockerfile.frontend     # frontend
├── docker-compose.yml      # dev local
├── docker-compose.prod.yml # produção
├── railway.toml           # config railway
├── .dockerignore          # ignorar no build
└── env.example            # template vars
```

---

## 📊 fluxo de trabalho

### desenvolvimento:
```
código local → testar mvp → git commit
```

### deploy:
```
git push → railway detecta → build docker → deploy → online!
```

### atualização:
```
modificar código → git push → auto-deploy
```

---

## 🚨 troubleshooting comum

### build falha:
```bash
# ver logs railway
railway logs --deployment

# testar local
docker-compose build
```

### aplicação não inicia:
```bash
# verificar variáveis
railway variables

# verificar health
curl https://seu-projeto.railway.app/health
```

### database error:
```bash
# verificar conexão
railway variables get DATABASE_URL

# conectar ao banco
railway connect postgresql
```

---

## 📚 recursos adicionais

### documentação:
- docker: https://docs.docker.com/
- railway: https://docs.railway.app/
- docker-compose: https://docs.docker.com/compose/

### tutoriais:
- railway quickstart: https://docs.railway.app/getting-started
- dockerfile best practices: https://docs.docker.com/develop/dev-best-practices/
- docker-compose tutorial: https://docs.docker.com/compose/gettingstarted/

---

## 🎓 próximos passos

### após deploy básico:
1. adicionar ci/cd (github actions)
2. implementar monitoramento (sentry, datadog)
3. configurar domínio customizado
4. implementar cdn para assets
5. adicionar testes automatizados
6. configurar staging environment

---

## 🚀 começar agora

**pronto para fazer deploy?**

1. **ler etapa 1:** [01_INTRODUCAO_DEPLOY.md](01_INTRODUCAO_DEPLOY.md)
2. **preparar código:** [02_PREPARAR_CODIGO.md](02_PREPARAR_CODIGO.md)
3. **criar dockerfiles:** etapa 3
4. **deploy!** etapas 4-7

---

**boa sorte com o deploy! 🎉☁️**
