# insere dados de teste no sqlite quando a variavel de ambiente permitir
# o objetivo e preencher dashboard simulacoes relatorios e templates para cada utilizador demo
# nao corre em producao com postgres a menos que se force a flag explicita
from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta

from backend.app.database import crud, models, schemas
from backend.app.database.connection import DATABASE_URL, DatabaseConnection
from backend.app.database.user_seed import ensure_default_profiles

# texto fixo na coluna created by para reconhecer linhas criadas por este script
CREATED_BY = "demo_seed"


def _truthy_env(name: str) -> bool | None:
    # le uma variavel de ambiente e devolve true false ou none
    # none significa que a variavel nao existe ou nao e reconhecida
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
    # devolve se devemos inserir dados demo no arranque
    # primeiro olhamos para seed demo data
    # se existir e for explicita usamos esse valor
    # se nao existir so ativamos quando a url for sqlite local
    explicit = _truthy_env("SEED_DEMO_DATA")
    if explicit is not None:
        return explicit
    return "sqlite" in DATABASE_URL.lower()


def _bed_seed_name(uid: int) -> str:
    # nome unico do leito por utilizador para nao colidir entre ids
    return f"leito demonstracao (seed) u{uid}"


def _seed_one_user(db, uid: int, now) -> None:
    # funcao interna que popula um utilizador se ainda nao tiver simulacoes demo
    # db sessao sqlalchemy
    # uid inteiro 1 2 ou 3
    # now instante utc para calcular datas relativas
    # passo um contamos simulacoes demo deste utilizador
    n_demo = (
        db.query(models.Simulation)
        .filter(
            models.Simulation.created_by == CREATED_BY,
            models.Simulation.user_id == uid,
        )
        .count()
    )
    # se ja existir pelo menos uma nao repetimos o bloco inteiro
    if n_demo > 0:
        return

    # passo dois obtemos ou criamos o leito base
    bed_name = _bed_seed_name(uid)
    bed = crud.BedCRUD.get_by_name_for_user(db, bed_name, uid)
    if not bed:
        bed_in = schemas.BedCreate(
            name=bed_name,
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
        bed = crud.BedCRUD.create(db, bed_in, user_id=uid)

    # lista de cenarios de simulacao com nome regime status e extra com metricas
    specs: list[tuple[str, str, str, dict]] = [
        (
            f"caso laminar referencia (u{uid})",
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
            f"ensaio turbulenta v2 (u{uid})",
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
            f"varredura velocidade 0.15 ms (u{uid})",
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
            f"malha fina pendente (u{uid})",
            "laminar",
            "pending",
            {"progress": 0},
        ),
        (
            f"caso divergencia solver (u{uid})",
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

    # guardamos o id da primeira simulacao completed para ligar resultados
    first_completed_id: int | None = None

    for name, regime, status, extra in specs:
        # criacao minima via schema pydantic
        sim_in = schemas.SimulationCreate(
            bed_id=bed.id,
            name=name,
            description="registro de demonstracao para interface",
            regime=regime,
            inlet_velocity=0.15 if regime == "laminar" else 0.45,
            fluid_density=1000.0,
            fluid_viscosity=1.0e-3,
            solver="simpleFoam",
            max_iterations=2000,
            convergence_criteria=1e-4,
            created_by=CREATED_BY,
        )
        sim = crud.SimulationCRUD.create(db, sim_in, user_id=uid)

        # dicionario de atualizacao parcial para estado e metricas de demo
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
        if status in ("completed", "failed") and sd is not None and rd is not None:
            upd["completed_at"] = (now - sd) + rd

        crud.SimulationCRUD.update(db, sim.id, schemas.SimulationUpdate(**upd))
        if status == "completed" and first_completed_id is None:
            first_completed_id = sim.id

    # dois resultados numericos ligados a primeira completed
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

    # relatorio simples por utilizador
    rep = models.Report(
        title=f"relatorio demo utilizador {uid}",
        body=f"texto de exemplo gerado pelo seed local para o utilizador {uid}.",
        status="draft",
        user_id=uid,
    )
    db.add(rep)
    db.commit()

    # template bed curto guardado na tabela bed templates
    import uuid

    tid = str(uuid.uuid4())
    tmpl = models.BedTemplate(
        id=tid,
        name=f"template demo u{uid}",
        content='title "demo"\nbed { diameter: 0.05 }\n',
        tag="bed",
        source="seed",
        user_id=uid,
    )
    db.add(tmpl)
    db.commit()


def seed_demo_data_if_needed() -> None:
    # ponto de entrada chamado pelo startup do main fastapi
    if not seed_demo_enabled():
        return

    db = DatabaseConnection.get_session()
    try:
        ensure_default_profiles(db)
        now = datetime.now(timezone.utc)
        for uid in (1, 2, 3):
            _seed_one_user(db, uid, now)

        print("[OK] dados de demonstracao inseridos por utilizador (SEED_DEMO_DATA / sqlite)")
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
