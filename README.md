# Fullstack Pre-selection Test — CIMNE BEE Group

Small fullstack application built for the CIMNE technical assessment
(<https://github.com/beegroup-cimne/fullstack-pre-selection-test>).

The repository contains a **React + TypeScript** frontend, a **FastAPI** backend
and a **Neo4j 4.4** database. It implements the two exercises described in the
assessment: user management with authentication, and an external indicator
visualisation on a map.

---

## Stack

| Layer    | Technology                                        |
|----------|---------------------------------------------------|
| Frontend | Vite + React 18 + TypeScript, React Router, React Query, react-leaflet |
| Backend  | FastAPI, Pydantic v2, Neo4j Python driver, python-jose (JWT), passlib (bcrypt) |
| Database | Neo4j 4.4 with APOC and Neosemantics (n10s) plugins |
| Tooling  | Docker Compose for local orchestration            |

---

## Repository layout

```
.
├── backend/                 FastAPI application
│   ├── app/
│   │   ├── routers/         auth, users, buildings
│   │   ├── services/        user_repo, building_repo, external_api
│   │   ├── schemas/         pydantic models
│   │   ├── config.py        env-driven settings
│   │   ├── db.py            Neo4j driver lifecycle
│   │   ├── deps.py          FastAPI dependencies (auth)
│   │   ├── security.py      bcrypt + JWT helpers
│   │   └── main.py          app factory
│   ├── scripts/             seeders
│   └── tests/
├── frontend/                Vite + React + TS app
│   └── src/
│       ├── api/             axios client + types
│       ├── auth/            AuthContext + ProtectedRoute
│       └── pages/           Login, Register, Main, Users, Buildings
├── data/                    place the provided buildings.geojson here
├── docker-compose.yml
└── README.md
```

---

## Getting started

### 1. Clone and configure

```bash
git clone <this-repo-url> cimne-fullstack-test
cd cimne-fullstack-test
cp .env.example .env
```

Edit `.env` and set at least `NEO4J_PASSWORD`, `JWT_SECRET`, and — if you want
exercise 2 to fetch real data — `EXTERNAL_API_EMAIL` and
`EXTERNAL_API_PASSWORD` (the test credentials are provided in the original
Postman collection).

### 2. Provide the building dataset

The assessment ships two artefacts:

- **`Neo4JDB-dump/fullstack-graph-db.dump`** — an official Neo4j 4.4 dump.
  Import it from Neo4j Desktop (Create new DBMS from dump → Neo4j 4.4 → add
  APOC and n10s plugins). This is the canonical option.
- **`buildings-layer/buildings.geojson`** — a GeoJSON layer of the same
  buildings. The provided seeder uses this file when the Docker Neo4j is used.

To use the seeder, copy the GeoJSON next to the project:

```bash
cp /path/to/fullstack-pre-selection-test/buildings-layer/buildings.geojson data/buildings.geojson
```

### 3. Run with Docker (recommended)

```bash
docker compose up --build
```

Services started:

| Service   | URL                              |
|-----------|----------------------------------|
| Frontend  | <http://localhost:5173>          |
| Backend   | <http://localhost:8000> (docs at `/docs`) |
| Neo4j UI  | <http://localhost:7474> (user `neo4j`, password from `.env`) |

Once Neo4j is healthy, seed the buildings:

```bash
docker compose exec backend python scripts/seed_buildings.py data/buildings.geojson
```

> If you prefer to use the official dump, import it through Neo4j Desktop
> instead and point the backend at that DBMS by editing `NEO4J_URI` in `.env`.

### 4. Run locally (without Docker)

Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Neo4j must be running separately (Neo4j Desktop, an existing instance, or the
compose service above).

---

## Using the application

1. Open <http://localhost:5173>.
2. Register the first user — choose the `admin` role to be able to manage all
   users from the UI. After registration you are auto-logged in.
3. The **Home** page shows the username, role and identifier of the
   authenticated user.
4. **Users** lists every `:User` node and lets admins edit or delete them. A
   regular user can only edit their own profile.
5. **Buildings** fetches an indicator from the CIMNE external API, intersects
   it against the local Neo4j buildings and renders the resulting points on a
   Leaflet/OpenStreetMap map. Change the indicator slug or calculation date in
   the form on top.

---

## API summary

| Method | Path                     | Description                              | Auth     |
|--------|--------------------------|------------------------------------------|----------|
| POST   | `/auth/register`         | Create a user and return a JWT           | public   |
| POST   | `/auth/login`            | Exchange credentials for a JWT           | public   |
| GET    | `/users/me`              | Authenticated user                       | bearer   |
| GET    | `/users`                 | List users                               | bearer   |
| GET    | `/users/{id}`            | Get one user                             | bearer   |
| PUT    | `/users/{id}`            | Update (self, or admin for any)          | bearer   |
| DELETE | `/users/{id}`            | Delete user                              | admin    |
| GET    | `/buildings`             | List local buildings                     | bearer   |
| GET    | `/buildings/indicator`   | External indicator ∩ local buildings     | bearer   |

Interactive OpenAPI documentation lives at `http://localhost:8000/docs`.

---

## Design notes & assumptions

- **Why Neo4j for users?** The assessment requires it. The `:User` node carries
  the bare fields requested (`username`, `email`, `password_hash`, `role`,
  `id`). The model is intentionally flat — a real product would model
  relationships such as `(User)-[:MANAGES]->(Building)`, which is left as an
  obvious extension point.
- **Authentication.** Stateless JWT (HS256), 60-minute expiry by default.
  Passwords are hashed with bcrypt. The frontend stores the token in
  `localStorage`; on 401 it clears it and redirects to `/login`. Cookie-based
  auth would be preferable in a production setting (httpOnly + SameSite), but
  it adds CSRF handling that is out of scope for this assessment.
- **Authorisation.** Two roles, `admin` and `user`. Admins can edit any user
  and delete users; regular users can only edit themselves. Role changes
  require admin.
- **External API token.** The backend logs into the CIMNE API on-demand and
  caches the bearer token in memory; on a 401 it re-authenticates once.
- **Filtering buildings.** Indicators returned by the external API are joined
  by `reference` against the `:Building` nodes loaded from the provided
  dataset. Coordinates come from the local GeoJSON centroids (or, if absent,
  from the external payload).
- **Frontend.** No design system — minimal hand-written CSS to keep the code
  small and the focus on structure, type-safety and data flow.
- **Constraints.** `UNIQUE` constraints on `User.email` and `User.id` are
  created on startup.
- **Errors.** HTTP semantics are respected — 401 vs 403 vs 404 vs 409.

---

## Tests

A small smoke test for the security primitives is included:

```bash
cd backend
pytest
```

The integration paths (Neo4j + external API) are exercised through the running
app rather than mocked.

---

## Environment variables

See `.env.example`. Required at minimum:

- `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- `JWT_SECRET`
- `EXTERNAL_API_EMAIL`, `EXTERNAL_API_PASSWORD` (only for exercise 2)
- `CORS_ORIGINS` (comma-separated)
- `VITE_API_BASE` (frontend only)
