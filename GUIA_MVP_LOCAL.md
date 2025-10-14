# guia: mvp local - passo a passo

## objetivo

executar o mvp (minimum viable product) completo localmente com frontend, backend e banco de dados funcionando juntos.

---

## pré-requisitos

### software necessário
- ✅ **python 3.11+** - backend
- ✅ **node.js 18+** - frontend
- ✅ **postgresql 15+** - banco de dados
- ✅ **blender 4.x** - geração 3d (opcional para testes básicos)
- ✅ **openfoam 11** - simulação cfd (opcional para testes básicos)

### verificar instalação
```bash
# verificar python
python --version

# verificar node
node --version

# verificar postgresql
psql --version

# verificar blender (opcional)
blender --version

# verificar openfoam (opcional)
# windows: wsl
wsl source /opt/openfoam11/etc/bashrc && echo $WM_PROJECT_VERSION
```

---

## configuração inicial

### 1. banco de dados postgresql

```bash
# criar banco de dados
psql -U postgres
CREATE DATABASE cfd_pipeline;
\q

# ou via script (windows)
createdb -U postgres cfd_pipeline
```

### 2. variáveis de ambiente backend

```bash
# criar arquivo .env no backend/
cd backend
copy env.example .env

# editar .env com suas configurações
# DATABASE_URL=postgresql://postgres:senha@localhost:5432/cfd_pipeline
```

### 3. instalar dependências

```bash
# backend
cd backend
pip install -r requirements.txt

# frontend
cd frontend
npm install
```

### 4. inicializar banco de dados

```bash
# criar tabelas
cd backend
python scripts/init_database.py

# ou via alembic
alembic upgrade head
```

---

## executar mvp local

### opção 1: script automático (recomendado)

```bash
# windows
iniciar-mvp.bat

# escolher opção 3 (backend + frontend)
```

### opção 2: manual

#### terminal 1 - backend
```bash
cd backend
python -m uvicorn app.main:app --reload
```

#### terminal 2 - frontend
```bash
cd frontend
npm run dev
```

---

## testar funcionalidades

### 1. verificar serviços

```bash
# backend
curl http://localhost:8000/health

# frontend
# acessar http://localhost:5173 no navegador
```

### 2. testar via swagger ui

```bash
# abrir documentação interativa
start http://localhost:8000/docs

# ou manualmente
curl http://localhost:8000/docs
```

### 3. criar leito via api

```bash
# criar leito
curl -X POST "http://localhost:8000/api/beds" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "leito_teste_mvp",
    "description": "teste do mvp local",
    "diameter": 0.025,
    "height": 0.1,
    "wall_thickness": 0.002,
    "particle_count": 100,
    "particle_diameter": 0.003,
    "particle_kind": "sphere",
    "packing_method": "rigid_body"
  }'
```

### 4. listar leitos

```bash
curl http://localhost:8000/api/beds
```

### 5. testar via frontend

1. **acessar:** http://localhost:5173
2. **criar leito:**
   - clicar em "criar leito"
   - preencher parâmetros
   - submeter formulário
3. **verificar lista:**
   - acessar "resultados"
   - conferir leito criado
4. **gerar modelo 3d:**
   - clicar em "gerar modelo"
   - aguardar processamento
   - visualizar resultado
5. **simular cfd:**
   - clicar em "simular"
   - aguardar execução
   - ver resultados

---

## fluxo completo

### 1. criar leito
```
frontend → POST /api/beds → backend → postgresql
```

### 2. gerar modelo 3d
```
frontend → POST /api/beds/{id}/generate → backend → blender → output/
```

### 3. executar simulação
```
frontend → POST /api/beds/{id}/simulate → backend → openfoam → output/
```

### 4. visualizar resultados
```
frontend → GET /api/beds/{id}/results → backend → postgresql → frontend
```

---

## estrutura de arquivos

### output/ (arquivos gerados)
```
output/
├── leito_teste_mvp/
│   ├── leito_teste_mvp.bed          # arquivo dsl
│   ├── leito_teste_mvp.bed.json     # parâmetros
│   ├── leito_teste_mvp.blend        # modelo blender
│   ├── leito_teste_mvp.gltf         # modelo 3d web
│   └── cfd/
│       ├── system/                  # configuração openfoam
│       ├── constant/                # propriedades
│       ├── 0/                       # condições iniciais
│       └── log.simpleFoam           # log simulação
```

---

## endpoints disponíveis

### beds (leitos)
- `GET /api/beds` - listar leitos
- `POST /api/beds` - criar leito
- `GET /api/beds/{id}` - obter leito
- `PUT /api/beds/{id}` - atualizar leito
- `DELETE /api/beds/{id}` - deletar leito

### wizard (pipeline completo)
- `POST /api/wizard/create` - criar via wizard
- `POST /api/wizard/generate` - gerar modelo
- `POST /api/wizard/simulate` - executar simulação

### cfd (simulações)
- `GET /api/simulations` - listar simulações
- `POST /api/simulations` - criar simulação
- `GET /api/simulations/{id}` - obter simulação
- `GET /api/simulations/{id}/results` - resultados

### casos (casos openfoam)
- `GET /api/casos` - listar casos
- `GET /api/casos/{name}` - obter caso
- `GET /api/casos/{name}/files` - arquivos do caso

### utilidades
- `GET /` - informações da api
- `GET /health` - health check
- `GET /docs` - documentação swagger
- `GET /files/{path}` - arquivos estáticos

---

## debugging

### backend não inicia
```bash
# verificar dependências
pip list | grep fastapi

# reinstalar
pip install -r requirements.txt --force-reinstall

# verificar porta
netstat -ano | findstr :8000
```

### frontend não inicia
```bash
# limpar cache
npm cache clean --force

# reinstalar
rm -rf node_modules package-lock.json
npm install

# verificar porta
netstat -ano | findstr :5173
```

### banco não conecta
```bash
# verificar serviço postgresql
services.msc

# testar conexão
psql -U postgres -h localhost -d cfd_pipeline

# verificar .env
cat backend/.env | grep DATABASE_URL
```

### cors bloqueado
```bash
# verificar configuração cors no backend/app/main.py
# deve incluir http://localhost:5173
```

---

## logs e monitoramento

### ver logs backend
```bash
# terminal onde backend está rodando
# logs aparecem automaticamente

# ou redirecionar para arquivo
python -m uvicorn app.main:app --reload > backend.log 2>&1
```

### ver logs frontend
```bash
# terminal onde frontend está rodando
# logs aparecem automaticamente

# ou abrir console do navegador (F12)
```

### monitorar banco de dados
```bash
# conectar ao banco
psql -U postgres -d cfd_pipeline

# listar tabelas
\dt

# ver leitos
SELECT id, name, diameter, height FROM beds;

# ver simulações
SELECT id, name, status FROM simulations;
```

---

## performance e otimização

### backend
- usar `--workers 4` para múltiplos workers
- habilitar cache com redis (futuro)
- otimizar queries do banco

### frontend
- build de produção: `npm run build`
- usar lazy loading para rotas
- otimizar assets (imagens, modelos 3d)

### banco de dados
- criar índices para queries frequentes
- vacuum regular: `VACUUM ANALYZE;`
- configurar connection pooling

---

## próximos passos

### após mvp funcionar
1. **adicionar testes** - pytest para backend, vitest para frontend
2. **melhorar ux** - loading states, mensagens de erro
3. **implementar cache** - redis para performance
4. **adicionar filas** - celery para tarefas assíncronas
5. **preparar deploy** - docker, cloud

### features adicionais
1. autenticação e autorização
2. histórico de alterações
3. comparação de resultados
4. exportação de relatórios
5. templates pré-definidos

---

## checklist final

### antes de considerar mvp pronto
- [ ] backend rodando sem erros
- [ ] frontend rodando sem erros
- [ ] banco de dados conectado
- [ ] criar leito via frontend funciona
- [ ] leito aparece na lista
- [ ] gerar modelo 3d funciona
- [ ] arquivos salvos em output/
- [ ] visualização 3d funciona
- [ ] executar simulação funciona (se openfoam instalado)
- [ ] resultados aparecem no frontend

---

**o mvp está pronto quando você conseguir:**
1. criar um leito via interface web
2. gerar o modelo 3d do leito
3. visualizar o modelo 3d no navegador
4. executar uma simulação cfd (opcional)
5. ver os resultados da simulação

**tempo estimado:** 30 minutos de setup + testes

**resultado:** aplicação web completa rodando localmente! 🎯✨
