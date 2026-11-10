"""TXT extraction tests."""

from app.services.extraction_service import extract_txt


def test_extract_txt():
    content = b"Hello world.\n\nThis is a terms document."
    result = extract_txt(content, "terms.txt")
    assert "Hello world" in result.text
    assert result.source_type == "file"
    assert result.mime_type == "text/plain"
