import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import { api } from "../api/client";
import type { BuildingIndicator } from "../api/types";

const DEFAULT_CENTER: [number, number] = [41.6176, 0.6200]; // Lleida
const DEFAULT_ZOOM = 12;

async function fetchIndicator(indicator: string, date: string): Promise<BuildingIndicator[]> {
  const r = await api.get<BuildingIndicator[]>("/buildings/indicator", {
    params: { indicator, calculation_date: date },
  });
  return r.data;
}

export function BuildingsPage() {
  const [indicator, setIndicator] = useState("average_dwelling_area");
  const [date, setDate] = useState("2025-05-14");

  const { data, isFetching, error, refetch } = useQuery({
    queryKey: ["indicator", indicator, date],
    queryFn: () => fetchIndicator(indicator, date),
  });

  const mappable = (data ?? []).filter(
    (b) => typeof b.lat === "number" && typeof b.lng === "number"
  );
  const center: [number, number] =
    mappable.length > 0 ? [mappable[0].lat as number, mappable[0].lng as number] : DEFAULT_CENTER;

  return (
    <div className="container">
      <div className="card">
        <h1>Buildings — Indicator Map</h1>
        <p className="muted">
          Buildings retrieved from the CIMNE external API, intersected with your local Neo4j dataset.
        </p>
        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1rem" }}>
          <label style={{ flex: 1, minWidth: 200 }}>
            Indicator
            <input value={indicator} onChange={(e) => setIndicator(e.target.value)} />
          </label>
          <label style={{ flex: 1, minWidth: 160 }}>
            Calculation date
            <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
          </label>
          <button
            className="primary"
            onClick={() => refetch()}
            disabled={isFetching}
            style={{ alignSelf: "end" }}
          >
            {isFetching ? "Loading…" : "Reload"}
          </button>
        </div>

        {error && <p className="error">Could not load indicator data.</p>}

        <div className="map">
          <MapContainer center={center} zoom={DEFAULT_ZOOM} style={{ height: "100%", width: "100%" }}>
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />
            {mappable.map((b) => (
              <Marker key={b.reference} position={[b.lat as number, b.lng as number]}>
                <Popup>
                  <strong>{b.name ?? b.reference}</strong>
                  <br />
                  <code>{b.reference}</code>
                  <br />
                  {b.indicator}: <strong>{b.value ?? "—"}</strong>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        <p className="muted" style={{ marginTop: "0.75rem" }}>
          {data?.length ?? 0} building(s) returned · {mappable.length} with coordinates
        </p>
      </div>
    </div>
  );
}
