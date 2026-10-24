
from io import BytesIO

from pypdf import PdfReader


def extract_pdf_text(pdf_source):
    """
    Extract text from a PDF.

    Accepts PDF bytes, a BytesIO object, or a file-like object.
    Returns extracted text as a string.
    """
    if isinstance(pdf_source, bytes):
        pdf_source = BytesIO(pdf_source)

    reader = PdfReader(pdf_source)

    extracted_pages = []

    for page in reader.pages:
        text = page.extract_text() or ""
        extracted_pages.append(text)

    return "\n".join(extracted_pages).strip()
