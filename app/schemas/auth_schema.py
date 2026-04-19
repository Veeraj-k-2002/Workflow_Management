from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"


class UserRoleEnum(str, Enum):
    admin = "admin"
    superuser = "superuser"
    normal = "normal"


class SignupRequest(BaseModel):
    username: str
    password: str
    name: str
    email: str
    country_code: str
    phone: str
    year_of_birth: int
    gender: GenderEnum
    company_id: Optional[str] = None


class SignupResponse(BaseModel):
    user_id: str
    message: str
    role: UserRoleEnum


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    user_id: str
    username: str
    name: str
    email: EmailStr
    role: UserRoleEnum
    company_id: Optional[str]
    access_token: str
    refresh_token: str
    token_type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str


class CommonResponse(BaseModel):
    user_id: str
    message: str


class CommonMessageResponse(BaseModel):
    message: str


class UserBaseResponse(BaseModel):
    user_id: str
    username: str
    name: str
    email: EmailStr
    year_of_birth: int
    gender: str
    country_code: str
    phone: str
    role: UserRoleEnum
    company_id: Optional[str]
