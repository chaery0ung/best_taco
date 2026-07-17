import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db
from ..services import mock_classifier, mock_gemini

router = APIRouter(prefix="/api", tags=["captures"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


def _get_owned_lesion(lesion_id: int, current_user: models.User, db: Session) -> models.Lesion:
    lesion = (
        db.query(models.Lesion)
        .filter(models.Lesion.id == lesion_id, models.Lesion.user_id == current_user.id)
        .first()
    )
    if not lesion:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesion not found")
    return lesion


def _to_detail(capture: models.Capture, lesion: models.Lesion) -> schemas.CaptureDetail:
    return schemas.CaptureDetail(
        id=capture.id,
        image_path=capture.image_path,
        heatmap_path=capture.heatmap_path,
        classification=capture.classification,
        confidence=capture.confidence,
        urgency=capture.urgency,
        gemini_report=capture.gemini_report,
        created_at=capture.created_at,
        lesion_id=lesion.id,
        body_part=lesion.body_part,
        lesion_label=lesion.label,
    )


@router.post("/lesions/{lesion_id}/captures", response_model=schemas.CaptureDetail, status_code=status.HTTP_201_CREATED)
async def create_capture(
    lesion_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lesion = _get_owned_lesion(lesion_id, current_user, db)

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only JPEG/PNG/WEBP image files are allowed")

    image_bytes = await file.read()
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Image is too large (max 10MB)")

    # In production this upload goes to GCP Cloud Storage and the classification
    # call goes to a Vertex AI Endpoint; both are mocked for the demo.
    result = mock_classifier.classify(image_bytes)
    heatmap_bytes = mock_classifier.generate_heatmap(image_bytes)

    file_id = uuid.uuid4().hex
    image_name = f"{file_id}.png"
    heatmap_name = f"{file_id}_heatmap.png"
    with open(os.path.join(UPLOAD_DIR, image_name), "wb") as f:
        f.write(image_bytes)
    with open(os.path.join(UPLOAD_DIR, heatmap_name), "wb") as f:
        f.write(heatmap_bytes)

    gemini_report = mock_gemini.generate_report(
        classification=result["classification"],
        confidence=result["confidence"],
        urgency=result["urgency"],
        body_part=lesion.body_part,
        age=current_user.age,
        gender=current_user.gender,
    )

    capture = models.Capture(
        lesion_id=lesion.id,
        image_path=f"/uploads/{image_name}",
        heatmap_path=f"/uploads/{heatmap_name}",
        classification=result["classification"],
        confidence=result["confidence"],
        urgency=result["urgency"],
        gemini_report=gemini_report,
    )
    db.add(capture)
    db.commit()
    db.refresh(capture)

    return _to_detail(capture, lesion)


@router.get("/captures/{capture_id}", response_model=schemas.CaptureDetail)
def get_capture(
    capture_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    capture = db.query(models.Capture).filter(models.Capture.id == capture_id).first()
    if not capture:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Capture not found")
    lesion = _get_owned_lesion(capture.lesion_id, current_user, db)
    return _to_detail(capture, lesion)
