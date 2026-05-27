from app.security import create_access_token, decode_token, hash_password, verify_password


def test_password_hash_roundtrip():
    h = hash_password("hello123")
    assert h != "hello123"
    assert verify_password("hello123", h)
    assert not verify_password("nope", h)


def test_jwt_roundtrip():
    token = create_access_token("user-123", "admin")
    payload = decode_token(token)
    assert payload["sub"] == "user-123"
    assert payload["role"] == "admin"
