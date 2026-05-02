import pytest
from unittest.mock import patch, MagicMock, mock_open
from app.services.ats_validator import ATSValidator

class TestATSValidator:
    @pytest.fixture
    def ats_validator(self):
        return ATSValidator()
    
    @pytest.fixture
    def sample_resume_text(self):
        return """
        John Smith
        john.smith@example.com
        
        SUMMARY
        Experienced software engineer with 5+ years in web development.
        
        WORK EXPERIENCE
        Senior Developer, Tech Company
        January 2020 - Present
        
        Software Engineer, Previous Company
        March 2017 - December 2019
        
        EDUCATION
        Bachelor of Science in Computer Science
        University of Technology, 2017
        
        SKILLS
        Python, JavaScript, React, FastAPI
        """
    
    def test_check_recognized_headers(self, ats_validator, sample_resume_text):
        result = ats_validator._check_recognized_headers(sample_resume_text)
        assert result is True
        
        # Test with insufficient headers
        insufficient_text = "John Smith\nSome random text without proper sections"
        result = ats_validator._check_recognized_headers(insufficient_text)
        assert result is False
    
    def test_check_date_formats(self, ats_validator, sample_resume_text):
        result = ats_validator._check_date_formats(sample_resume_text)
        assert result is True
        
        # Test with insufficient date formats
        insufficient_text = "John Smith\nSome random text without proper dates"
        result = ats_validator._check_date_formats(insufficient_text)
        assert result is False
    
    def test_validate_content(self, ats_validator, sample_resume_text):
        with patch.object(ats_validator, '_check_recognized_headers', return_value=True):
            with patch.object(ats_validator, '_check_date_formats', return_value=True):
                results = ats_validator._validate_content(sample_resume_text)
                
                assert "recognized_section_headers" in results
                assert results["recognized_section_headers"] is True
                assert "proper_date_formats" in results
                assert results["proper_date_formats"] is True
                assert "standard_fonts" in results
                assert results["standard_fonts"] is True
    
    def test_validate_resume_pdf(self, ats_validator):
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Sample resume text with SUMMARY and EXPERIENCE sections"
        mock_doc.__iter__.return_value = [mock_page]
        
        with patch('fitz.open', return_value=mock_doc):
            with patch.object(ats_validator, '_validate_content', return_value={
                "recognized_section_headers": True,
                "proper_date_formats": True,
                "standard_fonts": True
            }):
                with patch.object(ats_validator, '_check_single_column_pdf', return_value=True):
                    with patch.object(ats_validator, '_check_no_images_tables_pdf', return_value=True):
                        result = ats_validator._validate_pdf("dummy.pdf")
                        
                        assert "overall_score" in result
                        assert result["passed"] is True
                        assert result["text_extractable"] is True
                        assert result["single_column"] is True
                        assert result["no_images_tables_textboxes"] is True
    
    def test_validate_resume_docx(self, ats_validator):
        mock_doc = MagicMock()
        mock_doc.paragraphs = [MagicMock(text="Sample resume text")]
        
        with patch('docx.Document', return_value=mock_doc):
            with patch.object(ats_validator, '_validate_content', return_value={
                "recognized_section_headers": True,
                "proper_date_formats": True,
                "standard_fonts": True
            }):
                with patch.object(ats_validator, '_check_standard_fonts_docx', return_value=True):
                    result = ats_validator._validate_docx("dummy.docx")
                    
                    assert "overall_score" in result
                    assert result["passed"] is True
                    assert result["standard_fonts"] is True
    
    def test_calculate_score(self, ats_validator):
        # Test with all rules passed
        results = {
            "recognized_section_headers": True,
            "proper_date_formats": True,
            "standard_fonts": True,
            "single_column": True,
            "no_images_tables_textboxes": True,
            "text_extractable": True
        }
        score = ats_validator._calculate_score(results)
        assert score == 100
        
        # Test with some rules failed
        results = {
            "recognized_section_headers": True,
            "proper_date_formats": True,
            "standard_fonts": False,
            "single_column": True,
            "no_images_tables_textboxes": False,
            "text_extractable": True
        }
        score = ats_validator._calculate_score(results)
        assert score < 100
        
    def test_validate_resume_unsupported_format(self, ats_validator):
        result = ats_validator.validate_resume("resume.txt")
        assert "error" in result
        assert result["passed"] is False
        assert result["overall_score"] == 0