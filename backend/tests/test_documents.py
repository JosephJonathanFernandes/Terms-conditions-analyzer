"""Document management API tests."""

import io


def test_list_documents_empty(client, clean_db):
    res = client.get("/api/documents")
    assert res.status_code == 200
    data = res.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_ingest_then_list_and_get(client, clean_db):
    # Ingest text to create a document.
    res = client.post("/api/ingest/text", data={"text": "We collect your personal data."})
    assert res.status_code == 200
    doc_id = res.json()["document_id"]

    # List documents.
    res = client.get("/api/documents")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["id"] == doc_id
    assert data["items"][0]["filename"] == "pasted_text.txt"

    # Get single document.
    res = client.get(f"/api/documents/{doc_id}")
    assert res.status_code == 200
    assert res.json()["id"] == doc_id


def test_get_document_not_found(client, clean_db):
    res = client.get("/api/documents/99999")
    assert res.status_code == 404


def test_delete_document(client, clean_db):
    res = client.post("/api/ingest/text", data={"text": "We collect your personal data."})
    doc_id = res.json()["document_id"]

    res = client.delete(f"/api/documents/{doc_id}")
    assert res.status_code == 204

    # Deleted document should not be findable.
    res = client.get(f"/api/documents/{doc_id}")
    assert res.status_code == 404


def test_delete_document_not_found(client, clean_db):
    res = client.delete("/api/documents/99999")
    assert res.status_code == 404


def test_export_document_json(client, clean_db):
    res = client.post("/api/ingest/text", data={"text": "We collect your personal data."})
    doc_id = res.json()["document_id"]

    res = client.get(f"/api/documents/{doc_id}/export?format=json")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/json"
    data = res.json()
    assert data["filename"] == "pasted_text.txt"
    assert data["extracted_text"] == "We collect your personal data."


def test_export_document_txt(client, clean_db):
    res = client.post("/api/ingest/text", data={"text": "We collect your personal data."})
    doc_id = res.json()["document_id"]

    res = client.get(f"/api/documents/{doc_id}/export?format=txt")
    assert res.status_code == 200
    assert res.headers["content-type"].startswith("text/plain")
    assert "We collect your personal data" in res.text


def test_export_document_pdf(client, clean_db):
    res = client.post("/api/ingest/text", data={"text": "We collect your personal data."})
    doc_id = res.json()["document_id"]

    res = client.get(f"/api/documents/{doc_id}/export?format=pdf")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert res.content.startswith(b"%PDF")


def test_export_all_documents(client, clean_db):
    client.post("/api/ingest/text", data={"text": "Document one."})
    client.post("/api/ingest/text", data={"text": "Document two."})

    res = client.get("/api/documents/export/all?format=json")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/zip"

    import zipfile, io as _io
    zf = zipfile.ZipFile(_io.BytesIO(res.content))
    names = zf.namelist()
    assert len(names) == 2


def test_export_invalid_format(client, clean_db):
    res = client.post("/api/ingest/text", data={"text": "test"})
    doc_id = res.json()["document_id"]

    res = client.get(f"/api/documents/{doc_id}/export?format=xml")
    assert res.status_code == 422  # query pattern validation


def test_pagination(client, clean_db):
    for i in range(5):
        client.post("/api/ingest/text", data={"text": f"Document {i}."})

    res = client.get("/api/documents?page=1&page_size=2")
    assert res.status_code == 200
    data = res.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5
    assert data["pages"] == 3


def test_duplicate_ingestion_short_circuit(client, clean_db):
    text = "Unique duplicate text for testing."
    res1 = client.post("/api/ingest/text", data={"text": text})
    res2 = client.post("/api/ingest/text", data={"text": text})
    assert res1.json()["document_id"] == res2.json()["document_id"]
