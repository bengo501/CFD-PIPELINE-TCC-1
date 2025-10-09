# schemas pydantic para validacao de dados
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime


# schemas para Bed

class BedBase(BaseModel):
    """schema base para leito"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    diameter: float = Field(..., gt=0, le=1.0, description="diametro em metros")
    height: float = Field(..., gt=0, le=2.0, description="altura em metros")
    wall_thickness: float = Field(..., gt=0, le=0.1, description="espessura em metros")
    particle_count: int = Field(..., ge=10, le=10000, description="numero de particulas")
    particle_diameter: float = Field(..., gt=0, le=0.1, description="diametro particula em metros")
    particle_kind: str = Field(..., description="tipo de particula")
    packing_method: str = Field(..., description="metodo de empacotamento")
    porosity: Optional[float] = Field(None, ge=0, le=1, description="porosidade")


class BedCreate(BedBase):
    """schema para criar leito"""
    parameters_json: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class BedUpdate(BaseModel):
    """schema para atualizar leito"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    porosity: Optional[float] = Field(None, ge=0, le=1)
    bed_file_path: Optional[str] = None
    json_file_path: Optional[str] = None
    blend_file_path: Optional[str] = None
    stl_file_path: Optional[str] = None
    parameters_json: Optional[Dict[str, Any]] = None


class BedResponse(BedBase):
    """schema de resposta para leito"""
    id: int
    bed_file_path: Optional[str]
    json_file_path: Optional[str]
    blend_file_path: Optional[str]
    stl_file_path: Optional[str]
    parameters_json: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


# schemas para Simulation

class SimulationBase(BaseModel):
    """schema base para simulacao"""
    bed_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    regime: str = Field(..., description="laminar ou turbulent")
    inlet_velocity: float = Field(..., gt=0, le=100, description="velocidade em m/s")
    fluid_density: float = Field(..., gt=0, description="densidade em kg/m³")
    fluid_viscosity: float = Field(..., gt=0, description="viscosidade em Pa·s")
    solver: str = Field(default="simpleFoam")
    max_iterations: int = Field(default=1000, ge=100, le=100000)
    convergence_criteria: float = Field(default=1e-4, gt=0, le=1)
    
    @validator('regime')
    def validate_regime(cls, v):
        if v not in ['laminar', 'turbulent']:
            raise ValueError('regime deve ser laminar ou turbulent')
        return v


class SimulationCreate(SimulationBase):
    """schema para criar simulacao"""
    parameters_json: Optional[Dict[str, Any]] = None
    created_by: Optional[str] = None


class SimulationUpdate(BaseModel):
    """schema para atualizar simulacao"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[str] = Field(None, description="pending, running, completed, failed")
    progress: Optional[int] = Field(None, ge=0, le=100)
    mesh_cells_count: Optional[int] = None
    mesh_quality: Optional[str] = None
    case_directory: Optional[str] = None
    log_file_path: Optional[str] = None
    pressure_drop: Optional[float] = None
    average_velocity: Optional[float] = None
    reynolds_number: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None
    
    @validator('status')
    def validate_status(cls, v):
        if v and v not in ['pending', 'running', 'completed', 'failed']:
            raise ValueError('status invalido')
        return v


class SimulationResponse(SimulationBase):
    """schema de resposta para simulacao"""
    id: int
    status: str
    progress: int
    mesh_cells_count: Optional[int]
    mesh_quality: Optional[str]
    case_directory: Optional[str]
    log_file_path: Optional[str]
    pressure_drop: Optional[float]
    average_velocity: Optional[float]
    reynolds_number: Optional[float]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time: Optional[float]
    parameters_json: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


# schemas para Result

class ResultBase(BaseModel):
    """schema base para resultado"""
    simulation_id: int = Field(..., gt=0)
    result_type: str = Field(..., description="field, metric, validation, visualization")
    name: str = Field(..., min_length=1, max_length=255)
    value: Optional[float] = None
    unit: Optional[str] = Field(None, max_length=50)
    data_json: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    timestep: Optional[int] = None
    
    @validator('result_type')
    def validate_result_type(cls, v):
        valid_types = ['field', 'metric', 'validation', 'visualization']
        if v not in valid_types:
            raise ValueError(f'result_type deve ser um de: {valid_types}')
        return v


class ResultCreate(ResultBase):
    """schema para criar resultado"""
    pass


class ResultResponse(ResultBase):
    """schema de resposta para resultado"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# schemas de listagem com paginacao

class PaginatedResponse(BaseModel):
    """schema para resposta paginada"""
    total: int = Field(..., description="total de items")
    page: int = Field(..., ge=1, description="pagina atual")
    per_page: int = Field(..., ge=1, le=100, description="items por pagina")
    pages: int = Field(..., description="total de paginas")
    items: List[Any] = Field(..., description="items da pagina")


class BedListResponse(BaseModel):
    """schema de resposta para lista de leitos"""
    total: int
    page: int
    per_page: int
    pages: int
    items: List[BedResponse]


class SimulationListResponse(BaseModel):
    """schema de resposta para lista de simulacoes"""
    total: int
    page: int
    per_page: int
    pages: int
    items: List[SimulationResponse]


class ResultListResponse(BaseModel):
    """schema de resposta para lista de resultados"""
    total: int
    page: int
    per_page: int
    pages: int
    items: List[ResultResponse]

