# guia: implementação banco de dados e deploy

## visão geral

implementação completa de um sistema de banco de dados distribuído com postgresql, minio, celery e deploy no railway para o projeto cfd pipeline.

---

## arquitetura do sistema

### componentes principais

```
┌─────────────────┬─────────────────┬─────────────────┐
│    FRONTEND     │     BACKEND     │   INFRAESTRUTURA │
│                 │                 │                 │
│ react (vite)    │ fastapi (python)│ postgresql      │
│ localhost:5173  │ localhost:8000  │ port:5432       │
│                 │                 │                 │
│                 │ celery worker   │ redis           │
│                 │ celery beat     │ port:6379       │
│                 │                 │                 │
│                 │                 │ minio           │
│                 │                 │ port:9000       │
└─────────────────┴─────────────────┴─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │     RAILWAY     │
                    │                 │
                    │ deploy cloud    │
                    │ postgresql      │
                    │ redis           │
                    │ minio           │
                    │ celery workers  │
                    └─────────────────┘
```

---

## tecnologias explicadas

### 1. postgresql
**função:** banco de dados relacional principal
- armazena metadados dos leitos
- histórico de simulações
- usuários e configurações
- relacionamentos entre entidades

### 2. redis
**função:** cache e message broker
- cache de resultados frequentes
- fila de tarefas do celery
- sessões de usuário
- rate limiting

### 3. minio
**função:** armazenamento de objetos
- arquivos .bed gerados
- modelos 3d (.blend, .gltf, .glb)
- resultados cfd (.foam, .vtk)
- backups e logs

### 4. celery
**função:** processamento assíncrono
- execução de simulações cfd
- geração de modelos blender
- processamento de arquivos
- tarefas agendadas

### 5. railway
**função:** plataforma de deploy
- containers docker
- bancos de dados gerenciados
- redis gerenciado
- minio gerenciado
- domínio automático

---

## implementação local (desenvolvimento)

### 1. estrutura de pastas

```
backend/
├── app/
│   ├── models/           # sqlalchemy models
│   ├── schemas/          # pydantic schemas
│   ├── api/              # endpoints fastapi
│   ├── core/             # configurações
│   ├── services/         # lógica de negócio
│   ├── tasks/            # tarefas celery
│   └── utils/            # utilitários
├── migrations/           # alembic migrations
├── docker-compose.yml    # containers locais
└── requirements.txt      # dependências
```

### 2. docker-compose.yml (desenvolvimento)

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
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  minio:
    image: minio/minio
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin123
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    command: server /data --console-address ":9001"

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://postgres:postgres123@postgres:5432/cfd_pipeline
      REDIS_URL: redis://redis:6379
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin123
    depends_on:
      - postgres
      - redis
      - minio
    volumes:
      - .:/app

  celery-worker:
    build: .
    command: celery -A app.core.celery worker --loglevel=info
    environment:
      DATABASE_URL: postgresql://postgres:postgres123@postgres:5432/cfd_pipeline
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - .:/app

  celery-beat:
    build: .
    command: celery -A app.core.celery beat --loglevel=info
    environment:
      DATABASE_URL: postgresql://postgres:postgres123@postgres:5432/cfd_pipeline
      REDIS_URL: redis://redis:6379
    depends_on:
      - postgres
      - redis
    volumes:
      - .:/app

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

### 3. models (sqlalchemy)

```python
# app/models/bed.py
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Bed(Base):
    __tablename__ = "beds"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    description = Column(Text)
    
    # parâmetros do leito
    diameter = Column(Float)
    height = Column(Float)
    particle_diameter = Column(Float)
    particle_count = Column(Integer)
    particle_shape = Column(String(20))
    
    # metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))
    
    # relacionamentos
    simulations = relationship("Simulation", back_populates="bed")
    files = relationship("BedFile", back_populates="bed")

class Simulation(Base):
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    bed_id = Column(Integer, ForeignKey("beds.id"))
    name = Column(String(100))
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    
    # parâmetros cfd
    reynolds_number = Column(Float)
    pressure_drop = Column(Float)
    
    # resultados
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    log_file_path = Column(String(500))
    result_file_path = Column(String(500))
    
    # relacionamentos
    bed = relationship("Bed", back_populates="simulations")

class BedFile(Base):
    __tablename__ = "bed_files"
    
    id = Column(Integer, primary_key=True, index=True)
    bed_id = Column(Integer, ForeignKey("beds.id"))
    file_type = Column(String(20))  # bed, blend, gltf, glb, foam
    file_path = Column(String(500))  # caminho no minio
    file_size = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # relacionamentos
    bed = relationship("Bed", back_populates="files")
```

### 4. schemas (pydantic)

```python
# app/schemas/bed.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BedBase(BaseModel):
    name: str
    description: Optional[str] = None
    diameter: float
    height: float
    particle_diameter: float
    particle_count: int
    particle_shape: str

class BedCreate(BedBase):
    pass

class BedUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    diameter: Optional[float] = None
    height: Optional[float] = None
    particle_diameter: Optional[float] = None
    particle_count: Optional[int] = None
    particle_shape: Optional[str] = None

class Bed(BedBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    
    class Config:
        from_attributes = True

class BedWithFiles(Bed):
    files: List["BedFile"] = []
    simulations: List["Simulation"] = []

class BedFileBase(BaseModel):
    file_type: str
    file_path: str
    file_size: int

class BedFile(BedFileBase):
    id: int
    bed_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

### 5. configurações

```python
# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # database
    database_url: str = "postgresql://postgres:postgres123@localhost:5432/cfd_pipeline"
    
    # redis
    redis_url: str = "redis://localhost:6379"
    
    # minio
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_bucket: str = "cfd-pipeline"
    
    # celery
    celery_broker_url: str = "redis://localhost:6379"
    celery_result_backend: str = "redis://localhost:6379"
    
    # api
    api_host: str = "localhost"
    api_port: int = 8000
    debug: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 6. conexão banco

```python
# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 7. minio client

```python
# app/core/minio_client.py
from minio import Minio
from minio.error import S3Error
from app.core.config import settings
import io

class MinioClient:
    def __init__(self):
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=False
        )
        self._ensure_bucket()
    
    def _ensure_bucket(self):
        try:
            if not self.client.bucket_exists(settings.minio_bucket):
                self.client.make_bucket(settings.minio_bucket)
        except S3Error as e:
            print(f"erro ao criar bucket: {e}")
    
    def upload_file(self, file_path: str, file_data: bytes, content_type: str = "application/octet-stream"):
        try:
            self.client.put_object(
                settings.minio_bucket,
                file_path,
                io.BytesIO(file_data),
                length=len(file_data),
                content_type=content_type
            )
            return True
        except S3Error as e:
            print(f"erro ao fazer upload: {e}")
            return False
    
    def download_file(self, file_path: str) -> bytes:
        try:
            response = self.client.get_object(settings.minio_bucket, file_path)
            return response.read()
        except S3Error as e:
            print(f"erro ao fazer download: {e}")
            return None
    
    def delete_file(self, file_path: str):
        try:
            self.client.remove_object(settings.minio_bucket, file_path)
            return True
        except S3Error as e:
            print(f"erro ao deletar arquivo: {e}")
            return False
    
    def list_files(self, prefix: str = ""):
        try:
            objects = self.client.list_objects(settings.minio_bucket, prefix=prefix)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            print(f"erro ao listar arquivos: {e}")
            return []

minio_client = MinioClient()
```

### 8. celery setup

```python
# app/core/celery.py
from celery import Celery
from app.core.config import settings

celery = Celery(
    "cfd_pipeline",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.bed_tasks", "app.tasks.cfd_tasks"]
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Sao_Paulo",
    enable_utc=True,
)
```

### 9. tarefas celery

```python
# app/tasks/bed_tasks.py
from celery import current_task
from app.core.celery import celery
from app.core.minio_client import minio_client
from app.models.bed import Bed, BedFile
from app.core.database import SessionLocal
import subprocess
import json
from pathlib import Path

@celery.task(bind=True)
def generate_bed_model(self, bed_id: int, params: dict):
    """gerar modelo 3d do leito no blender"""
    db = SessionLocal()
    try:
        bed = db.query(Bed).filter(Bed.id == bed_id).first()
        if not bed:
            return {"status": "error", "message": "leito não encontrado"}
        
        # atualizar status
        self.update_state(state="PROGRESS", meta={"status": "gerando modelo 3d"})
        
        # criar arquivo .bed
        bed_content = f"""
bed {bed.name} {{
    geometry {{
        diameter = {params['diameter']}m;
        height = {params['height']}m;
    }}
    
    particles {{
        diameter = {params['particle_diameter']}m;
        count = {params['particle_count']};
        shape = {params['particle_shape']};
    }}
}}
"""
        
        # salvar no minio
        minio_client.upload_file(
            f"beds/{bed_id}/{bed.name}.bed",
            bed_content.encode(),
            "text/plain"
        )
        
        # executar blender
        self.update_state(state="PROGRESS", meta={"status": "executando blender"})
        
        result = subprocess.run([
            "blender", "--background", "--python", "scripts/blender_scripts/leito_extracao.py",
            "--", "--params", json.dumps(params)
        ], capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            return {"status": "error", "message": result.stderr}
        
        # salvar arquivos gerados
        output_dir = Path("output") / bed.name
        for file_path in output_dir.glob("*"):
            with open(file_path, "rb") as f:
                file_data = f.read()
            
            minio_client.upload_file(
                f"beds/{bed_id}/{file_path.name}",
                file_data,
                "application/octet-stream"
            )
            
            # salvar no banco
            bed_file = BedFile(
                bed_id=bed_id,
                file_type=file_path.suffix[1:],
                file_path=f"beds/{bed_id}/{file_path.name}",
                file_size=len(file_data)
            )
            db.add(bed_file)
        
        db.commit()
        
        return {"status": "completed", "message": "modelo gerado com sucesso"}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@celery.task(bind=True)
def run_cfd_simulation(self, simulation_id: int, bed_id: int):
    """executar simulação cfd"""
    db = SessionLocal()
    try:
        simulation = db.query(Simulation).filter(Simulation.id == simulation_id).first()
        bed = db.query(Bed).filter(Bed.id == bed_id).first()
        
        if not simulation or not bed:
            return {"status": "error", "message": "simulação ou leito não encontrado"}
        
        # atualizar status
        simulation.status = "running"
        db.commit()
        
        self.update_state(state="PROGRESS", meta={"status": "preparando simulação"})
        
        # baixar arquivos do minio
        mesh_file = minio_client.download_file(f"beds/{bed_id}/{bed.name}.foam")
        
        # executar openfoam
        self.update_state(state="PROGRESS", meta={"status": "executando openfoam"})
        
        result = subprocess.run([
            "bash", "-c", "cd /tmp && source /opt/openfoam11/etc/bashrc && ./Allrun"
        ], capture_output=True, text=True, timeout=1800)  # 30 minutos
        
        if result.returncode != 0:
            simulation.status = "failed"
            db.commit()
            return {"status": "error", "message": result.stderr}
        
        # salvar resultados
        with open("/tmp/result.foam", "rb") as f:
            result_data = f.read()
        
        minio_client.upload_file(
            f"simulations/{simulation_id}/result.foam",
            result_data,
            "application/octet-stream"
        )
        
        simulation.status = "completed"
        simulation.result_file_path = f"simulations/{simulation_id}/result.foam"
        db.commit()
        
        return {"status": "completed", "message": "simulação concluída"}
        
    except Exception as e:
        simulation.status = "failed"
        db.commit()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
```

### 10. endpoints api

```python
# app/api/beds.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.bed import Bed, Simulation
from app.schemas.bed import BedCreate, BedUpdate, Bed as BedSchema
from app.tasks.bed_tasks import generate_bed_model, run_cfd_simulation

router = APIRouter()

@router.post("/", response_model=BedSchema)
def create_bed(bed: BedCreate, db: Session = Depends(get_db)):
    """criar novo leito"""
    db_bed = Bed(**bed.dict())
    db.add(db_bed)
    db.commit()
    db.refresh(db_bed)
    return db_bed

@router.get("/", response_model=List[BedSchema])
def list_beds(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """listar leitos"""
    beds = db.query(Bed).offset(skip).limit(limit).all()
    return beds

@router.post("/{bed_id}/generate")
def generate_model(bed_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """gerar modelo 3d do leito"""
    bed = db.query(Bed).filter(Bed.id == bed_id).first()
    if not bed:
        raise HTTPException(status_code=404, detail="leito não encontrado")
    
    params = {
        "diameter": bed.diameter,
        "height": bed.height,
        "particle_diameter": bed.particle_diameter,
        "particle_count": bed.particle_count,
        "particle_shape": bed.particle_shape
    }
    
    task = generate_bed_model.delay(bed_id, params)
    return {"task_id": task.id, "status": "started"}

@router.post("/{bed_id}/simulate")
def run_simulation(bed_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """executar simulação cfd"""
    bed = db.query(Bed).filter(Bed.id == bed_id).first()
    if not bed:
        raise HTTPException(status_code=404, detail="leito não encontrado")
    
    simulation = Simulation(bed_id=bed_id, name=f"sim_{bed.name}")
    db.add(simulation)
    db.commit()
    db.refresh(simulation)
    
    task = run_cfd_simulation.delay(simulation.id, bed_id)
    return {"task_id": task.id, "simulation_id": simulation.id, "status": "started"}

@router.get("/task/{task_id}")
def get_task_status(task_id: str):
    """obter status de tarefa"""
    task = generate_bed_model.AsyncResult(task_id)
    
    if task.state == "PENDING":
        response = {"state": task.state, "status": "aguardando"}
    elif task.state == "PROGRESS":
        response = {"state": task.state, "current": task.info.get("current", 0), "total": task.info.get("total", 1), "status": task.info.get("status", "")}
    elif task.state == "SUCCESS":
        response = {"state": task.state, "result": task.result}
    else:
        response = {"state": task.state, "error": str(task.info)}
    
    return response
```

---

## deploy no railway

### 1. railway.toml

```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"

[environments.production]
variables = { NODE_ENV = "production" }
```

### 2. railway services

```bash
# criar projeto
railway login
railway init

# adicionar postgresql
railway add postgresql

# adicionar redis
railway add redis

# adicionar minio (custom service)
railway add --service minio

# conectar variáveis
railway variables set DATABASE_URL=${{Postgres.DATABASE_URL}}
railway variables set REDIS_URL=${{Redis.REDIS_URL}}
railway variables set MINIO_ENDPOINT=minio:9000
railway variables set MINIO_ACCESS_KEY=minioadmin
railway variables set MINIO_SECRET_KEY=minioadmin123
```

### 3. dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# instalar openfoam (se necessário)
RUN curl -s https://dl.openfoam.org/gpg.key | apt-key add - \
    && echo "deb http://dl.openfoam.org/ubuntu focal main" >> /etc/apt/sources.list.d/openfoam.list \
    && apt-get update \
    && apt-get install -y openfoam11-dev

# copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copiar código
COPY . .

# criar diretórios
RUN mkdir -p output logs

# comando padrão
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 4. requirements.txt

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
redis==5.0.1
celery[redis]==5.3.4
minio==7.2.0
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

---

## fluxo de dados

### 1. criação de leito

```
frontend → fastapi → postgresql
         ↓
    celery task → blender → minio
         ↓
    postgresql (atualizar status)
```

### 2. simulação cfd

```
frontend → fastapi → postgresql
         ↓
    celery task → minio (baixar mesh)
         ↓
    openfoam → minio (salvar resultados)
         ↓
    postgresql (atualizar status)
```

### 3. visualização

```
frontend → fastapi → postgresql (metadados)
         ↓
    fastapi → minio (download arquivos)
         ↓
    frontend (exibir)
```

---

## comandos úteis

### desenvolvimento local

```bash
# iniciar containers
docker-compose up -d

# executar migrations
alembic upgrade head

# iniciar backend
uvicorn app.main:app --reload

# iniciar celery worker
celery -A app.core.celery worker --loglevel=info

# iniciar celery beat
celery -A app.core.celery beat --loglevel=info
```

### deploy railway

```bash
# deploy
railway up

# logs
railway logs

# conectar ao banco
railway connect postgresql

# variáveis
railway variables
```

---

## monitoramento

### 1. health checks

```python
# app/api/health.py
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": check_database(),
            "redis": check_redis(),
            "minio": check_minio(),
            "celery": check_celery()
        }
    }
```

### 2. métricas

```python
# app/core/metrics.py
from prometheus_client import Counter, Histogram, generate_latest

simulation_counter = Counter('simulations_total', 'total simulations', ['status'])
simulation_duration = Histogram('simulation_duration_seconds', 'simulation duration')

@router.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## próximos passos

1. **implementar modelos** - criar entidades sqlalchemy
2. **configurar docker** - docker-compose local
3. **criar endpoints** - api fastapi
4. **implementar tarefas** - celery workers
5. **configurar minio** - upload/download arquivos
6. **deploy railway** - configuração cloud
7. **testes** - unit + integration
8. **monitoramento** - logs + métricas

---

**este guia fornece a base completa para implementar um sistema robusto de banco de dados e deploy!**
