"""Mock stand-in for the Vertex AI CNN classification + Explainable AI heatmap endpoint.

In the real architecture this module's job is done by a deployed Vertex AI
model endpoint plus Vertex Explainable AI. Here we fabricate a deterministic
(but varied) result from the image bytes so demo captures behave consistently
on repeat runs, and render a plausible-looking attention heatmap with Pillow.
"""
import hashlib
import io
import random

from PIL import Image, ImageDraw, ImageFilter

CLASSES = [
    {"key": "nevus", "label": "Nevus (benign mole)", "urgency": "low", "weight": 40},
    {"key": "seborrheic_keratosis", "label": "Seborrheic Keratosis", "urgency": "low", "weight": 25},
    {"key": "actinic_keratosis", "label": "Actinic Keratosis (suspected)", "urgency": "low", "weight": 15},
    {"key": "bcc", "label": "Basal Cell Carcinoma (suspected)", "urgency": "high", "weight": 12},
    {"key": "melanoma", "label": "Melanoma (suspected)", "urgency": "high", "weight": 8},
]

MAX_DIM = 512


def _seeded_random(image_bytes: bytes) -> random.Random:
    digest = hashlib.md5(image_bytes).hexdigest()
    return random.Random(int(digest, 16))


def classify(image_bytes: bytes) -> dict:
    rng = _seeded_random(image_bytes)
    population = [c["key"] for c in CLASSES]
    weights = [c["weight"] for c in CLASSES]
    chosen_key = rng.choices(population, weights=weights, k=1)[0]
    chosen = next(c for c in CLASSES if c["key"] == chosen_key)
    confidence = round(rng.uniform(0.64, 0.97), 3)
    return {
        "classification": chosen["label"],
        "confidence": confidence,
        "urgency": chosen["urgency"],
    }


def generate_heatmap(image_bytes: bytes) -> bytes:
    """Overlay a fabricated attention blob on the source image and return PNG bytes."""
    rng = _seeded_random(image_bytes)
    base = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    base.thumbnail((MAX_DIM, MAX_DIM))
    w, h = base.size

    # Build a soft grayscale "attention" mask via layered blurred ellipses.
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    cx = rng.uniform(0.35, 0.65) * w
    cy = rng.uniform(0.35, 0.65) * h
    base_r = rng.uniform(0.12, 0.22) * min(w, h)
    for i, alpha in zip(range(4, 0, -1), (60, 110, 170, 255)):
        r = base_r * (i / 2.2)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=alpha)
    mask = mask.filter(ImageFilter.GaussianBlur(radius=base_r / 3))

    # Colorize the mask: hot center (red/yellow) fading to transparent.
    heat = Image.new("RGBA", (w, h))
    mask_px = mask.load()
    heat_px = heat.load()
    for y in range(h):
        for x in range(w):
            v = mask_px[x, y]
            if v == 0:
                continue
            heat_px[x, y] = (255, max(0, 200 - v), 0, int(v * 0.65))

    composed = base.convert("RGBA")
    composed.alpha_composite(heat)
    out = io.BytesIO()
    composed.convert("RGB").save(out, format="PNG")
    return out.getvalue()
