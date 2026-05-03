import re
import fitz  # PyMuPDF
import docx
import pytesseract
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ResumeParser:
    """Service for parsing resume files in PDF or DOCX format"""

    def __init__(self):
        self.section_headers = [
            "work experience", "experience", "employment history",
            "education", "academic background", "skills", "technical skills",
            "projects", "certifications", "languages", "summary", "profile"
        ]

    def parse_resume(self, file_content: bytes, filename: str) -> Dict:
        """Parse resume file and extract relevant information"""
        try:
            # Extract text based on file type
            if filename.lower().endswith('.pdf'):
                text = self._extract_text_from_pdf(file_content)
            elif filename.lower().endswith(('.docx', '.doc')):
                text = self._extract_text_from_docx(file_content)
            else:
                raise ValueError(f"Unsupported file format: {filename}")

            # Use OCR as fallback if needed
            if not text or len(text.strip()) < 50:
                text = self._extract_text_with_ocr(file_content)

            # Extract information
            name = self._extract_name(text)
            email = self._extract_email(text)
            sections = self._identify_sections(text)

            return {
                "text": text,
                "name": name,
                "email": email,
                "sections": sections[:5]  # Top 5 sections
            }
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            raise

    def parse(self, file_content: bytes, file_ext: str) -> Dict:
        """Parse method expected by routes - delegates to parse_resume"""
        filename = f"resume{file_ext}"
        return self.parse_resume(file_content, filename)

    def _extract_text_from_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            with fitz.open(stream=file_content, filetype="pdf") as doc:
                return "".join(page.get_text() for page in doc)
        except Exception as e:
            logger.error(f"PDF extraction error: {str(e)}")
            return ""

    def _extract_text_from_docx(self, file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            import io
            doc = docx.Document(io.BytesIO(file_content))
            return "\n".join(para.text for para in doc.paragraphs)
        except Exception as e:
            logger.error(f"DOCX extraction error: {str(e)}")
            return ""

    def _extract_text_with_ocr(self, file_content: bytes) -> str:
        """OCR fallback extraction (simplified implementation)"""
        return "OCR extraction placeholder"

    def _extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name from text.

        Heuristic: return the first line that looks like a real name:
        - 2-4 words
        - only alphabetic characters (plus common punctuation like . and -)
        - not an email/phone
        """
        lines = text.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            if not line:
                continue

            # Reject lines that look like email/phone
            if '@' in line:
                continue
            if re.search(r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}', line):
                continue

            # Only allow name-like characters
            if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]*", line):
                continue

            parts = [p for p in line.split() if p]
            if 2 <= len(parts) <= 4 and all(p[0].isupper() for p in parts if p):
                return line

        return None

    def _extract_email(self, text: str) -> Optional[str]:
        """Extract email address from text (simple regex)."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
        match = re.search(email_pattern, text)
        return match.group(0) if match else None

    def _identify_sections(self, text: str) -> List[str]:
        """Identify resume sections"""
        sections = []
        text_lower = text.lower()

        for header in self.section_headers:
            if header in text_lower:
                sections.append(header.title())

        return sections
