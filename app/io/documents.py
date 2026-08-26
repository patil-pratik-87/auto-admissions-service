"""PyMuPDF implementation of the local PDF preflight seam."""

import pymupdf

from app.facts.documents import PdfRejected


class PyMuPDFPreflight:
    """Accept exact in-memory PDF bytes by proving every page can render."""

    def accept(self, content: bytes) -> int:
        """Validate the PDF and prove that every page can render."""
        if not content.startswith(b"%PDF-"):
            raise PdfRejected("NOT_PDF", "The input is not a PDF document.")

        try:
            with pymupdf.open(stream=content, filetype="pdf") as document:  # type: ignore[no-untyped-call]
                if document.needs_pass:
                    raise PdfRejected("ENCRYPTED_PDF", "Encrypted PDFs are not supported.")
                if document.page_count < 1:
                    raise PdfRejected("CORRUPT_PDF", "The PDF contains no pages.")
                for page in document:
                    try:
                        page.get_pixmap(
                            matrix=pymupdf.Matrix(0.25, 0.25),  # type: ignore[no-untyped-call]
                            alpha=False,
                        )
                    except Exception as error:
                        raise PdfRejected(
                            "PAGE_RENDER_FAILED",
                            "At least one PDF page could not be rendered.",
                        ) from error
                return int(document.page_count)
        except PdfRejected:
            raise
        except Exception as error:
            raise PdfRejected("CORRUPT_PDF", "The PDF could not be parsed.") from error
