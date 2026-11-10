"""API ingestion tests using TestClient."""


def test_health(client, clean_db):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"
    assert "X-Request-ID" in res.headers


def test_ingest_text(client, clean_db):
    res = client.post("/api/ingest/text", data={"text": "We collect your personal data."})
    assert res.status_code == 200
    assert res.json()["document_id"] is not None


def test_ssrf_url_blocked(client, clean_db):
    res = client.post("/api/ingest/url", json={"url": "http://127.0.0.1/"})
    assert res.status_code == 400
    assert "error" in res.json()
