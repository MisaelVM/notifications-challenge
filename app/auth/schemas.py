from pydantic import BaseModel, EmailStr, Field


class RegisterUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)
    password: str = Field(min_length=12)


class Token(BaseModel):
    access_token: str
    token_type: str
