"""
rotas da api rest integradas com postgresql
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path

from backend.app.database.connection import get_db
from backend.app.database import crud, schemas

router = APIRouter()


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

