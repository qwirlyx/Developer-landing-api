import re
from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    phone: str = Field(..., min_length=5, max_length=30)
    email: EmailStr
    comment: str = Field(..., min_length=5, max_length=2000)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be empty")

        if re.search(r"[<>]", value):
            raise ValueError("Name contains forbidden characters")

        return value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        value = value.strip()

        if not re.fullmatch(r"[\d\s()+\-]+", value):
            raise ValueError("Phone contains invalid characters")

        digits_count = len(re.sub(r"\D", "", value))

        if digits_count < 5 or digits_count > 20:
            raise ValueError("Phone must contain from 5 to 20 digits")

        return value

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value: str) -> str:
        value = value.strip()

        if re.search(r"<script|</script", value, re.IGNORECASE):
            raise ValueError("Comment contains forbidden content")

        return value


class ContactResponse(BaseModel):
    status: str
    message: str
    ai: dict
    email: dict