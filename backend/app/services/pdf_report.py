import io

from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.shapes import Drawing, String
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image as RLImage
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .mock_gemini import body_part_label

styles = getSampleStyleSheet()
BODY_STYLE = ParagraphStyle("body_ko", parent=styles["Normal"], fontSize=10, leading=15)
TITLE_STYLE = ParagraphStyle("title_ko", parent=styles["Title"], fontSize=18)
H2_STYLE = ParagraphStyle("h2_ko", parent=styles["Heading2"], fontSize=13)


def _confidence_chart(history: list[dict]) -> Drawing:
    drawing = Drawing(420, 160)
    chart = HorizontalLineChart()
    chart.x = 40
    chart.y = 20
    chart.height = 110
    chart.width = 350
    values = [round(h["confidence"] * 100, 1) for h in history]
    chart.data = [values]
    chart.categoryAxis.categoryNames = [h["date"] for h in history]
    chart.categoryAxis.labels.fontSize = 7
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = 100
    chart.valueAxis.valueStep = 20
    chart.lines[0].strokeColor = colors.HexColor("#d64545")
    chart.lines[0].strokeWidth = 2
    drawing.add(chart)
    drawing.add(String(40, 145, "신뢰도 변화 추이 (%)", fontSize=9, fillColor=colors.grey))
    return drawing


def build_pdf(
    *,
    user_name: str,
    age: int | None,
    gender: str | None,
    skin_tone: str | None,
    body_part: str,
    lesion_label: str | None,
    classification: str,
    confidence: float,
    urgency: str,
    gemini_report: str,
    capture_image_bytes: bytes | None,
    heatmap_image_bytes: bytes | None,
    history: list[dict],
) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm, leftMargin=1.8 * cm, rightMargin=1.8 * cm
    )
    story = []

    story.append(Paragraph("피부 병변 촬영 분석 리포트", TITLE_STYLE))
    story.append(Spacer(1, 0.4 * cm))

    info_rows = [
        ["환자", user_name],
        ["나이 / 성별", f"{age or '-'}세 / {gender or '-'}"],
        ["피부톤", skin_tone or "-"],
        ["촬영 부위", body_part_label(body_part) + (f" ({lesion_label})" if lesion_label else "")],
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

    story.append(Paragraph("AI 분류 결과", H2_STYLE))
    result_rows = [
        ["분류", classification],
        ["신뢰도", f"{round(confidence * 100, 1)}%"],
        ["긴급도", "높음 (전문의 상담 권장)" if urgency == "high" else "낮음 (정기 관찰)"],
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

    story.append(Paragraph("Gemini 자연어 리포트", H2_STYLE))
    for line in gemini_report.split("\n"):
        story.append(Paragraph(line, BODY_STYLE))
    story.append(Spacer(1, 0.5 * cm))

    if len(history) >= 2:
        story.append(Paragraph("변화 추이", H2_STYLE))
        story.append(_confidence_chart(history))

    doc.build(story)
    return buf.getvalue()
