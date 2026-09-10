from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from database.connection import users_collection
from models.schemas import UserCreate, UserResponse, Token
from api.auth_utils import verify_password, get_password_hash, create_access_token, get_current_user
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    existing = await users_collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = get_password_hash(user.password)
    user_doc = {
        "name": user.name,
        "email": user.email,
        "password": hashed_pw,
        "created_at": datetime.utcnow()
    }
    result = await users_collection.insert_one(user_doc)
    return {"message": "User created successfully", "id": str(result.inserted_id)}

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["email"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "name": user.get("name"),
            "email": user.get("email")
        }
    }

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "id": str(current_user["_id"]),
        "name": current_user.get("name"),
        "email": current_user.get("email"),
        "created_at": current_user.get("created_at")
    }

@router.post("/change-password")
async def change_password(request: dict, current_user: dict = Depends(get_current_user)):
    """Change user password with verification of current password."""
    try:
        current_password = request.get("currentPassword")
        new_password = request.get("newPassword")
        
        if not verify_password(current_password, current_user.get("password", "")):
            raise HTTPException(status_code=401, detail="Current password is incorrect")
        
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
        
        hashed_pw = get_password_hash(new_password)
        await users_collection.update_one(
            {"_id": current_user["_id"]},
            {"$set": {"password": hashed_pw, "updated_at": datetime.utcnow()}}
        )
        
        return {"message": "Password changed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))