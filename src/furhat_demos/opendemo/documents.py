from __future__ import annotations

import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from pypdf import PdfReader

from furhat_demos.opendemo.qa import DATA_DIR

UPLOAD_FILENAME_PREFIX = "uploaded-"


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", Path(name).stem.lower()).strip("-")
    return slug or "document"


def extract_text(pdf_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(pdf_bytes))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(page.strip() for page in pages if page.strip())


@dataclass(frozen=True)
class UploadedDocument:
    filename: str


def save_uploaded_pdf(
    original_filename: str, pdf_bytes: bytes, data_dir: Path = DATA_DIR
) -> UploadedDocument:
    text = extract_text(pdf_bytes)
    if not text:
        raise ValueError(f"No extractable text found in {original_filename}")
    filename = f"{UPLOAD_FILENAME_PREFIX}{_slugify(original_filename)}.md"
    data_dir.mkdir(parents=True, exist_ok=True)
    content = f"<!-- Uploaded via admin: {original_filename} -->\n\n{text}\n"
    (data_dir / filename).write_text(content)
    return UploadedDocument(filename=filename)


def list_uploaded_documents(data_dir: Path = DATA_DIR) -> list[UploadedDocument]:
    pattern = f"{UPLOAD_FILENAME_PREFIX}*.md"
    return [UploadedDocument(filename=p.name) for p in sorted(data_dir.glob(pattern))]


def delete_uploaded_document(filename: str, data_dir: Path = DATA_DIR) -> bool:
    safe_name = Path(filename).name
    if not (safe_name.startswith(UPLOAD_FILENAME_PREFIX) and safe_name.endswith(".md")):
        raise ValueError(f"Not an uploaded document: {filename}")
    path = data_dir / safe_name
    if not path.exists():
        return False
    path.unlink()
    return True
