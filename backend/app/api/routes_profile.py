# router fastapi para perfis locais
# nao existe password nem oauth nesta versao
# o isolamento de dados vem do cabecalho x user id lido em deps user
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database import models as M
from backend.app.api.models import UserProfileResponse, UserProfileUpdate
from backend.app.api.deps_user import get_active_user_id
from backend.app.database.user_seed import (
    DEFAULT_PROFILE_IDS,
    ensure_default_profiles,
    ensure_profile_by_id,
)

router = APIRouter()


def _iso(v) -> str:
    # converte valores datetime do sql alchemy para texto iso
    # v pode ser none se a coluna veio vazia
    if v is None:
        return ""
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return str(v)


def _to_response(row: M.UserProfile) -> UserProfileResponse:
    # copia campos do orm para o modelo pydantic da resposta json
    # o pydantic valida tipos antes de serializar
    return UserProfileResponse(
        id=row.id,
        display_name=row.display_name or "",
        email=row.email or "",
        organization=row.organization or "",
        role=row.role or "researcher",
        bio=row.bio,
        preferred_language=row.preferred_language or "pt",
        created_at=_iso(row.created_at),
        updated_at=_iso(row.updated_at),
    )


def _ensure_profile(db: Session, user_id: int) -> M.UserProfile:
    # delega para user seed que cria linha em falta
    return ensure_profile_by_id(db, user_id)


@router.get("/users", response_model=List[UserProfileResponse], tags=["profile"])
async def list_users(db: Session = Depends(get_db)):
    # lista apenas ids em default profile ids ordenados
    # o frontend usa isto para preencher o menu de troca de utilizador
    ensure_default_profiles(db)
    rows = (
        db.query(M.UserProfile)
        .filter(M.UserProfile.id.in_(DEFAULT_PROFILE_IDS))
        .order_by(M.UserProfile.id)
        .all()
    )
    return [_to_response(r) for r in rows]


@router.get("/profile", response_model=UserProfileResponse, tags=["profile"])
async def get_profile(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    # le o perfil associado ao id do cabecalho atual
    row = _ensure_profile(db, user_id)
    return _to_response(row)


@router.patch("/profile", response_model=UserProfileResponse, tags=["profile"])
async def update_profile(
    body: UserProfileUpdate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    # patch parcial so campos enviados no json mudam
    row = _ensure_profile(db, user_id)
    if body.display_name is not None:
        row.display_name = body.display_name.strip()
    if body.email is not None:
        row.email = body.email.strip()
    if body.organization is not None:
        row.organization = body.organization.strip()
    if body.role is not None:
        row.role = body.role
    if body.bio is not None:
        row.bio = body.bio.strip() if body.bio.strip() else None
    if body.preferred_language is not None:
        row.preferred_language = body.preferred_language
    row.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return _to_response(row)
