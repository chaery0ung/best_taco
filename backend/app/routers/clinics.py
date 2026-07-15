from fastapi import APIRouter, Depends

from .. import models
from ..auth import get_current_user
from ..services import mock_maps

router = APIRouter(prefix="/api/clinics", tags=["clinics"])


@router.get("")
def get_nearby_clinics(
    lat: float | None = None,
    lng: float | None = None,
    current_user: models.User = Depends(get_current_user),
):
    return mock_maps.nearby_dermatology(lat, lng)
