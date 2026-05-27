"""Seed Neo4j with buildings from the provided GeoJSON layer.

Usage (from repo root):
    python backend/scripts/seed_buildings.py data/buildings.geojson

The GeoJSON ships in the official test repo at `buildings-layer/buildings.geojson`.
Copy it to `data/buildings.geojson` (or pass the path explicitly) before running.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db import session_scope  # noqa: E402


def _centroid(coords) -> tuple[float | None, float | None]:
    """Return a rough centroid for Polygon / MultiPolygon / Point geometries."""
    if not coords:
        return None, None
    try:
        if isinstance(coords[0], (int, float)):
            return float(coords[1]), float(coords[0])
        flat: list[tuple[float, float]] = []

        def _walk(node):
            if isinstance(node, (list, tuple)) and node and isinstance(node[0], (int, float)):
                flat.append((float(node[0]), float(node[1])))
            else:
                for c in node:
                    _walk(c)

        _walk(coords)
        if not flat:
            return None, None
        lng = sum(p[0] for p in flat) / len(flat)
        lat = sum(p[1] for p in flat) / len(flat)
        return lat, lng
    except Exception:
        return None, None


def seed(geojson_path: Path) -> int:
    data = json.loads(geojson_path.read_text(encoding="utf-8"))
    features = data.get("features", [])
    inserted = 0
    with session_scope() as s:
        for feat in features:
            props = feat.get("properties", {}) or {}
            reference = props.get("reference") or props.get("ref") or props.get("cadastral_reference")
            if not reference:
                continue
            name = props.get("name")
            geom = feat.get("geometry") or {}
            lat, lng = _centroid(geom.get("coordinates"))
            s.run(
                """
                MERGE (b:Building {reference: $reference})
                SET b.name = $name,
                    b.latitude = $lat,
                    b.longitude = $lng
                """,
                reference=str(reference),
                name=name,
                lat=lat,
                lng=lng,
            )
            inserted += 1
    return inserted


if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/buildings.geojson")
    if not path.exists():
        raise SystemExit(f"GeoJSON not found at {path}")
    count = seed(path)
    print(f"Seeded {count} buildings into Neo4j")
