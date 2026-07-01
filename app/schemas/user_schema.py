from pydantic import BaseModel


class UserRegister(BaseModel):

    username:str
    email:str
    password:str


class UserResponse(BaseModel):

    id:int
    username:str
    email:str