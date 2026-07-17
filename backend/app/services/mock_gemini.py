"""Mock stand-in for the Gemini API natural-language report generation step.

Real integration would send the classification result, heatmap, and patient
metadata to the Gemini API. Here we render an equivalent English summary from
a template so the rest of the product flow (PDF export, result screen) can
be built and demoed without a live API key.
"""

BODY_PART_LABELS = {
    "head": "Head",
    "neck": "Neck",
    "chest": "Chest",
    "abdomen": "Abdomen",
    "back": "Back",
    "left_upper_arm": "Left Upper Arm",
    "left_forearm": "Left Forearm",
    "right_upper_arm": "Right Upper Arm",
    "right_forearm": "Right Forearm",
    "left_thigh": "Left Thigh",
    "left_lower_leg": "Left Lower Leg",
    "right_thigh": "Right Thigh",
    "right_lower_leg": "Right Lower Leg",
}


def body_part_label(body_part: str) -> str:
    return BODY_PART_LABELS.get(body_part, body_part)


def generate_report(
    *,
    classification: str,
    confidence: float,
    urgency: str,
    body_part: str,
    age: int | None,
    gender: str | None,
) -> str:
    part_label = body_part_label(body_part)
    confidence_pct = round(confidence * 100, 1)
    patient_bits = []
    if age:
        patient_bits.append(f"{age} years old")
    if gender:
        patient_bits.append(gender)
    patient_desc = ", ".join(patient_bits) if patient_bits else "Patient"

    if urgency == "high":
        risk_line = (
            "This lesion shows morphological features that cannot rule out malignancy. "
            "An in-person dermatologist evaluation is recommended as soon as possible."
        )
    else:
        risk_line = (
            "This lesion currently appears benign, but regular monitoring for changes "
            "in size or color is recommended."
        )

    lines = [
        f"[{part_label} Capture Analysis Report]",
        f"Patient: {patient_desc}",
        f"AI classification: {classification} (confidence {confidence_pct}%)",
        risk_line,
        "This report is an AI-generated reference only and does not replace a "
        "clinical diagnosis. Please consult a healthcare professional for an "
        "accurate diagnosis.",
    ]
    return "\n".join(lines)
