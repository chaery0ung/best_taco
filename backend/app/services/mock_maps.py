"""Mock stand-in for the Google Maps Places API "nearby dermatology" lookup."""
import math
import random

CLINIC_NAME_POOL = [
    "Seoul Forest Dermatology Clinic",
    "Yonsei Smile Dermatology",
    "Green Skin Clinic",
    "Cheongdam Derma Clinic",
    "Neighborhood Dermatology Clinic",
    "Sky Dermatology",
    "Spring Day Dermatology Clinic",
    "MediSkin Clinic",
]

DEFAULT_LAT = 37.5665  # Seoul City Hall, used when the client can't get geolocation
DEFAULT_LNG = 126.9780


def _haversine_km(lat1, lng1, lat2, lng2):
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return r * 2 * math.asin(math.sqrt(a))


def nearby_dermatology(lat: float | None, lng: float | None) -> list[dict]:
    lat = lat if lat is not None else DEFAULT_LAT
    lng = lng if lng is not None else DEFAULT_LNG
    rng = random.Random(round(lat, 3) * 1000 + round(lng, 3))

    clinics = []
    for name in rng.sample(CLINIC_NAME_POOL, k=5):
        offset_lat = lat + rng.uniform(-0.02, 0.02)
        offset_lng = lng + rng.uniform(-0.02, 0.02)
        distance = _haversine_km(lat, lng, offset_lat, offset_lng)
        clinics.append(
            {
                "name": name,
                "address": f"Near Seoul, Block {rng.randint(1, 200)}",
                "lat": offset_lat,
                "lng": offset_lng,
                "distance_km": round(distance, 2),
                "phone": f"02-{rng.randint(300,999)}-{rng.randint(1000,9999)}",
            }
        )
    clinics.sort(key=lambda c: c["distance_km"])
    return clinics
