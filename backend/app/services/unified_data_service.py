from datetime import datetime, timezone
from math import ceil
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.database import models, schemas


class UnifiedDataService:
    """centraliza leituras para dashboard, historico e resultados."""

    @staticmethod
    def _to_public_file_url(relative_path: Optional[str]) -> Optional[str]:
        if not relative_path:
            return None
        normalized = str(relative_path).replace("\\", "/").lstrip("/")
        if normalized.startswith("generated/"):
            normalized = normalized[len("generated/"):]
        if normalized.startswith("3d/") or normalized.startswith("models/"):
            return f"/files/{normalized}"
        return None

    def _bed_to_model_3d(self, bed: models.Bed) -> schemas.Model3DResponse:
        blend_url = self._to_public_file_url(bed.blend_file_path)
        stl_url = self._to_public_file_url(bed.stl_file_path)
        return schemas.Model3DResponse(
            id=bed.id,
            user_id=bed.user_id,
            name=bed.name,
            description=bed.description,
            diameter=bed.diameter,
            height=bed.height,
            wall_thickness=bed.wall_thickness,
            particle_count=bed.particle_count,
            particle_diameter=bed.particle_diameter,
            particle_kind=bed.particle_kind,
            packing_method=bed.packing_method,
            porosity=bed.porosity,
            bed_file_path=bed.bed_file_path,
            json_file_path=bed.json_file_path,
            blend_file_path=bed.blend_file_path,
            stl_file_path=bed.stl_file_path,
            blend_file_url=blend_url,
            stl_file_url=stl_url,
            preview_model_url=blend_url or stl_url,
            has_model_files=bool(bed.blend_file_path or bed.stl_file_path),
            parameters_json=bed.parameters_json,
            created_at=bed.created_at,
            updated_at=bed.updated_at,
            created_by=bed.created_by,
        )

    def _simulation_query(self, db: Session, user_id: int):
        return db.query(models.Simulation).filter(models.Simulation.user_id == user_id)

    def _models_query(self, db: Session, user_id: int):
        return (
            db.query(models.Bed)
            .filter(models.Bed.user_id == user_id)
            .filter(
                (models.Bed.blend_file_path.isnot(None))
                | (models.Bed.stl_file_path.isnot(None))
            )
        )

    def list_models_3d(
        self,
        db: Session,
        user_id: int,
        page: int = 1,
        per_page: int = 50,
    ) -> schemas.Model3DListResponse:
        query = self._models_query(db, user_id).order_by(models.Bed.created_at.desc())
        total = query.count()
        page = max(1, page)
        per_page = min(max(1, per_page), 100)
        skip = (page - 1) * per_page
        items = query.offset(skip).limit(per_page).all()
        return schemas.Model3DListResponse(
            total=total,
            page=page,
            per_page=per_page,
            pages=ceil(total / per_page) if total > 0 else 1,
            items=[self._bed_to_model_3d(bed) for bed in items],
        )

    def get_history(
        self,
        db: Session,
        user_id: int,
        limit: int = 100,
    ) -> schemas.HistoryResponse:
        simulations = (
            self._simulation_query(db, user_id)
            .order_by(models.Simulation.created_at.desc())
            .limit(limit)
            .all()
        )
        model_beds = (
            self._models_query(db, user_id)
            .order_by(models.Bed.updated_at.desc().nullslast(), models.Bed.created_at.desc())
            .limit(limit)
            .all()
        )

        history_items: list[schemas.HistoryEntryResponse] = []

        for sim in simulations:
            history_items.append(
                schemas.HistoryEntryResponse(
                    entry_type="simulation",
                    source_id=sim.id,
                    title=sim.name,
                    description=sim.description,
                    status=sim.status,
                    created_at=sim.created_at,
                    updated_at=sim.updated_at,
                    simulation_id=sim.id,
                    bed_id=sim.bed_id,
                    metadata={
                        "progress": sim.progress,
                        "case_directory": sim.case_directory,
                        "execution_time": sim.execution_time,
                    },
                )
            )

        for bed in model_beds:
            created_at = bed.updated_at or bed.created_at
            history_items.append(
                schemas.HistoryEntryResponse(
                    entry_type="model_3d",
                    source_id=bed.id,
                    title=bed.name,
                    description=bed.description,
                    created_at=created_at,
                    updated_at=bed.updated_at,
                    model_3d_id=bed.id,
                    bed_id=bed.id,
                    metadata={
                        "blend_file_path": bed.blend_file_path,
                        "stl_file_path": bed.stl_file_path,
                        "has_blend": bool(bed.blend_file_path),
                        "has_stl": bool(bed.stl_file_path),
                    },
                )
            )

        def sort_key(item: schemas.HistoryEntryResponse):
            dt = item.updated_at or item.created_at
            if dt is None:
                return datetime.min.replace(tzinfo=timezone.utc)
            return dt

        history_items.sort(key=sort_key, reverse=True)
        if limit > 0:
            history_items = history_items[:limit]

        return schemas.HistoryResponse(
            simulations=[schemas.SimulationResponse.model_validate(sim) for sim in simulations],
            models_3d=[self._bed_to_model_3d(bed) for bed in model_beds],
            items=history_items,
        )

    def get_dashboard_summary(
        self,
        db: Session,
        user_id: int,
        recent_limit: int = 8,
    ) -> schemas.DashboardSummaryResponse:
        simulations = self._simulation_query(db, user_id).all()
        recent_simulations = (
            self._simulation_query(db, user_id)
            .order_by(models.Simulation.created_at.desc())
            .limit(recent_limit)
            .all()
        )
        recent_models = (
            self._models_query(db, user_id)
            .order_by(models.Bed.updated_at.desc().nullslast(), models.Bed.created_at.desc())
            .limit(recent_limit)
            .all()
        )

        by_status = {
            "pending": 0,
            "running": 0,
            "completed": 0,
            "failed": 0,
        }
        execution_times: list[float] = []
        pressure_drops: list[float] = []
        reynolds_numbers: list[float] = []

        for sim in simulations:
            if sim.status in by_status:
                by_status[sim.status] += 1
            if sim.execution_time is not None:
                execution_times.append(sim.execution_time)
            if sim.pressure_drop is not None:
                pressure_drops.append(sim.pressure_drop)
            if sim.reynolds_number is not None:
                reynolds_numbers.append(sim.reynolds_number)

        total = len(simulations)
        completed = by_status["completed"]
        success_rate = (completed / total * 100.0) if total > 0 else 0.0

        return schemas.DashboardSummaryResponse(
            total_simulations=total,
            total_models_3d=self._models_query(db, user_id).count(),
            by_status=by_status,
            success_rate=success_rate,
            average_execution_time=(
                sum(execution_times) / len(execution_times) if execution_times else None
            ),
            average_pressure_drop=(
                sum(pressure_drops) / len(pressure_drops) if pressure_drops else None
            ),
            average_reynolds_number=(
                sum(reynolds_numbers) / len(reynolds_numbers) if reynolds_numbers else None
            ),
            recent_simulations=[
                schemas.SimulationResponse.model_validate(sim) for sim in recent_simulations
            ],
            recent_models_3d=[self._bed_to_model_3d(bed) for bed in recent_models],
        )
