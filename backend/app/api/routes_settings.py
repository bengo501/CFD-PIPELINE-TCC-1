"""
configurações globais da app (singleton app_settings id=1).
ao alterar idioma, sincroniza user_profiles.preferred_language (id=1) se existir.
campos extra (modo simples, dev, openfoam, modelagem) ficam em options_json.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database import models as M
from backend.app.api.models import (
    AppSettingsResponse,
    AppSettingsUpdate,
    CfdOtherNotes,
    DatabaseUiOptions,
    ModelingOptions,
    OpenFoamDefaults,
)

router = APIRouter()

SETTINGS_ROW_ID = 1

DEFAULT_OPTIONS: Dict[str, Any] = {
    "simple_mode": False,
    "dev_mode": False,
    "database": {"notes": "", "client_timeout_sec": 30},
    "openfoam": {
        "solver": "simpleFoam",
        "max_iterations": 1000,
        "turbulence_model": "kEpsilon",
        "convergence": 1e-6,
    },
    "modeling": {"profile": "blender", "notes": ""},
    "cfd_other": {"notes": ""},
}


def _iso(v) -> str:
    if v is None:
        return ""
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return str(v)


def _deep_merge(base: Dict[str, Any], overlay: Dict[str, Any] | None) -> Dict[str, Any]:
    if not overlay:
        return dict(base)
    out = dict(base)
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _raw_options_to_dict(raw: Any) -> Dict[str, Any]:
    if raw is None:
        return {}
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    if isinstance(raw, dict):
        return dict(raw)
    return {}


def _resolved_options(row: M.AppSettings) -> Dict[str, Any]:
    return _deep_merge(DEFAULT_OPTIONS, _raw_options_to_dict(row.options_json))


def _to_response(row: M.AppSettings) -> AppSettingsResponse:
    opts = _resolved_options(row)
    return AppSettingsResponse(
        id=row.id,
        theme_mode=row.theme_mode or "system",
        language=row.language or "pt",
        jobs_poll_interval_sec=int(row.jobs_poll_interval_sec or 5),
        show_advanced_hints=bool(row.show_advanced_hints),
        simple_mode=bool(opts.get("simple_mode", False)),
        dev_mode=bool(opts.get("dev_mode", False)),
        database_ui=DatabaseUiOptions.model_validate(opts.get("database", {})),
        openfoam_defaults=OpenFoamDefaults.model_validate(opts.get("openfoam", {})),
        modeling=ModelingOptions.model_validate(opts.get("modeling", {})),
        cfd_other=CfdOtherNotes.model_validate(opts.get("cfd_other", {})),
        created_at=_iso(row.created_at),
        updated_at=_iso(row.updated_at),
    )


def _ensure_settings(db: Session) -> M.AppSettings:
    row = db.query(M.AppSettings).filter(M.AppSettings.id == SETTINGS_ROW_ID).first()
    if row:
        return row
    row = M.AppSettings(
        id=SETTINGS_ROW_ID,
        theme_mode="system",
        language="pt",
        jobs_poll_interval_sec=5,
        show_advanced_hints=False,
        options_json=dict(DEFAULT_OPTIONS),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/settings", response_model=AppSettingsResponse, tags=["settings"])
async def get_settings(db: Session = Depends(get_db)):
    """obter configurações; cria linha por defeito na primeira chamada."""
    row = _ensure_settings(db)
    return _to_response(row)


@router.patch("/settings", response_model=AppSettingsResponse, tags=["settings"])
async def update_settings(body: AppSettingsUpdate, db: Session = Depends(get_db)):
    """atualizar preferências; idioma também atualiza o perfil singleton."""
    row = _ensure_settings(db)
    if body.theme_mode is not None:
        row.theme_mode = body.theme_mode
    if body.language is not None:
        row.language = body.language
        prof = (
            db.query(M.UserProfile)
            .filter(M.UserProfile.id == 1)
            .first()
        )
        if prof:
            prof.preferred_language = body.language
            prof.updated_at = datetime.now(timezone.utc)
    if body.jobs_poll_interval_sec is not None:
        row.jobs_poll_interval_sec = body.jobs_poll_interval_sec
    if body.show_advanced_hints is not None:
        row.show_advanced_hints = body.show_advanced_hints

    opts = _resolved_options(row)
    if body.simple_mode is not None:
        opts["simple_mode"] = body.simple_mode
    if body.dev_mode is not None:
        opts["dev_mode"] = body.dev_mode
    if body.database_ui is not None:
        opts["database"] = {
            **opts.get("database", {}),
            **body.database_ui.model_dump(exclude_unset=True),
        }
    if body.openfoam_defaults is not None:
        opts["openfoam"] = {
            **opts.get("openfoam", {}),
            **body.openfoam_defaults.model_dump(exclude_unset=True),
        }
    if body.modeling is not None:
        opts["modeling"] = {
            **opts.get("modeling", {}),
            **body.modeling.model_dump(exclude_unset=True),
        }
    if body.cfd_other is not None:
        opts["cfd_other"] = {
            **opts.get("cfd_other", {}),
            **body.cfd_other.model_dump(exclude_unset=True),
        }
    row.options_json = opts

    row.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return _to_response(row)
