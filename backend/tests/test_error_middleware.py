"""Error middleware / exception handler shape tests."""


def test_404_shape(client, clean_db):
    res = client.get("/api/documents/99999")
    assert res.status_code == 404
    body = res.json()
    assert "error" in body
    assert body["error"]["code"] == "not_found"


def test_validation_shape(client, clean_db):
    # Invalid URL scheme should be a 400 validation/extraction error.
    res = client.post("/api/ingest/url", json={"url": "ftp://example.com/"})
    assert res.status_code == 400
    body = res.json()
    assert "error" in body


def test_request_id_header(client, clean_db):
    res = client.get("/health")
    assert res.status_code == 200
    assert "X-Request-ID" in res.headers
