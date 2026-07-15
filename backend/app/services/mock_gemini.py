"""Mock stand-in for the Gemini API natural-language report generation step.

Real integration would send the classification result, heatmap, and patient
metadata to the Gemini API. Here we render an equivalent Korean summary from
a template so the rest of the product flow (PDF export, result screen) can
be built and demoed without a live API key.
"""

BODY_PART_LABELS_KO = {
    "head": "머리",
    "neck": "목",
    "chest": "가슴",
    "abdomen": "복부",
    "back": "등",
    "left_upper_arm": "왼쪽 위팔",
    "left_forearm": "왼쪽 아래팔",
    "right_upper_arm": "오른쪽 위팔",
    "right_forearm": "오른쪽 아래팔",
    "left_thigh": "왼쪽 허벅지",
    "left_lower_leg": "왼쪽 종아리",
    "right_thigh": "오른쪽 허벅지",
    "right_lower_leg": "오른쪽 종아리",
}


def body_part_label(body_part: str) -> str:
    return BODY_PART_LABELS_KO.get(body_part, body_part)


def generate_report(
    *,
    classification: str,
    confidence: float,
    urgency: str,
    body_part: str,
    age: int | None,
    gender: str | None,
    skin_tone: str | None,
    change_note: str | None = None,
) -> str:
    part_ko = body_part_label(body_part)
    confidence_pct = round(confidence * 100, 1)
    patient_bits = []
    if age:
        patient_bits.append(f"{age}세")
    if gender:
        patient_bits.append(gender)
    if skin_tone:
        patient_bits.append(f"피부톤 {skin_tone}")
    patient_desc = ", ".join(patient_bits) if patient_bits else "환자"

    if urgency == "high":
        risk_line = (
            "해당 병변은 형태학적으로 악성 가능성을 배제할 수 없는 소견을 보입니다. "
            "가급적 빠른 시일 내 피부과 전문의의 대면 진료를 받으시길 권장합니다."
        )
    else:
        risk_line = (
            "해당 병변은 현재로서는 양성 소견에 가까우나, 정기적인 관찰을 통해 "
            "크기나 색조 변화를 추적하는 것이 좋습니다."
        )

    lines = [
        f"[{part_ko} 부위 촬영 분석 리포트]",
        f"대상: {patient_desc}",
        f"AI 분류 결과: {classification} (신뢰도 {confidence_pct}%)",
        risk_line,
    ]
    if change_note:
        lines.append(change_note)
    lines.append(
        "본 리포트는 참고용 AI 분석 결과이며, 정식 진단을 대체하지 않습니다. "
        "정확한 진단은 반드시 의료진과 상담하시기 바랍니다."
    )
    return "\n".join(lines)
