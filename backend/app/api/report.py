"""Report / PDF export endpoints."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.services import analysis_service

router = APIRouter()


@router.get("/report/{analysis_id}/pdf", tags=["report"])
async def report_pdf(analysis_id: int):
    try:
        report = analysis_service.get_report(analysis_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    # Build a simple PDF report text -> PDF bytes.
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        import io

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        width, height = letter
        y = height - 50

        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "ClauseClear Analysis Report")
        y -= 30
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Document: {report['document']['filename']}")
        y -= 16
        c.drawString(50, y, f"Source: {report['document']['source_type']}")
        y -= 24

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Executive Summary")
        y -= 18
        c.setFont("Helvetica", 10)
        for line in (report["analysis"]["summary"] or "").split("\n"):
            c.drawString(50, y, line[:100])
            y -= 14
        y -= 10

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "Risk Distribution")
        y -= 18
        c.setFont("Helvetica", 10)
        for k, v in (report["risk_distribution"] or {}).items():
            c.drawString(50, y, f"{k}: {v}")
            y -= 14

        c.drawString(50, y - 20, report["disclaimer"][:100])
        c.showPage()
        c.save()
        pdf = buf.getvalue()
        return Response(content=pdf, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename=clauseclear_report_{analysis_id}.pdf"
        })
    except ImportError:
        # reportlab not installed: return JSON fallback
        raise HTTPException(
            status_code=500,
            detail="PDF generation requires reportlab. Install with: pip install reportlab",
        )
