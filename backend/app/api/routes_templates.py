"""
rotas para gerenciamento de templates salvos
"""
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import uuid

from backend.app.database.connection import get_db
from backend.app.api.models import Template, TemplateCreate, TemplateResponse

router = APIRouter()

# armazenamento em memória de templates (simulação)
templates_store: dict[str, dict] = {}

@router.post("/templates/save", response_model=TemplateResponse, tags=["templates"])
async def save_template(
    template_data: TemplateCreate,
    db: Session = Depends(get_db)
):
    """
    salvar um novo template
    """
    template_id = str(uuid.uuid4())
    template = {
        "id": template_id,
        "name": template_data.name,
        "content": template_data.content,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    templates_store[template_id] = template
    
    return TemplateResponse(
        id=template_id,
        name=template.name,
        content=template.content,
        created_at=template["created_at"],
        updated_at=template["updated_at"]
    )

@router.get("/templates/list", response_model=List[TemplateResponse], tags=["templates"])
async def list_templates():
    """
    listar todos os templates salvos
    """
    templates = []
    for template_id, template in templates_store.items():
        templates.append(TemplateResponse(
            id=template_id,
            name=template["name"],
            content=template["content"],
            created_at=template["created_at"],
            updated_at=template["updated_at"]
        ))
    
    return templates

@router.get("/templates/{template_id}", response_model=TemplateResponse, tags=["templates"])
async def get_template(template_id: str):
    """
    buscar um template específico
    """
    if template_id not in templates_store:
        raise HTTPException(status_code=404, detail="template não encontrado")
    
    template = templates_store[template_id]
    return TemplateResponse(
        id=template_id,
        name=template["name"],
        content=template["content"],
        created_at=template["created_at"],
        updated_at=template["updated_at"]
    )

@router.put("/templates/{template_id}", response_model=TemplateResponse, tags=["templates"])
async def update_template(
    template_id: str,
    template_data: TemplateCreate,
    db: Session = Depends(get_db)
):
    """
    atualizar um template existente
    """
    if template_id not in templates_store:
        raise HTTPException(status_code=404, detail="template não encontrado")
    
    template = templates_store[template_id]
    template["name"] = template_data.name
    template["content"] = template_data.content
    template["updated_at"] = datetime.now().isoformat()
    
    return TemplateResponse(
        id=template_id,
        name=template["name"],
        content=template["content"],
        created_at=template["created_at"],
        updated_at=template["updated_at"]
    )

@router.delete("/templates/{template_id}", tags=["templates"])
async def delete_template(template_id: str):
    """
    deletar um template
    """
    if template_id not in templates_store:
        raise HTTPException(status_code=404, detail="template não encontrado")
    
    del templates_store[template_id]
    return {"message": "template deletado com sucesso"}
