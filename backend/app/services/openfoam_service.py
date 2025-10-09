"""
serviço para criação de simulações openfoam
"""
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from backend.app.api.models import JobStatus

class OpenFOAMService:
    """gerencia criação de casos openfoam"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.scripts_dir = self.project_root / "scripts" / "openfoam_scripts"
        self.setup_script = self.scripts_dir / "setup_openfoam_case.py"
        self.output_dir = self.project_root / "output" / "simulations"
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def check_availability(self) -> bool:
        """verifica se openfoam está disponível"""
        # verifica se script existe
        if not self.setup_script.exists():
            return False
        
        # em produção, verificar wsl/openfoam
        # por enquanto, apenas verifica script
        return True
    
    async def create_case(
        self,
        job_id: str,
        json_file: str,
        blend_file: str,
        run_simulation: bool,
        jobs_store: Dict[str, Any]
    ):
        """
        cria caso openfoam (executado em background)
        
        args:
            job_id: id do job
            json_file: caminho do arquivo json
            blend_file: caminho do arquivo blend
            run_simulation: executar simulação após criar
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
            blend_path = self.project_root / blend_file
            
            if not json_path.exists():
                raise FileNotFoundError(f"arquivo json não encontrado: {json_file}")
            
            if not blend_path.exists():
                raise FileNotFoundError(f"arquivo blend não encontrado: {blend_file}")
            
            # executar script de setup
            job.progress = 30
            job.updated_at = datetime.now()
            
            cmd = [
                sys.executable,
                str(self.setup_script),
                str(json_path),
                str(blend_path)
            ]
            
            if run_simulation:
                cmd.append("--run")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minutos
            )
            
            job.progress = 80
            job.updated_at = datetime.now()
            
            if result.returncode != 0:
                raise Exception(f"erro no openfoam: {result.stderr}")
            
            # extrair nome do caso do output (assumindo formato padrão)
            case_name = blend_path.stem  # nome do arquivo sem extensão
            case_dir = self.output_dir / case_name
            
            # atualizar job com sucesso
            job.status = JobStatus.COMPLETED
            job.progress = 100
            job.updated_at = datetime.now()
            job.output_files = [str(case_dir.relative_to(self.project_root))]
            job.metadata["case_dir"] = str(case_dir.relative_to(self.project_root))
            job.metadata["ran_simulation"] = run_simulation
            
        except subprocess.TimeoutExpired:
            job.status = JobStatus.FAILED
            job.error_message = "timeout na criação do caso (>10min)"
            job.updated_at = datetime.now()
            
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error_message = str(e)
            job.updated_at = datetime.now()

