from typing import Literal

from pydantic import BaseModel, EmailStr, Field

Role = Literal["admin", "user"]


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=6, max_length=200)
    role: Role = "user"


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=2, max_length=80)
    role: Role | None = None
    password: str | None = Field(default=None, min_length=6, max_length=200)


class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
