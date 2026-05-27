from fastapi import APIRouter, HTTPException, status

from ..schemas.user import LoginRequest, TokenResponse, UserCreate, UserOut
from ..security import create_access_token, verify_password
from ..services import user_repo

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate) -> TokenResponse:
    if user_repo.get_user_by_email(payload.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    user = user_repo.create_user(
        username=payload.username,
        email=payload.email,
        password=payload.password,
        role=payload.role,
    )
    token = create_access_token(subject=user["id"], role=user["role"])
    return TokenResponse(access_token=token, user=UserOut(**user))


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    user = user_repo.get_user_by_email(payload.email)
    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(subject=user["id"], role=user["role"])
    user_out = UserOut(
        id=user["id"], username=user["username"], email=user["email"], role=user["role"]
    )
    return TokenResponse(access_token=token, user=user_out)
