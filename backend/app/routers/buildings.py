import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from ..deps import get_current_user
from ..schemas.building import BuildingIndicator
from ..services import building_repo, external_api

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/buildings", tags=["buildings"])


@router.get("", response_model=list[dict])
def list_local(_: dict = Depends(get_current_user)) -> list[dict]:
    return building_repo.list_buildings()


@router.get("/indicator", response_model=list[BuildingIndicator])
def get_indicator(
    indicator: str = Query("average_dwelling_area", description="Indicator slug"),
    calculation_date: str = Query("2025-05-14", description="YYYY-MM-DD"),
    _: dict = Depends(get_current_user),
) -> list[BuildingIndicator]:
    """Fetch an indicator from the CIMNE external API and intersect with local Neo4j buildings.

    The upstream endpoint returns a single document per indicator/date with a
    ``kpis`` mapping of ``{cadastral_reference: value}``. We flatten that map
    and keep only references that exist in the local Neo4j dataset.
    """
    try:
        external_items = external_api.fetch_indicator(indicator, calculation_date)
    except Exception as exc:
        logger.exception("External API call failed")
        raise HTTPException(status_code=502, detail=f"External API error: {exc}")

    local_buildings = {b["reference"]: b for b in building_repo.list_buildings() if b.get("reference")}
    if not local_buildings:
        return []

    kpis: dict[str, float] = {}
    for item in external_items:
        if isinstance(item, dict) and isinstance(item.get("kpis"), dict):
            kpis.update(item["kpis"])

    out: list[BuildingIndicator] = []
    for ref, value in kpis.items():
        if ref not in local_buildings:
            continue
        local = local_buildings[ref]
        out.append(
            BuildingIndicator(
                reference=ref,
                name=local.get("name"),
                indicator=indicator,
                value=float(value) if isinstance(value, (int, float)) else None,
                lat=local.get("lat"),
                lng=local.get("lng"),
                calculation_date=calculation_date,
            )
        )
    return out
