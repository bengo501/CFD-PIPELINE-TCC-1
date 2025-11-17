"""
serviço para geração de modelos 3d no blender
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from backend.app.api.models import JobStatus

class BlenderService:
    """gerencia geração de modelos 3d no blender"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.scripts_dir = self.project_root / "scripts" / "blender_scripts"
        self.leito_script = self.scripts_dir / "leito_extracao.py"
        self.output_dir = self.project_root / "generated" / "3d" / "output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # detectar blender
        self.blender_exe = self._find_blender()
    
    def _find_blender(self) -> str:
        """encontra executável do blender"""
        import platform
        
        system = platform.system()
        
        # caminhos comuns
        if system == "Windows":
            common_paths = [
                r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            ]
        elif system == "Linux":
            common_paths = [
                "/usr/bin/blender",
                "/usr/local/bin/blender",
            ]
        else:  # macOS
            common_paths = [
                "/Applications/Blender.app/Contents/MacOS/Blender",
            ]
        
        for path in common_paths:
            if Path(path).exists():
                return path
        
        # tentar comando simples
        return "blender"
    
    def check_availability(self) -> bool:
        """verifica se blender está disponível"""
        try:
            result = subprocess.run(
                [self.blender_exe, "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    async def generate_model(
        self,
        job_id: str,
        json_file: str,
        open_blender: bool,
        jobs_store: Dict[str, Any],
        bed_id: Optional[int] = None,
        db_session = None
    ):
        """
        gera modelo 3d (executado em background)
        
        args:
            job_id: id do job
            json_file: caminho do arquivo json
            open_blender: abrir blender gui após gerar
            jobs_store: armazenamento de jobs
        """
        job = jobs_store[job_id]
        
        try:
            # atualizar status
            job.status = JobStatus.RUNNING
            job.progress = 10
            job.updated_at = datetime.now()
            
            # preparar caminhos
            json_path = self.project_root / json_file
            
            if not json_path.exists():
                raise FileNotFoundError(f"arquivo json não encontrado: {json_file}")
            
            # gerar nome do arquivo .blend
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            blend_filename = f"leito_{timestamp}.blend"
            blend_path = self.output_dir / blend_filename
            
            # executar blender headless
            job.progress = 30
            job.updated_at = datetime.now()
            
            cmd = [
                self.blender_exe,
                "--background",
                "--python", str(self.leito_script),
                "--",
                "--params", str(json_path),
                "--output", str(blend_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutos
            )
            
            job.progress = 80
            job.updated_at = datetime.now()
            
            if result.returncode != 0:
                raise Exception(f"erro no blender: {result.stderr}")
            
            # verificar se arquivo foi gerado
            if not blend_path.exists():
                raise Exception("arquivo .blend não foi gerado")
            
            # atualizar job com sucesso
            job.status = JobStatus.COMPLETED
            job.progress = 100
            job.updated_at = datetime.now()
            job.output_files = [str(blend_path.relative_to(self.project_root))]
            job.metadata["blend_file"] = str(blend_path.relative_to(self.project_root))
            
            # atualizar bed no banco se fornecido
            if bed_id and db_session:
                from backend.app.database import crud, schemas
                
                update_data = schemas.BedUpdate(
                    blend_file_path=str(blend_path.relative_to(self.project_root))
                )
                crud.BedCRUD.update(db_session, bed_id, update_data)
            
            # abrir blender gui se solicitado
            if open_blender and blend_path.exists():
                subprocess.Popen([self.blender_exe, str(blend_path)])
            
        except subprocess.TimeoutExpired:
            job.status = JobStatus.FAILED
            job.error_message = "timeout na geração do modelo (>5min)"
            job.updated_at = datetime.now()
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.updated_at = datetime.now()

