import pytest
import io
from unittest.mock import patch, MagicMock
from app.services.resume_parser import ResumeParser

class TestResumeParser:
    def setup_method(self):
        self.parser = ResumeParser()
        self.sample_text = """
        John Smith
        john.smith@example.com
        
        SUMMARY
        Experienced software engineer with 5+ years in web development.
        
        WORK EXPERIENCE
        Senior Developer, Tech Company
        2020 - Present
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology, 2018
        
        SKILLS
        Python, JavaScript, React, FastAPI
        """

    def test_extract_name(self):
        name = self.parser._extract_name(self.sample_text)
        assert name == "John Smith"
        
        # Test with no name
        assert self.parser._extract_name("No name here") is None
    
    def test_extract_email(self):
        email = self.parser._extract_email(self.sample_text)
        assert email == "john.smith@example.com"
        
        # Test with no email
        assert self.parser._extract_email("No email here") is None
        
        # Test with invalid email
        assert self.parser._extract_email("invalid.email@") is None
    
    def test_identify_sections(self):
        sections = self.parser._identify_sections(self.sample_text)
        assert "Summary" in sections
        assert "Work Experience" in sections
        assert "Education" in sections
        assert "Skills" in sections
        
        # Test with no sections
        assert len(self.parser._identify_sections("No sections here")) == 0
    
    @patch('fitz.open')
    def test_extract_text_from_pdf(self, mock_fitz_open):
        # Mock PDF extraction
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = self.sample_text
        mock_doc.__enter__.return_value = [mock_page]
        mock_fitz_open.return_value = mock_doc
        
        result = self.parser._extract_text_from_pdf(b"dummy pdf content")
        assert result == self.sample_text
        
        # Test exception handling
        mock_fitz_open.side_effect = Exception("PDF error")
        assert self.parser._extract_text_from_pdf(b"dummy pdf content") == ""
    
    @patch('docx.Document')
    def test_extract_text_from_docx(self, mock_docx):
        # Mock DOCX extraction
        mock_doc = MagicMock()
        mock_para1 = MagicMock()
        mock_para1.text = "John Smith"
        mock_para2 = MagicMock()
        mock_para2.text = "john.smith@example.com"
        mock_doc.paragraphs = [mock_para1, mock_para2]
        mock_docx.return_value = mock_doc
        
        result = self.parser._extract_text_from_docx(b"dummy docx content")
        assert result == "John Smith\njohn.smith@example.com"
        
        # Test exception handling
        mock_docx.side_effect = Exception("DOCX error")
        assert self.parser._extract_text_from_docx(b"dummy docx content") == ""
    
    def test_parse_resume_pdf(self):
        with patch.object(self.parser, '_extract_text_from_pdf', return_value=self.sample_text):
            result = self.parser.parse_resume(b"dummy content", "resume.pdf")
            assert result["text"] == self.sample_text
            assert result["name"] == "John Smith"
            assert result["email"] == "john.smith@example.com"
            assert len(result["sections"]) <= 5
            assert "Work Experience" in result["sections"]
    
    def test_parse_resume_docx(self):
        with patch.object(self.parser, '_extract_text_from_docx', return_value=self.sample_text):
            result = self.parser.parse_resume(b"dummy content", "resume.docx")
            assert result["text"] == self.sample_text
            assert result["name"] == "John Smith"
            assert result["email"] == "john.smith@example.com"
            assert len(result["sections"]) <= 5
    
    def test_parse_resume_unsupported_format(self):
        with pytest.raises(ValueError) as excinfo:
            self.parser.parse_resume(b"dummy content", "resume.txt")
        assert "Unsupported file format" in str(excinfo.value)
    
    def test_parse_resume_extraction_failure(self):
        with patch.object(self.parser, '_extract_text_from_pdf', return_value=""):
            with patch.object(self.parser, '_extract_text_with_ocr', return_value=self.sample_text):
                result = self.parser.parse_resume(b"dummy content", "resume.pdf")
                assert result["text"] == self.sample_text
    
    def test_parse_resume_exception(self):
        with patch.object(self.parser, '_extract_text_from_pdf', side_effect=Exception("Test error")):
            with pytest.raises(Exception) as excinfo:
                self.parser.parse_resume(b"dummy content", "resume.pdf")
            assert "Test error" in str(excinfo.value)