import requests
from .config import API_BASE


def _get(path: str, params: dict = None) -> dict | list | None:
    try:
        resp = requests.get(f"{API_BASE}{path}", params=params, timeout=5)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException:
        return None


def fetch_businesses() -> list[dict]:
    return _get("/businesses") or []


def fetch_summary() -> dict | None:
    return _get("/summary")


def fetch_insights(business_id: int) -> dict | None:
    return _get(f"/businesses/{business_id}/insights")


def fetch_reviews(business_id: int, limit: int = 20, offset: int = 0) -> list[dict]:
    return _get(
        f"/businesses/{business_id}/reviews",
        params={"limit": limit, "offset": offset},
    ) or []
