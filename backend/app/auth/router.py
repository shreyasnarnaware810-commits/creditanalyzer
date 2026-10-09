import uuid
from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schema import UserSignupRequest, UserLoginRequest, UserResponse, TokenResponse
from app.auth.security import hash_password, verify_password, create_access_token, get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/signup", response_model=TokenResponse)
def signup(req: UserSignupRequest):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (req.username, req.email))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        
        user_id = f"usr_{uuid.uuid4().hex[:12]}"
        pw_hash = hash_password(req.password)
        cursor.execute("""
            INSERT INTO users (id, username, email, password_hash, role, full_name, is_demo_user)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        """, (user_id, req.username, req.email, pw_hash, req.role, req.full_name))
        
        user_resp = UserResponse(
            id=user_id,
            username=req.username,
            email=req.email,
            role=req.role,
            full_name=req.full_name,
            is_demo_user=False
        )
        token = create_access_token({"sub": user_id, "role": req.role})
        return TokenResponse(access_token=token, user=user_resp)

@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest):
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email, password_hash, role, full_name, is_demo_user FROM users WHERE username = ?", (req.username,))
        row = cursor.fetchone()
        if not row:
            # Check by email as fallback
            cursor.execute("SELECT id, username, email, password_hash, role, full_name, is_demo_user FROM users WHERE email = ?", (req.username,))
            row = cursor.fetchone()
            
        if not row or not verify_password(req.password, row["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        user = dict(row)
        user_resp = UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            role=user["role"],
            full_name=user["full_name"],
            is_demo_user=bool(user["is_demo_user"])
        )
        token = create_access_token({"sub": user["id"], "role": user["role"]})
        return TokenResponse(access_token=token, user=user_resp)

@router.post("/logout")
def logout(current_user: dict = Depends(get_current_user)):
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
def me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        email=current_user["email"],
        role=current_user["role"],
        full_name=current_user["full_name"],
        is_demo_user=current_user["is_demo_user"]
    )
