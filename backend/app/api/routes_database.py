"""
rotas da api rest integradas com postgresql
"""
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path

from backend.app.database.connection import get_db, DATABASE_URL
from backend.app.database import crud, schemas, models
from backend.app.api.models import (
    AdminPanelEventCreate,
    DatabasePanelCounts,
    DatabasePanelEventOut,
    DatabasePanelResponse,
)
from backend.app.services.results_service import ResultsService

router = APIRouter()
results_service = ResultsService()


# ==================== ENDPOINTS BEDS ====================

@router.post("/beds", response_model=schemas.BedResponse, tags=["database", "beds"])
async def create_bed(bed: schemas.BedCreate, db: Session = Depends(get_db)):
    """
    criar novo leito no banco de dados
    """
    # verificar se ja existe leito com esse nome
    existing = crud.BedCRUD.get_by_name(db, bed.name)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"leito com nome '{bed.name}' ja existe"
        )
    
    try:
        db_bed = crud.BedCRUD.create(db, bed)
        return db_bed
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao criar leito: {str(e)}")


@router.get("/beds", response_model=schemas.BedListResponse, tags=["database", "beds"])
async def list_beds(
    page: int = Query(1, ge=1, description="numero da pagina"),
    per_page: int = Query(50, ge=1, le=100, description="items por pagina"),
    search: Optional[str] = Query(None, description="buscar por nome ou descricao"),
    db: Session = Depends(get_db)
):
    """
    listar leitos com paginacao e busca opcional
    """
    try:
        skip, limit, _ = crud.paginate(0, page, per_page)
        
        if search:
            beds, total = crud.BedCRUD.search(db, search, skip, limit)
        else:
            beds, total = crud.BedCRUD.get_all(db, skip, limit)
        
        import math
        pages = math.ceil(total / per_page) if total > 0 else 1
        
        return schemas.BedListResponse(
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
            items=beds
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao listar leitos: {str(e)}")


@router.get("/beds/{bed_id}", response_model=schemas.BedResponse, tags=["database", "beds"])
async def get_bed(bed_id: int, db: Session = Depends(get_db)):
    """
    obter detalhes de um leito especifico
    """
    db_bed = crud.BedCRUD.get(db, bed_id)
    if not db_bed:
        raise HTTPException(status_code=404, detail="leito nao encontrado")
    return db_bed


@router.patch("/beds/{bed_id}", response_model=schemas.BedResponse, tags=["database", "beds"])
async def update_bed(
    bed_id: int,
    bed_update: schemas.BedUpdate,
    db: Session = Depends(get_db)
):
    """
    atualizar leito (parcial)
    """
    db_bed = crud.BedCRUD.update(db, bed_id, bed_update)
    if not db_bed:
        raise HTTPException(status_code=404, detail="leito nao encontrado")
    return db_bed


@router.delete("/beds/{bed_id}", tags=["database", "beds"])
async def delete_bed(bed_id: int, db: Session = Depends(get_db)):
    """
    deletar leito (e todas simulacoes relacionadas em cascade)
    """
    success = crud.BedCRUD.delete(db, bed_id)
    if not success:
        raise HTTPException(status_code=404, detail="leito nao encontrado")
    return {"message": "leito deletado com sucesso", "bed_id": bed_id}


# ==================== ENDPOINTS SIMULATIONS ====================

@router.post("/simulations", response_model=schemas.SimulationResponse, tags=["database", "simulations"])
async def create_simulation(
    simulation: schemas.SimulationCreate,
    db: Session = Depends(get_db)
):
    """
    criar nova simulacao no banco de dados
    """
    # verificar se bed existe
    bed = crud.BedCRUD.get(db, simulation.bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail=f"leito {simulation.bed_id} nao encontrado")
    
    try:
        db_simulation = crud.SimulationCRUD.create(db, simulation)
        return db_simulation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao criar simulacao: {str(e)}")


@router.get("/simulations", response_model=schemas.SimulationListResponse, tags=["database", "simulations"])
async def list_simulations(
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    bed_id: Optional[int] = Query(None, description="filtrar por leito"),
    status: Optional[str] = Query(None, description="filtrar por status"),
    db: Session = Depends(get_db)
):
    """
    listar simulacoes com paginacao e filtros
    """
    try:
        skip, limit, _ = crud.paginate(0, page, per_page)
        
        if bed_id:
            simulations, total = crud.SimulationCRUD.get_by_bed(db, bed_id, skip, limit)
        elif status:
            simulations, total = crud.SimulationCRUD.get_by_status(db, status, skip, limit)
        else:
            simulations, total = crud.SimulationCRUD.get_all(db, skip, limit)
        
        import math
        pages = math.ceil(total / per_page) if total > 0 else 1
        
        return schemas.SimulationListResponse(
            total=total,
            page=page,
            per_page=per_page,
            pages=pages,
            items=simulations
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao listar simulacoes: {str(e)}")


@router.get("/simulations/{simulation_id}", response_model=schemas.SimulationResponse, tags=["database", "simulations"])
async def get_simulation(simulation_id: int, db: Session = Depends(get_db)):
    """
    obter detalhes de uma simulacao especifica
    """
    db_simulation = crud.SimulationCRUD.get(db, simulation_id)
    if not db_simulation:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    return db_simulation


@router.patch("/simulations/{simulation_id}", response_model=schemas.SimulationResponse, tags=["database", "simulations"])
async def update_simulation(
    simulation_id: int,
    simulation_update: schemas.SimulationUpdate,
    db: Session = Depends(get_db)
):
    """
    atualizar simulacao (ex: status, progress, metricas)
    """
    db_simulation = crud.SimulationCRUD.update(db, simulation_id, simulation_update)
    if not db_simulation:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    return db_simulation


@router.delete("/simulations/{simulation_id}", tags=["database", "simulations"])
async def delete_simulation(simulation_id: int, db: Session = Depends(get_db)):
    """
    deletar simulacao (e todos resultados relacionados em cascade)
    """
    success = crud.SimulationCRUD.delete(db, simulation_id)
    if not success:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    return {"message": "simulacao deletada com sucesso", "simulation_id": simulation_id}


# ==================== ENDPOINTS RESULTS ====================

@router.post("/results", response_model=schemas.ResultResponse, tags=["database", "results"])
async def create_result(result: schemas.ResultCreate, db: Session = Depends(get_db)):
    """
    criar novo resultado
    """
    # verificar se simulacao existe
    simulation = crud.SimulationCRUD.get(db, result.simulation_id)
    if not simulation:
        raise HTTPException(
            status_code=404,
            detail=f"simulacao {result.simulation_id} nao encontrada"
        )
    
    try:
        db_result = crud.ResultCRUD.create(db, result)
        return db_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao criar resultado: {str(e)}")


@router.post("/results/bulk", response_model=List[schemas.ResultResponse], tags=["database", "results"])
async def create_results_bulk(
    results: List[schemas.ResultCreate],
    db: Session = Depends(get_db)
):
    """
    criar multiplos resultados em batch (para pos-processamento)
    """
    try:
        db_results = crud.ResultCRUD.create_bulk(db, results)
        return db_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao criar resultados: {str(e)}")


@router.get("/results/simulation/{simulation_id}", response_model=List[schemas.ResultResponse], tags=["database", "results"])
async def get_simulation_results(
    simulation_id: int,
    result_type: Optional[str] = Query(None, description="filtrar por tipo"),
    db: Session = Depends(get_db)
):
    """
    listar resultados de uma simulacao especifica
    """
    # verificar se simulacao existe
    simulation = crud.SimulationCRUD.get(db, simulation_id)
    if not simulation:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")
    
    results = crud.ResultCRUD.get_by_simulation(db, simulation_id, result_type)
    return results


@router.get("/results/{result_id}", response_model=schemas.ResultResponse, tags=["database", "results"])
async def get_result(result_id: int, db: Session = Depends(get_db)):
    """
    obter resultado especifico
    """
    db_result = crud.ResultCRUD.get(db, result_id)
    if not db_result:
        raise HTTPException(status_code=404, detail="resultado nao encontrado")
    return db_result


# ==================== ENDPOINTS DE INGESTAO E RESUMOS PARA DASHBOARD ====================

@router.post(
    "/simulations/{simulation_id}/ingest-results",
    response_model=schemas.SimulationResponse,
    tags=["database", "simulations"],
)
async def ingest_results_for_simulation(
    simulation_id: int,
    db: Session = Depends(get_db),
):
    """
    ler generated/cfd/NOME_CASO/results.json e atualizar Simulation/Result.

    este endpoint pode ser chamado apos a simulacao openfoam concluir.
    """
    sim = crud.SimulationCRUD.get(db, simulation_id)
    if not sim:
        raise HTTPException(status_code=404, detail="simulacao nao encontrada")

    try:
        updated = results_service.ingest_simulation_results(db, simulation_id)
        if not updated:
            raise HTTPException(status_code=404, detail="simulacao nao encontrada")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao ingerir resultados: {str(e)}")


@router.get(
    "/simulations/summary",
    tags=["database", "simulations"],
)
async def get_simulations_summary(db: Session = Depends(get_db)):
    """
    resumo agregado de simulacoes para o dashboard.

    retorna contagens por status, taxa de sucesso e medias basicas
    de algumas metricas (pressure_drop, reynolds_number).
    """
    sims: list[models.Simulation] = db.query(models.Simulation).all()
    total = len(sims)
    by_status = {
        "pending": 0,
        "running": 0,
        "completed": 0,
        "failed": 0,
    }

    pressures: list[float] = []
    reynolds: list[float] = []

    for s in sims:
        if s.status in by_status:
            by_status[s.status] += 1
        if s.pressure_drop is not None:
            pressures.append(s.pressure_drop)
        if s.reynolds_number is not None:
            reynolds.append(s.reynolds_number)

    completed = by_status["completed"]
    success_rate = (completed / total * 100.0) if total > 0 else 0.0

    avg_pressure = sum(pressures) / len(pressures) if pressures else None
    avg_reynolds = sum(reynolds) / len(reynolds) if reynolds else None

    return {
        "total": total,
        "by_status": by_status,
        "success_rate": success_rate,
        "average_pressure_drop": avg_pressure,
        "average_reynolds_number": avg_reynolds,
    }


@router.get(
    "/simulations/recent",
    response_model=schemas.SimulationListResponse,
    tags=["database", "simulations"],
)
async def list_recent_simulations(
    limit: int = Query(8, ge=1, le=100, description="numero maximo de simulacoes"),
    db: Session = Depends(get_db),
):
    """
    listar as simulacoes mais recentes (para o dashboard).
    """
    try:
        sims_query = db.query(models.Simulation).order_by(
            models.Simulation.created_at.desc()
        )
        simulations = sims_query.limit(limit).all()
        total = sims_query.count()
        # reusar schema de lista com uma 'pagina' unica
        return schemas.SimulationListResponse(
            total=total,
            page=1,
            per_page=limit,
            pages=1,
            items=simulations,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"erro ao listar simulacoes recentes: {str(e)}")


@router.delete("/results/{result_id}", tags=["database", "results"])
async def delete_result(result_id: int, db: Session = Depends(get_db)):
    """
    deletar resultado
    """
    success = crud.ResultCRUD.delete(db, result_id)
    if not success:
        raise HTTPException(status_code=404, detail="resultado nao encontrado")
    return {"message": "resultado deletado com sucesso", "result_id": result_id}


# ==================== ENDPOINTS COMPOSTOS ====================

@router.get("/beds/{bed_id}/simulations", response_model=schemas.SimulationListResponse, tags=["database", "beds"])
async def get_bed_simulations(
    bed_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    listar todas simulacoes de um leito especifico
    """
    # verificar se bed existe
    bed = crud.BedCRUD.get(db, bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="leito nao encontrado")
    
    skip, limit, _ = crud.paginate(0, page, per_page)
    simulations, total = crud.SimulationCRUD.get_by_bed(db, bed_id, skip, limit)
    
    import math
    pages = math.ceil(total / per_page) if total > 0 else 1
    
    return schemas.SimulationListResponse(
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
        items=simulations
    )


@router.get("/beds/{bed_id}/summary", tags=["database", "beds"])
async def get_bed_summary(bed_id: int, db: Session = Depends(get_db)):
    """
    obter resumo de um leito (com estatisticas de simulacoes)
    """
    bed = crud.BedCRUD.get(db, bed_id)
    if not bed:
        raise HTTPException(status_code=404, detail="leito nao encontrado")
    
    # contar simulacoes por status
    from sqlalchemy import func
    from backend.app.database.models import Simulation
    
    stats = db.query(
        Simulation.status,
        func.count(Simulation.id)
    ).filter(
        Simulation.bed_id == bed_id
    ).group_by(Simulation.status).all()
    
    status_counts = {status: count for status, count in stats}
    
    # calcular metricas medias das simulacoes completadas
    from sqlalchemy import func as sql_func
    avg_metrics = db.query(
        sql_func.avg(Simulation.pressure_drop).label('avg_pressure_drop'),
        sql_func.avg(Simulation.average_velocity).label('avg_velocity'),
        sql_func.avg(Simulation.reynolds_number).label('avg_reynolds'),
        sql_func.avg(Simulation.execution_time).label('avg_execution_time')
    ).filter(
        Simulation.bed_id == bed_id,
        Simulation.status == 'completed'
    ).first()
    
    return {
        "bed": schemas.BedResponse.from_orm(bed),
        "simulations_count": sum(status_counts.values()),
        "simulations_by_status": status_counts,
        "average_metrics": {
            "pressure_drop": avg_metrics.avg_pressure_drop,
            "velocity": avg_metrics.avg_velocity,
            "reynolds_number": avg_metrics.avg_reynolds,
            "execution_time": avg_metrics.avg_execution_time
        }
    }


@router.get("/stats/overview", tags=["database", "stats"])
async def get_overview_stats(db: Session = Depends(get_db)):
    """
    obter estatisticas gerais do sistema
    """
    from sqlalchemy import func
    from backend.app.database.models import Bed, Simulation, Result
    
    total_beds = db.query(func.count(Bed.id)).scalar()
    total_simulations = db.query(func.count(Simulation.id)).scalar()
    total_results = db.query(func.count(Result.id)).scalar()
    
    # simulacoes por status
    sim_stats = db.query(
        Simulation.status,
        func.count(Simulation.id)
    ).group_by(Simulation.status).all()
    
    simulations_by_status = {status: count for status, count in sim_stats}
    
    # ultimas simulacoes
    recent_simulations = db.query(Simulation).order_by(
        Simulation.created_at.desc()
    ).limit(5).all()
    
    return {
        "total_beds": total_beds,
        "total_simulations": total_simulations,
        "total_results": total_results,
        "simulations_by_status": simulations_by_status,
        "recent_simulations": [schemas.SimulationResponse.from_orm(s) for s in recent_simulations]
    }


def _describe_database_url(url: str) -> tuple[str, str]:
    u = (url or "").lower()
    if "sqlite" in u:
        return "sqlite", "sqlite · ficheiro local"
    if "postgres" in u:
        return "postgresql", "postgresql · servidor"
    return "other", "motor sql (ver DATABASE_URL)"


def _dt_iso(v) -> str:
    if v is None:
        return ""
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return str(v)


@router.get(
    "/database/panel",
    response_model=DatabasePanelResponse,
    tags=["database", "admin"],
)
async def get_database_panel(db: Session = Depends(get_db)):
    """
    dados agregados para a página "banco de dados" no frontend:
    motor sql (sem expor credenciais), contagens de tabelas e últimos eventos do painel.
    """
    backend, display = _describe_database_url(DATABASE_URL)
    now = datetime.now(timezone.utc).isoformat()
    integrations = {
        "redis": "não integrado à api",
        "object_storage": "não integrado à api",
    }

    try:
        beds = db.query(func.count(models.Bed.id)).scalar() or 0
        sims = db.query(func.count(models.Simulation.id)).scalar() or 0
        res = db.query(func.count(models.Result.id)).scalar() or 0
        tmpl = db.query(func.count(models.BedTemplate.id)).scalar() or 0

        ev_rows = (
            db.query(models.AdminPanelEvent)
            .order_by(models.AdminPanelEvent.created_at.desc())
            .limit(20)
            .all()
        )
        events = [
            DatabasePanelEventOut(
                id=e.id,
                event_type=e.event_type,
                detail=e.detail,
                created_at=_dt_iso(e.created_at),
            )
            for e in ev_rows
        ]

        return DatabasePanelResponse(
            connected=True,
            backend=backend,
            database_display=display,
            counts=DatabasePanelCounts(
                beds=beds,
                simulations=sims,
                results=res,
                bed_templates=tmpl,
            ),
            integrations=integrations,
            recent_events=events,
            checked_at=now,
            error=None,
        )
    except Exception as e:
        return DatabasePanelResponse(
            connected=False,
            backend=backend,
            database_display=display,
            counts=DatabasePanelCounts(
                beds=0,
                simulations=0,
                results=0,
                bed_templates=0,
            ),
            integrations=integrations,
            recent_events=[],
            checked_at=now,
            error=str(e),
        )


@router.post("/database/events", tags=["database", "admin"])
async def log_database_panel_event(
    body: AdminPanelEventCreate,
    db: Session = Depends(get_db),
):
    """
    regista um pedido do painel (backup manual ou teste de ligação) na tabela admin_panel_events.
    """
    row = models.AdminPanelEvent(
        event_type=body.event_type,
        detail=body.detail,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "event_type": row.event_type,
        "created_at": _dt_iso(row.created_at),
    }

