import logging
from typing import Any

import httpx

from ..config import get_settings

logger = logging.getLogger(__name__)

_token_cache: dict[str, str] = {}


def _login() -> str:
    """Authenticate against the CIMNE external API and cache the bearer token."""
    s = get_settings()
    if not s.external_api_email or not s.external_api_password:
        raise RuntimeError("EXTERNAL_API_EMAIL / EXTERNAL_API_PASSWORD not configured")

    with httpx.Client(timeout=20.0) as client:
        resp = client.post(
            f"{s.external_api_base}/auth/login",
            json={"email": s.external_api_email, "password": s.external_api_password},
        )
        resp.raise_for_status()
        data = resp.json()
        token = data.get("token") or data.get("access_token")
        if not token:
            raise RuntimeError(f"Login response missing token: {data}")
        _token_cache["token"] = token
        return token


def _get_token() -> str:
    return _token_cache.get("token") or _login()


def fetch_indicator(indicator: str, calculation_date: str) -> list[dict[str, Any]]:
    """Fetch an indicator collection from the external API.

    Retries once on 401 by re-logging in.
    """
    s = get_settings()
    url = f"{s.external_api_base}/data/collection/{indicator}"
    params = {"calculation_date": calculation_date}

    def _do_request(token: str) -> httpx.Response:
        with httpx.Client(timeout=30.0) as client:
            return client.get(url, params=params, headers={"Authorization": f"Bearer {token}"})

    token = _get_token()
    resp = _do_request(token)
    if resp.status_code == 401:
        _token_cache.pop("token", None)
        token = _login()
        resp = _do_request(token)

    resp.raise_for_status()
    payload = resp.json()
    if isinstance(payload, list):
        return payload
    for key in ("data", "items", "results"):
        if isinstance(payload.get(key), list):
            return payload[key]
    logger.warning("Unexpected payload shape from indicator endpoint: %s", type(payload).__name__)
    return []
