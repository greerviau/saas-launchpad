from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    token: str
    expires_days: float


class UserInDB(BaseModel):
    email: EmailStr
    name: Optional[str] = ""
    timezone: str
    last_login: datetime
    has_access: bool


class SignupRequest(BaseModel):
    email: EmailStr
    name: str = ""
    password: str


class EditUserRequest(BaseModel):
    name: str
    timezone: str
    native_language_code: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleLoginRequest(BaseModel):
    code: str


class LoginResponse(BaseModel):
    email: EmailStr
    name: str
    timezone: str
    access_token: Token
    last_login: datetime


class RefreshTokenRequest(BaseModel):
    refresh_token: str
