# insere leito e simulacoes demo se env permitir e base ainda vazia de demo
# evita duplicar usando created_by e contagem de linhas demo
from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta

from backend.app.database import crud, models, schemas
from backend.app.database.connection import DATABASE_URL, DatabaseConnection

# nome fixo para nao duplicar corrida seed
BED_SEED_NAME = "leito demonstracao (seed)"
# marca linhas criadas por este modulo
CREATED_BY = "demo_seed"


def _truthy_env(name: str) -> bool | None:
    # normaliza texto para decidir se env e positivo negativo ou invalido
    raw = os.getenv(name)
    if raw is None:
        return None
    v = raw.strip().lower()
    if v in ("1", "true", "yes", "on"):
        return True
    if v in ("0", "false", "no", "off"):
        return False
    return None


def seed_demo_enabled() -> bool:
    """ativa seed explicitamente; se nao definido, default so para sqlite local."""
    # prioriza flag explicita senao heuristica por url sqlite
    explicit = _truthy_env("SEED_DEMO_DATA")
    if explicit is not None:
        return explicit
    return "sqlite" in DATABASE_URL.lower()


def seed_demo_data_if_needed() -> None:
    if not seed_demo_enabled():
        return

    db = DatabaseConnection.get_session()
    try:
        # contagem rapida evita repetir seed em cada restart
        n_demo = (
            db.query(models.Simulation)
            .filter(models.Simulation.created_by == CREATED_BY)
            .count()
        )
        if n_demo > 0:
            return

        # cria bed base uma vez e reutiliza bed id nas simulacoes seguintes
        bed = crud.BedCRUD.get_by_name(db, BED_SEED_NAME)
        if not bed:
            bed_in = schemas.BedCreate(
                name=BED_SEED_NAME,
                description="leito criado automaticamente para dados de teste do dashboard",
                diameter=0.1,
                height=0.3,
                wall_thickness=0.005,
                particle_count=500,
                particle_diameter=0.01,
                particle_kind="sphere",
                packing_method="random",
                porosity=0.42,
                created_by=CREATED_BY,
            )
            bed = crud.BedCRUD.create(db, bed_in)

        now = datetime.now(timezone.utc)
        # cada tupla nome regime status dict com metricas e deltas temporais
        specs: list[tuple[str, str, str, dict]] = [
            (
                "caso laminar referencia",
                "laminar",
                "completed",
                {
                    "progress": 100,
                    "mesh_cells_count": 420_000,
                    "mesh_quality": "good",
                    "pressure_drop": 1280.5,
                    "average_velocity": 0.11,
                    "reynolds_number": 165.0,
                    "execution_time": 842.3,
                    "started_delta": timedelta(hours=5),
                    "run_delta": timedelta(minutes=14),
                },
            ),
            (
                "ensaio turbulenta v2",
                "turbulent",
                "completed",
                {
                    "progress": 100,
                    "mesh_cells_count": 890_000,
                    "mesh_quality": "acceptable",
                    "pressure_drop": 3420.0,
                    "average_velocity": 0.28,
                    "reynolds_number": 12_400.0,
                    "execution_time": 3_102.0,
                    "started_delta": timedelta(days=1, hours=2),
                    "run_delta": timedelta(hours=1, minutes=3),
                },
            ),
            (
                "varredura velocidade 0.15 ms",
                "laminar",
                "running",
                {
                    "progress": 52,
                    "mesh_cells_count": 310_000,
                    "mesh_quality": "good",
                    "started_delta": timedelta(minutes=25),
                },
            ),
            (
                "malha fina pendente",
                "laminar",
                "pending",
                {"progress": 0},
            ),
            (
                "caso divergencia solver",
                "turbulent",
                "failed",
                {
                    "progress": 78,
                    "mesh_cells_count": 600_000,
                    "mesh_quality": "poor",
                    "started_delta": timedelta(days=2),
                    "run_delta": timedelta(minutes=40),
                },
            ),
        ]

        first_completed_id: int | None = None

        for name, regime, status, extra in specs:
            # create insere defaults do schema depois update aplica campos de demo
            sim_in = schemas.SimulationCreate(
                bed_id=bed.id,
                name=name,
                description="registro de demonstracao para interface",
                regime=regime,
                # velocidade maior em turbulent para diferenciar cenarios de demo
                inlet_velocity=0.15 if regime == "laminar" else 0.45,
                fluid_density=1000.0,
                fluid_viscosity=1.0e-3,
                solver="simpleFoam",
                max_iterations=2000,
                convergence_criteria=1e-4,
                created_by=CREATED_BY,
            )
            sim = crud.SimulationCRUD.create(db, sim_in)

            upd: dict = {
                "status": status,
                "progress": extra.get("progress", 0),
            }
            if "mesh_cells_count" in extra:
                upd["mesh_cells_count"] = extra["mesh_cells_count"]
            if "mesh_quality" in extra:
                upd["mesh_quality"] = extra["mesh_quality"]
            if "pressure_drop" in extra:
                upd["pressure_drop"] = extra["pressure_drop"]
            if "average_velocity" in extra:
                upd["average_velocity"] = extra["average_velocity"]
            if "reynolds_number" in extra:
                upd["reynolds_number"] = extra["reynolds_number"]
            if "execution_time" in extra:
                upd["execution_time"] = extra["execution_time"]

            sd = extra.get("started_delta")
            rd = extra.get("run_delta")
            if sd is not None:
                upd["started_at"] = now - sd
            # completed at e started at mais duracao simulada quando fechado
            if status in ("completed", "failed") and sd is not None and rd is not None:
                upd["completed_at"] = (now - sd) + rd

            crud.SimulationCRUD.update(
                db, sim.id, schemas.SimulationUpdate(**upd)
            )
            if status == "completed" and first_completed_id is None:
                first_completed_id = sim.id

        if first_completed_id is not None:
            crud.ResultCRUD.create(
                db,
                schemas.ResultCreate(
                    simulation_id=first_completed_id,
                    result_type="metric",
                    name="queda_pressao_pa",
                    value=1280.5,
                    unit="Pa",
                ),
            )
            crud.ResultCRUD.create(
                db,
                schemas.ResultCreate(
                    simulation_id=first_completed_id,
                    result_type="metric",
                    name="numero_reynolds",
                    value=165.0,
                    unit="",
                ),
            )

        print("[OK] dados de demonstracao inseridos (SEED_DEMO_DATA / sqlite)")
    except Exception as e:
        print(f"[AVISO] seed demonstracao ignorado: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    from pathlib import Path
    import sys

    root = Path(__file__).resolve().parents[3]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    DatabaseConnection.create_tables()
    seed_demo_data_if_needed()
