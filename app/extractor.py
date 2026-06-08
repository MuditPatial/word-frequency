"""
Document text extractor.
Supports: .txt, .pdf (pdfplumber), .docx (python-docx)
"""

import os


def extract_text(filepath: str) -> str:
    """
    Extract plain text from a file based on its extension.
    Raises ValueError for unsupported types, IOError for read failures.
    """
    ext = os.path.splitext(filepath)[1].lower()

    if ext == ".txt":
        return _read_txt(filepath)
    elif ext == ".pdf":
        return _read_pdf(filepath)
    elif ext in (".docx", ".doc"):
        return _read_docx(filepath)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


# ── Readers ──────────────────────────────────────────────────────────────

def _read_txt(path: str) -> str:
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            with open(path, encoding=encoding) as fh:
                return fh.read()
        except UnicodeDecodeError:
            continue
    raise IOError("Unable to decode text file with common encodings.")


def _read_pdf(path: str) -> str:
    try:
        import pdfplumber
        pages = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    pages.append(text)
        if not pages:
            raise ValueError("PDF appears to be empty or image-only (no extractable text).")
        return "\n\n".join(pages)
    except ImportError:
        raise ImportError(
            "pdfplumber is not installed. Run: pip install pdfplumber"
        )


def _read_docx(path: str) -> str:
    try:
        from docx import Document
        doc = Document(path)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        if not paragraphs:
            raise ValueError("DOCX appears to be empty.")
        return "\n\n".join(paragraphs)
    except ImportError:
        raise ImportError(
            "python-docx is not installed. Run: pip install python-docx"
        )
