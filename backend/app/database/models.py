# modelos do banco de dados (sqlalchemy orm)
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .connection import Base


class Bed(Base):
    """
    modelo para leitos empacotados
    
    representa configuracoes de leitos gerados pela dsl
    """
    __tablename__ = "beds"
    
    # campos principais
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # parametros geometricos
    diameter = Column(Float, nullable=False)  # metros
    height = Column(Float, nullable=False)    # metros
    wall_thickness = Column(Float, nullable=False)  # metros
    
    # parametros de particulas
    particle_count = Column(Integer, nullable=False)
    particle_diameter = Column(Float, nullable=False)  # metros
    particle_kind = Column(String(50), nullable=False)  # sphere, cylinder, etc
    
    # parametros de empacotamento
    packing_method = Column(String(50), nullable=False)  # rigid_body, random, etc
    porosity = Column(Float, nullable=True)  # porosidade calculada
    
    # arquivos gerados
    bed_file_path = Column(String(500), nullable=True)      # caminho .bed
    json_file_path = Column(String(500), nullable=True)     # caminho .bed.json
    blend_file_path = Column(String(500), nullable=True)    # caminho .blend
    stl_file_path = Column(String(500), nullable=True)      # caminho .stl
    
    # parametros completos em json
    parameters_json = Column(JSON, nullable=True)
    
    # metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=True)  # usuario que criou
    
    # relacionamentos
    simulations = relationship("Simulation", back_populates="bed", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Bed(id={self.id}, name='{self.name}', diameter={self.diameter}m, height={self.height}m)>"


class Simulation(Base):
    """
    modelo para simulacoes cfd
    
    representa simulacoes openfoam executadas
    """
    __tablename__ = "simulations"
    
    # campos principais
    id = Column(Integer, primary_key=True, index=True)
    bed_id = Column(Integer, ForeignKey("beds.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # parametros cfd
    regime = Column(String(50), nullable=False)  # laminar, turbulent
    inlet_velocity = Column(Float, nullable=False)  # m/s
    fluid_density = Column(Float, nullable=False)   # kg/m³
    fluid_viscosity = Column(Float, nullable=False) # Pa·s
    
    # configuracao de malha
    mesh_cells_count = Column(Integer, nullable=True)
    mesh_quality = Column(String(50), nullable=True)  # good, acceptable, poor
    
    # configuracao solver
    solver = Column(String(50), nullable=False, default="simpleFoam")
    max_iterations = Column(Integer, nullable=False, default=1000)
    convergence_criteria = Column(Float, nullable=False, default=1e-4)
    
    # status da simulacao
    status = Column(String(50), nullable=False, default="pending")  
    # pending, running, completed, failed
    
    progress = Column(Integer, default=0)  # 0-100%
    
    # arquivos e diretorios
    case_directory = Column(String(500), nullable=True)
    log_file_path = Column(String(500), nullable=True)
    
    # resultados principais (calculados apos simulacao)
    pressure_drop = Column(Float, nullable=True)  # Pa
    average_velocity = Column(Float, nullable=True)  # m/s
    reynolds_number = Column(Float, nullable=True)
    
    # tempos de execucao
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    execution_time = Column(Float, nullable=True)  # segundos
    
    # parametros completos em json
    parameters_json = Column(JSON, nullable=True)
    
    # metadados
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(100), nullable=True)
    
    # relacionamentos
    bed = relationship("Bed", back_populates="simulations")
    results = relationship("Result", back_populates="simulation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Simulation(id={self.id}, name='{self.name}', status='{self.status}')>"


class Result(Base):
    """
    modelo para resultados detalhados de simulacoes
    
    armazena campos, metricas e pos-processamento
    """
    __tablename__ = "results"
    
    # campos principais
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"), nullable=False, index=True)
    
    # tipo de resultado
    result_type = Column(String(50), nullable=False, index=True)  
    # field, metric, validation, visualization
    
    # nome do campo ou metrica
    name = Column(String(255), nullable=False)
    
    # valor (para metricas escalares)
    value = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    
    # dados completos (para campos vetoriais, arrays, etc)
    data_json = Column(JSON, nullable=True)
    
    # arquivo associado
    file_path = Column(String(500), nullable=True)
    file_type = Column(String(50), nullable=True)  # vtk, csv, png, etc
    
    # metadados
    timestep = Column(Integer, nullable=True)  # para resultados transientes
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # relacionamentos
    simulation = relationship("Simulation", back_populates="results")
    
    def __repr__(self):
        return f"<Result(id={self.id}, type='{self.result_type}', name='{self.name}')>"


# indices adicionais para performance
from sqlalchemy import Index

# indices compostos para queries comuns
Index('ix_simulations_bed_status', Simulation.bed_id, Simulation.status)
Index('ix_results_simulation_type', Result.simulation_id, Result.result_type)

