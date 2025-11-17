# backend cfd pipeline - fastapi

api rest para gerenciar pipeline de simulações cfd de leitos empacotados.

## início rápido

### 1. instalar dependências

```bash
cd backend
pip install -r requirements.txt
```

### 2. executar servidor

```bash
# opção 1: python direto
python -m backend.app.main

# opção 2: uvicorn
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. acessar documentação

- **swagger ui:** http://localhost:8000/docs
- **redoc:** http://localhost:8000/redoc
- **api root:** http://localhost:8000

## endpoints principais

### bed compiler

```http
POST /api/bed/compile
```

compila parâmetros em arquivo `.bed` e `.bed.json`

**body:**

```json
{
  "parameters": {
    "diameter": 0.05,
    "height": 0.1,
    "particle_count": 100,
    "particle_diameter": 0.005
  }
}
```

**response:**

```json
{
  "success": true,
  "bed_file": "generated/configs/leito_20251009_091500.bed",
  "json_file": "generated/configs/leito_20251009_091500.bed.json",
  "message": "compilação bem-sucedida"
}
```

### gerar modelo 3d

```http
POST /api/model/generate
```

gera modelo 3d no blender (assíncrono)

**body:**

```json
{
  "json_file": "generated/configs/leito_20251009_091500.bed.json",
  "open_blender": false
}
```

**response:**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued",
  "message": "geração de modelo iniciada"
}
```

### criar simulação openfoam

```http
POST /api/simulation/create
```

cria caso openfoam (assíncrono)

**body:**

```json
{
  "json_file": "generated/configs/leito_20251009_091500.bed.json",
  "blend_file": "generated/3d/output/leito_20251009_091500.blend",
  "run_simulation": false
}
```

### verificar job

```http
GET /api/job/{job_id}
```

**response:**

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "job_type": "generate_model",
  "status": "completed",
  "progress": 100,
  "created_at": "2025-10-09T09:15:00",
  "updated_at": "2025-10-09T09:18:30",
  "output_files": ["generated/3d/output/leito_20251009_091500.blend"]
}
```

### listar arquivos

```http
GET /api/files/{file_type}
```

tipos: `bed`, `json`, `blend`, `stl`, `simulations`

## arquitetura

```
backend/
├── app/
│   ├── main.py              # aplicação fastapi
│   ├── api/
│   │   ├── routes.py        # endpoints
│   │   └── models.py        # modelos pydantic
│   ├── services/
│   │   ├── bed_service.py         # compilação .bed
│   │   ├── blender_service.py     # geração 3d
│   │   └── openfoam_service.py    # simulação cfd
│   └── utils/
│       └── file_manager.py        # gestão de arquivos
└── requirements.txt
```

---

## fluxo de trabalho

```
1. POST /api/bed/compile
   └─> gera .bed e .bed.json
   
2. POST /api/model/generate
   └─> job assíncrono
   └─> executa blender headless
   └─> gera .blend e .stl
   
3. GET /api/job/{job_id}
   └─> verifica progresso
   
4. POST /api/simulation/create
   └─> job assíncrono
   └─> executa setup_openfoam_case.py
   └─> cria caso openfoam
   
5. GET /api/files/simulations
   └─> lista simulações criadas
```

## testar api

### usar curl

```bash
# compilar bed
curl -X POST http://localhost:8000/api/bed/compile \
  -H "Content-Type: application/json" \
  -d '{
    "parameters": {
      "diameter": 0.05,
      "height": 0.1,
      "particle_count": 100,
      "particle_diameter": 0.005
    }
  }'

# gerar modelo
curl -X POST http://localhost:8000/api/model/generate \
  -H "Content-Type: application/json" \
  -d '{
    "json_file": "generated/configs/leito_20251009_091500.bed.json"
  }'

# verificar job
curl http://localhost:8000/api/job/{job_id}
```

### usar swagger ui

1. abrir http://localhost:8000/docs
2. expandir endpoint
3. clicar "try it out"
4. preencher body
5. executar

## configuração

### cors

por padrão, permite acesso de:

- http://localhost:3000 (react cra)
- http://localhost:5173 (vite)

editar em `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["seu-dominio.com"],
    ...
)
```

### porta

alterar em `main.py`:

```python
uvicorn.run(..., port=8000)
```

ou via comando:

```bash
uvicorn backend.app.main:app --port 3001
```

## monitoramento

### status do sistema

```http
GET /api/status
```

retorna:

- status da api
- disponibilidade dos serviços
- estatísticas de jobs

### health check

```http
GET /health
```

---

## troubleshooting

### erro: "module 'backend' has no attribute 'app'"

executar do diretório raiz do projeto:

```bash
python -m backend.app.main
```

### erro: "blender not found"

editar `blender_service.py` e adicionar caminho:

```python
self.blender_exe = r"C:\caminho\para\blender.exe"
```

### erro: "compilation failed"

verificar:

1. antlr está instalado
2. arquivos em `dsl/generated/` existem
3. executar `python dsl/setup_antlr.py`

## containerização (futuro)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# build
docker build -t cfd-backend .

# run
docker run -p 8000:8000 -v $(pwd)/output:/app/output cfd-backend
```

## desenvolvimento

### adicionar novo endpoint

1. criar função em `routes.py`
2. definir models em `models.py`
3. implementar lógica em `services/`

### adicionar novo serviço

1. criar arquivo em `services/`
2. implementar classe com métodos assíncronos
3. importar em `routes.py`

## próximos passos

- [ ] adicionar autenticação (jwt)
- [ ] persistência de jobs (database)
- [ ] websockets para progresso em tempo real
- [ ] cache de resultados (redis)
- [ ] rate limiting
- [ ] logging estruturado
- [ ] testes unitários
