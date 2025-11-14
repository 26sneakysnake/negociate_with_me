# backend/routers/templates.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import crud
from typing import List
from pydantic import BaseModel

router = APIRouter(prefix="/api/templates", tags=["templates"])

class TemplateResponse(BaseModel):
    id: str
    name: str
    category: str
    description: str
    context_template: str
    objective_template: str
    minimum_template: str
    icon: str | None

@router.get("/", response_model=List[TemplateResponse])
async def list_templates(db: Session = Depends(get_db)):
    """Get all available context templates"""
    templates = crud.get_all_templates(db)

    return [
        TemplateResponse(
            id=t.id,
            name=t.name,
            category=t.category,
            description=t.description,
            context_template=t.context_template,
            objective_template=t.objective_template,
            minimum_template=t.minimum_template,
            icon=t.icon
        )
        for t in templates
    ]

@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(template_id: str, db: Session = Depends(get_db)):
    """Get a specific template"""
    template = crud.get_template(db, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return TemplateResponse(
        id=template.id,
        name=template.name,
        category=template.category,
        description=template.description,
        context_template=template.context_template,
        objective_template=template.objective_template,
        minimum_template=template.minimum_template,
        icon=template.icon
    )
