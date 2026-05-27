import uuid
from typing import Any

from ..db import session_scope
from ..security import hash_password


def _row_to_user(row: dict[str, Any] | None) -> dict | None:
    if row is None:
        return None
    u = row["u"]
    return {
        "id": u["id"],
        "username": u["username"],
        "email": u["email"],
        "role": u["role"],
    }


def create_user(username: str, email: str, password: str, role: str = "user") -> dict:
    user_id = str(uuid.uuid4())
    password_hash = hash_password(password)
    with session_scope() as s:
        record = s.run(
            """
            CREATE (u:User {
                id: $id,
                username: $username,
                email: $email,
                password_hash: $password_hash,
                role: $role,
                created_at: datetime()
            })
            RETURN u
            """,
            id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
        ).single()
    return _row_to_user(record)


def get_user_by_email(email: str) -> dict | None:
    with session_scope() as s:
        record = s.run(
            "MATCH (u:User {email: $email}) RETURN u",
            email=email,
        ).single()
        if not record:
            return None
        u = record["u"]
        return {
            "id": u["id"],
            "username": u["username"],
            "email": u["email"],
            "role": u["role"],
            "password_hash": u["password_hash"],
        }


def get_user_by_id(user_id: str) -> dict | None:
    with session_scope() as s:
        record = s.run(
            "MATCH (u:User {id: $id}) RETURN u",
            id=user_id,
        ).single()
        return _row_to_user(record)


def list_users() -> list[dict]:
    with session_scope() as s:
        records = s.run("MATCH (u:User) RETURN u ORDER BY u.username")
        return [_row_to_user(r) for r in records]


def update_user(
    user_id: str,
    username: str | None = None,
    role: str | None = None,
    password: str | None = None,
) -> dict | None:
    sets: list[str] = []
    params: dict[str, Any] = {"id": user_id}
    if username is not None:
        sets.append("u.username = $username")
        params["username"] = username
    if role is not None:
        sets.append("u.role = $role")
        params["role"] = role
    if password is not None:
        sets.append("u.password_hash = $password_hash")
        params["password_hash"] = hash_password(password)
    if not sets:
        return get_user_by_id(user_id)

    query = "MATCH (u:User {id: $id}) SET " + ", ".join(sets) + " RETURN u"
    with session_scope() as s:
        record = s.run(query, **params).single()
    return _row_to_user(record)


def delete_user(user_id: str) -> bool:
    with session_scope() as s:
        result = s.run(
            "MATCH (u:User {id: $id}) DETACH DELETE u RETURN count(u) AS deleted",
            id=user_id,
        ).single()
    return bool(result and result["deleted"] > 0)
