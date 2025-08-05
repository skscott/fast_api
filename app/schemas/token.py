from pydantic import BaseModel
from app.schemas.user import User

class Token(BaseModel):
    token: str
    user: User
