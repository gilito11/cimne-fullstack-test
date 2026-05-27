import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from ..deps import get_current_user
from ..schemas.building import BuildingIndicator
from ..services import building_repo, external_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/buildings", tags=["buildings"])


def _pick(item: dict[str, Any], *keys: str) -> Any:
    for k in keys:
        if k in item and item[k] is not None:
            return item[k]
    return None


@router.get("", response_model=list[dict])
def list_local(_: dict = Depends(get_current_user)) -> list[dict]:
    return building_repo.list_buildings()


@router.get("/indicator", response_model=list[BuildingIndicator])
def get_indicator(
    indicator: str = Query("average_dwelling_area", description="Indicator slug"),
    calculation_date: str = Query("2025-05-14", description="YYYY-MM-DD"),
    _: dict = Depends(get_current_user),
) -> list[BuildingIndicator]:
    """Fetch an indicator from the CIMNE external API and intersect with local Neo4j buildings."""
    try:
        external_items = external_api.fetch_indicator(indicator, calculation_date)
    except Exception as exc:
        logger.exception("External API call failed")
        raise HTTPException(status_code=502, detail=f"External API error: {exc}")

    local_buildings = {b["reference"]: b for b in building_repo.list_buildings() if b.get("reference")}
    if not local_buildings:
        return []

    out: list[BuildingIndicator] = []
    for item in external_items:
        ref = _pick(item, "reference", "building_reference", "cadastral_reference", "ref")
        if not ref or ref not in local_buildings:
            continue
        local = local_buildings[ref]
        out.append(
            BuildingIndicator(
                reference=ref,
                name=local.get("name") or _pick(item, "name"),
                indicator=indicator,
                value=_pick(item, "value", "indicator_value", "average"),
                lat=local.get("lat") or _pick(item, "lat", "latitude"),
                lng=local.get("lng") or _pick(item, "lng", "longitude"),
                calculation_date=calculation_date,
            )
        )
    return out
