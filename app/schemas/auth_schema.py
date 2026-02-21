from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Union, Annotated, Optional
from enum import Enum

class GenderEnum(str, Enum):
    male = "Male"
    female = "Female"

class SignupRequest(BaseModel):
    username: str 
    password: str
    name: str
    email: str
    country_code : str
    phone : str
    year_of_birth: int
    gender: GenderEnum

class SignupResponse(BaseModel):
    user_id: str
    message: str

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    user_id : str
    username : str
    name : str
    email : EmailStr
    access_token: str
    refresh_token: str
    token_type: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type : str

class CommonResponse(BaseModel):
    user_id: str
    message: str

class CommonMessageResponse(BaseModel):
    message: str

class UserBaseResponse(BaseModel):
    user_id: str
    username : str
    name: str
    email: EmailStr
    year_of_birth: int
    gender: str
    country_code: str
    phone: str