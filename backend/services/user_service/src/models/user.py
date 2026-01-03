from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    full_name: str
    mobile_number: str
    password: str
    ward_zone: str
    residential_address: str
    email: EmailStr
    language_preference: str

class UserLogin(BaseModel):
    mobile_number: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    mobile_number: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    full_name: str
    mobile_number: str
    ward_zone: str
    residential_address: str
    email: EmailStr
    language_preference: str
