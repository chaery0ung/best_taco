import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from .. import models
from ..auth import get_current_user
from ..database import get_db
from ..services.pdf_report import build_pdf

router = APIRouter(prefix="/api/reports", tags=["reports"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


def _read_upload(relative_path: str | None) -> bytes | None:
    if not relative_path:
        return None
    filename = relative_path.split("/uploads/")[-1]
    full_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(full_path):
        return None
    with open(full_path, "rb") as f:
        return f.read()


@router.get("/{capture_id}/pdf")
def download_report(
    capture_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    capture = db.query(models.Capture).filter(models.Capture.id == capture_id).first()
    if not capture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capture not found")

    lesion = (
        db.query(models.Lesion)
        .filter(models.Lesion.id == capture.lesion_id, models.Lesion.user_id == current_user.id)
        .first()
    )
    if not lesion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesion not found")

    pdf_bytes = build_pdf(
        user_name=current_user.name,
        age=current_user.age,
        gender=current_user.gender,
        body_part=lesion.body_part,
        lesion_label=lesion.label,
        classification=capture.classification,
        confidence=capture.confidence,
        urgency=capture.urgency,
        gemini_report=capture.gemini_report or "",
        capture_image_bytes=_read_upload(capture.image_path),
        heatmap_image_bytes=_read_upload(capture.heatmap_path),
    )

    return StreamingResponse(
        iter([pdf_bytes]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="skin_report_{capture_id}.pdf"'},
    )
