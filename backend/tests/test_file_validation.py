"""File validation tests."""

from app.security.files import validate_extension, verify_content_type, sanitize_filename


def test_pdf_extension_allowed():
    ok, err = validate_extension("document.pdf")
    assert ok is True


def test_exe_extension_blocked():
    ok, err = validate_extension("malware.exe")
    assert ok is False


def test_pdf_magic_bytes():
    ok, err = verify_content_type(b"%PDF-1.4 fake", ".pdf")
    assert ok is True


def test_txt_utf8():
    ok, err = verify_content_type(b"hello world", ".txt")
    assert ok is True


def test_sanitize_filename_blocks_traversal():
    name = sanitize_filename("../../../etc/passwd")
    assert ".." not in name


def test_sanitize_filename_default():
    assert sanitize_filename("") == "uploaded_file"
