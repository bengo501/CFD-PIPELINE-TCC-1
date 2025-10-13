# exemplo prático: implementação de código

## implementação passo a passo

vou mostrar como implementar o sistema de banco de dados e deploy no projeto cfd pipeline.

---

## passo 1: estrutura de pastas

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── bed.py
│   │   ├── simulation.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── bed.py
│   │   ├── simulation.py
│   │   └── user.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   ├── beds.py
│   │   ├── simulations.py
│   │   └── health.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── celery.py
│   │   └── minio_client.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── bed_service.py
│   │   ├── simulation_service.py
│   │   └── file_service.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── bed_tasks.py
│   │   ├── cfd_tasks.py
│   │   └── cleanup_tasks.py
│   └── utils/
│       ├── __init__.py
│       ├── blender_utils.py
│       └── openfoam_utils.py
├── migrations/
├── tests/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── alembic.ini
└── .env.example
```

---

## passo 2: configurações base

### app/core/config.py
```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # api
    api_v1_str: str = "/api/v1"
    project_name: str = "cfd pipeline"
    version: str = "0.1.0"
    
    # database
    database_url: str = "postgresql://postgres:postgres123@localhost:5432/cfd_pipeline"
    
    # redis
    redis_url: str = "redis://localhost:6379"
    
    # minio
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_bucket: str = "cfd-pipeline"
    minio_secure: bool = False
    
    # celery
    celery_broker_url: str = "redis://localhost:6379"
    celery_result_backend: str = "redis://localhost:6379"
    
    # paths
    blender_script_path: str = "scripts/blender_scripts/leito_extracao.py"
    openfoam_install_path: str = "/opt/openfoam11"
    
    # security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### app/core/database.py
```python
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

---

## passo 3: modelos sqlalchemy

### app/models/bed.py
```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base import Base

class Bed(Base):
    __tablename__ = "beds"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    
    # parâmetros geométricos
    diameter = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    
    # parâmetros das partículas
    particle_diameter = Column(Float, nullable=False)
    particle_count = Column(Integer, nullable=False)
    particle_shape = Column(String(20), default="sphere")
    
    # configurações de simulação
    simulation_time = Column(Float, default=20.0)
    gravity = Column(Float, default=9.81)
    
    # metadados
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100))
    is_active = Column(Boolean, default=True)
    
    # relacionamentos
    simulations = relationship("Simulation", back_populates="bed", cascade="all, delete-orphan")
    files = relationship("BedFile", back_populates="bed", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Bed(id={self.id}, name='{self.name}')>"
```

### app/models/simulation.py
```python
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.models.base import Base

class SimulationStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Simulation(Base):
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    bed_id = Column(Integer, ForeignKey("beds.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # status da simulação
    status = Column(Enum(SimulationStatus), default=SimulationStatus.PENDING)
    
    # parâmetros cfd
    reynolds_number = Column(Float)
    inlet_velocity = Column(Float, default=1.0)
    fluid_density = Column(Float, default=1.225)
    fluid_viscosity = Column(Float, default=1.81e-5)
    
    # resultados
    pressure_drop = Column(Float)
    flow_rate = Column(Float)
    
    # timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # arquivos
    log_file_path = Column(String(500))
    result_file_path = Column(String(500))
    mesh_file_path = Column(String(500))
    
    # relacionamentos
    bed = relationship("Bed", back_populates="simulations")
    files = relationship("SimulationFile", back_populates="simulation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Simulation(id={self.id}, name='{self.name}', status='{self.status}')>"
```

---

## passo 4: schemas pydantic

### app/schemas/bed.py
```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.simulation import Simulation

class BedBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    diameter: float = Field(..., gt=0, description="diâmetro do leito em metros")
    height: float = Field(..., gt=0, description="altura do leito em metros")
    particle_diameter: float = Field(..., gt=0, description="diâmetro das partículas em metros")
    particle_count: int = Field(..., gt=0, description="número de partículas")
    particle_shape: str = Field(default="sphere", description="forma das partículas")
    simulation_time: float = Field(default=20.0, gt=0, description="tempo de simulação em segundos")
    gravity: float = Field(default=9.81, gt=0, description="aceleração da gravidade")

class BedCreate(BedBase):
    pass

class BedUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    diameter: Optional[float] = Field(None, gt=0)
    height: Optional[float] = Field(None, gt=0)
    particle_diameter: Optional[float] = Field(None, gt=0)
    particle_count: Optional[int] = Field(None, gt=0)
    particle_shape: Optional[str] = None
    simulation_time: Optional[float] = Field(None, gt=0)
    gravity: Optional[float] = Field(None, gt=0)

class Bed(BedBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True

class BedWithDetails(Bed):
    simulations: List[Simulation] = []
    files_count: int = 0
    
    class Config:
        from_attributes = True
```

---

## passo 5: serviços

### app/services/bed_service.py
```python
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from app.models.bed import Bed
from app.schemas.bed import BedCreate, BedUpdate
from app.core.minio_client import minio_client
from app.tasks.bed_tasks import generate_bed_model_task
from datetime import datetime

class BedService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_bed(self, bed_data: BedCreate, user_id: str = None) -> Bed:
        """criar novo leito"""
        db_bed = Bed(
            **bed_data.dict(),
            created_by=user_id
        )
        self.db.add(db_bed)
        self.db.commit()
        self.db.refresh(db_bed)
        return db_bed
    
    def get_bed(self, bed_id: int) -> Optional[Bed]:
        """obter leito por id"""
        return self.db.query(Bed).filter(
            and_(Bed.id == bed_id, Bed.is_active == True)
        ).first()
    
    def list_beds(self, skip: int = 0, limit: int = 100) -> List[Bed]:
        """listar leitos"""
        return self.db.query(Bed).filter(Bed.is_active == True)\
            .offset(skip).limit(limit).all()
    
    def update_bed(self, bed_id: int, bed_data: BedUpdate) -> Optional[Bed]:
        """atualizar leito"""
        db_bed = self.get_bed(bed_id)
        if not db_bed:
            return None
        
        update_data = bed_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_bed, field, value)
        
        db_bed.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_bed)
        return db_bed
    
    def delete_bed(self, bed_id: int) -> bool:
        """deletar leito (soft delete)"""
        db_bed = self.get_bed(bed_id)
        if not db_bed:
            return False
        
        db_bed.is_active = False
        db_bed.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    def generate_model(self, bed_id: int) -> str:
        """gerar modelo 3d do leito"""
        db_bed = self.get_bed(bed_id)
        if not db_bed:
            raise ValueError("leito não encontrado")
        
        # disparar tarefa celery
        task = generate_bed_model_task.delay(bed_id)
        return task.id
    
    def get_bed_files(self, bed_id: int) -> List[dict]:
        """listar arquivos do leito"""
        files = minio_client.list_files(f"beds/{bed_id}/")
        return [
            {
                "name": file.split("/")[-1],
                "path": file,
                "type": file.split(".")[-1] if "." in file else "unknown"
            }
            for file in files
        ]
```

---

## passo 6: tarefas celery

### app/tasks/bed_tasks.py
```python
from celery import current_task
from app.core.celery import celery
from app.core.database import SessionLocal
from app.core.minio_client import minio_client
from app.models.bed import Bed
from app.models.bed_file import BedFile
from app.utils.blender_utils import BlenderUtils
import json
import subprocess
from pathlib import Path
import tempfile

@celery.task(bind=True, name="generate_bed_model")
def generate_bed_model_task(self, bed_id: int):
    """gerar modelo 3d do leito no blender"""
    db = SessionLocal()
    
    try:
        # obter dados do leito
        bed = db.query(Bed).filter(Bed.id == bed_id).first()
        if not bed:
            return {"status": "error", "message": "leito não encontrado"}
        
        # atualizar progresso
        self.update_state(
            state="PROGRESS",
            meta={"current": 0, "total": 100, "status": "preparando parâmetros"}
        )
        
        # preparar parâmetros para blender
        params = {
            "diameter": bed.diameter,
            "height": bed.height,
            "particle_diameter": bed.particle_diameter,
            "particle_count": bed.particle_count,
            "particle_shape": bed.particle_shape,
            "simulation_time": bed.simulation_time,
            "gravity": bed.gravity,
            "output_name": bed.name
        }
        
        self.update_state(
            state="PROGRESS",
            meta={"current": 20, "total": 100, "status": "executando blender"}
        )
        
        # criar diretório temporário
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # executar blender
            result = subprocess.run([
                "blender",
                "--background",
                "--python", "scripts/blender_scripts/leito_extracao.py",
                "--",
                "--params", json.dumps(params),
                "--output", str(temp_path)
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                return {"status": "error", "message": f"erro blender: {result.stderr}"}
            
            self.update_state(
                state="PROGRESS",
                meta={"current": 80, "total": 100, "status": "salvando arquivos"}
            )
            
            # salvar arquivos no minio
            saved_files = []
            for file_path in temp_path.glob("*"):
                if file_path.is_file():
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                    
                    # upload para minio
                    minio_path = f"beds/{bed_id}/{file_path.name}"
                    success = minio_client.upload_file(
                        minio_path,
                        file_data,
                        "application/octet-stream"
                    )
                    
                    if success:
                        # salvar no banco
                        bed_file = BedFile(
                            bed_id=bed_id,
                            file_type=file_path.suffix[1:] if file_path.suffix else "unknown",
                            file_path=minio_path,
                            file_size=len(file_data)
                        )
                        db.add(bed_file)
                        saved_files.append(file_path.name)
            
            db.commit()
            
            self.update_state(
                state="PROGRESS",
                meta={"current": 100, "total": 100, "status": "concluído"}
            )
            
            return {
                "status": "completed",
                "message": f"modelo gerado com sucesso",
                "files": saved_files
            }
    
    except subprocess.TimeoutExpired:
        return {"status": "error", "message": "timeout na execução do blender"}
    except Exception as e:
        return {"status": "error", "message": f"erro interno: {str(e)}"}
    finally:
        db.close()

@celery.task(bind=True, name="cleanup_temp_files")
def cleanup_temp_files_task(self, file_paths: list):
    """limpar arquivos temporários"""
    try:
        for file_path in file_paths:
            minio_client.delete_file(file_path)
        return {"status": "completed", "message": "arquivos limpos"}
    except Exception as e:
        return {"status": "error", "message": f"erro na limpeza: {str(e)}"}
```

---

## passo 7: endpoints api

### app/api/beds.py
```python
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.bed import BedCreate, BedUpdate, Bed, BedWithDetails
from app.services.bed_service import BedService
from app.tasks.bed_tasks import generate_bed_model_task
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=Bed, status_code=201)
def create_bed(
    bed: BedCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """criar novo leito"""
    bed_service = BedService(db)
    
    # verificar se nome já existe
    existing_bed = db.query(Bed).filter(Bed.name == bed.name).first()
    if existing_bed:
        raise HTTPException(status_code=400, detail="nome do leito já existe")
    
    return bed_service.create_bed(bed, current_user)

@router.get("/", response_model=List[Bed])
def list_beds(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """listar leitos"""
    bed_service = BedService(db)
    return bed_service.list_beds(skip, limit)

@router.get("/{bed_id}", response_model=BedWithDetails)
def get_bed(bed_id: int, db: Session = Depends(get_db)):
    """obter leito por id"""
    bed_service = BedService(db)
    bed = bed_service.get_bed(bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="leito não encontrado")
    
    # adicionar contagem de arquivos
    files = bed_service.get_bed_files(bed_id)
    bed_dict = bed.__dict__.copy()
    bed_dict["files_count"] = len(files)
    
    return BedWithDetails(**bed_dict)

@router.put("/{bed_id}", response_model=Bed)
def update_bed(
    bed_id: int,
    bed_update: BedUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """atualizar leito"""
    bed_service = BedService(db)
    bed = bed_service.update_bed(bed_id, bed_update)
    if not bed:
        raise HTTPException(status_code=404, detail="leito não encontrado")
    return bed

@router.delete("/{bed_id}")
def delete_bed(
    bed_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """deletar leito"""
    bed_service = BedService(db)
    success = bed_service.delete_bed(bed_id)
    if not success:
        raise HTTPException(status_code=404, detail="leito não encontrado")
    return {"message": "leito deletado com sucesso"}

@router.post("/{bed_id}/generate")
def generate_model(bed_id: int, db: Session = Depends(get_db)):
    """gerar modelo 3d do leito"""
    bed_service = BedService(db)
    
    try:
        task_id = bed_service.generate_model(bed_id)
        return {"task_id": task_id, "message": "geração iniciada"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{bed_id}/files")
def get_bed_files(bed_id: int, db: Session = Depends(get_db)):
    """listar arquivos do leito"""
    bed_service = BedService(db)
    bed = bed_service.get_bed(bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="leito não encontrado")
    
    return bed_service.get_bed_files(bed_id)

@router.get("/task/{task_id}")
def get_task_status(task_id: str):
    """obter status de tarefa"""
    task = generate_bed_model_task.AsyncResult(task_id)
    
    if task.state == "PENDING":
        response = {"state": task.state, "status": "aguardando"}
    elif task.state == "PROGRESS":
        response = {
            "state": task.state,
            "current": task.info.get("current", 0),
            "total": task.info.get("total", 1),
            "status": task.info.get("status", "")
        }
    elif task.state == "SUCCESS":
        response = {"state": task.state, "result": task.result}
    else:
        response = {"state": task.state, "error": str(task.info)}
    
    return response
```

---

## passo 8: main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import engine
from app.models import base
from app.api import beds, simulations, health

# criar tabelas
base.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    openapi_url=f"{settings.api_v1_str}/openapi.json"
)

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# rotas
app.include_router(health.router, tags=["health"])
app.include_router(beds.router, prefix=f"{settings.api_v1_str}/beds", tags=["beds"])
app.include_router(simulations.router, prefix=f"{settings.api_v1_str}/simulations", tags=["simulations"])

@app.get("/")
def root():
    return {"message": "cfd pipeline api", "version": settings.version}
```

---

## passo 9: docker-compose.yml

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
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
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
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3

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
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      minio:
        condition: service_healthy
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  celery-worker:
    build: .
    environment:
      DATABASE_URL: postgresql://postgres:postgres123@postgres:5432/cfd_pipeline
      REDIS_URL: redis://redis:6379
      MINIO_ENDPOINT: minio:9000
      MINIO_ACCESS_KEY: minioadmin
      MINIO_SECRET_KEY: minioadmin123
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - .:/app
    command: celery -A app.core.celery worker --loglevel=info --concurrency=2

  celery-beat:
    build: .
    environment:
      DATABASE_URL: postgresql://postgres:postgres123@postgres:5432/cfd_pipeline
      REDIS_URL: redis://redis:6379
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - .:/app
    command: celery -A app.core.celery beat --loglevel=info

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

---

## passo 10: comandos de execução

### desenvolvimento local
```bash
# iniciar containers
docker-compose up -d

# aguardar serviços ficarem saudáveis
docker-compose ps

# executar migrations
alembic upgrade head

# iniciar backend
uvicorn app.main:app --reload

# em outro terminal - iniciar celery worker
celery -A app.core.celery worker --loglevel=info

# em outro terminal - iniciar celery beat
celery -A app.core.celery beat --loglevel=info
```

### testar api
```bash
# criar leito
curl -X POST "http://localhost:8000/api/v1/beds/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "leito_teste",
    "diameter": 0.025,
    "height": 0.1,
    "particle_diameter": 0.003,
    "particle_count": 100,
    "particle_shape": "sphere"
  }'

# listar leitos
curl "http://localhost:8000/api/v1/beds/"

# gerar modelo
curl -X POST "http://localhost:8000/api/v1/beds/1/generate"

# verificar status da tarefa
curl "http://localhost:8000/api/v1/beds/task/{task_id}"
```

---

## resumo da implementação

1. **configurações** - settings e conexões
2. **modelos** - sqlalchemy entities
3. **schemas** - pydantic validation
4. **serviços** - business logic
5. **tarefas** - celery workers
6. **endpoints** - fastapi routes
7. **containers** - docker-compose
8. **testes** - api endpoints

**esta implementação fornece uma base sólida para o sistema completo!**
