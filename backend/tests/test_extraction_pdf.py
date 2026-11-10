"""PDF extraction tests with a real (minimal) PDF fixture."""

import fitz  # PyMuPDF


def _make_minimal_pdf(tmp_path, text: str):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), text)
    path = tmp_path / "test.pdf"
    doc.save(str(path))
    doc.close()
    return path


def test_extract_pdf(tmp_path):
    from app.services.extraction_service import extract_pdf

    path = _make_minimal_pdf(tmp_path, "We collect your personal data.\nWe share it with third parties.")
    file_bytes = path.read_bytes()
    result = extract_pdf(file_bytes, "test.pdf")

    assert "We collect your personal data" in result.text
    assert result.source_type == "file"
    assert result.mime_type == "application/pdf"
    assert result.page_count == 1
    assert result.extraction_confidence == "high"


def test_extract_pdf_empty(tmp_path):
    from app.services.extraction_service import extract_pdf

    # PDF with no text (scanned).
    doc = fitz.open()
    doc.new_page()
    path = tmp_path / "empty.pdf"
    doc.save(str(path))
    doc.close()

    file_bytes = path.read_bytes()
    result = extract_pdf(file_bytes, "empty.pdf")

    assert result.extraction_confidence == "low"
    assert any("OCR" in w for w in result.warnings)
