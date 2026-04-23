from pydantic import BaseModel, field_validator


class UploadRequest(BaseModel):
    file_name: str
    content_type: str = "application/pdf"

    @field_validator("content_type")
    @classmethod
    def must_be_pdf(cls, v: str) -> str:
        if v != "application/pdf":
            raise ValueError("Only PDF files are supported")
        return v


class AnalyzeRequest(BaseModel):
    s3_key: str
    job_description: str

    @field_validator("job_description")
    @classmethod
    def must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Job description cannot be empty")
        return v.strip()
