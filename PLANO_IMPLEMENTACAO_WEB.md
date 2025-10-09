# plano de implementação frontend + backend

implementação simples e incremental para conectar interface web com pipeline cfd.

---

## 🎯 objetivo

criar interface web que:
1. permite criar arquivos `.bed` visualmente
2. compila via backend
3. gera modelo 3d no blender
4. executa simulação openfoam
5. exibe resultados

**foco:** funcional e simples primeiro, refinamento depois

---

## 🏗️ arquitetura proposta

```
┌─────────────────────────────────────────────────────────────┐
│ FRONTEND (React)                                            │
│ http://localhost:3000                                       │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Formulário   │  │ Visualização │  │ Resultados   │     │
│  │ Parâmetros   │  │ 3D (Three.js)│  │ (Plotly)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────┬────────────────────────────────────────────────┘
             │ HTTP/REST
             │
┌────────────▼────────────────────────────────────────────────┐
│ BACKEND (FastAPI)                                           │
│ http://localhost:8000                                       │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ API Routes   │  │ Job Queue    │  │ File Storage │     │
│  │ /bed/compile │  │ (tasks)      │  │ (output/)    │     │
│  │ /model/gen   │  └──────────────┘  └──────────────┘     │
│  │ /sim/run     │                                          │
│  └──────────────┘                                          │
└────────────┬────────────────────────────────────────────────┘
             │ subprocess
             │
┌────────────▼────────────────────────────────────────────────┐
│ SCRIPTS PYTHON (existentes)                                 │
│                                                             │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │ bed_compiler     │  │ blender headless │               │
│  │ (dsl/)           │  │ (leito_extracao) │               │
│  └──────────────────┘  └──────────────────┘               │
│                                                             │
│  ┌──────────────────┐                                      │
│  │ openfoam setup   │                                      │
│  │ (setup_case)     │                                      │
│  └──────────────────┘                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 estrutura de pastas

```
CFD-PIPELINE-TCC-1/
├── backend/                    # ← novo
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py            # fastapi app
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py      # endpoints
│   │   │   └── models.py      # pydantic models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── bed_service.py
│   │   │   ├── blender_service.py
│   │   │   └── openfoam_service.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── file_manager.py
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                   # ← novo
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   ├── components/
│   │   │   ├── BedForm.jsx           # formulário parâmetros
│   │   │   ├── ModelViewer.jsx       # three.js
│   │   │   ├── ResultsChart.jsx      # plotly
│   │   │   └── JobStatus.jsx         # status simulação
│   │   ├── services/
│   │   │   └── api.js                # cliente http
│   │   └── styles/
│   │       └── App.css
│   ├── package.json
│   └── README.md
│
├── dsl/                        # existente
├── scripts/                    # existente
├── output/                     # existente
│   ├── models/                 # .blend, .stl
│   ├── simulations/            # casos openfoam
│   └── results/                # dados processados
└── docker/                     # ← futuro (containerização)
    ├── Dockerfile.backend
    ├── Dockerfile.frontend
    ├── Dockerfile.blender
    ├── Dockerfile.openfoam
    └── docker-compose.yml
```

---

## 🚀 implementação fase 1: mvp simples

### passo 1: backend fastapi (2-3 horas)

**objetivo:** api rest que executa scripts python existentes

**endpoints essenciais:**

```python
POST /api/bed/compile
  body: { "parameters": {...} }
  retorna: { "bed_file": "path", "json_file": "path" }

POST /api/model/generate
  body: { "bed_json": "path" }
  retorna: { "job_id": "uuid", "status": "queued" }

GET /api/job/{job_id}
  retorna: { "status": "running|completed|failed", "progress": 75 }

POST /api/simulation/create
  body: { "blend_file": "path", "bed_json": "path" }
  retorna: { "job_id": "uuid" }

GET /api/files/{type}
  retorna: [ "file1.blend", "file2.blend" ]
```

**tecnologias:**
- fastapi (framework)
- uvicorn (servidor)
- pydantic (validação)
- subprocess (executar scripts)

---

### passo 2: frontend react básico (3-4 horas)

**objetivo:** interface simples para criar leitos

**telas essenciais:**

1. **tela 1: criar leito**
   - formulário com campos do bed_wizard
   - botão "gerar modelo 3d"
   - barra de progresso

2. **tela 2: visualizar modelo**
   - three.js mostrando .stl
   - botão "executar simulação"

3. **tela 3: resultados**
   - gráficos plotly
   - download de arquivos

**tecnologias:**
- react + vite (rápido)
- tailwind css (estilização)
- @react-three/fiber (visualização 3d)
- plotly.js (gráficos)
- axios (http client)

---

## 💻 código inicial - backend

vou criar os arquivos principais agora!

---

## 🐳 preparação para containerização (futuro)

### requisitos identificados:

1. **backend:**
   - python 3.11
   - fastapi + uvicorn
   - acesso aos scripts python

2. **frontend:**
   - node 18+
   - build estático (nginx)

3. **blender:**
   - blender 4.0.2 headless
   - python scripts
   - sem display (xvfb)

4. **openfoam:**
   - wsl2/linux
   - openfoam 11
   - paraview (opcional)

5. **compartilhamento:**
   - volumes docker para `output/`
   - rede interna para comunicação
   - variáveis de ambiente

**docker-compose.yml estrutura:**
```yaml
services:
  backend:
    build: ./docker/Dockerfile.backend
    ports: ["8000:8000"]
    volumes: ["./output:/app/output"]
  
  frontend:
    build: ./docker/Dockerfile.frontend
    ports: ["3000:80"]
  
  blender:
    build: ./docker/Dockerfile.blender
    volumes: ["./output:/app/output"]
  
  openfoam:
    build: ./docker/Dockerfile.openfoam
    volumes: ["./output:/app/output"]
```

---

## ✅ próximos passos

quer que eu implemente agora?

**vou criar:**

1. ✅ estrutura completa backend fastapi
2. ✅ estrutura completa frontend react
3. ✅ integração com scripts existentes
4. ✅ documentação de uso
5. ✅ scripts de inicialização

**isso vai permitir:**
- testar localmente primeiro
- entender fluxo completo
- identificar problemas antes de containerizar
- base sólida para expansão

**posso começar?** 🚀

