# plano de implementação prática

## roteiro passo a passo

implementação gradual do sistema de banco de dados e deploy no projeto cfd pipeline.

---

## fase 1: preparação (1-2 dias)

### 1.1 setup do ambiente
```bash
# criar estrutura de pastas
mkdir -p backend/app/{models,schemas,api,core,services,tasks,utils}
mkdir -p backend/migrations backend/tests

# instalar dependências
cd backend
pip install fastapi uvicorn sqlalchemy alembic psycopg2-binary redis celery minio pydantic pydantic-settings
```

### 1.2 configuração docker
```bash
# criar docker-compose.yml básico
# testar containers postgres, redis, minio
docker-compose up -d postgres redis minio

# verificar conectividade
docker-compose ps
```

### 1.3 configuração inicial
```bash
# criar .env
# configurar alembic
# testar conexões
```

---

## fase 2: modelos e banco (2-3 dias)

### 2.1 criar modelos básicos
- [ ] Bed (leito)
- [ ] Simulation (simulação)
- [ ] BedFile (arquivos)
- [ ] User (usuário)

### 2.2 configurar migrations
```bash
# inicializar alembic
alembic init migrations

# criar primeira migration
alembic revision --autogenerate -m "initial models"

# aplicar migration
alembic upgrade head
```

### 2.3 testar modelos
```python
# criar script de teste
# inserir dados de exemplo
# verificar relacionamentos
```

---

## fase 3: api básica (2-3 dias)

### 3.1 endpoints crud
- [ ] POST /beds (criar leito)
- [ ] GET /beds (listar leitos)
- [ ] GET /beds/{id} (obter leito)
- [ ] PUT /beds/{id} (atualizar leito)
- [ ] DELETE /beds/{id} (deletar leito)

### 3.2 validação e schemas
- [ ] BedCreate, BedUpdate, Bed schemas
- [ ] validação de parâmetros
- [ ] tratamento de erros

### 3.3 testar api
```bash
# usar curl ou postman
# testar todos endpoints
# verificar validações
```

---

## fase 4: minio e arquivos (1-2 dias)

### 4.1 configuração minio
```python
# criar minio_client.py
# testar upload/download
# configurar buckets
```

### 4.2 endpoints de arquivo
- [ ] POST /beds/{id}/upload (upload arquivo)
- [ ] GET /beds/{id}/files (listar arquivos)
- [ ] GET /beds/{id}/files/{file_id} (download arquivo)
- [ ] DELETE /beds/{id}/files/{file_id} (deletar arquivo)

### 4.3 integrar com modelos
- [ ] salvar metadados no postgres
- [ ] referências para arquivos no minio
- [ ] limpeza automática

---

## fase 5: celery e tarefas (3-4 dias)

### 5.1 configuração celery
```python
# criar celery.py
# configurar broker (redis)
# testar conexão
```

### 5.2 tarefa de geração blender
- [ ] criar bed_tasks.py
- [ ] integrar com script blender existente
- [ ] upload de resultados para minio
- [ ] atualização de status no banco

### 5.3 tarefa de simulação cfd
- [ ] criar cfd_tasks.py
- [ ] integrar com openfoam
- [ ] processamento assíncrono
- [ ] salvamento de resultados

### 5.4 monitoramento de tarefas
- [ ] endpoint para status de tarefas
- [ ] websockets para updates em tempo real
- [ ] logs e debugging

---

## fase 6: integração frontend (2-3 dias)

### 6.1 atualizar frontend
- [ ] conectar com novos endpoints
- [ ] upload de arquivos
- [ ] progress bars para tarefas
- [ ] listagem de resultados

### 6.2 melhorar ux
- [ ] loading states
- [ ] error handling
- [ ] notifications
- [ ] refresh automático

---

## fase 7: deploy railway (2-3 dias)

### 7.1 preparação para deploy
```bash
# criar Dockerfile
# configurar railway.toml
# testar build local
```

### 7.2 configuração railway
```bash
# criar projeto railway
# adicionar serviços (postgres, redis)
# configurar variáveis de ambiente
```

### 7.3 deploy e testes
```bash
# deploy inicial
# configurar domínio
# testar em produção
# monitoramento
```

---

## fase 8: otimizações (1-2 dias)

### 8.1 performance
- [ ] cache com redis
- [ ] otimização de queries
- [ ] compressão de arquivos
- [ ] cdn para assets

### 8.2 monitoramento
- [ ] health checks
- [ ] métricas prometheus
- [ ] logs estruturados
- [ ] alertas

---

## cronograma sugerido

### semana 1
- **dia 1-2:** fase 1 (preparação)
- **dia 3-4:** fase 2 (modelos)
- **dia 5:** fase 3 (api básica)

### semana 2
- **dia 1-2:** fase 3 (finalizar api)
- **dia 3-4:** fase 4 (minio)
- **dia 5:** fase 5 (celery setup)

### semana 3
- **dia 1-3:** fase 5 (tarefas celery)
- **dia 4-5:** fase 6 (frontend)

### semana 4
- **dia 1-3:** fase 7 (deploy)
- **dia 4-5:** fase 8 (otimizações)

---

## comandos úteis por fase

### fase 1 - preparação
```bash
# setup inicial
mkdir -p backend/app/{models,schemas,api,core,services,tasks,utils}
cd backend
pip install -r requirements.txt
docker-compose up -d postgres redis minio
```

### fase 2 - modelos
```bash
# migrations
alembic revision --autogenerate -m "initial models"
alembic upgrade head
python -c "from app.models.bed import Bed; print('modelos ok')"
```

### fase 3 - api
```bash
# testar api
uvicorn app.main:app --reload
curl http://localhost:8000/api/v1/beds/
```

### fase 4 - minio
```bash
# testar minio
python -c "from app.core.minio_client import minio_client; print('minio ok')"
```

### fase 5 - celery
```bash
# iniciar workers
celery -A app.core.celery worker --loglevel=info
celery -A app.core.celery beat --loglevel=info
```

### fase 7 - deploy
```bash
# deploy railway
railway login
railway init
railway up
```

---

## checkpoints de validação

### checkpoint 1 (fim fase 2)
- [ ] containers rodando
- [ ] banco criado
- [ ] modelos funcionando
- [ ] migrations aplicadas

### checkpoint 2 (fim fase 3)
- [ ] api respondendo
- [ ] crud funcionando
- [ ] validações ok
- [ ] testes básicos passando

### checkpoint 3 (fim fase 5)
- [ ] minio funcionando
- [ ] celery workers ativos
- [ ] tarefas executando
- [ ] arquivos salvos

### checkpoint 4 (fim fase 7)
- [ ] deploy realizado
- [ ] produção funcionando
- [ ] domínio configurado
- [ ] monitoramento ativo

---

## troubleshooting comum

### problemas de conexão
```bash
# verificar containers
docker-compose ps
docker-compose logs postgres
docker-compose logs redis

# testar conectividade
telnet localhost 5432
telnet localhost 6379
```

### problemas celery
```bash
# verificar redis
redis-cli ping

# reiniciar workers
pkill -f celery
celery -A app.core.celery worker --loglevel=info
```

### problemas minio
```bash
# verificar bucket
mc ls local/cfd-pipeline

# testar upload
python -c "from app.core.minio_client import minio_client; minio_client.upload_file('test.txt', b'hello', 'text/plain')"
```

---

## métricas de sucesso

### desenvolvimento
- [ ] 100% dos endpoints funcionando
- [ ] 0 erros de validação
- [ ] < 2s tempo de resposta api
- [ ] 100% cobertura de testes básicos

### produção
- [ ] uptime > 99%
- [ ] tempo de deploy < 5min
- [ ] backup automático funcionando
- [ ] monitoramento ativo

---

**este plano fornece um roteiro claro e executável para implementar o sistema completo!**
