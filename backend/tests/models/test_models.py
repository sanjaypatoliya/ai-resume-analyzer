import pytest
from pydantic import ValidationError

from app.models.requests import AnalyzeRequest, UploadRequest


class TestUploadRequest:
    def test_valid_pdf(self):
        req = UploadRequest(file_name="resume.pdf", content_type="application/pdf")
        assert req.file_name == "resume.pdf"

    def test_default_content_type_is_pdf(self):
        req = UploadRequest(file_name="resume.pdf")
        assert req.content_type == "application/pdf"

    def test_rejects_non_pdf(self):
        with pytest.raises(ValidationError):
            UploadRequest(file_name="resume.docx", content_type="application/docx")


class TestAnalyzeRequest:
    def test_valid_request(self):
        req = AnalyzeRequest(s3_key="uploads/uuid/resume.pdf", job_description="We need a Python developer")
        assert req.s3_key == "uploads/uuid/resume.pdf"

    def test_strips_whitespace_from_job_description(self):
        req = AnalyzeRequest(s3_key="uploads/uuid/resume.pdf", job_description="  Python developer  ")
        assert req.job_description == "Python developer"

    def test_rejects_empty_job_description(self):
        with pytest.raises(ValidationError):
            AnalyzeRequest(s3_key="uploads/uuid/resume.pdf", job_description="")

    def test_rejects_whitespace_only_job_description(self):
        with pytest.raises(ValidationError):
            AnalyzeRequest(s3_key="uploads/uuid/resume.pdf", job_description="   ")
