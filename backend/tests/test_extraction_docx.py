"""DOCX extraction tests with a real fixture."""

from docx import Document as DocxDocument


def _make_minimal_docx(tmp_path, text: str):
    doc = DocxDocument()
    doc.add_paragraph(text)
    cp = doc.core_properties
    cp.title = "Test Doc"
    cp.author = "Tester"
    path = tmp_path / "test.docx"
    doc.save(str(path))
    return path


def test_extract_docx(tmp_path):
    from app.services.extraction_service import extract_docx

    path = _make_minimal_docx(tmp_path, "We collect your personal data.")
    file_bytes = path.read_bytes()
    result = extract_docx(file_bytes, "test.docx")

    assert "We collect your personal data" in result.text
    assert result.mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    assert result.metadata.get("title") == "Test Doc"
    assert result.metadata.get("author") == "Tester"


def test_extract_docx_tables(tmp_path):
    from app.services.extraction_service import extract_docx

    doc = DocxDocument()
    doc.add_paragraph("Intro text.")
    table = doc.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text = "Key"
    table.rows[0].cells[1].text = "Value"
    path = tmp_path / "table.docx"
    doc.save(str(path))

    file_bytes = path.read_bytes()
    result = extract_docx(file_bytes, "table.docx")

    assert "Key | Value" in result.text
