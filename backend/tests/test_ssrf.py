"""SSRF protection tests."""

from app.security.ssrf import validate_url


def test_valid_url():
    ok, normalized, err = validate_url("https://example.com/terms")
    assert ok is True
    assert err is None


def test_localhost_blocked():
    ok, _, err = validate_url("http://127.0.0.1/")
    assert ok is False
    assert err is not None


def test_private_ip_blocked():
    ok, _, err = validate_url("http://10.0.0.1/")
    assert ok is False


def test_metadata_endpoint_blocked():
    ok, _, err = validate_url("http://169.254.169.254/")
    assert ok is False


def test_invalid_scheme():
    ok, _, err = validate_url("ftp://example.com/")
    assert ok is False


def test_empty_url():
    ok, _, err = validate_url("")
    assert ok is False
