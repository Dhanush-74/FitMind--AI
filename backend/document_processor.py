import io
import os
import uuid
from typing import Tuple, Dict, Optional, List
import pymupdf as fitz  # PyMuPDF
from docx import Document as DocxDocument
import config

class DocumentProcessor:
    def validate_document(self, file_bytes: bytes, content_type: str, filename: str) -> Tuple[bool, str]:
        size_mb = len(file_bytes) / (1024 * 1024)
        if size_mb > config.MAX_FILE_SIZE_MB:
            return False, f"File too large ({size_mb:.1f}MB). Maximum: {config.MAX_FILE_SIZE_MB}MB"
        
        ext = os.path.splitext(filename)[1].lower()
        allowed_exts = {'.pdf', '.docx', '.txt'}
        if ext not in allowed_exts:
            return False, f"Unsupported file format '{ext}'. Allowed: PDF, DOCX, TXT"
        return True, "Valid document"

    def extract_text(self, file_bytes: bytes, filename: str) -> Dict:
        ext = os.path.splitext(filename)[1].lower()
        if ext == '.pdf':
            return self._extract_pdf(file_bytes)
        elif ext == '.docx':
            return self._extract_docx(file_bytes)
        elif ext == '.txt':
            return self._extract_txt(file_bytes)
        else:
            return {"text": "", "pages": 0, "error": "Unsupported format"}

    def _extract_pdf(self, file_bytes: bytes) -> Dict:
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            pages = []
            full_text = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                if text.strip():
                    pages.append({"page": page_num + 1, "text": text.strip()})
                    full_text.append(f"[Page {page_num + 1}]\n{text.strip()}")
            doc.close()
            return {
                "text": "\n\n".join(full_text),
                "pages": len(pages),
                "page_data": pages,
                "error": None
            }
        except Exception as e:
            return {"text": "", "pages": 0, "error": f"PDF extraction error: {str(e)}"}

    def _extract_docx(self, file_bytes: bytes) -> Dict:
        try:
            doc = DocxDocument(io.BytesIO(file_bytes))
            paragraphs = []
            for para in doc.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text.strip())
            text = "\n\n".join(paragraphs)
            # Also extract from tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join([cell.text.strip() for cell in row.cells if cell.text.strip()])
                    if row_text:
                        paragraphs.append(row_text)
            return {
                "text": "\n\n".join(paragraphs),
                "pages": max(1, len(paragraphs) // 20),
                "error": None
            }
        except Exception as e:
            return {"text": "", "pages": 0, "error": f"DOCX extraction error: {str(e)}"}

    def _extract_txt(self, file_bytes: bytes) -> Dict:
        try:
            for encoding in ['utf-8', 'latin-1', 'cp1252']:
                try:
                    text = file_bytes.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                text = file_bytes.decode('utf-8', errors='replace')
            return {
                "text": text.strip(),
                "pages": 1,
                "error": None
            }
        except Exception as e:
            return {"text": "", "pages": 0, "error": f"TXT extraction error: {str(e)}"}

    def get_preview(self, text: str, max_length: int = 500) -> str:
        if len(text) <= max_length:
            return text
        return text[:max_length] + "..."

# Singleton
document_processor = DocumentProcessor()
