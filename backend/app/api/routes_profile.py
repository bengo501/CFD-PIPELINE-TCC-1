# perfil singleton sem autenticacao multi conta id fixo igual a um
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database import models as M
from backend.app.api.models import UserProfileResponse, UserProfileUpdate

router = APIRouter()

# constante centraliza o id esperado pela ui e por migracoes manuais
PROFILE_ROW_ID = 1


def _iso(v) -> str:
    # converte datetime sql para string iso ou devolve vazio
    if v is None:
        return ""
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return str(v)


def _to_response(row: M.UserProfile) -> UserProfileResponse:
    # mapeia colunas orm para modelo pydantic de resposta http
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


def _ensure_profile(db: Session) -> M.UserProfile:
    # select por chave primaria
    row = db.query(M.UserProfile).filter(M.UserProfile.id == PROFILE_ROW_ID).first()
    if row:
        return row
    # primeira execucao cria linha demo coerente com textos do frontend
    row = M.UserProfile(
        id=PROFILE_ROW_ID,
        display_name="ana silva",
        email="ana.silva@exemplo.edu",
        organization="laboratório de engenharia — demo",
        role="researcher",
        bio=None,
        preferred_language="pt",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/profile", response_model=UserProfileResponse, tags=["profile"])
async def get_profile(db: Session = Depends(get_db)):
    """obter perfil; cria linha por defeito na primeira chamada."""
    row = _ensure_profile(db)
    return _to_response(row)


@router.patch("/profile", response_model=UserProfileResponse, tags=["profile"])
async def update_profile(body: UserProfileUpdate, db: Session = Depends(get_db)):
    """atualizar campos do perfil singleton."""
    row = _ensure_profile(db)
    # cada if so altera colunas explicitamente enviadas no patch
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
