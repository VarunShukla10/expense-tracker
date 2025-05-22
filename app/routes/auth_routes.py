from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models import UserCreate, Token
from app.auth import hash_password, verify_password, create_access_token
from app.database import get_pool
from app.queries import get_user

router = APIRouter()

@router.post("/signup", response_model=Token)
async def signup(payload: UserCreate):
    pool = get_pool()
    if await get_user(pool, payload.username):
        raise HTTPException(400, "Username already exists")

    hashed_pw = hash_password(payload.password)
    await pool.execute("INSERT INTO users (username, password_hash) VALUES ($1, $2)", payload.username, hashed_pw)
    token = create_access_token({"sub": payload.username})
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    pool = get_pool()
    user = await get_user(pool, form_data.username)
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(400, "Invalid credentials")
    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}
