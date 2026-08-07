from typing import Annotated
from uuid import UUID

import phonenumbers
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumberValidator

type E164NumberType = Annotated[
    str | phonenumbers.PhoneNumber, PhoneNumberValidator(number_format="E164")
]


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email: EmailStr = Field(max_length=120)


class UserCreate(UserBase):
    password_hash: str
    phone_number: E164NumberType | None = Field(default=None)
    push_token: str | None = Field(default=None, max_length=200)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=120)
    phone_number: E164NumberType | None = Field(default=None, max_length=200)
    push_token: str | None = Field(default=None, max_length=200)


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class UserPrivate(UserPublic):
    email: EmailStr
    phone_number: E164NumberType | None
    push_token: str | None
