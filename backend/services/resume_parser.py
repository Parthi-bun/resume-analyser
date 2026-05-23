from io import BytesIO
from tempfile import NamedTemporaryFile

import docx2txt
from fastapi import UploadFile
from pypdf import PdfReader

from utils.text_processing import clean_text


class ResumeParser:
    SUPPORTED_TYPES = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    SUPPORTED_EXTENSIONS = {".pdf", ".docx"}

    async def read_upload(self, upload_file: UploadFile) -> bytes:
        file_bytes = await upload_file.read()
        if not file_bytes:
            raise ValueError("Uploaded file is empty.")
        return file_bytes

    def parse_resume(self, file_bytes: bytes, filename: str) -> str:
        filename_lower = filename.lower()
        if filename_lower.endswith(".pdf"):
            text = self._extract_from_pdf(file_bytes)
        elif filename_lower.endswith(".docx"):
            text = self._extract_from_docx(file_bytes)
        else:
            raise ValueError("Unsupported file format. Please upload a PDF or DOCX resume.")

        cleaned = clean_text(text)
        if not cleaned:
            raise ValueError("No readable text could be extracted from the uploaded resume.")
        return cleaned

    @staticmethod
    def _extract_from_pdf(file_bytes: bytes) -> str:
        reader = PdfReader(BytesIO(file_bytes))
        return " ".join(page.extract_text() or "" for page in reader.pages)

    @staticmethod
    def _extract_from_docx(file_bytes: bytes) -> str:
        with NamedTemporaryFile(suffix=".docx") as temp_file:
            temp_file.write(file_bytes)
            temp_file.flush()
            return docx2txt.process(temp_file.name)
