# operacoes crud (create, read, update, delete) para banco de dados
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Tuple
from . import models, schemas
import math


class BedCRUD:
    """operacoes crud para leitos"""
    
    @staticmethod
    def create(db: Session, bed: schemas.BedCreate) -> models.Bed:
        """
        criar novo leito
        
        args:
            db: sessao do banco
            bed: dados do leito
        
        returns:
            leito criado
        """
        db_bed = models.Bed(**bed.dict())
        db.add(db_bed)
        db.commit()
        db.refresh(db_bed)
        return db_bed
    
    @staticmethod
    def get(db: Session, bed_id: int) -> Optional[models.Bed]:
        """
        obter leito por id
        
        args:
            db: sessao do banco
            bed_id: id do leito
        
        returns:
            leito ou None
        """
        return db.query(models.Bed).filter(models.Bed.id == bed_id).first()
    
    @staticmethod
    def get_by_name(db: Session, name: str) -> Optional[models.Bed]:
        """obter leito por nome"""
        return db.query(models.Bed).filter(models.Bed.name == name).first()
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[models.Bed], int]:
        """
        listar todos leitos com paginacao
        
        args:
            db: sessao do banco
            skip: offset para paginacao
            limit: limite de items por pagina
        
        returns:
            tupla (leitos, total)
        """
        query = db.query(models.Bed)
        total = query.count()
        beds = query.order_by(models.Bed.created_at.desc()).offset(skip).limit(limit).all()
        return beds, total
    
    @staticmethod
    def update(
        db: Session,
        bed_id: int,
        bed_update: schemas.BedUpdate
    ) -> Optional[models.Bed]:
        """
        atualizar leito
        
        args:
            db: sessao do banco
            bed_id: id do leito
            bed_update: dados para atualizar
        
        returns:
            leito atualizado ou None
        """
        db_bed = db.query(models.Bed).filter(models.Bed.id == bed_id).first()
        if not db_bed:
            return None
        
        # atualizar apenas campos fornecidos
        update_data = bed_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_bed, field, value)
        
        db.commit()
        db.refresh(db_bed)
        return db_bed
    
    @staticmethod
    def delete(db: Session, bed_id: int) -> bool:
        """
        deletar leito
        
        args:
            db: sessao do banco
            bed_id: id do leito
        
        returns:
            True se deletado, False se nao encontrado
        """
        db_bed = db.query(models.Bed).filter(models.Bed.id == bed_id).first()
        if not db_bed:
            return False
        
        db.delete(db_bed)
        db.commit()
        return True
    
    @staticmethod
    def search(
        db: Session,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[models.Bed], int]:
        """
        buscar leitos por nome ou descricao
        
        args:
            db: sessao do banco
            query: texto para buscar
            skip: offset para paginacao
            limit: limite de items
        
        returns:
            tupla (leitos, total)
        """
        search_query = db.query(models.Bed).filter(
            (models.Bed.name.ilike(f"%{query}%")) |
            (models.Bed.description.ilike(f"%{query}%"))
        )
        total = search_query.count()
        beds = search_query.order_by(models.Bed.created_at.desc()).offset(skip).limit(limit).all()
        return beds, total


class SimulationCRUD:
    """operacoes crud para simulacoes"""
    
    @staticmethod
    def create(db: Session, simulation: schemas.SimulationCreate) -> models.Simulation:
        """criar nova simulacao"""
        db_simulation = models.Simulation(**simulation.dict())
        db.add(db_simulation)
        db.commit()
        db.refresh(db_simulation)
        return db_simulation
    
    @staticmethod
    def get(db: Session, simulation_id: int) -> Optional[models.Simulation]:
        """obter simulacao por id"""
        return db.query(models.Simulation).filter(
            models.Simulation.id == simulation_id
        ).first()
    
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[models.Simulation], int]:
        """listar todas simulacoes"""
        query = db.query(models.Simulation)
        total = query.count()
        simulations = query.order_by(
            models.Simulation.created_at.desc()
        ).offset(skip).limit(limit).all()
        return simulations, total
    
    @staticmethod
    def get_by_bed(
        db: Session,
        bed_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[models.Simulation], int]:
        """listar simulacoes de um leito especifico"""
        query = db.query(models.Simulation).filter(models.Simulation.bed_id == bed_id)
        total = query.count()
        simulations = query.order_by(
            models.Simulation.created_at.desc()
        ).offset(skip).limit(limit).all()
        return simulations, total
    
    @staticmethod
    def get_by_status(
        db: Session,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[models.Simulation], int]:
        """listar simulacoes por status"""
        query = db.query(models.Simulation).filter(models.Simulation.status == status)
        total = query.count()
        simulations = query.order_by(
            models.Simulation.created_at.desc()
        ).offset(skip).limit(limit).all()
        return simulations, total
    
    @staticmethod
    def update(
        db: Session,
        simulation_id: int,
        simulation_update: schemas.SimulationUpdate
    ) -> Optional[models.Simulation]:
        """atualizar simulacao"""
        db_simulation = db.query(models.Simulation).filter(
            models.Simulation.id == simulation_id
        ).first()
        if not db_simulation:
            return None
        
        update_data = simulation_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_simulation, field, value)
        
        db.commit()
        db.refresh(db_simulation)
        return db_simulation
    
    @staticmethod
    def delete(db: Session, simulation_id: int) -> bool:
        """deletar simulacao"""
        db_simulation = db.query(models.Simulation).filter(
            models.Simulation.id == simulation_id
        ).first()
        if not db_simulation:
            return False
        
        db.delete(db_simulation)
        db.commit()
        return True


class ResultCRUD:
    """operacoes crud para resultados"""
    
    @staticmethod
    def create(db: Session, result: schemas.ResultCreate) -> models.Result:
        """criar novo resultado"""
        db_result = models.Result(**result.dict())
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        return db_result
    
    @staticmethod
    def create_bulk(
        db: Session,
        results: List[schemas.ResultCreate]
    ) -> List[models.Result]:
        """criar multiplos resultados em batch"""
        db_results = [models.Result(**result.dict()) for result in results]
        db.add_all(db_results)
        db.commit()
        for result in db_results:
            db.refresh(result)
        return db_results
    
    @staticmethod
    def get(db: Session, result_id: int) -> Optional[models.Result]:
        """obter resultado por id"""
        return db.query(models.Result).filter(models.Result.id == result_id).first()
    
    @staticmethod
    def get_by_simulation(
        db: Session,
        simulation_id: int,
        result_type: Optional[str] = None
    ) -> List[models.Result]:
        """listar resultados de uma simulacao"""
        query = db.query(models.Result).filter(
            models.Result.simulation_id == simulation_id
        )
        if result_type:
            query = query.filter(models.Result.result_type == result_type)
        return query.order_by(models.Result.created_at.desc()).all()
    
    @staticmethod
    def delete(db: Session, result_id: int) -> bool:
        """deletar resultado"""
        db_result = db.query(models.Result).filter(models.Result.id == result_id).first()
        if not db_result:
            return False
        
        db.delete(db_result)
        db.commit()
        return True
    
    @staticmethod
    def delete_by_simulation(db: Session, simulation_id: int) -> int:
        """deletar todos resultados de uma simulacao"""
        deleted = db.query(models.Result).filter(
            models.Result.simulation_id == simulation_id
        ).delete()
        db.commit()
        return deleted


# funcoes auxiliares para paginacao

def paginate(
    total: int,
    page: int = 1,
    per_page: int = 50
) -> Tuple[int, int, int]:
    """
    calcular parametros de paginacao
    
    args:
        total: total de items
        page: pagina atual (1-indexed)
        per_page: items por pagina
    
    returns:
        tupla (skip, limit, pages)
    """
    page = max(1, page)
    per_page = min(per_page, 100)  # max 100 items por pagina
    
    skip = (page - 1) * per_page
    limit = per_page
    pages = math.ceil(total / per_page) if total > 0 else 1
    
    return skip, limit, pages

