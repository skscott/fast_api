from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.security import get_password_hash, verify_password, create_access_token
from app.db.database import get_db
from app.db.models.user import User as UserModel
from app.db.schemas import User, Token, RegisterInput, LoginInput

router = APIRouter()

@router.post("/register", response_model=User)
def register(user: RegisterInput, db: Session = Depends(get_db)):
    existing = db.query(UserModel).filter(UserModel.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = get_password_hash(user.password)
    new_user = UserModel(username=user.username, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
def login_json(credentials: LoginInput, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.username == credentials.username).first()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=30)
    )

    return {
        "token": token,
        "user": {"id": user.id, "username": user.username}
    }


@router.post("/logout")
def logout():
    # No server-side state to clear in JWT-based auth
    return {"message": "Logged out successfully"}
