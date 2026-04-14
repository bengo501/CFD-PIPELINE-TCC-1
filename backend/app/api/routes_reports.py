# relatorios com anexos fracos a simulacao template ou result
# anexos guardam ref id string para nao forcar fk rigida a todas entidades
from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, selectinload

from backend.app.database.connection import get_db
from backend.app.database import models as M
from backend.app.api.models import (
    ReportAttachmentCreate,
    ReportAttachmentOut,
    ReportCatalogResponse,
    ReportCatalogSimulation,
    ReportCatalogTemplate,
    ReportCreate,
    ReportDetail,
    ReportMetaResultItem,
    ReportSummary,
    ReportUpdate,
)

router = APIRouter()


def _iso(v) -> str:
    if v is None:
        return ""
    if hasattr(v, "isoformat"):
        return v.isoformat()
    return str(v)


def _attachment_display(db: Session, a: M.ReportAttachment) -> str:
    if a.label and a.label.strip():
        return a.label.strip()
    if a.kind == "simulation" and a.ref_id:
        try:
            sid = int(a.ref_id)
            s = db.query(M.Simulation).filter(M.Simulation.id == sid).first()
            return s.name if s else f"simulation #{a.ref_id}"
        except ValueError:
            return a.ref_id
    if a.kind == "template" and a.ref_id:
        t = db.query(M.BedTemplate).filter(M.BedTemplate.id == a.ref_id).first()
        return t.name if t else a.ref_id
    if a.kind == "result" and a.ref_id:
        try:
            rid = int(a.ref_id)
            r = db.query(M.Result).filter(M.Result.id == rid).first()
            if r:
                return f"{r.name} ({r.result_type})"
            return f"result #{a.ref_id}"
        except ValueError:
            return a.ref_id
    if a.kind == "data_note":
        if a.note:
            t = a.note.strip()
            return t[:100] + ("…" if len(t) > 100 else "")
        return "nota de dados"
    return f"{a.kind} · {a.ref_id or '—'}"


def _attachment_to_out(db: Session, a: M.ReportAttachment) -> ReportAttachmentOut:
    return ReportAttachmentOut(
        id=a.id,
        kind=a.kind,
        ref_id=a.ref_id,
        label=a.label,
        note=a.note,
        created_at=_iso(a.created_at),
        display_ref=_attachment_display(db, a),
    )


def _build_detail(db: Session, r: M.Report) -> ReportDetail:
    atts = sorted(r.attachments, key=lambda x: x.id)
    return ReportDetail(
        id=r.id,
        title=r.title,
        body=r.body or "",
        status=r.status,
        created_at=_iso(r.created_at),
        updated_at=_iso(r.updated_at),
        attachments=[_attachment_to_out(db, a) for a in atts],
    )


@router.get(
    "/reports/meta/catalog",
    response_model=ReportCatalogResponse,
    tags=["reports"],
)
async def reports_meta_catalog(db: Session = Depends(get_db)):
    """listas compactas para selects no frontend (simulações e templates .bed)."""
    sims = (
        db.query(M.Simulation)
        .order_by(M.Simulation.created_at.desc())
        .limit(60)
        .all()
    )
    tmpl = (
        db.query(M.BedTemplate)
        .order_by(M.BedTemplate.updated_at.desc())
        .limit(100)
        .all()
    )
    return ReportCatalogResponse(
        simulations=[
            ReportCatalogSimulation(id=s.id, name=s.name, status=s.status) for s in sims
        ],
        templates=[
            ReportCatalogTemplate(id=t.id, name=t.name, tag=t.tag or "bed") for t in tmpl
        ],
    )


@router.get(
    "/reports/meta/results",
    response_model=List[ReportMetaResultItem],
    tags=["reports"],
)
async def reports_meta_results(
    simulation_id: int = Query(..., ge=1),
    db: Session = Depends(get_db),
):
    """resultados orm de uma simulação (para anexar ao relatório)."""
    sim = db.query(M.Simulation).filter(M.Simulation.id == simulation_id).first()
    if not sim:
        raise HTTPException(status_code=404, detail="simulação não encontrada")
    rows = (
        db.query(M.Result)
        .filter(M.Result.simulation_id == simulation_id)
        .order_by(M.Result.id.desc())
        .limit(300)
        .all()
    )
    return [
        ReportMetaResultItem(
            id=r.id,
            name=r.name,
            result_type=r.result_type,
            value=r.value,
            unit=r.unit,
        )
        for r in rows
    ]


@router.get("/reports", response_model=List[ReportSummary], tags=["reports"])
async def list_reports(db: Session = Depends(get_db)):
    rows = (
        db.query(M.Report)
        .options(selectinload(M.Report.attachments))
        .order_by(M.Report.updated_at.desc())
        .all()
    )
    return [
        ReportSummary(
            id=r.id,
            title=r.title,
            status=r.status,
            created_at=_iso(r.created_at),
            updated_at=_iso(r.updated_at),
            attachment_count=len(r.attachments),
        )
        for r in rows
    ]


@router.post("/reports", response_model=ReportDetail, tags=["reports"])
async def create_report(body: ReportCreate, db: Session = Depends(get_db)):
    row = M.Report(
        title=body.title.strip(),
        body=body.body or "",
        status=body.status,
    )
    db.add(row)
    db.commit()
    r = (
        db.query(M.Report)
        .options(selectinload(M.Report.attachments))
        .filter(M.Report.id == row.id)
        .first()
    )
    return _build_detail(db, r)


@router.get("/reports/{report_id}", response_model=ReportDetail, tags=["reports"])
async def get_report(report_id: int, db: Session = Depends(get_db)):
    r = (
        db.query(M.Report)
        .options(selectinload(M.Report.attachments))
        .filter(M.Report.id == report_id)
        .first()
    )
    if not r:
        raise HTTPException(status_code=404, detail="relatório não encontrado")
    return _build_detail(db, r)


@router.patch("/reports/{report_id}", response_model=ReportDetail, tags=["reports"])
async def update_report(
    report_id: int,
    body: ReportUpdate,
    db: Session = Depends(get_db),
):
    r = db.query(M.Report).filter(M.Report.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="relatório não encontrado")
    if body.title is not None:
        r.title = body.title.strip()
    if body.body is not None:
        r.body = body.body
    if body.status is not None:
        r.status = body.status
    r.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(r)
    r = (
        db.query(M.Report)
        .options(selectinload(M.Report.attachments))
        .filter(M.Report.id == report_id)
        .first()
    )
    return _build_detail(db, r)


@router.delete("/reports/{report_id}", tags=["reports"])
async def delete_report(report_id: int, db: Session = Depends(get_db)):
    r = db.query(M.Report).filter(M.Report.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="relatório não encontrado")
    db.delete(r)
    db.commit()
    return {"message": "relatório eliminado", "id": report_id}


@router.post(
    "/reports/{report_id}/attachments",
    response_model=ReportAttachmentOut,
    tags=["reports"],
)
async def add_report_attachment(
    report_id: int,
    body: ReportAttachmentCreate,
    db: Session = Depends(get_db),
):
    r = db.query(M.Report).filter(M.Report.id == report_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="relatório não encontrado")

    ref = body.ref_id.strip() if body.ref_id else None
    k = body.kind

    if k == "simulation":
        if not ref:
            raise HTTPException(status_code=400, detail="ref_id da simulação obrigatório")
        try:
            sid = int(ref)
        except ValueError:
            raise HTTPException(status_code=400, detail="ref_id de simulação inválido")
        if not db.query(M.Simulation).filter(M.Simulation.id == sid).first():
            raise HTTPException(status_code=400, detail="simulação não encontrada")
        ref = str(sid)
    elif k == "template":
        if not ref:
            raise HTTPException(status_code=400, detail="ref_id do template obrigatório")
        if not db.query(M.BedTemplate).filter(M.BedTemplate.id == ref).first():
            raise HTTPException(status_code=400, detail="template não encontrado")
    elif k == "result":
        if not ref:
            raise HTTPException(status_code=400, detail="ref_id do resultado obrigatório")
        try:
            rid = int(ref)
        except ValueError:
            raise HTTPException(status_code=400, detail="ref_id de resultado inválido")
        if not db.query(M.Result).filter(M.Result.id == rid).first():
            raise HTTPException(status_code=400, detail="resultado não encontrado")
        ref = str(rid)
    elif k == "data_note":
        note = (body.note or "").strip()
        if not note:
            raise HTTPException(
                status_code=400,
                detail="campo note obrigatório para nota de dados",
            )
        ref = None
    else:
        raise HTTPException(status_code=400, detail="tipo de anexo inválido")

    row = M.ReportAttachment(
        report_id=report_id,
        kind=k,
        ref_id=ref,
        label=body.label.strip() if body.label else None,
        note=body.note.strip() if body.note else None,
    )
    db.add(row)
    r.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(row)
    return _attachment_to_out(db, row)


@router.delete("/reports/{report_id}/attachments/{attachment_id}", tags=["reports"])
async def remove_report_attachment(
    report_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
):
    att = (
        db.query(M.ReportAttachment)
        .filter(
            M.ReportAttachment.id == attachment_id,
            M.ReportAttachment.report_id == report_id,
        )
        .first()
    )
    if not att:
        raise HTTPException(status_code=404, detail="anexo não encontrado")
    r = db.query(M.Report).filter(M.Report.id == report_id).first()
    db.delete(att)
    if r:
        r.updated_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "anexo removido", "id": attachment_id}
