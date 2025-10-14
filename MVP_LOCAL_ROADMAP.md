# roadmap: mvp local funcional

## objetivo

criar um mvp (minimum viable product) completo rodando localmente com frontend, backend e banco de dados integrados.

---

## o que já temos pronto

### ✅ frontend
- [x] aplicação react com vite
- [x] interface para criar leitos
- [x] visualização 3d com three.js
- [x] preview de parâmetros
- [x] internacionalização (pt/en)
- [x] paleta de cores aplicada
- [x] sidebar com navegação

### ✅ scripts blender
- [x] geração de modelos 3d
- [x] física de partículas
- [x] exportação múltiplos formatos
- [x] animação de queda

### ✅ scripts openfoam
- [x] configuração de casos cfd
- [x] geração de mesh
- [x] simulação de escoamento

### ✅ infraestrutura
- [x] docker-compose configurado
- [x] dockerfiles criados
- [x] scripts de setup

---

## o que falta implementar

### 🔧 backend (prioridade 1)
- [ ] estrutura fastapi básica
- [ ] endpoints crud para leitos
- [ ] integração com scripts blender
- [ ] integração com scripts openfoam
- [ ] upload/download de arquivos
- [ ] api de resultados

### 🗄️ banco de dados (prioridade 2)
- [ ] modelos sqlalchemy
- [ ] migrations com alembic
- [ ] conexão com postgresql
- [ ] seed data inicial

### 🔗 integração front-back (prioridade 3)
- [ ] conectar frontend com api
- [ ] endpoints de criação de leito
- [ ] endpoints de simulação
- [ ] listagem de resultados
- [ ] download de arquivos

### 📦 simplificações para mvp
- [ ] remover celery (executar tarefas síncronas)
- [ ] remover minio (salvar arquivos localmente)
- [ ] usar sqlite ao invés de postgresql (opcional)
- [ ] focar nas funcionalidades essenciais

---

## arquitetura do mvp local

```
┌─────────────────────────────────────────────────┐
│                   MVP LOCAL                     │
│                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │   FRONTEND  │  │   BACKEND   │  │  SQLITE │ │
│  │   (React)   │→ │  (FastAPI)  │→ │  (Dados)│ │
│  │ :5173       │  │  :8000      │  │         │ │
│  └─────────────┘  └─────────────┘  └─────────┘ │
│                           ↓                     │
│                   ┌───────────────┐             │
│                   │  SCRIPTS      │             │
│                   │  - Blender    │             │
│                   │  - OpenFOAM   │             │
│                   └───────────────┘             │
│                           ↓                     │
│                   ┌───────────────┐             │
│                   │  ARQUIVOS     │             │
│                   │  output/      │             │
│                   └───────────────┘             │
└─────────────────────────────────────────────────┘
```

---

## plano de implementação (1 semana)

### dia 1-2: backend básico
**objetivo:** criar api funcional

```
backend/
├── main.py                    # fastapi app
├── models.py                  # sqlalchemy models
├── schemas.py                 # pydantic schemas
├── database.py                # db connection
├── crud.py                    # database operations
└── requirements.txt           # dependências
```

**funcionalidades:**
- criar leito (post /beds)
- listar leitos (get /beds)
- obter leito (get /beds/{id})
- deletar leito (delete /beds/{id})

### dia 3: integração blender
**objetivo:** gerar modelos via api

**funcionalidades:**
- endpoint post /beds/{id}/generate
- executar script blender
- salvar arquivos em output/
- retornar status

### dia 4: integração openfoam
**objetivo:** simular via api

**funcionalidades:**
- endpoint post /beds/{id}/simulate
- executar script openfoam
- salvar resultados
- retornar dados

### dia 5: integração frontend
**objetivo:** conectar front com back

**funcionalidades:**
- chamar api de criação
- mostrar lista de leitos
- disparar geração de modelo
- disparar simulação
- mostrar resultados

### dia 6: testes e ajustes
**objetivo:** garantir funcionamento

**funcionalidades:**
- testar fluxo completo
- corrigir bugs
- melhorar ux
- documentar

### dia 7: polish
**objetivo:** finalizar mvp

**funcionalidades:**
- melhorias visuais
- tratamento de erros
- loading states
- documentação final

---

## estrutura simplificada do backend

### backend/main.py
```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/beds/", response_model=schemas.Bed)
def create_bed(bed: schemas.BedCreate, db: Session = Depends(get_db)):
    return crud.create_bed(db=db, bed=bed)

@app.get("/beds/", response_model=list[schemas.Bed])
def read_beds(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    beds = crud.get_beds(db, skip=skip, limit=limit)
    return beds

@app.post("/beds/{bed_id}/generate")
def generate_bed(bed_id: int, db: Session = Depends(get_db)):
    bed = crud.get_bed(db, bed_id=bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="bed not found")
    
    # executar blender
    result = run_blender_script(bed)
    return {"status": "success", "result": result}

@app.post("/beds/{bed_id}/simulate")
def simulate_bed(bed_id: int, db: Session = Depends(get_db)):
    bed = crud.get_bed(db, bed_id=bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="bed not found")
    
    # executar openfoam
    result = run_openfoam_script(bed)
    return {"status": "success", "result": result}
```

### backend/models.py
```python
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Bed(Base):
    __tablename__ = "beds"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    diameter = Column(Float)
    height = Column(Float)
    particle_diameter = Column(Float)
    particle_count = Column(Integer)
    particle_shape = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### backend/requirements.txt
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
python-multipart==0.0.6
```

---

## funcionalidades do mvp

### core features (essenciais)
1. **criar leito** - interface para definir parâmetros
2. **gerar modelo 3d** - executar blender e salvar arquivos
3. **simular cfd** - executar openfoam e obter resultados
4. **visualizar resultados** - mostrar modelos 3d e dados

### nice to have (opcional)
1. histórico de leitos
2. comparação de resultados
3. exportar relatórios
4. templates pré-definidos

---

## como executar o mvp

### setup inicial
```bash
# 1. backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

# 2. frontend (outro terminal)
cd frontend
npm install
npm run dev

# 3. acessar
# frontend: http://localhost:5173
# backend: http://localhost:8000
# docs: http://localhost:8000/docs
```

---

## métricas de sucesso do mvp

### funcionais
- [ ] criar leito via interface ✓
- [ ] gerar modelo 3d ✓
- [ ] executar simulação cfd ✓
- [ ] visualizar resultados ✓
- [ ] download de arquivos ✓

### técnicas
- [ ] frontend conectado ao backend ✓
- [ ] banco de dados funcionando ✓
- [ ] scripts blender integrados ✓
- [ ] scripts openfoam integrados ✓
- [ ] tratamento de erros ✓

### ux
- [ ] interface intuitiva ✓
- [ ] feedback visual (loading) ✓
- [ ] mensagens de erro claras ✓
- [ ] fluxo completo funcional ✓

---

## próximos passos

1. **implementar backend básico** (dia 1-2)
   - estrutura fastapi
   - modelos sqlalchemy
   - endpoints crud

2. **integrar blender** (dia 3)
   - endpoint de geração
   - executar script
   - salvar resultados

3. **integrar openfoam** (dia 4)
   - endpoint de simulação
   - executar script
   - retornar dados

4. **conectar frontend** (dia 5)
   - chamar endpoints
   - mostrar resultados
   - download de arquivos

5. **testar e ajustar** (dia 6-7)
   - testes completos
   - correções
   - documentação

---

## decisões de simplificação

### o que remover temporariamente
- ❌ celery (usar execução síncrona)
- ❌ minio (usar filesystem local)
- ❌ redis (sem cache por enquanto)
- ❌ docker (rodar nativo primeiro)
- ❌ autenticação (adicionar depois)

### o que manter
- ✅ fastapi (backend)
- ✅ react (frontend)
- ✅ sqlite/postgresql (banco)
- ✅ blender (geração 3d)
- ✅ openfoam (simulação)

---

**vamos começar implementando o backend básico?**
