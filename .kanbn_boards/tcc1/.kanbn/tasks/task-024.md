---
name: containerização docker e orquestração
tags:
  - docker
  - devops
  - infraestrutura
created: 2025-10-09
assigned: 
sprint: mes 7 sem 3-4 + mes 8 sem 1
atividades-tcc: a23, a24
story-points: 13
---

# containerização docker e orquestração

containerizar todo o sistema com docker e docker-compose.

## tarefas

### dockerfiles
- [ ] `docker/Dockerfile.backend`
- [ ] `docker/Dockerfile.frontend`
- [ ] `docker/Dockerfile.blender`
- [ ] `docker/Dockerfile.openfoam`
- [ ] otimizar imagens (multi-stage builds)
- [ ] reduzir tamanho das imagens

### docker-compose
- [ ] criar `docker-compose.yml`
- [ ] serviço backend (fastapi)
- [ ] serviço frontend (nginx)
- [ ] serviço blender (headless)
- [ ] serviço openfoam (wsl/linux)
- [ ] serviço postgresql
- [ ] serviço redis
- [ ] networks isoladas
- [ ] volumes persistentes

### redis para jobs
- [ ] instalar redis
- [ ] configurar celery/rq
- [ ] job queue distribuída
- [ ] workers assíncronos
- [ ] monitoramento de filas

### configuração
- [ ] variáveis de ambiente (.env)
- [ ] secrets management
- [ ] health checks
- [ ] restart policies
- [ ] resource limits (cpu, memory)

### scripts auxiliares
- [ ] `docker/build.sh`
- [ ] `docker/start.sh`
- [ ] `docker/stop.sh`
- [ ] `docker/logs.sh`
- [ ] `docker/clean.sh`

### testes
- [ ] build de todas as imagens
- [ ] start do sistema completo
- [ ] teste end-to-end
- [ ] teste de volumes
- [ ] teste de networking

## estrutura de arquivos

```
docker/
├── Dockerfile.backend
├── Dockerfile.frontend
├── Dockerfile.blender
├── Dockerfile.openfoam
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── .env.example
├── build.sh
├── start.sh
└── README.md
```

## docker-compose.yml exemplo

```yaml
version: '3.8'

services:
  backend:
    build: 
      context: .
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./output:/app/output
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/cfd
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  blender:
    build:
      context: .
      dockerfile: docker/Dockerfile.blender
    volumes:
      - ./output:/app/output
    environment:
      - DISPLAY=:99

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=cfd_pipeline
      - POSTGRES_USER=cfd_user
      - POSTGRES_PASSWORD=cfd_pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## deploy em nuvem (futuro)
- [ ] preparar para aws/azure/gcp
- [ ] kubernetes configs (opcional)
- [ ] ci/cd pipeline
- [ ] monitoramento (prometheus/grafana)

## prioridade
alta - essencial para produção

## estimativa
3-5 dias (13 story points)

## critérios de aceitação
- [ ] 4 dockerfiles criados
- [ ] docker-compose funcional
- [ ] redis integrado
- [ ] celery/rq para jobs
- [ ] postgresql containerizado
- [ ] volumes persistentes
- [ ] sistema completo sobe com 1 comando
- [ ] documentação completa
- [ ] scripts auxiliares
- [ ] testes passando

