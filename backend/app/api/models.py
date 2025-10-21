"""
modelos pydantic para validação de dados
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum
from datetime import datetime

# enums
class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class JobType(str, Enum):
    COMPILE = "compile"
    GENERATE_MODEL = "generate_model"
    SIMULATION = "simulation"
    FULL_PIPELINE = "full_pipeline"

# modelos de parâmetros do leito
class BedParameters(BaseModel):
    """parâmetros do leito empacotado"""
    # geometria do leito
    diameter: float = Field(..., description="diâmetro do leito (m)", ge=0.01, le=1.0)
    height: float = Field(..., description="altura do leito (m)", ge=0.01, le=2.0)
    wall_thickness: float = Field(0.002, description="espessura da parede (m)")
    
    # tampas
    lid_top: str = Field("flat", description="tipo tampa superior (flat/hemispherical/none)")
    lid_bottom: str = Field("flat", description="tipo tampa inferior")
    lid_thickness: float = Field(0.003, description="espessura das tampas (m)")
    
    # partículas
    particle_count: int = Field(..., description="quantidade de partículas", ge=10, le=10000)
    particle_type: str = Field("sphere", description="tipo de partícula (sphere/cube)")
    particle_diameter: float = Field(..., description="diâmetro da partícula (m)", ge=0.001, le=0.1)
    
    # empacotamento
    packing_method: str = Field("rigid_body", description="método de empacotamento")
    gravity: float = Field(-9.81, description="gravidade (m/s²)")
    friction: float = Field(0.5, description="coeficiente de atrito")
    substeps: int = Field(10, description="substeps da simulação física")
    
    # cfd (opcional)
    cfd_regime: Optional[str] = Field("laminar", description="regime do fluido")
    inlet_velocity: Optional[float] = Field(0.01, description="velocidade entrada (m/s)")
    fluid_density: Optional[float] = Field(1000.0, description="densidade fluido (kg/m³)")
    fluid_viscosity: Optional[float] = Field(0.001, description="viscosidade (Pa.s)")

class CompileRequest(BaseModel):
    """requisição para compilar arquivo .bed"""
    parameters: BedParameters
    filename: Optional[str] = Field(None, description="nome do arquivo (auto se null)")

class CompileResponse(BaseModel):
    """resposta da compilação"""
    success: bool
    bed_file: str
    json_file: str
    message: str

class GenerateModelRequest(BaseModel):
    """requisição para gerar modelo 3d"""
    json_file: str
    open_blender: bool = Field(False, description="abrir blender gui após gerar")

class SimulationRequest(BaseModel):
    """requisição para criar simulação cfd"""
    json_file: str
    blend_file: str
    run_simulation: bool = Field(False, description="executar simulação imediatamente")

# modelos de job (tarefa assíncrona)
class Job(BaseModel):
    """tarefa assíncrona"""
    job_id: str
    job_type: JobType
    status: JobStatus
    progress: int = Field(0, ge=0, le=100)
    created_at: datetime
    updated_at: datetime
    output_files: List[str] = []
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}

class JobResponse(BaseModel):
    """resposta de criação de job"""
    job_id: str
    status: JobStatus
    message: str

# modelos de listagem
class FileInfo(BaseModel):
    """informações de arquivo"""
    filename: str
    path: str
    size: int
    created_at: datetime
    file_type: str

class FileListResponse(BaseModel):
    """lista de arquivos"""
    files: List[FileInfo]
    total: int

