from pydantic import BaseModel
from app.db.schemas.user import User

class Token(BaseModel):
    token: str
    user: User
