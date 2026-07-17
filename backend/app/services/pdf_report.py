import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .mock_gemini import body_part_label

styles = getSampleStyleSheet()
BODY_STYLE = ParagraphStyle("body_text", parent=styles["Normal"], fontSize=10, leading=15)
TITLE_STYLE = ParagraphStyle("title_text", parent=styles["Title"], fontSize=18)
H2_STYLE = ParagraphStyle("h2_text", parent=styles["Heading2"], fontSize=13)


def build_pdf(
    *,
    user_name: str,
    age: int | None,
    gender: str | None,
    body_part: str,
    lesion_label: str | None,
    classification: str,
    confidence: float,
    urgency: str,
    gemini_report: str,
    capture_image_bytes: bytes | None,
    heatmap_image_bytes: bytes | None,
) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm, leftMargin=1.8 * cm, rightMargin=1.8 * cm
    )
    story = []

    story.append(Paragraph("Skin Lesion Capture Analysis Report", TITLE_STYLE))
    story.append(Spacer(1, 0.4 * cm))

    info_rows = [
        ["Patient", user_name],
        ["Age / Gender", f"{age or '-'} / {gender or '-'}"],
        ["Body Part", body_part_label(body_part) + (f" ({lesion_label})" if lesion_label else "")],
    ]
    info_table = Table(info_rows, colWidths=[4 * cm, 10 * cm])
    info_table.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(info_table)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("AI Classification Result", H2_STYLE))
    result_rows = [
        ["Classification", classification],
        ["Confidence", f"{round(confidence * 100, 1)}%"],
        ["Urgency", "High (specialist consultation recommended)" if urgency == "high" else "Low (routine monitoring)"],
    ]
    result_table = Table(result_rows, colWidths=[4 * cm, 10 * cm])
    result_table.setStyle(
        TableStyle(
            [
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("TEXTCOLOR", (0, 0), (0, -1), colors.grey),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(result_table)
    story.append(Spacer(1, 0.4 * cm))

    if capture_image_bytes or heatmap_image_bytes:
        img_cells = []
        if capture_image_bytes:
            img_cells.append(RLImage(io.BytesIO(capture_image_bytes), width=7 * cm, height=7 * cm))
        if heatmap_image_bytes:
            img_cells.append(RLImage(io.BytesIO(heatmap_image_bytes), width=7 * cm, height=7 * cm))
        img_table = Table([img_cells])
        story.append(img_table)
        story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Gemini AI Report", H2_STYLE))
    for line in gemini_report.split("\n"):
        story.append(Paragraph(line, BODY_STYLE))

    doc.build(story)
    return buf.getvalue()
