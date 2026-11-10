"""Document and website text extraction service.

Supports PDF (PyMuPDF), DOCX (python-docx), TXT, and website URLs
(Trafilatura + BeautifulSoup). All extracted text is cleaned: duplicate
removal, whitespace normalization, HTML cleanup, and truncation to the
configured maximum.
"""

import io
import logging
import re
import urllib.request
from typing import Optional, Tuple

import fitz  # PyMuPDF
from docx import Document as DocxDocument
from bs4 import BeautifulSoup

from app.config import settings
from app.security.ssrf import validate_url
from app.security.html import sanitize_html, html_to_text
from app.utils.text import normalize_whitespace, remove_duplicates, truncate, split_paragraphs

logger = logging.getLogger("clauseclear")


class ExtractionResult:
    def __init__(
        self,
        text: str,
        source_type: str,
        source_url: Optional[str] = None,
        filename: Optional[str] = None,
        file_size: Optional[int] = None,
        mime_type: Optional[str] = None,
        metadata: Optional[dict] = None,
        page_count: Optional[int] = None,
        paragraph_count: Optional[int] = None,
        discovered_documents: Optional[list] = None,
        extraction_confidence: str = "high",
        warnings: Optional[list] = None,
    ):
        self.text = text
        self.source_type = source_type
        self.source_url = source_url
        self.filename = filename
        self.file_size = file_size
        self.mime_type = mime_type
        self.metadata = metadata or {}
        self.page_count = page_count
        self.paragraph_count = paragraph_count
        self.discovered_documents = discovered_documents or []
        self.extraction_confidence = extraction_confidence
        self.warnings = warnings or []


class ExtractionError(Exception):
    """Raised when text extraction fails."""


def extract_pdf(file_bytes: bytes, filename: str) -> ExtractionResult:
    """Extract text from a PDF file using PyMuPDF."""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as exc:
        raise ExtractionError(f"Unable to open PDF: {exc}")

    texts = []
    metadata = {}
    try:
        metadata = dict(doc.metadata or {})
    except Exception:
        metadata = {}

    warnings = []
    for page_num, page in enumerate(doc, start=1):
        try:
            page_text = page.get_text("text")
        except Exception as exc:
            logger.warning("Failed to extract page %d: %s", page_num, exc)
            page_text = ""
        if page_text.strip():
            texts.append(f"--- Page {page_num} ---\n{page_text}")

    page_count = doc.page_count
    doc.close()

    raw = "\n\n".join(texts)
    cleaned = _clean_text(raw)

    confidence = "high"
    if page_count > 0 and not cleaned.strip():
        confidence = "low"
        warnings.append("PDF contains no extractable text (may be scanned/image-based). OCR is recommended.")

    return ExtractionResult(
        text=cleaned,
        source_type="file",
        filename=filename,
        file_size=len(file_bytes),
        mime_type="application/pdf",
        metadata=metadata,
        page_count=page_count,
        paragraph_count=len(split_paragraphs(cleaned)),
        extraction_confidence=confidence,
        warnings=warnings,
    )


def extract_docx(file_bytes: bytes, filename: str) -> ExtractionResult:
    """Extract text from a DOCX file using python-docx."""
    try:
        doc = DocxDocument(io.BytesIO(file_bytes))
    except Exception as exc:
        raise ExtractionError(f"Unable to open DOCX: {exc}")

    paragraphs = []
    for para in doc.paragraphs:
        if para.text.strip():
            paragraphs.append(para.text)

    # Also extract table content.
    for table in doc.tables:
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
            if cells:
                paragraphs.append(" | ".join(cells))

    # Core properties metadata.
    metadata = {}
    try:
        cp = doc.core_properties
        metadata = {
            "title": cp.title or "",
            "author": cp.author or "",
            "subject": cp.subject or "",
            "created": str(cp.created) if cp.created else "",
            "modified": str(cp.modified) if cp.modified else "",
        }
    except Exception:
        metadata = {}

    raw = "\n\n".join(paragraphs)
    cleaned = _clean_text(raw)

    return ExtractionResult(
        text=cleaned,
        source_type="file",
        filename=filename,
        file_size=len(file_bytes),
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        metadata=metadata,
        paragraph_count=len(split_paragraphs(cleaned)),
    )


def extract_txt(file_bytes: bytes, filename: str) -> ExtractionResult:
    """Extract text from a plain-text file."""
    try:
        raw = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raw = file_bytes.decode("utf-8", errors="replace")

    cleaned = _clean_text(raw)

    return ExtractionResult(
        text=cleaned,
        source_type="file",
        filename=filename,
        file_size=len(file_bytes),
        mime_type="text/plain",
        metadata={},
        paragraph_count=len(split_paragraphs(cleaned)),
    )


def extract_url(url: str) -> ExtractionResult:
    """Extract text from a website URL.

    Validates the URL for SSRF safety, fetches with Trafilatura, falls back
    to BeautifulSoup, and discovers likely legal pages (Terms, Privacy, etc.)
    for user selection. Respects robots.txt via Trafilatura's fetch defaults.
    """
    is_valid, normalized_url, error = validate_url(url)
    if not is_valid:
        raise ExtractionError(error or "Invalid URL")

    # Normalize: strip common tracking query params and trailing slash.
    normalized_url = _normalize_url(normalized_url)

    # Trafilatura fetch + extraction.
    fetched = None
    try:
        fetched = trafilatura_fetch_url(normalized_url)
    except Exception as exc:
        logger.warning("Trafilatura fetch failed for %s: %s", normalized_url, exc)

    text = ""
    metadata = {}
    warnings = []

    if fetched:
        try:
            text = trafilatura.extract(
                fetched,
                include_comments=False,
                include_tables=True,
                no_fallback=False,
            ) or ""
            meta = trafilatura.metadata.extract_metadata(fetched) or {}
            metadata = {
                "title": getattr(meta, "title", "") or "",
                "author": getattr(meta, "author", "") or "",
                "sitename": getattr(meta, "sitename", "") or "",
                "description": getattr(meta, "description", "") or "",
                "language": getattr(meta, "language", "") or "",
            }
        except Exception as exc:
            logger.warning("Trafilatura extraction failed: %s", exc)

    # Fallback: BeautifulSoup if Trafilatura yielded nothing useful.
    if not text or len(text.strip()) < 100:
        warnings.append("Limited text extracted; page may be JavaScript-rendered or image-based")
        try:
            req = urllib.request.Request(
                normalized_url,
                headers={"User-Agent": "ClauseClear/1.0 (contact: support@example.com)"},
            )
            with urllib.request.urlopen(
                req, timeout=settings.request_timeout_seconds
            ) as resp:
                html = resp.read()
            soup = BeautifulSoup(html, "html.parser")
            for tag in soup.find_all(["script", "style", "noscript", "iframe"]):
                tag.decompose()
            text = soup.get_text(separator="\n")
            if not metadata.get("title"):
                title_tag = soup.find("title")
                metadata["title"] = title_tag.get_text().strip() if title_tag else ""
        except Exception as exc:
            raise ExtractionError(f"Unable to extract from URL: {exc}")

    cleaned = _clean_text(text)

    confidence = "high"
    if len(cleaned.strip()) < 100:
        confidence = "low"

    # Discover likely legal pages from links.
    discovered = _discover_legal_pages(cleaned, normalized_url)

    return ExtractionResult(
        text=cleaned,
        source_type="url",
        source_url=normalized_url,
        metadata=metadata,
        paragraph_count=len(split_paragraphs(cleaned)),
        discovered_documents=discovered,
        extraction_confidence=confidence,
        warnings=warnings,
    )


def trafilatura_fetch_url(url: str) -> Optional[str]:
    """Fetch a URL with Trafilatura, honoring timeouts."""
    import trafilatura

    return trafilatura.fetch_url(url, timeout=settings.request_timeout_seconds)


def _normalize_url(url: str) -> str:
    """Strip tracking query params and trailing slash."""
    try:
        from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

        parsed = urlparse(url)
        tracking = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid", "gclid"}
        qs = [(k, v) for k, v in parse_qsl(parsed.query) if k not in tracking]
        new_query = urlencode(qs)
        path = parsed.path or "/"
        if path != "/" and path.endswith("/"):
            path = path.rstrip("/")
        return urlunparse((parsed.scheme, parsed.netloc, path, parsed.params, new_query, ""))
    except Exception:
        return url


def _clean_text(raw: str) -> str:
    """Clean extracted text: sanitize HTML, normalize whitespace, remove
    duplicates, truncate to configured maximum."""
    text = sanitize_html(raw) if ("<" in raw and ">" in raw) else raw
    text = html_to_text(text) if ("<" in text and ">" in text) else text
    text = normalize_whitespace(text)
    text = remove_duplicates(text)
    text = truncate(text, settings.max_extracted_chars)
    return text


def _discover_legal_pages(text: str, base_url: str) -> list:
    """Heuristically discover likely legal-pages links from extracted text.

    Returns a list of {title, url} dicts. This is a lightweight hint; the
    user selects which document to analyze.
    """
    discovered = []
    keywords = [
        ("terms of service", "Terms of Service"),
        ("terms and conditions", "Terms and Conditions"),
        ("privacy policy", "Privacy Policy"),
        ("user agreement", "User Agreement"),
        ("legal", "Legal"),
    ]
    lower = text.lower()
    seen = set()
    for keyword, label in keywords:
        if keyword in lower and label not in seen:
            seen.add(label)
            discovered.append({"title": label, "url": base_url, "matched_keyword": keyword})
    return discovered[:5]


def extract_file(file_bytes: bytes, filename: str) -> ExtractionResult:
    """Dispatch file extraction based on extension."""
    import os

    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return extract_pdf(file_bytes, filename)
    if ext == ".docx":
        return extract_docx(file_bytes, filename)
    if ext == ".txt":
        return extract_txt(file_bytes, filename)
    raise ExtractionError(f"Unsupported file type: {ext}")
