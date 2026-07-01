from pydantic import BaseModel
from pydantic import EmailStr


class RegisterRequest(BaseModel):

    name:str
    email:EmailStr
    password:str


class LoginRequest(BaseModel):

    email:EmailStr
    password:str


class UserResponse(BaseModel):

    id_user:int
    name:str
    email:str
    role:str

    class Config:
        from_attributes=True


class TokenResponse(BaseModel):

    access_token:str
    token_type:str