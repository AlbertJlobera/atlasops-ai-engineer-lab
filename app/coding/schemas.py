from pydantic import BaseModel, Field


class CodeChangeProposal(BaseModel):
    file_path: str = Field(
        description="Repository-relative path of the file to modify."
    )

    reason: str = Field(
        description="Why this code change is required."
    )

    original_sha: str = Field(
        description="GitHub SHA of the original file version."
    )

    original_content: str = Field(
        description="Current content of the file before modification."
    )

    proposed_content: str = Field(
        description="Complete proposed file content after modification."
    )

    summary: str = Field(
        description="Short human-readable summary of the proposed change."
    )


class CodeChangeRequest(BaseModel):
    instruction: str = Field(
        description="User request describing the desired code change."
    )


class CodeChangeValidation(BaseModel):
    valid: bool

    reason: str

    changed_file: str | None = None

class CodePublishResult(BaseModel):
    branch: str
    commit_sha: str
    pull_request_number: int
    pull_request_url: str