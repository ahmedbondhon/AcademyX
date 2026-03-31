from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from database.crud import get_user_by_email, create_user
from core.security import verify_password, create_access_token
from models.schemas import UserRegister, UserLogin, TokenResponse, UserOut

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    # Check if email already exists
    existing = get_user_by_email(db, payload.email)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    user = create_user(
        db=db,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=payload.role
    )
    return user

@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    # Find user
    user = get_user_by_email(db, payload.email)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    # Check password
    if not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    # Check active
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account is disabled"
        )
    # Create token
    token = create_access_token(data={
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })
    return TokenResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        email=user.email,
        role=user.role
    )

@router.get("/me", response_model=UserOut)
def get_me(db: Session = Depends(get_db), token: str = ""):
    # We'll upgrade this to proper token extraction in Part 3
    # For now just use it to test the endpoint exists
    return {"message": "Auth working — /me will be protected in Part 3"}