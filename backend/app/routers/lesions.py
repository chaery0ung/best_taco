from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db

router = APIRouter(prefix="/api/lesions", tags=["lesions"])


@router.get("", response_model=list[schemas.LesionSummary])
def list_lesions(
    body_part: str | None = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(models.Lesion).filter(models.Lesion.user_id == current_user.id)
    if body_part:
        query = query.filter(models.Lesion.body_part == body_part)
    lesions = query.order_by(models.Lesion.created_at).all()

    summaries = []
    for lesion in lesions:
        captures = lesion.captures
        latest = captures[-1] if captures else None
        summaries.append(
            schemas.LesionSummary(
                id=lesion.id,
                body_part=lesion.body_part,
                label=lesion.label,
                latest_classification=latest.classification if latest else None,
                latest_urgency=latest.urgency if latest else None,
                latest_created_at=latest.created_at if latest else None,
            )
        )
    return summaries


@router.post("", response_model=schemas.LesionOut, status_code=status.HTTP_201_CREATED)
def create_lesion(
    payload: schemas.LesionCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lesion = models.Lesion(user_id=current_user.id, body_part=payload.body_part, label=payload.label)
    db.add(lesion)
    db.commit()
    db.refresh(lesion)
    return lesion


@router.get("/{lesion_id}", response_model=schemas.LesionOut)
def get_lesion(
    lesion_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lesion = (
        db.query(models.Lesion)
        .filter(models.Lesion.id == lesion_id, models.Lesion.user_id == current_user.id)
        .first()
    )
    if not lesion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesion not found")
    return lesion


@router.delete("/{lesion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesion(
    lesion_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lesion = (
        db.query(models.Lesion)
        .filter(models.Lesion.id == lesion_id, models.Lesion.user_id == current_user.id)
        .first()
    )
    if not lesion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesion not found")
    db.delete(lesion)
    db.commit()
