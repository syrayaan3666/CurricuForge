"""
CurricuForge AI — Premium PDF Generator
Supports Semester Mode + Persona Roadmap Mode
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape


def safe(text):
    """Escape text for ReportLab XML parsing to prevent crashes on special characters."""
    if text is None:
        return ""
    return escape(str(text))


def generate_pdf_from_curriculum(curriculum: dict) -> bytes:
    print("PDF BUILDER V2 EXECUTED")

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
    )

    elements = []

    styles = getSampleStyleSheet()

    # =======================
    # 🎨 CUSTOM STYLES
    # =======================

    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#0F1724"),
        alignment=TA_CENTER,
        spaceAfter=14,
        fontName="Helvetica-Bold",
    )

    heading_style = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#0F1724"),
        spaceBefore=12,
        spaceAfter=8,
        fontName="Helvetica-Bold",
        backColor=colors.HexColor("#F0F8FF"),
    )

    subheading_style = ParagraphStyle(
        "Subheading",
        parent=styles["Heading3"],
        fontSize=11,
        textColor=colors.HexColor("#333333"),
        spaceBefore=6,
        spaceAfter=4,
        fontName="Helvetica-Bold",
    )

    body_style = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontSize=9,
        textColor=colors.HexColor("#505050"),
        alignment=TA_JUSTIFY,
        spaceAfter=4,
        leftIndent=12,
    )

    meta_style = ParagraphStyle(
        "Meta",
        parent=styles["BodyText"],
        fontSize=8,
        textColor=colors.HexColor("#606060"),
        leftIndent=12,
        spaceAfter=2,
    )

    # =======================
    # 🧠 TITLE + SUMMARY
    # =======================

    title = curriculum.get("program_title", "Curriculum Plan")
    elements.append(Paragraph(safe(title), title_style))

    if curriculum.get("summary"):
        elements.append(Paragraph(safe(curriculum["summary"]), body_style))
        elements.append(Spacer(1, 12))

    # =======================
    # 📊 METADATA
    # =======================

    meta_items = []

    if curriculum.get("total_weeks"):
        meta_items.append(f"<b>Duration:</b> {safe(curriculum['total_weeks'])} weeks")

    if curriculum.get("weekly_hours"):
        meta_items.append(f"<b>Weekly Hours:</b> {safe(curriculum['weekly_hours'])}")

    if curriculum.get("difficulty"):
        meta_items.append(f"<b>Difficulty:</b> {safe(curriculum['difficulty'])}")

    if curriculum.get("focus"):
        meta_items.append(f"<b>Focus:</b> {safe(curriculum['focus'])}")
    elif curriculum.get("level"):
        meta_items.append(f"<b>Level:</b> {safe(curriculum['level'])}")

    for item in meta_items:
        elements.append(Paragraph(item, meta_style))

    elements.append(Spacer(1, 12))

    # =====================================================
    # 🎓 SEMESTER MODE
    # =====================================================

    if curriculum.get("semesters"):

        for sem_idx, semester in enumerate(curriculum["semesters"]):

            if sem_idx > 0 and sem_idx % 2 == 0:
                elements.append(PageBreak())

            sem_num = semester.get("semester", sem_idx + 1)
            elements.append(Paragraph(f"Semester {sem_num}", heading_style))

            courses = semester.get("courses", [])

            for course_idx, course in enumerate(courses, 1):

                # Title
                elements.append(
                    Paragraph(
                        f"{course_idx}. {safe(course.get('title','Untitled Course'))}",
                        subheading_style,
                    )
                )

                # Difficulty
                if course.get("difficulty"):
                    elements.append(
                        Paragraph(
                            f"<font color='#1932A8'>[{safe(course['difficulty']).upper()}]</font>",
                            meta_style,
                        )
                    )

                # Description
                if course.get("description"):
                    elements.append(Paragraph(safe(course["description"]), body_style))

                # Skills
                if course.get("skills"):
                    skills_str = ", ".join(safe(str(s)) for s in course["skills"])
                    elements.append(
                        Paragraph(f"<b>🎯 Skills:</b> {skills_str}", meta_style)
                    )

                # Topics (✨ NEW STRUCTURED HANDLING)
                if course.get("topics"):
                    elements.append(Paragraph("<b>📚 Topics:</b>", meta_style))

                    for topic in course["topics"]:
                        if isinstance(topic, dict):

                            line = f"• {safe(topic.get('name',''))}"

                            if topic.get("estimated_hours"):
                                line += f" ({safe(topic['estimated_hours'])} hrs)"

                            if topic.get("weeks"):
                                line += f" — {safe(topic['weeks'])}"

                            elements.append(Paragraph(line, body_style))
                        else:
                            elements.append(Paragraph(f"• {safe(str(topic))}", body_style))

                # Deliverable
                if course.get("outcome_project"):
                    elements.append(
                        Paragraph(
                            f"<b>💡 Deliverable:</b> {safe(course['outcome_project'])}",
                            meta_style,
                        )
                    )

                elements.append(Spacer(1, 6))

            elements.append(Spacer(1, 12))

    # =====================================================
    # 🧠 ROADMAP MODE (PERSONA PLANNER)
    # =====================================================

    elif curriculum.get("roadmap"):

        for phase_idx, phase in enumerate(curriculum["roadmap"]):

            if phase_idx > 0:
                elements.append(PageBreak())

            elements.append(
                Paragraph(safe(phase.get("phase", f"Phase {phase_idx+1}")), heading_style)
            )

            for milestone in phase.get("milestones", []):

                elements.append(
                    Paragraph(f"• {safe(milestone.get('title','Milestone'))}", subheading_style)
                )

                if milestone.get("estimated_total_hours"):
                    elements.append(
                        Paragraph(
                            f"<b>Time:</b> {safe(milestone['estimated_total_hours'])} hrs",
                            meta_style,
                        )
                    )

                if milestone.get("skills"):
                    elements.append(
                        Paragraph(
                            "<b>Skills:</b> " + ", ".join(safe(str(s)) for s in milestone["skills"]),
                            meta_style,
                        )
                    )

                if milestone.get("topics"):
                    elements.append(Paragraph("<b>Topics:</b>", meta_style))

                    for topic in milestone["topics"]:
                        if isinstance(topic, dict):
                            line = f"• {safe(topic.get('name',''))}"
                            if topic.get("estimated_hours"):
                                line += f" ({safe(topic['estimated_hours'])} hrs)"
                            elements.append(Paragraph(line, body_style))
                        else:
                            elements.append(Paragraph(f"• {safe(str(topic))}", body_style))

                elements.append(Spacer(1, 6))

            elements.append(Spacer(1, 12))

    # =====================================================
    # 📋 VALIDATION PAGE
    # =====================================================

    if curriculum.get("validation_status"):

        elements.append(PageBreak())
        elements.append(Paragraph("Curriculum Quality Review", heading_style))

        status = curriculum["validation_status"]
        status_color = "#008000" if status.lower() == "approved" else "#FF6B6B"

        elements.append(
            Paragraph(f"<font color='{status_color}'><b>Status:</b> {safe(status)}</font>", meta_style)
        )

        for issue in curriculum.get("validation_issues", []):
            elements.append(Paragraph(f"• {safe(issue)}", body_style))

        for sugg in curriculum.get("validation_suggestions", []):
            elements.append(Paragraph(f"• {safe(sugg)}", body_style))

    # =======================
    # 🕓 FOOTER
    # =======================

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Spacer(1, 16))
    elements.append(
        Paragraph(
            f"<font size='7' color='#999999'>Generated by CurricuForge AI • {timestamp}</font>",
            meta_style,
        )
    )

    # =======================
    # BUILD PDF
    # =======================

    doc.build(elements)

    buffer.seek(0)
    return buffer.getvalue()
