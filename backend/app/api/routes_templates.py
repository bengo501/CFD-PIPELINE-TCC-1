# crud de templates bed armazenados como texto na tabela bed templates
from datetime import datetime, timezone
from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import BedTemplate
from backend.app.api.models import (
    TemplateCreate,
    TemplateResponse,
    TemplateSummary,
)

router = APIRouter()


def _dt_iso(v) -> str:
    # normaliza timestamps para strings json estaveis
    if v is None:
        return ""
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return str(v)


def _to_summary(row: BedTemplate) -> TemplateSummary:
    # payload leve sem campo content grande
    return TemplateSummary(
        id=row.id,
        name=row.name,
        created_at=_dt_iso(row.created_at),
        updated_at=_dt_iso(row.updated_at),
        tag=row.tag or "bed",
        source=row.source or "editor",
    )


def _to_response(row: BedTemplate) -> TemplateResponse:
    # payload completo para edicao
    return TemplateResponse(
        id=row.id,
        name=row.name,
        content=row.content,
        created_at=_dt_iso(row.created_at),
        updated_at=_dt_iso(row.updated_at),
        tag=row.tag or "bed",
        source=row.source or "editor",
    )


@router.post("/templates/save", response_model=TemplateResponse, tags=["templates"])
async def save_template(template_data: TemplateCreate, db: Session = Depends(get_db)):
    """salvar um novo template"""
    # uuid4 string evita colisao sem servico central
    template_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    row = BedTemplate(
        id=template_id,
        name=template_data.name.strip(),
        content=template_data.content,
        tag=(template_data.tag or "bed").strip()[:50] or "bed",
        source=(template_data.source or "editor").strip()[:50] or "editor",
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_response(row)


@router.get("/templates/list", response_model=List[TemplateSummary], tags=["templates"])
async def list_templates(db: Session = Depends(get_db)):
    """listar templates (sem conteúdo .bed)"""
    rows = (
        db.query(BedTemplate)
        .order_by(BedTemplate.updated_at.desc(), BedTemplate.created_at.desc())
        .all()
    )
    return [_to_summary(r) for r in rows]


@router.get("/templates/{template_id}", response_model=TemplateResponse, tags=["templates"])
async def get_template(template_id: str, db: Session = Depends(get_db)):
    """buscar um template específico com conteúdo"""
    row = db.query(BedTemplate).filter(BedTemplate.id == template_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="template não encontrado")
    return _to_response(row)


@router.put("/templates/{template_id}", response_model=TemplateResponse, tags=["templates"])
async def update_template(
    template_id: str,
    template_data: TemplateCreate,
    db: Session = Depends(get_db),
):
    """atualizar um template existente"""
    row = db.query(BedTemplate).filter(BedTemplate.id == template_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="template não encontrado")

    row.name = template_data.name.strip()
    row.content = template_data.content
    row.tag = (template_data.tag or row.tag or "bed").strip()[:50] or "bed"
    row.source = (template_data.source or row.source or "editor").strip()[:50] or "editor"
    row.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(row)
    return _to_response(row)


@router.post("/templates/{template_id}/duplicate", response_model=TemplateResponse, tags=["templates"])
async def duplicate_template(template_id: str, db: Session = Depends(get_db)):
    """duplicar template existente"""
    orig = db.query(BedTemplate).filter(BedTemplate.id == template_id).first()
    if not orig:
        raise HTTPException(status_code=404, detail="template não encontrado")

    new_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    copy_name = f"{orig.name} (copy)"
    row = BedTemplate(
        id=new_id,
        name=copy_name[:255],
        content=orig.content,
        tag=orig.tag or "bed",
        source="duplicate",
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_response(row)


@router.delete("/templates/{template_id}", tags=["templates"])
async def delete_template(template_id: str, db: Session = Depends(get_db)):
    """deletar um template"""
    row = db.query(BedTemplate).filter(BedTemplate.id == template_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="template não encontrado")

    db.delete(row)
    db.commit()
    return {"message": "template deletado com sucesso"}
