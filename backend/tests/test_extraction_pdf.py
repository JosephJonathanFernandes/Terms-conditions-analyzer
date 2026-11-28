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
    # When Tesseract is not installed, OCR is unavailable.
    from app.services.extraction_service import PytesseractAvailable
    if not PytesseractAvailable:
        assert any("OCR unavailable" in w for w in result.warnings)


def test_extract_pdf_ocr_unavailable_warning(tmp_path):
    """Empty PDF with OCR disabled should warn about OCR being unavailable."""
    from app.services.extraction_service import extract_pdf, PytesseractAvailable

    if PytesseractAvailable:
        # Skip if Tesseract is installed — we can't easily simulate unavailability.
        return

    doc = fitz.open()
    doc.new_page()
    path = tmp_path / "empty.pdf"
    doc.save(str(path))
    doc.close()

    file_bytes = path.read_bytes()
    result = extract_pdf(file_bytes, "empty.pdf")

    assert result.extraction_confidence == "low"
    assert any("OCR unavailable" in w for w in result.warnings)


def test_extract_pdf_ocr_disabled(tmp_path, monkeypatch):
    """PDF with OCR disabled should not attempt OCR."""
    from app.services.extraction_service import extract_pdf

    # Temporarily disable OCR.
    import app.config as config_module
    settings = config_module.get_settings()
    settings.ocr_enabled = False

    doc = fitz.open()
    doc.new_page()
    path = tmp_path / "empty.pdf"
    doc.save(str(path))
    doc.close()

    file_bytes = path.read_bytes()
    result = extract_pdf(file_bytes, "empty.pdf")

    assert result.extraction_confidence == "low"
    assert result.text == ""
    # Restore setting.
    settings.ocr_enabled = True
