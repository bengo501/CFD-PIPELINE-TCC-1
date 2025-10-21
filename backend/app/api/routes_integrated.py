"""
rotas integradas que combinam compilacao, geracao 3d, simulacao e banco de dados
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from typing import Optional

from backend.app.database.connection import get_db
from backend.app.api.models import (
    BedParameters,
    JobResponse, JobStatus, JobType,
    Job
)
from backend.app.services.bed_service import BedService
from backend.app.services.blender_service import BlenderService
from backend.app.services.openfoam_service import OpenFOAMService

from datetime import datetime
import uuid

router = APIRouter()

# armazenamento em memoria de jobs (compartilhado com routes.py)
jobs_store_integrated: dict[str, Job] = {}

# servicos
bed_service = BedService()
blender_service = BlenderService()
openfoam_service = OpenFOAMService()

import asyncio
import subprocess
from pathlib import Path


@router.post("/pipeline/create-bed", response_model=JobResponse, tags=["pipeline"])
async def create_bed_full(
    parameters: BedParameters,
    generate_model: bool = True,
    run_simulation: bool = False,
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    fluxo completo: compila .bed, salva no banco, opcionalmente gera modelo 3d e simulacao
    
    este endpoint:
    1. compila parametros para .bed e .bed.json
    2. salva leito no banco de dados postgresql
    3. opcionalmente gera modelo 3d no blender
    4. opcionalmente cria caso openfoam
    
    args:
        parameters: parametros do leito
        generate_model: gerar modelo 3d automaticamente
        run_simulation: criar simulacao openfoam automaticamente
        
    returns:
        job_id para monitorar progresso
    """
    # criar job
    job_id = str(uuid.uuid4())
    job = Job(
        job_id=job_id,
        job_type=JobType.COMPILE,
        status=JobStatus.QUEUED,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        metadata={
            "generate_model": generate_model,
            "run_simulation": run_simulation
        }
    )
    
    jobs_store_integrated[job_id] = job
    
    # adicionar tarefa em background
    if background_tasks:
        background_tasks.add_task(
            _execute_full_pipeline,
            job_id=job_id,
            parameters=parameters.model_dump(),
            generate_model=generate_model,
            run_simulation=run_simulation,
            db_session=db,
            jobs_store=jobs_store_integrated
        )
    
    return JobResponse(
        job_id=job_id,
        status=JobStatus.QUEUED,
        message="pipeline iniciado"
    )


async def _execute_full_pipeline(
    job_id: str,
    parameters: dict,
    generate_model: bool,
    run_simulation: bool,
    db_session: Session,
    jobs_store: dict
):
    """
    executa pipeline completo em background
    """
    job = jobs_store[job_id]
    
    try:
        # etapa 1: compilar .bed e salvar no banco
        job.status = JobStatus.RUNNING
        job.progress = 10
        job.updated_at = datetime.now()
        
        result = await bed_service.compile_bed(
            parameters=parameters,
            save_to_db=True,
            db_session=db_session
        )
        
        job.progress = 30
        job.updated_at = datetime.now()
        job.output_files.append(result["bed_file"])
        job.output_files.append(result["json_file"])
        job.metadata["bed_id"] = result.get("bed_id")
        job.metadata["json_file"] = result["json_file"]
        
        # etapa 2: gerar modelo 3d (opcional)
        if generate_model:
            job.progress = 40
            job.updated_at = datetime.now()
            
            # criar sub-job para blender
            blender_job_id = str(uuid.uuid4())
            blender_job = Job(
                job_id=blender_job_id,
                job_type=JobType.GENERATE_MODEL,
                status=JobStatus.QUEUED,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata={}
            )
            jobs_store[blender_job_id] = blender_job
            
            await blender_service.generate_model(
                job_id=blender_job_id,
                json_file=result["json_file"],
                open_blender=False,
                jobs_store=jobs_store,
                bed_id=result.get("bed_id"),
                db_session=db_session
            )
            
            # verificar se blender foi bem sucedido
            if blender_job.status == JobStatus.COMPLETED:
                job.progress = 70
                job.updated_at = datetime.now()
                job.output_files.extend(blender_job.output_files)
                job.metadata["blend_file"] = blender_job.metadata.get("blend_file")
                
                # etapa 3: criar simulacao openfoam (opcional)
                if run_simulation and blender_job.metadata.get("blend_file"):
                    job.progress = 75
                    job.updated_at = datetime.now()
                    
                    # criar sub-job para openfoam
                    openfoam_job_id = str(uuid.uuid4())
                    openfoam_job = Job(
                        job_id=openfoam_job_id,
                        job_type=JobType.SIMULATION,
                        status=JobStatus.QUEUED,
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        metadata={}
                    )
                    jobs_store[openfoam_job_id] = openfoam_job
                    
                    await openfoam_service.create_case(
                        job_id=openfoam_job_id,
                        json_file=result["json_file"],
                        blend_file=blender_job.metadata.get("blend_file"),
                        run_simulation=False,
                        jobs_store=jobs_store,
                        bed_id=result.get("bed_id"),
                        db_session=db_session
                    )
                    
                    if openfoam_job.status == JobStatus.COMPLETED:
                        job.output_files.extend(openfoam_job.output_files)
                        job.metadata["simulation_id"] = openfoam_job.metadata.get("simulation_id")
                        job.metadata["case_dir"] = openfoam_job.metadata.get("case_dir")
            else:
                raise Exception(f"erro na geracao do modelo: {blender_job.error_message}")
        
        # finalizar job
        job.status = JobStatus.COMPLETED
        job.progress = 100
        job.updated_at = datetime.now()
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.updated_at = datetime.now()


@router.get("/pipeline/job/{job_id}", response_model=Job, tags=["pipeline"])
async def get_pipeline_job(job_id: str):
    """
    busca status de job do pipeline integrado
    """
    if job_id not in jobs_store_integrated:
        raise HTTPException(status_code=404, detail="job nao encontrado")
    
    return jobs_store_integrated[job_id]


@router.post("/pipeline/full-simulation", response_model=JobResponse, tags=["pipeline"])
async def execute_full_pipeline_with_simulation(
    parameters: BedParameters,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    pipeline completo end-to-end com execucao da simulacao cfd no wsl
    
    este endpoint executa todas as etapas:
    1. compila parametros para .bed e .bed.json
    2. salva leito no banco de dados postgresql
    3. gera modelo 3d no blender com fisica
    4. cria caso openfoam completo
    5. executa simulacao cfd no wsl/ubuntu
    
    retorna job_id para acompanhamento do progresso
    
    tempo estimado: 10-45 minutos
    """
    # criar job
    job_id = str(uuid.uuid4())
    job = Job(
        job_id=job_id,
        job_type=JobType.FULL_PIPELINE,
        status=JobStatus.QUEUED,
        progress=0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        output_files=[],
        logs=[],
        metadata={}
    )
    
    jobs_store_integrated[job_id] = job
    
    # executar pipeline em background
    background_tasks.add_task(
        _execute_full_pipeline_with_simulation,
        job_id,
        parameters.dict(),
        db,
        jobs_store_integrated
    )
    
    return JobResponse(
        job_id=job_id,
        status=job.status,
        message="pipeline completo iniciado - acompanhe o progresso via /pipeline/job/{job_id}"
    )


async def _execute_full_pipeline_with_simulation(
    job_id: str,
    parameters: dict,
    db_session: Session,
    jobs_store: dict
):
    """
    executa pipeline completo com simulacao cfd em background
    
    etapas:
    1. compilacao .bed -> .json (0-15%)
    2. modelagem 3d blender com fisica (15-40%)
    3. criacao caso openfoam (40-50%)
    4. execucao simulacao cfd no wsl (50-100%)
    """
    job = jobs_store[job_id]
    
    try:
        # ===== etapa 1: compilar .bed (0-15%) =====
        job.status = JobStatus.RUNNING
        job.progress = 0
        job.logs.append(f"[{datetime.now()}] iniciando pipeline completo")
        job.logs.append(f"[{datetime.now()}] etapa 1/4: compilando arquivo .bed")
        job.updated_at = datetime.now()
        
        result = await bed_service.compile_bed(
            parameters=parameters,
            save_to_db=True,
            db_session=db_session
        )
        
        bed_file = result["bed_file"]
        json_file = result["json_file"]
        
        job.progress = 15
        job.output_files.append(bed_file)
        job.output_files.append(json_file)
        job.metadata["bed_id"] = result.get("bed_id")
        job.metadata["json_file"] = json_file
        job.metadata["bed_file"] = bed_file
        job.logs.append(f"[{datetime.now()}] ✓ arquivo .bed compilado: {bed_file}")
        job.logs.append(f"[{datetime.now()}] ✓ arquivo .json gerado: {json_file}")
        job.updated_at = datetime.now()
        
        # ===== etapa 2: gerar modelo 3d no blender (15-40%) =====
        job.progress = 15
        job.logs.append(f"[{datetime.now()}] etapa 2/4: gerando modelo 3d no blender")
        job.updated_at = datetime.now()
        
        # determinar formatos de exportacao
        export_formats = parameters.get("export", {}).get("formats", ["blend", "stl"])
        if "stl" not in export_formats:
            export_formats.append("stl")  # stl é obrigatório para cfd
        
        # gerar modelo no blender
        model_result = await blender_service.generate_model(
            json_file=json_file,
            export_formats=export_formats
        )
        
        blend_file = model_result.get("blend_file")
        stl_file = model_result.get("stl_file")
        
        job.progress = 40
        job.output_files.append(blend_file)
        if stl_file:
            job.output_files.append(stl_file)
        job.metadata["blend_file"] = blend_file
        job.metadata["stl_file"] = stl_file
        job.logs.append(f"[{datetime.now()}] ✓ modelo 3d gerado: {blend_file}")
        if stl_file:
            job.logs.append(f"[{datetime.now()}] ✓ arquivo stl exportado: {stl_file}")
        job.updated_at = datetime.now()
        
        # ===== etapa 3: criar caso openfoam (40-50%) =====
        job.progress = 40
        job.logs.append(f"[{datetime.now()}] etapa 3/4: criando caso openfoam")
        job.updated_at = datetime.now()
        
        case_dir = await _create_openfoam_case(json_file, blend_file, job, jobs_store)
        
        if not case_dir:
            raise Exception("falha na criacao do caso openfoam")
        
        job.progress = 50
        job.metadata["case_dir"] = case_dir
        job.logs.append(f"[{datetime.now()}] ✓ caso openfoam criado: {case_dir}")
        job.updated_at = datetime.now()
        
        # ===== etapa 4: executar simulacao cfd no wsl (50-100%) =====
        job.progress = 50
        job.logs.append(f"[{datetime.now()}] etapa 4/4: executando simulacao cfd no wsl")
        job.logs.append(f"[{datetime.now()}] ⚠️  este processo pode levar 10-30 minutos")
        job.updated_at = datetime.now()
        
        success = await _run_openfoam_simulation_wsl(case_dir, job, jobs_store)
        
        if not success:
            raise Exception("falha na execucao da simulacao cfd")
        
        # ===== finalizacao =====
        job.status = JobStatus.COMPLETED
        job.progress = 100
        job.logs.append(f"[{datetime.now()}] ✓ pipeline completo finalizado com sucesso!")
        job.logs.append(f"[{datetime.now()}] resultados disponiveis em: {case_dir}")
        job.logs.append(f"[{datetime.now()}] visualize no paraview: {case_dir}/caso.foam")
        job.updated_at = datetime.now()
        
    except Exception as e:
        job.status = JobStatus.FAILED
        job.error_message = str(e)
        job.logs.append(f"[{datetime.now()}] ✗ erro: {str(e)}")
        job.updated_at = datetime.now()
        import traceback
        job.logs.append(f"[{datetime.now()}] traceback: {traceback.format_exc()}")


async def _create_openfoam_case(json_file: str, blend_file: str, job: Job, jobs_store: dict) -> Optional[str]:
    """
    cria caso openfoam usando setup_openfoam_case.py
    
    returns:
        caminho do diretorio do caso ou None se falhar
    """
    try:
        import sys
        
        json_path = Path(json_file)
        blend_path = Path(blend_file)
        
        # diretorio de saida
        output_root = Path("output/cfd")
        output_root.mkdir(parents=True, exist_ok=True)
        
        # script de setup
        script_path = Path("scripts/openfoam_scripts/setup_openfoam_case.py")
        
        if not script_path.exists():
            job.logs.append(f"[{datetime.now()}] erro: script setup_openfoam_case.py nao encontrado")
            return None
        
        job.logs.append(f"[{datetime.now()}] executando setup_openfoam_case.py...")
        job.updated_at = datetime.now()
        
        # executar script
        process = await asyncio.create_subprocess_exec(
            sys.executable,
            str(script_path),
            str(json_path),
            str(blend_path),
            "--output-dir", str(output_root),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            # parsear output para logs
            for line in stdout.decode().split('\n'):
                if line.strip():
                    job.logs.append(f"[{datetime.now()}] {line}")
            
            # determinar diretorio do caso
            case_name = json_path.stem.replace('.bed', '')
            case_dir = output_root / case_name
            
            job.updated_at = datetime.now()
            return str(case_dir)
        else:
            job.logs.append(f"[{datetime.now()}] erro na criacao do caso openfoam")
            job.logs.append(f"[{datetime.now()}] codigo de erro: {process.returncode}")
            if stderr:
                for line in stderr.decode().split('\n'):
                    if line.strip():
                        job.logs.append(f"[{datetime.now()}] {line}")
            job.updated_at = datetime.now()
            return None
            
    except Exception as e:
        job.logs.append(f"[{datetime.now()}] erro inesperado ao criar caso openfoam: {str(e)}")
        job.updated_at = datetime.now()
        return None


async def _run_openfoam_simulation_wsl(case_dir: str, job: Job, jobs_store: dict) -> bool:
    """
    executa simulacao openfoam no wsl/ubuntu
    
    returns:
        True se sucesso, False se falhar
    """
    try:
        case_path = Path(case_dir)
        
        if not case_path.exists():
            job.logs.append(f"[{datetime.now()}] erro: diretorio do caso nao encontrado: {case_dir}")
            job.updated_at = datetime.now()
            return False
        
        # converter caminho windows para wsl
        # C:\Users\... -> /mnt/c/Users/...
        wsl_path = str(case_path).replace('\\', '/')
        if len(wsl_path) > 1 and wsl_path[1] == ':':
            drive = wsl_path[0].lower()
            wsl_path = f"/mnt/{drive}{wsl_path[2:]}"
        
        job.logs.append(f"[{datetime.now()}] caminho wsl: {wsl_path}")
        job.updated_at = datetime.now()
        
        # verificar wsl
        job.progress = 55
        job.logs.append(f"[{datetime.now()}] [1/4] verificando wsl...")
        job.updated_at = datetime.now()
        
        process = await asyncio.create_subprocess_exec(
            "wsl", "--list", "--quiet",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        
        if process.returncode != 0:
            job.logs.append(f"[{datetime.now()}] erro: wsl nao esta instalado ou configurado")
            job.updated_at = datetime.now()
            return False
        
        job.logs.append(f"[{datetime.now()}] ✓ wsl detectado")
        job.updated_at = datetime.now()
        
        # executar Allrun no wsl
        job.progress = 60
        job.logs.append(f"[{datetime.now()}] [2/4] executando ./Allrun no wsl...")
        job.logs.append(f"[{datetime.now()}] diretorio: {wsl_path}")
        job.updated_at = datetime.now()
        
        wsl_command = f"cd '{wsl_path}' && chmod +x Allrun && ./Allrun"
        
        # executar com captura de output
        process = await asyncio.create_subprocess_exec(
            "wsl", "bash", "-c", wsl_command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        
        # ler output em tempo real e atualizar progresso
        line_count = 0
        async for line in process.stdout:
            line_text = line.decode().strip()
            if line_text:
                job.logs.append(f"[{datetime.now()}] {line_text}")
                line_count += 1
                
                # atualizar progresso baseado em keywords
                if "blockMesh" in line_text:
                    job.progress = 70
                elif "snappyHexMesh" in line_text:
                    job.progress = 75
                elif "checkMesh" in line_text:
                    job.progress = 80
                elif "simpleFoam" in line_text or "icoFoam" in line_text:
                    job.progress = 85
                elif "SIMPLE solution converged" in line_text or "End" in line_text:
                    job.progress = 95
                
                # atualizar a cada 10 linhas para não sobrecarregar
                if line_count % 10 == 0:
                    job.updated_at = datetime.now()
        
        await process.wait()
        
        job.updated_at = datetime.now()
        
        if process.returncode == 0:
            job.progress = 95
            job.logs.append(f"[{datetime.now()}] [3/4] ✓ simulacao concluida com sucesso")
            job.updated_at = datetime.now()
            
            # criar arquivo .foam para paraview
            job.logs.append(f"[{datetime.now()}] [4/4] criando arquivo para paraview...")
            foam_file = case_path / "caso.foam"
            foam_file.touch()
            
            job.logs.append(f"[{datetime.now()}] ✓ arquivo paraview criado: {foam_file}")
            job.updated_at = datetime.now()
            
            return True
        else:
            job.logs.append(f"[{datetime.now()}] [3/4] erro: simulacao falhou com codigo {process.returncode}")
            job.logs.append(f"[{datetime.now()}] verifique os logs em: {case_dir}/log.*")
            job.updated_at = datetime.now()
            return False
            
    except FileNotFoundError:
        job.logs.append(f"[{datetime.now()}] erro: comando 'wsl' nao encontrado")
        job.logs.append(f"[{datetime.now()}] instale o wsl2 no windows")
        job.updated_at = datetime.now()
        return False
    except Exception as e:
        job.logs.append(f"[{datetime.now()}] erro inesperado: {str(e)}")
        job.updated_at = datetime.now()
        import traceback
        job.logs.append(f"[{datetime.now()}] traceback: {traceback.format_exc()}")
        return False

