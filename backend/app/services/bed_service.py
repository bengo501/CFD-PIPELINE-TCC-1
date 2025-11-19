"""
serviço para compilação de arquivos .bed
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

class BedService:
    """gerencia compilação de arquivos .bed"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.dsl_dir = self.project_root / "dsl"
        self.compiler_script = self.dsl_dir / "compiler" / "bed_compiler_antlr_standalone.py"
        self.output_dir = self.project_root / "output"
        
    def check_availability(self) -> bool:
        """verifica se compilador está disponível"""
        return self.compiler_script.exists()
    
    async def compile_bed(
        self,
        parameters: Dict[str, Any],
        filename: Optional[str] = None,
        save_to_db: bool = False,
        db_session = None
    ) -> Dict[str, Any]:
        """
        compila parâmetros em arquivo .bed e .bed.json
        
        args:
            parameters: dicionário com parâmetros do leito
            filename: nome do arquivo (opcional, gera automaticamente se None)
            save_to_db: salvar leito no banco de dados
            db_session: sessão do banco (necessário se save_to_db=True)
        
        returns:
            dict com caminhos dos arquivos gerados e opcionalmente bed_id
        """
        # gerar nome de arquivo se não fornecido
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"leito_{timestamp}"
        
        # garantir que não tem extensão
        filename = filename.replace(".bed", "").replace(".json", "")
        
        # criar arquivo .bed
        bed_content = self._generate_bed_content(parameters)
        bed_file = self.output_dir / f"{filename}.bed"
        
        bed_file.write_text(bed_content, encoding="utf-8")
        
        # compilar usando script existente
        json_file = await self._run_compiler(str(bed_file))
        
        result = {
            "bed_file": str(bed_file.relative_to(self.project_root)),
            "json_file": str(Path(json_file).relative_to(self.project_root))
        }
        
        # salvar no banco se solicitado (opcional - falha graciosamente se banco não disponível)
        if save_to_db and db_session:
            try:
                from backend.app.database import crud, schemas
                
                bed_data = schemas.BedCreate(
                    name=filename,
                    description=f"leito gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    diameter=parameters.get('bed', {}).get('diameter', 0.05) if isinstance(parameters.get('bed'), dict) else parameters.get('diameter', 0.05),
                    height=parameters.get('bed', {}).get('height', 0.1) if isinstance(parameters.get('bed'), dict) else parameters.get('height', 0.1),
                    wall_thickness=parameters.get('bed', {}).get('wall_thickness', 0.002) if isinstance(parameters.get('bed'), dict) else parameters.get('wall_thickness', 0.002),
                    particle_count=parameters.get('particles', {}).get('particle_count', 100) if isinstance(parameters.get('particles'), dict) else parameters.get('particle_count', 100),
                    particle_diameter=parameters.get('particles', {}).get('particle_diameter', 0.005) if isinstance(parameters.get('particles'), dict) else parameters.get('particle_diameter', 0.005),
                    particle_kind=parameters.get('particles', {}).get('particle_type', 'sphere') if isinstance(parameters.get('particles'), dict) else parameters.get('particle_type', 'sphere'),
                    packing_method=parameters.get('packing', {}).get('packing_method', 'rigid_body') if isinstance(parameters.get('packing'), dict) else parameters.get('packing_method', 'rigid_body'),
                    porosity=parameters.get('particles', {}).get('target_porosity') if isinstance(parameters.get('particles'), dict) else parameters.get('porosity'),
                    bed_file_path=result["bed_file"],
                    json_file_path=result["json_file"],
                    parameters_json=parameters,
                    created_by='api'
                )
                
                db_bed = crud.BedCRUD.create(db_session, bed_data)
                result["bed_id"] = db_bed.id
            except Exception as db_error:
                # Falha graciosamente - banco não é obrigatório para compilação
                # Log do erro mas continua o processo
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Falha ao salvar no banco de dados (continuando sem salvar): {str(db_error)}")
                # Não adiciona bed_id ao resultado, mas continua normalmente
        
        return result
    
    def _generate_bed_content(self, params: Dict[str, Any]) -> str:
        """gera conteúdo do arquivo .bed"""
        # extrair parâmetros da estrutura aninhada
        bed_params = params.get('bed', {})
        lids_params = params.get('lids', {})
        particles_params = params.get('particles', {})
        packing_params = params.get('packing', {})
        
        content = f"""bed {{
    diameter = {bed_params.get('diameter', 0.05)} m;
    height = {bed_params.get('height', 0.1)} m;
    wall_thickness = {bed_params.get('wall_thickness', 0.002)} m;
    clearance = {bed_params.get('clearance', 0.01)} m;
    material = "{bed_params.get('material', 'steel')}";
    roughness = {bed_params.get('roughness', 0.0)} m;
}}

lids {{
    top_type = "{lids_params.get('top_type', 'flat')}";
    bottom_type = "{lids_params.get('bottom_type', 'flat')}";
    top_thickness = {lids_params.get('top_thickness', 0.003)} m;
    bottom_thickness = {lids_params.get('bottom_thickness', 0.003)} m;
    seal_clearance = {lids_params.get('seal_clearance', 0.001)} m;
}}

particles {{
    kind = "{particles_params.get('kind', 'sphere')}";
    diameter = {particles_params.get('diameter', 0.005)} m;
    count = {particles_params.get('count', 100)};
    target_porosity = {particles_params.get('target_porosity', 0.4)};
    density = {particles_params.get('density', 2500.0)} kg/m3;
    mass = {particles_params.get('mass', 0.0)} g;
    restitution = {particles_params.get('restitution', 0.3)};
    friction = {particles_params.get('friction', 0.5)};
    rolling_friction = {particles_params.get('rolling_friction', 0.1)};
    linear_damping = {particles_params.get('linear_damping', 0.1)};
    angular_damping = {particles_params.get('angular_damping', 0.1)};
    seed = {particles_params.get('seed', 42)};
}}

packing {{
    method = "{packing_params.get('method', 'rigid_body')}";
    gravity = {packing_params.get('gravity', -9.81)} m/s2;
    substeps = {packing_params.get('substeps', 10)};
    iterations = {packing_params.get('iterations', 10)};
    damping = {packing_params.get('damping', 0.1)};
    rest_velocity = {packing_params.get('rest_velocity', 0.01)} m/s;
    max_time = {packing_params.get('max_time', 5.0)} s;
    collision_margin = {packing_params.get('collision_margin', 0.001)} m;
}}

export {{
    formats = ["stl_binary", "blend"];
    units = "m";
    scale = 1.0;
    wall_mode = "surface";
    fluid_mode = "none";
    manifold_check = true;
    merge_distance = 0.001 m;
}}
"""
        
        # adicionar seção cfd se parâmetros fornecidos
        if 'cfd_regime' in params:
            content += f"""
cfd {{
    regime = "{params['cfd_regime']}";
    inlet_velocity = {params.get('inlet_velocity', 0.01)} m/s;
    fluid_density = {params.get('fluid_density', 1000.0)} kg/m3;
    fluid_viscosity = {params.get('fluid_viscosity', 0.001)} Pa.s;
}}
"""
        
        return content
    
    async def _run_compiler(self, bed_file: str) -> str:
        """executa compilador antlr"""
        try:
            # arquivo json gerado tem mesmo nome + .json
            json_file = f"{bed_file}.json"
            
            # executar compilador com parâmetro -o para especificar saída
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.compiler_script),
                    bed_file,
                    "-o", json_file,
                    "-v"  # modo verbose para debug
                ],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(self.dsl_dir)
            )
            
            if result.returncode != 0:
                error_msg = result.stderr if result.stderr else result.stdout
                raise Exception(f"erro na compilação: {error_msg}")
            
            # verificar se arquivo foi gerado
            json_path = Path(json_file)
            if not json_path.exists():
                # tentar caminho absoluto
                json_path = Path(bed_file).parent / Path(json_file).name
                if not json_path.exists():
                    raise Exception(f"arquivo json não foi gerado. stdout: {result.stdout}, stderr: {result.stderr}")
                json_file = str(json_path)
            
            return json_file
            
        except subprocess.TimeoutExpired:
            raise Exception("timeout na compilação (>30s)")
        except Exception as e:
            raise Exception(f"erro ao executar compilador: {str(e)}")
    
    async def validate_bed(self, filename: str) -> Dict[str, Any]:
        """valida arquivo .bed existente"""
        bed_file = self.output_dir / filename
        
        if not bed_file.exists():
            raise FileNotFoundError(f"arquivo {filename} não encontrado")
        
        try:
            # tentar compilar para validar sintaxe
            json_file = await self._run_compiler(str(bed_file))
            
            return {
                "valid": True,
                "bed_file": str(bed_file.relative_to(self.project_root)),
                "json_file": str(Path(json_file).relative_to(self.project_root)),
                "message": "arquivo válido"
            }
            
        except Exception as e:
            return {
                "valid": False,
                "bed_file": str(bed_file.relative_to(self.project_root)),
                "message": str(e)
            }

