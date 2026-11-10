"""HTML sanitization for extracted web content.

Uses BeautifulSoup to strip scripts, styles, and dangerous attributes so
extracted page text can be handled safely downstream.
"""

from bs4 import BeautifulSoup


DANGEROUS_TAGS = {"script", "style", "noscript", "iframe", "object", "embed", "applet", "form", "input"}


def sanitize_html(html: str) -> str:
    """Remove dangerous tags and attributes from HTML, return cleaned HTML string."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(True):
        if tag.name in DANGEROUS_TAGS:
            tag.decompose()
        # Strip dangerous attributes.
        for attr in list(tag.attrs.keys()):
            if attr.lower() in {"onclick", "onload", "onerror", "onmouseover", "srcdoc", "javascript"}:
                del tag.attrs[attr]
    return str(soup)


def html_to_text(html: str) -> str:
    """Convert HTML to plain text, preserving minimal structure."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(DANGEROUS_TAGS):
        tag.decompose()
    # Replace block elements with newlines for readability.
    for tag in soup.find_all(["p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr"]):
        tag.insert_after("\n")
    text = soup.get_text(separator=" ")
    # Collapse excessive whitespace.
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)
