"""
rotas da api para simulacoes cfd openfoam
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict
from pathlib import Path
import subprocess
import json
import uuid
from datetime import datetime

router = APIRouter()

# armazenar status das simulacoes em memoria
# em producao, usar redis ou banco de dados
simulations_status: Dict[str, dict] = {}


class CFDRequest(BaseModel):
    bed_json_path: str
    blend_file_path: str
    output_dir: Optional[str] = None
    run_simulation: bool = True


class CFDStatus(BaseModel):
    simulation_id: str
    status: str  # 'queued', 'preparing', 'meshing', 'running', 'completed', 'error'
    progress: int  # 0-100
    message: str
    created_at: str
    completed_at: Optional[str] = None
    case_dir: Optional[str] = None
    error: Optional[str] = None


@router.post("/cfd/create")
async def create_cfd_case(request: CFDRequest, background_tasks: BackgroundTasks):
    """
    criar caso openfoam e opcionalmente executar simulacao
    """
    try:
        # gerar id unico para simulacao
        simulation_id = str(uuid.uuid4())[:8]
        
        # definir caminhos
        project_root = Path(__file__).parent.parent.parent.parent
        script_path = project_root / "scripts" / "openfoam_scripts" / "setup_openfoam_case.py"
        
        # verificar se arquivos existem
        bed_json = project_root / request.bed_json_path
        blend_file = project_root / request.blend_file_path
        
        if not bed_json.exists():
            raise HTTPException(status_code=404, detail=f"arquivo json nao encontrado: {bed_json}")
        
        if not blend_file.exists():
            raise HTTPException(status_code=404, detail=f"arquivo blend nao encontrado: {blend_file}")
        
        # definir diretorio de saida
        if request.output_dir:
            output_dir = project_root / request.output_dir
        else:
            output_dir = project_root / "output" / "cfd" / f"sim_{simulation_id}"
        
        # criar entrada de status
        simulations_status[simulation_id] = {
            "simulation_id": simulation_id,
            "status": "queued",
            "progress": 0,
            "message": "simulacao na fila",
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
            "case_dir": str(output_dir),
            "error": None,
            "bed_json": str(bed_json),
            "blend_file": str(blend_file)
        }
        
        # executar em background
        background_tasks.add_task(
            run_cfd_simulation,
            simulation_id,
            script_path,
            bed_json,
            blend_file,
            output_dir,
            request.run_simulation
        )
        
        return {
            "success": True,
            "simulation_id": simulation_id,
            "message": "simulacao criada com sucesso",
            "status_url": f"/api/cfd/status/{simulation_id}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao criar caso cfd: {str(e)}")


@router.get("/cfd/status/{simulation_id}")
async def get_cfd_status(simulation_id: str):
    """
    obter status de uma simulacao
    """
    if simulation_id not in simulations_status:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    
    return simulations_status[simulation_id]


@router.get("/cfd/list")
async def list_cfd_simulations():
    """
    listar todas as simulacoes
    """
    return {
        "simulations": list(simulations_status.values()),
        "count": len(simulations_status)
    }


@router.delete("/cfd/{simulation_id}")
async def delete_cfd_simulation(simulation_id: str):
    """
    deletar simulacao (apenas status, nao deleta arquivos)
    """
    if simulation_id not in simulations_status:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    
    del simulations_status[simulation_id]
    
    return {
        "success": True,
        "message": "simulacao deletada"
    }


async def run_cfd_simulation(
    simulation_id: str,
    script_path: Path,
    bed_json: Path,
    blend_file: Path,
    output_dir: Path,
    run_simulation: bool
):
    """
    executar simulacao cfd em background
    """
    import sys
    
    try:
        # atualizar status: preparando
        simulations_status[simulation_id].update({
            "status": "preparing",
            "progress": 10,
            "message": "preparando caso openfoam..."
        })
        
        # construir comando
        cmd = [
            sys.executable,
            str(script_path),
            str(bed_json),
            str(blend_file),
            "--output-dir", str(output_dir)
        ]
        
        if run_simulation:
            cmd.append("--run")
        
        # executar script de setup
        simulations_status[simulation_id].update({
            "status": "meshing",
            "progress": 30,
            "message": "criando caso e gerando malha..."
        })
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutos timeout
        )
        
        if result.returncode != 0:
            simulations_status[simulation_id].update({
                "status": "error",
                "progress": 0,
                "message": "erro ao criar caso openfoam",
                "error": result.stderr,
                "completed_at": datetime.now().isoformat()
            })
            return
        
        # caso criado com sucesso
        if run_simulation:
            simulations_status[simulation_id].update({
                "status": "running",
                "progress": 60,
                "message": "executando simulacao cfd..."
            })
            
            # monitorar simulacao (simulado - em producao ler log)
            # aqui poderiamos ler o log.simpleFoam e atualizar progresso real
            
            simulations_status[simulation_id].update({
                "status": "completed",
                "progress": 100,
                "message": "simulacao concluida com sucesso!",
                "completed_at": datetime.now().isoformat()
            })
        else:
            simulations_status[simulation_id].update({
                "status": "completed",
                "progress": 100,
                "message": "caso openfoam criado (simulacao nao executada)",
                "completed_at": datetime.now().isoformat()
            })
            
    except subprocess.TimeoutExpired:
        simulations_status[simulation_id].update({
            "status": "error",
            "progress": 0,
            "message": "timeout na criacao do caso",
            "error": "execucao excedeu 10 minutos",
            "completed_at": datetime.now().isoformat()
        })
    except Exception as e:
        simulations_status[simulation_id].update({
            "status": "error",
            "progress": 0,
            "message": "erro inesperado",
            "error": str(e),
            "completed_at": datetime.now().isoformat()
        })


@router.post("/cfd/run-from-wizard")
async def run_cfd_from_wizard(
    background_tasks: BackgroundTasks,
    fileName: str,
    runSimulation: bool = True
):
    """
    executar cfd a partir de arquivo gerado pelo wizard
    busca automaticamente os arquivos .bed.json e .blend
    """
    try:
        project_root = Path(__file__).parent.parent.parent.parent
        
        # obter nome base do arquivo (sem extensao)
        file_base = fileName.replace('.bed', '')
        
        # buscar arquivos
        bed_json = project_root / "output" / f"{file_base}.bed.json"
        blend_file = project_root / "output" / "models" / f"{file_base}.blend"
        
        # verificar se existem
        if not bed_json.exists():
            raise HTTPException(
                status_code=404,
                detail=f"arquivo json nao encontrado. compile o .bed primeiro"
            )
        
        if not blend_file.exists():
            raise HTTPException(
                status_code=404,
                detail=f"modelo 3d nao encontrado. gere o modelo no blender primeiro"
            )
        
        # criar requisicao cfd
        request = CFDRequest(
            bed_json_path=str(bed_json.relative_to(project_root)),
            blend_file_path=str(blend_file.relative_to(project_root)),
            run_simulation=runSimulation
        )
        
        # criar simulacao
        return await create_cfd_case(request, background_tasks)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro: {str(e)}")

