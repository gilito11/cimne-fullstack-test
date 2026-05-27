from ..db import session_scope


def list_buildings() -> list[dict]:
    """Return all buildings stored in Neo4j (reference + optional name/lat/lng)."""
    with session_scope() as s:
        records = s.run(
            """
            MATCH (b:Building)
            RETURN b.reference AS reference,
                   b.name      AS name,
                   b.latitude  AS lat,
                   b.longitude AS lng
            """
        )
        return [dict(r) for r in records]


def get_building_references() -> set[str]:
    with session_scope() as s:
        records = s.run("MATCH (b:Building) RETURN b.reference AS reference")
        return {r["reference"] for r in records if r["reference"]}
