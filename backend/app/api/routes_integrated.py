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

