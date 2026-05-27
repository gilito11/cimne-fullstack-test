from pydantic import BaseModel


class BuildingIndicator(BaseModel):
    reference: str
    name: str | None = None
    indicator: str
    value: float | None = None
    lat: float | None = None
    lng: float | None = None
    calculation_date: str | None = None
