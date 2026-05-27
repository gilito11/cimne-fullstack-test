from fastapi import APIRouter, Depends, HTTPException

from ..deps import get_current_user, require_admin
from ..schemas.user import UserOut, UserUpdate
from ..services import user_repo

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
def me(current: dict = Depends(get_current_user)) -> UserOut:
    return UserOut(**current)


@router.get("", response_model=list[UserOut])
def list_all(_: dict = Depends(get_current_user)) -> list[UserOut]:
    return [UserOut(**u) for u in user_repo.list_users()]


@router.get("/{user_id}", response_model=UserOut)
def get_one(user_id: str, _: dict = Depends(get_current_user)) -> UserOut:
    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(**user)


@router.put("/{user_id}", response_model=UserOut)
def update(
    user_id: str,
    payload: UserUpdate,
    current: dict = Depends(get_current_user),
) -> UserOut:
    is_self = current["id"] == user_id
    is_admin = current.get("role") == "admin"
    if not (is_self or is_admin):
        raise HTTPException(status_code=403, detail="Not allowed")
    if payload.role is not None and not is_admin:
        raise HTTPException(status_code=403, detail="Only admins can change roles")

    updated = user_repo.update_user(
        user_id, username=payload.username, role=payload.role, password=payload.password
    )
    if not updated:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(**updated)


@router.delete("/{user_id}", status_code=204)
def delete(user_id: str, _: dict = Depends(require_admin)) -> None:
    if not user_repo.delete_user(user_id):
        raise HTTPException(status_code=404, detail="User not found")
