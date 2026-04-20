# crud de templates bed armazenados como texto na tabela bed templates
from datetime import datetime, timezone
from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.database.connection import get_db
from backend.app.database.models import BedTemplate
from backend.app.api.deps_user import get_active_user_id
from backend.app.api.models import (
    PaginatedTemplateSummary,
    TemplateCreate,
    TemplateResponse,
    TemplateSummary,
)
from backend.app.utils.pagination import (
    build_paginated_payload,
    clean_filters,
    parse_datetime_filter,
    resolve_page_limit,
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
async def save_template(
    template_data: TemplateCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
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
        user_id=user_id,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_response(row)


@router.get("/templates/list", response_model=PaginatedTemplateSummary, tags=["templates"])
async def list_templates(
    page: int = Query(1, ge=1),
    limit: int | None = Query(None, ge=1, le=100),
    per_page: int | None = Query(None, ge=1, le=100, description="alias legado de limit"),
    search: str | None = Query(None, description="buscar por nome"),
    tag: str | None = Query(None, description="filtrar por tag"),
    source: str | None = Query(None, description="filtrar por origem"),
    created_from: str | None = Query(None, description="filtrar por data inicial"),
    created_to: str | None = Query(None, description="filtrar por data final"),
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """listar templates (sem conteúdo .bed)"""
    page, limit, skip = resolve_page_limit(page=page, limit=limit, per_page=per_page)
    parsed_from = parse_datetime_filter(created_from)
    parsed_to = parse_datetime_filter(created_to, end_of_day=True)
    query = db.query(BedTemplate).filter(BedTemplate.user_id == user_id)
    if search:
        like = f"%{search.strip()}%"
        query = query.filter(BedTemplate.name.ilike(like))
    if tag:
        query = query.filter(BedTemplate.tag == tag)
    if source:
        query = query.filter(BedTemplate.source == source)
    if parsed_from:
        query = query.filter(BedTemplate.updated_at >= parsed_from)
    if parsed_to:
        query = query.filter(BedTemplate.updated_at <= parsed_to)
    total = query.count()
    rows = (
        query.order_by(BedTemplate.updated_at.desc(), BedTemplate.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return PaginatedTemplateSummary(
        **build_paginated_payload(
            items=[_to_summary(r) for r in rows],
            total=total,
            page=page,
            limit=limit,
            applied_filters=clean_filters(
                search=search,
                tag=tag,
                source=source,
                created_from=created_from,
                created_to=created_to,
            ),
        )
    )


@router.get("/templates/{template_id}", response_model=TemplateResponse, tags=["templates"])
async def get_template(
    template_id: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """buscar um template específico com conteúdo"""
    row = db.query(BedTemplate).filter(BedTemplate.id == template_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="template não encontrado")
    if row.user_id != user_id:
        raise HTTPException(status_code=404, detail="template não encontrado")
    return _to_response(row)


@router.put("/templates/{template_id}", response_model=TemplateResponse, tags=["templates"])
async def update_template(
    template_id: str,
    template_data: TemplateCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """atualizar um template existente"""
    row = db.query(BedTemplate).filter(BedTemplate.id == template_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="template não encontrado")
    if row.user_id != user_id:
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
async def duplicate_template(
    template_id: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """duplicar template existente"""
    orig = db.query(BedTemplate).filter(BedTemplate.id == template_id).first()
    if not orig:
        raise HTTPException(status_code=404, detail="template não encontrado")
    if orig.user_id != user_id:
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
        user_id=user_id,
        created_at=now,
        updated_at=now,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _to_response(row)


@router.delete("/templates/{template_id}", tags=["templates"])
async def delete_template(
    template_id: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_active_user_id),
):
    """deletar um template"""
    row = db.query(BedTemplate).filter(BedTemplate.id == template_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="template não encontrado")
    if row.user_id != user_id:
        raise HTTPException(status_code=404, detail="template não encontrado")

    db.delete(row)
    db.commit()
    return {"message": "template deletado com sucesso"}
