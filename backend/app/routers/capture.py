import datetime
import os
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import get_current_user
from ..database import get_db
from ..services import mock_classifier, mock_gemini, vertex_classifier

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="병변을 찾을 수 없습니다")
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


def _change_note(previous: models.Capture | None, current_classification: str) -> str | None:
    if previous is None:
        return None
    days = (datetime.datetime.utcnow() - previous.created_at).days
    when = f"{days}일 전" if days < 60 else f"약 {days // 30}개월 전"
    if previous.classification == current_classification:
        return f"{when} 촬영 결과와 동일한 분류로, 유의미한 변화가 관찰되지 않았습니다."
    return f"{when} 촬영에서는 '{previous.classification}'(으)로 분류되었으나, 이번에는 분류가 변경되어 추가 확인이 필요합니다."


@router.post("/lesions/{lesion_id}/captures", response_model=schemas.CaptureDetail, status_code=status.HTTP_201_CREATED)
async def create_capture(
    lesion_id: int,
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    lesion = _get_owned_lesion(lesion_id, current_user, db)

    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미지 파일(JPEG/PNG/WEBP)만 업로드할 수 있습니다")

    image_bytes = await file.read()
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이미지 크기가 너무 큽니다 (최대 10MB)")

    # Classification calls the deployed Vertex AI endpoint; the Explainable AI
    # heatmap isn't wired up yet, so that part stays mocked.
    try:
        result = vertex_classifier.classify(image_bytes)
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    heatmap_bytes = mock_classifier.generate_heatmap(image_bytes)

    file_id = uuid.uuid4().hex
    image_name = f"{file_id}.png"
    heatmap_name = f"{file_id}_heatmap.png"
    with open(os.path.join(UPLOAD_DIR, image_name), "wb") as f:
        f.write(image_bytes)
    with open(os.path.join(UPLOAD_DIR, heatmap_name), "wb") as f:
        f.write(heatmap_bytes)

    previous_capture = lesion.captures[-1] if lesion.captures else None
    change_note = _change_note(previous_capture, result["classification"])

    gemini_report = mock_gemini.generate_report(
        classification=result["classification"],
        confidence=result["confidence"],
        urgency=result["urgency"],
        body_part=lesion.body_part,
        age=current_user.age,
        gender=current_user.gender,
        skin_tone=current_user.skin_tone,
        change_note=change_note,
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="촬영 기록을 찾을 수 없습니다")
    lesion = _get_owned_lesion(capture.lesion_id, current_user, db)
    return _to_detail(capture, lesion)
