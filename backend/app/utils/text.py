"""Text cleaning and normalization utilities."""

import re


def remove_duplicates(text: str) -> str:
    """Remove duplicate consecutive lines while preserving order."""
    seen = set()
    lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped and stripped not in seen:
            seen.add(stripped)
            lines.append(stripped)
    return "\n".join(lines)


def normalize_whitespace(text: str) -> str:
    text = re.sub(r"\r\n|\r", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n...[truncated]"


def split_paragraphs(text: str) -> list[str]:
    """Split text into non-empty paragraphs."""
    paragraphs = [p.strip() for p in re.split(r"\n{2,}", text)]
    return [p for p in paragraphs if p]
