from pydantic import BaseModel

class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

class RegisterInput(BaseModel):
    username: str
    password: str

class LoginInput(BaseModel):
    username: str
    password: str
