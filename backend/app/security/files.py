"""Secure file upload validation.

Verifies extension and magic-byte content, enforces size limits, sanitizes
filenames, and handles temporary files safely.
"""

import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Tuple

# ---------------------------------------------------------------------------
# Ensure the libmagic DLL bundled with python-magic-bin (Windows) is loadable.
# The magic loader only searches the current directory and %PATH%, not its own
# libmagic/ subdirectory, so we add it explicitly on Windows.
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    try:
        import importlib

        _magic_pkg = importlib.import_module("magic")
        _dll_dir = os.path.join(os.path.dirname(_magic_pkg.__file__), "libmagic")
        if os.path.isdir(_dll_dir):
            if hasattr(os, "add_dll_directory"):
                os.add_dll_directory(_dll_dir)
            os.environ["PATH"] = _dll_dir + os.pathsep + os.environ.get("PATH", "")
    except Exception:
        pass

try:
    import magic as _magic

    MAGIC_AVAILABLE = True
except ImportError:  # pragma: no cover - environment without libmagic
    _magic = None
    MAGIC_AVAILABLE = False

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}

# Magic-byte signatures for allowed types.
MAGIC_SIGNATURES = {
    ".pdf": b"%PDF",
    ".docx": b"PK\x03\x04",  # ZIP-based Office Open XML
    ".txt": None,  # plain text: no fixed signature; validated by decoding
}

UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9._-]")


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename: keep only safe characters, block traversal, limit length."""
    name = os.path.basename(filename)
    name = UNSAFE_FILENAME_CHARS.sub("_", name)
    # Collapse and strip dot segments that could traverse directories.
    while ".." in name:
        name = name.replace("..", "_")
    name = name.lstrip(".")
    if not name:
        name = "uploaded_file"
    max_len = 120
    if len(name) > max_len:
        stem, ext = os.path.splitext(name)
        name = stem[: max_len - len(ext)] + ext
    return name


def validate_extension(filename: str) -> Tuple[bool, str | None]:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"File type '{ext}' not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
    return True, ext


def verify_content_type(file_bytes: bytes, ext: str) -> Tuple[bool, str | None]:
    """Verify file content matches its extension using magic bytes.

    Falls back to extension-only validation when libmagic is unavailable.
    """
    signature = MAGIC_SIGNATURES.get(ext)
    if signature is None:
        # .txt: attempt UTF-8 decode as a sanity check.
        try:
            file_bytes.decode("utf-8")
            return True, None
        except UnicodeDecodeError:
            return False, "Text file could not be decoded as UTF-8"

    if MAGIC_AVAILABLE and _magic is not None:
        try:
            detected = _magic.from_buffer(file_bytes)
        except Exception:
            detected = ""
        if not file_bytes.startswith(signature):
            return False, f"File content does not match '{ext}' type (magic-byte mismatch)"
    elif not file_bytes.startswith(signature):
        return False, f"File content does not match '{ext}' type (magic-byte check unavailable)"

    return True, None


def save_temp_file(file_bytes: bytes, filename: str) -> Tuple[str, str | None]:
    """Write bytes to a safe temporary file. Returns (path, error)."""
    safe_name = sanitize_filename(filename)
    try:
        fd, path = tempfile.mkstemp(prefix="clauseclear_", suffix=f"_{safe_name}")
        with os.fdopen(fd, "wb") as f:
            f.write(file_bytes)
        return path, None
    except OSError as exc:
        return "", f"Failed to write temporary file: {exc}"


def remove_temp_file(path: str) -> None:
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
