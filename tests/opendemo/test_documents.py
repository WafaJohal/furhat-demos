from pathlib import Path

import pytest
from pypdf.errors import PdfReadError

from furhat_demos.opendemo.documents import (
    delete_uploaded_document,
    extract_text,
    list_uploaded_documents,
    save_uploaded_pdf,
)

FIXTURE_PDF = Path(__file__).parent / "fixtures" / "sample_upload.pdf"
BLANK_FIXTURE_PDF = Path(__file__).parent / "fixtures" / "blank_page.pdf"


def test_extract_text_returns_pdf_content():
    text = extract_text(FIXTURE_PDF.read_bytes())

    assert "Zylophone Studies" in text


def test_extract_text_raises_for_invalid_pdf_bytes():
    with pytest.raises(PdfReadError):
        extract_text(b"not a real pdf")


def test_save_uploaded_pdf_writes_markdown_file(tmp_path):
    doc = save_uploaded_pdf("My Course Guide.pdf", FIXTURE_PDF.read_bytes(), data_dir=tmp_path)

    assert doc.filename == "uploaded-my-course-guide.md"
    saved_path = tmp_path / doc.filename
    assert saved_path.exists()
    content = saved_path.read_text()
    assert "Zylophone Studies" in content
    assert "My Course Guide.pdf" in content  # source filename recorded


def test_save_uploaded_pdf_raises_when_no_text_extracted(tmp_path):
    with pytest.raises(ValueError, match="No extractable text"):
        save_uploaded_pdf("empty.pdf", BLANK_FIXTURE_PDF.read_bytes(), data_dir=tmp_path)


def test_list_uploaded_documents_returns_only_uploaded_files(tmp_path):
    (tmp_path / "handbook-comp10001.md").write_text("not an upload")
    save_uploaded_pdf("Doc One.pdf", FIXTURE_PDF.read_bytes(), data_dir=tmp_path)
    save_uploaded_pdf("Doc Two.pdf", FIXTURE_PDF.read_bytes(), data_dir=tmp_path)

    docs = list_uploaded_documents(data_dir=tmp_path)

    assert {d.filename for d in docs} == {"uploaded-doc-one.md", "uploaded-doc-two.md"}


def test_list_uploaded_documents_empty_when_none_uploaded(tmp_path):
    assert list_uploaded_documents(data_dir=tmp_path) == []


def test_delete_uploaded_document_removes_file(tmp_path):
    doc = save_uploaded_pdf("Doc One.pdf", FIXTURE_PDF.read_bytes(), data_dir=tmp_path)

    result = delete_uploaded_document(doc.filename, data_dir=tmp_path)

    assert result is True
    assert not (tmp_path / doc.filename).exists()


def test_delete_uploaded_document_returns_false_when_missing(tmp_path):
    assert delete_uploaded_document("uploaded-nope.md", data_dir=tmp_path) is False


def test_delete_uploaded_document_rejects_non_uploaded_filenames(tmp_path):
    with pytest.raises(ValueError, match="Not an uploaded document"):
        delete_uploaded_document("handbook-comp10001.md", data_dir=tmp_path)


def test_delete_uploaded_document_rejects_path_traversal(tmp_path):
    with pytest.raises(ValueError, match="Not an uploaded document"):
        delete_uploaded_document("../../etc/passwd", data_dir=tmp_path)
